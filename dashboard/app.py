"""Dashboard local (Streamlit) — Observatorio de Idoneidad y Capacidad del Estado.

Ejecuta: streamlit run dashboard/app.py
Lee data/processed/observatorio.duckdb (generado por el ETL). Local, sin nube.
"""
from __future__ import annotations
import os
import sys
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from observatorio.config import DUCKDB_PATH  # noqa: E402

st.set_page_config(page_title="Idoneidad y Capacidad del Estado", layout="wide")


@st.cache_data
def load(table: str) -> pd.DataFrame:
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    df = con.execute(f"SELECT * FROM {table}").df()
    con.close()
    return df


st.title("🏛️ Observatorio de Idoneidad y Capacidad del Estado")
st.caption("Datos públicos (peru-transparente · Portal de Transparencia). Indicadores "
           "**descriptivos y neutrales** sobre toda entidad. Correlación ≠ causalidad. "
           "No se clasifica a personas por ideología ni identidad.")

if not DUCKDB_PATH.exists():
    st.warning("No hay datos. Corre primero el ETL: `make etl`.")
    st.stop()

ice = load("ice_entidad")
personal = load("personal")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Entidades con ICE", int(ice["ice"].notna().sum()))
c2.metric("Registros de personal", f"{len(personal):,}")
c3.metric("ICE medio", round(ice["ice"].mean(), 3))
c4.metric("% por mérito (medio)", f"{round(ice['meritocracia'].mean()*100)}%")

tab1, tab2, tab3, tab4 = st.tabs(["Ranking ICE", "Régimen", "Rotación", "Red por entidad"])

with tab1:
    cats = ["(todas)"] + sorted(ice["categoria"].dropna().unique().tolist())
    cat = st.selectbox("Categoría de entidad", cats)
    d = ice if cat == "(todas)" else ice[ice["categoria"] == cat]
    d = d.dropna(subset=["ice"]).sort_values("ice", ascending=False).head(25)
    fig = px.bar(d, x="ice", y="nombre", orientation="h", color="nivel_ice",
                 hover_data=["meritocracia", "estabilidad", "capacidad"],
                 labels={"ice": "Índice ICE", "nombre": ""})
    fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("ICE = mérito·0.35 + estabilidad·0.35 + capacidad·0.30 (pesos en config/indicators.yaml).")

with tab2:
    reg = personal["regimen"].value_counts().reset_index()
    reg.columns = ["regimen", "n"]
    st.plotly_chart(px.pie(reg, names="regimen", values="n",
                           title="Distribución de régimen laboral (mérito vs. confianza)"),
                    use_container_width=True)

with tab3:
    dec = personal[personal["nivel"].isin(
        ["Ministro/Titular", "Viceministro", "Director/a", "Gerente", "Secretario General"])]
    rot = (dec.groupby(["entidad", "cargo_norm", "nivel"])["person_id"].nunique()
           .reset_index(name="personas_distintas"))
    rot = rot[rot["personas_distintas"] >= 2].sort_values("personas_distintas", ascending=False).head(30)
    st.subheader("Cargos de decisión con mayor recambio")
    st.dataframe(rot, use_container_width=True, hide_index=True)

with tab4:
    nombres = ice.dropna(subset=["nombre"]).sort_values("nombre")["nombre"].tolist()
    sel = st.selectbox("Entidad central", nombres)
    row = ice[ice["nombre"] == sel].iloc[0]
    idc = row["id_entidad"]
    a = personal[personal["id_entidad"] == idc][["person_id"]].drop_duplicates()
    b = personal.merge(a, on="person_id")
    edges = (b[b["id_entidad"] != idc].groupby("entidad")["person_id"].nunique()
             .reset_index(name="personas").sort_values("personas", ascending=False).head(20))
    st.subheader(f"Entidades conectadas a «{sel}» por trayectorias compartidas")
    if edges.empty:
        st.info("Sin trayectorias compartidas registradas.")
    else:
        st.plotly_chart(px.bar(edges, x="personas", y="entidad", orientation="h"),
                        use_container_width=True)
        st.caption("Personas que trabajaron en esta entidad y también en otras (movilidad, no juicio).")

"""Pipeline ETL local: peru-transparente CSV -> DuckDB + Parquet + métricas ICE.

Uso: python -m observatorio.etl.pipeline
Solo fuentes públicas. Conserva `fuente_url` y `captured_at` en cada fila (trazabilidad).
"""
from __future__ import annotations
import hashlib
import sys
import duckdb
import pandas as pd

from ..config import PT_DATA_DIR, DUCKDB_PATH, INTERIM_DIR, load_indicators
from .normalize import norm_nombre, identity_key, nivel_desde_cargo, norm_text
from ..metrics import meritocracia, estabilidad, capacidad, indice, redes


def _person_id(idkey: str) -> str:
    return hashlib.sha1(idkey.encode("utf-8")).hexdigest()[:16]


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    ent_path = PT_DATA_DIR / "entidades.csv"
    fun_path = PT_DATA_DIR / "funcionarios.csv"
    if not fun_path.exists():
        sys.exit(f"No se encontró {fun_path}. Configura PT_DATA_DIR (ver .env.example).")
    entidades = pd.read_csv(ent_path, dtype=str).fillna("")
    funcionarios = pd.read_csv(fun_path, dtype=str).fillna("")
    return entidades, funcionarios


def transform(funcionarios: pd.DataFrame) -> pd.DataFrame:
    p = funcionarios.copy()
    p["anio"] = pd.to_numeric(p["anio"], errors="coerce").fillna(0).astype(int)
    p["mes"] = pd.to_numeric(p["mes"], errors="coerce").fillna(0).astype(int)
    p["ingreso"] = pd.to_numeric(p.get("total_ingreso_mensual"), errors="coerce")
    p["nombre_norm"] = p["apellidos_nombres"].map(norm_nombre)
    p["person_id"] = p["nombre_norm"].map(lambda n: _person_id(identity_key(n)))
    p["cargo_norm"] = p["cargo"].map(norm_text)
    p["nivel"] = p.apply(lambda r: nivel_desde_cargo(r["cargo"]), axis=1)
    return p[p["anio"] > 0]


def snapshot_vigente(personal: pd.DataFrame) -> pd.DataFrame:
    """Última foto por entidad (anio,mes máximos) para composición actual."""
    per = personal.assign(period=personal["anio"] * 12 + personal["mes"])
    last = per.groupby("id_entidad")["period"].transform("max")
    return per[per["period"] == last]


def run() -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg = load_indicators()

    print("· Extrayendo de peru-transparente…")
    entidades, funcionarios = extract()
    print(f"  entidades={len(entidades)}  filas_personal={len(funcionarios)}")

    print("· Normalizando…")
    personal = transform(funcionarios)
    vigente = snapshot_vigente(personal)

    print("· Calculando métricas…")
    merit = meritocracia.score_entidad(vigente, cfg)
    estab = estabilidad.score_entidad(personal, cfg)
    cap = capacidad.score_entidad(personal)
    ice = indice.compute(merit, estab, cap, cfg)
    ice = ice.merge(entidades[["id_entidad", "nombre", "categoria", "tipo_label"]],
                    on="id_entidad", how="left")

    print("· Red de movilidad institucional (centralidad/comunidades)…")
    cent, edges = redes.centralidad(personal)
    ice = ice.merge(cent, on="id_entidad", how="left")

    print("· Escribiendo Parquet (intermedios versionables) y DuckDB…")
    cols_person = ["person_id", "id_entidad", "entidad", "anio", "mes", "regimen",
                   "cargo_norm", "nivel", "ingreso", "fuente_url", "captured_at"]
    personal[cols_person].to_parquet(INTERIM_DIR / "personal.parquet", index=False)
    ice.to_parquet(INTERIM_DIR / "ice_entidad.parquet", index=False)
    entidades.to_parquet(INTERIM_DIR / "entidades.parquet", index=False)
    edges.to_parquet(INTERIM_DIR / "red_aristas.parquet", index=False)

    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute("CREATE OR REPLACE TABLE entidades AS SELECT * FROM entidades")
    con.execute(f"CREATE OR REPLACE TABLE personal AS SELECT * FROM read_parquet('{INTERIM_DIR / 'personal.parquet'}')")
    con.execute(f"CREATE OR REPLACE TABLE ice_entidad AS SELECT * FROM read_parquet('{INTERIM_DIR / 'ice_entidad.parquet'}')")
    con.execute(f"CREATE OR REPLACE TABLE red_aristas AS SELECT * FROM read_parquet('{INTERIM_DIR / 'red_aristas.parquet'}')")
    con.close()

    top = ice.dropna(subset=["ice"]).head(5)[["nombre", "ice", "nivel_ice"]]
    print(f"✓ Listo. {len(ice)} entidades con ICE. DuckDB: {DUCKDB_PATH}")
    print(top.to_string(index=False))


if __name__ == "__main__":
    run()

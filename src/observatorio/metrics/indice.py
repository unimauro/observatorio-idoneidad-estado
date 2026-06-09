"""Índice de Idoneidad y Capacidad del Estado (ICE) por entidad.

ICE = w_merito·meritocracia + w_estab·estabilidad + w_cap·capacidad + w_idon·idoneidad
Los pesos viven en config/indicators.yaml (auditables). El índice DESCRIBE, no juzga;
es un punto de partida para investigar, no una conclusión.
"""
from __future__ import annotations
import pandas as pd


def compute(merit: pd.DataFrame, estab: pd.DataFrame, cap: pd.DataFrame,
            cfg: dict, idon: pd.DataFrame | None = None) -> pd.DataFrame:
    w = cfg["ice_pesos"]
    df = merit.merge(estab, on="id_entidad", how="outer").merge(cap, on="id_entidad", how="outer")
    if idon is not None and not idon.empty:
        df = df.merge(idon, on="id_entidad", how="outer")
    if "idoneidad" not in df:
        df["idoneidad"] = 0.0

    for col in ("meritocracia", "estabilidad", "capacidad", "idoneidad"):
        df[col] = pd.to_numeric(df.get(col), errors="coerce")

    # peso idoneidad solo si hay datos; redistribuye al resto si es 0 (Fase 1)
    wi = w.get("idoneidad", 0.0)
    base = w["meritocracia"] + w["estabilidad"] + w["capacidad"]
    df["ice"] = (
        w["meritocracia"] * df["meritocracia"].fillna(0)
        + w["estabilidad"] * df["estabilidad"].fillna(0.5)
        + w["capacidad"] * df["capacidad"].fillna(0)
        + wi * df["idoneidad"].fillna(0)
    ) / (base + wi)
    df["ice"] = df["ice"].round(4)

    thr = cfg["interpretacion_ice"]
    df["nivel_ice"] = pd.cut(df["ice"], bins=[-0.01, thr["medio"], thr["alto"], 1.01],
                             labels=["bajo", "medio", "alto"])
    return df.sort_values("ice", ascending=False).reset_index(drop=True)

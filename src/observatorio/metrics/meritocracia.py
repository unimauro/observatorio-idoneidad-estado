"""Sub-índice de MERITOCRACIA por entidad.

Mide qué proporción del personal —ponderada por nivel de decisión— accede por
mérito/carrera (Ley Servir, Nombrado) frente a designación/confianza. Neutral:
se aplica igual a toda entidad. No evalúa a personas individuales.
"""
from __future__ import annotations
import pandas as pd
from ..config import merito_regimen, peso_nivel


def score_entidad(personal: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """personal: filas con columnas id_entidad, regimen, nivel (snapshot vigente)."""
    p = personal.copy()
    p["merito"] = p["regimen"].map(lambda r: merito_regimen(r, cfg))
    p["w"] = p["nivel"].map(lambda n: peso_nivel(n, cfg))

    def agg(d: pd.DataFrame) -> pd.Series:
        wsum = d["w"].sum()
        merito_pond = (d["merito"] * d["w"]).sum() / wsum if wsum else d["merito"].mean()
        return pd.Series({
            "meritocracia": round(float(merito_pond), 4),
            "pct_merito": round(float((d["merito"] >= 0.8).mean()), 4),
            "pct_confianza": round(float((d["merito"] <= 0.2).mean()), 4),
            "n_personal": int(len(d)),
        })

    return p.groupby("id_entidad", group_keys=False).apply(agg).reset_index()

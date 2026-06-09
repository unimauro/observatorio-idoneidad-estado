"""Sub-índice de ESTABILIDAD por entidad.

Mide permanencia y rotación en cargos, con foco en niveles de decisión. Alta
rotación en cargos de decisión = menor capacidad de sostener políticas y servicios.
Neutral y agregado por entidad.
"""
from __future__ import annotations
import pandas as pd

DECISION = {"Ministro/Titular", "Viceministro", "Secretario General",
            "Gerente General", "Director/a", "Gerente"}


def add_period(personal: pd.DataFrame) -> pd.DataFrame:
    p = personal.copy()
    p["period"] = p["anio"].astype(int) * 12 + p["mes"].astype(int)
    return p


def tenure(personal: pd.DataFrame) -> pd.DataFrame:
    """Meses de permanencia por (person_id, id_entidad, cargo_norm)."""
    p = add_period(personal)
    g = p.groupby(["person_id", "id_entidad", "cargo_norm"]).agg(
        period_min=("period", "min"), period_max=("period", "max"), nivel=("nivel", "first"),
    ).reset_index()
    g["meses"] = g["period_max"] - g["period_min"] + 1
    return g


def score_entidad(personal: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    meses_min = cfg["estabilidad"]["meses_minimos_deseables"]
    t = tenure(personal)
    dec = t[t["nivel"].isin(DECISION)].copy()

    def agg(d: pd.DataFrame) -> pd.Series:
        if d.empty:
            return pd.Series({"estabilidad": 0.5, "permanencia_media_meses": 0.0,
                              "rotacion_cargos_decision": 0.0})
        permanencia = float(d["meses"].mean())
        # rotación: personas distintas por cargo de decisión (≥2 = hubo recambio)
        por_cargo = d.groupby("cargo_norm")["person_id"].nunique()
        rotacion = float((por_cargo >= 2).mean()) if len(por_cargo) else 0.0
        estab = min(permanencia / meses_min, 1.0) * (1 - 0.5 * rotacion)
        return pd.Series({
            "estabilidad": round(max(0.0, min(estab, 1.0)), 4),
            "permanencia_media_meses": round(permanencia, 1),
            "rotacion_cargos_decision": round(rotacion, 4),
        })

    return dec.groupby("id_entidad", group_keys=False).apply(agg).reset_index()

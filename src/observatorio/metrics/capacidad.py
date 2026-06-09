"""Sub-índice de CAPACIDAD por entidad (v0).

Proxy de capacidad operativa a partir de: cobertura temporal de datos, presencia
de cargos de decisión cubiertos y dotación. Es un proxy explícito, no un juicio;
se refinará con datos de ejecución presupuestal y vacancias (Fase 2). Neutral.
"""
from __future__ import annotations
import pandas as pd
from .estabilidad import add_period, DECISION


def score_entidad(personal: pd.DataFrame) -> pd.DataFrame:
    p = add_period(personal)

    def agg(d: pd.DataFrame) -> pd.Series:
        meses_cubiertos = d["period"].nunique()
        # cobertura de cargos de decisión (¿hay personas en niveles de decisión?)
        tiene_decision = float(d["nivel"].isin(DECISION).any())
        n_personal = int(d["person_id"].nunique())
        # normalización suave: cobertura temporal (hasta 24 meses) y dotación (log)
        cob = min(meses_cubiertos / 24.0, 1.0)
        dot = min((n_personal ** 0.5) / 10.0, 1.0)  # ~100 personas satura
        cap = 0.4 * cob + 0.3 * tiene_decision + 0.3 * dot
        return pd.Series({
            "capacidad": round(float(min(cap, 1.0)), 4),
            "meses_cubiertos": int(meses_cubiertos),
            "n_personal_unico": n_personal,
        })

    return p.groupby("id_entidad", group_keys=False).apply(agg).reset_index()

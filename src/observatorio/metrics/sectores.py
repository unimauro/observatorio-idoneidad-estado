"""Drill-down "decantado" por ministerio/sector prioritario.

Agrupa por patrón de NOMBRE (configurable) el ministerio central + entidades del
sector y consolida: ICE ponderado por personal, mezcla de régimen y de nivel,
top sub-entidades y top cargos. Neutral y agregado; no perfila personas.
"""
from __future__ import annotations
import re
import pandas as pd

DECISION = {"Ministro/Titular", "Viceministro", "Secretario General",
            "Gerente General", "Director/a", "Gerente"}


def _match_ids(ice: pd.DataFrame, patron: str) -> list[str]:
    rx = re.compile(patron, re.IGNORECASE)
    return ice[ice["nombre"].fillna("").map(lambda n: bool(rx.search(n)))]["id_entidad"].tolist()


def consolidar(personal: pd.DataFrame, ice: pd.DataFrame, sectores_cfg: list[dict]) -> list[dict]:
    out = []
    for s in sectores_cfg:
        ids = _match_ids(ice, s["patron"])
        sub = ice[ice["id_entidad"].isin(ids)].copy()
        psec = personal[personal["id_entidad"].isin(ids)]
        if sub.empty:
            continue
        npers = int(psec["person_id"].nunique())
        w = sub["n_personal"].fillna(0)

        def pond(col: str) -> float:
            if col not in sub:
                return 0.0
            return float((sub[col].fillna(0) * w).sum() / w.sum()) if w.sum() else float(sub[col].fillna(0).mean())

        ice_pond = pond("ice")
        merito_pond = pond("meritocracia")
        prof_pond = pond("profesionalizacion")
        # masa salarial mensual (proxy de tamaño; el presupuesto total requiere datos MEF)
        masa = float(psec["ingreso"].dropna().sum()) if "ingreso" in psec else 0.0

        regimen = psec["regimen"].value_counts().head(8).to_dict()
        nivel = psec["nivel"].value_counts().to_dict()
        n_decision = int(psec[psec["nivel"].isin(DECISION)]["person_id"].nunique())
        top_sub = (sub.sort_values("n_personal", ascending=False)
                   .head(8)[["nombre", "n_personal", "ice"]].to_dict("records"))
        top_cargos = (psec[psec["nivel"].isin(DECISION)]["cargo_norm"].value_counts()
                      .head(10).reset_index().values.tolist())
        ingreso_prom = float(psec["ingreso"].dropna().mean()) if psec["ingreso"].notna().any() else None

        central_row = ice[ice["id_entidad"] == str(s["central"])]
        central = central_row["nombre"].iloc[0] if not central_row.empty else s["nombre"]

        out.append({
            "clave": s["clave"], "nombre": s["nombre"], "central": central,
            "n_entidades": int(len(sub)), "n_personal": npers,
            "masa_salarial_mensual": round(masa, 2),
            "ice_ponderado": round(ice_pond, 4), "merito_ponderado": round(merito_pond, 4),
            "profesionalizacion": round(prof_pond, 4),
            "n_decision": n_decision,
            "ingreso_promedio": round(ingreso_prom, 2) if ingreso_prom else None,
            "regimen": [{"regimen": k, "n": int(v)} for k, v in regimen.items()],
            "nivel": [{"nivel": k, "n": int(v)} for k, v in nivel.items()],
            "top_entidades": [{"nombre": r["nombre"], "n_personal": int(r["n_personal"] or 0),
                               "ice": round(float(r["ice"]), 4) if pd.notna(r["ice"]) else None} for r in top_sub],
            "top_cargos_decision": [{"cargo": c[0], "n": int(c[1])} for c in top_cargos],
        })
    out.sort(key=lambda s: s["masa_salarial_mensual"], reverse=True)
    return out

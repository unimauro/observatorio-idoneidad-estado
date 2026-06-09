"""Sub-índice de IDONEIDAD (perfil del puesto vs. credenciales) — FASE 2.

Requiere ingerir el PERFIL exigido por cada cargo (manuales de puestos / SERVIR) y
las CREDENCIALES de quien lo ocupa (hojas de vida, declaraciones juradas SERVIR,
SUNEDU para grados). Aquí se deja el contrato de función y un stub neutral.

IMPORTANTE: la idoneidad se mide contra el PERFIL del puesto (formación y
experiencia exigidas), nunca contra afiliación ideológica, identidad ni opinión.
"""
from __future__ import annotations
import pandas as pd


def score_persona(credenciales: dict, perfil: dict) -> float:
    """0..1: cumplimiento del perfil exigido por el puesto.

    credenciales: {grado, anios_experiencia, especialidad, ...}
    perfil:       {grado_min, anios_min, especialidades, ...}
    """
    if not perfil:
        return float("nan")  # sin perfil de referencia no se puede afirmar idoneidad
    puntos, total = 0.0, 0.0
    if "grado_min" in perfil:
        total += 1
        puntos += 1.0 if _grado_ok(credenciales.get("grado"), perfil["grado_min"]) else 0.0
    if "anios_min" in perfil:
        total += 1
        puntos += 1.0 if (credenciales.get("anios_experiencia", 0) or 0) >= perfil["anios_min"] else 0.0
    if perfil.get("especialidades"):
        total += 1
        esp = (credenciales.get("especialidad") or "").lower()
        puntos += 1.0 if any(e.lower() in esp for e in perfil["especialidades"]) else 0.0
    return round(puntos / total, 4) if total else float("nan")


_ORDEN = ["secundaria", "tecnico", "bachiller", "titulo", "maestria", "doctorado"]


def _grado_ok(grado: str | None, grado_min: str) -> bool:
    try:
        return _ORDEN.index((grado or "").lower()) >= _ORDEN.index(grado_min.lower())
    except ValueError:
        return False


def score_entidad(matches: pd.DataFrame) -> pd.DataFrame:
    """Promedio de idoneidad por entidad (cuando haya datos de credenciales)."""
    if matches.empty or "idoneidad" not in matches:
        return pd.DataFrame(columns=["id_entidad", "idoneidad"])
    return matches.groupby("id_entidad")["idoneidad"].mean().round(4).reset_index()

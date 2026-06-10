"""FASE 2 — Ingesta de credenciales para activar el sub-índice de IDONEIDAD.

La idoneidad se mide contra el PERFIL del puesto (formación/experiencia exigidas),
NUNCA contra ideología o afiliación. Este módulo define el camino de ingesta; no
fabrica datos: trabaja con lo que se cargue desde fuentes públicas verificables.

Fuentes reales (a integrar, con su procedencia):
- SUNEDU — Registro Nacional de Grados y Títulos (consulta pública por nombre/DNI):
  https://enlinea.sunedu.gob.pe/  → verifica grado académico. Tiene CAPTCHA; el camino
  práctico es exportar/cargar un CSV de resultados, no scraping masivo.
- SERVIR — Declaraciones Juradas / hojas de vida de funcionarios públicos.
- Portales gob.pe de autoridades (formación académica declarada).
- Perfiles de puesto: Manuales (MPP/MOF) y convocatorias CAS/concurso (perfil exigido).

Flujo: cargar credenciales (CSV) + perfiles (CSV) → emparejar por person_id/cargo →
metrics.idoneidad.score_persona → promedio por entidad → activar peso `idoneidad` en config.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

from ..metrics.idoneidad import score_persona

# Esquema esperado del CSV de credenciales (cargado manualmente desde fuentes públicas):
CREDENCIALES_COLS = ["person_id", "nombre", "grado", "anios_experiencia", "especialidad", "fuente_url"]
# Esquema esperado del CSV de perfiles de puesto:
PERFIL_COLS = ["cargo_norm", "grado_min", "anios_min", "especialidades", "fuente_url"]


def cargar_credenciales(path: str | Path) -> pd.DataFrame:
    """Carga un CSV de credenciales verificadas (con fuente_url por fila)."""
    df = pd.read_csv(path, dtype=str).fillna("")
    faltan = [c for c in CREDENCIALES_COLS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en credenciales: {faltan}")
    df["anios_experiencia"] = pd.to_numeric(df["anios_experiencia"], errors="coerce").fillna(0)
    return df


def cargar_perfiles(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df["anios_min"] = pd.to_numeric(df.get("anios_min"), errors="coerce").fillna(0)
    return df


def calcular_idoneidad(personal: pd.DataFrame, credenciales: pd.DataFrame,
                       perfiles: pd.DataFrame) -> pd.DataFrame:
    """Empareja persona-cargo con sus credenciales y el perfil exigido → idoneidad 0..1.

    Devuelve filas [person_id, id_entidad, cargo_norm, idoneidad] solo donde HAY datos
    (sin credenciales/perfil no se afirma idoneidad: el dato queda ausente, no en cero).
    """
    perf = {r["cargo_norm"]: r for _, r in perfiles.iterrows()}
    cred = {r["person_id"]: r for _, r in credenciales.iterrows()}
    rows = []
    for _, p in personal.iterrows():
        c = cred.get(p["person_id"])
        pf = perf.get(p["cargo_norm"])
        if c is None or pf is None:
            continue
        especialidades = [e.strip() for e in str(pf.get("especialidades", "")).split("|") if e.strip()]
        idon = score_persona(
            {"grado": c["grado"], "anios_experiencia": c["anios_experiencia"], "especialidad": c["especialidad"]},
            {"grado_min": pf.get("grado_min"), "anios_min": pf.get("anios_min"), "especialidades": especialidades},
        )
        rows.append({"person_id": p["person_id"], "id_entidad": p["id_entidad"],
                     "cargo_norm": p["cargo_norm"], "idoneidad": idon})
    return pd.DataFrame(rows)

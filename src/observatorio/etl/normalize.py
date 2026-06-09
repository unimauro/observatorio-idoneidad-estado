"""Normalización de nombres, cargos y régimen, y matching de IDENTIDAD.

Aquí el "matching" sirve solo para reconciliar los registros del MISMO funcionario
público a lo largo del tiempo y entre entidades (para medir trayectoria/rotación).
No clasifica ni vincula personas por ideología, identidad ni afiliación.
"""
from __future__ import annotations
import re
from unidecode import unidecode
from rapidfuzz import fuzz

_WS = re.compile(r"\s+")
_NON = re.compile(r"[^A-Z ]")


def norm_text(s: str) -> str:
    """Mayúsculas, sin tildes, sin signos, espacios colapsados."""
    if not s:
        return ""
    s = unidecode(str(s)).upper()
    s = _NON.sub(" ", s)
    return _WS.sub(" ", s).strip()


def norm_nombre(apellidos_nombres: str) -> str:
    """Normaliza 'APELLIDOS, NOMBRES' a una forma canónica comparable.

    Reordena 'APELLIDOS, NOMBRES' -> 'NOMBRES APELLIDOS' normalizados, para que
    formatos distintos del mismo nombre coincidan.
    """
    raw = (apellidos_nombres or "").strip()
    if "," in raw:
        apellidos, nombres = raw.split(",", 1)
        raw = f"{nombres} {apellidos}"
    return norm_text(raw)


def identity_key(nombre_norm: str) -> str:
    """Clave de bloqueo (blocking) para acelerar el matching: tokens ordenados."""
    return " ".join(sorted(nombre_norm.split()))


def same_person_score(a: str, b: str) -> float:
    """Score 0..1 de que dos nombres normalizados sean la MISMA persona.

    Combina similitud de conjunto de tokens (robusta a orden) y ratio global.
    Es una heurística de reconciliación, no una prueba de identidad: los matches
    por debajo de un umbral alto deben revisarse y el DNI, cuando exista, manda.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    tset = fuzz.token_sort_ratio(a, b) / 100.0
    tsetx = fuzz.token_set_ratio(a, b) / 100.0
    return round(max(tset, 0.6 * tset + 0.4 * tsetx), 4)


# Niveles jerárquicos a partir del texto del cargo (cuando no viene `nivel`).
_NIVEL_PATRONES = [
    ("Ministro/Titular", r"\bMINISTR"),
    ("Viceministro", r"\bVICEMINISTR"),
    ("Secretario General", r"SECRETARI[OA] GENERAL"),
    ("Gerente General", r"GERENTE GENERAL"),
    ("Director/a", r"\bDIRECTOR"),
    ("Gerente", r"\bGERENTE"),
    ("Subdirector/Subgerente", r"SUBDIRECTOR|SUBGERENTE"),
    ("Jefe/a", r"\bJEFE"),
]


def nivel_desde_cargo(cargo: str, nivel: str = "") -> str:
    if nivel:
        return nivel
    c = norm_text(cargo)
    for etiqueta, patron in _NIVEL_PATRONES:
        if re.search(patron, c):
            return etiqueta
    return "Operativo"

"""Trazabilidad de procedencia.

Cada registro derivado conserva la URL de la fuente y la fecha de captura del dato
original de peru-transparente (Portal de Transparencia Estándar). Toda afirmación del
observatorio debe poder rastrearse a una fila con `fuente_url`.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Provenance:
    source_repo: str = "peru-transparente"
    source_file: str = ""
    fuente_url: str = ""          # URL pública original (Portal de Transparencia / gob.pe)
    captured_at: str = ""         # cuándo se capturó el dato original
    method: str = ""              # cómo se derivó este registro
    confidence: float = 1.0       # confianza del derivado (p.ej. matching de identidad)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Sourced:
    """Valor con su procedencia, para que ningún número viaje sin fuente."""
    value: Any
    provenance: Provenance = field(default_factory=Provenance)

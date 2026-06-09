"""Configuración central: rutas y carga de indicadores configurables."""
from __future__ import annotations
import os
from pathlib import Path
import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]

PT_DATA_DIR = Path(os.getenv("PT_DATA_DIR", ROOT.parent / "peru-transparente" / "data"))
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", ROOT / "data" / "processed" / "observatorio.duckdb"))
INTERIM_DIR = ROOT / "data" / "interim"
CONFIG_PATH = ROOT / "config" / "indicators.yaml"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "idoneidad_local")


def load_indicators() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def merito_regimen(regimen: str, cfg: dict | None = None) -> float:
    cfg = cfg or load_indicators()
    table = cfg["merito_por_regimen"]
    return float(table.get((regimen or "").strip(), table["_default"]))


def peso_nivel(nivel: str, cfg: dict | None = None) -> float:
    cfg = cfg or load_indicators()
    table = cfg["peso_por_nivel"]
    return float(table.get((nivel or "").strip(), table["_default"]))

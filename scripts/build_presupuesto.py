"""Construye el presupuesto por ministerio (PIM/devengado/%ejec) desde MEF Datos Abiertos.

Fuente: API de Datos Abiertos del MEF (SIAF), agregada por SECTOR. Reutiliza la salida
ya calculada por el repo hermano `qhaway-dashboard` (que consulta
api.datosabiertos.mef.gob.pe). Mapea SECTOR_NOMBRE -> clave de ministerio.

Uso: python scripts/build_presupuesto.py
Salida: data/interim/presupuesto_sector.json  {clave: {pim, devengado, ejecucion, year, fuente}}
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QHAWAY = Path(os.getenv("QHAWAY_DATA_DIR", ROOT.parent / "qhaway-dashboard" / "dist" / "data"))
OUT = ROOT / "data" / "interim" / "presupuesto_sector.json"
YEAR = int(os.getenv("MEF_YEAR", "2025"))  # último año cerrado disponible

# SECTOR_NOMBRE (MEF/SIAF) -> clave de ministerio del observatorio
SECTOR_A_CLAVE = {
    "ECONOMIA Y FINANZAS": "MEF",
    "EDUCACION": "MINEDU",
    "INTERIOR": "MININTER",
    "SALUD": "MINSA",
    "TRANSPORTES Y COMUNICACIONES": "MTC",
    "DEFENSA": "MINDEF",
    "PRESIDENCIA CONSEJO MINISTROS": "PCM",
    "DESARROLLO E INCLUSION SOCIAL": "MIDIS",
    "VIVIENDA CONSTRUCCION Y SANEAMIENTO": "VIVIENDA",
    "AGRARIO Y DE RIEGO": "MIDAGRI",
    "JUSTICIA": "MINJUS",
    "ENERGIA Y MINAS": "MINEM",
    "AMBIENTAL": "MINAM",
    "RELACIONES EXTERIORES": "RREE",
    "MUJER Y POBLACIONES VULNERABLES": "MIMP",
    "PRODUCCION": "PRODUCE",
    "TRABAJO Y PROMOCION DEL EMPLEO": "MTPE",
    "CULTURA": "MINCUL",
    "COMERCIO EXTERIOR Y TURISMO": "MINCETUR",
}
FUENTE = "https://api.datosabiertos.mef.gob.pe (SIAF) vía qhaway-dashboard"


def main() -> None:
    src = QHAWAY / f"por-sector-{YEAR}.json"
    if not src.exists():
        sys.exit(f"No se encontró {src}. Ajusta QHAWAY_DATA_DIR/MEF_YEAR o corre el ETL de qhaway.")
    rows = json.loads(src.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for r in rows:
        clave = SECTOR_A_CLAVE.get((r.get("sector") or "").strip().upper())
        if not clave:
            continue
        pim = float(r.get("pim") or 0)
        dev = float(r.get("devengado") or 0)
        out[clave] = {
            "pim_mm": round(pim / 1e6, 1),
            "devengado_mm": round(dev / 1e6, 1),
            "ejecucion_pct": round(100 * dev / pim, 1) if pim else None,
            "year": YEAR,
            "fuente": FUENTE,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ Presupuesto {YEAR} para {len(out)} ministerios -> {OUT}")
    for k, v in sorted(out.items(), key=lambda x: -x[1]["pim_mm"])[:6]:
        print(f"  {k:9} PIM S/{v['pim_mm']:>9,.1f} MM  ejec {v['ejecucion_pct']}%")


if __name__ == "__main__":
    main()

"""Exporta agregados institucionales (SIN datos personales) a web/data/*.json
para el sitio estático de GitHub Pages.

Uso: python scripts/export_web.py   (requiere haber corrido el ETL antes)
Solo publica entidades y métricas agregadas; ninguna persona se exporta.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
import duckdb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from observatorio.config import DUCKDB_PATH, load_indicators  # noqa: E402
from observatorio.metrics import sectores as sectores_m  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "web" / "data"


def main() -> None:
    if not DUCKDB_PATH.exists():
        sys.exit("No hay DuckDB. Corre primero el ETL: make etl")
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    ice = con.execute("""
        SELECT id_entidad, nombre, categoria, tipo_label,
               ROUND(ice,4) ice, nivel_ice,
               ROUND(meritocracia,4) meritocracia, ROUND(estabilidad,4) estabilidad,
               ROUND(capacidad,4) capacidad, n_personal,
               ROUND(permanencia_media_meses,1) permanencia_media_meses,
               ROUND(rotacion_cargos_decision,4) rotacion_cargos_decision,
               ROUND(pagerank,6) pagerank, ROUND(betweenness,6) betweenness, grado, comunidad,
               ROUND(profesionalizacion,4) profesionalizacion
        FROM ice_entidad WHERE ice IS NOT NULL ORDER BY ice DESC
    """).df()

    # Aristas de la red de movilidad institucional (con nombres), top por peso
    redes = con.execute("""
        SELECT a.origen, eo.nombre origen_nombre, a.destino, ed.nombre destino_nombre, a.peso
        FROM red_aristas a
        JOIN ice_entidad eo ON eo.id_entidad = a.origen
        JOIN ice_entidad ed ON ed.id_entidad = a.destino
        ORDER BY a.peso DESC LIMIT 200
    """).df()

    regimen = con.execute(
        "SELECT regimen, COUNT(*) n FROM personal GROUP BY regimen ORDER BY n DESC").df()

    rotacion = con.execute("""
        SELECT e.nombre entidad, p.cargo_norm, p.nivel,
               COUNT(DISTINCT p.person_id) personas
        FROM personal p JOIN ice_entidad e USING(id_entidad)
        WHERE p.nivel IN ('Ministro/Titular','Viceministro','Director/a','Gerente','Secretario General')
        GROUP BY e.nombre, p.cargo_norm, p.nivel HAVING personas >= 2
        ORDER BY personas DESC LIMIT 40
    """).df()

    n_personal = con.execute("SELECT COUNT(*) n FROM personal").fetchone()[0]

    # Decantado por ministerio/sector prioritario
    cfg = load_indicators()
    personal_df = con.execute(
        "SELECT id_entidad, person_id, regimen, nivel, cargo_norm, ingreso FROM personal").df()
    ice_df = con.execute(
        "SELECT id_entidad, nombre, ice, n_personal, meritocracia, estabilidad, profesionalizacion FROM ice_entidad").df()
    sectores = sectores_m.consolidar(personal_df, ice_df, cfg.get("sectores_prioritarios", []))
    con.close()

    stats = {
        "entidades_con_ice": int(len(ice)),
        "registros_personal": int(n_personal),
        "ice_medio": round(float(ice["ice"].mean()), 4),
        "merito_medio": round(float(ice["meritocracia"].mean()), 4),
        "por_nivel_ice": ice["nivel_ice"].astype(str).value_counts().to_dict(),
        "por_regimen": regimen.to_dict("records"),
        "generado": "2026-06-09",
        "fuente": "peru-transparente (Portal de Transparencia Estándar)",
    }

    (OUT / "ice.json").write_text(ice.to_json(orient="records", force_ascii=False), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "rotacion.json").write_text(rotacion.to_json(orient="records", force_ascii=False), encoding="utf-8")
    (OUT / "redes.json").write_text(redes.to_json(orient="records", force_ascii=False), encoding="utf-8")
    (OUT / "sectores.json").write_text(json.dumps(sectores, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Exportado a {OUT}: ice.json ({len(ice)}), stats.json, rotacion.json ({len(rotacion)}), "
          f"redes.json ({len(redes)}), sectores.json ({len(sectores)})")


if __name__ == "__main__":
    main()

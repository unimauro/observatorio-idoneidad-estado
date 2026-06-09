"""Carga el grafo neutral a Neo4j desde los Parquet intermedios.

Uso: python -m observatorio.graph.load_neo4j   (requiere Neo4j; ver docker-compose)
Carga Person, GovernmentEntity, GovernmentPosition y relaciones de trayectoria.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

from ..config import INTERIM_DIR, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

SCHEMA = Path(__file__).with_name("schema.cypher")


def _statements(text: str) -> list[str]:
    out = []
    for raw in text.split(";"):
        s = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("//")).strip()
        if s:
            out.append(s)
    return out


def run() -> None:
    try:
        from neo4j import GraphDatabase
    except ImportError:
        raise SystemExit("Instala el driver: pip install neo4j")

    personal = pd.read_parquet(INTERIM_DIR / "personal.parquet")
    ice = pd.read_parquet(INTERIM_DIR / "ice_entidad.parquet")

    # Agregados por persona-entidad y persona-cargo (para no cargar 213k filas crudas)
    pe = personal.groupby(["person_id", "id_entidad", "entidad"]).agg(
        anio_min=("anio", "min"), anio_max=("anio", "max"), n=("anio", "size")).reset_index()
    pc = personal.groupby(["person_id", "id_entidad", "cargo_norm", "nivel", "regimen"]).size().reset_index(name="n")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as s:
        for stmt in _statements(SCHEMA.read_text(encoding="utf-8")):
            s.run(stmt)

        s.run("""UNWIND $rows AS r
            MERGE (e:GovernmentEntity {id_entidad:r.id_entidad})
            SET e.nombre=r.nombre, e.categoria=r.categoria, e.ice=r.ice,
                e.meritocracia=r.meritocracia, e.estabilidad=r.estabilidad, e.capacidad=r.capacidad
        """, rows=ice.where(pd.notnull(ice), None).to_dict("records"))

        s.run("""UNWIND $rows AS r
            MERGE (p:Person {person_id:r.person_id})
            MERGE (e:GovernmentEntity {id_entidad:r.id_entidad})
            MERGE (p)-[w:WORKED_AT]->(e)
            SET w.anio_min=r.anio_min, w.anio_max=r.anio_max, w.n=r.n
        """, rows=pe.to_dict("records"))

        s.run("""UNWIND $rows AS r
            MERGE (g:GovernmentPosition {position_id: r.id_entidad + '|' + r.cargo_norm})
            SET g.cargo_norm=r.cargo_norm, g.nivel=r.nivel
            MERGE (e:GovernmentEntity {id_entidad:r.id_entidad})
            MERGE (g)-[:AT_ENTITY]->(e)
            MERGE (p:Person {person_id:r.person_id})
            MERGE (p)-[h:HELD]->(g)
            SET h.regimen=r.regimen
        """, rows=pc.to_dict("records"))
    driver.close()
    print(f"✓ Grafo cargado: {len(pe)} vínculos persona-entidad, {len(pc)} persona-cargo.")


if __name__ == "__main__":
    run()

"""API REST del Observatorio de Idoneidad y Capacidad del Estado (FastAPI).

Solo expone datos públicos agregados y trayectorias de cargos públicos, con
procedencia. No expone clasificaciones por ideología/identidad (no existen).
Uso: uvicorn observatorio.api.main:app --reload
"""
from __future__ import annotations
import duckdb
from fastapi import FastAPI, Query, HTTPException

from ..config import DUCKDB_PATH

app = FastAPI(title="Observatorio de Idoneidad y Capacidad del Estado", version="0.1.0")


def q(sql: str, params: list | None = None):
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        cur = con.execute(sql, params or [])
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        con.close()


@app.get("/")
def root():
    return {"servicio": "observatorio-idoneidad-estado", "endpoints":
            ["/entities", "/entities/{id}", "/people/{person_id}", "/rotation", "/network", "/statistics"]}


@app.get("/entities")
def entities(categoria: str | None = None, min_ice: float = 0.0, limit: int = 50):
    where = "WHERE ice IS NOT NULL AND ice >= ?"
    params: list = [min_ice]
    if categoria:
        where += " AND categoria = ?"
        params.append(categoria)
    return q(f"""SELECT id_entidad, nombre, categoria, ice, nivel_ice,
                 meritocracia, estabilidad, capacidad, n_personal
                 FROM ice_entidad {where} ORDER BY ice DESC LIMIT ?""", params + [limit])


@app.get("/entities/{id_entidad}")
def entity(id_entidad: str):
    rows = q("SELECT * FROM ice_entidad WHERE id_entidad = ?", [id_entidad])
    if not rows:
        raise HTTPException(404, "entidad no encontrada")
    return rows[0]


@app.get("/people/{person_id}")
def person(person_id: str):
    """Trayectoria pública: cargos por entidad y periodo (con fuente)."""
    rows = q("""SELECT id_entidad, entidad, cargo_norm, nivel, regimen,
                MIN(anio*12+mes) AS desde, MAX(anio*12+mes) AS hasta,
                ANY_VALUE(fuente_url) AS fuente_url
                FROM personal WHERE person_id = ?
                GROUP BY id_entidad, entidad, cargo_norm, nivel, regimen
                ORDER BY desde""", [person_id])
    if not rows:
        raise HTTPException(404, "person_id no encontrado")
    return {"person_id": person_id, "trayectoria": rows}


@app.get("/rotation")
def rotation(limit: int = 30):
    """Cargos de decisión con mayor recambio de ocupantes (puerta giratoria interna)."""
    return q("""SELECT e.nombre AS entidad, p.cargo_norm, p.nivel,
                COUNT(DISTINCT p.person_id) AS personas_distintas
                FROM personal p JOIN ice_entidad e USING(id_entidad)
                WHERE p.nivel IN ('Ministro/Titular','Viceministro','Director/a','Gerente','Secretario General')
                GROUP BY e.nombre, p.cargo_norm, p.nivel
                HAVING personas_distintas >= 2
                ORDER BY personas_distintas DESC LIMIT ?""", [limit])


@app.get("/network")
def network(id_entidad: str = Query(..., description="entidad central del ego-network")):
    """Ego-network: personas que pasaron por la entidad y a qué otras entidades fueron."""
    nodes = q("SELECT id_entidad AS id, nombre AS label FROM ice_entidad WHERE id_entidad = ?", [id_entidad])
    edges = q("""SELECT DISTINCT b.id_entidad AS target, e.nombre AS target_label, COUNT(DISTINCT a.person_id) AS personas
                 FROM personal a JOIN personal b ON a.person_id = b.person_id AND a.id_entidad <> b.id_entidad
                 JOIN ice_entidad e ON e.id_entidad = b.id_entidad
                 WHERE a.id_entidad = ? GROUP BY b.id_entidad, e.nombre
                 ORDER BY personas DESC LIMIT 25""", [id_entidad])
    return {"center": id_entidad, "nodes": nodes, "edges": edges}


@app.get("/statistics")
def statistics():
    regimen = q("SELECT regimen, COUNT(*) n FROM personal GROUP BY regimen ORDER BY n DESC")
    ice = q("""SELECT nivel_ice, COUNT(*) n, ROUND(AVG(ice),3) ice_medio
               FROM ice_entidad WHERE ice IS NOT NULL GROUP BY nivel_ice""")
    tot = q("SELECT COUNT(*) entidades FROM ice_entidad")[0]
    return {"entidades": tot["entidades"], "por_nivel_ice": ice, "por_regimen": regimen,
            "nota": "Indicadores descriptivos. Correlación no implica causalidad."}

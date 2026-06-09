# Arquitectura

```
peru-transparente/data/*.csv   (fuente pública, fuente_url por fila)
        │  extract
        ▼
[ ETL ]  normalize (nombres, cargo, nivel, régimen, person_id)
        │  → metrics (meritocracia · estabilidad · capacidad · idoneidad[F2]) → ICE
        ▼
data/interim/*.parquet   (intermedios versionables)   ──►  data/processed/observatorio.duckdb
        │                                                          │
        ├──────────────► [ Neo4j ]  grafo neutral (Person·Entity·Position)
        │                                                          │
   [ FastAPI ]  /entities /people /rotation /network /statistics   │
        │                                                          │
   [ Streamlit ]  ranking ICE · régimen · rotación · red ◄─────────┘
```

## Capas
- **ETL** (`src/observatorio/etl`): `extract` → `normalize` → `pipeline` (orquesta y persiste).
- **Métricas** (`src/observatorio/metrics`): funciones puras y testeables por sub-índice + `indice` (ICE).
- **Almacén**: DuckDB (consulta analítica local) + Parquet (intermedios reproducibles/versionables).
- **Grafo** (`src/observatorio/graph`): esquema Cypher neutral + loader; analítica de redes con GDS.
- **API** (`src/observatorio/api`): FastAPI de solo lectura sobre DuckDB.
- **Dashboard** (`dashboard/app.py`): Streamlit local.
- **Config** (`config/indicators.yaml`): pesos y reglas auditables.
- **Procedencia** (`provenance.py`): `fuente_url`/`captured_at` viajan con cada registro.

## Decisiones
- **Local-first / sin nube:** todo corre con `make` o `docker compose`; cero costos, datos en disco.
- **Parquet como contrato:** los intermedios son la unidad de versionado y reproducibilidad.
- **Pesos fuera del código:** el juicio metodológico es explícito y editable, no está enterrado en funciones.
- **Sin nodo de afiliación:** el modelo no admite clasificar personas por causa/ideología (decisión de diseño, no un filtro removible).

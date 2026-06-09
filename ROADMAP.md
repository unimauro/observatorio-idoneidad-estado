# Roadmap por fases

## Fase 1 — Núcleo local (✅ inicial en este repo)
- ETL peru-transparente → DuckDB + Parquet.
- Sub-índices meritocracia, estabilidad, capacidad → **ICE por entidad** (646 entidades calculadas).
- Grafo neutral en Neo4j (Person · GovernmentEntity · GovernmentPosition).
- API FastAPI (`/entities /people /rotation /network /statistics`) + dashboard Streamlit.
- Tests, CI, Docker Compose, documentación y procedencia.

## Fase 2 — Idoneidad real (perfil vs. credenciales)
- Ingerir **perfiles de puestos** (manuales/SERVIR) y **credenciales** (declaraciones juradas SERVIR, grados SUNEDU).
- Activar el sub-índice `idoneidad` (hoy con peso 0) y subir su peso en `config`.
- Reconciliación de identidad con **DNI** cuando esté disponible (reduce homónimos).

## Fase 3 — Capacidad ↔ servicio (correlación, no causa)
- Cruzar capacidad institucional con **indicadores de servicio** a población vulnerable (INEI/MIMP/MIDIS) y **ejecución presupuestal** (MEF).
- Análisis de redes: degree, betweenness, **PageRank**, detección de comunidades (entidades/cargos centrales en trayectorias).
- Series temporales: evolución 2000→presente de mérito/rotación/capacidad.

## Fase 4 — Publicación responsable
- Export estático/semiestático (D3.js / Sigma.js / Cytoscape.js) a **GitHub Pages**.
- Acceso **protegido** (Cloudflare Access o proxy con Basic Auth) **hasta validar** la metodología.
- Reportes reproducibles en **PDF y HTML** con procedencia embebida.

## Fase 5 — Robustez
- Versionado de datasets (manifiestos/DVC-lite), reproducibilidad bit a bit.
- Revisión metodológica externa antes de cualquier afirmación pública.
- Explicabilidad: por cada indicador, «por qué» (qué filas y fuentes lo sustentan).

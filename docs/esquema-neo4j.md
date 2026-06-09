# Esquema Neo4j (neutral)

El esquema completo (restricciones + modelo) está en
[`src/observatorio/graph/schema.cypher`](../src/observatorio/graph/schema.cypher).

Nodos: `Person` · `GovernmentEntity` · `GovernmentPosition` · `Regime` · `Policy`/`Law` (Fase 2).
Relaciones: `WORKED_AT` · `HELD` · `AT_ENTITY` · `HAS_REGIME` · `SUCCEEDED_BY` · `IMPULSED_DURING` (F2).

No existe nodo `Organization` por causa ni etiqueta de afiliación: el grafo describe el
ejercicio de cargos públicos, no la vida privada ni las ideas de las personas.

Carga: `make graph` (requiere Neo4j de `docker compose up neo4j`).
Analítica de redes (GDS): `gds.degree`, `gds.betweenness`, `gds.pageRank`, `gds.louvain`
sobre el subgrafo de trayectorias entidad↔persona.

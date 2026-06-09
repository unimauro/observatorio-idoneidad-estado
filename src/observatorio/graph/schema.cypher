// Esquema Neo4j — Observatorio de Idoneidad y Capacidad del Estado
// Modelo NEUTRAL: nodos del sector público y sus cargos. NO existe nodo de
// "organización por causa" ni clasificación de personas por ideología/identidad.
// Las personas son funcionarios públicos en el ejercicio de cargos públicos.

// --- Restricciones / índices ---
CREATE CONSTRAINT person_id IF NOT EXISTS
  FOR (p:Person) REQUIRE p.person_id IS UNIQUE;
CREATE CONSTRAINT entity_id IF NOT EXISTS
  FOR (e:GovernmentEntity) REQUIRE e.id_entidad IS UNIQUE;
CREATE CONSTRAINT position_id IF NOT EXISTS
  FOR (g:GovernmentPosition) REQUIRE g.position_id IS UNIQUE;
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.nombre_norm);

// --- Modelo (documentación) ---
// (:Person {person_id, nombre_norm})
// (:GovernmentEntity {id_entidad, nombre, categoria, tipo, ice, meritocracia, estabilidad, capacidad})
// (:GovernmentPosition {position_id, cargo_norm, nivel})
// (:Regime {nombre, merito})              // CAS, Ley Servir, Altos Funcionarios…
// (:Policy {id, nombre})  (:Law {id, nombre})   // FASE 2
//
// Relaciones:
//   (:Person)-[:WORKED_AT {anio_min, anio_max, meses}]->(:GovernmentEntity)
//   (:Person)-[:HELD {start, end, meses, regimen, nivel}]->(:GovernmentPosition)
//   (:GovernmentPosition)-[:AT_ENTITY]->(:GovernmentEntity)
//   (:Person)-[:HAS_REGIME]->(:Regime)
//   (:Person)-[:SUCCEEDED_BY]->(:Person)    // rotación en un mismo cargo (puerta giratoria interna)
//   (:Policy)-[:IMPULSED_DURING]->(:GovernmentPosition)   // FASE 2 (correlación, no causa)
//
// Analítica de redes (GDS): degree, betweenness, PageRank, community detection —
// para identificar entidades/cargos centrales en trayectorias, NUNCA para perfilar
// a personas por afiliación.

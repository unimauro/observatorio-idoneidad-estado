# Metodología y salvaguardas

## Principio rector
El objetivo es **medir capacidad e idoneidad del Estado**, no perfilar personas. El sujeto de
análisis es la **entidad pública y el cargo público**, no la vida privada ni las ideas de nadie.

## Qué medimos y cómo
| Sub-índice | Qué mide | Fuente | Cómputo |
|---|---|---|---|
| Meritocracia | acceso por mérito/carrera vs. confianza/designación | régimen laboral (PTE) | peso por régimen × peso por nivel de decisión |
| Estabilidad | permanencia y rotación en cargos de decisión | serie año/mes (PTE) | permanencia media vs. umbral, ajustada por recambio |
| Capacidad | cobertura, dotación, continuidad | personal por entidad (PTE) | proxy v0 (cobertura temporal + dotación + presencia de decisión) |
| Idoneidad | perfil del puesto vs. credenciales | SERVIR/SUNEDU (Fase 2) | cumplimiento de grado/experiencia/especialidad exigidos |

## Salvaguardas anti-sesgo
1. **Neutralidad por diseño:** el mismo cómputo se aplica a TODAS las entidades; no hay filtros por causa, ideología, género ni identidad. No existe un nodo «organización por causa» ni etiquetas de afiliación.
2. **Idoneidad = perfil, no afiliación:** la idoneidad se evalúa contra el perfil exigido por el puesto (formación y experiencia), nunca contra opiniones o pertenencias.
3. **Correlación ≠ causalidad:** ningún cruce capacidad↔resultados se presenta como causa; se etiqueta explícitamente como asociación.
4. **Procedencia obligatoria:** cada fila conserva `fuente_url` y `captured_at`; toda cifra es rastreable a su origen público.
5. **Pesos auditables:** los pesos del índice viven en `config/indicators.yaml` y se versionan; cambiarlos recomputa y queda en el historial.
6. **Matching solo de identidad propia:** el fuzzy matching sirve para reconciliar los registros del MISMO funcionario en el tiempo (trayectoria), no para vincular personas a terceros. Los matches bajo umbral alto se marcan como tentativos; el DNI, cuando exista, manda.

## Limitaciones declaradas
- El régimen es un **proxy** de meritocracia, no una medición directa del proceso de selección.
- Sin datos de credenciales (Fase 2), la idoneidad individual **no se afirma**: se reporta como dato faltante, no como cero.
- La capacidad v0 es un proxy operativo; se refinará con ejecución presupuestal y vacancias.
- Los homónimos pueden inflar trayectorias hasta incorporar el DNI; se trata como incertidumbre, no como hecho.

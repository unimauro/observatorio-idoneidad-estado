# Modelo de datos

## Origen (peru-transparente)
- `funcionarios.csv` — `id_entidad, entidad, anio, mes, regimen, apellidos_nombres, cargo, dependencia, total_ingreso_mensual, fuente_url, captured_at` (≈213k filas).
- `funcionarios_clave.csv` — igual + `nivel` (Director/a, Viceministro…).
- `entidades.csv` — `id_entidad, nombre, categoria, tipo_label`.
- `autoridades.csv` — autoridades nominales por institución (gob.pe).

## Tablas derivadas (DuckDB / Parquet)
**`personal`** (hecho, una fila por persona-entidad-mes)
| columna | tipo | nota |
|---|---|---|
| person_id | str | sha1 de la clave de identidad normalizada |
| id_entidad, entidad | str | |
| anio, mes | int | periodo = anio·12+mes |
| regimen | str | CAS, Ley Servir, Altos Funcionarios… |
| cargo_norm | str | cargo normalizado (sin tildes, mayúsculas) |
| nivel | str | nivel de decisión derivado del cargo |
| ingreso | float | total_ingreso_mensual |
| fuente_url, captured_at | str | **procedencia** |

**`ice_entidad`** (una fila por entidad)
`id_entidad, nombre, categoria, tipo_label, meritocracia, pct_merito, pct_confianza, n_personal, estabilidad, permanencia_media_meses, rotacion_cargos_decision, capacidad, meses_cubiertos, n_personal_unico, idoneidad, ice, nivel_ice`.

## Identidad de persona
`person_id = sha1(tokens_ordenados(nombre_normalizado))`. Reconcilia el mismo funcionario entre
meses y entidades para medir trayectoria. **Riesgo de homónimos** hasta incorporar DNI (Fase 2);
se trata como incertidumbre. Ningún `person_id` se enriquece con datos privados ni de afiliación.

# Observatorio de Idoneidad y Capacidad del Estado peruano 🏛️

Plataforma de investigación, **100 % local y con datos públicos**, para medir de forma
**objetiva y neutral** si el Estado peruano cuenta con personal idóneo y capacidad
institucional suficiente para atender bien a la población —en especial a la más vulnerable.

> **Propósito (sin sesgo de diseño).** No mide si una persona u organización es «buena»
> o «mala», ni clasifica a nadie por ideología, identidad o afiliación. Mide, sobre **toda**
> entidad por igual: acceso por mérito vs. designación, estabilidad/rotación en cargos de
> decisión, capacidad operativa y —en Fase 2— idoneidad (perfil del puesto vs. credenciales).
> Que **los datos hablen**: alta capacidad puede coincidir con buenos o malos resultados;
> el observatorio describe, no concluye. **Correlación ≠ causalidad.**

## Qué responde

- ¿Qué entidades acceden a sus cargos por **mérito/carrera** y cuáles por **confianza/designación**?
- ¿Dónde hay **alta rotación** en cargos de decisión (que erosiona la continuidad del servicio)?
- ¿Cómo se distribuye la **capacidad institucional** y cómo se relaciona con la calidad del servicio? *(correlación)*
- ¿Cumple quien ocupa un cargo el **perfil exigido** por ese puesto? *(Fase 2, requiere ingesta de credenciales)*

## Índice ICE (Idoneidad y Capacidad del Estado)

`ICE = 0.35·meritocracia + 0.35·estabilidad + 0.30·capacidad` (+ idoneidad en Fase 2).
Pesos **configurables y auditables** en [`config/indicators.yaml`](config/indicators.yaml).

## Stack (local-first)

Python · **DuckDB** · **Parquet** (intermedios versionables) · **Neo4j** · FastAPI · Streamlit · Docker.
Sin nube, sin costos. Publicación posterior (Fase 4) estática/semiestática y **protegida** hasta validar.

## Cómo correr

```bash
pip install -r requirements.txt
cp .env.example .env                 # apunta PT_DATA_DIR a ../peru-transparente/data
make etl                             # construye DuckDB + Parquet + índice ICE
make dashboard                       # Streamlit en http://localhost:8501
make api                             # FastAPI en http://localhost:8000/docs
docker compose up neo4j && make graph  # carga el grafo neutral en Neo4j
make test
```

## Fuentes

- [`peru-transparente`](https://github.com/unimauro/peru-transparente): personal del Estado por
  entidad/cargo/régimen/periodo (Portal de Transparencia Estándar), con `fuente_url` por fila.
- Fase 2: SERVIR (perfiles y declaraciones juradas), SUNEDU (grados), MEF (ejecución), INEI/MIMP (indicadores de servicio).

## Principios

1. Solo fuentes públicas. 2. Procedencia (`fuente_url`) en cada dato. 3. Trazabilidad completa.
4. Sin perfilamiento por ideología/identidad. 5. Solo evidencia verificable. 6. Correlación ≠ causalidad.

Ver [`docs/metodologia.md`](docs/metodologia.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`ROADMAP.md`](ROADMAP.md).

import pandas as pd
from observatorio.config import load_indicators
from observatorio.metrics import meritocracia, indice


def test_meritocracia_pondera_por_nivel():
    cfg = load_indicators()
    df = pd.DataFrame([
        {"id_entidad": "1", "regimen": "Ley Servir", "nivel": "Director/a"},
        {"id_entidad": "1", "regimen": "Altos Funcionarios", "nivel": "Operativo"},
    ])
    out = meritocracia.score_entidad(df, cfg).iloc[0]
    # el cargo de decisión (mérito alto) pesa más que el operativo de confianza
    assert out["meritocracia"] > 0.5


def test_ice_en_rango_0_1():
    cfg = load_indicators()
    merit = pd.DataFrame([{"id_entidad": "1", "meritocracia": 0.9, "n_personal": 10}])
    estab = pd.DataFrame([{"id_entidad": "1", "estabilidad": 0.8}])
    cap = pd.DataFrame([{"id_entidad": "1", "capacidad": 0.7}])
    out = indice.compute(merit, estab, cap, cfg)
    assert 0.0 <= out.iloc[0]["ice"] <= 1.0
    assert out.iloc[0]["nivel_ice"] in {"bajo", "medio", "alto"}

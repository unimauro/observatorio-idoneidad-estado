import math
from observatorio.metrics.idoneidad import score_persona


def test_cumple_perfil_completo():
    cred = {"grado": "maestria", "anios_experiencia": 8, "especialidad": "gestión pública"}
    perfil = {"grado_min": "titulo", "anios_min": 5, "especialidades": ["gestión pública"]}
    assert score_persona(cred, perfil) == 1.0


def test_no_cumple_experiencia():
    cred = {"grado": "titulo", "anios_experiencia": 2, "especialidad": "derecho"}
    perfil = {"grado_min": "titulo", "anios_min": 5, "especialidades": ["derecho"]}
    assert score_persona(cred, perfil) < 1.0


def test_sin_perfil_no_se_afirma():
    # sin perfil de referencia, la idoneidad es NaN (dato ausente, no cero)
    assert math.isnan(score_persona({"grado": "titulo"}, {}))

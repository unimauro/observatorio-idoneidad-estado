from observatorio.etl.normalize import (
    norm_nombre, identity_key, same_person_score, nivel_desde_cargo,
)


def test_norm_nombre_reordena_y_limpia():
    assert norm_nombre("PÉREZ GÓMEZ, María Elena") == "MARIA ELENA PEREZ GOMEZ"
    assert norm_nombre("ABANTO CHAVEZ, WALTER JAIME") == "WALTER JAIME ABANTO CHAVEZ"


def test_identity_key_orden_independiente():
    assert identity_key(norm_nombre("PÉREZ, María")) == identity_key(norm_nombre("María PÉREZ"))


def test_same_person_score():
    a = norm_nombre("PEREZ GOMEZ, Maria Elena")
    assert same_person_score(a, a) == 1.0
    assert same_person_score(a, norm_nombre("PEREZ GOMEZ, Maria")) >= 0.6
    assert same_person_score(a, norm_nombre("QUISPE MAMANI, Jose")) < 0.6


def test_nivel_desde_cargo():
    assert nivel_desde_cargo("VICEMINISTRO DE LA MUJER") == "Viceministro"
    assert nivel_desde_cargo("DIRECTOR GENERAL DE PRESUPUESTO") == "Director/a"
    assert nivel_desde_cargo("ASISTENTE ADMINISTRATIVO") == "Operativo"
    assert nivel_desde_cargo("cualquiera", nivel="Gerente") == "Gerente"

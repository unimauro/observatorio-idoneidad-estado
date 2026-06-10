import pandas as pd
from observatorio.metrics import redes


def _personal(rows):
    return pd.DataFrame(rows, columns=["person_id", "id_entidad"])


def test_arista_si_persona_en_dos_entidades():
    p = _personal([("p1", "A"), ("p1", "B"), ("p2", "A")])
    g = redes.build_graph(p)
    assert g.has_edge("A", "B")
    assert g["A"]["B"]["weight"] == 1


def test_peso_acumula_personas_compartidas():
    p = _personal([("p1", "A"), ("p1", "B"), ("p2", "A"), ("p2", "B")])
    g = redes.build_graph(p)
    assert g["A"]["B"]["weight"] == 2


def test_sin_movilidad_grafo_vacio():
    p = _personal([("p1", "A"), ("p2", "B")])
    cent, edges = redes.centralidad(p)
    assert edges.empty and cent.empty


def test_centralidad_tiene_columnas():
    p = _personal([("p1", "A"), ("p1", "B"), ("p2", "B"), ("p2", "C")])
    cent, edges = redes.centralidad(p)
    assert set(["id_entidad", "pagerank", "betweenness", "grado", "comunidad"]).issubset(cent.columns)
    assert len(cent) == 3

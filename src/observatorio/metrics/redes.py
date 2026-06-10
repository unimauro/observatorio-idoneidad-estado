"""Red de MOVILIDAD INSTITUCIONAL (neutral, a nivel de entidad).

Dos entidades se conectan si comparten personas que pasaron por ambas (peso = nº de
personas compartidas). Mide qué entidades son "hubs" de circulación de personal —útil
para ver concentración/circulación institucional—. NO perfila personas: el grafo es
entidad↔entidad. Centralidad con PageRank/betweenness/grado y detección de comunidades.
"""
from __future__ import annotations
from itertools import combinations
import pandas as pd
import networkx as nx
from networkx.algorithms import community as nx_comm


def build_graph(personal: pd.DataFrame) -> nx.Graph:
    # personas que pasaron por 2+ entidades
    pe = personal.groupby("person_id")["id_entidad"].apply(lambda s: sorted(set(s)))
    pares: dict[tuple, int] = {}
    for entidades in pe:
        if len(entidades) < 2:
            continue
        for a, b in combinations(entidades, 2):
            pares[(a, b)] = pares.get((a, b), 0) + 1
    g = nx.Graph()
    for (a, b), w in pares.items():
        g.add_edge(a, b, weight=w)
    return g


def centralidad(personal: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (centralidad_por_entidad, aristas)."""
    g = build_graph(personal)
    if g.number_of_nodes() == 0:
        return (pd.DataFrame(columns=["id_entidad", "pagerank", "betweenness", "grado", "comunidad"]),
                pd.DataFrame(columns=["origen", "destino", "peso"]))

    pr = nx.pagerank(g, weight="weight")
    deg = dict(g.degree())
    # betweenness con distancia = 1/peso (más personas compartidas = más "cerca")
    bet = nx.betweenness_centrality(g, weight=lambda u, v, d: 1.0 / d["weight"], normalized=True)
    comms = nx_comm.greedy_modularity_communities(g, weight="weight")
    com_of = {n: i for i, c in enumerate(comms) for n in c}

    cent = pd.DataFrame({
        "id_entidad": list(g.nodes()),
        "pagerank": [round(pr[n], 6) for n in g.nodes()],
        "betweenness": [round(bet[n], 6) for n in g.nodes()],
        "grado": [deg[n] for n in g.nodes()],
        "comunidad": [com_of[n] for n in g.nodes()],
    })
    edges = pd.DataFrame([(a, b, d["weight"]) for a, b, d in g.edges(data=True)],
                         columns=["origen", "destino", "peso"]).sort_values("peso", ascending=False)
    return cent, edges

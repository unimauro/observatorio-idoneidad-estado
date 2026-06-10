import pandas as pd
from observatorio.metrics import sectores


def test_consolida_por_patron():
    ice = pd.DataFrame([
        {"id_entidad": "1", "nombre": "MINISTERIO DE SALUD (MINSA)", "ice": 0.4, "n_personal": 100, "meritocracia": 0.5},
        {"id_entidad": "2", "nombre": "HOSPITAL CAYETANO HEREDIA", "ice": 0.6, "n_personal": 300, "meritocracia": 0.9},
        {"id_entidad": "3", "nombre": "MINISTERIO DE EDUCACION", "ice": 0.5, "n_personal": 50, "meritocracia": 0.7},
    ])
    personal = pd.DataFrame([
        {"id_entidad": "1", "person_id": "a", "regimen": "CAS", "nivel": "Ministro/Titular", "cargo_norm": "MINISTRO", "ingreso": 30000},
        {"id_entidad": "2", "person_id": "b", "regimen": "Ley Servir", "nivel": "Director/a", "cargo_norm": "DIRECTOR", "ingreso": 12000},
        {"id_entidad": "3", "person_id": "c", "regimen": "CAS", "nivel": "Operativo", "cargo_norm": "ASISTENTE", "ingreso": 4000},
    ])
    cfg = [{"clave": "MINSA", "nombre": "Salud", "central": "1", "patron": r"\bSALUD\b|MINSA|HOSPITAL"}]
    out = sectores.consolidar(personal, ice, cfg)
    assert len(out) == 1
    s = out[0]
    assert s["clave"] == "MINSA"
    assert s["n_entidades"] == 2            # MINSA + Hospital, no Educación
    # ICE ponderado por personal: (0.4*100 + 0.6*300)/400 = 0.55
    assert abs(s["ice_ponderado"] - 0.55) < 1e-6
    assert s["n_decision"] == 2             # Ministro + Director


def test_sector_sin_match_se_omite():
    ice = pd.DataFrame([{"id_entidad": "1", "nombre": "OTRA COSA", "ice": 0.5, "n_personal": 10, "meritocracia": 0.5}])
    personal = pd.DataFrame([{"id_entidad": "1", "person_id": "a", "regimen": "CAS", "nivel": "Operativo", "cargo_norm": "X", "ingreso": None}])
    out = sectores.consolidar(personal, ice, [{"clave": "Z", "nombre": "Z", "central": "9", "patron": "NOEXISTE"}])
    assert out == []

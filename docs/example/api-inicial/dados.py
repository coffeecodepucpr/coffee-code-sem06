"""Dados de exemplo da API, guardados em memória.

Não existe banco de dados: tudo volta ao estado inicial quando o servidor reinicia.
"""
import itertools
from datetime import datetime, timezone


def _data(dia: int) -> datetime:
    return datetime(2026, 9, dia, 12, 0, tzinfo=timezone.utc)


MATERIAS = {
    1: {"materia_id": 1, "nome": "Cálculo I", "codigo": "MAT101"},
    2: {"materia_id": 2, "nome": "Estrutura de Dados", "codigo": "INF201"},
    3: {"materia_id": 3, "nome": "Banco de Dados", "codigo": "INF301"},
    4: {"materia_id": 4, "nome": "Engenharia de Software", "codigo": "INF305"},
    5: {"materia_id": 5, "nome": "Redes de Computadores", "codigo": "INF310"},
    6: {"materia_id": 6, "nome": "Sistemas Operacionais", "codigo": "INF315"},
}

GRUPOS = {
    1: {"grupo_id": 1, "nome_grupo": "Cálculo passo a passo", "materia_id": 1,
        "max_participantes": 6, "descricao": None, "criado_em": _data(1)},
    2: {"grupo_id": 2, "nome_grupo": "Estruturas na prática", "materia_id": 2,
        "max_participantes": 5, "descricao": None, "criado_em": _data(2)},
    3: {"grupo_id": 3, "nome_grupo": "Modelagem e SQL", "materia_id": 3,
        "max_participantes": 8, "descricao": "Encontros online às terças e aos sábados",
        "criado_em": _data(3)},
    4: {"grupo_id": 4, "nome_grupo": "Requisitos e histórias", "materia_id": 4,
        "max_participantes": 5, "descricao": None, "criado_em": _data(4)},
    5: {"grupo_id": 5, "nome_grupo": "Redes na unha", "materia_id": 5,
        "max_participantes": 6, "descricao": None, "criado_em": _data(5)},
    6: {"grupo_id": 6, "nome_grupo": "Processos e memória", "materia_id": 6,
        "max_participantes": 4, "descricao": None, "criado_em": _data(6)},
}

CONTADOR_GRUPOS = itertools.count(7)

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "veterano" / "api"))

import pytest
from fastapi.testclient import TestClient

import dados
import main

GRUPOS_INICIAIS = {k: dict(v) for k, v in dados.GRUPOS.items()}
PAGINA = "http://127.0.0.1:5500"


@pytest.fixture(autouse=True)
def dados_limpos():
    dados.GRUPOS.clear()
    dados.GRUPOS.update({k: dict(v) for k, v in GRUPOS_INICIAIS.items()})
    dados.CONTADOR_GRUPOS = itertools.count(7)


@pytest.fixture
def client():
    return TestClient(main.app)

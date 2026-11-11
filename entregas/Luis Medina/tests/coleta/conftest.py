import json
import threading
import time

import pytest
import requests

from coleta import banco, config
from coleta.api_simulada import criar_servidor

PORTA_TESTE = 8199
URL_TESTE = f"http://127.0.0.1:{PORTA_TESTE}"


@pytest.fixture(scope="session")
def servidor_ml():
    servidor = criar_servidor(porta=PORTA_TESTE)
    fio = threading.Thread(target=servidor.serve_forever, daemon=True)
    fio.start()
    for _ in range(50):
        try:
            requests.get(URL_TESTE + "/_dev/reset", timeout=0.2)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    yield URL_TESTE
    servidor.shutdown()


@pytest.fixture(autouse=True)
def resetar_servidor(servidor_ml):
    requests.get(servidor_ml + "/_dev/reset", timeout=1)
    yield


@pytest.fixture
def ambiente_api(tmp_path, monkeypatch, servidor_ml):
    """Aponta o pipeline pro servidor falso, com um token inicial válido."""
    monkeypatch.setattr(config, "API_BASE", servidor_ml)
    monkeypatch.setattr(config, "CLIENT_ID", "id-de-teste")
    monkeypatch.setattr(config, "CLIENT_SECRET", "segredo-de-teste")
    monkeypatch.setattr(config, "TOKENS_CAMINHO", tmp_path / "ml_tokens.json")
    monkeypatch.setattr(config, "ESPERA_ENTRE_PEDIDOS_SEGUNDOS", 0.0)
    (tmp_path / "ml_tokens.json").write_text(
        json.dumps({"access_token": "tok-1", "refresh_token": "ref-1"}), encoding="utf-8"
    )
    return servidor_ml


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    caminho = tmp_path / "coleta.db"
    monkeypatch.setattr(config, "BANCO_CAMINHO", caminho)
    conexao = banco.conectar(caminho)
    yield conexao
    conexao.close()

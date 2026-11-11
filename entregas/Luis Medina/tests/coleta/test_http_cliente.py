import pytest
import requests

from coleta import config
from coleta.http_cliente import ClienteML


@pytest.fixture
def cliente_rapido(ambiente_api, monkeypatch):
    monkeypatch.setattr(config, "ESPERA_INICIAL_SEGUNDOS", 0.01)
    return ClienteML()


def test_token_vencido_e_renovado_automaticamente(ambiente_api):
    import json
    config.TOKENS_CAMINHO.write_text(
        json.dumps({"access_token": "token-invalido", "refresh_token": "ref-1"}), encoding="utf-8"
    )
    cliente = ClienteML()
    resposta = cliente.get("/items?ids=MLB001")
    assert resposta.status_code == 200  # funcionou depois de renovar sozinho


def test_404_nao_e_repetido(cliente_rapido):
    with pytest.raises(requests.exceptions.HTTPError):
        cliente_rapido.get("/caminho-que-nao-existe")


def test_503_e_repetido_ate_funcionar(cliente_rapido):
    resposta = cliente_rapido.get("/items?ids=MLB001&simular=503&falhas=2")
    assert resposta.status_code == 200


def test_429_e_repetido_ate_funcionar(cliente_rapido):
    resposta = cliente_rapido.get("/items?ids=MLB001&simular=429&falhas=2")
    assert resposta.status_code == 200


def test_toda_requisicao_tem_timeout():
    assert config.TIMEOUT_SEGUNDOS > 0

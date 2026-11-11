import json

import pytest

from coleta import auth, config
from coleta.auth import TokenIndisponivel


def test_access_token_atual_le_do_arquivo(ambiente_api):
    assert auth.access_token_atual() == "tok-1"


def test_renovar_troca_o_token_e_salva_o_novo(ambiente_api):
    novo = auth.renovar()
    assert novo == "tok-2"
    estado = json.loads(config.TOKENS_CAMINHO.read_text(encoding="utf-8"))
    assert estado["access_token"] == "tok-2"
    assert estado["refresh_token"] == "ref-2"  # o Mercado Livre troca o refresh_token a cada uso


def test_renovar_duas_vezes_seguidas_funciona_porque_usa_o_refresh_novo(ambiente_api):
    auth.renovar()
    terceiro = auth.renovar()
    assert terceiro == "tok-3"


def test_usar_refresh_token_velho_falha(ambiente_api):
    auth.renovar()  # agora o refresh salvo é "ref-2"; "ref-1" já foi usado
    config.TOKENS_CAMINHO.write_text(json.dumps({"access_token": "tok-x", "refresh_token": "ref-1"}), encoding="utf-8")
    with pytest.raises(TokenIndisponivel):
        auth.renovar()


def test_sem_client_id_nao_renova(ambiente_api, monkeypatch):
    monkeypatch.setattr(config, "CLIENT_ID", None)
    with pytest.raises(TokenIndisponivel):
        auth.renovar()

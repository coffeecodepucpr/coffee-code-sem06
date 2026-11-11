from coleta.coletores import coletar_produtos
from coleta.http_cliente import ClienteML


def test_coleta_produtos_conhecidos(ambiente_api):
    cliente = ClienteML()
    resultado = coletar_produtos(cliente, ["MLB001", "MLB002"])
    assert resultado.completa is True
    assert len(resultado.itens) == 2
    titulos = {item["titulo"] for item in resultado.itens}
    assert titulos == {"Teclado mecânico", "Mouse sem fio"}


def test_produto_que_nao_existe_e_ignorado_sem_quebrar_a_coleta(ambiente_api):
    cliente = ClienteML()
    resultado = coletar_produtos(cliente, ["MLB001", "MLB999-NAO-EXISTE"])
    assert resultado.completa is True  # 404 de item não é falha transitória
    assert len(resultado.itens) == 1
    assert resultado.itens[0]["id_externo"] == "MLB001"


def test_limite_de_lotes(ambiente_api, monkeypatch):
    from coleta import config
    monkeypatch.setattr(config, "TAMANHO_LOTE", 1)
    monkeypatch.setattr(config, "MAX_LOTES", 1)
    cliente = ClienteML()
    resultado = coletar_produtos(cliente, ["MLB001", "MLB002"])
    assert resultado.completa is False
    assert resultado.motivo_incompleta == "limite_lotes"
    assert len(resultado.itens) == 1

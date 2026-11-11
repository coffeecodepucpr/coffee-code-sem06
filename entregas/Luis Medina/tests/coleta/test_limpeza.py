from coleta import limpeza


def test_preco_simples_vira_centavos():
    assert limpeza.limpar_preco_centavos(349.90) == 34990


def test_preco_com_arredondamento_de_ponto_flutuante():
    assert limpeza.limpar_preco_centavos(10.1) == 1010  # não pode virar 1009 por erro de float


def test_preco_ausente_vira_none():
    assert limpeza.limpar_preco_centavos(None) is None


def test_quantidade_zero_nao_e_tratada_como_ausente():
    bruto = {"id_externo": "MLB1", "titulo": "X", "quantidade_disponivel": 0}
    assert limpeza.limpar_produto(bruto)["quantidade_disponivel"] == 0


def test_item_valido_falso_sem_titulo():
    assert limpeza.item_valido({"id_externo": "MLB1", "titulo": None}, ["id_externo", "titulo"]) is False


def test_item_valido_verdadeiro():
    assert limpeza.item_valido({"id_externo": "MLB1", "titulo": "X"}, ["id_externo", "titulo"]) is True


def test_limpar_produto_mantem_status_e_permalink():
    bruto = {
        "id_externo": "MLB1", "titulo": "  Teclado  mecânico ", "preco": 349.9, "moeda": "BRL",
        "quantidade_disponivel": 5, "status": "active", "permalink": "https://x",
        "atualizado_na_origem": "2026-10-01T10:00:00.000-03:00",
    }
    limpo = limpeza.limpar_produto(bruto)
    assert limpo["titulo"] == "Teclado mecânico"
    assert limpo["preco_centavos"] == 34990
    assert limpo["status"] == "active"

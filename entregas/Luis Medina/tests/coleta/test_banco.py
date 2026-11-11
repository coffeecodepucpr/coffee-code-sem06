import sqlite3

from coleta import banco


def _produto(id_externo="MLB001", **sobrescritas):
    base = {
        "id_externo": id_externo, "titulo": "Teclado mecânico", "preco_centavos": 34990,
        "moeda": "BRL", "quantidade_disponivel": 5, "status": "active",
        "permalink": "https://produto.mercadolivre.com.br/MLB001",
        "atualizado_na_origem": "2026-10-01T10:00:00.000-03:00",
    }
    base.update(sobrescritas)
    return base


def test_esquema_tem_unique_fonte_id_externo(banco_temporario):
    banco_temporario.execute(
        "INSERT INTO produtos_coletados (fonte, id_externo, titulo, ativa, primeira_vez_em, atualizada_em) "
        "VALUES ('x', 'MLB1', 't', 1, 'a', 'a')"
    )
    try:
        banco_temporario.execute(
            "INSERT INTO produtos_coletados (fonte, id_externo, titulo, ativa, primeira_vez_em, atualizada_em) "
            "VALUES ('x', 'MLB1', 't2', 1, 'a', 'a')"
        )
        assert False, "deveria ter rejeitado id_externo duplicado pra mesma fonte"
    except sqlite3.IntegrityError:
        pass


def test_salvar_produto_insere_como_novo(banco_temporario):
    contagem = banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto()])
    assert contagem == {"nova": 1, "atualizada": 0, "igual": 0}


def test_rodar_duas_vezes_nao_duplica(banco_temporario):
    banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto()])
    contagem = banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto()])
    assert contagem == {"nova": 0, "atualizada": 0, "igual": 1}
    total = banco_temporario.execute("SELECT COUNT(*) FROM produtos_coletados").fetchone()[0]
    assert total == 1


def test_mudanca_de_preco_classifica_como_atualizada(banco_temporario):
    banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto()])
    contagem = banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto(preco_centavos=29990)])
    assert contagem == {"nova": 0, "atualizada": 1, "igual": 0}


def test_inativar_sumidos_marca_ativa_zero(banco_temporario):
    banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto("MLB001"), _produto("MLB002")])
    inativadas = banco.inativar_sumidos(banco_temporario, "mercado-livre", {"MLB001"})
    assert inativadas == 1
    status = dict(banco_temporario.execute("SELECT id_externo, ativa FROM produtos_coletados").fetchall())
    assert status == {"MLB001": 1, "MLB002": 0}


def test_produto_que_reaparece_e_reativado(banco_temporario):
    banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto("MLB001"), _produto("MLB002")])
    banco.inativar_sumidos(banco_temporario, "mercado-livre", {"MLB001"})
    banco.salvar_produtos(banco_temporario, "mercado-livre", [_produto("MLB001"), _produto("MLB002")])
    ativa = banco_temporario.execute("SELECT ativa FROM produtos_coletados WHERE id_externo = 'MLB002'").fetchone()[0]
    assert ativa == 1


def test_registrar_historico_acrescenta_uma_linha_por_item(banco_temporario):
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001"), _produto("MLB002")])
    total = banco_temporario.execute("SELECT COUNT(*) FROM historico_precos").fetchone()[0]
    assert total == 2


def test_registrar_historico_nao_sobrescreve_coletas_anteriores(banco_temporario):
    # mesma chamada duas vezes = duas linhas, mesmo com o preço igual — é um log, não um upsert
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=34990)])
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=34990)])
    total = banco_temporario.execute("SELECT COUNT(*) FROM historico_precos").fetchone()[0]
    assert total == 2


def test_registrar_historico_com_lista_vazia_nao_grava_nada(banco_temporario):
    banco.registrar_historico(banco_temporario, "mercado-livre", [])
    total = banco_temporario.execute("SELECT COUNT(*) FROM historico_precos").fetchone()[0]
    assert total == 0


def test_historico_do_produto_devolve_em_ordem_cronologica(banco_temporario):
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=10000)])
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=9000)])
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=8000)])
    historico = banco.historico_do_produto(banco_temporario, "mercado-livre", "MLB001")
    assert [linha["preco_centavos"] for linha in historico] == [10000, 9000, 8000]


def test_historico_do_produto_respeita_o_limite(banco_temporario):
    for preco in (10000, 9000, 8000, 7000):
        banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=preco)])
    historico = banco.historico_do_produto(banco_temporario, "mercado-livre", "MLB001", limite=2)
    # as 2 últimas (mais recentes), ainda em ordem cronológica
    assert [linha["preco_centavos"] for linha in historico] == [8000, 7000]


def test_historico_do_produto_nao_mistura_outro_produto(banco_temporario):
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB001", preco_centavos=10000)])
    banco.registrar_historico(banco_temporario, "mercado-livre", [_produto("MLB002", preco_centavos=5000)])
    historico = banco.historico_do_produto(banco_temporario, "mercado-livre", "MLB001")
    assert len(historico) == 1
    assert historico[0]["preco_centavos"] == 10000


def test_execucao_registra_status_e_resumo(banco_temporario):
    execucao_id = banco.iniciar_execucao(banco_temporario)
    banco.finalizar_execucao(banco_temporario, execucao_id, "sucesso", 1, 0, 0, 0, "ok")
    linha = banco_temporario.execute(
        "SELECT status, novas, resumo FROM execucoes WHERE id = ?", (execucao_id,)
    ).fetchone()
    assert linha == ("sucesso", 1, "ok")

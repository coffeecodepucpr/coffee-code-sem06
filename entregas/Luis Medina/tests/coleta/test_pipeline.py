"""Teste de ponta a ponta: roda o pipeline de verdade contra a API falsa."""
import sqlite3

import requests

from coleta import config, executar
from coleta.executar import JaEmExecucao, _Trava


def _preparar(tmp_path, monkeypatch, ambiente_api, ids=("MLB001", "MLB002", "MLB003")):
    monkeypatch.setattr(config, "BANCO_CAMINHO", tmp_path / "coleta.db")
    monkeypatch.setattr(config, "LOG_CAMINHO", tmp_path / "coleta.log")
    monkeypatch.setattr(config, "LOCK_CAMINHO", tmp_path / "coleta.lock")
    arquivo = tmp_path / "produtos_monitorados.txt"
    arquivo.write_text(
        "\n".join(f"https://produto.mercadolivre.com.br/{id_}-x" for id_ in ids), encoding="utf-8"
    )
    monkeypatch.setattr(config, "PRODUTOS_MONITORADOS_CAMINHO", arquivo)


def test_primeira_execucao_cria_tudo(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    codigo = executar.main()
    assert codigo == 0
    c = sqlite3.connect(config.BANCO_CAMINHO)
    assert c.execute("SELECT COUNT(*) FROM produtos_coletados").fetchone()[0] == 3


def test_segunda_execucao_nao_duplica(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    executar.main()
    codigo = executar.main()
    assert codigo == 0
    c = sqlite3.connect(config.BANCO_CAMINHO)
    assert c.execute("SELECT COUNT(*) FROM produtos_coletados").fetchone()[0] == 3
    status, iguais = c.execute("SELECT status, iguais FROM execucoes ORDER BY id DESC LIMIT 1").fetchone()
    assert (status, iguais) == ("sucesso", 3)


def test_produto_removido_e_inativado_sem_apagar(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    executar.main()
    requests.get(ambiente_api + "/_dev/remover?id=MLB002", timeout=1)
    codigo = executar.main()
    assert codigo == 0
    c = sqlite3.connect(config.BANCO_CAMINHO)
    ativa = c.execute("SELECT ativa FROM produtos_coletados WHERE id_externo = 'MLB002'").fetchone()[0]
    assert ativa == 0
    total = c.execute("SELECT COUNT(*) FROM produtos_coletados").fetchone()[0]
    assert total == 3  # continua no banco, só inativo


def test_mudanca_de_preco_classifica_como_atualizada(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    executar.main()
    requests.get(ambiente_api + "/_dev/preco?id=MLB001&valor=299.90", timeout=1)
    executar.main()
    c = sqlite3.connect(config.BANCO_CAMINHO)
    preco, atualizadas = c.execute(
        "SELECT preco_centavos FROM produtos_coletados WHERE id_externo = 'MLB001'"
    ).fetchone()[0], c.execute("SELECT atualizadas FROM execucoes ORDER BY id DESC LIMIT 1").fetchone()[0]
    assert preco == 29990
    assert atualizadas == 1


def test_historico_acumula_uma_linha_por_execucao(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    executar.main()  # dia 1
    executar.main()  # dia 2, preço igual
    requests.get(ambiente_api + "/_dev/preco?id=MLB001&valor=299.90", timeout=1)
    executar.main()  # dia 3, preço mudou
    c = sqlite3.connect(config.BANCO_CAMINHO)
    precos = [
        linha[0] for linha in c.execute(
            "SELECT preco_centavos FROM historico_precos WHERE id_externo = 'MLB001' ORDER BY id"
        ).fetchall()
    ]
    # 3 execuções = 3 linhas no histórico, mesmo a do meio tendo preço "igual"
    assert precos == [34990, 34990, 29990]


def test_execucao_parcial_ainda_registra_historico_dos_itens_coletados(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    # Força uma coleta PARCIAL (mesmo truque do test_coletores.py): com 3
    # produtos monitorados, 1 por lote e no máximo 2 lotes, o 3º produto
    # fica de fora e a execução termina incompleta.
    monkeypatch.setattr(config, "TAMANHO_LOTE", 1)
    monkeypatch.setattr(config, "MAX_LOTES", 2)
    codigo = executar.main()
    assert codigo == 1  # status "parcial"
    c = sqlite3.connect(config.BANCO_CAMINHO)
    status = c.execute("SELECT status FROM execucoes ORDER BY id DESC LIMIT 1").fetchone()[0]
    assert status == "parcial"
    total = c.execute("SELECT COUNT(*) FROM historico_precos").fetchone()[0]
    assert total == 2  # só os 2 que realmente foram coletados, não os 3 monitorados


def test_sem_produtos_monitorados_falha_sem_inativar_nada(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    executar.main()  # popula o banco normalmente primeiro
    monkeypatch.setattr(config, "PRODUTOS_MONITORADOS_CAMINHO", tmp_path / "vazio.txt")
    codigo = executar.main()
    assert codigo == 2
    c = sqlite3.connect(config.BANCO_CAMINHO)
    ativos = c.execute("SELECT COUNT(*) FROM produtos_coletados WHERE ativa = 1").fetchone()[0]
    assert ativos == 3  # não apagou nada só porque a lista veio vazia


def test_execucao_concorrente_e_barrada_pela_trava(tmp_path, monkeypatch, ambiente_api):
    _preparar(tmp_path, monkeypatch, ambiente_api)
    caminho_trava = tmp_path / "coleta.lock"
    with _Trava(caminho_trava):
        try:
            with _Trava(caminho_trava):
                assert False, "não deveria conseguir travar duas vezes"
        except JaEmExecucao:
            pass

"""Liga os preços coletados (coleta/) aos produtos exibidos pela API.

Não muda o formato dos produtos nem o banco da coleta: só lê a tabela
produtos_coletados e sobrepõe precoAtual/ultimaVerificacao nos produtos cuja
URL a gente reconhece (mesmo id_externo do Mercado Livre, ver
coleta/mapeamento.py).

Se o banco da coleta ainda não existir (nenhuma coleta rodou ainda), os
produtos voltam sem alteração — não é erro, só não tem dado novo ainda.
"""
from __future__ import annotations

import sqlite3

from coleta import config, mapeamento


def _buscar_coletados() -> dict[str, dict]:
    """Devolve {id_externo: {preco_centavos, atualizado_na_origem}} dos ativos."""
    caminho = config.BANCO_CAMINHO
    if not caminho.exists():
        return {}

    conexao = sqlite3.connect(caminho)
    try:
        linhas = conexao.execute(
            "SELECT id_externo, preco_centavos, atualizado_na_origem "
            "FROM produtos_coletados WHERE fonte = ? AND ativa = 1",
            (config.FONTE,),
        ).fetchall()
    finally:
        conexao.close()

    return {
        id_externo: {"preco_centavos": preco_centavos, "atualizado_na_origem": atualizado}
        for id_externo, preco_centavos, atualizado in linhas
    }


def aplicar_precos_coletados(produtos: list[dict]) -> list[dict]:
    """Devolve uma CÓPIA da lista de produtos, com precoAtual/ultimaVerificacao
    atualizados pra quem a coleta encontrou. Quem não tem id reconhecido, ou
    ainda não foi coletado, volta como estava — nunca altera dados.produtos
    direto, pra não misturar dado de demonstração com dado real sem querer.
    """
    coletados = _buscar_coletados()
    if not coletados:
        return produtos

    resultado = []
    for produto in produtos:
        id_externo = mapeamento.extrair_id_externo(produto.get("url", ""))
        dado = coletados.get(id_externo) if id_externo else None

        if dado is None or dado["preco_centavos"] is None:
            resultado.append(produto)
            continue

        produto_atualizado = dict(produto)
        produto_atualizado["precoAtual"] = dado["preco_centavos"] / 100
        produto_atualizado["ultimaVerificacao"] = dado["atualizado_na_origem"]
        resultado.append(produto_atualizado)

    return resultado

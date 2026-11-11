from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from coleta import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS produtos_coletados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte TEXT NOT NULL,
    id_externo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    preco_centavos INTEGER,
    moeda TEXT,
    quantidade_disponivel INTEGER,
    status TEXT,
    permalink TEXT,
    atualizado_na_origem TEXT,
    ativa INTEGER NOT NULL DEFAULT 1,
    primeira_vez_em TEXT NOT NULL,
    atualizada_em TEXT NOT NULL,
    UNIQUE (fonte, id_externo)
);

CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    iniciada_em TEXT NOT NULL,
    finalizada_em TEXT,
    status TEXT NOT NULL,
    novas INTEGER NOT NULL DEFAULT 0,
    atualizadas INTEGER NOT NULL DEFAULT 0,
    iguais INTEGER NOT NULL DEFAULT 0,
    inativadas INTEGER NOT NULL DEFAULT 0,
    resumo TEXT
);

-- Log append-only: uma linha por produto A CADA execução (nunca UPDATE/DELETE
-- aqui). produtos_coletados guarda só o estado atual; esta tabela guarda a
-- evolução do preço ao longo do tempo, pra poder resumir uma variação
-- (Semana 08 — Smart Hub).
CREATE TABLE IF NOT EXISTS historico_precos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte TEXT NOT NULL,
    id_externo TEXT NOT NULL,
    preco_centavos INTEGER,
    coletado_em TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_historico_produto
    ON historico_precos (fonte, id_externo, coletado_em);
"""

_CAMPOS = ["titulo", "preco_centavos", "moeda", "quantidade_disponivel",
           "status", "permalink", "atualizado_na_origem"]


def conectar(caminho=None) -> sqlite3.Connection:
    if caminho is None:
        caminho = config.BANCO_CAMINHO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.executescript(ESQUEMA)
    return conexao


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def salvar_produtos(conexao, fonte: str, itens: list[dict]) -> dict[str, int]:
    """Insere ou atualiza cada produto; devolve quantos ficaram nova/atualizada/igual."""
    contagem = {"nova": 0, "atualizada": 0, "igual": 0}
    agora = _agora()

    for item in itens:
        atual = conexao.execute(
            f"SELECT {', '.join(_CAMPOS)} FROM produtos_coletados WHERE fonte = ? AND id_externo = ?",
            (fonte, item["id_externo"]),
        ).fetchone()

        if atual is None:
            colunas = ["fonte", "id_externo", *_CAMPOS, "ativa", "primeira_vez_em", "atualizada_em"]
            valores = [fonte, item["id_externo"], *(item.get(c) for c in _CAMPOS), 1, agora, agora]
            conexao.execute(
                f"INSERT INTO produtos_coletados ({', '.join(colunas)}) VALUES ({', '.join('?' for _ in colunas)})",
                valores,
            )
            contagem["nova"] += 1
            continue

        novos_valores = [item.get(c) for c in _CAMPOS]
        if tuple(novos_valores) == atual:
            conexao.execute(
                "UPDATE produtos_coletados SET ativa = 1 WHERE fonte = ? AND id_externo = ?",
                (fonte, item["id_externo"]),
            )
            contagem["igual"] += 1
            continue

        atribuicoes = ", ".join(f"{campo} = ?" for campo in _CAMPOS)
        conexao.execute(
            f"UPDATE produtos_coletados SET {atribuicoes}, ativa = 1, atualizada_em = ? "
            f"WHERE fonte = ? AND id_externo = ?",
            [*novos_valores, agora, fonte, item["id_externo"]],
        )
        contagem["atualizada"] += 1

    conexao.commit()
    return contagem


def registrar_historico(conexao, fonte: str, itens: list[dict]) -> None:
    """Grava uma linha por item nesta coleta — sempre, mesmo quando o preço
    não mudou ("igual"). É o preço ficar parado por várias coletas que mostra
    estabilidade; se só gravássemos mudança, perderíamos essa informação.

    Nunca dá UPDATE nem DELETE aqui: cada chamada só ACRESCENTA linhas. Quem
    decide quando chamar é o pipeline (executar.py) — aqui é só o INSERT.
    """
    if not itens:
        return
    agora = _agora()
    conexao.executemany(
        "INSERT INTO historico_precos (fonte, id_externo, preco_centavos, coletado_em) "
        "VALUES (?, ?, ?, ?)",
        [(fonte, item["id_externo"], item.get("preco_centavos"), agora) for item in itens],
    )
    conexao.commit()


def historico_do_produto(conexao, fonte: str, id_externo: str, limite: int = 10) -> list[dict]:
    """Últimas N coletas de um produto, mais recente por último (ordem
    cronológica — fica mais fácil de ler/resumir "do mais antigo pro mais
    novo" do que o inverso)."""
    linhas = conexao.execute(
        "SELECT preco_centavos, coletado_em FROM historico_precos "
        "WHERE fonte = ? AND id_externo = ? ORDER BY coletado_em DESC LIMIT ?",
        (fonte, id_externo, limite),
    ).fetchall()
    linhas.reverse()
    return [{"preco_centavos": preco, "coletado_em": quando} for preco, quando in linhas]


def inativar_sumidos(conexao, fonte: str, ids_vistos: set[str]) -> int:
    """Marca ativa=0 quem não apareceu nesta coleta. Só chamar com coleta COMPLETA."""
    cursor = conexao.execute(
        "SELECT id_externo FROM produtos_coletados WHERE fonte = ? AND ativa = 1", (fonte,)
    )
    sumidos = [linha[0] for linha in cursor.fetchall() if linha[0] not in ids_vistos]
    if sumidos:
        agora = _agora()
        conexao.executemany(
            "UPDATE produtos_coletados SET ativa = 0, atualizada_em = ? WHERE fonte = ? AND id_externo = ?",
            [(agora, fonte, id_) for id_ in sumidos],
        )
        conexao.commit()
    return len(sumidos)


def iniciar_execucao(conexao) -> int:
    cursor = conexao.execute(
        "INSERT INTO execucoes (iniciada_em, status) VALUES (?, ?)", (_agora(), "em_andamento")
    )
    conexao.commit()
    return cursor.lastrowid


def finalizar_execucao(conexao, execucao_id: int, status: str, novas: int, atualizadas: int,
                        iguais: int, inativadas: int, resumo: str) -> None:
    conexao.execute(
        "UPDATE execucoes SET finalizada_em = ?, status = ?, novas = ?, atualizadas = ?, "
        "iguais = ?, inativadas = ?, resumo = ? WHERE id = ?",
        (_agora(), status, novas, atualizadas, iguais, inativadas, resumo, execucao_id),
    )
    conexao.commit()

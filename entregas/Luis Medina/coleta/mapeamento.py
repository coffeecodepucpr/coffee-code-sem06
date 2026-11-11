from __future__ import annotations

import re

_RE_ITEM_ID_NA_QUERY = re.compile(r"item_id[:=](MLB-?\d+)", re.IGNORECASE)
_RE_ID_DE_CATALOGO = re.compile(r"/p/(MLB-?\d+)", re.IGNORECASE)
_RE_QUALQUER_ID = re.compile(r"(MLB-?\d+)", re.IGNORECASE)


def _normalizar(id_bruto: str) -> str:
    return id_bruto.upper().replace("-", "")


def extrair_id_externo(url: str) -> str | None:
    url = url or ""

    casamento = _RE_ITEM_ID_NA_QUERY.search(url)
    if casamento:
        return _normalizar(casamento.group(1))

    sem_id_de_catalogo = _RE_ID_DE_CATALOGO.sub("", url)
    casamento = _RE_QUALQUER_ID.search(sem_id_de_catalogo)
    if not casamento:
        return None
    return _normalizar(casamento.group(1))


def ler_produtos_monitorados(caminho) -> list[str]:
    """Lê o arquivo de URLs (uma por linha, '#' inicia comentário) e devolve os IDs."""
    if not caminho.exists():
        return []
    ids = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        id_externo = extrair_id_externo(linha)
        if id_externo:
            ids.append(id_externo)
    return ids


def mapear_item(bruto: dict) -> dict:
    """Pega os campos que interessam do JSON de /items (já sem o envelope {code, body})."""
    return {
        "id_externo": bruto.get("id"),
        "titulo": bruto.get("title"),
        "preco": bruto.get("price"),            # None se o item não tem preço ativo
        "moeda": bruto.get("currency_id"),
        "quantidade_disponivel": bruto.get("available_quantity"),
        "status": bruto.get("status"),            # active, paused, closed...
        "permalink": bruto.get("permalink"),
        "atualizado_na_origem": bruto.get("last_updated"),
    }

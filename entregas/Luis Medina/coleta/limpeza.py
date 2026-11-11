from __future__ import annotations

from decimal import Decimal, InvalidOperation


def limpar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None
    valor = " ".join(valor.split())
    return valor or None


def limpar_preco_centavos(preco) -> int | None:
    """129.9 -> 12990. None (sem preço ativo) continua None."""
    if preco is None:
        return None
    try:
        return int((Decimal(str(preco)) * 100).to_integral_value())
    except (InvalidOperation, ValueError):
        return None


def item_valido(item: dict, campos_essenciais: list[str]) -> bool:
    return all(item.get(campo) not in (None, "") for campo in campos_essenciais)


def limpar_produto(bruto: dict) -> dict:
    return {
        "id_externo": limpar_texto(bruto.get("id_externo")),
        "titulo": limpar_texto(bruto.get("titulo")),
        "preco_centavos": limpar_preco_centavos(bruto.get("preco")),
        "moeda": limpar_texto(bruto.get("moeda")),
        "quantidade_disponivel": bruto.get("quantidade_disponivel"),
        "status": limpar_texto(bruto.get("status")),
        "permalink": limpar_texto(bruto.get("permalink")),
        "atualizado_na_origem": limpar_texto(bruto.get("atualizado_na_origem")),
    }

"""Gerencia o access_token da API do Mercado Livre.

Duas coisas importantes sobre o token do Mercado Livre:
1. O access_token expira em poucas horas.
2. O refresh_token só pode ser usado UMA VEZ: a cada renovação, o Mercado
   Livre devolve um refresh_token NOVO e invalida o antigo.

Por isso não dá pra deixar o token fixo no .env: guardamos o token "vivo"
em dados/ml_tokens.json (fora do Git) e atualizamos esse arquivo a cada
renovação. O .env só serve pra "semear" esse arquivo da primeira vez.
"""
from __future__ import annotations

import json
import logging

import requests

from coleta import config

logger = logging.getLogger("coleta.auth")


class TokenIndisponivel(Exception):
    """Não há token válido e não foi possível renovar."""


def _ler_estado() -> dict | None:
    if not config.TOKENS_CAMINHO.exists():
        return None
    return json.loads(config.TOKENS_CAMINHO.read_text(encoding="utf-8"))


def _salvar_estado(estado: dict) -> None:
    config.TOKENS_CAMINHO.parent.mkdir(parents=True, exist_ok=True)
    config.TOKENS_CAMINHO.write_text(json.dumps(estado, indent=2), encoding="utf-8")


def _semear_do_env() -> dict:
    """Primeira execução: usa o token do .env pra começar."""
    if not config.ACCESS_TOKEN_INICIAL or not config.REFRESH_TOKEN_INICIAL:
        raise TokenIndisponivel(
            "não há dados/ml_tokens.json nem ACCESS_TOKEN/REFRESH_TOKEN no .env. "
            "Faça a autorização OAuth uma vez e preencha o .env."
        )
    estado = {"access_token": config.ACCESS_TOKEN_INICIAL, "refresh_token": config.REFRESH_TOKEN_INICIAL}
    _salvar_estado(estado)
    return estado


def access_token_atual() -> str:
    estado = _ler_estado() or _semear_do_env()
    return estado["access_token"]


def renovar() -> str:
    estado = _ler_estado() or _semear_do_env()

    if not config.CLIENT_ID or not config.CLIENT_SECRET:
        raise TokenIndisponivel("CLIENT_ID/CLIENT_SECRET não estão no .env — não dá pra renovar o token.")

    resposta = requests.post(
        f"{config.API_BASE}/oauth/token",
        headers={"accept": "application/json", "content-type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "refresh_token": estado["refresh_token"],
        },
        timeout=config.TIMEOUT_SEGUNDOS,
    )
    if resposta.status_code != 200:
        logger.error("falha ao renovar o token (status %d)", resposta.status_code)
        raise TokenIndisponivel(f"Mercado Livre recusou a renovação (status {resposta.status_code})")

    corpo = resposta.json()
    novo_estado = {"access_token": corpo["access_token"], "refresh_token": corpo["refresh_token"]}
    _salvar_estado(novo_estado)
    logger.info("token renovado com sucesso")
    return novo_estado["access_token"]

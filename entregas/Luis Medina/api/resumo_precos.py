"""Resumo do histórico de preço de um produto usando IA local (Ollama) com
cache (Redis/Memurai) — adaptação da Semana 08 (Smart Hub) pro Estom.

A vaga do notebook do curso virou "histórico de preço": o modelo recebe os
últimos preços coletados (coleta/banco.py::historico_do_produto) e escreve
um resumo curto em português, tipo "caiu de R$349,90 pra R$239,90".

Duas peças ficam injetáveis nas funções (cliente_redis, chamar_modelo) em
vez de fixas, só pra dar pra testar sem precisar de um Ollama/Redis de
verdade rodando — ver tests/api/test_resumo_precos.py.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from threading import Lock

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODELO_OLLAMA = os.environ.get("OLLAMA_MODELO", "qwen2.5:0.5b")
TIMEOUT_OLLAMA_SEGUNDOS = 30

# TTL mais longo que o do notebook (5 min): a coleta aqui roda no máximo uma
# vez por dia (ver agendamento/), então o histórico de um produto não muda
# várias vezes por hora como uma vaga recém-publicada poderia. Reaproveitar
# o resumo por mais tempo evita gerar a mesma coisa de novo sem necessidade.
TTL_CACHE_SEGUNDOS = 3600  # 1 hora
VERSAO_PROMPT = "v2"
CONFIG_GERACAO = {"temperature": 0.2}

# Serializa as chamadas ao modelo neste processo — mesma ideia do notebook
# (trava_geracao): evita duas requisições gerarem ao mesmo tempo e brigarem
# pelo mesmo modelo carregado. Não coordena múltiplos processos/workers.
_TRAVA_GERACAO = Lock()


class OllamaIndisponivel(Exception):
    """O Ollama não respondeu, ou respondeu algo que não dá pra usar."""


class CacheIndisponivel(Exception):
    """O Redis/Memurai não respondeu."""


def montar_texto_historico(historico: list[dict]) -> str:
    """Do formato de coleta/banco.py::historico_do_produto pra texto legível,
    uma linha por coleta, do mais antigo pro mais novo."""
    linhas = []
    for ponto in historico:
        preco = ponto["preco_centavos"]
        preco_texto = f"R$ {preco / 100:.2f}".replace(".", ",") if preco is not None else "sem preço ativo"
        data = _formatar_data(ponto["coletado_em"])
        linhas.append(f"{data}: {preco_texto}")
    return "\n".join(linhas)


def _formatar_data(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y")
    except ValueError:
        return iso


def montar_mensagens(nome_produto: str, texto_historico: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "Você resume o histórico de preço de um produto de e-commerce, "
                "em português brasileiro. Use somente os valores informados, "
                "nunca invente um preço nem uma porcentagem. "
                "Se o histórico tiver dois ou mais preços, diga se o preço subiu, "
                "caiu ou ficou estável, citando os valores. "
                "Se o histórico tiver só UM preço, não existe variação para "
                "descrever: diga apenas qual é o preço atual, sem dizer que "
                "subiu, caiu ou mudou. Responda em até duas frases curtas."
            ),
        },
        {
            "role": "user",
            "content": (
                f'Resuma a variação de preço do produto "{nome_produto}" '
                f"a partir do histórico abaixo (um preço por coleta):\n\n{texto_historico}"
            ),
        },
    ]


def chave_resumo(nome_produto: str, texto_historico: str) -> str:
    """SHA-256 da identidade do pedido — texto, prompt, modelo e config.
    Mudar qualquer um desses muda a chave (igual ao notebook: não é só o
    texto que decide se um resumo serve, é o pedido inteiro)."""
    identidade = {
        "modelo": MODELO_OLLAMA,
        "versao_prompt": VERSAO_PROMPT,
        "mensagens": montar_mensagens(nome_produto, texto_historico),
        "geracao": CONFIG_GERACAO,
    }
    conteudo = json.dumps(identidade, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
    return "estom:resumo-preco:" + digest


def _chamar_ollama(mensagens: list[dict]) -> str:
    """Implementação de verdade: POST /api/chat no Ollama local."""
    try:
        resposta = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODELO_OLLAMA,
                "messages": mensagens,
                "stream": False,
                "options": CONFIG_GERACAO,
            },
            timeout=TIMEOUT_OLLAMA_SEGUNDOS,
        )
    except requests.exceptions.RequestException as exc:
        raise OllamaIndisponivel(f"não consegui falar com o Ollama em {OLLAMA_URL}: {exc}") from exc

    if resposta.status_code != 200:
        raise OllamaIndisponivel(f"Ollama respondeu {resposta.status_code}: {resposta.text[:300]}")

    corpo = resposta.json()
    texto = corpo.get("message", {}).get("content", "")
    return texto.strip()


def gerar_resumo(
    cliente_redis,
    nome_produto: str,
    historico: list[dict],
    chamar_modelo=None,
) -> dict:
    """Devolve {"resumo": str, "cache": bool}. Levanta OllamaIndisponivel ou
    CacheIndisponivel se alguma das duas peças falhar — quem chama decide o
    HTTP (ver api/main.py), igual o notebook faz com o 502/503."""
    chamar_modelo = chamar_modelo or _chamar_ollama
    texto_historico = montar_texto_historico(historico)
    chave = chave_resumo(nome_produto, texto_historico)

    try:
        with _TRAVA_GERACAO:
            salvo = cliente_redis.get(chave)
            if salvo is not None:
                return {"resumo": salvo, "cache": True}

            resumo = chamar_modelo(montar_mensagens(nome_produto, texto_historico))
            if not resumo:
                raise OllamaIndisponivel("o modelo não gerou um resumo")

            cliente_redis.set(chave, resumo, ex=TTL_CACHE_SEGUNDOS)
            return {"resumo": resumo, "cache": False}
    except OllamaIndisponivel:
        raise
    except Exception as exc:  # erros do cliente redis (ConnectionError etc.)
        raise CacheIndisponivel(f"Redis/Memurai indisponível: {exc}") from exc

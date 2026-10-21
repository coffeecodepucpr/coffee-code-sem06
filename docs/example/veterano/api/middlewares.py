"""Middlewares de requisição, escritos como ASGI puro.

Um middleware ASGI é uma classe que recebe a aplicação (`app`) e é chamada a cada
conexão com `scope`, `receive` e `send`. Ele pode olhar o pedido antes de passá-lo
adiante, e olhar a resposta (interceptando o `send`) antes de ela sair.
"""
import logging
import re
import time
import uuid

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("api")
if not logger.handlers:
    _manipulador = logging.StreamHandler()
    _manipulador.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_manipulador)
    logger.setLevel(logging.INFO)

# Só aceitamos um identificador vindo do cliente se ele tiver um formato seguro.
FORMATO_DO_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class IdentificadorDoPedido:
    """Dá um identificador a cada pedido, mede o tempo, registra um log e devolve cabeçalhos."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        recebido = dict(scope["headers"]).get(b"x-request-id", b"")
        recebido = recebido.decode("latin-1")
        valido = FORMATO_DO_ID.match(recebido)
        identificador = recebido if valido else uuid.uuid4().hex[:12]
        scope.setdefault("state", {})["request_id"] = identificador
        inicio = time.perf_counter()
        codigo = 0

        async def enviar(mensagem: Message):
            nonlocal codigo
            if mensagem["type"] == "http.response.start":
                codigo = mensagem["status"]
                duracao = (time.perf_counter() - inicio) * 1000
                cabecalhos = list(mensagem.get("headers", []))
                cabecalhos.append((b"x-request-id", identificador.encode()))
                tempo = f"{duracao:.1f}ms".encode()
                cabecalhos.append((b"x-process-time", tempo))
                mensagem = {**mensagem, "headers": cabecalhos}
            await send(mensagem)

        try:
            await self.app(scope, receive, enviar)
        finally:
            duracao = (time.perf_counter() - inicio) * 1000
            logger.info(
                "request_id=%s metodo=%s caminho=%s status=%s ms=%.1f",
                identificador, scope["method"], scope["path"], codigo, duracao,
            )


class PegaTudo:
    """Garante que um erro inesperado vire um 500 em JSON, ainda DENTRO do CORS.

    O ServerErrorMiddleware, que o Starlette sempre coloca por fora de tudo, responde
    sem cabeçalhos CORS. Capturar o erro aqui, antes de ele chegar lá, mantém os
    cabeçalhos e deixa o navegador mostrar o 500 de verdade.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        iniciada = False

        async def enviar(mensagem: Message):
            nonlocal iniciada
            if mensagem["type"] == "http.response.start":
                iniciada = True
            await send(mensagem)

        try:
            await self.app(scope, receive, enviar)
        except Exception:
            identificador = scope.get("state", {}).get("request_id")
            logger.exception(
                "request_id=%s erro inesperado em %s %s",
                identificador, scope["method"], scope["path"],
            )
            if iniciada:
                raise  # a resposta já começou a sair: não dá para trocá-la
            corpo = {
                "erro": {
                    "codigo": "erro_interno",
                    "mensagem": "Erro interno do servidor",
                    "detalhes": None,
                },
                "meta": {"requestId": identificador},
            }
            await JSONResponse(corpo, status_code=500)(scope, receive, send)

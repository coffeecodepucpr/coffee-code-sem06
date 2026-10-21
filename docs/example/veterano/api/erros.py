"""Tratadores de erro: todo erro sai no mesmo envelope { erro, meta }."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

CODIGO_POR_STATUS = {
    404: "nao_encontrado",
    405: "metodo_nao_permitido",
    409: "conflito",
    422: "regra_de_negocio",
}


# As mensagens padrão do framework chegam em inglês: traduzimos só as que ele mesmo gera.
MENSAGEM_PADRAO = {
    "Not Found": "Recurso não encontrado",
    "Method Not Allowed": "Método não permitido para este recurso",
}


def _meta(request: Request) -> dict:
    return {"requestId": getattr(request.state, "request_id", None)}


def resposta_de_erro(
    request: Request, status_code: int, codigo: str, mensagem: str,
    detalhes=None, headers=None,
) -> JSONResponse:
    erro = {"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes}
    corpo = {"erro": erro, "meta": _meta(request)}
    return JSONResponse(corpo, status_code=status_code, headers=headers)


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def tratar_erro_http(request: Request, erro: StarletteHTTPException):
        codigo = CODIGO_POR_STATUS.get(erro.status_code, "erro_http")
        mensagem = MENSAGEM_PADRAO.get(str(erro.detail), str(erro.detail))
        return resposta_de_erro(
            request, erro.status_code, codigo, mensagem,
            headers=getattr(erro, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(request: Request, erro: RequestValidationError):
        detalhes = [
            {"campo": ".".join(str(p) for p in e["loc"]), "mensagem": e["msg"]}
            for e in erro.errors()
        ]
        return resposta_de_erro(
            request, 422, "validacao",
            "Os dados enviados são inválidos", detalhes,
        )

"""API Central, versão veterano: middlewares de requisição e JSON padronizado.

Rodar:  fastapi dev main.py
"""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

import dados
from erros import registrar_tratadores
from middlewares import IdentificadorDoPedido, PegaTudo
from schemas import GrupoCreate, GrupoOut, GrupoPatch, MateriaOut, RespostaDeErro, RespostaItem, RespostaLista

app = FastAPI(
    title="API Central: Buscador de Grupos de Estudo (veterano)",
    description="Toda resposta vem em `{ dados, meta }`, e todo erro em `{ erro, meta }`. O JSON usa camelCase.",
    version="2.0.0",
    responses={
        422: {"model": RespostaDeErro, "description": "Dados inválidos"},
        500: {"model": RespostaDeErro, "description": "Erro interno"},
    },
)

# A ORDEM IMPORTA: o último middleware adicionado é o mais EXTERNO.
#   CORS  >  IdentificadorDoPedido  >  PegaTudo  >  rotas
app.add_middleware(PegaTudo)
app.add_middleware(IdentificadorDoPedido)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)
registrar_tratadores(app)


def meta_do(request: Request, **extras) -> dict:
    return {"requestId": request.state.request_id, **extras}


def buscar_grupo_ou_404(grupo_id: int) -> dict:
    grupo = dados.GRUPOS.get(grupo_id)
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


def conferir_materia(materia_id: int) -> None:
    if materia_id not in dados.MATERIAS:
        raise HTTPException(status_code=422, detail=f"A matéria {materia_id} não existe")


def conferir_nome_livre(nome_grupo: str, materia_id: int, ignorar_id: int | None = None) -> None:
    for g in dados.GRUPOS.values():
        if g["nome_grupo"].lower() == nome_grupo.lower() and g["materia_id"] == materia_id and g["grupo_id"] != ignorar_id:
            raise HTTPException(status_code=409, detail="Já existe um grupo com esse nome nessa matéria")


@app.get("/materias", response_model=RespostaItem[list[MateriaOut]], tags=["materias"], summary="Lista as matérias")
def listar_materias(request: Request):
    return {"dados": list(dados.MATERIAS.values()), "meta": meta_do(request)}


@app.get("/grupos", response_model=RespostaLista[GrupoOut], tags=["grupos"], summary="Lista os grupos, com busca e paginação")
def listar_grupos(
    request: Request,
    q: str | None = None,
    materia_id: Annotated[int | None, Query(alias="materiaId")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    grupos = sorted(dados.GRUPOS.values(), key=lambda g: g["nome_grupo"].lower())
    if q is not None:
        grupos = [g for g in grupos if q.lower() in g["nome_grupo"].lower()]
    if materia_id is not None:
        grupos = [g for g in grupos if g["materia_id"] == materia_id]
    return {
        "dados": grupos[offset : offset + limit],
        "meta": meta_do(request, total=len(grupos), limit=limit, offset=offset),
    }


@app.get("/grupos/{grupo_id}", response_model=RespostaItem[GrupoOut], tags=["grupos"], summary="Busca um grupo")
def buscar_grupo(grupo_id: int, request: Request):
    return {"dados": buscar_grupo_ou_404(grupo_id), "meta": meta_do(request)}


@app.post("/grupos", response_model=RespostaItem[GrupoOut], status_code=status.HTTP_201_CREATED, tags=["grupos"], summary="Cria um grupo")
def criar_grupo(novo: GrupoCreate, request: Request, response: Response):
    conferir_materia(novo.materia_id)
    conferir_nome_livre(novo.nome_grupo, novo.materia_id)
    grupo_id = next(dados.CONTADOR_GRUPOS)
    grupo = {**novo.model_dump(), "grupo_id": grupo_id, "criado_em": datetime.now(timezone.utc)}
    dados.GRUPOS[grupo_id] = grupo
    response.headers["Location"] = f"/grupos/{grupo_id}"
    return {"dados": grupo, "meta": meta_do(request)}


@app.patch("/grupos/{grupo_id}", response_model=RespostaItem[GrupoOut], tags=["grupos"], summary="Altera só alguns campos de um grupo")
def alterar_grupo(grupo_id: int, mudancas: GrupoPatch, request: Request):
    grupo = buscar_grupo_ou_404(grupo_id)
    campos = mudancas.model_dump(exclude_unset=True)
    if "materia_id" in campos:
        conferir_materia(campos["materia_id"])
    conferir_nome_livre(campos.get("nome_grupo", grupo["nome_grupo"]), campos.get("materia_id", grupo["materia_id"]), ignorar_id=grupo_id)
    grupo.update(campos)
    return {"dados": grupo, "meta": meta_do(request)}


@app.delete("/grupos/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["grupos"], summary="Apaga um grupo")
def apagar_grupo(grupo_id: int):
    buscar_grupo_ou_404(grupo_id)
    del dados.GRUPOS[grupo_id]


@app.get("/diagnostico/erro", include_in_schema=False)
def provocar_erro():
    """Só para estudo: provoca um erro inesperado. Em um sistema real, remova esta rota."""
    raise RuntimeError("falha provocada de propósito")

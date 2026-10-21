"""API Central do Buscador de Grupos de Estudo, com CORS configurado (resultado do Módulo 09).

Rodar:  fastapi dev main.py
Docs:   http://127.0.0.1:8000/docs
"""
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

import dados
from schemas import GrupoCreate, GrupoOut, GrupoPatch, MateriaOut

app = FastAPI(
    title="API Central: Buscador de Grupos de Estudo",
    description="Grupos de estudo e matérias. Os dados ficam **em memória** e voltam ao início a cada reinício.",
    version="1.0.0",
)


# CORS: quais páginas (origens) podem LER as respostas desta API pelo navegador.
# Cada origem é esquema + host + porta, escrita exatamente como o navegador a envia.
ORIGENS_PERMITIDAS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Total-Count"],
)


def buscar_grupo_ou_404(grupo_id: int) -> dict:
    grupo = dados.GRUPOS.get(grupo_id)
    if grupo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return grupo


def conferir_materia(materia_id: int) -> None:
    if materia_id not in dados.MATERIAS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"A matéria {materia_id} não existe")


def conferir_nome_livre(nome_grupo: str, materia_id: int, ignorar_id: int | None = None) -> None:
    for g in dados.GRUPOS.values():
        if g["nome_grupo"].lower() == nome_grupo.lower() and g["materia_id"] == materia_id and g["grupo_id"] != ignorar_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um grupo com esse nome nessa matéria")


@app.get("/", include_in_schema=False)
def raiz():
    return {"api": "Buscador de Grupos de Estudo", "documentacao": "/docs"}


@app.get("/materias", response_model=list[MateriaOut], tags=["materias"], summary="Lista as matérias")
def listar_materias():
    return list(dados.MATERIAS.values())


@app.get("/grupos", response_model=list[GrupoOut], tags=["grupos"], summary="Lista os grupos, com busca e paginação")
def listar_grupos(
    response: Response,
    q: str | None = None,
    materia_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    grupos = sorted(dados.GRUPOS.values(), key=lambda g: g["nome_grupo"].lower())
    if q is not None:
        grupos = [g for g in grupos if q.lower() in g["nome_grupo"].lower()]
    if materia_id is not None:
        grupos = [g for g in grupos if g["materia_id"] == materia_id]
    response.headers["X-Total-Count"] = str(len(grupos))
    return grupos[offset : offset + limit]


@app.get("/grupos/{grupo_id}", response_model=GrupoOut, tags=["grupos"], summary="Busca um grupo")
def buscar_grupo(grupo_id: int):
    return buscar_grupo_ou_404(grupo_id)


@app.post("/grupos", response_model=GrupoOut, status_code=status.HTTP_201_CREATED, tags=["grupos"], summary="Cria um grupo")
def criar_grupo(novo: GrupoCreate, response: Response):
    conferir_materia(novo.materia_id)
    conferir_nome_livre(novo.nome_grupo, novo.materia_id)
    grupo_id = next(dados.CONTADOR_GRUPOS)
    grupo = {**novo.model_dump(), "grupo_id": grupo_id, "criado_em": datetime.now(timezone.utc)}
    dados.GRUPOS[grupo_id] = grupo
    response.headers["Location"] = f"/grupos/{grupo_id}"
    return grupo


@app.patch("/grupos/{grupo_id}", response_model=GrupoOut, tags=["grupos"], summary="Altera só alguns campos de um grupo")
def alterar_grupo(grupo_id: int, mudancas: GrupoPatch):
    grupo = buscar_grupo_ou_404(grupo_id)
    campos = mudancas.model_dump(exclude_unset=True)
    if "materia_id" in campos:
        conferir_materia(campos["materia_id"])
    conferir_nome_livre(campos.get("nome_grupo", grupo["nome_grupo"]), campos.get("materia_id", grupo["materia_id"]), ignorar_id=grupo_id)
    grupo.update(campos)
    return grupo


@app.delete("/grupos/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["grupos"], summary="Apaga um grupo")
def apagar_grupo(grupo_id: int):
    buscar_grupo_ou_404(grupo_id)
    del dados.GRUPOS[grupo_id]

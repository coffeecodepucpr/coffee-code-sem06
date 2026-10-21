"""Modelos da API padronizada: JSON em camelCase e respostas dentro de um envelope."""
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class Base(BaseModel):
    # alias_generator: no JSON, nomeGrupo; no Python, nome_grupo.
    # populate_by_name: o Python ainda pode usar o nome com sublinhado.
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class MateriaOut(Base):
    materia_id: int
    nome: str
    codigo: str


class GrupoBase(Base):
    nome_grupo: str = Field(min_length=3, max_length=60)
    materia_id: int = Field(gt=0)
    max_participantes: int = Field(default=10, ge=2, le=50)
    descricao: str | None = Field(default=None, max_length=200)


class GrupoCreate(GrupoBase):
    """Corpo do POST."""


class GrupoPatch(Base):
    """Corpo do PATCH: omitir um campo é não alterá-lo. Só a descrição aceita null."""

    nome_grupo: str | None = Field(default=None, min_length=3, max_length=60)
    materia_id: int | None = Field(default=None, gt=0)
    max_participantes: int | None = Field(default=None, ge=2, le=50)
    descricao: str | None = Field(default=None, max_length=200)

    @field_validator("nome_grupo", "materia_id", "max_participantes")
    @classmethod
    def nao_aceita_null(cls, valor):
        if valor is None:
            raise ValueError("este campo não aceita null: omita-o para não alterá-lo")
        return valor


class GrupoOut(GrupoBase):
    grupo_id: int
    criado_em: datetime


class MetaDoPedido(Base):
    request_id: str


class MetaDeLista(Base):
    request_id: str
    total: int
    limit: int
    offset: int


class RespostaItem(Base, Generic[T]):
    """Envelope de um item: { dados, meta }."""

    dados: T
    meta: MetaDoPedido


class RespostaLista(Base, Generic[T]):
    """Envelope de uma lista: { dados, meta } com o total e a paginação."""

    dados: list[T]
    meta: MetaDeLista


class DetalheDoErro(Base):
    campo: str
    mensagem: str


class CorpoDoErro(Base):
    codigo: str
    mensagem: str
    detalhes: list[DetalheDoErro] | None = None


class RespostaDeErro(Base):
    """Envelope de erro: { erro, meta }."""

    erro: CorpoDoErro
    meta: MetaDoPedido

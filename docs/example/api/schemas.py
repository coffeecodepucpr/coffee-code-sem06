"""Os modelos que descrevem o formato dos dados da API."""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class MateriaOut(BaseModel):
    materia_id: int
    nome: str
    codigo: str


class GrupoBase(BaseModel):
    nome_grupo: str = Field(min_length=3, max_length=60)
    materia_id: int = Field(gt=0)
    max_participantes: int = Field(default=10, ge=2, le=50)
    descricao: str | None = Field(default=None, max_length=200)


class GrupoCreate(GrupoBase):
    """Corpo do POST."""


class GrupoPatch(BaseModel):
    """Corpo do PATCH: omitir um campo significa não alterá-lo. Só a descrição aceita null."""

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

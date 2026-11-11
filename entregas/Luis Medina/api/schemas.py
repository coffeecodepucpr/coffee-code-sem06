from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator

HOSTS_PERMITIDOS = ("mercadolivre.com.br",)


def validar_link_mercado_livre(url: HttpUrl) -> HttpUrl:
    # Confere o domínio de verdade, e não só se o texto aparece em algum lugar do link
    host = (url.host or "").lower()
    if not any(host == h or host.endswith("." + h) for h in HOSTS_PERMITIDOS):
        raise ValueError("informe um link do Mercado Livre (mercadolivre.com.br)")
    return url


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=60)
    url: HttpUrl
    categoriaId: int
    precoMaximo: float | None = Field(default=None, gt=0)

    @field_validator("url")
    @classmethod
    def validar_url(cls, valor):
        return validar_link_mercado_livre(valor)


class ProdutoUpdate(BaseModel):
    # Omitir um campo = não alterar. Só o precoMaximo aceita null (remove a meta).
    nome: str | None = Field(default=None, min_length=3, max_length=60)
    url: HttpUrl | None = None
    categoriaId: int | None = None
    precoMaximo: float | None = Field(default=None, gt=0)

    @field_validator("nome", "url", "categoriaId")
    @classmethod
    def nao_aceitar_nulo(cls, valor):
        if valor is None:
            raise ValueError("este campo não aceita null: omita-o para não alterá-lo")
        return valor

    @field_validator("url")
    @classmethod
    def validar_url(cls, valor):
        return validar_link_mercado_livre(valor)


class Produto(BaseModel):
    """Formato que a API devolve.
    precoAtual e ultimaVerificacao não são enviados pelo cliente: serão preenchidos
    pelo monitoramento (por enquanto, só existem nos dados de demonstração)."""
    id: int
    nome: str
    url: str
    loja: str
    imagem: str | None
    categoriaId: int
    precoMaximo: float | None
    precoAtual: float | None
    ultimaVerificacao: datetime | None
    criadoEm: datetime


class Categoria(BaseModel):
    id: int
    nome: str


class ResumoPreco(BaseModel):
    """Resposta do GET /produtos/{id}/resumo-preco (Semana 08 — Smart Hub)."""
    resumo: str
    cache: bool

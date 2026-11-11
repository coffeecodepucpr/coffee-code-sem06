import os
import sqlite3
from datetime import datetime, timezone

import redis
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from api import coleta_integracao, dados, resumo_precos
from api.schemas import Categoria, Produto, ProdutoCreate, ProdutoUpdate, ResumoPreco
from coleta import banco, config, mapeamento

app = FastAPI(
    title="Estom API",
    description="API para gerenciamento de produtos e acompanhamento de preços.",
    version="1.1.0",
)

# ---------- CORS ----------
# As duas formas de abrir a página (para o navegador, são duas origens diferentes)
ORIGENS_PERMITIDAS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],  # só o que a página usa
    allow_headers=["Content-Type"],                    # para enviar JSON
    expose_headers=["X-Total-Count"],                  # para o JS ler o total
)


# ---------- Cliente Redis (Smart Hub — resumo de preço) ----------
# Mesma ideia do notebook: um cliente só, reaproveitado entre chamadas. Fica de
# fora de gerar_resumo() pra essa função não precisar saber ONDE o Redis está
# (ela só recebe um cliente pronto) — ver api/resumo_precos.py.
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

_cliente_redis: redis.Redis | None = None


def obter_cliente_redis() -> redis.Redis:
    global _cliente_redis
    if _cliente_redis is None:
        _cliente_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return _cliente_redis


# ---------- Funções auxiliares ----------

def buscar_produto_ou_404(produto_id: int) -> dict:
    for produto in dados.produtos:
        if produto["id"] == produto_id:
            return produto
    raise HTTPException(status_code=404, detail="Produto não encontrado")


def garantir_categoria_existe(categoria_id: int) -> None:
    if not any(c["id"] == categoria_id for c in dados.categorias):
        # Mesmo formato da validação automática, para a página achar o campo pelo "loc"
        raise HTTPException(
            status_code=422,
            detail=[{
                "type": "categoria_inexistente",
                "loc": ["body", "categoriaId"],
                "msg": f"A categoria {categoria_id} não existe",
                "input": categoria_id,
            }],
        )


def garantir_url_unica(url: str, ignorar_id: int | None = None) -> None:
    for produto in dados.produtos:
        if produto["url"] == url and produto["id"] != ignorar_id:
            raise HTTPException(status_code=409, detail="Este produto já está cadastrado")


# ---------- Produtos ----------

@app.get("/produtos", response_model=list[Produto], summary="Listar produtos",
         responses={422: {"description": "Parâmetro inválido"}})
def listar_produtos(
    response: Response,
    q: str | None = Query(default=None, description="Busca por parte do nome"),
    categoria_id: int | None = Query(default=None, alias="categoriaId",
                                     description="Só os produtos dessa categoria"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    resultado = coleta_integracao.aplicar_precos_coletados(dados.produtos)

    if q:
        termo = q.strip().lower()
        resultado = [p for p in resultado if termo in p["nome"].lower()]

    if categoria_id is not None:
        resultado = [p for p in resultado if p["categoriaId"] == categoria_id]

    resultado = sorted(resultado, key=lambda p: p["nome"].lower())

    # Total ANTES de cortar a página (a página usa para calcular "Página N de M")
    response.headers["X-Total-Count"] = str(len(resultado))

    return resultado[offset: offset + limit]


@app.get("/produtos/{produto_id}", response_model=Produto, summary="Buscar produto por ID",
         responses={404: {"description": "Produto não encontrado"},
                    422: {"description": "ID inválido"}})
def buscar_produto(produto_id: int):
    produto = buscar_produto_ou_404(produto_id)
    return coleta_integracao.aplicar_precos_coletados([produto])[0]


@app.get("/produtos/{produto_id}/resumo-preco", response_model=ResumoPreco,
         summary="Resumir em português a variação de preço do produto",
         responses={404: {"description": "Produto não encontrado, não identificado no "
                                          "Mercado Livre, ou sem histórico de preço coletado"},
                    502: {"description": "O modelo de IA (Ollama) não respondeu"},
                    503: {"description": "O cache (Redis/Memurai) não respondeu"}})
def resumo_preco_produto(produto_id: int, cliente_redis: redis.Redis = Depends(obter_cliente_redis)):
    produto = buscar_produto_ou_404(produto_id)

    id_externo = mapeamento.extrair_id_externo(produto["url"])
    if id_externo is None:
        raise HTTPException(
            status_code=404,
            detail="Não foi possível identificar este produto no Mercado Livre",
        )

    if not config.BANCO_CAMINHO.exists():
        raise HTTPException(status_code=404, detail="Ainda não há histórico de preço coletado")

    conexao = sqlite3.connect(config.BANCO_CAMINHO)
    try:
        historico = banco.historico_do_produto(conexao, config.FONTE, id_externo)
    finally:
        conexao.close()

    if not historico:
        raise HTTPException(status_code=404, detail="Ainda não há histórico de preço coletado")

    try:
        return resumo_precos.gerar_resumo(cliente_redis, produto["nome"], historico)
    except resumo_precos.OllamaIndisponivel as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except resumo_precos.CacheIndisponivel as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/produtos", response_model=Produto, status_code=status.HTTP_201_CREATED,
          summary="Cadastrar produto",
          responses={409: {"description": "Produto já cadastrado"},
                     422: {"description": "Dados inválidos"}})
def criar_produto(produto: ProdutoCreate, response: Response):
    url = str(produto.url)
    garantir_categoria_existe(produto.categoriaId)
    garantir_url_unica(url)

    novo_produto = {
        "id": dados.proximo_id,
        "nome": produto.nome,
        "url": url,
        "loja": "Mercado Livre",
        "imagem": None,
        "categoriaId": produto.categoriaId,
        "precoMaximo": produto.precoMaximo,
        "precoAtual": None,          # ainda não verificado
        "ultimaVerificacao": None,
        "criadoEm": datetime.now(timezone.utc).isoformat(),
    }

    dados.produtos.append(novo_produto)
    dados.proximo_id += 1

    response.headers["Location"] = f"/produtos/{novo_produto['id']}"
    return novo_produto


@app.patch("/produtos/{produto_id}", response_model=Produto,
           summary="Atualizar parcialmente produto",
           responses={404: {"description": "Produto não encontrado"},
                      409: {"description": "URL já cadastrada em outro produto"},
                      422: {"description": "Dados inválidos"}})
def atualizar_produto_parcial(produto_id: int, dados_recebidos: ProdutoUpdate):
    produto = buscar_produto_ou_404(produto_id)

    # Só os campos que o cliente realmente enviou
    alteracoes = dados_recebidos.model_dump(exclude_unset=True)

    if "url" in alteracoes:
        alteracoes["url"] = str(alteracoes["url"])
        garantir_url_unica(alteracoes["url"], ignorar_id=produto_id)

    if "categoriaId" in alteracoes:
        garantir_categoria_existe(alteracoes["categoriaId"])

    produto.update(alteracoes)
    return produto


@app.put("/produtos/{produto_id}", response_model=Produto, summary="Substituir produto",
         responses={404: {"description": "Produto não encontrado"},
                    409: {"description": "URL já cadastrada em outro produto"},
                    422: {"description": "Dados inválidos"}})
def substituir_produto(produto_id: int, dados_recebidos: ProdutoCreate):
    produto = buscar_produto_ou_404(produto_id)

    alteracoes = dados_recebidos.model_dump()
    alteracoes["url"] = str(alteracoes["url"])
    garantir_url_unica(alteracoes["url"], ignorar_id=produto_id)
    garantir_categoria_existe(alteracoes["categoriaId"])

    produto.update(alteracoes)
    return produto


@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT,
            summary="Excluir produto",
            responses={404: {"description": "Produto não encontrado"},
                       422: {"description": "ID inválido"}})
def deletar_produto(produto_id: int):
    produto = buscar_produto_ou_404(produto_id)
    dados.produtos.remove(produto)


# ---------- Categorias ----------

@app.get("/categorias", response_model=list[Categoria], summary="Listar categorias")
def listar_categorias():
    return dados.categorias


@app.get("/categorias/{categoria_id}", response_model=Categoria,
         summary="Buscar categoria por ID",
         responses={404: {"description": "Categoria não encontrada"},
                    422: {"description": "ID inválido"}})
def buscar_categoria(categoria_id: int):
    for categoria in dados.categorias:
        if categoria["id"] == categoria_id:
            return categoria
    raise HTTPException(status_code=404, detail="Categoria não encontrada")

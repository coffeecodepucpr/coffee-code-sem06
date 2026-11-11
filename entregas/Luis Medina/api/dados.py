# Dados de DEMONSTRAÇÃO, em memória: voltam ao estado inicial quando a API reinicia.
#
# Os produtos 1, 2 e 5 têm URL de prova de conceito (ver coleta/README.md):
# apontam pros ids MLB001/MLB002/MLB003 da API simulada de coleta
# (coleta/api_simulada.py). Quando a coleta roda contra essa API simulada,
# o preço/data desses 3 produtos abaixo é SOBRESCRITO pelo dado coletado de
# verdade (ver api/coleta_integracao.py) — o nome do produto aqui não precisa
# bater com o nome na API simulada, é só pra mostrar o link funcionando.
# Os produtos 3 e 4 continuam sendo só dado de demonstração, sem coleta.

categorias = [
    {"id": 1, "nome": "Periféricos"},
    {"id": 2, "nome": "Informática"},
    {"id": 3, "nome": "Acessórios"},
    {"id": 4, "nome": "Games"},
    {"id": 5, "nome": "Casa e escritório"},
]

_DEMO_VERIFICACAO = "2026-09-29T16:00:00Z"
_DEMO_CRIACAO = "2026-09-20T12:00:00Z"

produtos = [
    {
        "id": 1,
        "nome": "Monitor",
        "url": "https://produto.mercadolivre.com.br/MLB-002-mouse-sem-fio",
        "loja": "Mercado Livre",
        "imagem": "assets/images/Foto monitor.webp",
        "categoriaId": 2,
        "precoMaximo": 800.00,
        "precoAtual": 829.90,
        "ultimaVerificacao": _DEMO_VERIFICACAO,
        "criadoEm": _DEMO_CRIACAO,
    },
    {
        "id": 2,
        "nome": "Cadeira do escritório",
        "url": "https://produto.mercadolivre.com.br/MLB-003-produto-de-teste",
        "loja": "Mercado Livre",
        "imagem": "assets/images/Cadeira ergonomica.webp",
        "categoriaId": 5,
        "precoMaximo": 364.90,
        "precoAtual": 494.80,
        "ultimaVerificacao": _DEMO_VERIFICACAO,
        "criadoEm": _DEMO_CRIACAO,
    },
    {
        "id": 3,
        "nome": "Apple AirPods 4",
        "url": "https://www.mercadolivre.com.br/demo-airpods",
        "loja": "Mercado Livre",
        "imagem": "assets/images/airpods4.webp",
        "categoriaId": 3,
        "precoMaximo": 1250.00,
        "precoAtual": 1190.90,
        "ultimaVerificacao": _DEMO_VERIFICACAO,
        "criadoEm": _DEMO_CRIACAO,
    },
    {
        "id": 4,
        "nome": "PlayStation 5 Slim",
        "url": "https://www.mercadolivre.com.br/demo-ps5",
        "loja": "Mercado Livre",
        "imagem": "assets/images/ps5.webp",
        "categoriaId": 4,
        "precoMaximo": None,
        "precoAtual": 3299.00,
        "ultimaVerificacao": _DEMO_VERIFICACAO,
        "criadoEm": _DEMO_CRIACAO,
    },
    {
        "id": 5,
        "nome": "Teclado mecânico",
        "url": "https://produto.mercadolivre.com.br/MLB-001-teclado-mecanico",
        "loja": "Mercado Livre",
        "imagem": None,
        "categoriaId": 1,
        "precoMaximo": 250.00,
        "precoAtual": None,
        "ultimaVerificacao": None,
        "criadoEm": _DEMO_CRIACAO,
    },
]

proximo_id = 6

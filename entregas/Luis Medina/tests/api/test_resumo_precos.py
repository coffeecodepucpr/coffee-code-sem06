"""Testes de api/resumo_precos.py e do endpoint GET /produtos/{id}/resumo-preco.

Nenhum dos dois roda Ollama/Memurai de verdade: cliente_redis é um
fakeredis.FakeRedis() (biblioteca Python pura, sem servidor), e a chamada ao
modelo é sempre uma função fake passada em `chamar_modelo=` (resumo_precos.py)
ou monkeypatchada em resumo_precos._chamar_ollama (endpoint) — mesma ideia do
`cliente_redis`/`chamar_modelo` injetáveis descritos no topo do módulo.
"""
import fakeredis
import pytest
from fastapi.testclient import TestClient

from api import dados, resumo_precos
from api.main import app, obter_cliente_redis
from coleta import banco, config


HISTORICO = [
    {"preco_centavos": 34990, "coletado_em": "2026-10-01T10:00:00"},
    {"preco_centavos": 34990, "coletado_em": "2026-10-15T10:00:00"},
    {"preco_centavos": 23990, "coletado_em": "2026-11-01T10:00:00"},
]


# ---------- montar_texto_historico / _formatar_data ----------

def test_montar_texto_historico_formata_preco_e_data_em_pt_br():
    texto = resumo_precos.montar_texto_historico(HISTORICO)

    linhas = texto.splitlines()
    assert linhas == [
        "01/10/2026: R$ 349,90",
        "15/10/2026: R$ 349,90",
        "01/11/2026: R$ 239,90",
    ]


def test_montar_texto_historico_sem_preco_ativo():
    texto = resumo_precos.montar_texto_historico(
        [{"preco_centavos": None, "coletado_em": "2026-10-01T10:00:00"}]
    )
    assert texto == "01/10/2026: sem preço ativo"


# ---------- chave_resumo ----------

def test_chave_resumo_e_estavel_para_o_mesmo_pedido():
    a = resumo_precos.chave_resumo("Teclado", "texto")
    b = resumo_precos.chave_resumo("Teclado", "texto")
    assert a == b
    assert a.startswith("estom:resumo-preco:")


def test_chave_resumo_muda_se_o_produto_mudar():
    a = resumo_precos.chave_resumo("Teclado", "texto")
    b = resumo_precos.chave_resumo("Mouse", "texto")
    assert a != b


# ---------- gerar_resumo ----------

def test_gerar_resumo_chama_o_modelo_na_primeira_vez_e_grava_no_cache():
    cliente_redis = fakeredis.FakeRedis(decode_responses=True)
    chamadas = []

    def modelo_fake(mensagens):
        chamadas.append(mensagens)
        return "O preço caiu de R$349,90 pra R$239,90."

    resultado = resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=modelo_fake)

    assert resultado == {"resumo": "O preço caiu de R$349,90 pra R$239,90.", "cache": False}
    assert len(chamadas) == 1


def test_gerar_resumo_reaproveita_cache_na_segunda_vez():
    cliente_redis = fakeredis.FakeRedis(decode_responses=True)
    chamadas = []

    def modelo_fake(mensagens):
        chamadas.append(mensagens)
        return "resumo"

    resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=modelo_fake)
    resultado = resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=modelo_fake)

    assert resultado == {"resumo": "resumo", "cache": True}
    assert len(chamadas) == 1  # não chamou o modelo de novo


def test_gerar_resumo_levanta_ollama_indisponivel_se_o_modelo_nao_devolver_nada():
    cliente_redis = fakeredis.FakeRedis(decode_responses=True)

    with pytest.raises(resumo_precos.OllamaIndisponivel):
        resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=lambda m: "")


def test_gerar_resumo_levanta_cache_indisponivel_se_o_redis_falhar():
    class RedisQueFalha:
        def get(self, chave):
            raise ConnectionError("recusou conexão")

    with pytest.raises(resumo_precos.CacheIndisponivel):
        resumo_precos.gerar_resumo(RedisQueFalha(), "Teclado", HISTORICO, chamar_modelo=lambda m: "resumo")


def test_gerar_resumo_expira_e_gera_de_novo(monkeypatch):
    """Entregável da trilha veterana: 'expiração demonstrada e nova geração'.
    Não espera 1h de verdade — manda o próprio Redis fake expirar a chave
    (pexpire), que é o mesmo efeito de o TTL ter vencido. Confirma que depois
    disso o modelo é chamado de NOVO (não fica preso numa resposta velha) e
    que a resposta nova é a que volta, não a antiga."""
    cliente_redis = fakeredis.FakeRedis(decode_responses=True)
    respostas = iter(["primeira versão do resumo", "segunda versão do resumo"])
    chamadas = []

    def modelo_fake(mensagens):
        chamadas.append(mensagens)
        return next(respostas)

    primeiro = resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=modelo_fake)
    assert primeiro == {"resumo": "primeira versão do resumo", "cache": False}

    # Simula o TTL vencendo: expira a chave em 1ms e aguarda passar.
    chave = resumo_precos.chave_resumo("Teclado", resumo_precos.montar_texto_historico(HISTORICO))
    cliente_redis.pexpire(chave, 1)
    import time
    time.sleep(0.05)
    assert cliente_redis.get(chave) is None  # confirma que expirou de verdade

    segundo = resumo_precos.gerar_resumo(cliente_redis, "Teclado", HISTORICO, chamar_modelo=modelo_fake)

    assert segundo == {"resumo": "segunda versão do resumo", "cache": False}  # gerou de novo, não "false" fantasma
    assert len(chamadas) == 2  # o modelo foi chamado as duas vezes


# ---------- endpoint GET /produtos/{id}/resumo-preco ----------

@pytest.fixture
def cliente_api(tmp_path, monkeypatch):
    """TestClient com Redis fake (override de dependência) e banco de coleta
    isolado em tmp_path — mesmo padrão de tests/api/test_coleta_integracao.py."""
    monkeypatch.setattr(config, "BANCO_CAMINHO", tmp_path / "coleta.db")
    app.dependency_overrides[obter_cliente_redis] = lambda: fakeredis.FakeRedis(decode_responses=True)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(obter_cliente_redis, None)


def _semear_historico(itens_coletados):
    conexao = banco.conectar(config.BANCO_CAMINHO)
    try:
        banco.registrar_historico(conexao, config.FONTE, itens_coletados)
    finally:
        conexao.close()


def test_endpoint_devolve_resumo_quando_tudo_disponivel(cliente_api, monkeypatch):
    # produto 1 (api/dados.py) aponta pro id_externo MLB002
    _semear_historico([
        {"id_externo": "MLB002", "preco_centavos": 34990},
        {"id_externo": "MLB002", "preco_centavos": 23990},
    ])
    monkeypatch.setattr(resumo_precos, "_chamar_ollama", lambda mensagens: "caiu de R$349,90 pra R$239,90")

    resposta = cliente_api.get("/produtos/1/resumo-preco")

    assert resposta.status_code == 200
    assert resposta.json() == {"resumo": "caiu de R$349,90 pra R$239,90", "cache": False}


def test_endpoint_404_produto_inexistente(cliente_api):
    resposta = cliente_api.get("/produtos/9999/resumo-preco")
    assert resposta.status_code == 404


def test_endpoint_404_produto_sem_id_reconhecido(cliente_api):
    # produto 3 (api/dados.py) é "demo-airpods", sem id de Mercado Livre no link
    resposta = cliente_api.get("/produtos/3/resumo-preco")
    assert resposta.status_code == 404


def test_endpoint_404_sem_historico_coletado(cliente_api):
    # nenhuma coleta rodou ainda (banco nem existe) pro produto 1
    resposta = cliente_api.get("/produtos/1/resumo-preco")
    assert resposta.status_code == 404


def test_endpoint_502_quando_ollama_indisponivel(cliente_api, monkeypatch):
    _semear_historico([{"id_externo": "MLB002", "preco_centavos": 34990}])

    def ollama_fora(mensagens):
        raise resumo_precos.OllamaIndisponivel("não consegui falar com o Ollama")

    monkeypatch.setattr(resumo_precos, "_chamar_ollama", ollama_fora)

    resposta = cliente_api.get("/produtos/1/resumo-preco")
    assert resposta.status_code == 502


def test_endpoint_503_quando_redis_indisponivel(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "BANCO_CAMINHO", tmp_path / "coleta.db")
    _semear_historico([{"id_externo": "MLB002", "preco_centavos": 34990}])

    class RedisQueFalha:
        def get(self, chave):
            raise ConnectionError("recusou conexão")

    app.dependency_overrides[obter_cliente_redis] = lambda: RedisQueFalha()
    try:
        resposta = TestClient(app).get("/produtos/1/resumo-preco")
    finally:
        app.dependency_overrides.pop(obter_cliente_redis, None)

    assert resposta.status_code == 503

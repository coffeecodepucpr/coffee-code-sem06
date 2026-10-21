"""A bateria de testes do CORS: tudo o que o navegador perguntaria, perguntado com o cabeçalho Origin."""
import pytest

PAGINA = "http://127.0.0.1:5500"
OUTRA_FORMA = "http://localhost:5500"
INTRUSA = "http://localhost:3000"


def preflight(client, metodo, cabecalhos="content-type", origem=PAGINA):
    return client.options(
        "/grupos",
        headers={"Origin": origem, "Access-Control-Request-Method": metodo, "Access-Control-Request-Headers": cabecalhos},
    )


@pytest.mark.parametrize("origem", [PAGINA, OUTRA_FORMA])
def test_origens_listadas_recebem_a_autorizacao(client, origem):
    resposta = client.get("/grupos", headers={"Origin": origem})
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == origem


@pytest.mark.parametrize("origem", [INTRUSA, "null", "https://127.0.0.1:5500"])
def test_origens_fora_da_lista_recebem_200_mas_sem_autorizacao(client, origem):
    resposta = client.get("/grupos", headers={"Origin": origem})
    assert resposta.status_code == 200   # o servidor responde normalmente...
    # ...e o navegador é quem bloqueia a leitura:
    assert "access-control-allow-origin" not in resposta.headers


def test_sem_origin_nao_ha_cabecalho_cors(client):
    assert "access-control-allow-origin" not in client.get("/grupos").headers


def test_o_total_de_grupos_e_exposto_ao_javascript(client):
    resposta = client.get("/grupos", headers={"Origin": PAGINA})
    assert resposta.headers["x-total-count"] == "6"
    assert "X-Total-Count" in resposta.headers["access-control-expose-headers"]


@pytest.mark.parametrize("metodo", ["GET", "POST", "PATCH", "DELETE"])
def test_preflight_dos_metodos_liberados(client, metodo):
    resposta = preflight(client, metodo)
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == PAGINA
    assert metodo in resposta.headers["access-control-allow-methods"]


def test_preflight_de_metodo_fora_da_lista_devolve_400(client):
    resposta = preflight(client, "PUT")
    assert resposta.status_code == 400
    assert resposta.text == "Disallowed CORS method"


def test_preflight_de_cabecalho_fora_da_lista_devolve_400(client):
    resposta = preflight(client, "GET", cabecalhos="authorization")
    assert resposta.status_code == 400
    assert resposta.text == "Disallowed CORS headers"


def test_preflight_de_origem_fora_da_lista_devolve_400_sem_autorizacao(client):
    resposta = preflight(client, "POST", origem=INTRUSA)
    assert resposta.status_code == 400
    assert resposta.text == "Disallowed CORS origin"
    assert "access-control-allow-origin" not in resposta.headers


def test_o_preflight_pode_ser_guardado_por_600_segundos(client):
    assert preflight(client, "POST").headers["access-control-max-age"] == "600"


def test_barra_final_gera_redirecionamento(client):
    resposta = client.get("/grupos/", headers={"Origin": PAGINA}, follow_redirects=False)
    assert resposta.status_code == 307
    assert resposta.headers["location"].endswith("/grupos")

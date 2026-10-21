"""Os middlewares de requisição: identificador, tempo, pega-tudo e a ordem em relação ao CORS."""
import re

from conftest import PAGINA


def test_todo_pedido_ganha_um_identificador_e_um_tempo(client):
    resposta = client.get("/grupos/1")
    assert re.fullmatch(r"[0-9a-f]{12}", resposta.headers["x-request-id"])
    assert re.fullmatch(r"\d+\.\d ms".replace(" ", ""), resposta.headers["x-process-time"])


def test_um_identificador_valido_enviado_pelo_cliente_e_mantido(client):
    resposta = client.get("/grupos/1", headers={"X-Request-ID": "meu-pedido-0001"})
    assert resposta.headers["x-request-id"] == "meu-pedido-0001"
    assert resposta.json()["meta"]["requestId"] == "meu-pedido-0001"


def test_um_identificador_fora_do_formato_e_trocado(client):
    resposta = client.get("/grupos/1", headers={"X-Request-ID": "x"})
    assert resposta.headers["x-request-id"] != "x"


def test_o_erro_inesperado_vira_500_em_json_e_ainda_tem_cabecalhos_cors(client):
    resposta = client.get("/diagnostico/erro", headers={"Origin": PAGINA})
    assert resposta.status_code == 500
    assert resposta.json()["erro"]["codigo"] == "erro_interno"
    assert resposta.json()["meta"]["requestId"] == resposta.headers["x-request-id"]
    assert resposta.headers["access-control-allow-origin"] == PAGINA      # o pega-tudo está DENTRO do CORS
    assert "falha provocada" not in resposta.text                          # nada do detalhe interno vaza


def test_os_cabecalhos_do_pedido_sao_expostos_ao_javascript(client):
    exposto = client.get("/grupos", headers={"Origin": PAGINA}).headers["access-control-expose-headers"]
    assert "X-Request-ID" in exposto and "X-Process-Time" in exposto


def test_enviar_x_request_id_pelo_navegador_exige_liberar_o_cabecalho(client):
    resposta = client.options(
        "/grupos", headers={"Origin": PAGINA, "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "x-request-id"}
    )
    assert resposta.status_code == 400

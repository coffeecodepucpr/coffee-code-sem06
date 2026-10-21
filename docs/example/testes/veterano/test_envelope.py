"""O formato único de resposta: { dados, meta }, em camelCase."""


def test_lista_vem_em_um_envelope_com_meta_de_paginacao(client):
    corpo = client.get("/grupos", params={"limit": 2, "offset": 2}).json()
    assert set(corpo) == {"dados", "meta"}
    assert [g["nomeGrupo"] for g in corpo["dados"]] == ["Modelagem e SQL", "Processos e memória"]
    assert (corpo["meta"]["total"], corpo["meta"]["limit"], corpo["meta"]["offset"]) == (6, 2, 2)


def test_o_json_usa_camel_case(client):
    grupo = client.get("/grupos/3").json()["dados"]
    assert set(grupo) == {"grupoId", "nomeGrupo", "materiaId", "maxParticipantes", "descricao", "criadoEm"}
    assert grupo["criadoEm"] == "2026-09-03T12:00:00Z"


def test_o_filtro_de_materia_usa_o_nome_em_camel_case(client):
    corpo = client.get("/grupos", params={"materiaId": 1}).json()
    assert corpo["meta"]["total"] == 1


def test_criar_aceita_camel_case_e_tambem_snake_case(client):
    camel = client.post("/grupos", json={"nomeGrupo": "Redes em foco", "materiaId": 5})
    snake = client.post("/grupos", json={"nome_grupo": "Redes em foco 2", "materia_id": 5})
    assert camel.status_code == snake.status_code == 201
    assert camel.json()["dados"]["nomeGrupo"] == "Redes em foco"


def test_o_request_id_do_corpo_e_o_do_cabecalho(client):
    resposta = client.get("/grupos/1")
    assert resposta.json()["meta"]["requestId"] == resposta.headers["x-request-id"]


def test_o_delete_nao_tem_envelope_porque_nao_tem_corpo(client):
    resposta = client.delete("/grupos/1")
    assert resposta.status_code == 204 and resposta.content == b""


def test_o_swagger_documenta_os_nomes_em_camel_case(client):
    esquemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "nomeGrupo" in esquemas["GrupoOut"]["properties"]
    assert "requestId" in esquemas["MetaDeLista"]["properties"]

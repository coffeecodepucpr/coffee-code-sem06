"""O formato único de erro: { erro: { codigo, mensagem, detalhes }, meta }."""


def test_404_de_negocio(client):
    corpo = client.get("/grupos/99").json()
    assert corpo["erro"] == {"codigo": "nao_encontrado", "mensagem": "Grupo não encontrado", "detalhes": None}
    assert corpo["meta"]["requestId"]


def test_rota_inexistente_e_metodo_nao_permitido_tem_mensagem_em_portugues(client):
    assert client.get("/nada").json()["erro"]["mensagem"] == "Recurso não encontrado"
    resposta = client.delete("/grupos")
    assert resposta.status_code == 405
    assert resposta.json()["erro"]["codigo"] == "metodo_nao_permitido"
    assert "allow" in resposta.headers


def test_validacao_lista_cada_campo_com_o_nome_em_camel_case(client):
    corpo = client.post("/grupos", json={"nomeGrupo": "ab", "materiaId": 0}).json()
    assert corpo["erro"]["codigo"] == "validacao"
    assert [d["campo"] for d in corpo["erro"]["detalhes"]] == ["body.nomeGrupo", "body.materiaId"]


def test_regra_de_negocio_e_conflito(client):
    assert client.post("/grupos", json={"nomeGrupo": "Fantasma", "materiaId": 99}).json()["erro"]["codigo"] == "regra_de_negocio"
    novo = {"nomeGrupo": "Cálculo II na prática", "materiaId": 1}
    client.post("/grupos", json=novo)
    assert client.post("/grupos", json=novo).json()["erro"]["codigo"] == "conflito"


def test_patch_com_null_devolve_validacao(client):
    corpo = client.patch("/grupos/1", json={"nomeGrupo": None}).json()
    assert corpo["erro"]["detalhes"][0]["campo"] == "body.nomeGrupo"

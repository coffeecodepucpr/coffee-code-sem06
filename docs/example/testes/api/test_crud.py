NOVO = {"nome_grupo": "Cálculo II na prática", "materia_id": 1, "max_participantes": 5}


def test_lista_ordenada_por_nome_com_total(client):
    resposta = client.get("/grupos")
    nomes = [g["nome_grupo"] for g in resposta.json()]
    assert nomes == sorted(nomes, key=str.lower)
    assert resposta.headers["x-total-count"] == "6"


def test_paginacao_e_busca(client):
    pagina = client.get("/grupos", params={"limit": 2, "offset": 2})
    assert [g["nome_grupo"] for g in pagina.json()] == ["Modelagem e SQL", "Processos e memória"]
    busca = client.get("/grupos", params={"q": "prática"})
    assert len(busca.json()) == 1 and busca.headers["x-total-count"] == "1"


def test_cria_um_grupo(client):
    resposta = client.post("/grupos", json=NOVO)
    assert resposta.status_code == 201
    assert resposta.headers["location"] == "/grupos/7"


def test_nome_repetido_devolve_409_e_materia_inexistente_422(client):
    client.post("/grupos", json=NOVO)
    assert client.post("/grupos", json=NOVO).status_code == 409
    assert client.post("/grupos", json={**NOVO, "nome_grupo": "Outro grupo", "materia_id": 99}).status_code == 422


def test_patch_com_null_devolve_422_e_nao_corrompe(client):
    assert client.patch("/grupos/1", json={"nome_grupo": None}).status_code == 422
    assert client.get("/grupos").status_code == 200


def test_delete_devolve_204_sem_corpo_e_depois_404(client):
    resposta = client.delete("/grupos/2")
    assert resposta.status_code == 204 and resposta.content == b""
    assert client.delete("/grupos/2").status_code == 404

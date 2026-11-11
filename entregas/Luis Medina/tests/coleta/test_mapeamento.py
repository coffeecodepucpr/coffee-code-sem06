from coleta import mapeamento


def test_extrai_id_de_url_com_hifen():
    url = "https://produto.mercadolivre.com.br/MLB-1234567890-um-produto-qualquer"
    assert mapeamento.extrair_id_externo(url) == "MLB1234567890"


def test_extrai_id_de_url_sem_hifen():
    assert mapeamento.extrair_id_externo("https://www.mercadolivre.com.br/MLB1234567890") == "MLB1234567890"


def test_url_de_anuncio_patrocinado_usa_item_id_nao_o_id_de_catalogo():
    # caso real: link de resultado de busca, com /p/MLB... (catálogo) e
    # item_id:MLB... (anúncio de verdade) na mesma URL — o item_id vence.
    url = (
        "https://www.mercadolivre.com.br/console-sony-playstation-5-edicao-slim-disk-1tb-branco"
        "/p/MLB52897777?pdp_filters=item_id:MLB4857423967|item_id:MLB4857423967"
        "#is_advertising=true&searchVariation=MLB52897777"
    )
    assert mapeamento.extrair_id_externo(url) == "MLB4857423967"


def test_link_de_catalogo_puro_sem_item_id_vira_none():
    # só o ID de produto de catálogo, sem o ID do anúncio — não dá pra saber
    # qual anúncio consultar, então é melhor devolver None do que arriscar.
    assert mapeamento.extrair_id_externo("https://www.mercadolivre.com.br/nome/p/MLB52897777") is None


def test_url_sem_id_reconhecivel_vira_none():
    assert mapeamento.extrair_id_externo("https://www.mercadolivre.com.br/categoria/eletronicos") is None


def test_ler_produtos_monitorados_ignora_comentario_e_linha_vazia(tmp_path):
    arquivo = tmp_path / "produtos.txt"
    arquivo.write_text(
        "# comentário\n"
        "\n"
        "https://produto.mercadolivre.com.br/MLB-001-x\n"
        "https://produto.mercadolivre.com.br/MLB-002-y\n",
        encoding="utf-8",
    )
    assert mapeamento.ler_produtos_monitorados(arquivo) == ["MLB001", "MLB002"]


def test_ler_produtos_monitorados_arquivo_inexistente(tmp_path):
    assert mapeamento.ler_produtos_monitorados(tmp_path / "nao-existe.txt") == []


def test_mapear_item_pega_so_os_campos_que_interessam():
    bruto = {
        "id": "MLB001", "title": "Teclado", "price": 349.9, "currency_id": "BRL",
        "available_quantity": 5, "status": "active",
        "permalink": "https://x", "last_updated": "2026-10-01T10:00:00.000-03:00",
        "seller_id": 12345,  # não nos interessa, deve ser ignorado
    }
    item = mapeamento.mapear_item(bruto)
    assert item["id_externo"] == "MLB001"
    assert item["preco"] == 349.9
    assert "seller_id" not in item

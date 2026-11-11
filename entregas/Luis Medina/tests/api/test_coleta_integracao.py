from coleta import banco, config
from api import coleta_integracao


def _seed(tmp_path, monkeypatch, itens):
    caminho = tmp_path / "coleta.db"
    monkeypatch.setattr(config, "BANCO_CAMINHO", caminho)
    conexao = banco.conectar(caminho)
    banco.salvar_produtos(conexao, config.FONTE, itens)
    conexao.close()


def _produto(id_, url, preco_atual=999.0):
    return {
        "id": id_,
        "nome": f"produto-{id_}",
        "url": url,
        "loja": "Mercado Livre",
        "imagem": None,
        "categoriaId": 1,
        "precoMaximo": None,
        "precoAtual": preco_atual,
        "ultimaVerificacao": "2020-01-01T00:00:00Z",
        "criadoEm": "2020-01-01T00:00:00Z",
    }


def test_sobrescreve_preco_de_produto_reconhecido(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, [{
        "id_externo": "MLB001", "titulo": "Teclado", "preco_centavos": 34990,
        "moeda": "BRL", "quantidade_disponivel": 5, "status": "active",
        "permalink": "https://produto.mercadolivre.com.br/MLB-001-teclado",
        "atualizado_na_origem": "2026-11-01T10:00:00Z",
    }])

    produtos = [_produto(1, "https://produto.mercadolivre.com.br/MLB-001-teclado-mecanico")]
    resultado = coleta_integracao.aplicar_precos_coletados(produtos)

    assert resultado[0]["precoAtual"] == 349.90
    assert resultado[0]["ultimaVerificacao"] == "2026-11-01T10:00:00Z"
    # não mexe no dict original
    assert produtos[0]["precoAtual"] == 999.0


def test_produto_sem_id_reconhecido_fica_igual(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, [{
        "id_externo": "MLB001", "titulo": "Teclado", "preco_centavos": 34990,
        "moeda": "BRL", "quantidade_disponivel": 5, "status": "active",
        "permalink": "x", "atualizado_na_origem": "2026-11-01T10:00:00Z",
    }])

    produtos = [_produto(1, "https://www.mercadolivre.com.br/demo-sem-id")]
    resultado = coleta_integracao.aplicar_precos_coletados(produtos)

    assert resultado[0]["precoAtual"] == 999.0


def test_produto_inativo_nao_sobrescreve(tmp_path, monkeypatch):
    caminho = tmp_path / "coleta.db"
    monkeypatch.setattr(config, "BANCO_CAMINHO", caminho)
    conexao = banco.conectar(caminho)
    banco.salvar_produtos(conexao, config.FONTE, [{
        "id_externo": "MLB001", "titulo": "Teclado", "preco_centavos": 34990,
        "moeda": "BRL", "quantidade_disponivel": 5, "status": "active",
        "permalink": "x", "atualizado_na_origem": "2026-11-01T10:00:00Z",
    }])
    banco.inativar_sumidos(conexao, config.FONTE, ids_vistos=set())
    conexao.close()

    produtos = [_produto(1, "https://produto.mercadolivre.com.br/MLB-001-teclado-mecanico")]
    resultado = coleta_integracao.aplicar_precos_coletados(produtos)

    assert resultado[0]["precoAtual"] == 999.0


def test_sem_banco_de_coleta_nao_altera_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "BANCO_CAMINHO", tmp_path / "nao-existe.db")

    produtos = [_produto(1, "https://produto.mercadolivre.com.br/MLB-001-teclado-mecanico")]
    resultado = coleta_integracao.aplicar_precos_coletados(produtos)

    assert resultado == produtos

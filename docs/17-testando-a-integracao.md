# Módulo 17, Testando a Integração

Português · [English](../docs-eng/17-testing-the-integration.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

> **TRILHA VETERANO, MÓDULO BÔNUS**
> Este módulo faz parte da trilha veterano e é um **bônus**: ele não é necessário para o entregável da semana. Quem segue a trilha principal pode pular para o `entregavel.md`.

No Módulo 14 você percorreu um roteiro de 17 itens à mão. Funciona, mas ninguém repete 17 itens a cada pequena mudança. Este módulo troca o roteiro, em boa parte, por **testes automatizados**: um conjunto para a **API** (com `pytest`) e outro para a **página** (com `jsdom`, que simula o navegador). Também mostra, com honestidade, o que eles **não** conseguem conferir.

## // O problema: a integração quebra nas bordas

A listagem funciona e ninguém olha de novo. Meses depois, alguém mexe no CORS, e a exclusão para de funcionar só para quem usa a página. Ou alguém muda uma regra, e a última página some. Defeitos de integração aparecem **entre** as duas pontas, onde nenhum teste de uma ponta isolada olha. Os testes desta semana cobrem os dois lados e a conversa entre eles.

## // O que existe em example/testes

```
testes/
├── pytest.ini
├── requirements-testes.txt
├── api/                    22 testes: CORS e CRUD da API
├── veterano/               18 testes: envelope, erros e middlewares
└── frontend/               a página, em jsdom, contra a API de verdade
    ├── test-integracao.mjs        12 passos
    ├── test-fora-de-ordem.mjs     respostas atrasadas
    └── test-api-fora.mjs          API desligada
```

## // Parte 1: testes da API, com pytest

Instale as ferramentas, dentro do ambiente virtual da API:

```
pip install pytest httpx2
```

O `httpx2` é a biblioteca de requisições que o `TestClient` do FastAPI usa. Ele evita um aviso de descontinuação que aparece com a biblioteca `httpx`. Rode **cada pasta separadamente**, porque as duas APIs têm arquivos com o mesmo nome (`main.py`, `dados.py`):

```
cd testes/api
pytest -q
```

```
......................                                                   [100%]
22 passed in 0.08s
```

```
cd testes/veterano
pytest -q
```

```
..................                                                       [100%]
18 passed in 0.10s
```

### > A bateria de CORS

A pasta `testes/api` tem uma bateria que faz, com o cabeçalho `Origin`, todas as perguntas que o navegador faria. Cada linha corresponde a algo que você viu no Módulo 09:

```python
@pytest.mark.parametrize("origem", [INTRUSA, "null", "https://127.0.0.1:5500"])
def test_origens_fora_da_lista_recebem_200_mas_sem_autorizacao(client, origem):
    resposta = client.get("/grupos", headers={"Origin": origem})
    assert resposta.status_code == 200   # o servidor responde normalmente...
    # ...e o navegador é quem bloqueia a leitura:
    assert "access-control-allow-origin" not in resposta.headers
```

| Teste | O que garante |
|---|---|
| Origens listadas recebem a autorização | A página consegue ler as respostas |
| Origens fora da lista recebem `200`, mas sem autorização | O CORS não é uma proteção do servidor (e o navegador bloqueia) |
| O total de grupos é exposto ao JavaScript | O `expose_headers` está configurado |
| Preflight de `GET`, `POST`, `PATCH` e `DELETE` | Todos os métodos usados pela página estão liberados |
| Preflight de `PUT`, de cabeçalho fora da lista e de origem fora da lista | Devolvem `400`, com a mensagem esperada |
| O preflight pode ser guardado por 600 segundos | O `max_age` é o esperado |
| A barra final gera redirecionamento | `GET /grupos/` devolve `307` |

Se alguém tirar o `PATCH` de `allow_methods`, o teste do preflight do `PATCH` **falha na hora**, antes de qualquer pessoa descobrir pela tela.

### > Os testes da API veterano

| Arquivo | Pergunta que responde |
|---|---|
| `test_envelope.py` | A lista vem em `dados` e `meta`? O JSON usa camelCase? O Swagger documenta isso? |
| `test_erros.py` | Todo erro sai em `erro` e `meta`, com o código certo? A mensagem de `404` e `405` está em português? |
| `test_middlewares.py` | Todo pedido ganha um identificador? Um identificador inválido é trocado? O `500` sai em JSON, **com** o cabeçalho de CORS, e sem vazar o detalhe? |

## // Parte 2: testes da página, com jsdom

O `jsdom` é uma biblioteca que simula o navegador dentro do Node: ela entende o HTML da sua página, executa o seu JavaScript e deixa um teste ler e mexer no resultado. Ele precisa do **Node** e do `npm`. A versão do `jsdom` usada aqui (30.1.2) declara que exige o Node **22.22.2 ou superior** (na série 22), o **24.15 ou superior** (na série 24), ou o **26 em diante**: confira com `node --version`. Os testes foram executados no Node 22.22.2:

```
cd testes/frontend
npm install
```

Os testes conversam com a **API de verdade**, então ligue a API em outro terminal (`fastapi dev main.py`, na pasta `example/api`) antes de rodar:

```
npm test
```

Cada passo carrega a página, age como uma pessoa (digita, clica, envia o formulário) e confere o que apareceu na tela. Resultado real:

```
  OK  a página carrega: estado da API, matérias e a primeira página de grupos
  OK  a paginação mostra o total de grupos informado pela API
  OK  o botão Próxima carrega a segunda página
  OK  a busca por nome filtra a lista (com atraso) e volta à página 1
  OK  o filtro por matéria devolve só os grupos dela
  OK  um texto com HTML vindo da API aparece como texto, e não vira elemento
  OK  criar um grupo válido: mensagem, formulário limpo e total atualizado
  OK  o 422 de validação aparece no campo certo
  OK  o 409 de nome repetido vira mensagem e erro no campo
  OK  editar: o formulário é preenchido, o PATCH atualiza e o card muda
  OK  apagar pede confirmação: cancelar não apaga, confirmar apaga
  OK  apagar o último item da última página volta para a última página que existe

12 passos conferidos
```

Para a versão veterano, o mesmo teste roda sem mudar uma linha, apontando a pasta do front-end e ligando a API veterano:

```
FRONTEND=../../veterano/frontend npm test
```

Essa forma de definir a variável `FRONTEND` vale para o terminal do macOS e do Linux. No Windows, a sintaxe muda (no PowerShell, `$env:FRONTEND="../../veterano/frontend"` em uma linha, e `npm test` na seguinte), e **não foi testada**.

### > Dois testes que merecem atenção

**A API desligada.** Rode com a API **parada**:

```
npm run test:api-fora
```

```
  OK  com a API desligada, a página avisa em vez de quebrar
```

**As respostas fora de ordem.** Este teste atrasa **de propósito** uma resposta, para simular uma rede irregular:

```js
// A segunda página SEM filtro de matéria demora 500 ms:
// ela será a resposta velha.
globalThis.fetch = async (url, opcoes) => {
  const endereco = String(url);
  if (endereco.includes("offset=4") && !/materia_?[iI]d=/.test(endereco)) {
    await dormir(500);
  }
  return fetchOriginal(url, opcoes);
};
```

A página pede a segunda página (lenta) e, em seguida, filtra por matéria (rápido). Se a resposta velha sobrescrevesse a nova, a tela mostraria os grupos errados. O teste confere que ela **não** sobrescreve:

```
  OK  a resposta velha (lenta) foi descartada, e a tela mostra a mais nova
```

E, para saber se o teste serve de verdade, foi feita a **prova ao contrário**: removeu-se do `app.js` a linha que descarta a resposta velha, e o teste **falhou**, com `a resposta velha NÃO pode sobrescrever a nova`. Um teste que nunca falha não protege nada, e a única forma de saber é quebrar o código de propósito.

## // O que os testes automatizados NÃO conferem

> **A LIMITAÇÃO MAIS IMPORTANTE DO MÓDULO**
> O teste da página usa o `fetch` do Node dentro do `jsdom`. O Node **não aplica o CORS**: ele não envia o preflight, não confere o `Access-Control-Allow-Origin` e não esconde cabeçalhos. Portanto, um teste da página **verde** não prova que o navegador vai aceitar as respostas. A parte do CORS está coberta pelos testes da **API** (que conferem os cabeçalhos exatos que o navegador pede), e, na outra ponta, pelos itens 15 a 17 do roteiro do Módulo 14, que só um navegador de verdade consegue conferir.

| Conferência | Teste da API | Teste da página (jsdom) | Navegador |
|---|---|---|---|
| A API responde os cabeçalhos CORS certos | Sim | Não | Sim |
| O navegador aceita e entrega a resposta | Não | Não | **Só aqui** |
| A página mostra a lista, os erros e a paginação certos | Não | **Sim** | Sim |
| O JavaScript lê o `X-Total-Count` entre origens | Não | Não | **Só aqui** |
| O aspecto visual (cores, posição) | Não | Não | **Só aqui** |

Os três tipos de teste se complementam: nenhum deles substitui os outros.

## // Bom exemplo × mau exemplo

**Mau exemplo**: um teste que sempre passa:

```js
assert.ok(true);
```

**Bom exemplo**: um teste que você **sabe** que falha quando o código quebra:

```
1. Rode o teste: verde.
2. Quebre o código de propósito (remova a proteção).
3. Rode o teste: vermelho. Se ele continuar verde, o teste não serve.
4. Restaure o código.
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `ModuleNotFoundError: No module named 'main'` | O `pytest` foi rodado na pasta errada | Rode dentro de `testes/api` ou de `testes/veterano` |
| Conflito entre as duas APIs ao rodar `pytest` na raiz | As duas têm `main.py` e `dados.py` | Rode cada pasta separadamente |
| `npm install` ou o teste reclama da versão do Node | O `jsdom` exige um Node mais novo | Atualize o Node (veja a versão exigida acima) |
| `TypeError: fetch failed` no teste da página | A API não está ligada, ou está em outra porta | Ligue a API na porta 8000 antes do teste |
| O teste da página falha na segunda execução | A API guarda dados em memória e o teste mexeu neles | Reinicie a API (salve o `main.py`) entre as execuções |
| Os testes da página rodam contra a API errada | O front-end veterano precisa da API veterano | Combine: API e front-end da **mesma** versão |
| O teste passa, mas o navegador falha com CORS | O `jsdom` não aplica o CORS | Confira o CORS nos testes da API e nos itens 15 a 17 do Módulo 14 |
| Um teste que nunca falha | Não confere nada de verdade | Faça a prova ao contrário: quebre o código e veja o teste falhar |

## // Prática guiada

1. Instale `pytest` e `httpx2` e rode os testes da pasta `testes/api`. Leia os nomes: cada um é uma frase.
2. Remova `"PATCH"` de `allow_methods` no `main.py` da API e rode de novo. Quais testes falharam? Restaure.
3. Rode os testes da pasta `testes/veterano` e leia `test_middlewares.py`.
4. Ligue a API, rode `npm install` e `npm test` em `testes/frontend`, e acompanhe os 12 passos.
5. Faça a prova ao contrário no teste de ordem: comente a linha `if (numero !== ultimoPedido) return;` no `carregarGrupos` do `app.js` e rode `npm run test:fora-de-ordem`. Restaure.

## // Pratique sozinho

> **DESAFIO**
> Escreva um novo passo para o teste da página: **o botão Salvar fica desabilitado enquanto o envio está em andamento**. Dica: use o truque do `test-fora-de-ordem.mjs` para atrasar a resposta do `POST`, envie o formulário e confira `salvar.disabled === true` antes de a resposta chegar, e `false` depois. Faça também a prova ao contrário (remova o `travarFormulario`).

## // Aplicando no projeto da semana

1. Copie a pasta `testes/api` para o seu projeto e rode-a antes de cada alteração no CORS.
2. Guarde no `README.md` o comando de cada teste e **o que eles não cobrem** (o CORS no navegador).
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Adiciona testes de integração"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Os 12 passos do teste da página passam, e os 22 testes da API também. Ainda assim, no navegador, a listagem falha por CORS. Como isso é possível, e o que os testes não viram?

Resposta: o teste da página usa o `fetch` do Node, que **não aplica o CORS**, então ele recebe a resposta mesmo que o servidor não a autorize. Os testes da API conferem os cabeçalhos CORS para as origens **que foram testadas**: se a origem real do navegador (por exemplo, `localhost` em vez de `127.0.0.1`) não estava na bateria, ou se a configuração mudou depois, nada falha. O que faltou foi o item mais valioso: **ver a página rodando em um navegador**, na aba Rede, com a origem real. Teste automatizado reduz o risco, e não o elimina.

## // Resumo do módulo

- [ ] Sei rodar os testes da API com `pytest`, cada pasta separadamente, e ler os nomes como frases.
- [ ] Sei o que a bateria de CORS garante, e que ela falha se alguém quebrar a configuração.
- [ ] Sei rodar o teste da página com `jsdom`, contra a API de verdade.
- [ ] Sei simular uma rede lenta atrasando uma resposta.
- [ ] Sei fazer a prova ao contrário: quebrar o código para ver o teste falhar.
- [ ] Sei o que os testes automatizados não conferem, e por que o navegador continua indispensável.

---

**Próximo passo:** `entregavel.md`, a revisão final de tudo que a Semana 06 pede.

`Material de Estudo // Coffee & Code`

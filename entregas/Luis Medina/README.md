# Estom

O Estom é um sistema de monitoramento de preços criado para ajudar pessoas que
desejam acompanhar produtos online sem precisar verificar manualmente seus
preços todos os dias.

O projeto está sendo desenvolvido durante o Coffee & Code da PUCPR e será
evoluído ao longo das próximas semanas.

## Objetivo

A primeira versão do Estom será focada no monitoramento de produtos do
Mercado Livre.

O usuário poderá cadastrar produtos, definir opcionalmente um preço máximo
desejado e acompanhar a situação do preço em relação à meta definida.

Futuramente, o sistema também deverá realizar o monitoramento automático dos
preços e enviar alertas quando as condições definidas pelo usuário forem
atingidas.

## Estado atual

Atualmente, o frontend inicial da aplicação está implementado utilizando
HTML, CSS e JavaScript.

A interface possui:

- visualização dos produtos monitorados;
- diferentes estados em relação à meta de preço;
- formulário de cadastro através de modal;
- tema claro e escuro;
- layout responsivo para desktop e dispositivos móveis;
- navegação por teclado;
- padrões visuais definidos através de um Design System.

A página está integrada à API REST (Semana 06): lista, busca, filtra, pagina,
cadastra, edita e exclui produtos pela API.

Os produtos e preços apresentados atualmente são dados de demonstração: o
monitoramento automático de preços ainda não existe, e um produto cadastrado
fica como "Aguardando atualização".

## Funcionalidades planejadas

- Cadastro de usuários;
- Cadastro de produtos para monitoramento;
- Monitoramento diário de preços;
- Definição opcional de preço máximo;
- Armazenamento do histórico de preços;
- Alertas por e-mail quando o preço desejado for atingido;
- Pausa, edição e exclusão de produtos monitorados.

## Tecnologias utilizadas

- HTML5;
- CSS3;
- JavaScript (módulos ES, `fetch` e `async/await`, sem frameworks);
- Python, FastAPI e Pydantic (API REST).

Novas tecnologias poderão ser adicionadas conforme a evolução da aplicação.

## API REST

A API REST do Estom está sendo desenvolvida com Python e FastAPI. Nesta etapa, ela permite cadastrar, listar, consultar, atualizar e excluir produtos monitorados.

Os dados são armazenados temporariamente em memória, portanto são perdidos quando a aplicação é reiniciada.


### Requisitos

- Python instalado;
- pip para instalação das dependências.

### Instalação

Na raiz do projeto, crie e ative um ambiente virtual.

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### Execução (duas pontas, dois terminais)

**Terminal 1 — API**, na raiz do projeto, com o ambiente virtual ativado:

```bash
fastapi dev api/main.py
```

A API fica em http://127.0.0.1:8000. Use sempre `fastapi dev` (atende só o
seu computador), e não `fastapi run`.

**Terminal 2 — página**, também na raiz do projeto:

```bash
py -m http.server 5500 --bind 127.0.0.1
```

(No macOS/Linux: `python3 -m http.server 5500 --bind 127.0.0.1`.)

Abra http://127.0.0.1:5500 no navegador. A página não funciona aberta
direto pelo arquivo (`file://`): ela precisa ser servida por HTTP.

Os dados ficam em memória: sempre que a API reinicia (o `fastapi dev`
reinicia ao salvar um arquivo), eles voltam ao estado inicial.

### Origens

A página e a API rodam em portas diferentes, então para o navegador são
**origens diferentes**, e a API precisa autorizar a página pelo CORS.

| Origem | O que é |
|---|---|
| `http://127.0.0.1:5500` | A página (autorizada) |
| `http://localhost:5500` | A mesma página, aberta por outro nome (autorizada) |
| `http://127.0.0.1:8000` | A API |

Configuração do CORS (`api/main.py`):

- `allow_origins`: só as duas origens da página (nunca `"*"`);
- `allow_methods`: `GET`, `POST`, `PATCH` e `DELETE` (os que a página usa);
- `allow_headers`: `Content-Type` (para enviar JSON);
- `expose_headers`: `X-Total-Count` (para o JavaScript ler o total da paginação).

### Testando o CORS com curl

No PowerShell, use `curl.exe` (o `curl` sozinho é outro comando). Com a API
ligada:

```bash
curl.exe -i -X OPTIONS "http://127.0.0.1:8000/produtos" -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type"
curl.exe -i -X OPTIONS "http://127.0.0.1:8000/produtos/1" -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: PATCH" -H "Access-Control-Request-Headers: content-type"
curl.exe -i -X OPTIONS "http://127.0.0.1:8000/produtos/1" -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: DELETE"
curl.exe -i -X OPTIONS "http://127.0.0.1:8000/produtos/1" -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: PUT"
curl.exe -i "http://127.0.0.1:8000/produtos?limit=2" -H "Origin: http://localhost:5500"
```

| Pedido | Resultado esperado |
|---|---|
| Preflight de POST, PATCH e DELETE | `200`, com `access-control-allow-methods: GET, POST, PATCH, DELETE` |
| Preflight de PUT | `400 Disallowed CORS method` (a página não usa PUT) |
| GET com `Origin: http://localhost:5500` | `200`, com `x-total-count`, `access-control-allow-origin` e `access-control-expose-headers: X-Total-Count` |
| GET com uma origem fora da lista | `200`, mas **sem** `access-control-allow-origin` (o navegador bloquearia) |

### Documentação interativa

Com a API em execução, acesse:

- [Swagger UI](http://127.0.0.1:8000/docs)
- [OpenAPI JSON](http://127.0.0.1:8000/openapi.json)

### Endpoints disponíveis

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/produtos` | Cadastra um produto |
| GET | `/produtos` | Lista os produtos |
| GET | `/produtos/{produto_id}` | Consulta um produto |
| PUT | `/produtos/{produto_id}` | Substitui os dados de um produto |
| PATCH | `/produtos/{produto_id}` | Atualiza parcialmente um produto |
| DELETE | `/produtos/{produto_id}` | Exclui um produto |
| GET | `/categorias` | Lista as categorias |
| GET | `/categorias/{categoria_id}` | Consulta uma categoria por ID |
| GET | `/produtos/{produto_id}/resumo-preco` | Resume em português a variação de preço (Semana 08 — Smart Hub) |

O `GET /produtos` aceita parâmetros opcionais: `q` (busca por parte do
nome), `categoriaId`, `limit` (1 a 100, padrão 10) e `offset` (padrão 0). A
resposta vem em ordem alfabética e traz o cabeçalho `X-Total-Count`, com o
total de produtos que atendem aos filtros.

A API valida os dados recebidos e utiliza códigos de status HTTP para indicar
sucesso ou erros nas operações:

| Situação | Status |
|---|---|
| Nome com menos de 3 ou mais de 60 caracteres | 422 |
| Link que não é do Mercado Livre (`mercadolivre.com.br`) | 422 |
| Categoria que não existe | 422 |
| Preço máximo menor ou igual a zero | 422 |
| Link já cadastrado em outro produto | 409 |
| Produto inexistente | 404 |
| Resumo de preço: produto não identificado no ML, ou sem histórico coletado | 404 |
| Resumo de preço: Ollama não respondeu | 502 |
| Resumo de preço: Redis/Memurai não respondeu | 503 |

### Rotas usadas pela página

| Ação na página | Pedido |
|---|---|
| Carregar as categorias (filtro e formulário) | `GET /categorias` |
| Listar, buscar, filtrar e paginar | `GET /produtos?q=&categoriaId=&limit=4&offset=` |
| Cadastrar | `POST /produtos` |
| Editar | `PATCH /produtos/{id}` |
| Excluir | `DELETE /produtos/{id}` |

### Os estados da tela

- **Carregando:** enquanto a API não responde, a página mostra "Carregando...".
- **Sucesso:** os cartões dos produtos e a paginação ("Página N de M (T produtos)").
- **Vazio:** a API respondeu sem itens, e a página mostra "Nenhum produto encontrado."
- **Erro:** a página explica o que houve; com a API desligada, o indicador
  muda para "API fora do ar".

No formulário, um erro de validação (422) aparece embaixo do campo certo, e um
link repetido (409) mostra uma mensagem de conflito no campo da URL. O botão de
salvar fica desabilitado durante o envio.

## Interface

A interface segue uma abordagem mobile-first e utiliza componentes e tokens
visuais documentados no Design System.

Também foram implementados temas claro e escuro, além de cuidados com
contraste, navegação por teclado e foco visível.

A interface foi auditada utilizando o Lighthouse e atingiu pontuação 100 na
categoria Accessibility.

## Protótipo

O fluxo inicial da aplicação foi desenvolvido no Figma.

[Acessar protótipo no Figma](https://www.figma.com/proto/oL9MehNA1Gea3Zhzh8I69z/Sem-t%C3%ADtulo?node-id=0-1)

## Documentação

A documentação do projeto está disponível na pasta [docs](./docs).

- [Requisitos](./docs/requisitos.md)
- [Histórias de usuário](./docs/historias-de-usuario.md)
- [Design System](./docs/design-system.md)
- [Arquitetura inicial](./docs/arquitetura.md)

## Estrutura do projeto

```text
Estom/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── dados.py
│   ├── schemas.py
│   ├── coleta_integracao.py
│   ├── resumo_precos.py
│   └── README.md          # Semana 08 — Smart Hub (resumo de preço com IA)
├── assets/
│   ├── css/
│   ├── images/
│   └── js/
│       ├── api.js
│       ├── ui.js
│       ├── app.js
│       ├── login.js
│       └── perfil.js
├── docs/
├── supabase/
├── index.html
├── login.html
├── perfil.html
├── requirements.txt
└── README.md
```

### O que cada arquivo faz

| Arquivo | Responsabilidade |
|---|---|
| `api/main.py` | As rotas, as regras e a configuração do CORS |
| `api/dados.py` | Os dados de demonstração, em memória |
| `api/schemas.py` | O formato e a validação dos dados (Pydantic) |
| `api/coleta_integracao.py` | Liga os preços coletados (Semana 07) aos produtos exibidos |
| `api/resumo_precos.py` | Resumo de preço com IA + cache (Semana 08 — Smart Hub) |
| `api/__init__.py` | Marca `api` como pacote, para o `fastapi dev api/main.py` funcionar |
| `index.html` | A estrutura da página de produtos |
| `assets/css/style.css` | A aparência (Design System) |
| `assets/js/api.js` | O único lugar que conhece o endereço da API e chama o `fetch` |
| `assets/js/ui.js` | O único lugar que lê e escreve a página (sempre com `textContent`) |
| `assets/js/app.js` | A orquestração: eventos, estado e os estados da tela |
| `login.html`, `perfil.html` e seus `.js` | Telas de demonstração, ainda sem integração |

## Roteiro de verificação (Semana 06)

Com as duas pontas ligadas e a página aberta em http://127.0.0.1:5500, com as
abas Rede e Console abertas. A API deve estar recém-iniciada (dados de
demonstração: 5 produtos).

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 1 | Abrir a página | O indicador mostra "API conectada" | |
| 2 | Olhar a lista | Quatro produtos, em ordem alfabética: Apple AirPods 4, Cadeira do escritório, Monitor, PlayStation 5 Slim | |
| 3 | Olhar a paginação | "Página 1 de 2 (5 produtos)", com Anterior desabilitado | |
| 4 | Clicar em Próxima | Teclado mecânico ("Aguardando atualização"), e Próxima desabilitado | |
| 5 | Buscar `play` | Só PlayStation 5 Slim, e "Página 1 de 1 (1 produto)" | |
| 6 | Buscar `zzz` | "Nenhum produto encontrado." | |
| 7 | Escolher a categoria Games | Só PlayStation 5 Slim | |
| 8 | Cadastrar "Mouse sem fio", link `https://www.mercadolivre.com.br/mouse-sem-fio`, Periféricos, meta 150 | "Produto cadastrado.", modal fechado, "Página 1 de 2 (6 produtos)" | |
| 9 | Enviar o nome `ab` | O erro "String should have at least 3 characters" no campo do nome | |
| 10 | Cadastrar o mesmo link de novo | "Este produto já está cadastrado." no campo da URL | |
| 11 | Editar o Mouse sem fio, mudando a meta para 120 | "Produto atualizado.", o cartão mostra "Meta: R$ 120,00" | |
| 12 | Excluir o Mouse sem fio, cancelando e depois confirmando | Cancelar não exclui; confirmar exclui e volta a 5 produtos | |
| 13 | Cadastrar quatro produtos extras, ir à página 3 e excluir o único item dela | Volta para a página 2, sem mostrar "Página 3 de 2" | |
| 14 | Parar a API (Ctrl+C) e buscar algo | O indicador muda para "API fora do ar" e a mensagem explica o que houve | |
| 15 | Aba Rede, ao cadastrar | Um `OPTIONS` (preflight) com 200, e depois o `POST` com 201 | |
| 16 | Aba Rede, nos cabeçalhos da listagem | `access-control-allow-origin: http://127.0.0.1:5500` e `access-control-expose-headers: X-Total-Count` | |
| 17 | Aba Console | Nenhum erro de JavaScript durante o roteiro (o aviso do passo 14 e as linhas vermelhas de "Failed to load resource" dos erros 422/409 provocados nos passos 9 e 10 são esperados) | |

## Status do projeto

Em desenvolvimento.

O Estom está sendo desenvolvido de forma incremental durante os encontros do
Coffee & Code da PUCPR.

## Escopo inicial

A primeira versão será focada no Mercado Livre.

Outras lojas e funcionalidades adicionais poderão ser consideradas em versões
futuras.

## Pipeline de coleta de preços (Semana 07)

Entregável da Semana 07 do Coffee & Code (Data & Scraping), adaptado pra consultar a API oficial do Mercado Livre em vez de um site de treino — a primeira coleta de preço de verdade do projeto. Ver [coleta/README.md](./coleta/README.md).

## Resumo de preço com IA (Semana 08 — Smart Hub)

Entregável da Semana 08 do Coffee & Code (Data & Scraping — Parte 2: Smart Hub), adaptado da trilha veterana (resumo de vaga) pro domínio do Estom (resumo da variação de preço de um produto monitorado, usando IA local via Ollama e cache via Redis/Memurai). Ver [api/README.md](./api/README.md).

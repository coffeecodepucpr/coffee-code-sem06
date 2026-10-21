# Módulo 15, Middlewares de Requisição

Português · [English](../docs-eng/15-request-middlewares.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

> **TRILHA VETERANO**
> Este módulo faz parte da trilha veterano: ele vem depois do conteúdo essencial e não é necessário para o entregável da semana. Quem segue a trilha principal pode pular para o `entregavel.md`.

Você já usou um middleware sem saber o nome: o `CORSMiddleware` do Módulo 09. Este módulo mostra como **escrever os seus**, para resolver três problemas reais da integração: ligar uma reclamação da tela a uma linha do log do servidor, medir quanto cada pedido demora, e fazer um erro inesperado chegar à página como um `500` legível, e não como um erro de CORS. O código completo está em `example/veterano/api/`.

## // O problema: do sintoma ao log

A pessoa diz: "a página deu erro às 14h". No servidor, há milhares de linhas de log desse horário. Sem um identificador que ligue as duas pontas, achar o pedido certo é adivinhação. Há ainda dois problemas vizinhos: ninguém sabe quais pedidos estão lentos, e, quando a API quebra com um erro inesperado, o navegador mostra um erro de CORS, em vez do `500` real (Módulo 09).

## // O que é um middleware

> **MIDDLEWARE: EM PALAVRAS SIMPLES**
> É uma camada de código que fica **entre** o servidor e as rotas. Todo pedido passa por ela na ida, e toda resposta passa por ela na volta. Ela pode olhar, registrar, medir, acrescentar cabeçalhos, ou até responder no lugar da rota.

<div align="center">
<img src="./assets/svg/middlewares-cebola.svg" alt="Os middlewares como camadas de cebola: ServerError, CORS, IdentificadorDoPedido, PegaTudo e as rotas" width="640">
</div>

Os middlewares formam **camadas**, como as de uma cebola: o pedido entra pela camada de fora, atravessa cada uma até a rota, e a resposta volta pelo mesmo caminho. A **ordem** das camadas importa, e ela decide o comportamento. Veja a regra, verificada em um teste com dois middlewares que anunciam quando entram e saem:

```python
app.add_middleware(A)    # adicionado primeiro
app.add_middleware(B)    # adicionado depois
```

```
B (adicionado 2º): entra > A (adicionado 1º): entra > rota >
A (adicionado 1º): sai > B (adicionado 2º): sai
```

> **A REGRA DA ORDEM**
> O **último** middleware adicionado é o **mais externo**: é o primeiro a ver o pedido e o último a ver a resposta. Parece ao contrário, porque a leitura de cima para baixo no código é a leitura de **dentro para fora**.

## // Escrevendo um middleware: o esqueleto ASGI

O Starlette (a base do FastAPI) permite escrever um middleware como uma classe simples, no padrão **ASGI**: ela recebe a aplicação seguinte e é chamada a cada conexão com três argumentos.

| Argumento | O que é |
|---|---|
| `scope` | Um dicionário com os dados do pedido (método, caminho, cabeçalhos) |
| `receive` | Uma função para ler o corpo do pedido |
| `send` | Uma função para enviar a resposta, em mensagens |

```python
class IdentificadorDoPedido:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        # ...olhar o pedido, chamar self.app(...) e olhar a resposta...
```

O padrão é sempre o mesmo: conferir se é uma conexão HTTP, fazer o que se quer **antes**, chamar `self.app(...)` (a próxima camada) e fazer o que se quer **depois**. O Starlette também oferece uma forma mais curta, a classe `BaseHTTPMiddleware`, com um método `dispatch`, e ela funciona (foi testada). Este módulo usa o ASGI puro porque ele mostra exatamente o que passa por dentro.

## // Middleware 1: identificar, medir e registrar

O `IdentificadorDoPedido` faz quatro coisas em um só lugar:

```python
FORMATO_DO_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")

class IdentificadorDoPedido:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        recebido = dict(scope["headers"]).get(b"x-request-id", b"")
        recebido = recebido.decode("latin-1")
        valido = FORMATO_DO_ID.match(recebido)
        identificador = recebido if valido else uuid.uuid4().hex[:12]
        scope.setdefault("state", {})["request_id"] = identificador
        inicio = time.perf_counter()
        codigo = 0

        async def enviar(mensagem: Message):
            nonlocal codigo
            if mensagem["type"] == "http.response.start":
                codigo = mensagem["status"]
                duracao = (time.perf_counter() - inicio) * 1000
                cabecalhos = list(mensagem.get("headers", []))
                cabecalhos.append((b"x-request-id", identificador.encode()))
                tempo = f"{duracao:.1f}ms".encode()
                cabecalhos.append((b"x-process-time", tempo))
                mensagem = {**mensagem, "headers": cabecalhos}
            await send(mensagem)

        try:
            await self.app(scope, receive, enviar)
        finally:
            duracao = (time.perf_counter() - inicio) * 1000
            logger.info(
                "request_id=%s metodo=%s caminho=%s status=%s ms=%.1f",
                identificador, scope["method"], scope["path"], codigo, duracao,
            )
```

| Parte | O que faz |
|---|---|
| `recebido` e `FORMATO_DO_ID` | Aceita um identificador enviado pelo cliente **só se** tiver um formato seguro (8 a 64 letras, números, ponto, sublinhado ou hífen). Um valor qualquer vindo de fora não vai direto para o log |
| `uuid.uuid4().hex[:12]` | Cria um identificador novo, de 12 caracteres, quando o cliente não mandou um válido |
| `scope["state"]["request_id"]` | Deixa o identificador à disposição das rotas e dos tratadores de erro |
| `enviar(...)` | Intercepta o envio da resposta para **acrescentar** os cabeçalhos `x-request-id` e `x-process-time` |
| O `finally` | Registra uma linha de log **sempre**, mesmo se a rota falhar |

### > O que a API devolve

```
GET /grupos?limit=2   (com Origin: http://127.0.0.1:5500)

HTTP/1.1 200 OK
x-request-id: 34c8e750cdbe
x-process-time: 2.4ms
access-control-expose-headers: X-Request-ID, X-Process-Time
access-control-allow-origin: http://127.0.0.1:5500
```

Um identificador **válido** enviado pelo cliente é mantido, e um **inválido** é trocado:

```
X-Request-ID enviado: meu-pedido-0001   ->   x-request-id: meu-pedido-0001
X-Request-ID enviado: x                 ->   x-request-id: b251fa462c28
```

E o log do servidor registra cada pedido, uma linha por pedido, com o mesmo identificador (os tempos foram arredondados aqui):

```
request_id=34c8e750cdbe metodo=GET caminho=/grupos status=200 ms=2.4
request_id=6bd607602de2 metodo=GET caminho=/grupos/99 status=404 ms=2.4
request_id=70960d45d4b3 metodo=POST caminho=/grupos status=201 ms=2.4
request_id=db0d3b05d6db metodo=DELETE caminho=/grupos status=405 ms=2.4
```

Agora a pessoa que reclamou pode informar o identificador que a tela mostrou, e quem mantém a API acha **a linha exata** no log.

## // Middleware 2: o pega-tudo

Quando uma rota levanta um erro que ninguém previu, o Starlette o trata em uma camada que **sempre fica por fora de todas as outras**, a `ServerErrorMiddleware`. A resposta que ela gera **não passa pelo CORS**, e sai sem cabeçalhos de autorização: no navegador, o `500` vira um erro de CORS (Módulo 09). Resultado real, mesmo com um `@app.exception_handler(Exception)`:

```
GET /quebra   (com Origin permitida)

500  {"erro": "erro_interno"}      cabeçalhos CORS: nenhum
```

A correção é um middleware que captura o erro **antes** de ele chegar à camada de fora, ainda **dentro do CORS**:

```python
class PegaTudo:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        iniciada = False

        async def enviar(mensagem: Message):
            nonlocal iniciada
            if mensagem["type"] == "http.response.start":
                iniciada = True
            await send(mensagem)

        try:
            await self.app(scope, receive, enviar)
        except Exception:
            identificador = scope.get("state", {}).get("request_id")
            logger.exception(
                "request_id=%s erro inesperado em %s %s",
                identificador, scope["method"], scope["path"],
            )
            if iniciada:
                raise  # a resposta já começou a sair: não dá para trocá-la
            corpo = {
                "erro": {
                    "codigo": "erro_interno",
                    "mensagem": "Erro interno do servidor",
                    "detalhes": None,
                },
                "meta": {"requestId": identificador},
            }
            await JSONResponse(corpo, status_code=500)(scope, receive, send)
```

Três decisões:

- O `iniciada` evita um erro pior: se a resposta já começou a sair, não dá mais para trocá-la por um `500`, então o erro segue adiante.
- O **detalhe interno vai para o log** (`logger.exception`, com o identificador), e **nunca** para o cliente: a resposta traz só a mensagem genérica.
- A resposta do `500` usa o mesmo formato de erro da API (Módulo 16), com o `requestId`.

### > A prova de que a posição importa

O mesmo `PegaTudo`, em duas posições, em um teste:

| Posição | Resultado do `500` |
|---|---|
| **Dentro** do CORS (adicionado antes dele) | `500` em JSON, com `access-control-allow-origin` |
| **Fora** do CORS (adicionado depois dele) | `500` em JSON, **sem** os cabeçalhos CORS |

O que o log registra, quando a rota `/diagnostico/erro` (que provoca um erro de propósito) é chamada:

```
request_id=8525fa0eceac erro inesperado em GET /diagnostico/erro
    raise RuntimeError("falha provocada de propósito")
```

E o cliente recebe só isto:

```
HTTP/1.1 500 Internal Server Error
x-request-id: 8525fa0eceac
access-control-allow-origin: http://127.0.0.1:5500
{"erro":{"codigo":"erro_interno","mensagem":"Erro interno do servidor",
         "detalhes":null},"meta":{"requestId":"8525fa0eceac"}}
```

O texto `falha provocada` não aparece na resposta: só no log.

> **A ROTA DE DIAGNÓSTICO**
> A rota `GET /diagnostico/erro` existe só para estudar o `500`. Em um sistema real, **remova-a**: uma rota que derruba a aplicação por pedido é um convite para abusos.

## // Montando na ordem certa

No `main.py` da API veterano:

```python
# A ORDEM IMPORTA: o último middleware adicionado é o mais EXTERNO.
#   CORS  >  IdentificadorDoPedido  >  PegaTudo  >  rotas
app.add_middleware(PegaTudo)
app.add_middleware(IdentificadorDoPedido)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)
```

| Camada | Por que fica ali |
|---|---|
| `PegaTudo`, a mais interna | Pega o erro antes de ele sair do conjunto. O `500` que ela cria ainda atravessa as outras duas |
| `IdentificadorDoPedido`, no meio | Vê o identificador, o status e o tempo de **todas** as respostas, inclusive o `500` do pega-tudo |
| `CORSMiddleware`, a mais externa dos três | Acrescenta os cabeçalhos CORS a **toda** resposta que sai, incluindo o `500` |

### > Conferindo a pilha de verdade

Não precisa acreditar na ordem: o FastAPI deixa você **olhar** a pilha montada. O código abaixo percorre as camadas, da mais externa para a mais interna, e imprime o nome de cada uma:

```python
pilha = main.app.build_middleware_stack()
atual, nomes = pilha, []
while atual is not None:
    nomes.append(type(atual).__name__)
    atual = getattr(atual, "app", None)
print(" > ".join(nomes))
```

Resultado real, nesta versão, com a API veterano:

```
ServerErrorMiddleware
> ExceptionTelemetryMiddleware
> CORSMiddleware
> IdentificadorDoPedido
> PegaTudo
> ExceptionMiddleware
> AsyncExitStackMiddleware
> APIRouter
```

Reconheça as três camadas suas (`CORSMiddleware`, `IdentificadorDoPedido` e `PegaTudo`), na ordem esperada. As demais pertencem ao framework e **variam entre versões**: o desenho do início do módulo mostra só as que importam aqui. O `ServerErrorMiddleware` é, de fato, a mais externa de todas.

Os cabeçalhos novos precisam ser **expostos** (`expose_headers`), senão o JavaScript da página não os lê (Módulo 13). E atenção a um detalhe de sentido contrário: se a **página** passar a enviar um cabeçalho `X-Request-ID`, ele precisa ser liberado em `allow_headers`. Resposta real a um preflight que pergunta por esse cabeçalho, sem a liberação:

```
OPTIONS /grupos   (Access-Control-Request-Headers: x-request-id)

400 Bad Request
```

## // Usando o identificador na página

No front-end veterano, o `ErroHttp` guarda o identificador, lido do cabeçalho da resposta (que ficou legível graças ao `expose_headers`) ou do corpo do erro:

```js
export class ErroHttp extends Error {
  constructor(status, corpo, requestId) {
    super(corpo?.erro?.mensagem ?? `A API respondeu ${status}`);
    this.name = "ErroHttp";
    this.status = status;
    this.codigo = corpo?.erro?.codigo ?? null;
    this.detalhes = corpo?.erro?.detalhes ?? [];
    this.requestId = requestId ?? corpo?.meta?.requestId ?? null;
  }
}
```

E a mensagem de erro da tela passa a trazer o identificador:

```js
ui.mostrarMensagem(`${erro.message} (pedido ${erro.requestId})`, "erro");
```

A tela mostra algo como `Erro interno do servidor (pedido 8525fa0eceac)`. A pessoa informa o identificador, e quem mantém a API acha, no log, a linha e o erro exato.

## // Bom exemplo × mau exemplo

**Mau exemplo**: registrar o erro no log sem ligá-lo ao pedido:

```
ERROR erro inesperado
Traceback (most recent call last): ...
```

Em um log com milhares de linhas, não há como saber de qual pedido (e de qual pessoa) veio este erro.

**Bom exemplo**: o mesmo identificador no log, no cabeçalho e na tela:

```
log:   request_id=8525fa0eceac erro inesperado em GET /diagnostico/erro
resp:  x-request-id: 8525fa0eceac
tela:  Erro interno do servidor (pedido 8525fa0eceac)
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O `500` aparece como erro de CORS no navegador | O pega-tudo está **fora** do CORS, ou não existe | Adicione o pega-tudo **antes** do CORS (a ordem das chamadas `add_middleware`) |
| A página não consegue ler o `x-request-id` | Faltou `expose_headers` | Acrescente os cabeçalhos ao `expose_headers` |
| O preflight falha ao enviar `X-Request-ID` pela página | O cabeçalho não está em `allow_headers` | Libere o cabeçalho |
| O log vem sem o identificador | O middleware do identificador está **dentro** do pega-tudo, e não por fora dele | Adicione o identificador **depois** do pega-tudo |
| O cliente vê o detalhe do erro interno | O pega-tudo devolveu `str(erro)` | Devolva só a mensagem genérica, e registre o detalhe no log |
| Um identificador vindo de fora vai direto para o log | Faltou validar o formato | Aceite só valores que casem com um padrão seguro |
| O erro do pega-tudo some | `except Exception: pass` sem registrar | Sempre registre com `logger.exception` |

## // Prática guiada

1. Copie `example/veterano/api` para uma pasta nova, instale as dependências e rode `fastapi dev main.py`.
2. Rode `curl -i "http://127.0.0.1:8000/grupos?limit=2"` e leia o `x-request-id` e o `x-process-time`.
3. Repita com `-H "X-Request-ID: meu-pedido-0001"` e depois com `-H "X-Request-ID: x"`. O que muda?
4. Rode `curl -i -H "Origin: http://127.0.0.1:5500" http://127.0.0.1:8000/diagnostico/erro` e confira o `500` em JSON, com o cabeçalho de CORS. Olhe o log do terminal da API.
5. No `main.py`, **troque a ordem** das duas primeiras linhas de `add_middleware` (ponha o `CORSMiddleware` antes do `PegaTudo`) e repita o passo 4: o que mudou nos cabeçalhos? Depois restaure.
6. Sirva o front-end veterano (`example/veterano/frontend`), provoque um erro e leia o identificador na mensagem.

## // Pratique sozinho

> **DESAFIO**
> Escreva um terceiro middleware, `AvisoDeLentidao`, que registre no log uma linha de aviso (`logger.warning`) sempre que um pedido demorar mais de 200 ms. Para testar, crie uma rota que espere 300 ms com `time.sleep(0.3)`. Decida **onde** adicioná-lo na ordem, e justifique: ele precisa ver o tempo do pedido inteiro, incluindo os outros middlewares?

## // Aplicando no projeto da semana

1. Se você seguiu a trilha veterano, acrescente o `IdentificadorDoPedido` e o `PegaTudo` à sua API, na ordem do módulo.
2. Atualize o `expose_headers` e mostre o `requestId` nas mensagens de erro da página.
3. No `README.md`, descreva o que cada middleware faz e **por que** a ordem importa.
4. Se você versiona o projeto com Git, faça um commit: `git commit -m "Adiciona middlewares de requisição"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Você quer que o log registre também o tempo gasto pelo `PegaTudo`. O `IdentificadorDoPedido` deve ficar **dentro** ou **fora** do `PegaTudo`? E por que o `CORSMiddleware` deve ficar fora dos dois?

Resposta: o `IdentificadorDoPedido` deve ficar **fora** do `PegaTudo`, para ver o tempo e o status de tudo o que acontece dentro dele, incluindo o `500` que o pega-tudo cria. Na prática, ele é adicionado **depois** (a ordem das chamadas é a inversa da posição). O `CORSMiddleware` fica fora dos dois para que **toda** resposta, inclusive a `500` do pega-tudo, receba os cabeçalhos de autorização. A regra geral: o que precisa ver tudo vai por fora, e o que cuida de uma parte vai por dentro.

## // Resumo do módulo

- [ ] Sei o que é um middleware e como as camadas se organizam.
- [ ] Sei a regra da ordem: o último adicionado é o mais externo.
- [ ] Sei escrever um middleware ASGI e interceptar o envio da resposta.
- [ ] Sei dar um identificador a cada pedido, devolvê-lo em cabeçalho e registrá-lo no log.
- [ ] Sei por que o `500` sem tratamento aparece como erro de CORS, e como o pega-tudo, dentro do CORS, o evita.
- [ ] Sei por que o detalhe do erro vai para o log, e nunca para o cliente.
- [ ] Sei expor e liberar cabeçalhos próprios no CORS.

---

**Próximo módulo:** `16-padronizacao-do-json.md`, todo pedido já tem um identificador. Falta dar a toda resposta e a todo erro o mesmo formato.

`Material de Estudo // Coffee & Code`

# Module 17, Testing the Integration

[Português](../docs/17-testando-a-integracao.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

> **VETERAN TRACK, BONUS MODULE**
> This module is part of the veteran track and is a **bonus**: it is not required for the week's deliverable. Anyone following the main track can skip to `deliverable.md`.

In Module 14 you went through a 17-item script by hand. It works, but nobody repeats 17 items on every small change. This module swaps the script, for the most part, for **automated tests**: one set for the **API** (with `pytest`) and another for the **page** (with `jsdom`, which simulates the browser). It also shows, honestly, what they **cannot** check.

## // The problem: integration breaks at the edges

The listing works and nobody looks at it again. Months later, someone touches CORS, and deleting stops working only for whoever uses the page. Or someone changes a rule, and the last page disappears. Integration defects show up **between** the two ends, where no test of a single isolated end looks. This week's tests cover both sides and the conversation between them.

## // What is in example/testes

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

## // Part 1: API tests, with pytest

Install the tools, inside the API's virtual environment:

```
pip install pytest httpx2
```

`httpx2` is the request library FastAPI's `TestClient` uses. It avoids a deprecation warning that shows up with the `httpx` library. Run **each folder separately**, because the two APIs have files with the same names (`main.py`, `dados.py`):

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

### > The CORS suite

The `testes/api` folder has a suite that asks, with the `Origin` header, every question the browser would ask. Each line corresponds to something you saw in Module 09:

```python
@pytest.mark.parametrize("origem", [INTRUSA, "null", "https://127.0.0.1:5500"])
def test_origens_fora_da_lista_recebem_200_mas_sem_autorizacao(client, origem):
    resposta = client.get("/grupos", headers={"Origin": origem})
    assert resposta.status_code == 200   # o servidor responde normalmente...
    # ...e o navegador é quem bloqueia a leitura:
    assert "access-control-allow-origin" not in resposta.headers
```

| Test | What it guarantees |
|---|---|
| Listed origins get the authorization | The page can read the responses |
| Origins outside the list get `200`, but no authorization | CORS is not a server protection (and the browser blocks it) |
| The total number of groups is exposed to JavaScript | The `expose_headers` is configured |
| Preflight for `GET`, `POST`, `PATCH` and `DELETE` | Every method the page uses is allowed |
| Preflight for `PUT`, for a header outside the list and for an origin outside the list | They return `400`, with the expected message |
| The preflight may be cached for 600 seconds | The `max_age` is the expected one |
| The trailing slash causes a redirect | `GET /grupos/` returns `307` |

If someone removes the `PATCH` from `allow_methods`, the `PATCH` preflight test **fails immediately**, before anyone finds out through the screen.

### > The veteran API's tests

| File | Question it answers |
|---|---|
| `test_envelope.py` | Does the list come in `dados` and `meta`? Does the JSON use camelCase? Does Swagger document that? |
| `test_erros.py` | Does every error come out in `erro` and `meta`, with the right code? Are the `404` and `405` messages in Portuguese? |
| `test_middlewares.py` | Does every request get an identifier? Is an invalid identifier replaced? Does the `500` come out in JSON, **with** the CORS header, and without leaking the detail? |

## // Part 2: page tests, with jsdom

`jsdom` is a library that simulates the browser inside Node: it understands your page's HTML, runs your JavaScript and lets a test read and touch the result. It needs **Node** and `npm`. The `jsdom` version used here (30.1.2) declares that it requires Node **22.22.2 or newer** (in the 22 series), **24.15 or newer** (in the 24 series), or **26 onwards**: check with `node --version`. The tests were run on Node 22.22.2:

```
cd testes/frontend
npm install
```

The tests talk to the **real API**, so start the API in another terminal (`fastapi dev main.py`, in the `example/api` folder) before running them:

```
npm test
```

Each step loads the page, acts like a person (types, clicks, submits the form) and checks what showed up on screen. Real result:

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

For the veteran version, the same test runs without changing a line, pointing at the front-end's folder and starting the veteran API:

```
FRONTEND=../../veterano/frontend npm test
```

That way of setting the `FRONTEND` variable works in the macOS and Linux terminal. On Windows, the syntax changes (in PowerShell, `$env:FRONTEND="../../veterano/frontend"` on one line, and `npm test` on the next), and it was **not tested**.

### > Two tests that deserve attention

**The API off.** Run it with the API **stopped**:

```
npm run test:api-fora
```

```
  OK  com a API desligada, a página avisa em vez de quebrar
```

**Out-of-order responses.** This test delays a response **on purpose**, to simulate an unreliable network:

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

The page asks for the second page (slow) and, right after, filters by subject (fast). If the old response overwrote the new one, the screen would show the wrong groups. The test checks that it does **not** overwrite:

```
  OK  a resposta velha (lenta) foi descartada, e a tela mostra a mais nova
```

And, to find out whether the test is actually worth anything, the **reverse proof** was done: the line that discards the old response was removed from `app.js`, and the test **failed**, with `a resposta velha NÃO pode sobrescrever a nova`. A test that never fails protects nothing, and the only way to know is to break the code on purpose.

## // What the automated tests do NOT check

> **THE MODULE'S MOST IMPORTANT LIMITATION**
> The page test uses Node's `fetch` inside `jsdom`. Node **does not apply CORS**: it does not send the preflight, does not check the `Access-Control-Allow-Origin` and does not hide headers. Therefore, a **green** page test does not prove that the browser will accept the responses. The CORS part is covered by the **API** tests (which check the exact headers the browser asks for), and, at the other end, by items 15 to 17 of Module 14's script, which only a real browser can check.

| Check | API test | Page test (jsdom) | Browser |
|---|---|---|---|
| The API answers with the right CORS headers | Yes | No | Yes |
| The browser accepts and hands over the response | No | No | **Only here** |
| The page shows the right list, errors and pagination | No | **Yes** | Yes |
| JavaScript reads the `X-Total-Count` across origins | No | No | **Only here** |
| The visual aspect (colours, position) | No | No | **Only here** |

The three kinds of test complement each other: none of them replaces the others.

## // Good example × bad example

**Bad example**: a test that always passes:

```js
assert.ok(true);
```

**Good example**: a test you **know** fails when the code breaks:

```
1. Rode o teste: verde.
2. Quebre o código de propósito (remova a proteção).
3. Rode o teste: vermelho. Se ele continuar verde, o teste não serve.
4. Restaure o código.
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| `ModuleNotFoundError: No module named 'main'` | `pytest` was run in the wrong folder | Run it inside `testes/api` or `testes/veterano` |
| A clash between the two APIs when running `pytest` at the root | Both have `main.py` and `dados.py` | Run each folder separately |
| `npm install` or the test complains about the Node version | `jsdom` requires a newer Node | Update Node (see the required version above) |
| `TypeError: fetch failed` in the page test | The API is not running, or is on another port | Start the API on port 8000 before the test |
| The page test fails on the second run | The API keeps data in memory and the test touched it | Restart the API (save `main.py`) between runs |
| The page tests run against the wrong API | The veteran front-end needs the veteran API | Match them: API and front-end of the **same** version |
| The test passes, but the browser fails with CORS | `jsdom` does not apply CORS | Check CORS in the API tests and in items 15 to 17 of Module 14 |
| A test that never fails | It checks nothing for real | Do the reverse proof: break the code and watch the test fail |

## // Guided practice

1. Install `pytest` and `httpx2` and run the tests in the `testes/api` folder. Read the names: each one is a sentence.
2. Remove `"PATCH"` from `allow_methods` in the API's `main.py` and run them again. Which tests failed? Restore it.
3. Run the tests in the `testes/veterano` folder and read `test_middlewares.py`.
4. Start the API, run `npm install` and `npm test` in `testes/frontend`, and follow the 12 steps.
5. Do the reverse proof on the ordering test: comment out the line `if (numero !== ultimoPedido) return;` in `carregarGrupos` in `app.js` and run `npm run test:fora-de-ordem`. Restore it.

## // Practice on your own

> **CHALLENGE**
> Write a new step for the page test: **the Salvar button stays disabled while the submission is in flight**. Hint: use the `test-fora-de-ordem.mjs` trick to delay the `POST` response, submit the form and check `salvar.disabled === true` before the response arrives, and `false` afterwards. Do the reverse proof as well (remove the `travarFormulario`).

## // Applying it to this week's project

1. Copy the `testes/api` folder into your project and run it before every CORS change.
2. Keep in `README.md` the command for each test and **what they do not cover** (CORS in the browser).
3. If you track the project with Git, make a commit: `git commit -m "Adiciona testes de integração"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> The page test's 12 steps pass, and so do the API's 22 tests. Even so, in the browser, the listing fails with CORS. How is that possible, and what did the tests not see?

Answer: the page test uses Node's `fetch`, which **does not apply CORS**, so it receives the response even if the server does not authorize it. The API tests check the CORS headers for the origins **that were tested**: if the browser's real origin (for example, `localhost` instead of `127.0.0.1`) was not in the suite, or if the configuration changed afterwards, nothing fails. What was missing is the most valuable item: **seeing the page running in a browser**, in the Network tab, with the real origin. Automated testing reduces the risk, it does not eliminate it.

## // Module summary

- [ ] I know how to run the API tests with `pytest`, each folder separately, and read the names as sentences.
- [ ] I know what the CORS suite guarantees, and that it fails if someone breaks the configuration.
- [ ] I know how to run the page test with `jsdom`, against the real API.
- [ ] I know how to simulate a slow network by delaying a response.
- [ ] I know how to do the reverse proof: break the code to watch the test fail.
- [ ] I know what the automated tests do not check, and why the browser remains indispensable.

---

**Next step:** `deliverable.md`, the final review of everything Week 06 asks for.

`Study Material // Coffee & Code`

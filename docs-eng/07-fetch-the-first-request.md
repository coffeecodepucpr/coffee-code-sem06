# Module 07, fetch: the First Request

[Português](../docs/07-fetch-o-primeiro-pedido.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

With HTTP, headers, JavaScript, the DOM and asynchronous code introduced, the first request has arrived: `fetch`, the function the browser offers for talking to an API. In this module you make real requests, read the responses, and learn two traps that catch a lot of people: `fetch` does **not** reject on a `404`, and `.json()` does **not** work on a `204`.

## // The problem: a request has many possible endings

When the page asks for data, several endings are possible: the API responds with the data; responds with an error (`404`, `422`); responds with no body (`204`); or does not respond at all (server off). Each one calls for a different reaction on screen, and `fetch` handles these cases in ways that are surprising.

## // Where to run the first tests

We have not covered CORS yet (Module 09), so, for now, make the requests **from the API's own origin**. With the API running, open `http://127.0.0.1:8000/docs`, the developer tools (F12) and the **Console** tab. Since the Swagger page and the API are on the **same origin**, the browser applies no restrictions to the requests. (This path follows MDN's same-origin rule, and was **not run in a browser** while the material was produced.)

The examples below were run in Node against the real API, and the outputs are the real ones.

## // The first request

```js
const API = "http://127.0.0.1:8000";
const resposta = await fetch(`${API}/grupos?limit=2`);
console.log(resposta.status, resposta.ok,
            resposta.headers.get("content-type"),
            resposta.headers.get("x-total-count"));
const dados = await resposta.json();
console.log(dados.length, dados[0].nome_grupo);
```

```
200 true application/json 6
2 Cálculo passo a passo
```

`fetch` returns a Promise of a `Response` object. It carries:

| Property | What it is |
|---|---|
| `resposta.status` | The status code (`200`, `404`...) |
| `resposta.ok` | `true` for the codes from `200` to `299` |
| `resposta.headers.get("nome")` | One response header, or `null` |
| `await resposta.json()` | The body, read as JSON |
| `await resposta.text()` | The body, read as text |

Notice there are **two** `await`s: one for the response to arrive (the headers), another for the body to be read.

> **THE BODY CAN ONLY BE READ ONCE**
> Reading the body again, after having read it, is an error. In Node, the message is `TypeError: Body is unusable: Body has already been read` (browsers use different wording). If you need the same body twice, store the result of the first read in a variable.

## // fetch does not reject on an HTTP error

This is the most common trap. A request the API **answered with an error** does not make `fetch` fail:

```js
const r404 = await fetch(`${API}/grupos/99`);
console.log(r404.status, r404.ok, await r404.json());
```

```
404 false { detail: 'Grupo não encontrado' }
```

The Promise was **fulfilled**, with a response whose `ok` is `false`. Anyone who writes `try { ... } catch { ... }` and expects to land in the `catch` on a `404` will be misled: the page would show the list as if everything had gone right. **Always check** `resposta.ok`.

`fetch` only rejects when the API **did not answer at all**:

```js
try { await fetch("http://127.0.0.1:9/nada"); }
catch (e) { console.log(e.name, e.message); }
```

```
TypeError fetch failed
```

That is Node's message. In browsers, the network failure is also a `TypeError`, with varying wording (in Chrome, it is usually `Failed to fetch`). The possible reasons: the server is off, the address is wrong, or the browser **blocked** the response because of CORS (Module 09).

<div align="center">
<img src="../docs/assets/svg/fluxo-do-fetch.svg" alt="What happens after a fetch: rejection, response with an error, status 204 and reading the body" width="640">
</div>

## // Sending data

To create a group, `fetch` takes a second argument, with the method, the headers and the body:

```js
const criado = await fetch(`${API}/grupos`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ nome_grupo: "Teste do fetch", materia_id: 1 }),
});
console.log(criado.status, criado.headers.get("location"),
            (await criado.json()).grupo_id);
```

```
201 /grupos/7 7
```

Without the `Content-Type`, the API refuses the body, as Module 02 showed:

```
POST sem Content-Type -> 422 | detalhe: model_attributes_type
```

When the body is text, `fetch`'s default is the `text/plain` type, according to the specification, and the API only understands JSON if the header says it is JSON.

## // The 204 response has no body

`DELETE` returns `204 No Content`: it worked, and **there is no body**. Calling `.json()` on it fails:

```js
const apagado = await fetch(`${API}/grupos/7`, { method: "DELETE" });
console.log(apagado.status, apagado.ok, (await apagado.text()) === "");
```

```
204 true true
```

```js
// com outra resposta 204:
try { await apagado2.json(); } catch (e) { console.log(e.name + ":", e.message); }
```

```
SyntaxError: Unexpected end of JSON input
```

Hence the flow's rule: **if the status is 204, do not read the body**.

## // The request, in one function: pedir()

So you do not have to repeat all those precautions on every call, the page's code gathers them into one function, `pedir()`, in the `api.js` file. Read it slowly:

```js
export const API_URL = "http://127.0.0.1:8000";

export class ErroDeRede extends Error {
  constructor() {
    super("Não foi possível falar com a API. Ela está ligada?");
    this.name = "ErroDeRede";
  }
}

export class ErroHttp extends Error {
  constructor(status, corpo) {
    super(`A API respondeu ${status}`);
    this.name = "ErroHttp";
    this.status = status;
    this.corpo = corpo;
  }
}

async function pedir(caminho, { metodo = "GET", corpo } = {}) {
  const opcoes = { method: metodo, headers: {} };
  if (corpo !== undefined) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }

  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  } catch {
    throw new ErroDeRede();
  }

  const dados = resposta.status === 204
    ? null
    : await resposta.json().catch(() => null);

  if (!resposta.ok) throw new ErroHttp(resposta.status, dados);
  return { dados, resposta };
}
```

What the function guarantees:

| Precaution | How the function handles it |
|---|---|
| The JSON `Content-Type` | Set automatically whenever there is a body |
| Network failure | Becomes an `ErroDeRede`, with a clear message |
| HTTP error (`404`, `409`, `422`...) | Becomes an `ErroHttp`, with the status and the error body |
| `204` response | Does not try to read the body |
| A body that is not JSON | The `.catch(() => null)` keeps the function from breaking |

The two error classes are the heart of the page's error handling: whoever calls the API uses `instanceof` to decide what to show (Modules 10 to 12).

## // Good example × bad example

**Bad example**: relying on the `catch` for HTTP errors:

```js
try {
  const resposta = await fetch(`${API}/grupos/99`);
  const grupo = await resposta.json();      // 404: o corpo é {"detail": ...}
  mostrar(grupo.nome_grupo);                 // undefined, sem nenhum erro
} catch (erro) {
  mostrarMensagem("Erro!");                  // nunca chega aqui em um 404
}
```

**Good example**: checking `resposta.ok` before using the body:

```js
const resposta = await fetch(`${API}/grupos/99`);
if (!resposta.ok) {
  mostrarMensagem(`A API respondeu ${resposta.status}.`);
  return;
}
const grupo = await resposta.json();
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The screen shows `undefined` on a `404` | `fetch` did not reject, and the error body was treated as data | Check `resposta.ok` |
| `Unexpected end of JSON input` | `.json()` on a `204` response | Do not read the body when the status is `204` |
| `Body is unusable` | The body was read twice | Store the result of the first read |
| `422` when creating a group | `Content-Type: application/json` was missing | Add the header |
| `TypeError: Failed to fetch` with the API running | The browser blocked the response (CORS), or the address is wrong | Check the Network tab and Module 09 |
| Forgetting `JSON.stringify` on the body | The body has to be text | `body: JSON.stringify(objeto)` |

## // Guided practice

1. Start the API. Open `http://127.0.0.1:8000/docs`, the tools (F12) and the Console.
2. Paste the first request and check the status, the `content-type` and the `x-total-count`.
3. Ask for group `99` and confirm that `fetch` does **not** reject, but `ok` is `false`.
4. Create a group with `POST` and read the `location`. Then delete it and confirm the `204`.
5. Turn the API off, repeat the request and read the `TypeError`.
6. In `frontend/api.js`, copy the `pedir()` function and the two error classes.

## // Practice on your own

> **CHALLENGE**
> Write the function `buscarGrupo(id)` using `pedir()`. Test it with a group that exists, with `99` (and catch the `ErroHttp`, printing the `status`) and with the API off (and catch the `ErroDeRede`). For each case, write in a comment what the screen should show.

## // Applying it to this week's project

1. Create `projeto-fullstack/frontend/api.js` with the `API_URL`, the two error classes and the `pedir()` function.
2. Add the exported function `listarMaterias()`, which returns `(await pedir("/materias")).dados`.
3. If you track the project with Git, make a commit: `git commit -m "Cria a camada de acesso à API"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Someone on a forum says that "`fetch` errors out when the API responds `500`". Why is that wrong, and what does it mean for the screen?

Answer: `fetch` only **rejects** when there is no response at all (network, server off, browser block). A `500` is a response like any other: the Promise is fulfilled, and `resposta.ok` is `false`. If the page only handles the `catch`, the `500` goes unnoticed and the screen ends up with empty or broken data, with no explanation. The defence is to check `resposta.ok` (or to use a function like `pedir()`, which turns the HTTP error into an `ErroHttp`).

## // Module summary

- [ ] I can make a `GET` with `fetch` and read `status`, `ok`, headers and the body.
- [ ] I know that `fetch` only rejects when the API does not answer at all, and **not** on `404`, `409`, `422` or `500`.
- [ ] I know how to send JSON with `method`, `Content-Type` and `JSON.stringify`.
- [ ] I know that the body can only be read once, and that a `204` response has no body.
- [ ] I understand the `pedir()` function and the `ErroDeRede` and `ErroHttp` classes.

---

**Next module:** `08-serving-the-front-end-and-the-origin.md`, the requests work from inside the API. The next step deliberately creates the problem CORS will solve.

`Study Material // Coffee & Code`

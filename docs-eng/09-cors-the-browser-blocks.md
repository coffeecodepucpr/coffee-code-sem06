# Module 09, CORS: the Browser Blocks

[Português](../docs/09-cors-o-navegador-bloqueia.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

In Module 08 you served the page on port `5500` and saw that the API lives on port `8000`: two different **origins**. In Module 07, the `fetch` calling the API worked fine through `curl` and Swagger. Now that it runs inside the page, something changes. This module explains what changes, why, and how to solve it, and it is the most important one of the week: almost every integration between a page and an API goes through it.

## // The problem: the API responds, and the page does not receive it

With the page open at `http://127.0.0.1:5500`, this code in `app.js` asks the API for two groups:

```js
const API = "http://127.0.0.1:8000";

fetch(`${API}/grupos?limit=2`)
  .then((resposta) => resposta.json())
  .then((dados) => console.log(dados))
  .catch((erro) => console.error("Falhou:", erro));
```

In the browser's console, the list does not show up. Instead, an error appears. The typical text, in Chrome, is this one (the exact wording varies between browsers, and this message was **not reproduced** while the material was produced):

```
Access to fetch at 'http://127.0.0.1:8000/grupos?limit=2' from origin
'http://127.0.0.1:5500' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

The sentence is alarming, because it sounds like the API refused the request. But look at what the server **actually** answered, using `curl` with the same `Origin` header the browser sends:

```
curl -i -H "Origin: http://127.0.0.1:5500" "http://127.0.0.1:8000/grupos?limit=2"

HTTP/1.1 200 OK
content-type: application/json
x-total-count: 6

[{"nome_grupo":"Cálculo passo a passo","materia_id":1, ... },
 {"nome_grupo":"Estruturas na prática","materia_id":2, ... }]
```

The server answered **200 OK, with the complete data**. The request was not refused, and no line of Python failed. The response reached the browser, and **the browser threw it away**, before handing it to your JavaScript. It is a browser security behaviour, and that is what CORS governs.

## // What CORS is

> **ORIGIN: IN SIMPLE WORDS**
> It is the combination of **scheme** (`http`), **host** (`127.0.0.1`) and **port** (`5500`) of an address. The path does not count. Two URLs are same-origin only if all three parts are identical.

<div align="center">
<img src="../docs/assets/svg/origem.svg" alt="A URL split into scheme, host, port and path, and four examples of same origin or different origin" width="640">
</div>

> **CORS: IN SIMPLE WORDS**
> *Cross-Origin Resource Sharing* is a mechanism, based on HTTP headers, by which the **server** states which other origins the **browser** may let read its responses. By default, a browser does not hand a page a response from an origin other than its own.

That default exists for safety. Without it, any page open in your browser could make requests, as you, to other sites where you are signed in, and read the responses. Source: the MDN documentation on CORS, consulted on 2026-10-08.

Two ideas need to be clear from the start:

1. **The one applying the rule is the browser**, not the server. The server only declares, through headers, what it allows.
2. **CORS only exists in browsers.** `curl`, the Swagger served by the API itself, and another Python program do not apply this rule. That is why the same request "works" from outside and "fails" on the page.

## // How the server authorizes: the simplest case

<div align="center">
<img src="../docs/assets/svg/cors-requisicao-simples.svg" alt="Sequence of a GET between the page, the browser and the API, with the Access-Control-Allow-Origin header" width="640">
</div>

In a simple `GET`, the browser sends the request normally, but adds the `Origin` header with the page's origin. The API responds, and the browser looks in the response for the `Access-Control-Allow-Origin` header:

- If it carries **the page's origin** (or `*`), the browser hands the response to the JavaScript.
- If it is **missing**, or carries **another origin**, the browser discards the response and the `fetch` fails with an error.

Compare the API's real response **with CORS configured** (the `curl` is the same one from the beginning):

```
HTTP/1.1 200 OK
x-total-count: 6
access-control-expose-headers: X-Total-Count
access-control-allow-origin: http://127.0.0.1:5500
vary: Origin
```

The `access-control-allow-origin` header is the **authorization**: it repeats the page's origin. The `vary: Origin` tells caches that the response depends on the requester's origin. The `access-control-expose-headers` is Module 13's subject.

## // The preflight: when the browser asks first

Not every request follows the simple path. A request is **only simple** if it uses `GET`, `HEAD` or `POST` and sends only headers the specification considers safe (`Content-Type`, for example, may only have the values `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`). Source: MDN.

Almost every request from your page is **not** simple: sending JSON (`Content-Type: application/json`), using `PATCH` or `DELETE`. In those cases, before the real request, the browser makes a **check** request, called a **preflight**, with the `OPTIONS` method.

<div align="center">
<img src="../docs/assets/svg/cors-preflight.svg" alt="Sequence of a POST with JSON, with the OPTIONS preflight before the real POST" width="640">
</div>

The preflight is made **by the browser, on its own**: your JavaScript does not write it. But you can see it in the Network tab, and the server has to know how to answer it. Here is the preflight of a JSON `POST`, and the API's real response **with CORS**:

```
curl -i -X OPTIONS \
  -H "Origin: http://127.0.0.1:5500" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  http://127.0.0.1:8000/grupos

HTTP/1.1 200 OK
access-control-allow-origin: http://127.0.0.1:5500
access-control-allow-methods: GET, POST, PATCH, DELETE
access-control-allow-headers: Accept, Accept-Language, Content-Language,
                              Content-Type
access-control-max-age: 600
vary: Origin, Access-Control-Request-Method,
      Access-Control-Request-Headers,
      Access-Control-Request-Private-Network
content-type: text/plain; charset=utf-8

OK
```

Each `Access-Control-Request-*` header in the request is a **question** ("may I use `POST`? may I send `content-type`?"), and each `Access-Control-Allow-*` in the response is the **answer** to it. The `access-control-max-age: 600` tells the browser it can reuse that answer for up to 600 seconds, without repeating the preflight.

And the same question asked of the API **without CORS** (the one from the start of the module):

```
HTTP/1.1 405 Method Not Allowed
allow: GET
{"detail":"Method Not Allowed"}
```

The API does not know how to answer `OPTIONS`, returns `405`, and the browser concludes that `POST` is not allowed. No `POST` is ever sent.

## // Configuring CORS in FastAPI

FastAPI ships a ready-made piece for this, the `CORSMiddleware`. A *middleware* is a snippet of code that sits between the server and the routes, and that sees every request and every response (Module 15 explores this in depth). In the API's `main.py`, add:

```python
from fastapi.middleware.cors import CORSMiddleware

ORIGENS_PERMITIDAS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Total-Count"],
)
```

| Parameter | What it declares | Value here |
|---|---|---|
| `allow_origins` | The origins whose pages may **read** the responses | The two ways of opening the local page |
| `allow_methods` | The methods allowed in the preflight | The four the page uses |
| `allow_headers` | The request headers allowed | `Content-Type`, for sending JSON |
| `expose_headers` | The **response** headers JavaScript may read | `X-Total-Count` (Module 13) |
| `allow_credentials` | Whether cookies travel with the requests | Not used: left at the default, which is off |
| `max_age` | How long the browser keeps the preflight | Default: 600 seconds |

Save the file: `fastapi dev` reloads by itself. The configuration, in this version, is described in the official FastAPI documentation, consulted on 2026-10-08.

## // Testing CORS without a browser

You do not need the browser to check the configuration. `curl`, with the `Origin` header, shows exactly what the server answers. These are the real results, and they make up a small **test suite** you can repeat whenever you touch CORS:

| Test | Result | What it means |
|---|---|---|
| `GET` with `Origin: http://127.0.0.1:5500` | `200`, with `access-control-allow-origin` | The allowed page can read it |
| `GET` with `Origin: http://localhost:3000` | `200`, **without** `access-control-allow-origin` | Origin outside the list: the browser would block it |
| `GET` with `Origin: null` | `200`, **without** `access-control-allow-origin` | Page opened via `file://`: blocked |
| `POST` preflight | `200` | Allowed |
| `PUT` preflight | `400`, `Disallowed CORS method` | `PUT` is not in `allow_methods` |
| Preflight with `authorization` | `400`, `Disallowed CORS headers` | The header is not in `allow_headers` |
| Preflight from an origin outside the list | `400`, `Disallowed CORS origin` | Origin refused |

> **CORS DOES NOT PROTECT YOUR API**
> Look at the second row of the table: the origin `http://localhost:3000` is **not in the list**, and even so the server answered `200 OK` with the data. The server blocked nothing: it merely **left out** the authorization header, and it is the browser that bars the read. Anyone calling the API through `curl`, a script or an application ignores CORS completely. To really protect data, you need **authentication and permissions**, a subject outside this week. CORS decides only **which page, in a browser, may read the response**.

## // The most common traps

Each of these was reproduced in a real run.

| Trap | What happens | How to avoid it |
|---|---|---|
| **Only the origin was configured** | The `CORSMiddleware` default allows only `GET`. The `DELETE` or `PATCH` preflight returns `400 Disallowed CORS method` | Declare `allow_methods` with everything the page uses |
| **localhost and 127.0.0.1** | They are different origins. A page opened at `http://localhost:5500` is not served if only `127.0.0.1:5500` is in the list | List both, or always open the page through the same address |
| **The page opened via file://** | The browser sends `Origin: null`, which is not in the list | Serve the page through a server (`python3 -m http.server`), as in Module 08 |
| **`allow_origins=["*"]` "to fix it"** | Any site is now able to read the API's responses | List only the real origins |
| **`"*"` together with `allow_credentials=True`** | The documentation says the two cannot be combined, but Starlette **does not raise an error**: it starts **echoing the requester's origin**, with `access-control-allow-credentials: true` | Never combine them. With credentials, list the origins |
| **The API returns a 500** | The error response goes out **without** CORS headers, and the browser shows a CORS error instead of the real one | Learn to recognize the symptom (see the tree below). Module 15 shows a fix |
| **Trailing slash in the URL** | `GET /grupos/` returns `307 Temporary Redirect` to `http://127.0.0.1:8000/grupos`. The redirect adds a network round trip | Always call the exact address, with no trailing slash |
| **Changed CORS and nothing changed** | The browser may reuse the preflight for up to `access-control-max-age` (600 seconds) | Reload with the Network tab open and check the new preflight |

Two of those traps deserve proof that they are real. With CORS configured with only `allow_origins` (defaults for the rest), the `DELETE` preflight answers:

```
HTTP/1.1 400 Bad Request
Disallowed CORS method
access-control-allow-methods: GET
```

And with `allow_origins=["*"]` and `allow_credentials=True`, a request coming from `https://qualquer.com` receives:

```
access-control-allow-origin: https://qualquer.com
access-control-allow-credentials: true
```

The server **repeated the origin of some random site** and even authorized sending credentials. It is the most dangerous combination of all, and it gives no warning whatsoever.

## // Diagnosing a CORS error

When the page fails, do not guess. Follow the questions, **in this order**, looking at the browser's Network tab:

<div align="center">
<img src="../docs/assets/svg/cors-por-que-falhou.svg" alt="Decision tree with five questions for diagnosing a CORS error" width="640">
</div>

The first question is the one that saves the most time: if **no response** shows up in the Network tab, the problem is **not CORS**. The API is down, or the address is wrong, and the browser shows a similar-looking error.

## // Good example × bad example

**Bad example**: allowing everything to make the error go away:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
    allow_credentials=True,
)
```

The error goes away, but any site in the world is now able to read the API's responses, and combining it with `allow_credentials=True` makes the server echo any origin.

**Good example**: an exact list of what the page actually uses:

```python
ORIGENS_PERMITIDAS = ["http://127.0.0.1:5500", "http://localhost:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Total-Count"],
)
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The list does not show up, and the console mentions CORS | The response came without `access-control-allow-origin` | Configure the `CORSMiddleware` and check the origin |
| The `GET` works, but the `POST` and the `DELETE` fail | `allow_methods` was missing, or the preflight returned `400` | Include the methods used and test the preflight with `curl` |
| It works on `127.0.0.1` and fails on `localhost` | They are different origins | Add both to `allow_origins` |
| The server returns `200`, but the page errors out | The browser discarded the response (CORS) | Compare it with `curl -H "Origin: ..."` |
| `405` when testing the preflight | The `CORSMiddleware` was not added to the `app` | Add the `add_middleware` and restart |
| A CORS error that disappears when the API does not break | The API returned a `500`, which goes out without CORS headers | Check the API's log: the real error is there |

## // Guided practice

1. Open two terminals. In the first, inside the `api-inicial` folder, activate the environment and run `fastapi dev main.py`. In the second, inside the `frontend-inicial` folder, run `python3 -m http.server 5500 --bind 127.0.0.1`.
2. Open `http://127.0.0.1:5500` in the browser, with the developer tools open (the **F12** key), on the **Console** tab.
3. Write this module's opening code in `app.js`, save and reload the page. Watch the error, then open the **Network** tab and find the request: read the status and the response headers.
4. Run the `curl` with `Origin` (the command from the start of the module) and confirm that the server answered `200` without the authorization header.
5. In `main.py`, add the `CORSMiddleware` with the "good example" configuration. Save (the API reloads by itself) and reload the page: the list of two groups shows up in the console.
6. Run the `POST` preflight with `curl` and compare it with the module's response.
7. Open the page at `http://localhost:5500` and see what changes. Then add the missing origin, save, and check again.

## // Practice on your own

> **CHALLENGE**
> Write, with `curl`, the preflight of a `PATCH` on `/grupos/1` coming from the origin `http://127.0.0.1:5500`, and then that of a `PUT`. Before running them, predict the status and the body of each. Then change `allow_methods` to remove the `PATCH`, and confirm the difference. Finally, add the origin `http://127.0.0.1:5501` and prove, with a `GET` and `Origin`, that it became authorized.

## // Applying it to this week's project

1. Leave the `CORSMiddleware` configured in your API's `main.py`, with the `ORIGENS_PERMITIDAS` list in a constant at the top of the file.
2. In the project's `README.md`, create a "CORS" section with the list of allowed origins and the reason for each one.
3. Save the preflight `curl` in a file named `testes-cors.md`: it will be your CORS test suite.
4. If you track the project with Git, make a commit: `git commit -m "Configura o CORS da API"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Someone reads on a forum that, to solve the CORS error, all you need is `allow_origins=["*"]`. The error really does go away. What is right about that tip, and what is risky?

Answer: it is right that the error goes away, because the server starts sending `access-control-allow-origin: *` and the browser allows the read for **any** page. The risk is exactly that: **any site** is now able to read the API's responses from the browser of whoever visits it. For a public API, with no sensitive data, that may be acceptable. For an API with people's data, or one that will one day use cookies, it is not. It gets much worse if combined with `allow_credentials=True`, because Starlette, in that case, starts echoing any origin. The safe practice is to list only your page's real origins.

## // Module summary

- [ ] I can explain what an origin is (scheme, host and port) and why `localhost` and `127.0.0.1` are different.
- [ ] I can explain what CORS is and that **the browser is the one applying it**.
- [ ] I know why `curl` and Swagger work and the page fails.
- [ ] I know the difference between a simple request and one that requires a **preflight**, and what the `OPTIONS` asks.
- [ ] I know how to configure the `CORSMiddleware` with origins, methods, headers and exposed headers.
- [ ] I know how to test CORS with `curl` and the `Origin` header.
- [ ] I know that CORS does **not** protect the API, and that `"*"` with credentials is dangerous.
- [ ] I know how to follow the diagnosis tree, starting with "does the Network tab show a response?".

---

**Next module:** `10-listing-groups-on-the-page.md`, CORS is solved. Time to turn the API's response into a real list on the page.

`Study Material // Coffee & Code`

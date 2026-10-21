# Runnable examples, Week 06

[Português](../../docs/example/README.md) · English

This folder gathers everything that can be run this week. It is a reference, not a mandatory answer key: your application needs to apply the same concepts, not to be identical to this one.

> **Where the code lives:** the runnable files are in [`docs/example/`](../../docs/example/). Their names, messages and comments are in Portuguese, and this page explains them in English.

## The environment everything was tested in

| Item | Version |
|---|---|
| Python | 3.12.3 (FastAPI requires 3.10 or newer) |
| FastAPI | 0.143.0 |
| Starlette | 1.7.0 |
| Pydantic | 2.13.5 |
| Uvicorn | 0.54.0 |
| pytest | 9.1.1 |
| httpx2 | 2.13.1 |
| Node (only for the page tests) | 22.22.2 |
| jsdom (only for the page tests) | 30.1.2 |
| System | Linux. **Not tested on Windows or macOS** |
| Browser | **None.** CORS was tested from the server side, and the JavaScript in a simulator (`jsdom`) |

The official FastAPI documentation and the MDN documentation were consulted on **2026-10-08**. FastAPI is a `0.x` library and changes often: if anything differs from what is here, the official documentation is the reference.

## Which folder to use

| Folder | Modules | What it is |
|---|---|---|
| `api-inicial/` | 03, 08 | The API **without CORS**: the starting point, and the one that shows the problem |
| `api/` | 09 to 14 | The same API, **with CORS configured**: the result of Module 09 |
| `frontend-inicial/` | 05, 08, 09 | The ready-made HTML and CSS, with an empty `app.js` |
| `frontend/` | 07, 10 to 14 | The complete page: `api.js`, `ui.js` and `app.js` |
| `veterano/api/` | 15, 16 | The API with middlewares, the `{ dados, meta }` envelope, a single error format and camelCase |
| `veterano/frontend/` | 16 | The page adapted to the veteran API's format |
| `testes/` | 17 | The API (`pytest`) and page (`jsdom`) tests |

## How to run the main track

In one terminal, inside `api/` (or `api-inicial/`):

```
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

In **another** terminal, inside `frontend/`:

```
python3 -m http.server 5500 --bind 127.0.0.1
```

Open `http://127.0.0.1:5500`. The API's documentation opens at `http://127.0.0.1:8000/docs`. Always use `fastapi dev`, not `fastapi run`: `dev` serves only your computer, and `run` serves the whole network. And always use `--bind 127.0.0.1` on the page's server.

## How to run the veteran track

The same commands, with the API from `veterano/api/` and the page from `veterano/frontend/`. Both have to be of the **same version**: the veteran page expects the response envelope, and the main page expects the raw list.

## How to run the tests

**API** (inside the API's virtual environment, with `pip install -r testes/requirements-testes.txt`). Run **each folder separately**:

```
cd testes/api
pytest -q            # 22 testes

cd ../veterano
pytest -q            # 18 testes
```

**Page** (needs Node, see the version above, and the API running in another terminal):

```
cd testes/frontend
npm install
npm test                       # 12 passos
npm run test:fora-de-ordem     # respostas atrasadas
npm run test:api-fora          # com a API DESLIGADA
```

For the veteran page, set `FRONTEND=../../veterano/frontend` before the command (the syntax on Windows is different and was not tested). The page tests touch the API's in-memory data: restart the API (by saving `main.py`) between two runs.

## What the tests do not cover

The page test uses Node's `fetch` inside `jsdom`, and **Node does not apply CORS**. Therefore, the final CORS check has to be done in a **real browser**, with Module 14's script. The API tests check the headers the browser would ask for.

## Safety rules

- Always run the API with `fastapi dev`, and the page's server always with `--bind 127.0.0.1`. Nothing here has access control.
- The `GET /diagnostico/erro` route, in the veteran API, exists only for studying the `500`: in a real system, remove it.
- The virtual environment (`.venv`) and the `node_modules` folder never go into the repository.
- The data lives in memory and goes back to its initial state on every API restart.

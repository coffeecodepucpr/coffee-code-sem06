# Deliverable, Week 06

[Português](../docs/entregavel.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

Use this file as the final checklist before considering Week 06 finished. It gathers what is **mandatory**; the extra challenges in `challenges.md` and Modules 15 to 17 of the veteran track are optional.

## // What you should have in hand now

If you followed the modules in order, your `projeto-fullstack` folder should contain an `api` subfolder (with `main.py`, `dados.py`, `schemas.py` and `requirements.txt`), a `frontend` subfolder (with `index.html`, `estilos.css`, `api.js`, `ui.js` and `app.js`) and a `README.md` at the root. Both ends should run at the same time, and the page, opened at `http://127.0.0.1:5500`, should list, create, edit and delete groups through the API.

## // The deliverable's checklist

### > Environment and running

- [ ] The API has a virtual environment, and the `.venv` is not in the repository (if you use Git).
- [ ] The `requirements.txt` pins the FastAPI version range (`fastapi[standard]>=0.143,<0.144`).
- [ ] The API starts with `fastapi dev main.py`, and the page is served with `python3 -m http.server 5500 --bind 127.0.0.1`.
- [ ] The `README.md` explains how to run **both** ends, in two terminals, and what the two origins are.

### > CORS

- [ ] The `CORSMiddleware` is configured with an **exact list** of origins (`http://127.0.0.1:5500` and `http://localhost:5500`), and not with `"*"`.
- [ ] `allow_methods` lists only the methods the page uses (`GET`, `POST`, `PATCH` and `DELETE`).
- [ ] `allow_headers` allows the `Content-Type`, and `expose_headers` exposes the `X-Total-Count`.
- [ ] You tested the preflight of `POST`, `PATCH` and `DELETE` with `curl` and the `Origin` header, and saved the commands.

### > The page and the integration

- [ ] The page lists the API's groups, showing the subject's name (and not just the number).
- [ ] The search by name and the filter by subject work, and go back to page 1.
- [ ] The form **creates** groups, and the page **edits** and **deletes** (with confirmation) using `PATCH` and `DELETE`.
- [ ] Every API call goes through `api.js`, and the API's address appears in **one** place only.
- [ ] Data coming from the API goes onto the page with `textContent`, **never** with `innerHTML`.

### > Screen states and errors

- [ ] The list shows all four states: loading, success, empty ("Nenhum grupo encontrado.") and error.
- [ ] A validation error (`422`) shows up **on the right field**, and a repeated name (`409`) has a clear message.
- [ ] With the API off, the page warns ("API fora do ar") instead of breaking.
- [ ] The **Salvar** button stays disabled during the submission and goes back to normal, even on error.
- [ ] The `fetch` call checks `resposta.ok` (or uses a function that does), and does not rely on the `catch` alone.

### > Pagination

- [ ] The page uses `limit` and `offset`, and shows "Página N de M (T grupos)", with the right agreement.
- [ ] The **Anterior** and **Próxima** buttons are disabled at the ends.
- [ ] The total comes from the `X-Total-Count`, and the page handles the case of it arriving `null`.
- [ ] Deleting the last item of the last page leads to the last page that exists, and not to an empty one.

### > Documentation

- [ ] The `README.md` describes how to run it, the origins, the list of routes the page uses and what each file does.
- [ ] The `README.md` records the steps of Module 14's verification script that you went through, with the result of each one.

### > Veteran track (optional)

- [ ] The `IdentificadorDoPedido` and the `PegaTudo` are in the right order (the `PegaTudo` inside CORS), and the `500` reaches the page in JSON, with the CORS header.
- [ ] The API returns the `{ dados, meta }` envelope and the `{ erro, meta }` error, with the names in camelCase.
- [ ] The page decides errors by the `erro.codigo`, and shows the `requestId` in the error messages.
- [ ] (Bonus) The API's tests pass with `pytest -q`, and the page's with `npm test`.

## // What is NOT expected this week

- No database is expected: the data lives in memory and goes back to its initial state when the API restarts.
- No login, cookies, tokens or any access control is expected.
- Publishing the application to the internet is not expected. Always use `fastapi dev` and the server with `--bind 127.0.0.1`.
- Front-end frameworks (React, Vue and others) are not expected: the page is plain HTML, CSS and JavaScript.
- A sophisticated look is not expected: the material's ready-made CSS will do.

> **CORRECT INTEGRATION IS WORTH MORE THAN THE LOOKS**
> A simple page that shows every state (loading, empty, error, API down), refuses invalid data on the right field and never writes outside data with `innerHTML` is worth more in this assessment than a beautiful screen that breaks when the API answers with an error. What is being assessed this week is the **conversation between the two ends**.

## // How to review before handing it in

> **THE MOST IMPORTANT TEST OF THE WEEK**
> In a new, empty folder, copy only the project's files (without the `.venv`), create the API's virtual environment, install the dependencies and start **both** ends, each in its own terminal. Then go through the 17 items of Module 14's script, watching the Network tab and the Console. If everything matches, your delivery works on any computer, and not only on yours.

If any item fails, **always** start with the Network tab and follow Module 09's diagnosis tree: the first question ("does the tab show a response from the API?") cuts the problem in half.

## // Where to ask questions

The Coffee & Code weekly meetings exist for this. "My list does not show up, the console talks about CORS, and in the Network tab the `GET /grupos` request has status 200 and no `access-control-allow-origin` header" is far quicker to solve than "my page does not work". Always include the request's method and address, the status code, the response headers and the Console's message.

If you want to go deeper than what was asked, see `challenges.md` and the veteran track, in Modules 15 to 17.

Good work so far.

`Study Material // Coffee & Code`

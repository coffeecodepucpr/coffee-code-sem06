# Module 14, Guided Project

[Português](../docs/14-projeto-guiado.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

Every piece has been introduced: the API, the page's server, CORS, the listing, the form, editing, deleting and pagination. This module puts them together into **one full-stack application** and gives a verification script to check, point by point, that everything is connected. The result is the week's deliverable.

## // The final design

<div align="center">
<img src="../docs/assets/svg/estrutura-fullstack.svg" alt="The project's structure: the front-end folder, the API folder and how the files connect" width="640">
</div>

The project's structure:

```
projeto-fullstack/
├── README.md
├── api/
│   ├── main.py
│   ├── dados.py
│   ├── schemas.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── estilos.css
    ├── api.js
    ├── ui.js
    └── app.js
```

Each file has **one** responsibility:

| File | Responsibility |
|---|---|
| `api/main.py` | The routes, the rules and the CORS configuration |
| `api/dados.py` | The sample data, in memory |
| `api/schemas.py` | The shape of the data (the models) |
| `frontend/index.html` | The page's structure |
| `frontend/estilos.css` | The look |
| `frontend/api.js` | The only place that knows the API's address and `fetch` |
| `frontend/ui.js` | The only place that reads from and writes to the page |
| `frontend/app.js` | The orchestration: events, state and the screen states |

The rule behind the split: **each file changes for a single reason**. If the API's address changes, only `api.js` changes. If the look of the cards changes, only `ui.js` and the CSS do.

## // Putting it together, step by step

1. **Structure.** Create the tree above. The `api` folder comes from `example/api` (the version **with CORS**), and `frontend` from `example/frontend`, or from your own versions of the files written in the earlier modules.
2. **The API.** In the first terminal, inside `api`, activate the virtual environment and run `fastapi dev main.py`. Confirm that `http://127.0.0.1:8000/docs` opens.
3. **The front-end.** In the second terminal, inside `frontend`, run `python3 -m http.server 5500 --bind 127.0.0.1`.
4. **The page.** Open `http://127.0.0.1:5500`, with the developer tools (F12) open on the Network tab and the Console tab.
5. **The data.** Remember: the API keeps everything in memory. If it restarts (`fastapi dev` restarts on every saved file), the data goes back to the beginning.

## // The verification script

Go through each item, in order, and tick it off. Items 1 to 14 were verified in automated tests against the real API, and the description of what shows up in the browser tabs follows the documentation and was **not reproduced in a browser**.

| # | What to do | What should happen |
|---|---|---|
| 1 | Open the page | The indicator shows "API conectada" |
| 2 | Look at the list | Four groups, in alphabetical order: `Cálculo passo a passo`, `Estruturas na prática`, `Modelagem e SQL`, `Processos e memória` |
| 3 | Look at the pagination | `Página 1 de 2 (6 grupos)`, with **Anterior** disabled |
| 4 | Click **Próxima** | `Redes na unha` and `Requisitos e histórias`, and **Próxima** disabled |
| 5 | Search for `prática` | Only `Estruturas na prática`, and `Página 1 de 1 (1 grupo)` |
| 6 | Search for `zzz` | "Nenhum grupo encontrado." |
| 7 | Pick the subject `Banco de Dados` | Only `Modelagem e SQL` |
| 8 | Create `Cálculo II na prática`, subject Cálculo I, limit 5 | "Grupo criado.", form cleared, `Página 1 de 2 (7 grupos)` |
| 9 | Submit the name `ab` | The error `String should have at least 3 characters` on the name field |
| 10 | Create the same group again | The conflict error on the name field |
| 11 | Edit the created group, changing the limit to 8 | "Grupo atualizado.", the card shows "Até 8 participantes" |
| 12 | Delete the group, cancelling and then confirming | Cancelling does not delete; confirming deletes and goes back to `6 grupos` |
| 13 | Create three extra groups, go to page 3 and delete its only item | It goes back to page 2, without showing "Página 3 de 2" |
| 14 | Stop the API (Ctrl+C) and search for something | The indicator changes to "API fora do ar" and the message explains what happened |

Three more checks, only possible in a browser:

| # | Where to look | What should show up |
|---|---|---|
| 15 | Network tab, when creating a group | An `OPTIONS` (preflight) with `200`, and then the `POST` with `201` |
| 16 | Network tab, in the listing's headers | `access-control-allow-origin` with `http://127.0.0.1:5500`, and `access-control-expose-headers` with `X-Total-Count` |
| 17 | Console tab | No red errors during the whole script (the warning in step 14 is expected) |

## // If something does not work

Follow Module 09's tree and always look at the Network tab before touching the code. The most common problems in this assembly:

| Symptom | Likely cause | Where to check |
|---|---|---|
| The list does not show up, and the console mentions CORS | The page's origin is not in `ORIGENS_PERMITIDAS` | `main.py` and the address in the bar |
| "API fora do ar" with the API running | The address in `API_URL` is wrong, or the API uses another port | `api.js` and the API's terminal |
| The pagination shows "0 grupos" | The `expose_headers` was missing | `main.py` (Module 13) |
| `PATCH` and `DELETE` fail, `GET` and `POST` work | Methods are missing from `allow_methods` | `main.py` (Module 09) |
| The groups I created are gone | The API restarted: the data lives in memory | That is expected |
| Nothing changes when saving a `.js` file | The browser cached the file | Reload without cache (usually Ctrl+Shift+R) |

## // Automatic verification (optional)

Items 1 to 14 were verified by an automated test, which loads the page in an environment that simulates the browser (`jsdom`) and talks to the real API. It **does not apply CORS** (the real browser is the one that applies it), so it does not replace items 15 to 17. Module 17 shows how to run it.

## // Good example × bad example

**Bad example**: handing it in without going through the script:

```
"Funcionou quando eu testei a listagem. Deve estar tudo certo."
```

The cases that break applications are the edge ones: the empty list, the repeated name, the API being down, the last page.

**Good example**: going through all 17 items, writing down each result:

```
1 ok | 2 ok | 3 ok | ... | 13 ok (corrigi: voltava para a página 3) | 14 ok
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The API runs, but the page cannot find it | The two ends are not up at the same time | Check both terminals are open |
| The `README.md` does not explain how to run it | The documentation was left for later | Write both commands and the two origins |
| The page's files were served from the wrong folder | The terminal was outside `frontend` | Run the server inside `frontend` |
| A `.venv` was sent to the repository | The `.gitignore` was missing | Add `.venv/` to the `.gitignore` |
| The API's address ended up scattered through the code | `fetch` was called in several files | Keep it all in `api.js` |

## // Guided practice

1. Put the project's structure together and bring both ends up.
2. Go through the script's 17 items, in order, writing down each result.
3. For every item that fails, use Module 09's tree and the Network tab to find the cause, and fix it.
4. Write the project's `README.md` (see `entregavel.md`).

## // Practice on your own

> **CHALLENGE**
> Pick one item from the script and **break it on purpose**: for example, remove the `expose_headers`, or remove the `PATCH` from `allow_methods`. Run the script, write down the symptoms on screen, in the Console and in the Network tab, and write, in three lines, how you would recognize that defect if it showed up without warning. Then restore it.

## // Applying it to this week's project

1. The complete project, with the API and the front-end, is the deliverable: see `entregavel.md`.
2. Review the `README.md`: how to run both ends, what the origins are and what each file does.
3. If you track the project with Git, make the final commit: `git commit -m "Conclui a aplicação full-stack"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> The script has 17 items, and an automated test covers 14 of them. Why does it not cover the last three, and why does that matter?

Answer: because the automated test runs in an environment that **simulates** the browser, and that environment, using Node's `fetch`, **does not apply CORS**. Items 15 to 17 (preflight, CORS headers, no errors in the console) only exist in a real browser. That matters because CORS is precisely the part of the integration that fails most often: a green test does not prove that the browser will accept the responses. Checking manually in the browser remains indispensable.

## // Module summary

- [ ] I put the project together with both folders and both ends running.
- [ ] I know each file's responsibility and why each one changes for a single reason.
- [ ] I went through the script's 17 items and fixed whatever failed.
- [ ] I know how to use the Network tab and Module 09's tree to diagnose a symptom.
- [ ] I know what an automated test confirms and what it cannot confirm.

---

**Next module:** `deliverable.md` to review what the week asks for, or `15-request-middlewares.md` for the veteran track.

`Study Material // Coffee & Code`

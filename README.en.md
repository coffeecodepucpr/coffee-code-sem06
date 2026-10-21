# Coffee & Code | WEEK 06 | Central RESTful API (Part 2: Integration)

[Português](README.md) · English

```text
> module: sem-06
> topic: central restful api (integration)
> status: online
> coffee loaded
```

Material for **Week 06** of the Coffee & Code track, a technology club founded by Software Engineering students at PUCPR and open to anyone who wants to learn by building.

This week takes someone who has never connected a page to an API to a **connected full-stack application**, with listing, search, creation, editing, deletion and pagination: HTTP, headers, CORS and integration.

> **A standalone week:** it does not require any other week of the club. The API comes ready, and HTTP, JavaScript and CORS are introduced from scratch.

> **About the language:** the English material lives in [`docs-eng/`](docs-eng/), with the same structure as [`docs/`](docs/) (Portuguese); the READMEs have an English version with the `.en.md` suffix. The diagrams and the runnable examples' code (names, messages and comments) stay in Portuguese.

## Where to start

**[docs-eng/00-start-here.md](docs-eng/00-start-here.md)**: read this one first. It gives the week's overview and the idea of full-stack integration.

Then follow the modules in order. Modules `01` to `14` make up the main track:

| # | Module | About |
|---|---|---|
| 01 | [HTTP from the browser](docs-eng/01-http-from-the-browser.md) | Request, response, methods, status and the Network tab |
| 02 | [Headers](docs-eng/02-headers.md) | The request and response headers, and which ones JavaScript reads |
| 03 | [The API we will use](docs-eng/03-the-api-we-will-use.md) | Running and testing the week's API |
| 04 | [Essential JavaScript for integration](docs-eng/04-essential-javascript-for-integration.md) | Values, objects, arrays, functions, JSON and modules |
| 05 | [The DOM: reading and changing the page](docs-eng/05-the-dom-reading-and-changing-the-page.md) | The DOM, events and the safety of `textContent` |
| 06 | [Async: promises and async/await](docs-eng/06-async-promises-and-async-await.md) | Promises, `async` and `await` |
| 07 | [fetch: the first request](docs-eng/07-fetch-the-first-request.md) | `fetch`, network error and HTTP error |
| 08 | [Serving the front-end and the origin](docs-eng/08-serving-the-front-end-and-the-origin.md) | Serving the page, origin and the same-origin policy |
| 09 | [CORS: the browser blocks](docs-eng/09-cors-the-browser-blocks.md) | CORS, preflight, configuration and diagnosis |
| 10 | [Listing groups on the page](docs-eng/10-listing-groups-on-the-page.md) | The list, the screen states, the search and the filter |
| 11 | [Sending data: form and POST](docs-eng/11-sending-data-form-and-post.md) | The form, the `POST` and the per-field errors |
| 12 | [Editing and deleting: PATCH and DELETE](docs-eng/12-editing-and-deleting-patch-and-delete.md) | `PATCH`, `DELETE` and the response with no body |
| 13 | [Pagination and exposed headers](docs-eng/13-pagination-and-exposed-headers.md) | Pagination and the exposed `X-Total-Count` |
| 14 | [Guided project](docs-eng/14-guided-project.md) | The complete application and the verification script |

Modules `15` and `16` are the **veteran track**, and module `17` is a bonus on that track. All of them are optional and can be read after the essentials:

| # | Module | About |
|---|---|---|
| 15 | [Request middlewares](docs-eng/15-request-middlewares.md) | Identifier, timing, log and catch-all |
| 16 | [JSON standardization](docs-eng/16-json-standardization.md) | Envelope, single error format and camelCase |
| 17 | [Testing the integration](docs-eng/17-testing-the-integration.md) | Bonus: `pytest` and `jsdom` |

And, to consult whenever you need:

- [Runnable examples](docs-eng/example/README.md): the versions of the API and of the page, for reference
- [Challenges](docs-eng/challenges.md): optional, to go beyond what is asked
- [Deliverable](docs-eng/deliverable.md): the final checklist before closing the week

## The runnable examples

The [`docs/example/`](docs/example/) folder has both ends of the Study Group Finder (*Buscador de Grupos de Estudo*), in versions that follow the track:

- `api-inicial/` and `frontend-inicial/`: the starting point, before CORS and the integration.
- `api/` and `frontend/`: the main track's final version, with CORS configured.
- `veterano/`: the version with request middlewares and standardized JSON.
- `testes/`: the API tests (`pytest`) and the page tests (`jsdom`).

Everything was run, and the responses quoted in the modules come from those runs. See the [folder's README](docs-eng/example/README.md) to install and run it.

It is material for **reference, not an answer key**: the example is there for you to see one possible solution when you get stuck, not to copy.

## The deliverable

By the end of Week 06, **your project's** repository (not this one) should have a `projeto-fullstack` folder with both ends:

```text
projeto-fullstack/
├── api/
│   ├── main.py
│   ├── dados.py
│   ├── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── estilos.css
│   ├── api.js
│   ├── ui.js
│   └── app.js
└── README.md         ← how to run both ends
```

Both have to run at the same time, in two terminals, and the page, opened at `http://127.0.0.1:5500`, should list, create, edit and delete groups through the API, with CORS configured by an exact list of origins.

The complete checklist is in [docs-eng/deliverable.md](docs-eng/deliverable.md).

## The class's deliveries

There are no Week 06 deliveries yet. Want to be the first? See [how to deliver](entregas/README.en.md).

## Versions and date consulted

Material verified with **FastAPI 0.143.0**, Pydantic 2.13.5, Starlette 1.7.0, Uvicorn 0.54.0 and Python 3.12.3. The official FastAPI documentation and the MDN documentation (on CORS) were consulted on **2026-10-08**. FastAPI is a `0.x` library and changes often: if anything differs from what is here, the official documentation is the reference.

**What was and what was not tested in a browser.** The server was tested with real requests (including the CORS preflight), and the page's JavaScript was tested with `jsdom`, a browser simulator, against the real API. The **browser's own behaviour** (the CORS block, the Network tab, the headers hidden across origins) follows the MDN documentation and was **not reproduced in a browser** while the material was produced. The browser error messages quoted are the "typical text" and vary between browsers.

## A continuing project

Every module uses the club's same fictional project: the **Study Group Finder** (*Buscador de Grupos de Estudo*), an application where students look for study groups by subject. This week connects the page to the API that handles the groups and the subjects. If you have a project of your own, each module's reasoning applies just the same: only the name changes.

## How it works

Coffee & Code is **100% online**. Each module was written to stand on its own: you study at your own pace, can move faster, go back to earlier weeks and consult the material while working on your project.

The weekly meetings, also online, exist to answer questions, review concepts, code together and show what you have produced, **not to give lectures**:

- **Wednesday**: 8:00 pm to 9:30 pm
- **Saturday**: 10:00 am to 11:30 am

Both cover the same content. Pick whichever fits your week better, and you do not have to stay on the call the whole time.

## Stuck?

Come to the meeting or to Discord with a specific question. `"the console mentions CORS, and in the Network tab the GET /grupos comes back 200 without the access-control-allow-origin header"` tends to be solved far faster than `"my page does not work"`.

This week, the Network tab is your first stop: the method, the address, the status and the response headers cut almost any problem in half.

And remember: not knowing something is not a problem. Knowing how to look things up is part of the job.

## Diagrams

All the diagrams used in the modules are in [`docs/assets/svg/`](docs/assets/svg/), in SVG format.

## Earlier weeks

- [WEEK 01: Kickoff & Design System](https://github.com/coffeecodepucpr/coffee-code-sem01)
- [WEEK 02: Web Interface (Part 1: Layout)](https://github.com/coffeecodepucpr/coffee-code-sem02)
- [WEEK 03: Web Interface (Part 2: Dynamics)](https://github.com/coffeecodepucpr/coffee-code-sem03)
- [WEEK 04: Data Modelling](https://github.com/coffeecodepucpr/coffee-code-sem04)
- [WEEK 05: Central RESTful API (Part 1: CRUD)](https://github.com/coffeecodepucpr/coffee-code-sem05)

The full track and the coming weeks: [Coffee & Code's profile](https://github.com/coffeecodepucpr)

---

```text
HTTP 418: I'm a teapot
> ready to code
```

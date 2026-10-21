# Module 01, HTTP From the Browser

[Português](../docs/01-http-visto-do-navegador.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

In Module 00 you saw that a full-stack application has two ends that talk to each other. This conversation has a name, **HTTP**, and a place where you can peek at it: the browser's **Network** tab. This module introduces both, because anyone who integrates systems spends more time reading requests and responses than writing code.

## // The problem: the browser speaks, and you do not listen

A single web page usually makes dozens of requests: the HTML, the CSS, the JavaScript, the images, the API data. Almost none of them were written by you, and they all happen silently. When the list of groups does not show up, there is no message saying "the request failed here, with this code". Without knowing how to look at the requests, all that is left is guessing. With the Network tab, each request becomes a line you can open and read.

## // What HTTP is

> **HTTP: IN SIMPLE WORDS**
> It is the protocol, that is, the set of conversation rules, that browsers and servers use on the web. It works by **request and response**: the client sends a **request**, and the server returns a **response**. Each request is independent: the server does not "remember" the previous one.

Everything that happens in this week's integration is made of HTTP requests and responses. A request has four parts: the **method** (the action), the **URL** (the resource), the **headers** (extra information) and, sometimes, a **body** (data sent). A response has three others: the **status code** (how it went), the **headers** and, almost always, a **body**.

This is a real conversation with this week's API, made with `curl` in verbose mode. The lines with `>` are the request, and the ones with `<` are the response:

```
> GET /grupos?limit=2 HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/X.Y
> Accept: */*
>
< HTTP/1.1 200 OK
< server: uvicorn
< content-length: 285
< content-type: application/json
< x-total-count: 6
<
[{"nome_grupo":"Cálculo passo a passo","materia_id":1, ... }, ... ]
```

Reading it: the client requested (`GET`) the `/grupos` resource, with the `limit=2` parameter, from the server at `127.0.0.1:8000`. The server answered `200 OK`, said the body is 285 bytes of JSON, reported that there are 6 groups in total, and delivered the body. (The real response also carries the `date` header, omitted here.)

## // The methods the page will use

| Method | What it is for | Example this week |
|---|---|---|
| `GET` | Read, without changing anything | `GET /grupos?limit=4` lists the groups |
| `POST` | Create a new resource | `POST /grupos` creates a group |
| `PATCH` | Change only some fields of a resource | `PATCH /grupos/3` changes the participant limit |
| `DELETE` | Delete a resource | `DELETE /grupos/3` removes the group |

## // The status codes you will run into

The first digit tells the story: **2xx** is success, **4xx** is a problem with the request (the caller's fault), **5xx** is a problem on the server. These are this week's API codes, all taken from real runs:

| Code | Name | When it shows up | Example |
|---|---|---|---|
| 200 | OK | It worked, with data | `GET /grupos` |
| 201 | Created | A resource was created | `POST /grupos`, with the `location: /grupos/7` header |
| 204 | No Content | It worked, **with no body** | `DELETE /grupos/7` |
| 404 | Not Found | The requested resource does not exist | `GET /grupos/99` returns `{"detail":"Grupo não encontrado"}` |
| 405 | Method Not Allowed | The route does not accept that method | `DELETE /grupos` |
| 409 | Conflict | The request conflicts with what already exists | Creating a group with a repeated name in the same subject |
| 422 | Unprocessable | The data sent is invalid | A name shorter than 3 characters |
| 500 | Internal Server Error | A failure inside the server | An unhandled programming error |

## // The Network tab

<div align="center">
<img src="../docs/assets/svg/aba-rede-esquema.svg" alt="Diagram of the browser's Network tab, with the list of requests and the headers panel" width="640">
</div>

Every current browser has **developer tools**, usually opened with the **F12** key (on macOS, it is normally Option, Command and I). In them, the **Network** tab lists every request the page makes. The drawing above is a simplified diagram: the names of the buttons and tabs vary between browsers and between languages, and the tab was **not reproduced in a browser** while this material was produced, so check the names on your own screen.

What to read in each request:

| Information | Where it shows up | What it is for |
|---|---|---|
| Method and URL | On the request line and in the headers | Checking whether the request is the one you had in mind |
| Status code | In the Status column | Knowing whether it worked and, if not, whose fault it is |
| Request and response headers | In the details panel | Spotting format and CORS problems |
| Response body | In the Response or Preview tab | Seeing what the API actually returned |
| Time | In the Time column | Noticing slow requests |

Two tips that save time: use the **Fetch/XHR filter** to see only the requests made by JavaScript, and, if the browser offers it, tick the option to **preserve the log**, so the list is not cleared when the page reloads.

## // Good example × bad example

**Bad example**: treating the browser as a black box:

```
"The list does not show up. I will poke at the JavaScript until it works."
```

Without looking at the request, it is impossible to know whether the problem is in the address, in the server, in the data or in the browser.

**Good example**: looking at the request before touching anything:

```
1. Open the Network tab and reload the page.
2. Find the request to /grupos.
3. Read the status, the headers and the response body.
4. Only then decide what to fix.
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The Network tab is empty | The tools were opened **after** the page loaded | Open the tools and reload the page |
| The request does not show up | A filter is hiding it (for example, JS only) | Choose "All", or the Fetch/XHR filter |
| Mistaking `200` for "it worked on screen" | The server answered, but the JavaScript did not handle the response | Check the Response tab and the Console |
| Thinking `404` and `500` are the same thing | Both are "errors" | `404` is a resource that does not exist, and `500` is a server failure |
| Expecting the server to remember the previous request | On a screen, the state lives in the page | In HTTP each request is independent: carry everything the server needs |

## // Guided practice

1. Open any website in the browser, press **F12** and open the **Network** tab. Reload the page.
2. Click the first request in the list and write down: the method, the status code and the response's `content-type`.
3. Pick another request (an image, a stylesheet) and compare the `content-type`.
4. If you already have `curl`, run `curl -v https://example.com` and identify the request (`>`) and response (`<`) lines.

## // Practice on your own

> **CHALLENGE**
> Open three different websites and, for each one, find in the Network tab a request from each status family: one `2xx`, one `3xx` (redirect) and, if you can, one `4xx`. Write down the method, the URL and what the code means. If no `4xx` shows up, type an address that does not exist on the same site (for example, `/pagina-que-nao-existe`) and look at the request the browser made.

## // Applying it to this week's project

1. Create a folder called `projeto-fullstack`, with two empty subfolders: `api` and `frontend`. They will hold the two ends of the application.
2. Inside the folder, create a file named `anotacoes-http.md` and write, in your own words, the difference between the codes `200`, `201`, `204`, `404`, `409` and `422`.
3. If you track the project with Git, make a commit: `git commit -m "Cria a estrutura do projeto full-stack"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> You open the Network tab and see a `GET /grupos` request with status `200`, but the list does not show up on the page. Is the problem in the API or in the page?

Answer: in the **page**, or in something between the API and the page. The `200` status shows that the API answered successfully and delivered data. What is missing is looking at the response **body** (did the server send what was expected?) and the **Console** (did the JavaScript fail while using the data?). That is exactly why the Network tab comes before any code change: it cuts the problem in half.

## // Module summary

- [ ] I can explain what HTTP is, and that each request is independent.
- [ ] I know the parts of a request (method, URL, headers, body) and of a response (status, headers, body).
- [ ] I know the `GET`, `POST`, `PATCH` and `DELETE` methods, and what each one does.
- [ ] I know what the codes `200`, `201`, `204`, `404`, `405`, `409`, `422` and `500` mean.
- [ ] I can open the Network tab, filter by Fetch/XHR and read status, headers and body.

---

**Next module:** `02-headers.md`, headers show up in every request and every response, and they are the key to understanding CORS.

`Study Material // Coffee & Code`

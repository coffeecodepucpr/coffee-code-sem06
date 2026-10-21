# Module 08, Serving the Front-end and the Origin

[Português](../docs/08-servindo-o-front-end-e-a-origem.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

In Module 07, the requests worked because they came from inside the API itself. The real page will live somewhere else: a folder on your computer. This module shows how to serve it properly, introduces the concept of an **origin**, and ends by deliberately triggering the problem Module 09 solves.

## // The problem: a file opened by double-clicking is not a site

It is tempting to open `index.html` with a double click. The browser opens the page, and it even seems to work. But the address in the bar starts with `file://`, not `http://`, and that changes what the browser allows: the page gets a special origin called `null`, and resources such as JavaScript modules may be blocked. To integrate with an API, the page needs to be served by a **web server**, however simple.

## // Serving the page

Python ships with a ready-made web server. In a **second terminal** (the first one still has the API), enter the front-end folder and run:

```
python3 -m http.server 5500 --bind 127.0.0.1
```

(On Windows, swap `python3` for `py`.) The terminal shows:

```
Serving HTTP on 127.0.0.1 port 5500 (http://127.0.0.1:5500/) ...
```

Open `http://127.0.0.1:5500` in the browser: the page shows up. For every file requested, the server writes a log line in the terminal:

```
127.0.0.1 - - [09/Oct/2026 02:29:11] "GET / HTTP/1.1" 200 -
```

| Part of the command | What it is for |
|---|---|
| `python3 -m http.server` | Starts Python's built-in web server, in the folder you are in |
| `5500` | The port. Any free number works, but we will always use this one |
| `--bind 127.0.0.1` | Serves **only your computer** |
| `--directory pasta` | Serves another folder, without having to enter it (optional) |

The server delivers each file with the right type, verified in a real run: `index.html` as `text/html`, `app.js` as `text/javascript` and `estilos.css` as `text/css`. The JavaScript type matters: modules require it to be delivered as JavaScript.

> **WITHOUT --BIND, THE SERVER SERVES YOUR WHOLE NETWORK**
> In a test, the same command **without** `--bind` announced `Serving HTTP on 0.0.0.0 port 5520`, and the folder started answering `200` on **another address of the machine**. `0.0.0.0` means "all networks": anyone on the same network (the campus Wi-Fi, for example) would be able to open your files. Always use `--bind 127.0.0.1`.

## // What an origin is

> **ORIGIN: IN SIMPLE WORDS**
> It is the combination of **scheme** (`http`), **host** (`127.0.0.1`) and **port** (`5500`) of an address. The path does not count. Two URLs are same-origin only if all three parts are identical.

<div align="center">
<img src="../docs/assets/svg/origem.svg" alt="A URL split into scheme, host, port and path, and four examples of same origin or different origin" width="640">
</div>

With that, this week's application has **two origins**:

| End | Address | Origin |
|---|---|---|
| The page | `http://127.0.0.1:5500` | scheme `http`, host `127.0.0.1`, port `5500` |
| The API | `http://127.0.0.1:8000` | scheme `http`, host `127.0.0.1`, port `8000` |

Only the port differs, and that is enough: **they are different origins**. The same goes for `localhost` and `127.0.0.1`: both point to your computer, but the browser compares them as text, and they are not equal.

## // The same-origin policy

> **SAME-ORIGIN POLICY: IN SIMPLE WORDS**
> It is the browser's basic security rule: a page's JavaScript may only **read** the responses of requests made to its **own origin**. To read a response from another origin, that other origin's server has to authorize it explicitly (that is CORS, the subject of the next module).

That is why Module 07 worked: the Swagger page and the API were on the same origin (`http://127.0.0.1:8000`). The new page, on port 5500, is not.

## // The experiment: triggering the problem

With the API up (port 8000, still **without CORS**, the `api-inicial` version) and the page served (port 5500), open `http://127.0.0.1:5500`, the developer tools (F12) and the **Console** tab. In the `app.js` file, write:

```js
const API = "http://127.0.0.1:8000";

const resposta = await fetch(`${API}/grupos?limit=2`);
console.log(await resposta.json());
```

Save and reload the page. What the browser should do, according to this section's rules: **not** hand the response to your code, and write a CORS error in the console. The exact text varies between browsers, and this message was **not reproduced** while the material was produced.

But you already know what the server saw, because we tested it with `curl`: it answered `200`, with the data. There is nothing wrong with the API. What is missing is the server's **authorization**, and Module 09 shows how it works and how to configure it.

## // Good example × bad example

**Bad example**: opening the page with a double click:

```
file:///C:/Users/ana/projeto-fullstack/frontend/index.html
```

The origin is `null`, and modules and requests may be blocked in confusing ways.

**Good example**: serving the folder and opening it through the server's address:

```
python3 -m http.server 5500 --bind 127.0.0.1
http://127.0.0.1:5500
```

## // Common mistakes

These messages and behaviours were obtained by running the commands.

| Mistake | Why it happens | How to fix it |
|---|---|---|
| `OSError: [Errno 98] Address already in use` | There is already a server on port 5500 (perhaps one from an earlier test) | Stop the other one with Ctrl+C in its terminal, or use another port |
| `404`, and `code 404, message File not found` in the terminal | The server was started in the wrong folder, or the file does not exist | Enter the folder that holds `index.html` and run it again |
| The page opens, but the old JavaScript keeps running | The browser cached the old file | Reload without cache (usually Ctrl+Shift+R), or tick "disable cache" in the tools |
| The server answers other computers on the network | `--bind 127.0.0.1` was missing | Stop it and run again with `--bind` |
| Opening the page via `file://` | Double-clicking the file | Serve the folder and use `http://127.0.0.1:5500` |
| `python3: command not found` on Windows | The command on Windows is `py` | Use `py -m http.server 5500 --bind 127.0.0.1` |

## // Guided practice

1. Copy `example/frontend-inicial` to `projeto-fullstack/frontend`.
2. In a terminal, inside that folder, run `python3 -m http.server 5500 --bind 127.0.0.1` and open `http://127.0.0.1:5500`.
3. Look at the terminal: check the log lines for `GET / ` and for the style and script files.
4. With the API (`api-inicial`) running in another terminal, open the Console and run this module's experiment.
5. Change the page's address to `http://localhost:5500` and answer: is the origin the same as `127.0.0.1:5500`?
6. Stop the server with Ctrl+C and try to bring up another one on the same port while the first is still up: read the error.

## // Practice on your own

> **CHALLENGE**
> Bring up **two** static servers at the same time, on ports 5500 and 5501, serving the same folder. Write down, for each one, the page's origin. Answer: could a page opened on `5501` read the API's responses without CORS? And could a page opened on `5501` read those of a page on `5500`? Justify it with the definition of an origin.

## // Applying it to this week's project

1. Write down in `README.md`, in the "Como rodar" section, both commands: the API's and the page server's, with the `--bind`.
2. Record the application's two origins and the same-origin rule in one line.
3. If you track the project with Git, make a commit: `git commit -m "Documenta como servir o front-end"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> The page is at `http://127.0.0.1:5500` and the API at `http://127.0.0.1:5500/api`, on the **same port**, behind the same server. Are they same-origin? And what if the API were at `https://127.0.0.1:5500`?

Answer: in the first case, **yes**: scheme, host and port are the same, and the path (`/api`) does not count, so the browser treats them as the same origin, with no CORS. In the second, **no**: the scheme changed from `http` to `https`, and just one of the three parts differing is enough to make it another origin.

## // Module summary

- [ ] I know how to serve the front-end folder with `python3 -m http.server 5500 --bind 127.0.0.1`.
- [ ] I know why `--bind 127.0.0.1` matters, and why not to open the page via `file://`.
- [ ] I can define an origin (scheme, host and port) and compare two origins.
- [ ] I know why `localhost` and `127.0.0.1` are different origins.
- [ ] I know what the same-origin policy is.
- [ ] I know how to trigger the CORS problem, and that the API itself is not wrong.

---

**Next module:** `09-cors-the-browser-blocks.md`, the server has to authorize the page. That is how CORS solves the problem.

`Study Material // Coffee & Code`

# Module 13, Pagination and Exposed Headers

[Português](../docs/13-paginacao-e-cabecalhos-expostos.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

The page's list shows four groups at a time, and **Anterior** and **Próxima** buttons move between pages. For that, the page needs to know **how many groups exist in total**, and that number travels in a response header, the `X-Total-Count`. It is the last piece of the integration, and it brings together two subjects you have already seen: the API's pagination (Module 03) and the headers JavaScript may or may not read (Modules 02 and 09).

## // The problem: how many pages are there?

The API returns only the requested page: with `limit=4`, four groups come back, and nothing in the list says whether there are more. Without the total, the page cannot know whether to enable **Próxima**, nor draw "page 1 of 2". The response is a list, and a list has no place for an extra number, so the API puts it in a **header**.

## // Pagination with limit and offset

The API accepts two parameters on `GET /grupos`:

| Parameter | Meaning |
|---|---|
| `limit` | How many groups to return (1 to 100, default 10) |
| `offset` | How many groups to skip before starting (default 0) |

The page uses four groups at a time. The requests for each page:

| Page | Request | What the API returns |
|---|---|---|
| 1 | `?limit=4&offset=0` | The first four, in alphabetical order |
| 2 | `?limit=4&offset=4` | The next two (there are six groups) |

The arithmetic is always the same: the `offset` of page `n` is `(n - 1) × limit`. In `app.js`:

```js
deslocamento: (estado.pagina - 1) * TAMANHO_DA_PAGINA,
```

And the number of pages is the total divided by the size, **rounded up**, with a minimum of one page:

```js
const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
```

With six groups and four per page, `Math.ceil(6 / 4)` is `2`. The `Math.max(1, ...)` makes sure that, with zero groups, "page 1" still exists, instead of "page 1 of 0".

## // The X-Total-Count header

Every `GET /grupos` response carries the total number of groups **matching the filters**, computed **before** the page is cut. The API's real response:

```
GET /grupos?limit=2

HTTP/1.1 200 OK
x-total-count: 6
```

The total respects the search and the filter: with `?q=prática&limit=1`, it is `1`, not `6`, because only one group matches the filter. The value is used to draw "page 1 of N" **for that search**.

In JavaScript, the header is read with `resposta.headers.get(...)`, and comes back as **text**, hence the `Number(...)`:

```js
const total = resposta.headers.get("X-Total-Count");
if (total === null) {
  console.warn(
    "X-Total-Count não está visível. Confira o expose_headers do CORS na API."
  );
}
return { grupos: dados, total: total === null ? dados.length : Number(total) };
```

## // The header the browser hides

The `X-Total-Count` is in the response, and even so JavaScript may receive `null`. The reason, which Module 02 foreshadowed: the page and the API are on **different origins**, and the browser only lets JavaScript read the response's **basic** headers (`Cache-Control`, `Content-Language`, `Content-Length`, `Content-Type`, `Expires`, `Last-Modified` and `Pragma`). Any other one has to be **exposed** by the server:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Total-Count"],
)
```

With that, the API's response starts carrying one more header, `access-control-expose-headers`, which **lists** the headers released to JavaScript (verified with `curl`, in Module 09):

```
x-total-count: 6
access-control-expose-headers: X-Total-Count
access-control-allow-origin: http://127.0.0.1:5500
```

Without the `expose_headers`, the browser would hand `null` to the JavaScript. This is a **browser** rule, described in MDN and in the Fetch specification, and it was **not reproduced in a browser** while the material was produced. The page's code defends itself: if `total` comes back `null`, it uses the page's size as the total and writes a warning in the console, pointing to the likely cause.

> **A SILENT TRAP**
> Without the defence, `Number(null)` is `0`. The page would show "0 grupos" and disable both buttons, with a full list on screen, and **no error** would show up in the console. That is why a missing `X-Total-Count` deserves an explicit warning.

## // The pagination buttons and text

The pagination drawing lives in a `ui.js` function:

```js
export function renderizarPaginacao({ pagina, totalDePaginas, total }) {
  const grupos = total === 1 ? "grupo" : "grupos";
  $("pagina-atual").textContent =
    `Página ${pagina} de ${totalDePaginas} (${total} ${grupos})`;
  $("anterior").disabled = pagina <= 1;
  $("proxima").disabled = pagina >= totalDePaginas;
}
```

The **Anterior** button is disabled on the first page, and **Próxima** on the last. Notice the agreement: `1 grupo`, and `6 grupos` (a small bit of care that makes the screen feel made by people).

And the clicks, registered in `iniciar()`:

```js
el.anterior.addEventListener("click", () => {
  estado.pagina -= 1;
  carregarGrupos();
});
el.proxima.addEventListener("click", () => {
  estado.pagina += 1;
  carregarGrupos();
});
```

The filters go back to page 1, because page 3 of one search makes no sense in the next search:

```js
el.busca.addEventListener("input", comAtraso(() => {
  estado.busca = el.busca.value.trim();
  estado.pagina = 1;
  carregarGrupos();
}, 300));
el.filtroMateria.addEventListener("change", () => {
  estado.materiaId = el.filtroMateria.value;
  estado.pagina = 1;
  carregarGrupos();
});
```

## // What the tests confirmed

In an automated test against the real API:

| Situation | Pagination text | Buttons |
|---|---|---|
| Initial page | `Página 1 de 2 (6 grupos)` | Anterior disabled, Próxima enabled |
| After **Próxima** | `Página 2 de 2` | Próxima disabled, and two groups in the list (`Redes na unha` and `Requisitos e histórias`) |
| Search `prática` | `Página 1 de 1 (1 grupo)` | Both disabled |
| After creating a group | `Página 1 de 2 (7 grupos)` | |
| With 9 groups, on page 3, deleting its only item | `Página 2 de 2 (8 grupos)` | Goes back by itself to the last page that exists |

## // Good example × bad example

**Bad example**: computing the total by counting the list that arrived:

```js
// grupos tem, no máximo, 4 itens!
const totalDePaginas = Math.ceil(grupos.length / 4);
```

The list is only **one page**: the result would always be `1`.

**Good example**: using the total the API reported:

```js
const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| `headers.get("X-Total-Count")` returns `null` | The API did not expose the header | Add `expose_headers=["X-Total-Count"]` to CORS |
| The screen shows "0 grupos" with a full list | `Number(null)` is `0` | Handle the `null` (the page already defends itself) |
| "Página 3 de 2" after deleting | The requested page stopped existing | Go back to the last page that exists (Module 10) |
| The pagination stays on page 3 after a search | The filter did not go back to page 1 | Set `estado.pagina = 1` when the filter changes |
| "1 grupos" in the singular | The agreement was not handled | Swap `grupos` for `grupo` when the total is 1 |
| The `offset` is wrong | The arithmetic used `pagina` instead of `pagina - 1` | `(pagina - 1) * limite` |
| `422` when asking for `limit=0` or `limit=101` | The `limit` stays between 1 and 100 | Respect the API's limits |

## // Guided practice

1. With the API (with CORS) and the page up, check "Página 1 de 2 (6 grupos)" and navigate to page 2 and back.
2. In the Network tab, find the listing request and read the `x-total-count` and the `access-control-expose-headers` in the response headers.
3. In `curl`, run `curl -i "http://127.0.0.1:8000/grupos?q=prática&limit=1"` and read the total.
4. Create groups until you go past four per page and check the new pages.
5. Remove `expose_headers` from the API, reload the page and watch the console warning and the pagination's behaviour. Then restore the line.

## // Practice on your own

> **CHALLENGE**
> Add a **page size selector** to the pagination, with the options 2, 4 and 8 groups per page. Swap the `TAMANHO_DA_PAGINA` constant for a value kept in `estado`, go back to page 1 when the size changes, and check that the `offset` and the number of pages stay correct at all three sizes.

## // Applying it to this week's project

1. Complete `renderizarPaginacao`, the two buttons and the page reset on the filters.
2. Check that the `expose_headers` is in the API's `main.py`.
3. In `README.md`, explain in two lines why the API has to expose the `X-Total-Count`.
4. If you track the project with Git, make a commit: `git commit -m "Pagina a lista de grupos"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> The API returned `x-total-count: 6`, and the Network tab shows the header in the response. The page, however, shows "0 grupos". What is the most likely cause, and how do you confirm it?

Answer: the server did not expose the header. The Network tab shows everything that **arrived** at the browser, but JavaScript may only **read** the basic headers and the ones listed in `Access-Control-Expose-Headers`. Without that, `headers.get(...)` returns `null`, and `Number(null)` gives `0`. To confirm it, look for the `access-control-expose-headers` header in the response: if it is absent, or does not list `X-Total-Count`, that is the cause. The fix is `expose_headers=["X-Total-Count"]` on the API.

## // Module summary

- [ ] I know how to compute the `offset` (`(page - 1) × limit`) and the number of pages (`Math.ceil`, at least 1).
- [ ] I know that the `X-Total-Count` reports the total after the filters, and before the page is cut.
- [ ] I know why the browser hides that header, and how to expose it with `expose_headers`.
- [ ] I know why `Number(null)` is a silent trap.
- [ ] I know how to enable and disable the buttons, and go back to page 1 when a filter changes.

---

**Next module:** `14-guided-project.md`, every piece is ready. Time to put them together and check the whole application.

`Study Material // Coffee & Code`

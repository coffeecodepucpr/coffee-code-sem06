# Challenges, Week 06

[Português](../docs/desafios.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

Optional challenges, organized by the week's modules. None of them is required for the basic delivery; see `deliverable.md` for what is mandatory. Use these challenges if you have finished the main modules and want to go further. In each block, the challenges for those who are **starting out** come first, and the ones for those who **already have experience**, after.

---

## // HTTP, headers and the API (Modules 01 to 03)

**If you are starting out**
- Open the Network tab on three sites and, for each one, find a response with a different `Content-Type` (HTML, image, JSON or stylesheet). Write down the type and what the browser does with each.
- Run `curl -v` against the API and note, in your own words, which request header and which response header you find most important for integration, and why.

**If you already have experience**
- Research the `429 Too Many Requests` code and the `Retry-After` header. Write how the page should react if the API started returning them.
- Research the `Cache-Control` header and the `304 Not Modified` response. Describe, in a paragraph, how an `ETag` would avoid resending the list of subjects (which almost never changes).

---

## // JavaScript, the DOM and asynchronous code (Modules 04 to 07)

**If you are starting out**
- Write a function `agruparPorMateria(grupos)` that takes the list of groups and returns an object where the key is the `materia_id` and the value is the array of that subject's groups. Test it in the console.
- Write an `async` function `buscarVariosGrupos(ids)` that fetches the groups of a list of identifiers **in parallel** with `Promise.all`, and returns only the ones that exist (ignoring the `404`s).

**If you already have experience**
- Research `AbortController` and use it to **cancel** a search request in flight when the person types another letter. Compare it with the request-number solution (Module 10): which is more efficient, and why?
- Research the difference between `Promise.all`, `Promise.allSettled` and `Promise.race`, and give an example from this week where each would be the best choice.

---

## // Origin and CORS (Modules 08 and 09)

**If you are starting out**
- Bring the page's server up on two ports (5500 and 5501) and write, in a table, which of the two origins the API authorizes and why. Then authorize the second one and prove it with `curl`.
- Write the `curl` for a `DELETE` preflight and predict the result before running it. Then remove `"DELETE"` from `allow_methods` and repeat.

**If you already have experience**
- Use `allow_origin_regex` instead of the fixed list to authorize any port on `127.0.0.1` (for example, from 5500 to 5599). Write the tests: what passes and what should **not** pass? What is the risk of a loose regular expression?
- Research `Access-Control-Allow-Credentials` and how cookies change the CORS rules. Explain, in a paragraph, why `Access-Control-Allow-Origin: *` cannot accompany credentials, and what Starlette does when someone tries (Module 09).

---

## // The page: list, form, editing and pagination (Modules 10 to 14)

**If you are starting out**
- Show next to each group's name a badge with the openings: "poucas vagas" if the limit is lower than 5, and "muitas vagas" otherwise. Use only `textContent` and a CSS class.
- Add a **Limpar filtros** button, which clears the search, sets the filter back to "Todas" and goes back to page 1.

**If you already have experience**
- Replace `window.confirm` with a small confirmation dialog built with the `<dialog>` element. Take care of the keyboard (Esc cancels) and of the focus.
- Make the page remember the last search and the current page, storing them in the **URL** (`?q=...&pagina=2`) with `URLSearchParams` and `history.replaceState`, so that reloading the page (or copying the address) preserves the state.

---

## // Middlewares and JSON standardization (Modules 15 to 17, veteran track)

- Write a middleware that **refuses** bodies larger than 10 KB with a `413`, in the single error format, before the route reads the body. Where should it sit in the order? And CORS?
- Add to the success envelope a `meta.versaoDaApi` field, and to the error one a `meta.documentacao` field with the `/docs` address. Update Swagger and the tests.
- Research the **RFC 9457** format (*Problem Details for HTTP APIs*) and compare it with this week's single error format: what does each one have that the other does not?
- Write a test that guarantees that **every** route of the veteran API returns a `requestId` in `meta` (walking through the `/openapi.json`) and prove, in reverse, that it fails if a route forgets the envelope.

---

## // General challenge (everyone)

Pick a **real** defect you found (or caused) during the week, for example, the `X-Total-Count` that arrives as `null`, the preflight that returns `400`, or the old response that overwrites the new one. Write a **one-page report**, with: the symptom the person sees, the cause, how you found it (which tab, which request, which header) and the fix. This is the exercise that most resembles the work of someone who integrates systems.

---

`Study Material // Coffee & Code`

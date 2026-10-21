# Module 11, Sending Data: Form and POST

[Português](../docs/11-enviando-dados-formulario-e-post.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

So far the page only **reads**. This module makes it **send**: it creates a study group from the form. This is where integration gets more interesting, because the API may **refuse** what the page sent, and the person needs to understand why. You will see the CORS preflight in action, receive errors from the API and show them on the right field of the screen.

## // The problem: the person makes a mistake, and the page has to explain

Two kinds of refusal are expected in a form. The first is **invalid data**: a name that is too short, a limit out of range. The second is a **conflict**: the name already exists in that subject. In both, the API responds with an error, and the page has to turn it into a clear message, in the right place, instead of a generic "something went wrong".

## // From the form to JSON

The `index.html` form has four fields. The `lerFormulario()` function, in `ui.js`, gathers what the person typed into an object ready to become JSON:

```js
export function lerFormulario() {
  const descricao = $("descricao").value.trim();
  return {
    nome_grupo: $("nome").value.trim(),
    materia_id: Number($("materia").value),
    max_participantes: Number($("limite").value),
    descricao: descricao === "" ? null : descricao,
  };
}
```

Three precautions in that function:

- The `.trim()` removes the spaces at the edges: `"   ab "` becomes `"ab"`.
- The `Number(...)` converts the field's text (always text, Module 05) into a number.
- An empty description becomes `null`, not `""`: the API accepts it as "no description".

And the sending, in `api.js`, is a `POST` with JSON (the `pedir()` function from Module 07 already handles the `Content-Type`):

```js
export async function criarGrupo(corpo) {
  return (await pedir("/grupos", { metodo: "POST", corpo })).dados;
}
```

## // The preflight, in the Network tab

A `POST` with `Content-Type: application/json` is **not a simple request** (Module 09): before it, the browser makes, on its own, an `OPTIONS` request. When creating a group, the Network tab should show **two** lines for `grupos`: first the `OPTIONS` (the preflight), with status `200`, then the `POST`, with status `201`. This description follows the specification, and was **not reproduced in a browser** while the material was produced.

This week's API answers the preflight because the `CORSMiddleware` allows the method and the header (verified with `curl` in Module 09):

```
OPTIONS /grupos  (Access-Control-Request-Method: POST, ...-Headers: content-type)

200  access-control-allow-methods: GET, POST, PATCH, DELETE
     access-control-allow-headers: Accept, Accept-Language,
                                   Content-Language, Content-Type
```

## // The errors the API returns

These are the API's real responses for a form's errors:

| What the person did | Status | What comes in `detail` |
|---|---|---|
| A 2-letter name | `422` | A **list**, with the `loc` pointing to `nome_grupo` |
| Limit of 51 | `422` | A **list**, with the `loc` pointing to `max_participantes` |
| A repeated name in the same subject | `409` | A **text**: `Já existe um grupo com esse nome nessa matéria` |
| A subject that does not exist | `422` | A **text**: `A matéria 99 não existe` |

The complete bodies of the first two cases:

```
POST /grupos   {"nome_grupo": "ab", "materia_id": 1}

422  {"detail":[{"type":"string_too_short",
                 "loc":["body","nome_grupo"],
                 "msg":"String should have at least 3 characters",
                 "input":"ab","ctx":{"min_length":3}}]}

POST /grupos   {"nome_grupo": "Teste valido", "materia_id": 1,
                "max_participantes": 51}

422  {"detail":[{"type":"less_than_equal",
                 "loc":["body","max_participantes"],
                 "msg":"Input should be less than or equal to 50",
                 "input":51,"ctx":{"le":50}}]}
```

Notice there are **two formats** of `detail`: a **list of problems** (the automatic validation, with the field in `loc`) and a **text** (the hand-written rules). The page's code has to recognize both.

### > Finding the error's field

In the validation error, `loc` is a list such as `["body", "nome_grupo"]`: the last item is the API's field name. The page keeps a table linking each API field to the element where the error shows up:

```js
const CAMPO_DO_ERRO = {
  nome_grupo: "erro-nome",
  materia_id: "erro-materia",
  max_participantes: "erro-limite",
  descricao: "erro-descricao",
};

export function mostrarErroDeCampo(campo, texto) {
  const id = CAMPO_DO_ERRO[campo];
  if (id) $(id).textContent = texto;
}
```

And `app.js` walks through the response's problems:

```js
function mostrarErrosDeValidacao(detail) {
  for (const problema of detail) {
    // ["body", "nome_grupo"] -> "nome_grupo"
    const campo = problema.loc[problema.loc.length - 1];
    ui.mostrarErroDeCampo(campo, problema.msg);
  }
  ui.mostrarMensagem("Corrija os campos indicados.", "erro");
}
```

The error's text comes from the API, in English (`String should have at least 3 characters`). That is acceptable for studying, and a challenge below proposes translating the messages.

## // The submission handler

The `salvar` function puts it all together. It serves both creating and (in Module 12) editing, and the snippet below shows the complete function:

```js
async function salvar(evento) {
  evento.preventDefault();
  ui.limparErros();
  ui.travarFormulario(true);
  const corpo = ui.lerFormulario();
  try {
    let aviso;
    if (estado.editandoId === null) {
      await api.criarGrupo(corpo);
      aviso = "Grupo criado.";
    } else {
      await api.alterarGrupo(estado.editandoId, corpo);
      aviso = "Grupo atualizado.";
    }
    cancelarEdicao();
    await carregarGrupos();
    // depois de recarregar, porque carregarGrupos limpa a mensagem
    ui.mostrarMensagem(aviso);
  } catch (erro) {
    if (erro instanceof api.ErroHttp && erro.status === 422) {
      if (Array.isArray(erro.corpo?.detail))
        mostrarErrosDeValidacao(erro.corpo.detail);
      else ui.mostrarMensagem(erro.corpo?.detail ?? "Dados inválidos.", "erro");
    } else if (erro instanceof api.ErroHttp && erro.status === 409) {
      ui.mostrarErroDeCampo(
        "nome_grupo", "Já existe um grupo com esse nome nessa matéria."
      );
      ui.mostrarMensagem("Conflito: escolha outro nome.", "erro");
    } else if (erro instanceof api.ErroHttp && erro.status === 404) {
      ui.mostrarMensagem("Esse grupo já não existe.", "erro");
      cancelarEdicao();
      await carregarGrupos();
    } else {
      tratarErro(erro);
    }
  } finally {
    ui.travarFormulario(false);
  }
}
```

The details that make the difference:

| Detail | Why it matters |
|---|---|
| `evento.preventDefault()` | Keeps the browser from reloading the page on submit |
| `ui.travarFormulario(true)` and the `finally` | Disables the **Salvar** button during the request and re-enables it at the end, **even on error**: it prevents the double click, which would create the group twice |
| The success message **after** `carregarGrupos()` | `carregarGrupos` clears the message when it finishes: writing the notice before would erase it (a defect the automated test found) |
| `Array.isArray(erro.corpo?.detail)` | Tells the two `detail` formats apart |
| The `409` branch | Picks the message and marks the name field |
| The `finally` | Always runs: on success or on error |

> **WHY THE PAGE DOES NOT VALIDATE EVERYTHING ITSELF**
> The `index.html` uses `novalidate`, which turns off the browser's automatic validations, and the page lets the **API validate**. The reason is that the API owns the rules (3 to 60 characters, a limit between 2 and 50): if the rule changes, the page stays correct without any edit. Validating on the page too improves the experience, but it **never** replaces the API's validation, because anyone can call the API without going through the page.

## // The result, verified

In an automated test against the real API, these were the confirmed behaviours:

| Action | Result on screen |
|---|---|
| Create `Cálculo II na prática`, subject 1, limit 5 | Message "Grupo criado.", form cleared, pagination "Página 1 de 2 (7 grupos)" |
| Submit the name `ab` | On the name field: `String should have at least 3 characters`; message "Corrija os campos indicados."; the Salvar button works again |
| Repeat `Cálculo II na prática` in subject 1 | On the name field: "Já existe um grupo com esse nome nessa matéria."; message starting with "Conflito" |
| Create a group named `<img src=x onerror=alert(1)>` | The name shows up as text, and no `<img>` element is created |

## // Good example × bad example

**Bad example**: a generic notice for any error:

```js
try {
  await api.criarGrupo(corpo);
} catch {
  alert("Erro ao salvar.");
}
```

The person does not know **what** to fix, **where**, or whether it is worth trying again.

**Good example**: each error, in its own message and on its own field:

```js
} catch (erro) {
  if (erro instanceof api.ErroHttp && erro.status === 422)
    mostrarErrosDeValidacao(erro.corpo.detail);
  else if (erro instanceof api.ErroHttp && erro.status === 409)
    ui.mostrarErroDeCampo("nome_grupo", "Já existe um grupo com esse nome.");
  else tratarErro(erro);
}
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The page reloads on submit | `evento.preventDefault()` was missing | Add it as the first line of `salvar` |
| `422` even with the right name | `Content-Type: application/json` was missing, or the body did not go through `JSON.stringify` | Use `pedir()`, which handles it |
| `422` on the limit, with the field "empty" | `Number("")` gives `0`, and `0` is out of range | That is expected: the API refuses it and the message shows up on the field |
| The group is created twice | A double click on the button | Disable the button during the send (`travarFormulario`) |
| The success message does not show up | It was written before `carregarGrupos()`, which erases it | Write it after reloading |
| The preflight fails with `400` | `POST` or `Content-Type` outside the API's CORS | Check `allow_methods` and `allow_headers` (Module 09) |
| The error shows up only in the console | The `catch` only has a `console.log` | Show the error on screen |

## // Guided practice

1. With the API (with CORS) and the page up, fill the form with a valid name and save. Watch the message and the list.
2. Open the Network tab, filter by Fetch/XHR and find the `OPTIONS` and the `POST` of the submission: read both statuses.
3. Submit the name `ab` and read the error on the field and the response body in the Network tab.
4. Repeat the same group to trigger the `409`.
5. Submit a limit of 51 and write down the message.
6. Click **Salvar** twice very quickly and check that only one group was created.

## // Practice on your own

> **CHALLENGE**
> Translate the validation error messages into Portuguese. Create a `TRADUCOES` object linking the error's `type` (`string_too_short`, `less_than_equal`, `greater_than_equal`, `string_too_long`, `int_parsing`) to a Portuguese text, and use it in `mostrarErrosDeValidacao`, falling back to the API's original message if the type is not in the table. Hint: the `type` is in `problema.type`.

## // Applying it to this week's project

1. Complete the form: `lerFormulario`, `criarGrupo`, `mostrarErroDeCampo`, `mostrarErrosDeValidacao` and the `salvar` function (for now, only the creation branch matters).
2. Test the four cases from the results table and write down what shows up in each.
3. If you track the project with Git, make a commit: `git commit -m "Cria grupos pelo formulário"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Why is the **Salvar** button re-enabled inside a `finally` block, and not at the end of the `try`?

Answer: because `finally` **always** runs, both when the submission works and when it errors out. If the button were re-enabled only at the end of the `try`, any error (a `422`, a `409`, the API being down) would skip that line and leave the button disabled forever: the person would fix the field and would not be able to submit again.

## // Module summary

- [ ] I know how to turn a form into a JSON object (`trim`, `Number` and an empty description as `null`).
- [ ] I know how to send a `POST` with JSON and recognize the preflight in the Network tab.
- [ ] I know the two `detail` formats (list and text) and how to find the error's field.
- [ ] I know how to show each error (`422`, `409`) in the right place on screen.
- [ ] I know how to lock the button during the send and release it with `finally`.
- [ ] I know why the API, and not the page, owns the validation rules.

---

**Next module:** `12-editing-and-deleting-patch-and-delete.md`, creating is done. Now, changing and removing.

`Study Material // Coffee & Code`

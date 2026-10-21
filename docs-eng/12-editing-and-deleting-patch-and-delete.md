# Module 12, Editing and Deleting: PATCH and DELETE

[Português](../docs/12-editar-e-apagar-patch-e-delete.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

Creating and reading are done. The two other CRUD verbs are left: **changing** (`PATCH`) and **deleting** (`DELETE`). Each brings an integration lesson: `PATCH` requires the form to work in two modes, and `DELETE` returns a response **with no body**, which the code has to recognize. Both need to be allowed in CORS, and this is where Module 09's `allow_methods` proves its worth.

## // The problem: the same form, two jobs

The "Novo grupo" form also serves to **edit** an existing group. The page has to remember **which** group is being edited, swap the title and the buttons, fill in the fields and, on save, choose between `POST` and `PATCH`. Without that control, editing would create a new group and leave the old one as it was.

## // The PATCH: changing a group

`PATCH` sends only the fields that change, and the API returns the updated group. The `api.js` function:

```js
export async function alterarGrupo(id, corpo) {
  return (await pedir(`/grupos/${id}`, { metodo: "PATCH", corpo })).dados;
}
```

The page keeps the group being edited in `estado.editandoId`. Clicking **Editar** on a card calls:

```js
function iniciarEdicao(grupo) {
  estado.editandoId = grupo.grupo_id;
  ui.limparErros();
  ui.preencherFormulario(grupo);
}

function cancelarEdicao() {
  estado.editandoId = null;
  ui.limparFormulario();
}
```

And `ui.js` takes care of how both modes look:

```js
export function preencherFormulario(g) {
  $("nome").value = g.nome_grupo;
  $("materia").value = g.materia_id;
  $("limite").value = g.max_participantes;
  $("descricao").value = g.descricao ?? "";
  $("titulo-form").textContent = "Editar grupo";
  $("cancelar").hidden = false;
}

export function limparFormulario() {
  $("form-grupo").reset();
  $("limite").value = 10;
  $("titulo-form").textContent = "Novo grupo";
  $("cancelar").hidden = true;
  limparErros();
}
```

Notice the `g.descricao ?? ""`: a `null` description becomes an empty field. And the **Cancelar edição** button only exists in edit mode (`hidden`).

In Module 11's `salvar` function, the edit branch is the `else`:

```js
if (estado.editandoId === null) {
  await api.criarGrupo(corpo);
  aviso = "Grupo criado.";
} else {
  await api.alterarGrupo(estado.editandoId, corpo);
  aviso = "Grupo atualizado.";
}
```

> **THE FORM SENDS ALL FOUR FIELDS**
> For simplicity, when editing, the page sends **all four** fields, not just the ones that changed. That works with `PATCH`, and it has a useful consequence: if the person **clears** the description, the page sends `descricao: null`, and the API erases it. The other three fields, on the other hand, **do not accept** `null`: the API answers `422`. The page's form never sends them that way, but another program could, and the API has to be protected.

A `PATCH` with `null` on a required field is refused, without corrupting the data. Real response:

```
PATCH /grupos/1   {"nome_grupo": null}

422  {"detail":[{"type":"value_error","loc":["body","nome_grupo"],
    "msg":"Value error, este campo não aceita null: omita-o para não alterá-lo",
    ... }]}
```

And `null` on the description is allowed:

```
PATCH /grupos/3   {"descricao": null}

200  {"nome_grupo":"Modelagem e SQL", ..., "descricao":null, ...}
```

Result verified in a test against the real API: when editing `Cálculo II na prática` and changing the limit to 8, the form goes back to "Novo grupo" mode and the card starts showing "Até 8 participantes".

## // The DELETE: deleting a group

`DELETE` answers `204 No Content`: **no body**. Module 07's `pedir()` function already knows that (it does not call `.json()` on a `204` response):

```js
export async function apagarGrupo(id) {
  await pedir(`/grupos/${id}`, { metodo: "DELETE" });
}
```

Deleting cannot be undone, so the page **asks first**:

```js
async function apagar(grupo) {
  if (!window.confirm(`Apagar o grupo "${grupo.nome_grupo}"?`)) return;
  try {
    await api.apagarGrupo(grupo.grupo_id);
    if (estado.editandoId === grupo.grupo_id) cancelarEdicao();
    await carregarGrupos();
    ui.mostrarMensagem("Grupo apagado.");
  } catch (erro) {
    if (erro instanceof api.ErroHttp && erro.status === 404) {
      ui.mostrarMensagem(
        "Esse grupo já não existe. A lista foi atualizada.", "erro"
      );
      await carregarGrupos();
    } else {
      tratarErro(erro);
    }
  }
}
```

The precautions:

| Precaution | Why |
|---|---|
| `window.confirm(...)` before the request | A question prevents the accidental click. If the person cancels, **nothing** is sent |
| `if (estado.editandoId === grupo.grupo_id) cancelarEdicao()` | If the deleted group was being edited, the form goes back to normal: otherwise saving would try to change a group that does not exist |
| `await carregarGrupos()` afterwards | The list comes to reflect what the API actually has |
| Handling the `404` | The group may already have been deleted (in another tab, or by someone else): the page warns and refreshes, instead of failing |
| The message **after** the reload | For the same reason as in Module 11 |

The API's real response when deleting a group that does not exist:

```
DELETE /grupos/99

404  {"detail":"Grupo não encontrado"}
```

Verified in a test: cancelling the `confirm` deletes nothing, and confirming deletes and updates the pagination (for example, from "Página 1 de 2 (7 grupos)" to "Página 1 de 2 (6 grupos)").

## // Why reload the list, instead of adjusting the screen

After creating, changing or deleting, the page could just touch the card. But it **reloads** the whole list from the API. It is a little slower, and far safer: the total, the alphabetical order and the pagination come to reflect exactly what the API has, and any difference between what the page "thought" and what actually happened disappears.

## // Good example × bad example

**Bad example**: deleting without asking, and adjusting the screen "blindly":

```js
await api.apagarGrupo(grupo.grupo_id);
cartao.remove();     // e se a API tiver recusado? e a paginação?
```

**Good example**: ask, delete, and reload the list from the API:

```js
if (!window.confirm(`Apagar o grupo "${grupo.nome_grupo}"?`)) return;
await api.apagarGrupo(grupo.grupo_id);
await carregarGrupos();
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The `PATCH` or the `DELETE` fail with a CORS error | `PATCH` or `DELETE` are not in `allow_methods` (the preflight returns `400 Disallowed CORS method`) | Allow the methods in the `CORSMiddleware` (Module 09) |
| Editing creates a new group | `salvar` did not check `estado.editandoId` | Use the `if (estado.editandoId === null)` |
| `Unexpected end of JSON input` on delete | `.json()` on a `204` response | Do not read the body (`pedir()` already handles it) |
| The form stays on "Editar grupo" after deleting the group | `cancelarEdicao()` was missing | Cancel the edit if the deleted group was the one being edited |
| The `PATCH` returns `422` with `null` | A required field was sent as `null` | Omit the field, or send a valid value |
| Deleted something by accident | The confirmation was missing | Use `window.confirm` before the request |

## // Guided practice

1. With the API (with CORS) and the page up, click **Editar** on a group, change the limit and save. Check the card.
2. Edit it again, clear the description and save: the description should disappear.
3. Click **Editar** and then **Cancelar edição**: the form goes back to "Novo grupo".
4. Delete a group, cancelling the question the first time and confirming the second.
5. In the Network tab, find the `OPTIONS` and the `PATCH`, and the `OPTIONS` and the `DELETE`: read the statuses (`200` for both preflights, `200` for the `PATCH` and `204` for the `DELETE`, as described in Module 11).
6. Remove `"PATCH"` from `allow_methods` on the API, try to edit, and read the error in the Console and in the Network tab. Then undo it.

## // Practice on your own

> **CHALLENGE**
> Add an **Desfazer** button: right after deleting a group, it **recreates** the deleted group with a `POST` using the same data. Store the last deleted group in `estado.ultimoApagado` and hide the button when there is nothing to undo. Then answer: is the recreated group's `grupo_id` the same as the original's? Check with the API, and explain the result.

## // Applying it to this week's project

1. Complete `alterarGrupo`, `apagarGrupo`, `iniciarEdicao`, `cancelarEdicao`, `preencherFormulario` and `apagar`.
2. Test editing, cancelling the edit, and deleting with and without confirmation.
3. If you track the project with Git, make a commit: `git commit -m "Edita e apaga grupos pela página"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> A person clicks **Editar** on a group and, in another browser tab, someone else deletes that same group. The first one clicks **Salvar**. What should happen, and how does the page handle it?

Answer: the API answers `404` to the `PATCH`, because the group no longer exists. In `salvar`'s `catch`, the `404` branch shows "Esse grupo já não existe.", cancels the edit and reloads the list, which comes to reflect the real state. The page does not break, and the person understands what happened. It is an example of why every error response needs a planned handling.

## // Module summary

- [ ] I know how to use the same form for creating and editing, with `estado.editandoId`.
- [ ] I know how to send a `PATCH` and that required fields do not accept `null`.
- [ ] I know how to delete with `DELETE`, that the `204` response has no body, and why to confirm first.
- [ ] I know how to handle the `404` of a group that no longer exists.
- [ ] I know why to reload the list after every change.
- [ ] I know that `PATCH` and `DELETE` have to be in `allow_methods` in CORS.

---

**Next module:** `13-pagination-and-exposed-headers.md`, the CRUD is complete. What is left is giving the list the pagination it deserves.

`Study Material // Coffee & Code`

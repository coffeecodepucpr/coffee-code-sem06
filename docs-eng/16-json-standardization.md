# Module 16, JSON Standardization

[Português](../docs/16-padronizacao-do-json.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

> **VETERAN TRACK**
> This module is part of the veteran track: it comes after the essential content and is not required for the week's deliverable. Anyone following the main track can skip to `deliverable.md`.

The API you have used so far returns every response with its own look: a raw list, an error as text, another error as a list, field names with underscores. It works, but it forces the page to know every exception. This module creates **one single format** for the responses and for the errors, which the page learns once and uses everywhere. The complete code is in `example/veterano/`.

## // The problem: each response with its own look

These are real responses from the main track's API:

| Situation | Response body | What the page has to know |
|---|---|---|
| List of groups | `[{"grupo_id": 1, ...}]` | That the response **is** the list |
| Nonexistent group (`404`) | `{"detail": "Grupo não encontrado"}` | That the error is a **text** in `detail` |
| Invalid data (`422`) | `{"detail": [{"loc": [...], "msg": ...}]}` | That the error is a **list** in `detail` |
| Total number of groups | The `x-total-count` header | That the total lives **outside** the body |
| Fields | `nome_grupo`, `criado_em` | That the names use **underscores** (and JavaScript, camelCase) |

Each difference becomes an `if` in the page's code. Standardizing means deciding on **one** shape, and making the API always honour it.

## // The format's design

<div align="center">
<img src="../docs/assets/svg/envelope-json.svg" alt="Before and after standardization: the raw list and the error in detail, against the envelope with dados, meta and erro" width="640">
</div>

An **envelope** is an object that wraps the response. Here, there are two:

**Success:** `{ "dados": ..., "meta": ... }`

```json
{
  "dados": [{
    "nomeGrupo": "Cálculo passo a passo", "materiaId": 1,
    "maxParticipantes": 6, "descricao": null,
    "grupoId": 1, "criadoEm": "2026-09-01T12:00:00Z"
  }],
  "meta": {"requestId": "34c8e750cdbe", "total": 6, "limit": 2, "offset": 0}
}
```

**Error:** `{ "erro": { "codigo", "mensagem", "detalhes" }, "meta": ... }`

```json
{
  "erro": {
    "codigo": "nao_encontrado",
    "mensagem": "Grupo não encontrado",
    "detalhes": null
  },
  "meta": {"requestId": "6bd607602de2"}
}
```

| Field | What it is |
|---|---|
| `dados` | What the page asked for: one item or a list |
| `meta` | Information **about** the response: the request's identifier (Module 15) and, in lists, the total and the pagination |
| `erro.codigo` | A short, **stable** text, meant for code to read (`nao_encontrado`, `conflito`...) |
| `erro.mensagem` | The text for a **person** to read |
| `erro.detalhes` | A list of specific points (used in validation), or `null` |

The page comes to decide by the **code**, and not by the message's text: the message can be rewritten or translated without breaking anything.

This API's codes:

| `erro.codigo` | Status | When |
|---|---|---|
| `nao_encontrado` | `404` | The group (or the route) does not exist |
| `metodo_nao_permitido` | `405` | The route does not accept that method |
| `conflito` | `409` | A repeated name in the same subject |
| `regra_de_negocio` | `422` | An API rule was violated (for example, a nonexistent subject) |
| `validacao` | `422` | Invalid data, with the list of fields in `detalhes` |
| `erro_interno` | `500` | An unexpected error (Module 15) |

## // Step 1: names in camelCase

JavaScript uses `nomeGrupo`, and Python uses `nome_grupo`. Instead of picking a side, Pydantic converts automatically, with an **alias generator**:

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    # alias_generator: no JSON, nomeGrupo; no Python, nome_grupo.
    # populate_by_name: o Python ainda pode usar o nome com sublinhado.
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class GrupoOut(Base):
    grupo_id: int
    nome_grupo: str
    criado_em: datetime
```

The result, in real responses:

| Direction | Example |
|---|---|
| The API **returns** | `{"grupoId": 3, "nomeGrupo": "Modelagem e SQL", "maxParticipantes": 8, "criadoEm": "2026-09-03T12:00:00Z"}` |
| The API **accepts** (camelCase) | `POST /grupos` with `{"nomeGrupo":"Cálculo II na prática","materiaId":1,"maxParticipantes":5}` returns `201` |
| The API **also accepts** (underscores) | Because of `populate_by_name=True`: `{"nome_grupo": "...", "materia_id": 5}` returns `201` |

Swagger keeps up: it documents the names in camelCase (`nomeGrupo`, `requestId`), because it reads the aliases. The **dates** already come out in the ISO 8601 standard, in UTC, with a `Z` at the end (`2026-09-03T12:00:00Z`), and JavaScript reads them with `new Date(...)`.

A **query parameter**'s name also needs an alias, because it does not go through the model:

```python
materia_id: Annotated[int | None, Query(alias="materiaId")] = None
```

## // Step 2: the success envelope

The envelope is a **generic** model: it works for any kind of `dados`.

```python
T = TypeVar("T")


class MetaDeLista(Base):
    request_id: str
    total: int
    limit: int
    offset: int


class RespostaLista(Base, Generic[T]):
    """Envelope de uma lista: { dados, meta } com o total e a paginação."""

    dados: list[T]
    meta: MetaDeLista
```

In the route, the response is declared with the type (`RespostaLista[GrupoOut]`), and the route returns a dictionary:

```python
@app.get("/grupos", response_model=RespostaLista[GrupoOut], tags=["grupos"])
def listar_grupos(request: Request, q: str | None = None, ...):
    ...
    return {
        "dados": grupos[offset : offset + limit],
        "meta": meta_do(request, total=len(grupos), limit=limit, offset=offset),
    }
```

Since the envelope is declared in the `response_model`, **Swagger documents it**: it shows the `dados` and `meta` structure, and the models' names generate `RespostaLista_GrupoOut_`. The documentation and the API tell the same story.

> **THE DELETE HAS NO ENVELOPE**
> The `204 No Content` response **has no body** (Module 07), so there is nowhere to put an envelope. That is normal: the single format applies to responses **with a body**. The page already knows how to handle the `204` through `pedir()`.

## // Step 3: the error envelope

The previous module's error handlers build the error envelope in **one single place**:

```python
def resposta_de_erro(
    request: Request, status_code: int, codigo: str, mensagem: str,
    detalhes=None, headers=None,
) -> JSONResponse:
    erro = {"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes}
    corpo = {"erro": erro, "meta": _meta(request)}
    return JSONResponse(corpo, status_code=status_code, headers=headers)


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def tratar_erro_http(request: Request, erro: StarletteHTTPException):
        codigo = CODIGO_POR_STATUS.get(erro.status_code, "erro_http")
        mensagem = MENSAGEM_PADRAO.get(str(erro.detail), str(erro.detail))
        return resposta_de_erro(
            request, erro.status_code, codigo, mensagem,
            headers=getattr(erro, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(request: Request, erro: RequestValidationError):
        detalhes = [
            {"campo": ".".join(str(p) for p in e["loc"]), "mensagem": e["msg"]}
            for e in erro.errors()
        ]
        return resposta_de_erro(
            request, 422, "validacao",
            "Os dados enviados são inválidos", detalhes,
        )
```

The first handler covers the errors the routes raise (`404`, `409`, rule-based `422`) and also the ones the framework itself generates (nonexistent route and method), and translates the default English messages. The second turns the validation error into a list of fields. The `500` is the catch-all's, from Module 15.

Real responses, for the same errors the page runs into:

| Request | Response |
|---|---|
| `POST /grupos` with `nomeGrupo` `"ab"` and `materiaId` `0` | `422`, `"codigo":"validacao"`, with one item in `detalhes` for each field (see below) |
| `POST /grupos` with a subject that does not exist | `422`, `"codigo":"regra_de_negocio"`, `"mensagem":"A matéria 99 não existe"` |
| `POST /grupos` with a repeated name | `409`, `"codigo":"conflito"`, `"mensagem":"Já existe um grupo com esse nome nessa matéria"` |
| `PATCH /grupos/7` with `nomeGrupo` equal to `null` | `422`, `"codigo":"validacao"`, `"campo":"body.nomeGrupo"` |
| `DELETE /grupos` | `405`, `"codigo":"metodo_nao_permitido"`, `"mensagem":"Método não permitido para este recurso"`, and the `allow: GET` header kept |

The complete body of the first case:

```
POST /grupos   {"nomeGrupo": "ab", "materiaId": 0}

422  {
  "erro": {
    "codigo": "validacao",
    "mensagem": "Os dados enviados são inválidos",
    "detalhes": [
      {"campo": "body.nomeGrupo",
       "mensagem": "String should have at least 3 characters"},
      {"campo": "body.materiaId",
       "mensagem": "Input should be greater than 0"}
    ]
  },
  "meta": {"requestId": "74c1e241d7b5"}
}
```

Notice that, in validation, the field names come out in camelCase (`body.nomeGrupo`), consistent with the rest of the API.

## // Step 4: the page learns the format once

The whole front-end change fits in **one file**, `api.js`, which comes to unwrap the envelope:

```js
const envelope = resposta.status === 204
  ? null
  : await resposta.json().catch(() => null);
if (!resposta.ok) {
  const idDoPedido = resposta.headers.get("X-Request-ID");
  throw new ErroHttp(resposta.status, envelope, idDoPedido);
}
return { dados: envelope?.dados ?? null, meta: envelope?.meta ?? null };
```

And the listing reads the total from the **body**, not from a header:

```js
const { dados, meta } = await pedir(`/grupos?${parametros}`);
// o total agora vem no corpo, não em um cabeçalho
return { grupos: dados, total: meta.total };
```

One good consequence: the total stops depending on the `expose_headers` (Module 13). The rest of `api.js` does not need to change. The remaining difference is in the names: `ui.js` and `app.js` come to use `nomeGrupo`, `materiaId`, `maxParticipantes` and `grupoId`. And the error handling comes to use the **code** (`erro.codigo === "validacao"`), with the list of fields ready in `erro.detalhes`:

```js
if (erro instanceof api.ErroHttp && erro.codigo === "validacao") {
  mostrarErrosDeValidacao(erro.detalhes);
} else if (erro instanceof api.ErroHttp && erro.codigo === "conflito") {
  ui.mostrarErroDeCampo(
    "nomeGrupo", "Já existe um grupo com esse nome nessa matéria."
  );
}
```

The **same automated test** of the front-end, without changing a line, passes with the standardized API and the adapted page: the 12 steps checked (Module 17). Standardization changed the format, not the behaviour.

## // The price of standardization

| Gain | Cost |
|---|---|
| The page learns **one** format for everything | The JSON gains one more level of nesting |
| The error's code is stable: the message can change | The `204` still has no envelope: the single format applies only to responses with a body |
| The `requestId` links the screen to the log, in every response | A client that already used the old API **breaks**: changing the format is an incompatible change |
| Swagger and the API match | The new format has to be documented and maintained by everyone who touches the API |

That last row of the table is the most important one in a real system: changing the format of an API that already has clients requires agreeing on the change, and in general a **new version** is published (under `/v2`, for example) instead of altering the old one. Here, since the API is only for study, the swap is direct.

## // Good example × bad example

**Bad example**: the page decides by the message's text:

```js
if (erro.message.includes("Já existe")) { /* conflito */ }
```

If someone fixes the message's wording, the page breaks without warning.

**Good example**: the page decides by the stable code:

```js
if (erro.codigo === "conflito") { /* conflito */ }
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| The page shows `undefined` in the fields | The page reads `nome_grupo`, and the API returns `nomeGrupo` | Update the names in `ui.js` and `app.js` |
| The subject filter stopped working | The parameter is now called `materiaId` | Use `materiaId` in the query |
| `422` when sending `nome_grupo` from the page | The model expects `nomeGrupo` | Send it in camelCase (`populate_by_name` accepts both, but the standard is camelCase) |
| The total shows up as `0` | `api.js` still reads the `X-Total-Count` header | Read `meta.total` |
| Trying to read `dados` from a `204` response | There is no body | Handle the `204` before unwrapping |
| An error with no `meta.requestId` | The handler built the error without the `_meta(request)` | Always use the `resposta_de_erro` function |
| Swagger shows the old format | The `response_model` was not updated | Declare `RespostaItem[...]` and `RespostaLista[...]` in the routes |

## // Guided practice

1. Run the veteran API (`example/veterano/api`) and do `curl -i "http://127.0.0.1:8000/grupos?limit=2"`: identify `dados`, `meta` and the `requestId` in the body and in the header.
2. Trigger, through `curl`, a `404`, a `409` and a `422`, and compare each response with the module's table.
3. Send a `POST` in camelCase and then with underscores: both should work.
4. Open `/docs` and look for `RespostaLista_GrupoOut_`: see the envelope's structure.
5. Serve the veteran front-end (`example/veterano/frontend`) and go through Module 14's script: nothing should have changed for the person using the screen.

## // Practice on your own

> **CHALLENGE**
> Add to the lists' `meta` a `totalDePaginas` field, computed on the API (`ceil(total / limit)`), and make the page use it instead of the arithmetic it does itself. Think about the consequences: what changes if the page size is set by the page, and not by the API? And in which places would the arithmetic end up duplicated?

## // Applying it to this week's project

1. If you followed the veteran track, apply the `alias_generator`, the envelopes and the error handlers to your API.
2. Adapt your `api.js` to unwrap the envelope and use the errors' `codigo`.
3. In `README.md`, document the success format, the error format and the table of codes.
4. If you track the project with Git, make a commit: `git commit -m "Padroniza o JSON da API"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Why is the `erro.codigo` (`conflito`) safer for the page to decide by than the `erro.mensagem`?

Answer: because the code is a **stable contract**, and the message is text for people, which may be corrected, rewritten or translated at any moment. If the page decides by the message, any wording tweak breaks it, and the defect only shows up when someone trips over it. The code changes only when the API really changes, and a change like that is agreed on. The rule: **code for machines, message for people**.

## // Module summary

- [ ] I know why responses with different formats weigh on the page's code.
- [ ] I know how to design a success envelope (`dados` and `meta`) and an error one (`erro` and `meta`).
- [ ] I know how to convert names to camelCase with `alias_generator` and `populate_by_name`.
- [ ] I know how to create a generic envelope model and declare it in the `response_model`.
- [ ] I know how to concentrate the building of errors in a single place, with stable codes.
- [ ] I know how to adapt `api.js` to unwrap the envelope, and decide by the error's code.
- [ ] I know that changing the format of an API with clients requires agreement, and generally versioning.

---

**Next module:** `17-testing-the-integration.md`, a bonus module: how to check both ends automatically.

`Study Material // Coffee & Code`

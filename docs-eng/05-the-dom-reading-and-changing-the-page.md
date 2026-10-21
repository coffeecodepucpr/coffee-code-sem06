# Module 05, The DOM: Reading and Changing the Page

[Português](../docs/05-o-dom-ler-e-mudar-a-pagina.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

In Module 04 you saw the language. Now, the bridge between it and the screen: the **DOM**. It is through the DOM that JavaScript reads what the person typed, reacts to a click and writes onto the page the data the API returned. There is also a security concern here, the most important thing in this module, about how to write data that comes from outside.

## // The problem: outside data is not trustworthy

The list of groups comes from the API, and the API receives whatever people type. If someone creates a group named `<img src=x onerror=alert(1)>` and the page writes that name onto the screen the wrong way, the browser will not show the text: it will **run** the code hidden in it. That attack is called XSS, and it is born from one careless line of code. Writing to the page safely is part of the craft of anyone who integrates systems.

## // What the DOM is

> **DOM: IN SIMPLE WORDS**
> *Document Object Model* is the representation of the page as a tree of objects that JavaScript can read and change. Each HTML element (a heading, a list, a button) becomes an object, and changing the object changes what appears on screen.

This week's page (`index.html`) has elements each with an `id`, which the JavaScript uses to find them:

| `id` | What it is |
|---|---|
| `estado-api` | The "API conectada" or "API fora do ar" notice |
| `busca` and `filtro-materia` | The search box and the subject filter |
| `mensagem` | The message area (loading, error, success) |
| `lista-grupos` | The list where the group cards show up |
| `anterior`, `proxima` and `pagina-atual` | The pagination buttons and text |
| `form-grupo` | The create and edit form |
| `nome`, `materia`, `limite` and `descricao` | The form fields |
| `erro-nome`, `erro-materia`, `erro-limite` and `erro-descricao` | Where each field's error shows up |
| `salvar` and `cancelar` | The form buttons |

## // Reading and changing elements

The examples below were run in an environment that simulates the browser (`jsdom`), and the outputs are the real ones.

```js
const titulo = document.getElementById("titulo");
console.log("lendo:", titulo.textContent, "|",
            document.querySelector("#lista").tagName, "|",
            document.querySelectorAll("li").length, "li");
titulo.textContent = "Grupos de estudo";
console.log("mudando:", document.getElementById("titulo").textContent);
```

```
lendo: Grupos | UL | 0 li
mudando: Grupos de estudo
```

| Method | What it does |
|---|---|
| `document.getElementById("x")` | Finds the element by its `id` |
| `document.querySelector("#x")` | Finds the first element matching a CSS selector |
| `document.querySelectorAll("li")` | Finds all the matching ones, in a list |
| `elemento.textContent` | Reads or writes the element's **text** |
| `elemento.dataset.estado` | Reads or writes the `data-estado` attribute |

## // Creating elements

To build the list of groups, the page creates one element per group and puts it into the list:

```js
const lista = document.getElementById("lista");
for (const nome of ["Cálculo", "Redes"]) {
  const li = document.createElement("li");
  li.textContent = nome;
  lista.append(li);
}
console.log("criados:", lista.children.length,
            [...lista.children].map((li) => li.textContent));
lista.replaceChildren();
console.log("depois de replaceChildren:", lista.children.length);
```

```
criados: 2 [ 'Cálculo', 'Redes' ]
depois de replaceChildren: 0
```

The pattern is always the same: **create** (`createElement`), **fill** (`textContent`), **place** (`append`). And, before redrawing the list, `replaceChildren()` with no arguments empties it.

## // The security concern: textContent, not innerHTML

There is another way to write into an element, `innerHTML`, which interprets the text as **HTML**. See the difference with the dangerous name, in real runs:

```js
const perigoso = "<img src=x onerror=alert(1)>";

const a = document.createElement("li"); a.innerHTML = perigoso;
// innerHTML criou um <img>? true  | texto visível: ""

const b = document.createElement("li"); b.textContent = perigoso;
// textContent criou um <img>? false
// texto visível: "<img src=x onerror=alert(1)>"
```

`innerHTML` turned the text into a **real element**, the `<img>` (and, in a browser, its `onerror` would have been run), and the visible text ended up empty. `textContent` treated everything as text: the name shows up on screen exactly as it was typed. The HTML it generates shows why, because it "escapes" the symbols:

```
&lt;img src=x onerror=alert(1)&gt;
```

> **GOLDEN RULE**
> Data coming from the API, from a form or from anywhere outside your code goes onto the page with `textContent`, never with `innerHTML`. This week's page test checks that: it creates a group with the name above, and verifies that no `<img>` element shows up in the list.

## // Events

An **event** is something that happens on the page: a click, a key, a form submission. JavaScript registers a function to be called when the event occurs:

```js
const botao = document.createElement("button");
let cliques = 0;
botao.addEventListener("click", () => { cliques += 1; });
// depois de dois cliques: cliques registrados: 2
```

This week's events:

| Event | On which element | What it is for |
|---|---|---|
| `click` | Buttons | Edit, delete, previous and next page |
| `submit` | The form | Send the new group or the edit |
| `input` | The search box | Search as the person types |
| `change` | The subject filter | Filter when the choice changes |

### > Submitting a form

A form's `submit` has a default behaviour: the browser **reloads the page**. On a page that talks to the API, that would wipe the state. That is why the handler's first step is `evento.preventDefault()`:

```js
formulario.addEventListener("submit", (e) => {
  e.preventDefault();
  // ...ler os campos e chamar a API
});
```

```
submit: enviou: Redes na unha | preventDefault chamado: true
```

## // A field's value is always text

Everything you read from a field (`input.value`) is **text**, even in a numeric field. Converting is up to you, and it has traps:

```
typeof document.getElementById("nome").value  ->  string
Number("10")   ->  10
Number("")     ->  0
Number("abc")  ->  NaN
```

An empty field becomes `0`, and text that is not a number becomes `NaN`. That is why this week's page converts with `Number(...)` and **lets the API validate**: if the limit is `0` or `NaN`, the response is a `422`, and the message shows up on the right field (Module 11).

## // Good example × bad example

**Bad example**: building the list with `innerHTML` and outside data:

```js
lista.innerHTML += `<li>${grupo.nome_grupo}</li>`;
```

A name with HTML inside becomes an element, and the page is left vulnerable to XSS.

**Good example**: creating the element and using `textContent`:

```js
const item = document.createElement("li");
item.textContent = grupo.nome_grupo;
lista.append(item);
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| `Cannot read properties of null` | `getElementById` did not find the element (the `id` is wrong, or the script ran before the page loaded) | Check the `id` and use `type="module"`, which only runs after the page has been read |
| The page reloads when the form is submitted | `evento.preventDefault()` was missing | Add it as the handler's first line |
| The list duplicates on every search | The new items were appended to the old ones | Call `replaceChildren()` before redrawing |
| A numeric field arrives as text | `input.value` is always text | Convert with `Number(...)` |
| A click calls the function right away, not on the click | It was written as `addEventListener("click", funcao())` | Pass the function, without the parentheses: `addEventListener("click", funcao)` |
| The API's text shows up with odd symbols | `textContent` was used on something that was already HTML (or the other way round) | For outside data, `textContent` is correct |

## // Guided practice

1. Open `frontend-inicial/index.html` through a server (Module 08) and, in the console, run `document.getElementById("mensagem")` to see the element.
2. Write `document.getElementById("mensagem").textContent = "Olá!"` and watch the change on screen.
3. Create three `<li>` elements with `createElement` and put them into `#lista-grupos`. Then empty the list with `replaceChildren()`.
4. Put the text `<b>negrito</b>` into one item with `innerHTML` and into another with `textContent`, and compare what shows up.
5. Register a `click` on a button you created and check the counter.

## // Practice on your own

> **CHALLENGE**
> Write a function `mostrarGrupos(grupos)` that takes an array of objects with `nome_grupo` and `max_participantes`, empties `#lista-grupos` and creates, for each group, an `<li>` with the text `Nome (até N participantes)`. Test it with a group whose name is `<b>teste</b>` and confirm that it shows up as text.

## // Applying it to this week's project

1. Copy `example/frontend-inicial` to `projeto-fullstack/frontend` and check that `index.html` has every `id` from this module's table.
2. In `app.js`, create the function `mostrarMensagem(texto)` that writes into the `#mensagem` element. It will be used for the rest of the week.
3. If you track the project with Git, make a commit: `git commit -m "Adiciona a página inicial e a função de mensagem"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> Why is `textContent` safe for API data, and `innerHTML` is not? What does each one do with the `<` symbol?

Answer: `textContent` treats everything it receives as **plain text**: the `<` shows up on screen as a symbol, and no element is created. `innerHTML` treats the content as **HTML**: a `<` opens a tag, and the browser creates elements (and runs their event attributes). Since content coming from outside may have been written by anyone, only `textContent` guarantees that it never becomes code.

## // Module summary

- [ ] I know what the DOM is and how to find elements by `id` and by selector.
- [ ] I know how to create elements, fill them with `textContent` and put them on the page.
- [ ] I know how to empty a list with `replaceChildren()`.
- [ ] I know why outside data goes in with `textContent`, and never with `innerHTML`.
- [ ] I know how to register events (`click`, `submit`, `input`, `change`) and use `preventDefault()`.
- [ ] I know that a field's value is always text and how to convert it with `Number(...)`.

---

**Next module:** `06-async-promises-and-async-await.md`, the page already knows how to move. What is left is learning to wait for a response that takes time.

`Study Material // Coffee & Code`

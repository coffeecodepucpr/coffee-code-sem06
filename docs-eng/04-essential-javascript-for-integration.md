# Module 04, Essential JavaScript for Integration

[Português](../docs/04-javascript-essencial-para-integrar.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

The page you are about to build is written in **JavaScript**, the language that runs inside the browser. This module is not a JavaScript course: it introduces only what integration requires, in the order in which it will come up. If you already program in JavaScript, you can skim the boxes and move on to Module 05.

## // The problem: the page needs to think

HTML describes the page and CSS makes it look good, but neither of them **does** anything. To ask the API for data, hold the state (which page, which search), react to clicks and show messages, you need a programming language. JavaScript is the only one the browser runs on its own.

## // Where JavaScript runs

The fastest way to test a line is the browser's **console**: open the tools (the **F12** key) and pick the **Console** tab. Everything you type there is run right away, and `console.log(...)` writes results there. The examples below were run in Node, an environment that runs the same JavaScript outside the browser, and the outputs shown are the real ones.

On the page, the code lives in a `.js` file loaded by the HTML:

```html
<script type="module" src="app.js"></script>
```

The `type="module"` matters: it lets you split the code into several files that import each other (see the last section of this module).

## // Values, variables and text

```js
const nome = "Cálculo I";
let vagas = 6;
vagas = vagas + 1;
console.log(`Grupo ${nome} tem ${vagas} vagas`);
```

```
Grupo Cálculo I tem 7 vagas
```

| Keyword | Meaning |
|---|---|
| `const` | A variable that **will not be reassigned**. This is the default choice |
| `let` | A variable that will be reassigned |
| `` `text ${value}` `` | Text between backticks, which inserts values with `${ }` |

## // Objects and arrays

An **object** holds named fields, and an **array** holds a list. The API's JSON is made of exactly that:

```js
const grupo = { grupo_id: 3, nome_grupo: "Modelagem e SQL", descricao: null };
console.log(
  grupo.nome_grupo, grupo["grupo_id"], grupo.descricao ?? "sem descrição"
);
```

```
Modelagem e SQL 3 sem descrição
```

The `??` returns the value on the right when the one on the left is `null` or `undefined`. Arrays have methods that integration uses all the time:

```js
const grupos = [
  { nome: "A", vagas: 6 }, { nome: "B", vagas: 2 }, { nome: "C", vagas: 8 },
];
console.log(grupos.filter((g) => g.vagas >= 6).map((g) => g.nome));
console.log(grupos.find((g) => g.nome === "B"),
            grupos.find((g) => g.nome === "Z"));
```

```
[ 'A', 'C' ]
{ nome: 'B', vagas: 2 } undefined
```

| Method | What it does |
|---|---|
| `filter` | Returns only the items that pass a test |
| `map` | Transforms each item and returns the new list |
| `find` | Returns the first item that passes the test, or `undefined` |

And **destructuring** pulls fields out of an object in one line:

```js
const { nome: n, vagas: v } = grupos[0];
console.log(n, v);
```

```
A 6
```

## // Functions

The snippet `(g) => g.vagas >= 6` is an **arrow function**, a small, nameless function. The two forms below are equivalent:

```js
function dobro(x) { return x * 2; }
const triplo = (x) => x * 3;
console.log([1, 2, 3].map(triplo));
```

```
[ 3, 6, 9 ]
```

## // Comparisons and "falsy" values

In JavaScript, `==` converts types before comparing, and `===` does not. Use `===` **always**:

```js
console.log(0 == "", 0 === "", null == undefined, null === undefined);
console.log(typeof 5, typeof "x", typeof null,
            typeof undefined, typeof {}, typeof []);
console.log(Boolean(0), Boolean(""), Boolean(null),
            Boolean(undefined), Boolean([]), Boolean("0"));
```

```
true false true false
number string object undefined object object
false false false false true true
```

Two historical surprises: `typeof null` is `"object"`, and an empty array (`[]`) counts as **true**. The values that count as falsy in an `if` are `0`, empty text, `null`, `undefined` and `NaN`. Everything else counts as true, including `"0"` and `[]`.

## // JSON and addresses

JSON is the API's text format, and JavaScript reads and writes it with two methods:

```js
console.log(JSON.stringify(grupo));
console.log(JSON.parse('{"a":1,"b":[true,null]}'));
```

```
{"grupo_id":3,"nome_grupo":"Modelagem e SQL","descricao":null}
{ a: 1, b: [ true, null ] }
```

Text that is not valid JSON makes `JSON.parse` throw an error (this is Node's message, and the wording varies between browsers):

```
SyntaxError: Unexpected token 'i', "isto nao e json" is not valid JSON
```

To build the `?key=value` part of an address without getting the symbols and accents wrong, use `URLSearchParams`:

```js
const params = new URLSearchParams({ limit: 4, offset: 0, q: "prática" });
console.log(params.toString());
```

```
limit=4&offset=0&q=pr%C3%A1tica
```

It encodes the `á` as `%C3%A1` (an address only accepts certain characters) and joins the pairs with `&`.

## // Modules: splitting the code into files

A `.js` file loaded with `type="module"` can **export** what it wants to share and **import** what it needs from other files:

```js
// api.js
export const API_URL = "http://127.0.0.1:8000";
export async function listarMaterias() { /* ... */ }

// app.js
import * as api from "./api.js";
import { API_URL } from "./api.js";
```

Each module has its own scope: a variable from `api.js` only exists in `app.js` if it is exported and imported. This week's page uses three files: `api.js` (talks to the API), `ui.js` (touches the page) and `app.js` (joins the two). Module 14 shows the full design.

> **IF YOU ALREADY PROGRAM IN PYTHON (OPTIONAL)**
> If you know Python, the correspondences help: JavaScript's object is the dictionary, the array is the list, `filter` and `map` play the role of list comprehensions, and backticks with `${ }` are f-strings. If you do not know Python, ignore this box.

## // Good example × bad example

**Bad example**: comparing with `==` and building the address by hand:

```js
if (resposta.status == "200") { /* ... */ }
const url = API + "/grupos?q=" + busca + "&limit=" + limite;
```

The `==` masks differences between number and text, and concatenation breaks if the search contains `&`, `#` or accents.

**Good example**: `===` and `URLSearchParams`:

```js
if (resposta.status === 200) { /* ... */ }
const parametros = new URLSearchParams({ q: busca, limit: limite });
const url = `${API}/grupos?${parametros}`;
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| `x is not defined` | The variable does not exist in that scope (or was typed wrong) | Check the name and the `import`/`export` |
| `Assignment to constant variable` | You tried to reassign a `const` | Use `let`, if the value really changes |
| `Cannot read properties of undefined` | An expected object is `undefined` | Check where the value comes from, and use `?.` or an `if` |
| `Unexpected token ... in JSON` | The text is not valid JSON | Look at the text: it may be an HTML error page |
| Building the address by concatenation | It is the shortest path | Use `URLSearchParams` |
| `import` does not work | `type="module"` is missing from the `<script>`, or the files are not served over `http` | Use `type="module"` and serve the page (Module 08) |

## // Guided practice

1. Open the browser's console (F12, Console tab) and test this module's lines, one by one.
2. Create an array of five groups with `nome` and `vagas`. Use `filter` for the ones with more than 4 openings and `map` for just the names.
3. Write an arrow function `descrever(grupo)` that returns text like `Redes na unha: 6 vagas`.
4. Use `JSON.stringify` on an object and `JSON.parse` on the result. Compare the two.
5. Build, with `URLSearchParams`, the address `http://127.0.0.1:8000/grupos?...` with `q`, `limit` and `offset`.

## // Practice on your own

> **CHALLENGE**
> Given the array `[{nome: "Redes", vagas: 0}, {nome: "SQL", vagas: 3}, {nome: "Cálculo", vagas: 5}]`, write a single expression that returns the text `SQL, Cálculo` (the names of the groups with openings, separated by a comma). Hint: `filter`, `map` and the `join(", ")` method.

## // Applying it to this week's project

1. In `projeto-fullstack/frontend`, create a file `rascunho.js` with the guided practice tests and run it with `node rascunho.js`, if you have Node, or paste the snippets into the browser console.
2. Write down in `README.md` which of these features (`filter`, `map`, `find`, `URLSearchParams`, `JSON`, modules) you think you will use to list groups.
3. If you track the project with Git, make a commit: `git commit -m "Pratica o JavaScript essencial"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> `if (grupo.descricao)` treats the description `""` (empty text) and the description `null` in the same way. When is that a problem, and when is it exactly what you want?

Answer: both values count as "falsy", so the `if` treats them alike. To **show the description on screen**, that is exactly what you want: with empty text or `null`, there is nothing to display. It would be a problem if the difference mattered, for example to know whether the person **cleared** the description (`null`) or **never filled it in**. In that case, compare explicitly: `grupo.descricao === null`.

## // Module summary

- [ ] I know how to use `const` and `let`, and backtick text with `${ }`.
- [ ] I know how to read object fields and use `filter`, `map` and `find` on arrays.
- [ ] I know how to write arrow functions and use destructuring.
- [ ] I know why to use `===`, and which values count as falsy.
- [ ] I know how to convert between text and object with `JSON.stringify` and `JSON.parse`.
- [ ] I know how to build address parameters with `URLSearchParams`.
- [ ] I know how to export and import between files with `type="module"`.

---

**Next module:** `05-the-dom-reading-and-changing-the-page.md`, the language is introduced. Now, how it touches the page.

`Study Material // Coffee & Code`

# Module 06, Async: Promises and async/await

[Português](../docs/06-assincrono-promises-e-async-await.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Before you start

Asking the API for data takes time: the request travels, the server works, the response comes back. Meanwhile, the page has to stay alive. JavaScript solves this with **asynchronous** code, and it is the most confusing subject for beginners. This module explains it step by step, with real outputs, because the next module's `fetch` depends on it.

## // The problem: waiting without freezing

Imagine JavaScript made the request and **stopped** until the response arrived. During that wait, the whole page would freeze: no click would respond, no animation would move. If the API took five seconds, the page would be dead for five seconds. The browser avoids that in a different way: it **starts** the request and moves on, and **comes back** to the code when the response arrives.

## // Synchronous and asynchronous code

```js
console.log("1: início do script");
setTimeout(() => console.log("4: setTimeout de 0 ms"), 0);
Promise.resolve().then(() => console.log("3: promise já resolvida"));
console.log("2: fim do script");
```

```
1: início do script
2: fim do script
3: promise já resolvida
4: setTimeout de 0 ms
```

The order of the messages is the module's lesson: the script reads **every line from top to bottom** first (1 and 2). Only afterwards, with the stack free, does the browser run what was left waiting: the promises (3) and, after them, the timers (4). Nothing waits for anything: what is asynchronous is **scheduled** for later.

## // Promise

> **PROMISE: IN SIMPLE WORDS**
> It is an object that represents a value that **does not exist yet, but will** (or the reason it did not). It is in one of three states: pending, fulfilled (with a value) or rejected (with an error). Whoever wants the value asks with `.then(...)`, and whoever wants the error asks with `.catch(...)`.

`fetch` returns a Promise: the request was started, and the response comes later.

## // async and await

Chaining `.then` works, but the code becomes hard to read. The `async` and `await` syntax writes the same behaviour top to bottom, as if it were synchronous:

```js
const esperar = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function buscar() {
  console.log("pedindo...");
  await esperar(100);
  console.log("chegou");
  return 42;
}

buscar().then((valor) => console.log("valor recebido:", valor));
console.log("a linha seguinte NÃO esperou");
```

```
pedindo...
a linha seguinte NÃO esperou
chegou
valor recebido: 42
```

Two rules:

- `await` can only be used **inside an** `async` **function** (and, in browser modules, at the top level of the file as well).
- Inside the function, `await` **pauses only that function**, waiting for the Promise. The rest of the page keeps working, and that is why `"a linha seguinte NÃO esperou"` shows up before `chegou`.

An `async` function **always returns a Promise**, even if you write `return 42`: whoever calls it needs to use `await` or `.then`.

## // Handling errors

A Promise can be **rejected**. With `await`, the error becomes an ordinary exception, caught with `try` and `catch`:

```js
async function falha() { await esperar(10); throw new Error("o servidor caiu"); }

try { await falha(); } catch (erro) { console.log("capturado:", erro.message); }
falha().catch((e) => console.log("com .catch:", e.message));
```

```
capturado: o servidor caiu
com .catch: o servidor caiu
```

Both ways catch the same error. If nobody catches it, it goes up unhandled and shows up in the console as an unhandled error, leaving the screen with no explanation: on this week's page, every API call sits inside a `try` and `catch`.

## // In sequence or in parallel

Two requests that **do not depend on each other** do not need to wait for one another:

```js
await esperar(100); await esperar(100); await esperar(100);   // em sequência
await Promise.all([esperar(100), esperar(100), esperar(100)]);   // em paralelo
```

```
em sequência: cerca de 300 ms
em paralelo: cerca de 100 ms
```

`Promise.all` takes a list of promises and returns a single one, fulfilled when **all** of them finish. On this week's page, it can load the subjects and the groups at the same time, if you want. (The final code loads them one after the other, for clarity.)

## // Good example × bad example

**Bad example**: forgetting the `await`:

```js
// sem await: isto é uma Promise, e não a lista
const grupos = listarGrupos();
console.log(grupos.length);          // undefined
```

`grupos` is not the list, it is a **pending Promise**. Any use that assumes a list gives `undefined` or an error.

**Good example**: `await` and `try`/`catch`:

```js
try {
  const grupos = await listarGrupos();
  mostrarGrupos(grupos);
} catch (erro) {
  mostrarMensagem("Não foi possível carregar os grupos.");
}
```

## // Common mistakes

| Mistake | Why it happens | How to fix it |
|---|---|---|
| Getting `Promise { <pending> }` instead of the data | The `await` was missing | Add `await` (inside an `async` function) |
| `await is only valid in async function` | The `await` is in an ordinary function | Declare the function with `async` |
| The data shows up out of order | One piece of code depends on another's result, but did not wait | Use `await` in the order the dependency exists |
| The error disappears, and the screen explains nothing | The Promise was rejected, with no `catch` | Put the `await` inside `try` and `catch` |
| Two independent requests take twice as long | They were awaited in sequence | Use `Promise.all` |
| Using the result "right after" starting the request | The following code does not wait | Put whatever depends on the result **after** the `await` |

## // Guided practice

1. Paste the first example (order 1, 2, 3, 4) into the console and check the order of the messages.
2. Write the `esperar(ms)` function and an `async` function that waits 200 ms and returns some text. Call it with `.then` and then with `await`.
3. Write a function that throws an error after 50 ms and catch it with `try` and `catch`.
4. Measure, with `performance.now()`, the time of three waits in sequence and in parallel.
5. Remove the `await` from an example and watch what gets printed instead.

## // Practice on your own

> **CHALLENGE**
> Write an `async` function called `carregarTudo()` that waits 100 ms to simulate the subjects and 150 ms to simulate the groups, **in parallel**, and returns `{ materias, grupos }`. Confirm with `performance.now()` that the total time is close to 150 ms, not 250 ms.

## // Applying it to this week's project

1. In the page's `app.js`, write `async function iniciar()` with a `console.log("página iniciada")` inside it and call it at the end of the file.
2. Leave a comment above the function with the rule: "toda chamada à API vai dentro de try/catch".
3. If you track the project with Git, make a commit: `git commit -m "Cria a função assíncrona de início da página"`.

## // Checkpoint

> **BEFORE MOVING ON, THINK ABOUT THIS**
> In `buscar().then(...); console.log("depois");`, which message shows up first: the one inside the function, after the `await`, or the "depois" one? Why?

Answer: the "depois" one. The `buscar()` call runs the function up to the first `await`, returns a pending Promise and **leaves**, and the script continues on the next line. What comes after the `await` only runs when the wait is over, at a later moment. It is the proof that `await` pauses the function, not the page.

## // Module summary

- [ ] I know why the browser does not "stand still waiting" for a response.
- [ ] I know the order in which synchronous code, promises and timers run.
- [ ] I know what a Promise is and its three states.
- [ ] I know how to use `async` and `await`, and that an `async` function always returns a Promise.
- [ ] I know how to handle errors with `try` and `catch`.
- [ ] I know how to use `Promise.all` for independent waits.

---

**Next module:** `07-fetch-the-first-request.md`, with the groundwork ready, it is time for the first real request to the API.

`Study Material // Coffee & Code`

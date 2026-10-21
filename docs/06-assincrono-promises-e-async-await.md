# Módulo 06, Assíncrono: Promises e async/await

Português · [English](../docs-eng/06-async-promises-and-async-await.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

Pedir dados à API leva tempo: o pedido viaja, o servidor trabalha, a resposta volta. Enquanto isso, a página precisa continuar viva. O JavaScript resolve isso com código **assíncrono**, e é o assunto mais confuso para quem está começando. Este módulo o explica passo a passo, com saídas reais, porque o `fetch` do próximo módulo depende dele.

## // O problema: esperar sem travar

Imagine que o JavaScript fizesse o pedido e **parasse** até a resposta chegar. Durante essa espera, a página inteira congelaria: nenhum clique responderia, nenhuma animação andaria. Se a API demorasse cinco segundos, a página ficaria cinco segundos morta. O navegador evita isso de um jeito diferente: ele **inicia** o pedido e segue em frente, e **volta** ao código quando a resposta chega.

## // Código síncrono e assíncrono

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

A ordem das mensagens é a lição do módulo: o script lê **todas as linhas de cima a baixo** primeiro (1 e 2). Só depois, com a pilha livre, o navegador executa o que ficou esperando: as promessas (3) e, depois delas, os temporizadores (4). Nada espera por nada: o que é assíncrono é **agendado** para depois.

## // Promise

> **PROMISE: EM PALAVRAS SIMPLES**
> É um objeto que representa um valor que **ainda não existe, mas vai existir** (ou o motivo de não ter existido). Ela está em um de três estados: pendente, cumprida (com um valor) ou rejeitada (com um erro). Quem quer o valor pede com `.then(...)`, e quem quer o erro pede com `.catch(...)`.

O `fetch` devolve uma Promise: o pedido foi iniciado, e a resposta vem depois.

## // async e await

Encadear `.then` funciona, mas o código fica difícil de ler. A sintaxe `async` e `await` escreve o mesmo comportamento de cima para baixo, como se fosse síncrono:

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

Duas regras:

- `await` só pode ser usado **dentro de uma função** `async` (e, nos módulos do navegador, também no nível do arquivo).
- Dentro da função, o `await` **pausa só aquela função**, esperando a Promise. O resto da página continua funcionando, e é por isso que `"a linha seguinte NÃO esperou"` aparece antes de `chegou`.

Uma função `async` **sempre devolve uma Promise**, mesmo que você escreva `return 42`: quem a chama precisa usar `await` ou `.then`.

## // Tratando erros

Uma Promise pode ser **rejeitada**. Com `await`, o erro vira uma exceção comum, que se captura com `try` e `catch`:

```js
async function falha() { await esperar(10); throw new Error("o servidor caiu"); }

try { await falha(); } catch (erro) { console.log("capturado:", erro.message); }
falha().catch((e) => console.log("com .catch:", e.message));
```

```
capturado: o servidor caiu
com .catch: o servidor caiu
```

Os dois jeitos pegam o mesmo erro. Se ninguém o capturar, ele sobe sem tratamento e aparece no console como um erro não tratado, e a tela fica sem explicação: na página desta semana, toda chamada à API está dentro de um `try` e `catch`.

## // Em sequência ou em paralelo

Dois pedidos que **não dependem um do outro** não precisam esperar um pelo outro:

```js
await esperar(100); await esperar(100); await esperar(100);   // em sequência
await Promise.all([esperar(100), esperar(100), esperar(100)]);   // em paralelo
```

```
em sequência: cerca de 300 ms
em paralelo: cerca de 100 ms
```

O `Promise.all` recebe uma lista de promessas e devolve uma só, cumprida quando **todas** terminam. Na página desta semana, ele serve para carregar as matérias e os grupos ao mesmo tempo, se você quiser. (O código final os carrega um após o outro, pela clareza.)

## // Bom exemplo × mau exemplo

**Mau exemplo**: esquecer o `await`:

```js
// sem await: isto é uma Promise, e não a lista
const grupos = listarGrupos();
console.log(grupos.length);          // undefined
```

`grupos` não é a lista, é uma **Promise pendente**. Qualquer uso que presuma uma lista dá `undefined` ou um erro.

**Bom exemplo**: `await` e `try`/`catch`:

```js
try {
  const grupos = await listarGrupos();
  mostrarGrupos(grupos);
} catch (erro) {
  mostrarMensagem("Não foi possível carregar os grupos.");
}
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| Receber `Promise { <pending> }` em vez dos dados | Faltou o `await` | Acrescente `await` (dentro de uma função `async`) |
| `await is only valid in async function` | O `await` está em uma função comum | Declare a função com `async` |
| Os dados aparecem fora de ordem | Um código depende do resultado de outro, mas não esperou | Use `await` na ordem em que a dependência existe |
| O erro some, e a tela não explica nada | A Promise foi rejeitada, sem `catch` | Coloque o `await` dentro de `try` e `catch` |
| Dois pedidos independentes demoram o dobro | Foram esperados em sequência | Use `Promise.all` |
| Usar o resultado "logo depois" de iniciar o pedido | O código seguinte não espera | Coloque o que depende do resultado **depois** do `await` |

## // Prática guiada

1. Cole o primeiro exemplo (ordem 1, 2, 3, 4) no console e confira a ordem das mensagens.
2. Escreva a função `esperar(ms)` e uma função `async` que espere 200 ms e devolva um texto. Chame-a com `.then` e depois com `await`.
3. Escreva uma função que lance um erro depois de 50 ms e capture-o com `try` e `catch`.
4. Meça, com `performance.now()`, o tempo de três esperas em sequência e em paralelo.
5. Tire o `await` de um exemplo e observe o que passa a ser impresso.

## // Pratique sozinho

> **DESAFIO**
> Escreva uma função `async` chamada `carregarTudo()` que espere 100 ms para simular as matérias e 150 ms para simular os grupos, **em paralelo**, e devolva `{ materias, grupos }`. Confirme com `performance.now()` que o tempo total é perto de 150 ms, e não de 250 ms.

## // Aplicando no projeto da semana

1. No `app.js` da página, escreva `async function iniciar()` com um `console.log("página iniciada")` dentro e chame-a no fim do arquivo.
2. Deixe um comentário em cima da função com a regra: "toda chamada à API vai dentro de try/catch".
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Cria a função assíncrona de início da página"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Em `buscar().then(...); console.log("depois");`, qual mensagem aparece primeiro: a de dentro da função, depois do `await`, ou a "depois"? Por quê?

Resposta: a "depois". A chamada `buscar()` executa a função até o primeiro `await`, devolve uma Promise pendente e **sai**, e o script continua na linha seguinte. O que está depois do `await` só roda quando a espera termina, em um momento posterior. É a prova de que o `await` pausa a função, e não a página.

## // Resumo do módulo

- [ ] Sei por que o navegador não "espera parado" por uma resposta.
- [ ] Sei a ordem em que o código síncrono, as promessas e os temporizadores executam.
- [ ] Sei o que é uma Promise e seus três estados.
- [ ] Sei usar `async` e `await`, e que uma função `async` sempre devolve uma Promise.
- [ ] Sei tratar erros com `try` e `catch`.
- [ ] Sei usar `Promise.all` para esperas independentes.

---

**Próximo módulo:** `07-fetch-o-primeiro-pedido.md`, com a base pronta, é hora do primeiro pedido de verdade à API.

`Material de Estudo // Coffee & Code`

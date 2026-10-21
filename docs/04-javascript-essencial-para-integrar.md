# Módulo 04, JavaScript Essencial para Integrar

Português · [English](../docs-eng/04-essential-javascript-for-integration.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

A página que você vai construir é escrita em **JavaScript**, a linguagem que roda dentro do navegador. Este módulo não é um curso de JavaScript: ele apresenta só o que a integração exige, na ordem em que vai aparecer. Quem já programa em JavaScript pode ler os quadros rapidamente e ir para o Módulo 05.

## // O problema: a página precisa pensar

O HTML descreve a página e o CSS a deixa bonita, mas nenhum dos dois **faz** nada. Para pedir dados à API, guardar o estado (qual página, qual busca), reagir a cliques e mostrar mensagens, é preciso uma linguagem de programação. O JavaScript é a única que o navegador executa por conta própria.

## // Onde o JavaScript roda

O jeito mais rápido de testar uma linha é o **console** do navegador: abra as ferramentas (tecla **F12**) e escolha a aba **Console**. Tudo o que você digitar ali é executado na hora, e `console.log(...)` escreve resultados lá. Os exemplos abaixo foram executados no Node, um ambiente que roda o mesmo JavaScript fora do navegador, e as saídas mostradas são as reais.

Na página, o código fica em um arquivo `.js` carregado pelo HTML:

```html
<script type="module" src="app.js"></script>
```

O `type="module"` é importante: ele permite dividir o código em vários arquivos que se importam entre si (veja a última seção deste módulo).

## // Valores, variáveis e texto

```js
const nome = "Cálculo I";
let vagas = 6;
vagas = vagas + 1;
console.log(`Grupo ${nome} tem ${vagas} vagas`);
```

```
Grupo Cálculo I tem 7 vagas
```

| Palavra | Significado |
|---|---|
| `const` | Uma variável que **não será reatribuída**. É a escolha padrão |
| `let` | Uma variável que será reatribuída |
| `` `texto ${valor}` `` | Um texto entre crases, que insere valores com `${ }` |

## // Objetos e arrays

Um **objeto** guarda campos nomeados, e um **array** guarda uma lista. O JSON da API é feito exatamente disso:

```js
const grupo = { grupo_id: 3, nome_grupo: "Modelagem e SQL", descricao: null };
console.log(
  grupo.nome_grupo, grupo["grupo_id"], grupo.descricao ?? "sem descrição"
);
```

```
Modelagem e SQL 3 sem descrição
```

O `??` devolve o valor da direita quando o da esquerda é `null` ou `undefined`. Os arrays têm métodos que a integração usa o tempo todo:

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

| Método | O que faz |
|---|---|
| `filter` | Devolve só os itens que passam em um teste |
| `map` | Transforma cada item e devolve a nova lista |
| `find` | Devolve o primeiro item que passa no teste, ou `undefined` |

E a **desestruturação** tira campos de um objeto em uma linha:

```js
const { nome: n, vagas: v } = grupos[0];
console.log(n, v);
```

```
A 6
```

## // Funções

O trecho `(g) => g.vagas >= 6` é uma **função de seta**, uma função pequena e sem nome. As duas formas a seguir são equivalentes:

```js
function dobro(x) { return x * 2; }
const triplo = (x) => x * 3;
console.log([1, 2, 3].map(triplo));
```

```
[ 3, 6, 9 ]
```

## // Comparações e valores "falsos"

Em JavaScript, `==` converte tipos antes de comparar, e `===` não. Use `===` **sempre**:

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

Duas surpresas históricas: `typeof null` é `"object"`, e um array vazio (`[]`) conta como **verdadeiro**. Os valores que valem como falsos em um `if` são `0`, texto vazio, `null`, `undefined` e `NaN`. Todo o resto vale como verdadeiro, incluindo `"0"` e `[]`.

## // JSON e endereços

O JSON é o formato de texto da API, e o JavaScript o lê e o escreve com dois métodos:

```js
console.log(JSON.stringify(grupo));
console.log(JSON.parse('{"a":1,"b":[true,null]}'));
```

```
{"grupo_id":3,"nome_grupo":"Modelagem e SQL","descricao":null}
{ a: 1, b: [ true, null ] }
```

Um texto que não é JSON válido faz o `JSON.parse` lançar um erro (esta é a mensagem do Node, e a redação varia entre navegadores):

```
SyntaxError: Unexpected token 'i', "isto nao e json" is not valid JSON
```

Para montar a parte `?chave=valor` de um endereço sem errar nos símbolos e nos acentos, use o `URLSearchParams`:

```js
const params = new URLSearchParams({ limit: 4, offset: 0, q: "prática" });
console.log(params.toString());
```

```
limit=4&offset=0&q=pr%C3%A1tica
```

Ele codifica o `á` como `%C3%A1` (o endereço só aceita certos caracteres) e junta os pares com `&`.

## // Módulos: dividir o código em arquivos

Um arquivo `.js` carregado com `type="module"` pode **exportar** o que quer compartilhar e **importar** o que precisa de outros arquivos:

```js
// api.js
export const API_URL = "http://127.0.0.1:8000";
export async function listarMaterias() { /* ... */ }

// app.js
import * as api from "./api.js";
import { API_URL } from "./api.js";
```

Cada módulo tem o seu próprio escopo: uma variável de `api.js` só existe em `app.js` se for exportada e importada. A página desta semana usa três arquivos: `api.js` (fala com a API), `ui.js` (mexe na página) e `app.js` (junta os dois). O módulo 14 mostra o desenho completo.

> **SE VOCÊ JÁ PROGRAMA EM PYTHON (OPCIONAL)**
> Se você conhece Python, as correspondências ajudam: o objeto do JavaScript é o dicionário, o array é a lista, `filter` e `map` fazem o papel das compreensões de lista, e as crases com `${ }` são as f-strings. Se você não conhece Python, ignore este quadro.

## // Bom exemplo × mau exemplo

**Mau exemplo**: comparar com `==` e montar o endereço à mão:

```js
if (resposta.status == "200") { /* ... */ }
const url = API + "/grupos?q=" + busca + "&limit=" + limite;
```

O `==` mascara diferenças entre número e texto, e a concatenação quebra se a busca tiver `&`, `#` ou acentos.

**Bom exemplo**: `===` e `URLSearchParams`:

```js
if (resposta.status === 200) { /* ... */ }
const parametros = new URLSearchParams({ q: busca, limit: limite });
const url = `${API}/grupos?${parametros}`;
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `x is not defined` | A variável não existe naquele escopo (ou foi digitada errado) | Confira o nome e o `import`/`export` |
| `Assignment to constant variable` | Tentou reatribuir uma `const` | Use `let`, se o valor realmente muda |
| `Cannot read properties of undefined` | Um objeto esperado é `undefined` | Confira de onde o valor vem, e use `?.` ou um `if` |
| `Unexpected token ... in JSON` | O texto não é JSON válido | Olhe o texto: pode ser uma página de erro HTML |
| Montar o endereço por concatenação | É o caminho mais curto | Use `URLSearchParams` |
| `import` não funciona | Faltou `type="module"` no `<script>`, ou os arquivos não são servidos por `http` | Use `type="module"` e sirva a página (Módulo 08) |

## // Prática guiada

1. Abra o console do navegador (F12, aba Console) e teste, uma a uma, as linhas deste módulo.
2. Crie um array de cinco grupos com `nome` e `vagas`. Use `filter` para os que têm mais de 4 vagas e `map` para só os nomes.
3. Escreva uma função de seta `descrever(grupo)` que devolva um texto como `Redes na unha: 6 vagas`.
4. Use `JSON.stringify` em um objeto e `JSON.parse` no resultado. Compare os dois.
5. Monte, com `URLSearchParams`, o endereço `http://127.0.0.1:8000/grupos?...` com `q`, `limit` e `offset`.

## // Pratique sozinho

> **DESAFIO**
> Dado o array `[{nome: "Redes", vagas: 0}, {nome: "SQL", vagas: 3}, {nome: "Cálculo", vagas: 5}]`, escreva uma única expressão que devolva o texto `SQL, Cálculo` (os nomes dos grupos com vagas, separados por vírgula). Dica: `filter`, `map` e o método `join(", ")`.

## // Aplicando no projeto da semana

1. Em `projeto-fullstack/frontend`, crie um arquivo `rascunho.js` com os testes da prática guiada e rode-o com `node rascunho.js`, se tiver o Node, ou cole os trechos no console do navegador.
2. Anote no `README.md` quais desses recursos (`filter`, `map`, `find`, `URLSearchParams`, `JSON`, módulos) você acha que vai usar para listar grupos.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Pratica o JavaScript essencial"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> O `if (grupo.descricao)` trata a descrição `""` (texto vazio) e a descrição `null` da mesma maneira. Quando isso é um problema, e quando é exatamente o que se quer?

Resposta: os dois valores valem como "falso", então o `if` os trata igual. Para **mostrar a descrição na tela**, é exatamente o que se quer: com texto vazio ou `null`, não há nada para exibir. Seria um problema se a diferença importasse, por exemplo, para saber se a pessoa **apagou** a descrição (`null`) ou **nunca preencheu**. Nesse caso, compare de forma explícita: `grupo.descricao === null`.

## // Resumo do módulo

- [ ] Sei usar `const` e `let`, e os textos com crases e `${ }`.
- [ ] Sei ler campos de objetos e usar `filter`, `map` e `find` em arrays.
- [ ] Sei escrever funções de seta e usar a desestruturação.
- [ ] Sei por que usar `===`, e quais valores valem como falsos.
- [ ] Sei converter entre texto e objeto com `JSON.stringify` e `JSON.parse`.
- [ ] Sei montar parâmetros de endereço com `URLSearchParams`.
- [ ] Sei exportar e importar entre arquivos com `type="module"`.

---

**Próximo módulo:** `05-o-dom-ler-e-mudar-a-pagina.md`, a linguagem está apresentada. Agora, como ela mexe na página.

`Material de Estudo // Coffee & Code`

# Módulo 05, O DOM: Ler e Mudar a Página

Português · [English](../docs-eng/05-the-dom-reading-and-changing-the-page.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

No Módulo 04 você viu a linguagem. Agora, a ponte entre ela e a tela: o **DOM**. É por ele que o JavaScript lê o que a pessoa digitou, reage a um clique e escreve na página os dados que a API devolveu. Há também um cuidado de segurança, o mais importante deste módulo, sobre como escrever dados que vêm de fora.

## // O problema: dados de fora não são confiáveis

A lista de grupos vem da API, e a API recebe o que as pessoas digitam. Se alguém criar um grupo chamado `<img src=x onerror=alert(1)>` e a página escrever esse nome na tela do jeito errado, o navegador não vai mostrar o texto: vai **executar** o código escondido nele. Esse ataque se chama XSS, e ele nasce de uma linha de código descuidada. Escrever na página com segurança é parte do ofício de quem integra.

## // O que é o DOM

> **DOM: EM PALAVRAS SIMPLES**
> *Document Object Model* é a representação da página como uma árvore de objetos que o JavaScript consegue ler e alterar. Cada elemento do HTML (um título, uma lista, um botão) vira um objeto, e mudar o objeto muda o que aparece na tela.

A página desta semana (`index.html`) tem elementos com um `id` cada um, que o JavaScript usa para encontrá-los:

| `id` | O que é |
|---|---|
| `estado-api` | O aviso "API conectada" ou "API fora do ar" |
| `busca` e `filtro-materia` | A caixa de busca e o filtro por matéria |
| `mensagem` | A área de mensagens (carregando, erro, sucesso) |
| `lista-grupos` | A lista onde os cartões dos grupos aparecem |
| `anterior`, `proxima` e `pagina-atual` | Os botões e o texto da paginação |
| `form-grupo` | O formulário de criar e editar |
| `nome`, `materia`, `limite` e `descricao` | Os campos do formulário |
| `erro-nome`, `erro-materia`, `erro-limite` e `erro-descricao` | Onde os erros de cada campo aparecem |
| `salvar` e `cancelar` | Os botões do formulário |

## // Ler e mudar elementos

Os exemplos abaixo foram executados em um ambiente que simula o navegador (o `jsdom`), e as saídas são as reais.

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

| Método | O que faz |
|---|---|
| `document.getElementById("x")` | Acha o elemento pelo `id` |
| `document.querySelector("#x")` | Acha o primeiro elemento que casa com um seletor CSS |
| `document.querySelectorAll("li")` | Acha todos que casam, em uma lista |
| `elemento.textContent` | Lê ou escreve o **texto** do elemento |
| `elemento.dataset.estado` | Lê ou escreve o atributo `data-estado` |

## // Criar elementos

Para montar a lista de grupos, a página cria um elemento por grupo e o coloca na lista:

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

O padrão é sempre o mesmo: **criar** (`createElement`), **preencher** (`textContent`), **colocar** (`append`). E, antes de redesenhar a lista, `replaceChildren()` sem argumentos a esvazia.

## // O cuidado de segurança: textContent, e não innerHTML

Existe outro jeito de escrever em um elemento, o `innerHTML`, que interpreta o texto como **HTML**. Veja a diferença com o nome perigoso, em execuções reais:

```js
const perigoso = "<img src=x onerror=alert(1)>";

const a = document.createElement("li"); a.innerHTML = perigoso;
// innerHTML criou um <img>? true  | texto visível: ""

const b = document.createElement("li"); b.textContent = perigoso;
// textContent criou um <img>? false
// texto visível: "<img src=x onerror=alert(1)>"
```

O `innerHTML` transformou o texto em um **elemento de verdade**, o `<img>` (e, em um navegador, o `onerror` dele seria executado), e o texto visível ficou vazio. O `textContent` tratou tudo como texto: o nome aparece na tela exatamente como foi digitado. O HTML que ele gera mostra o motivo, pois ele "escapa" os símbolos:

```
&lt;img src=x onerror=alert(1)&gt;
```

> **REGRA DE OURO**
> Dados que vêm da API, de um formulário ou de qualquer lugar fora do seu código vão para a página com `textContent`, nunca com `innerHTML`. O teste da página desta semana confere isso: ele cria um grupo com o nome acima, e verifica que nenhum elemento `<img>` aparece na lista.

## // Eventos

Um **evento** é algo que acontece na página: um clique, uma tecla, o envio de um formulário. O JavaScript registra uma função para ser chamada quando o evento ocorre:

```js
const botao = document.createElement("button");
let cliques = 0;
botao.addEventListener("click", () => { cliques += 1; });
// depois de dois cliques: cliques registrados: 2
```

Os eventos desta semana:

| Evento | Em que elemento | Para que serve |
|---|---|---|
| `click` | Botões | Editar, apagar, páginas anterior e próxima |
| `submit` | O formulário | Enviar o novo grupo ou a edição |
| `input` | A caixa de busca | Buscar enquanto a pessoa digita |
| `change` | O filtro de matéria | Filtrar quando a escolha muda |

### > O envio de um formulário

O `submit` de um formulário tem um comportamento padrão: o navegador **recarrega a página**. Em uma página que fala com a API, isso apagaria o estado. Por isso, o primeiro passo do tratador é `evento.preventDefault()`:

```js
formulario.addEventListener("submit", (e) => {
  e.preventDefault();
  // ...ler os campos e chamar a API
});
```

```
submit: enviou: Redes na unha | preventDefault chamado: true
```

## // O valor de um campo é sempre texto

Tudo que se lê de um campo (`input.value`) é **texto**, até em um campo numérico. A conversão é por sua conta, e tem armadilhas:

```
typeof document.getElementById("nome").value  ->  string
Number("10")   ->  10
Number("")     ->  0
Number("abc")  ->  NaN
```

Um campo vazio vira `0`, e um texto que não é número vira `NaN`. Por isso a página desta semana converte com `Number(...)` e **deixa a API validar**: se o limite for `0` ou `NaN`, a resposta é um `422`, e a mensagem aparece no campo certo (Módulo 11).

## // Bom exemplo × mau exemplo

**Mau exemplo**: montar a lista com `innerHTML` e dados de fora:

```js
lista.innerHTML += `<li>${grupo.nome_grupo}</li>`;
```

Um nome com HTML dentro vira elemento, e a página fica vulnerável a XSS.

**Bom exemplo**: criar o elemento e usar `textContent`:

```js
const item = document.createElement("li");
item.textContent = grupo.nome_grupo;
lista.append(item);
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `Cannot read properties of null` | O `getElementById` não achou o elemento (o `id` está errado, ou o script rodou antes de a página carregar) | Confira o `id` e use `type="module"`, que só executa depois que a página foi lida |
| A página recarrega ao enviar o formulário | Faltou `evento.preventDefault()` | Acrescente na primeira linha do tratador |
| A lista duplica a cada busca | Os itens novos foram acrescentados aos antigos | Chame `replaceChildren()` antes de redesenhar |
| Um campo numérico chega como texto | `input.value` é sempre texto | Converta com `Number(...)` |
| Um clique chama a função na hora, e não no clique | Foi escrito `addEventListener("click", funcao())` | Passe a função, sem os parênteses: `addEventListener("click", funcao)` |
| O texto da API aparece com símbolos estranhos | Foi usado `textContent` em algo que já era HTML (ou o contrário) | Para dados de fora, `textContent` está correto |

## // Prática guiada

1. Abra o `frontend-inicial/index.html` por meio de um servidor (Módulo 08) e, no console, rode `document.getElementById("mensagem")` para ver o elemento.
2. Escreva `document.getElementById("mensagem").textContent = "Olá!"` e veja a mudança na tela.
3. Crie três `<li>` com `createElement` e coloque-os em `#lista-grupos`. Depois esvazie a lista com `replaceChildren()`.
4. Coloque o texto `<b>negrito</b>` em um item com `innerHTML` e em outro com `textContent`, e compare o que aparece.
5. Registre um `click` em um botão criado por você e confira o contador.

## // Pratique sozinho

> **DESAFIO**
> Escreva uma função `mostrarGrupos(grupos)` que receba um array de objetos com `nome_grupo` e `max_participantes`, esvazie `#lista-grupos` e crie, para cada grupo, um `<li>` com o texto `Nome (até N participantes)`. Teste com um grupo cujo nome seja `<b>teste</b>` e confirme que ele aparece como texto.

## // Aplicando no projeto da semana

1. Copie `example/frontend-inicial` para `projeto-fullstack/frontend` e confira que o `index.html` tem todos os `id` da tabela deste módulo.
2. Crie, no `app.js`, a função `mostrarMensagem(texto)` que escreve no elemento `#mensagem`. Ela será usada o resto da semana.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Adiciona a página inicial e a função de mensagem"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Por que `textContent` é seguro para dados da API, e `innerHTML` não? O que cada um faz com o símbolo `<`?

Resposta: o `textContent` trata tudo o que recebe como **texto puro**: o `<` aparece na tela como um símbolo, e nenhum elemento é criado. O `innerHTML` trata o conteúdo como **HTML**: um `<` abre uma marcação, e o navegador cria elementos (e executa os atributos de evento deles). Como o conteúdo vindo de fora pode ter sido escrito por qualquer pessoa, só o `textContent` garante que ele jamais vire código.

## // Resumo do módulo

- [ ] Sei o que é o DOM e como achar elementos por `id` e por seletor.
- [ ] Sei criar elementos, preenchê-los com `textContent` e colocá-los na página.
- [ ] Sei esvaziar uma lista com `replaceChildren()`.
- [ ] Sei por que dados de fora vão com `textContent`, e nunca com `innerHTML`.
- [ ] Sei registrar eventos (`click`, `submit`, `input`, `change`) e usar `preventDefault()`.
- [ ] Sei que o valor de um campo é sempre texto e como converter com `Number(...)`.

---

**Próximo módulo:** `06-assincrono-promises-e-async-await.md`, a página já sabe se mexer. Falta aprender a esperar uma resposta que demora.

`Material de Estudo // Coffee & Code`

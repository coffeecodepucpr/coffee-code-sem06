# Módulo 10, Listando Grupos na Página

Português · [English](../docs-eng/10-listing-groups-on-the-page.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

Com o CORS resolvido, a página finalmente recebe a resposta da API. Este módulo transforma essa resposta em uma **lista na tela**, e vai além do caminho feliz: trata os momentos em que a lista ainda não chegou, está vazia, ou nem deveria ser mostrada porque a API falhou. É isso que separa uma página que "funciona na demonstração" de uma que o usuário consegue confiar.

## // O problema: uma tela que fica em silêncio

Uma lista que simplesmente aparece quando os dados chegam parece suficiente. Mas pense nos outros momentos: o que a pessoa vê **enquanto** a API responde? E se a busca não achar nada? E se a API estiver desligada? Uma tela que não diz nada nesses momentos parece quebrada, e a pessoa não tem como saber se deve esperar, tentar de novo ou desistir.

## // Os quatro estados da lista

<div align="center">
<img src="./assets/svg/estados-da-tela.svg" alt="Os estados da lista: carregando, sucesso, vazio e erro, e as duas origens do erro" width="640">
</div>

| Estado | O que a tela mostra | Quem cuida |
|---|---|---|
| **Carregando** | A mensagem "Carregando..." | `carregarGrupos()`, antes do pedido |
| **Sucesso** | Os cartões dos grupos e a paginação | `renderizarGrupos()` |
| **Vazio** | "Nenhum grupo encontrado." | `renderizarGrupos()`, com uma lista sem itens |
| **Erro** | Uma mensagem clara e o estado da API | `tratarErro()` |

Toda vez que a pessoa age (abre a página, busca, pagina), a lista passa por **carregando** e termina em um dos outros três.

## // A camada de API: listarGrupos

O pedido da lista fica no `api.js`. Ele monta os parâmetros com o `URLSearchParams` (Módulo 04) e lê o total de grupos do cabeçalho (o Módulo 13 explica o cabeçalho):

```js
export async function listarGrupos(
  { busca = "", materiaId = "", limite = 4, deslocamento = 0 } = {}
) {
  const parametros = new URLSearchParams({ limit: limite, offset: deslocamento });
  if (busca) parametros.set("q", busca);
  if (materiaId) parametros.set("materia_id", materiaId);

  const { dados, resposta } = await pedir(`/grupos?${parametros}`);
  const total = resposta.headers.get("X-Total-Count");
  if (total === null) {
    console.warn(
      "X-Total-Count não está visível. Confira o expose_headers do CORS na API."
    );
  }
  return { grupos: dados, total: total === null ? dados.length : Number(total) };
}
```

## // A camada de interface: renderizar

O `ui.js` não sabe nada de API: ele recebe dados prontos e escreve na página. Cada grupo vira um cartão, montado com `createElement` e `textContent`, como o Módulo 05 ensinou:

```js
export function renderizarGrupos(
  grupos, nomesDeMaterias, { aoEditar, aoApagar }
) {
  const lista = $("lista-grupos");
  lista.replaceChildren();

  if (grupos.length === 0) {
    const vazio = document.createElement("li");
    vazio.className = "vazio";
    vazio.textContent = "Nenhum grupo encontrado.";
    lista.append(vazio);
    return;
  }

  for (const g of grupos) {
    const item = document.createElement("li");
    item.className = "cartao";

    const titulo = document.createElement("h3");
    // textContent: o texto da API nunca vira HTML
    titulo.textContent = g.nome_grupo;
    // ...matéria, limite e descrição, no mesmo estilo...
  }
}
```

Três decisões a notar:

- A lista é **esvaziada** antes de cada desenho (`replaceChildren()`), para não acumular cartões.
- A lista vazia **não é um erro**: a API respondeu `200` sem itens, e a tela explica isso com uma frase.
- O nome da matéria vem de um `Map` (`nomesDeMaterias`) montado uma vez, a partir de `GET /materias`. O grupo só traz o `materia_id`, e mostrar um número seria inútil para a pessoa.

## // O orquestrador: carregarGrupos

O `app.js` junta as duas camadas, e é onde moram os estados:

```js
// numera os pedidos de listagem, para descartar respostas atrasadas
let ultimoPedido = 0;

async function carregarGrupos() {
  const numero = ++ultimoPedido;
  ui.mostrarMensagem("Carregando...");
  try {
    const { grupos, total } = await api.listarGrupos({
      busca: estado.busca,
      materiaId: estado.materiaId,
      limite: TAMANHO_DA_PAGINA,
      deslocamento: (estado.pagina - 1) * TAMANHO_DA_PAGINA,
    });
    // já existe um pedido mais novo: esta resposta é velha
    if (numero !== ultimoPedido) return;

    const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
    if (estado.pagina > totalDePaginas) {
      estado.pagina = totalDePaginas;
      return carregarGrupos();
    }

    estado.total = total;
    ui.mostrarEstadoApi("conectada");
    ui.renderizarGrupos(grupos, estado.nomesDeMaterias, {
      aoEditar: iniciarEdicao,
      aoApagar: apagar,
    });
    ui.renderizarPaginacao({ pagina: estado.pagina, totalDePaginas, total });
    ui.mostrarMensagem("");
  } catch (erro) {
    if (numero !== ultimoPedido) return;
    tratarErro(erro);
  }
}
```

Duas linhas pedem explicação.

### > O número do pedido: respostas fora de ordem

Imagine a pessoa clicando em **Próxima** e, logo em seguida, escolhendo uma matéria no filtro. Dois pedidos estão no ar. Se o **primeiro** (mais velho) demorar mais e chegar **depois** do segundo, ele sobrescreve a tela com dados que a pessoa já não pediu. É uma condição de corrida, e é real.

A solução é numerar cada pedido (`++ultimoPedido`) e, ao receber a resposta, conferir se ela ainda é a **mais nova** (`numero !== ultimoPedido`). Se não for, ela é descartada. Esse comportamento foi verificado em um teste que atrasa de propósito a resposta velha: com a conferência, a tela mostra a resposta nova. **Sem** a conferência (testado ao remover a linha), o teste falha, o que mostra que ele detecta o defeito de verdade.

### > A página que deixou de existir

Se a pessoa estiver na última página e apagar o único item dela, o total diminui e a página não existe mais. Sem o cuidado, a tela mostrava "Página 3 de 2", sem nenhum cartão. As três linhas do `if (estado.pagina > totalDePaginas)` voltam para a última página que existe e recarregam.

## // O erro: duas origens, duas mensagens

```js
function tratarErro(erro) {
  if (erro instanceof api.ErroDeRede) {
    ui.mostrarEstadoApi("fora");
    ui.mostrarMensagem(erro.message, "erro");
  } else if (erro instanceof api.ErroHttp) {
    ui.mostrarMensagem(`A API respondeu com o código ${erro.status}.`, "erro");
  } else {
    console.error(erro);
    ui.mostrarMensagem("Algo inesperado aconteceu. Veja o console.", "erro");
  }
}
```

Cada ramo diz algo diferente à pessoa: o `ErroDeRede` ("a API não respondeu") é um problema de conexão, que ela talvez possa resolver; o `ErroHttp` ("a API respondeu com um erro") é um problema do sistema. Com a API desligada, o teste automatizado confirma o resultado:

```
estado da API: "API fora do ar"
mensagem: "Não foi possível falar com a API. Ela está ligada?"
```

## // Busca e filtro

A busca por nome roda **enquanto a pessoa digita**, mas não a cada letra: um pequeno atraso (`comAtraso`, de 300 milissegundos) espera a pessoa parar de digitar, para não fazer um pedido por tecla. Cada nova busca volta para a página 1. O filtro por matéria usa o evento `change`, que dispara quando a escolha muda.

Resultados verificados em um teste com a API real: sem filtros, a página mostra os quatro primeiros grupos em ordem alfabética (`Cálculo passo a passo`, `Estruturas na prática`, `Modelagem e SQL` e `Processos e memória`); a busca `prática` mostra só `Estruturas na prática`; a busca `zzz` mostra "Nenhum grupo encontrado."; e o filtro pela matéria 3 mostra só `Modelagem e SQL`.

## // Bom exemplo × mau exemplo

**Mau exemplo**: desenhar a lista só quando dá certo:

```js
const grupos = await api.listarGrupos();
renderizar(grupos);        // se a API cair, a tela não muda e nada é dito
```

**Bom exemplo**: cada estado tem o seu desenho:

```js
ui.mostrarMensagem("Carregando...");
try {
  const { grupos } = await api.listarGrupos();
  renderizar(grupos);            // sucesso, ou a mensagem de lista vazia
  ui.mostrarMensagem("");
} catch (erro) {
  tratarErro(erro);              // erro de rede, ou erro HTTP
}
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| A lista duplica a cada busca | Os cartões novos foram somados aos antigos | `replaceChildren()` antes de desenhar |
| Uma busca "velha" aparece na tela | Respostas fora de ordem | Numere os pedidos e descarte os atrasados |
| `Página 3 de 2` depois de apagar | A página pedida deixou de existir | Volte para a última página que existe |
| "Carregando..." fica na tela para sempre | O `try` não limpa a mensagem, ou o erro não foi tratado | Limpe a mensagem em caso de sucesso e trate o erro |
| Um pedido por tecla digitada | Faltou o atraso na busca | Use um atraso (`comAtraso`) |
| A tela mostra o número da matéria | O `materia_id` não foi trocado pelo nome | Monte um `Map` a partir de `GET /materias` |

## // Prática guiada

1. Copie `example/frontend/api.js`, `ui.js` e `app.js` para `projeto-fullstack/frontend`, **ou** escreva-os por partes, na ordem deste módulo: `listarGrupos`, `renderizarGrupos`, `carregarGrupos`, `tratarErro` e `iniciar`.
2. Ligue a **API com CORS** (`example/api`), sirva a página e abra `http://127.0.0.1:5500`.
3. Confira os quatro primeiros grupos e o estado "API conectada".
4. Busque `prática`, depois `zzz`, e depois limpe a busca.
5. Escolha uma matéria no filtro e volte para "Todas".
6. Desligue a API (Ctrl+C no terminal dela) e use a busca: leia a mensagem e o estado da API.

## // Pratique sozinho

> **DESAFIO**
> Acrescente ao cartão de cada grupo uma linha com a **data de criação** em formato brasileiro (dia/mês/ano). A API devolve `criado_em` em texto ISO (por exemplo, `2026-09-03T12:00:00Z`). Dica: `new Date(g.criado_em).toLocaleDateString("pt-BR")`. Confirme o resultado para o grupo `Modelagem e SQL`, e use `textContent`.

## // Aplicando no projeto da semana

1. Deixe a listagem funcionando, com os quatro estados, a busca e o filtro.
2. No `README.md`, descreva em uma frase cada um dos quatro estados da tela.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Lista os grupos da API na página"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> `GET /grupos?q=zzz` devolve `200` com uma lista vazia. A página deve tratar isso como um **erro** ou como um **estado normal**? E o que ela deve mostrar?

Resposta: como um **estado normal**. A API respondeu corretamente, e simplesmente não há grupos que atendam à busca. A tela deve dizer isso com clareza ("Nenhum grupo encontrado."), sem usar o estilo de erro, e a paginação deve continuar coerente. Tratar a lista vazia como erro assustaria a pessoa sem motivo, e deixá-la em branco a faria achar que a página quebrou.

## // Resumo do módulo

- [ ] Sei os quatro estados da lista (carregando, sucesso, vazio e erro) e como mostrar cada um.
- [ ] Sei dividir o trabalho em `api.js`, `ui.js` e `app.js`.
- [ ] Sei desenhar uma lista com `createElement` e `textContent`.
- [ ] Sei diferenciar `ErroDeRede` de `ErroHttp` e dar a cada um a mensagem certa.
- [ ] Sei descartar respostas fora de ordem com um número de pedido.
- [ ] Sei tratar a página que deixou de existir.
- [ ] Sei implementar a busca com atraso e o filtro por matéria.

---

**Próximo módulo:** `11-enviando-dados-formulario-e-post.md`, a página já lê dados. Falta enviar.

`Material de Estudo // Coffee & Code`

# Módulo 12, Editar e Apagar: PATCH e DELETE

Português · [English](../docs-eng/12-editing-and-deleting-patch-and-delete.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

Criar e ler estão prontos. Faltam os dois outros verbos do CRUD: **alterar** (`PATCH`) e **apagar** (`DELETE`). Cada um traz uma lição de integração: o `PATCH` exige que o formulário saiba trabalhar em dois modos, e o `DELETE` devolve uma resposta **sem corpo**, que o código precisa reconhecer. Os dois precisam estar liberados no CORS, e é aqui que o `allow_methods` do Módulo 09 mostra o seu valor.

## // O problema: o mesmo formulário, dois trabalhos

O formulário de "Novo grupo" também serve para **editar** um grupo existente. A página precisa lembrar **qual** grupo está em edição, trocar o título e os botões, preencher os campos e, ao salvar, escolher entre `POST` e `PATCH`. Sem esse controle, editar criaria um grupo novo e deixaria o antigo como estava.

## // O PATCH: alterar um grupo

O `PATCH` envia só os campos que mudam, e a API devolve o grupo atualizado. A função do `api.js`:

```js
export async function alterarGrupo(id, corpo) {
  return (await pedir(`/grupos/${id}`, { metodo: "PATCH", corpo })).dados;
}
```

A página guarda o grupo em edição em `estado.editandoId`. Clicar em **Editar** em um cartão chama:

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

E o `ui.js` cuida da aparência dos dois modos:

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

Repare no `g.descricao ?? ""`: uma descrição `null` vira um campo vazio. E o botão **Cancelar edição** só existe no modo de edição (`hidden`).

Na função `salvar` do Módulo 11, o ramo de edição é o `else`:

```js
if (estado.editandoId === null) {
  await api.criarGrupo(corpo);
  aviso = "Grupo criado.";
} else {
  await api.alterarGrupo(estado.editandoId, corpo);
  aviso = "Grupo atualizado.";
}
```

> **O FORMULÁRIO ENVIA OS QUATRO CAMPOS**
> Por simplicidade, ao editar, a página envia os **quatro** campos, e não só os que mudaram. Isso funciona com o `PATCH`, e tem uma consequência útil: se a pessoa **esvaziar** a descrição, a página envia `descricao: null`, e a API a apaga. Já os outros três campos **não aceitam** `null`: a API responde `422`. O formulário da página nunca os envia assim, mas outro programa poderia, e a API precisa estar protegida.

Um `PATCH` com `null` em um campo obrigatório é recusado, sem corromper os dados. Resposta real:

```
PATCH /grupos/1   {"nome_grupo": null}

422  {"detail":[{"type":"value_error","loc":["body","nome_grupo"],
    "msg":"Value error, este campo não aceita null: omita-o para não alterá-lo",
    ... }]}
```

E o `null` na descrição é permitido:

```
PATCH /grupos/3   {"descricao": null}

200  {"nome_grupo":"Modelagem e SQL", ..., "descricao":null, ...}
```

Resultado verificado em um teste com a API real: ao editar `Cálculo II na prática` e mudar o limite para 8, o formulário volta ao modo "Novo grupo" e o cartão passa a mostrar "Até 8 participantes".

## // O DELETE: apagar um grupo

O `DELETE` responde `204 No Content`: **sem corpo**. A função `pedir()` do Módulo 07 já sabe disso (não chama `.json()` em uma resposta `204`):

```js
export async function apagarGrupo(id) {
  await pedir(`/grupos/${id}`, { metodo: "DELETE" });
}
```

Apagar não tem volta, então a página **pergunta antes**:

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

Os cuidados:

| Cuidado | Por que |
|---|---|
| `window.confirm(...)` antes do pedido | Uma pergunta evita o clique acidental. Se a pessoa cancelar, **nada** é enviado |
| `if (estado.editandoId === grupo.grupo_id) cancelarEdicao()` | Se o grupo apagado estava em edição, o formulário volta ao normal: senão, salvar tentaria alterar um grupo que não existe |
| `await carregarGrupos()` depois | A lista passa a refletir o que a API realmente tem |
| O tratamento do `404` | O grupo pode já ter sido apagado (em outra aba, ou por outra pessoa): a página avisa e atualiza, em vez de falhar |
| A mensagem **depois** do recarregamento | Pelo mesmo motivo do Módulo 11 |

Resposta real da API ao apagar um grupo que não existe:

```
DELETE /grupos/99

404  {"detail":"Grupo não encontrado"}
```

Verificado em teste: cancelar o `confirm` não apaga nada, e confirmar apaga e atualiza a paginação (por exemplo, de "Página 1 de 2 (7 grupos)" para "Página 1 de 2 (6 grupos)").

## // Por que recarregar a lista, em vez de ajustar a tela

Depois de criar, alterar ou apagar, a página poderia só mexer no cartão. Mas ela **recarrega a lista** inteira da API. É um pouco mais lento, e muito mais seguro: o total, a ordem alfabética e a paginação passam a refletir exatamente o que a API tem, e qualquer diferença entre o que a página "achava" e o que realmente aconteceu desaparece.

## // Bom exemplo × mau exemplo

**Mau exemplo**: apagar sem perguntar, e ajustar a tela "no escuro":

```js
await api.apagarGrupo(grupo.grupo_id);
cartao.remove();     // e se a API tiver recusado? e a paginação?
```

**Bom exemplo**: perguntar, apagar, e recarregar a lista da API:

```js
if (!window.confirm(`Apagar o grupo "${grupo.nome_grupo}"?`)) return;
await api.apagarGrupo(grupo.grupo_id);
await carregarGrupos();
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| O `PATCH` ou o `DELETE` falham com um erro de CORS | `PATCH` ou `DELETE` não estão em `allow_methods` (o preflight devolve `400 Disallowed CORS method`) | Libere os métodos no `CORSMiddleware` (Módulo 09) |
| Editar cria um grupo novo | O `salvar` não conferiu `estado.editandoId` | Use o `if (estado.editandoId === null)` |
| `Unexpected end of JSON input` ao apagar | `.json()` em uma resposta `204` | Não leia o corpo (a `pedir()` já cuida disso) |
| O formulário continua em "Editar grupo" depois de apagar o grupo | Faltou `cancelarEdicao()` | Cancele a edição se o grupo apagado era o editado |
| O `PATCH` devolve `422` com `null` | O campo obrigatório foi enviado como `null` | Omita o campo, ou envie um valor válido |
| Apagou sem querer | Faltou a confirmação | Use `window.confirm` antes do pedido |

## // Prática guiada

1. Com a API (com CORS) e a página no ar, clique em **Editar** em um grupo, mude o limite e salve. Confira o cartão.
2. Edite de novo, esvazie a descrição e salve: a descrição deve sumir.
3. Clique em **Editar** e depois em **Cancelar edição**: o formulário volta a "Novo grupo".
4. Apague um grupo, cancelando a pergunta na primeira vez e confirmando na segunda.
5. Na aba Rede, localize o `OPTIONS` e o `PATCH`, e o `OPTIONS` e o `DELETE`: leia os status (`200` para os dois preflights, `200` para o `PATCH` e `204` para o `DELETE`, como descrito no Módulo 11).
6. Remova `"PATCH"` de `allow_methods` na API, tente editar, e leia o erro no Console e na aba Rede. Depois desfaça.

## // Pratique sozinho

> **DESAFIO**
> Acrescente um botão **Desfazer**: logo depois de apagar um grupo, ele **recria** o grupo apagado com um `POST` com os mesmos dados. Guarde o último grupo apagado em `estado.ultimoApagado` e esconda o botão quando não houver nada a desfazer. Depois, responda: o `grupo_id` do grupo recriado é o mesmo do original? Verifique com a API, e explique o resultado.

## // Aplicando no projeto da semana

1. Complete `alterarGrupo`, `apagarGrupo`, `iniciarEdicao`, `cancelarEdicao`, `preencherFormulario` e `apagar`.
2. Teste editar, cancelar a edição, apagar com e sem confirmação.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Edita e apaga grupos pela página"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> A pessoa clica em **Editar** em um grupo e, em outra aba do navegador, outra pessoa apaga esse mesmo grupo. A primeira clica em **Salvar**. O que deve acontecer, e como a página trata isso?

Resposta: a API responde `404` ao `PATCH`, porque o grupo já não existe. No `catch` do `salvar`, o ramo do `404` mostra "Esse grupo já não existe.", cancela a edição e recarrega a lista, que passa a refletir o estado real. A página não quebra, e a pessoa entende o que aconteceu. É um exemplo de por que cada resposta de erro precisa de um tratamento previsto.

## // Resumo do módulo

- [ ] Sei usar o mesmo formulário para criar e editar, com `estado.editandoId`.
- [ ] Sei enviar um `PATCH` e que os campos obrigatórios não aceitam `null`.
- [ ] Sei apagar com `DELETE`, que a resposta `204` não tem corpo, e por que confirmar antes.
- [ ] Sei tratar o `404` de um grupo que já não existe.
- [ ] Sei por que recarregar a lista depois de cada alteração.
- [ ] Sei que `PATCH` e `DELETE` precisam estar em `allow_methods` no CORS.

---

**Próximo módulo:** `13-paginacao-e-cabecalhos-expostos.md`, o CRUD está completo. Falta dar à lista a paginação que ela merece.

`Material de Estudo // Coffee & Code`

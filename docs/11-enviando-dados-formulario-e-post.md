# Módulo 11, Enviando Dados: Formulário e POST

Português · [English](../docs-eng/11-sending-data-form-and-post.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

Até aqui a página só **lê**. Este módulo a faz **enviar**: ela cria um grupo de estudo a partir do formulário. É onde a integração fica mais interessante, porque a API pode **recusar** o que a página enviou, e a pessoa precisa entender o motivo. Você vai ver o preflight do CORS em ação, receber erros da API e mostrá-los no campo certo da tela.

## // O problema: a pessoa erra, e a página precisa explicar

Dois tipos de recusa são esperados em um formulário. O primeiro é o **dado inválido**: nome curto demais, limite fora da faixa. O segundo é o **conflito**: o nome já existe naquela matéria. Em ambos, a API responde com um erro, e a página precisa transformá-lo em uma mensagem clara, no lugar certo, em vez de um genérico "algo deu errado".

## // Do formulário ao JSON

O formulário do `index.html` tem quatro campos. A função `lerFormulario()`, em `ui.js`, junta o que a pessoa digitou em um objeto pronto para virar JSON:

```js
export function lerFormulario() {
  const descricao = $("descricao").value.trim();
  return {
    nome_grupo: $("nome").value.trim(),
    materia_id: Number($("materia").value),
    max_participantes: Number($("limite").value),
    descricao: descricao === "" ? null : descricao,
  };
}
```

Três cuidados nessa função:

- O `.trim()` tira os espaços das pontas: `"   ab "` vira `"ab"`.
- O `Number(...)` converte o texto do campo (sempre texto, Módulo 05) em número.
- Uma descrição vazia vira `null`, e não `""`: a API a aceita como "sem descrição".

E o envio, em `api.js`, é um `POST` com JSON (a função `pedir()` do Módulo 07 já cuida do `Content-Type`):

```js
export async function criarGrupo(corpo) {
  return (await pedir("/grupos", { metodo: "POST", corpo })).dados;
}
```

## // O preflight, na aba Rede

O `POST` com `Content-Type: application/json` **não é um pedido simples** (Módulo 09): antes dele, o navegador faz, sozinho, um pedido `OPTIONS`. Ao criar um grupo, a aba Rede deve mostrar **duas** linhas para `grupos`: primeiro o `OPTIONS` (o preflight), com status `200`, depois o `POST`, com status `201`. Essa descrição segue a especificação, e **não foi reproduzida em um navegador** durante a produção do material.

A API desta semana responde ao preflight porque o `CORSMiddleware` libera o método e o cabeçalho (verificado com `curl` no Módulo 09):

```
OPTIONS /grupos  (Access-Control-Request-Method: POST, ...-Headers: content-type)

200  access-control-allow-methods: GET, POST, PATCH, DELETE
     access-control-allow-headers: Accept, Accept-Language,
                                   Content-Language, Content-Type
```

## // Os erros que a API devolve

Estas são as respostas reais da API para os erros de um formulário:

| O que a pessoa fez | Status | O que vem em `detail` |
|---|---|---|
| Nome com 2 letras | `422` | Uma **lista**, com o `loc` apontando `nome_grupo` |
| Limite 51 | `422` | Uma **lista**, com o `loc` apontando `max_participantes` |
| Nome repetido na mesma matéria | `409` | Um **texto**: `Já existe um grupo com esse nome nessa matéria` |
| Uma matéria que não existe | `422` | Um **texto**: `A matéria 99 não existe` |

Os corpos completos dos dois primeiros casos:

```
POST /grupos   {"nome_grupo": "ab", "materia_id": 1}

422  {"detail":[{"type":"string_too_short",
                 "loc":["body","nome_grupo"],
                 "msg":"String should have at least 3 characters",
                 "input":"ab","ctx":{"min_length":3}}]}

POST /grupos   {"nome_grupo": "Teste valido", "materia_id": 1,
                "max_participantes": 51}

422  {"detail":[{"type":"less_than_equal",
                 "loc":["body","max_participantes"],
                 "msg":"Input should be less than or equal to 50",
                 "input":51,"ctx":{"le":50}}]}
```

Repare que existem **dois formatos** de `detail`: uma **lista de problemas** (a validação automática, com o campo em `loc`) e um **texto** (as regras escritas à mão). O código da página precisa reconhecer os dois.

### > Achando o campo do erro

No erro de validação, o `loc` é uma lista como `["body", "nome_grupo"]`: o último item é o nome do campo da API. A página mantém uma tabela que liga cada campo da API ao elemento onde o erro aparece:

```js
const CAMPO_DO_ERRO = {
  nome_grupo: "erro-nome",
  materia_id: "erro-materia",
  max_participantes: "erro-limite",
  descricao: "erro-descricao",
};

export function mostrarErroDeCampo(campo, texto) {
  const id = CAMPO_DO_ERRO[campo];
  if (id) $(id).textContent = texto;
}
```

E o `app.js` percorre os problemas da resposta:

```js
function mostrarErrosDeValidacao(detail) {
  for (const problema of detail) {
    // ["body", "nome_grupo"] -> "nome_grupo"
    const campo = problema.loc[problema.loc.length - 1];
    ui.mostrarErroDeCampo(campo, problema.msg);
  }
  ui.mostrarMensagem("Corrija os campos indicados.", "erro");
}
```

O texto do erro vem da API, em inglês (`String should have at least 3 characters`). Isso é aceitável para estudar, e um desafio abaixo propõe traduzir as mensagens.

## // O tratador do envio

A função `salvar` junta tudo. Ela serve para criar e (no Módulo 12) para editar, e o trecho abaixo mostra a função completa:

```js
async function salvar(evento) {
  evento.preventDefault();
  ui.limparErros();
  ui.travarFormulario(true);
  const corpo = ui.lerFormulario();
  try {
    let aviso;
    if (estado.editandoId === null) {
      await api.criarGrupo(corpo);
      aviso = "Grupo criado.";
    } else {
      await api.alterarGrupo(estado.editandoId, corpo);
      aviso = "Grupo atualizado.";
    }
    cancelarEdicao();
    await carregarGrupos();
    // depois de recarregar, porque carregarGrupos limpa a mensagem
    ui.mostrarMensagem(aviso);
  } catch (erro) {
    if (erro instanceof api.ErroHttp && erro.status === 422) {
      if (Array.isArray(erro.corpo?.detail))
        mostrarErrosDeValidacao(erro.corpo.detail);
      else ui.mostrarMensagem(erro.corpo?.detail ?? "Dados inválidos.", "erro");
    } else if (erro instanceof api.ErroHttp && erro.status === 409) {
      ui.mostrarErroDeCampo(
        "nome_grupo", "Já existe um grupo com esse nome nessa matéria."
      );
      ui.mostrarMensagem("Conflito: escolha outro nome.", "erro");
    } else if (erro instanceof api.ErroHttp && erro.status === 404) {
      ui.mostrarMensagem("Esse grupo já não existe.", "erro");
      cancelarEdicao();
      await carregarGrupos();
    } else {
      tratarErro(erro);
    }
  } finally {
    ui.travarFormulario(false);
  }
}
```

Os detalhes que fazem diferença:

| Detalhe | Por que importa |
|---|---|
| `evento.preventDefault()` | Impede que o navegador recarregue a página ao enviar |
| `ui.travarFormulario(true)` e o `finally` | Desabilita o botão **Salvar** durante o pedido e o reabilita no fim, **mesmo se der erro**: evita o clique duplo, que criaria o grupo duas vezes |
| A mensagem de sucesso **depois** de `carregarGrupos()` | A `carregarGrupos` limpa a mensagem ao terminar: escrever o aviso antes o apagaria (um defeito que o teste automatizado encontrou) |
| `Array.isArray(erro.corpo?.detail)` | Distingue os dois formatos do `detail` |
| O ramo do `409` | Escolhe a mensagem e marca o campo do nome |
| O `finally` | Roda sempre: com sucesso ou com erro |

> **POR QUE A PÁGINA NÃO VALIDA TUDO SOZINHA**
> O `index.html` usa `novalidate`, que desliga as validações automáticas do navegador, e a página deixa a **API validar**. A razão é que a API é a dona das regras (3 a 60 caracteres, limite entre 2 e 50): se a regra mudar, a página continua certa sem alteração. Validar também na página melhora a experiência, mas **nunca** substitui a validação da API, porque qualquer pessoa pode chamar a API sem passar pela página.

## // O resultado, verificado

Em um teste automatizado com a API real, estes foram os comportamentos confirmados:

| Ação | Resultado na tela |
|---|---|
| Criar `Cálculo II na prática`, matéria 1, limite 5 | Mensagem "Grupo criado.", formulário limpo, paginação "Página 1 de 2 (7 grupos)" |
| Enviar o nome `ab` | No campo do nome: `String should have at least 3 characters`; mensagem "Corrija os campos indicados."; o botão Salvar volta a funcionar |
| Repetir `Cálculo II na prática` na matéria 1 | No campo do nome: "Já existe um grupo com esse nome nessa matéria."; mensagem começando com "Conflito" |
| Criar um grupo chamado `<img src=x onerror=alert(1)>` | O nome aparece como texto, e nenhum elemento `<img>` é criado |

## // Bom exemplo × mau exemplo

**Mau exemplo**: um aviso genérico para qualquer erro:

```js
try {
  await api.criarGrupo(corpo);
} catch {
  alert("Erro ao salvar.");
}
```

A pessoa não sabe **o que** corrigir, **onde**, nem se vale a pena tentar de novo.

**Bom exemplo**: cada erro, na sua mensagem e no seu campo:

```js
} catch (erro) {
  if (erro instanceof api.ErroHttp && erro.status === 422)
    mostrarErrosDeValidacao(erro.corpo.detail);
  else if (erro instanceof api.ErroHttp && erro.status === 409)
    ui.mostrarErroDeCampo("nome_grupo", "Já existe um grupo com esse nome.");
  else tratarErro(erro);
}
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| A página recarrega ao enviar | Faltou `evento.preventDefault()` | Acrescente na primeira linha de `salvar` |
| `422` mesmo com o nome certo | Faltou `Content-Type: application/json`, ou o corpo não foi passado por `JSON.stringify` | Use a `pedir()`, que cuida disso |
| `422` no limite, com o campo "vazio" | `Number("")` dá `0`, e `0` está fora da faixa | É o esperado: a API recusa e a mensagem aparece no campo |
| O grupo é criado duas vezes | Clique duplo no botão | Desabilite o botão durante o envio (`travarFormulario`) |
| A mensagem de sucesso não aparece | Foi escrita antes de `carregarGrupos()`, que a apaga | Escreva depois de recarregar |
| O preflight falha com `400` | `POST` ou `Content-Type` fora do CORS da API | Confira `allow_methods` e `allow_headers` (Módulo 09) |
| O erro aparece só no console | O `catch` só tem `console.log` | Mostre o erro na tela |

## // Prática guiada

1. Com a API (com CORS) e a página no ar, preencha o formulário com um nome válido e salve. Veja a mensagem e a lista.
2. Abra a aba Rede, filtre por Fetch/XHR e localize o `OPTIONS` e o `POST` do envio: leia os dois status.
3. Envie o nome `ab` e leia o erro no campo e o corpo da resposta na aba Rede.
4. Repita o mesmo grupo para provocar o `409`.
5. Envie um limite de 51 e anote a mensagem.
6. Clique em **Salvar** duas vezes bem depressa e confira que só um grupo foi criado.

## // Pratique sozinho

> **DESAFIO**
> Traduza as mensagens de erro de validação para o português. Crie um objeto `TRADUCOES` que ligue o `type` do erro (`string_too_short`, `less_than_equal`, `greater_than_equal`, `string_too_long`, `int_parsing`) a um texto em português, e use-o em `mostrarErrosDeValidacao`, caindo na mensagem original da API se o tipo não estiver na tabela. Dica: o `type` está em `problema.type`.

## // Aplicando no projeto da semana

1. Complete o formulário: `lerFormulario`, `criarGrupo`, `mostrarErroDeCampo`, `mostrarErrosDeValidacao` e a função `salvar` (por enquanto, só o ramo de criação importa).
2. Teste os quatro casos da tabela de resultados e anote o que aparece em cada um.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Cria grupos pelo formulário"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Por que o botão **Salvar** é reabilitado dentro de um bloco `finally`, e não no fim do `try`?

Resposta: porque o `finally` roda **sempre**, tanto quando o envio dá certo quanto quando dá erro. Se o botão fosse reabilitado só no fim do `try`, qualquer erro (um `422`, um `409`, a API fora do ar) pularia essa linha e deixaria o botão desabilitado para sempre: a pessoa corrigiria o campo e não conseguiria enviar de novo.

## // Resumo do módulo

- [ ] Sei transformar um formulário em um objeto JSON (`trim`, `Number` e descrição vazia como `null`).
- [ ] Sei enviar um `POST` com JSON e reconhecer o preflight na aba Rede.
- [ ] Sei os dois formatos de `detail` (lista e texto) e como achar o campo do erro.
- [ ] Sei mostrar cada erro (`422`, `409`) no lugar certo da tela.
- [ ] Sei travar o botão durante o envio e liberá-lo com `finally`.
- [ ] Sei por que a API, e não a página, é a dona das regras de validação.

---

**Próximo módulo:** `12-editar-e-apagar-patch-e-delete.md`, criar está pronto. Agora, alterar e remover.

`Material de Estudo // Coffee & Code`

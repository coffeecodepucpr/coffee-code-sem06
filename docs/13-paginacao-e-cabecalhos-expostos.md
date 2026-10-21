# Módulo 13, Paginação e Cabeçalhos Expostos

Português · [English](../docs-eng/13-pagination-and-exposed-headers.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

A lista da página mostra quatro grupos por vez, e botões **Anterior** e **Próxima** passam de página. Para isso, a página precisa saber **quantos grupos existem ao todo**, e esse número viaja em um cabeçalho da resposta, o `X-Total-Count`. É a última peça da integração, e junta dois assuntos que você já viu: a paginação da API (Módulo 03) e os cabeçalhos que o JavaScript pode ou não ler (Módulos 02 e 09).

## // O problema: quantas páginas existem?

A API devolve só a página pedida: com `limit=4`, vêm quatro grupos, e nada na lista diz se há mais. Sem o total, a página não consegue saber se deve habilitar **Próxima**, nem desenhar "página 1 de 2". A resposta é uma lista, e uma lista não tem lugar para um número extra, então a API o coloca em um **cabeçalho**.

## // Paginação com limit e offset

A API aceita dois parâmetros no `GET /grupos`:

| Parâmetro | Significado |
|---|---|
| `limit` | Quantos grupos devolver (1 a 100, padrão 10) |
| `offset` | Quantos grupos pular antes de começar (padrão 0) |

A página usa quatro grupos por vez. Os pedidos de cada página:

| Página | Pedido | O que a API devolve |
|---|---|---|
| 1 | `?limit=4&offset=0` | Os quatro primeiros, em ordem alfabética |
| 2 | `?limit=4&offset=4` | Os dois seguintes (existem seis grupos) |

A conta é a mesma sempre: o `offset` da página `n` é `(n - 1) × limite`. No `app.js`:

```js
deslocamento: (estado.pagina - 1) * TAMANHO_DA_PAGINA,
```

E o número de páginas é o total dividido pelo tamanho, **arredondado para cima**, com no mínimo uma página:

```js
const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
```

Com seis grupos e quatro por página, `Math.ceil(6 / 4)` é `2`. O `Math.max(1, ...)` garante que, com zero grupos, ainda exista "a página 1", em vez de "página 1 de 0".

## // O cabeçalho X-Total-Count

Cada resposta de `GET /grupos` traz o total de grupos **que atendem aos filtros**, calculado **antes** de cortar a página. Resposta real da API:

```
GET /grupos?limit=2

HTTP/1.1 200 OK
x-total-count: 6
```

O total respeita a busca e o filtro: com `?q=prática&limit=1`, ele vale `1`, e não `6`, porque só um grupo atende ao filtro. O valor serve para desenhar "página 1 de N" **daquela busca**.

Em JavaScript, o cabeçalho é lido com `resposta.headers.get(...)`, e vem como **texto**, por isso o `Number(...)`:

```js
const total = resposta.headers.get("X-Total-Count");
if (total === null) {
  console.warn(
    "X-Total-Count não está visível. Confira o expose_headers do CORS na API."
  );
}
return { grupos: dados, total: total === null ? dados.length : Number(total) };
```

## // O cabeçalho que o navegador esconde

O `X-Total-Count` está na resposta, e mesmo assim o JavaScript pode receber `null`. O motivo, que o Módulo 02 antecipou: a página e a API estão em **origens diferentes**, e o navegador só deixa o JavaScript ler os cabeçalhos **básicos** da resposta (`Cache-Control`, `Content-Language`, `Content-Length`, `Content-Type`, `Expires`, `Last-Modified` e `Pragma`). Qualquer outro precisa ser **exposto** pelo servidor:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Total-Count"],
)
```

Com isso, a resposta da API passa a trazer um cabeçalho a mais, `access-control-expose-headers`, que **lista** os cabeçalhos liberados para o JavaScript (verificado com `curl`, no Módulo 09):

```
x-total-count: 6
access-control-expose-headers: X-Total-Count
access-control-allow-origin: http://127.0.0.1:5500
```

Sem o `expose_headers`, o navegador entregaria `null` ao JavaScript. Essa é uma regra do **navegador**, descrita no MDN e na especificação Fetch, e **não foi reproduzida em um navegador** durante a produção do material. O código da página se defende: se `total` vier `null`, ele usa o tamanho da página como total e escreve um aviso no console, apontando a causa provável.

> **UMA ARMADILHA SILENCIOSA**
> Sem a defesa, `Number(null)` vale `0`. A página mostraria "0 grupos" e desabilitaria os dois botões, com a lista cheia na tela, e **nenhum erro** apareceria no console. Por isso o `X-Total-Count` ausente merece um aviso explícito.

## // Os botões e o texto da paginação

O desenho da paginação fica em uma função do `ui.js`:

```js
export function renderizarPaginacao({ pagina, totalDePaginas, total }) {
  const grupos = total === 1 ? "grupo" : "grupos";
  $("pagina-atual").textContent =
    `Página ${pagina} de ${totalDePaginas} (${total} ${grupos})`;
  $("anterior").disabled = pagina <= 1;
  $("proxima").disabled = pagina >= totalDePaginas;
}
```

O botão **Anterior** fica desabilitado na primeira página, e o **Próxima**, na última. Repare na concordância: `1 grupo`, e `6 grupos` (um pequeno cuidado que faz a tela parecer feita por gente).

E os cliques, registrados em `iniciar()`:

```js
el.anterior.addEventListener("click", () => {
  estado.pagina -= 1;
  carregarGrupos();
});
el.proxima.addEventListener("click", () => {
  estado.pagina += 1;
  carregarGrupos();
});
```

Os filtros voltam à página 1, porque a página 3 de uma busca não faz sentido na busca seguinte:

```js
el.busca.addEventListener("input", comAtraso(() => {
  estado.busca = el.busca.value.trim();
  estado.pagina = 1;
  carregarGrupos();
}, 300));
el.filtroMateria.addEventListener("change", () => {
  estado.materiaId = el.filtroMateria.value;
  estado.pagina = 1;
  carregarGrupos();
});
```

## // O que os testes confirmaram

Em um teste automatizado com a API real:

| Situação | Texto da paginação | Botões |
|---|---|---|
| Página inicial | `Página 1 de 2 (6 grupos)` | Anterior desabilitado, Próxima habilitado |
| Depois de **Próxima** | `Página 2 de 2` | Próxima desabilitado, e dois grupos na lista (`Redes na unha` e `Requisitos e histórias`) |
| Busca `prática` | `Página 1 de 1 (1 grupo)` | Os dois desabilitados |
| Depois de criar um grupo | `Página 1 de 2 (7 grupos)` | |
| Com 9 grupos, na página 3, apagando o único item dela | `Página 2 de 2 (8 grupos)` | Volta sozinha para a última página que existe |

## // Bom exemplo × mau exemplo

**Mau exemplo**: calcular o total contando a lista que veio:

```js
// grupos tem, no máximo, 4 itens!
const totalDePaginas = Math.ceil(grupos.length / 4);
```

A lista é só **uma página**: o resultado seria sempre `1`.

**Bom exemplo**: usar o total que a API informou:

```js
const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `headers.get("X-Total-Count")` devolve `null` | A API não expôs o cabeçalho | Acrescente `expose_headers=["X-Total-Count"]` ao CORS |
| A tela mostra "0 grupos" com a lista cheia | `Number(null)` vale `0` | Trate o `null` (a página já se defende) |
| "Página 3 de 2" depois de apagar | A página pedida deixou de existir | Volte para a última página que existe (Módulo 10) |
| A paginação continua na página 3 depois de buscar | O filtro não voltou à página 1 | Faça `estado.pagina = 1` ao mudar o filtro |
| "1 grupos" no singular | A concordância não foi tratada | Troque `grupos` por `grupo` quando o total for 1 |
| O `offset` está errado | A conta usou `pagina` em vez de `pagina - 1` | `(pagina - 1) * limite` |
| `422` ao pedir `limit=0` ou `limit=101` | O `limit` fica entre 1 e 100 | Respeite os limites da API |

## // Prática guiada

1. Com a API (com CORS) e a página no ar, confira "Página 1 de 2 (6 grupos)" e navegue para a página 2 e de volta.
2. Na aba Rede, localize o pedido da listagem e leia o `x-total-count` e o `access-control-expose-headers` nos cabeçalhos da resposta.
3. No `curl`, rode `curl -i "http://127.0.0.1:8000/grupos?q=prática&limit=1"` e leia o total.
4. Crie grupos até passar de quatro por página e confira as novas páginas.
5. Remova `expose_headers` da API, recarregue a página e observe o aviso no console e o comportamento da paginação. Depois restaure a linha.

## // Pratique sozinho

> **DESAFIO**
> Acrescente à paginação um **seletor de tamanho de página** com as opções 2, 4 e 8 grupos por página. Troque a constante `TAMANHO_DA_PAGINA` por um valor guardado em `estado`, volte à página 1 quando o tamanho mudar, e confira que o `offset` e o número de páginas continuam certos nos três tamanhos.

## // Aplicando no projeto da semana

1. Complete `renderizarPaginacao`, os dois botões e o reinício da página nos filtros.
2. Confira que o `expose_headers` está no `main.py` da API.
3. No `README.md`, explique em duas linhas por que a API precisa expor o `X-Total-Count`.
4. Se você versiona o projeto com Git, faça um commit: `git commit -m "Pagina a lista de grupos"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> A API devolveu `x-total-count: 6`, e a aba Rede mostra o cabeçalho na resposta. A página, porém, mostra "0 grupos". Qual é a causa mais provável, e como confirmar?

Resposta: o servidor não expôs o cabeçalho. A aba Rede mostra tudo o que **chegou** ao navegador, mas o JavaScript só pode **ler** os cabeçalhos básicos e os listados em `Access-Control-Expose-Headers`. Sem isso, `headers.get(...)` devolve `null`, e `Number(null)` dá `0`. Para confirmar, procure o cabeçalho `access-control-expose-headers` na resposta: se ele estiver ausente, ou não listar `X-Total-Count`, a causa é essa. A correção é `expose_headers=["X-Total-Count"]` na API.

## // Resumo do módulo

- [ ] Sei calcular o `offset` (`(página - 1) × limite`) e o número de páginas (`Math.ceil`, no mínimo 1).
- [ ] Sei que o `X-Total-Count` informa o total depois dos filtros, e antes do corte da página.
- [ ] Sei por que o navegador esconde esse cabeçalho, e como expô-lo com `expose_headers`.
- [ ] Sei por que `Number(null)` é uma armadilha silenciosa.
- [ ] Sei habilitar e desabilitar os botões, e voltar à página 1 ao mudar um filtro.

---

**Próximo módulo:** `14-projeto-guiado.md`, todas as peças estão prontas. Hora de montá-las e conferir a aplicação inteira.

`Material de Estudo // Coffee & Code`

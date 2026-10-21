# Módulo 02, Headers

Português · [English](../docs-eng/02-headers.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

No Módulo 01 você viu que um pedido e uma resposta têm **cabeçalhos**. Eles pareciam um detalhe, e não são: quase todo erro de integração tem um cabeçalho no meio, faltando, errado ou escondido. Este módulo mostra quais são os cabeçalhos importantes, quem coloca cada um, e quais o seu JavaScript consegue ler.

## // O problema: o mesmo pedido, resultados diferentes

Imagine dois pedidos idênticos para a API: um feito pelo `curl` e outro feito pela página. O primeiro funciona, e o segundo não. As URLs são iguais, os dados são iguais. A diferença está em cabeçalhos que ninguém escreveu à mão: o navegador acrescentou um deles no pedido, e a resposta voltou sem outro que ele esperava.

## // O que é um cabeçalho

> **CABEÇALHO (HEADER): EM PALAVRAS SIMPLES**
> É uma informação extra que viaja junto com o pedido ou com a resposta, no formato `nome: valor`, uma por linha. Ela descreve o que está sendo enviado (o formato, o tamanho), quem está pedindo, ou o que se permite fazer com a resposta.

Os nomes dos cabeçalhos **não diferenciam maiúsculas de minúsculas**: `Content-Type` e `content-type` são o mesmo. Em JavaScript, você confirma isso: `resposta.headers.get("X-Total-Count")` e `resposta.headers.get("x-total-count")` devolvem o mesmo valor.

## // Os cabeçalhos de uma conversa real

Estas são as linhas de uma conversa real com a API, já com o CORS configurado, vista pelo `curl` em modo detalhado. Primeiro, um `GET` que a página faria:

```
> GET /grupos?limit=2 HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/X.Y
> Accept: */*
> Origin: http://127.0.0.1:5500
>
< HTTP/1.1 200 OK
< server: uvicorn
< content-length: 285
< content-type: application/json
< x-total-count: 6
< access-control-expose-headers: X-Total-Count
< access-control-allow-origin: http://127.0.0.1:5500
< vary: Origin
```

E um `POST` com um corpo em JSON:

```
> POST /grupos HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/X.Y
> Accept: */*
> Content-Type: application/json
> Content-Length: 51
>
< HTTP/1.1 201 Created
< server: uvicorn
< content-length: 146
< content-type: application/json
< location: /grupos/7
< vary: Origin
```

(Em ambas, a resposta real traz também o cabeçalho `date`, omitido aqui.)

## // Os cabeçalhos do pedido

| Cabeçalho | Quem coloca | Para que serve |
|---|---|---|
| `Host` | O cliente, automaticamente | O servidor e a porta de destino |
| `User-Agent` | O cliente, automaticamente | Quem está pedindo (o navegador, o `curl`...) |
| `Accept` | O cliente | Os formatos de resposta que ele aceita |
| `Content-Type` | **Você**, quando envia um corpo | O formato do corpo: `application/json` para JSON |
| `Content-Length` | O cliente, automaticamente | O tamanho do corpo, em bytes |
| `Origin` | **O navegador**, nos pedidos entre origens | A origem da página que fez o pedido (a base do CORS) |

## // Os cabeçalhos da resposta

| Cabeçalho | Para que serve | Onde aparece nesta semana |
|---|---|---|
| `Content-Type` | O formato do corpo da resposta | `application/json` em toda resposta com corpo |
| `Content-Length` | O tamanho do corpo | Nas respostas com corpo |
| `Location` | O endereço do recurso recém-criado | No `201` do `POST /grupos` |
| `Allow` | Os métodos que a rota aceita | Na resposta `405` |
| `X-Total-Count` | O total de grupos, para a paginação | No `GET /grupos` (Módulo 13) |
| `Access-Control-Allow-Origin` | A origem autorizada a ler a resposta | Nas respostas do CORS (Módulo 09) |
| `Vary` | Avisa aos caches que a resposta depende de outro cabeçalho | `vary: Origin` |

## // Quem coloca cada cabeçalho

<div align="center">
<img src="./assets/svg/mapa-de-cabecalhos.svg" alt="Os cabeçalhos que o navegador coloca, os que o JavaScript escolhe e os que a API devolve" width="640">
</div>

Uma distinção que vai evitar muita dor de cabeça: existem cabeçalhos que **só o navegador** pode definir. O seu JavaScript pode tentar mudar o `Origin` ou o `Host`, e o navegador ignora a tentativa. A documentação do MDN mantém uma lista desses nomes proibidos (entre eles `Host`, `Origin`, `Content-Length` e `Cookie`). Isso existe por segurança: uma página não pode se passar por outra.

Já o `Content-Type` e o `Accept` você escolhe, e os cabeçalhos próprios da sua aplicação (muitos começam com `X-`, uma convenção antiga) também. Mas há um custo: um cabeçalho fora do conjunto básico torna o pedido "não simples", e o navegador passa a fazer o **preflight** do Módulo 09, que exige que a API libere o cabeçalho em `allow_headers`.

## // O que o seu JavaScript consegue ler

Em um `fetch`, os cabeçalhos da resposta ficam em `resposta.headers`:

```js
const resposta = await fetch("http://127.0.0.1:8000/grupos?limit=2");
console.log(resposta.headers.get("content-type"));       // "application/json"
console.log(resposta.headers.get("x-total-count"));      // "6"
console.log(resposta.headers.get("x-nao-existe"));       // null
```

Este código, executado no Node contra a API real, devolveu exatamente os valores dos comentários. Repare em dois detalhes: o valor de um cabeçalho é sempre **texto** (`"6"`, e não `6`), e um cabeçalho que não existe devolve `null`.

Quando a página e a API estão em **origens diferentes**, existe uma restrição a mais: o navegador só deixa o JavaScript ler os cabeçalhos "básicos" da resposta (`Cache-Control`, `Content-Language`, `Content-Length`, `Content-Type`, `Expires`, `Last-Modified` e `Pragma`) e os que o servidor listar em `Access-Control-Expose-Headers`. Qualquer outro chega como `null`, mesmo estando na resposta. É por isso que o `X-Total-Count` precisa de `expose_headers=["X-Total-Count"]` na API. Fonte: documentação do MDN e a especificação Fetch, consultadas em 08/10/2026. Esse comportamento é **do navegador**: o Node, que não aplica o CORS, entrega todos os cabeçalhos, por isso ele não o reproduziu.

## // O cabeçalho que mais causa problemas: Content-Type

Quando você envia JSON, o `Content-Type: application/json` é obrigatório. Se ele faltar, o `fetch` envia o corpo como texto simples (o padrão, para um corpo em texto, é `text/plain;charset=UTF-8`, segundo a especificação), e a API não o reconhece como JSON. Resultado real, ao enviar o corpo certo sem o cabeçalho:

```
POST /grupos   (sem Content-Type)

422  {"detail":[{"type":"model_attributes_type", ...,
    "msg":"Input should be a valid dictionary or object to extract fields from"}]}
```

A mensagem fala em "dicionário", e não menciona o cabeçalho. Quem não sabe disso procura o erro no corpo, e ele está no cabeçalho que faltou.

## // Bom exemplo × mau exemplo

**Mau exemplo**: enviar JSON sem dizer que é JSON:

```js
await fetch(`${API}/grupos`, {
  method: "POST",
  body: JSON.stringify({ nome_grupo: "Redes", materia_id: 5 }),
});
```

**Bom exemplo**: declarar o formato do corpo:

```js
await fetch(`${API}/grupos`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ nome_grupo: "Redes", materia_id: 5 }),
});
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `422` ao enviar JSON, mesmo com o corpo certo | Faltou `Content-Type: application/json` | Acrescente o cabeçalho ao `fetch` |
| `headers.get("x-total-count")` devolve `null` | A API não expôs o cabeçalho (`expose_headers`) ao navegador | Acrescente o cabeçalho ao `expose_headers` do CORS |
| Tentar mudar o `Origin` pelo JavaScript | É um cabeçalho proibido: o navegador ignora | Não tente: ele é a base do CORS |
| Esperar um número e receber texto | Todo valor de cabeçalho é texto | Converta com `Number(...)` |
| O preflight falha ao acrescentar um cabeçalho próprio | O cabeçalho não está em `allow_headers` | Libere o cabeçalho na API (Módulo 09) |
| Comparar nomes de cabeçalho diferenciando maiúsculas | Os nomes não diferenciam | Use `headers.get(...)`, que já resolve isso |

## // Prática guiada

1. Rode a API (Módulo 03) e execute `curl -v "http://127.0.0.1:8000/grupos?limit=2"`. Identifique, nas linhas `>`, os cabeçalhos que o `curl` enviou sozinho.
2. Rode o mesmo comando com `-H "Origin: http://127.0.0.1:5500"` e compare as linhas `<`: o que mudou (e o que continua faltando, se a API ainda estiver sem CORS)?
3. Rode um `POST` com `-H "Content-Type: application/json"` e leia o `location` e o `content-length` da resposta.
4. Rode o mesmo `POST` **sem** o `-H` e leia o `422`.
5. Na aba Rede de qualquer site, clique em um pedido e localize os cabeçalhos do pedido e da resposta.

## // Pratique sozinho

> **DESAFIO**
> Escreva, em um arquivo, uma tabela com três colunas: o cabeçalho, quem o coloca (navegador, o seu JavaScript ou a API) e o que acontece se ele faltar. Preencha para: `Content-Type` no pedido, `Origin`, `Location`, `Access-Control-Allow-Origin` e `X-Total-Count`. Depois confira cada linha com o que viu no `curl -v`.

## // Aplicando no projeto da semana

1. No `anotacoes-http.md`, acrescente a seção "Cabeçalhos" com a tabela do desafio.
2. Anote, em uma linha, qual cabeçalho você precisa expor para que a página leia o total de grupos.
3. Se você versiona o projeto com Git, faça um commit: `git commit -m "Anota os cabeçalhos da integração"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> A API devolve `x-total-count: 6`, e a aba Rede do navegador mostra o cabeçalho na resposta. Mesmo assim, o seu JavaScript recebe `null` ao pedir `resposta.headers.get("X-Total-Count")`. O que está acontecendo?

Resposta: a página e a API estão em origens diferentes, e o navegador só entrega ao JavaScript os cabeçalhos básicos e os listados em `Access-Control-Expose-Headers`. A aba Rede mostra tudo o que **chegou** ao navegador, mas o JavaScript só pode **ler** o que o servidor permitiu. A solução está na API: `expose_headers=["X-Total-Count"]`.

## // Resumo do módulo

- [ ] Sei o que é um cabeçalho e que o nome não diferencia maiúsculas de minúsculas.
- [ ] Sei os cabeçalhos principais do pedido e da resposta e quem coloca cada um.
- [ ] Sei que alguns cabeçalhos só o navegador define.
- [ ] Sei ler cabeçalhos em JavaScript com `resposta.headers.get(...)`.
- [ ] Sei que, entre origens diferentes, só os cabeçalhos básicos e os expostos são legíveis.
- [ ] Sei por que o `Content-Type: application/json` é obrigatório ao enviar JSON.

---

**Próximo módulo:** `03-a-api-que-vamos-usar.md`, hora de ligar a API da semana e testá-la, antes de chamá-la pela página.

`Material de Estudo // Coffee & Code`

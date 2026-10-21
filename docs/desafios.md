# Desafios, Semana 06

Português · [English](../docs-eng/challenges.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

Desafios opcionais, organizados pelos módulos da semana. Nenhum é obrigatório para a entrega básica; veja `entregavel.md` para o que é obrigatório. Use estes desafios se terminou os módulos principais e quer ir além. Em cada bloco, os desafios para quem **está começando** vêm primeiro, e os para quem **já tem experiência**, depois.

---

## // HTTP, cabeçalhos e a API (Módulos 01 a 03)

**Se você está começando**
- Abra a aba Rede em três sites e, para cada um, encontre uma resposta com `Content-Type` diferente (HTML, imagem, JSON ou estilo). Anote o tipo e o que o navegador faz com cada um.
- Rode o `curl -v` contra a API e marque, com as suas palavras, qual cabeçalho do pedido e qual da resposta você acha mais importante para a integração, e por quê.

**Se você já tem experiência**
- Pesquise o código `429 Too Many Requests` e o cabeçalho `Retry-After`. Escreva como a página deveria reagir se a API passasse a devolvê-los.
- Pesquise o cabeçalho `Cache-Control` e a resposta `304 Not Modified`. Descreva, em um parágrafo, como um `ETag` evitaria reenviar a lista de matérias (que quase nunca muda).

---

## // JavaScript, DOM e código assíncrono (Módulos 04 a 07)

**Se você está começando**
- Escreva uma função `agruparPorMateria(grupos)` que receba a lista de grupos e devolva um objeto em que a chave é o `materia_id` e o valor é o array dos grupos daquela matéria. Teste no console.
- Escreva uma função `async` `buscarVariosGrupos(ids)` que busque os grupos de uma lista de identificadores **em paralelo** com `Promise.all`, e devolva só os que existem (ignorando os `404`).

**Se você já tem experiência**
- Pesquise `AbortController` e use-o para **cancelar** um pedido de busca em andamento quando a pessoa digita outra letra. Compare com a solução do número do pedido (Módulo 10): qual é mais eficiente, e por quê?
- Pesquise a diferença entre `Promise.all`, `Promise.allSettled` e `Promise.race`, e dê um exemplo desta semana em que cada uma seria a melhor escolha.

---

## // Origem e CORS (Módulos 08 e 09)

**Se você está começando**
- Suba o servidor da página em duas portas (5500 e 5501) e escreva, em uma tabela, qual das duas origens a API autoriza e por quê. Depois, autorize a segunda e prove com `curl`.
- Escreva o `curl` do preflight de um `DELETE` e preveja o resultado antes de rodar. Depois, remova `"DELETE"` de `allow_methods` e repita.

**Se você já tem experiência**
- Use `allow_origin_regex` no lugar da lista fixa para autorizar qualquer porta de `127.0.0.1` (por exemplo, de 5500 a 5599). Escreva os testes: o que passa e o que **não** deve passar? Qual é o risco de uma expressão regular frouxa?
- Pesquise `Access-Control-Allow-Credentials` e como os cookies mudam as regras do CORS. Explique, em um parágrafo, por que o `Access-Control-Allow-Origin: *` não pode acompanhar credenciais, e o que o Starlette faz quando alguém tenta (Módulo 09).

---

## // A página: lista, formulário, edição e paginação (Módulos 10 a 14)

**Se você está começando**
- Mostre ao lado do nome de cada grupo um selo com as vagas: "poucas vagas" se o limite for menor que 5, e "muitas vagas" no resto. Use só `textContent` e uma classe de CSS.
- Acrescente um botão **Limpar filtros**, que esvazie a busca, volte o filtro para "Todas" e volte para a página 1.

**Se você já tem experiência**
- Substitua `window.confirm` por uma pequena janela de confirmação feita com o elemento `<dialog>`. Cuide do teclado (Esc cancela) e do foco.
- Faça a página lembrar a última busca e a página atual, guardando-as na **URL** (`?q=...&pagina=2`) com `URLSearchParams` e `history.replaceState`, de modo que recarregar a página (ou copiar o endereço) preserve o estado.

---

## // Middlewares e padronização do JSON (Módulos 15 a 17, trilha veterano)

- Escreva um middleware que **recuse** corpos maiores que 10 KB com um `413`, no formato único de erro, antes de a rota ler o corpo. Onde ele deve ficar na ordem? E o CORS?
- Acrescente ao envelope de sucesso o campo `meta.versaoDaApi`, e ao de erro um campo `meta.documentacao` com o endereço do `/docs`. Atualize o Swagger e os testes.
- Pesquise o formato **RFC 9457** (*Problem Details for HTTP APIs*) e compare com o formato único de erro desta semana: o que cada um tem que o outro não tem?
- Escreva um teste que garanta que **toda** rota da API veterano devolve um `requestId` em `meta` (percorrendo o `/openapi.json`) e prove, ao contrário, que ele falha se uma rota esquecer o envelope.

---

## // Desafio geral (todos)

Escolha um defeito **real** que você encontrou (ou provocou) durante a semana, por exemplo, o `X-Total-Count` que chega como `null`, o preflight que devolve `400`, ou a resposta velha que sobrescreve a nova. Escreva um **relatório de uma página**, com: o sintoma que a pessoa vê, a causa, como você a descobriu (qual aba, qual pedido, qual cabeçalho) e a correção. Esse é o exercício mais parecido com o trabalho de quem integra sistemas.

---

`Material de Estudo // Coffee & Code`

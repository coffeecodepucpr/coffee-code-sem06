# Coffee & Code | SEM 06 | API RESTful Central (Parte 2: Integração)

Português · [English](README.en.md)

```text
> module: sem-06
> tema: api restful central (integração)
> status: online
> coffee loaded
```

Material da **Semana 06** da trilha do Coffee & Code, clube de tecnologia fundado por estudantes de Engenharia de Software da PUCPR e aberto a todos que querem aprender construindo.

Esta semana leva uma pessoa que nunca ligou uma página a uma API até uma **aplicação full-stack conectada**, com listagem, busca, criação, edição, exclusão e paginação: HTTP, cabeçalhos, CORS e integração.

> **Semana independente:** ela não exige nenhuma outra semana do clube. A API vem pronta, e o HTTP, o JavaScript e o CORS são apresentados do zero.

> **Sobre o idioma:** o material em inglês fica em [`docs-eng/`](docs-eng/), com a mesma estrutura de [`docs/`](docs/); os READMEs têm versão em inglês com o sufixo `.en.md`. Os diagramas e o código dos exemplos executáveis (nomes, mensagens e comentários) permanecem em português.

## Por onde começar

**[docs/00-comece-aqui.md](docs/00-comece-aqui.md)**: leia este primeiro. Ele apresenta o panorama da semana e a ideia de integração full-stack.

Depois, siga os módulos na ordem. Os módulos `01` a `14` formam a trilha principal:

| # | Módulo | Sobre |
|---|---|---|
| 01 | [HTTP visto do navegador](docs/01-http-visto-do-navegador.md) | Pedido, resposta, métodos, status e a aba Rede |
| 02 | [Headers](docs/02-headers.md) | Os cabeçalhos do pedido e da resposta, e quais o JavaScript lê |
| 03 | [A API que vamos usar](docs/03-a-api-que-vamos-usar.md) | Executar e testar a API da semana |
| 04 | [JavaScript essencial para integrar](docs/04-javascript-essencial-para-integrar.md) | Valores, objetos, arrays, funções, JSON e módulos |
| 05 | [O DOM: ler e mudar a página](docs/05-o-dom-ler-e-mudar-a-pagina.md) | O DOM, os eventos e a segurança do `textContent` |
| 06 | [Assíncrono: promises e async/await](docs/06-assincrono-promises-e-async-await.md) | Promises, `async` e `await` |
| 07 | [fetch: o primeiro pedido](docs/07-fetch-o-primeiro-pedido.md) | `fetch`, erro de rede e erro HTTP |
| 08 | [Servindo o front-end e a origem](docs/08-servindo-o-front-end-e-a-origem.md) | Servir a página, origem e política de mesma origem |
| 09 | [CORS: o navegador bloqueia](docs/09-cors-o-navegador-bloqueia.md) | CORS, preflight, configuração e diagnóstico |
| 10 | [Listando grupos na página](docs/10-listando-grupos-na-pagina.md) | A lista, os estados da tela, a busca e o filtro |
| 11 | [Enviando dados: formulário e POST](docs/11-enviando-dados-formulario-e-post.md) | O formulário, o `POST` e os erros por campo |
| 12 | [Editar e apagar: PATCH e DELETE](docs/12-editar-e-apagar-patch-e-delete.md) | `PATCH`, `DELETE` e a resposta sem corpo |
| 13 | [Paginação e cabeçalhos expostos](docs/13-paginacao-e-cabecalhos-expostos.md) | Paginação e o `X-Total-Count` exposto |
| 14 | [Projeto guiado](docs/14-projeto-guiado.md) | A aplicação completa e o roteiro de verificação |

Os módulos `15` e `16` são a **trilha veterano**, e o módulo `17` é um bônus dessa trilha. Todos são opcionais e podem ser lidos depois do essencial:

| # | Módulo | Sobre |
|---|---|---|
| 15 | [Middlewares de requisição](docs/15-middlewares-de-requisicao.md) | Identificador, tempo, log e pega-tudo |
| 16 | [Padronização do JSON](docs/16-padronizacao-do-json.md) | Envelope, erro único e camelCase |
| 17 | [Testando a integração](docs/17-testando-a-integracao.md) | Bônus: `pytest` e `jsdom` |

E, para consultar quando precisar:

- [Exemplos executáveis](docs/example/README.md): as versões da API e da página, para consulta
- [Desafios](docs/desafios.md): opcionais, para ir além do pedido
- [Entregável](docs/entregavel.md): checklist final antes de fechar a semana

## Os exemplos executáveis

A pasta [`docs/example/`](docs/example/) tem as duas pontas do Buscador de Grupos de Estudo, em versões que acompanham a trilha:

- `api-inicial/` e `frontend-inicial/`: o ponto de partida, antes do CORS e da integração.
- `api/` e `frontend/`: a versão final da trilha principal, com CORS configurado.
- `veterano/`: a versão com middlewares de requisição e o JSON padronizado.
- `testes/`: os testes da API (`pytest`) e os da página (`jsdom`).

Tudo foi executado, e as respostas citadas nos módulos vêm dessas execuções. Veja o [README da pasta](docs/example/README.md) para instalar e rodar.

É material de **consulta, não gabarito**: o exemplo serve para você ver uma solução possível quando travar, não para copiar.

## O entregável

Ao final da Semana 06, o repositório do **seu projeto** (não este aqui) deve ter uma pasta `projeto-fullstack` com as duas pontas:

```text
projeto-fullstack/
├── api/
│   ├── main.py
│   ├── dados.py
│   ├── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── estilos.css
│   ├── api.js
│   ├── ui.js
│   └── app.js
└── README.md         ← como rodar as duas pontas
```

As duas precisam rodar ao mesmo tempo, em dois terminais, e a página, aberta em `http://127.0.0.1:5500`, deve listar, criar, editar e apagar grupos pela API, com o CORS configurado por lista exata de origens.

O checklist completo está em [docs/entregavel.md](docs/entregavel.md).

## Entregas da turma

Ainda não há entregas da Semana 06. Quer ser a primeira pessoa? Veja [como entregar](entregas/README.md).

## Versões e data de consulta

Material verificado com **FastAPI 0.143.0**, Pydantic 2.13.5, Starlette 1.7.0, Uvicorn 0.54.0 e Python 3.12.3. A documentação oficial do FastAPI e a do MDN (sobre CORS) foram consultadas em **08/10/2026**. O FastAPI é uma biblioteca de versão `0.x` e muda com frequência: se algo divergir do que está aqui, a documentação oficial é a referência.

**O que foi e o que não foi testado em um navegador.** O servidor foi testado com requisições reais (incluindo o preflight do CORS), e o JavaScript da página foi testado com `jsdom`, um simulador de navegador, contra a API de verdade. **O comportamento do próprio navegador** (o bloqueio do CORS, a aba Rede, os cabeçalhos escondidos entre origens) segue a documentação do MDN e **não foi reproduzido em um navegador** durante a produção do material. As mensagens de erro de navegador citadas são o "texto típico" e variam entre navegadores.

## Projeto contínuo

Todos os módulos usam o mesmo projeto fictício do clube: o **Buscador de Grupos de Estudo**, uma aplicação em que estudantes procuram grupos de estudo por matéria. Esta semana liga a página à API que cuida dos grupos e das matérias. Se você tem um projeto próprio, o raciocínio de cada módulo se aplica da mesma forma: só troque o nome.

## Como funciona

O Coffee & Code é **100% online**. Cada módulo foi escrito para ser autossuficiente: você estuda no seu ritmo, pode avançar mais rápido, voltar em semanas anteriores e consultar o material durante o projeto.

Os encontros semanais, também online, existem para tirar dúvidas, revisar conceitos, programar junto e mostrar o que você produziu, **não para dar aula**:

- **quarta-feira**: 20h00 às 21h30
- **sábado**: 10h00 às 11h30

Os dois trabalham o mesmo conteúdo. Escolha o que couber melhor na sua semana, e não precisa ficar o horário inteiro na call.

## Travou?

Chega no encontro ou no Discord com uma pergunta específica. `"o console fala de CORS, e na aba Rede o GET /grupos volta 200 sem o cabeçalho access-control-allow-origin"` costuma ser resolvido muito mais rápido do que `"minha página não funciona"`.

Nesta semana, a aba Rede é a sua primeira parada: o método, o endereço, o status e os cabeçalhos da resposta dividem quase qualquer problema ao meio.

E lembra: não saber alguma coisa não é problema. Saber pesquisar faz parte da área.

## Diagramas

Todos os diagramas usados nos módulos estão em [`docs/assets/svg/`](docs/assets/svg/), em formato SVG.

## Semanas anteriores

- [SEM 01: Kickoff & Design System](https://github.com/coffeecodepucpr/coffee-code-sem01)
- [SEM 02: Interface Web (Parte 1: Layout)](https://github.com/coffeecodepucpr/coffee-code-sem02)
- [SEM 03: Interface Web (Parte 2: Dinâmica)](https://github.com/coffeecodepucpr/coffee-code-sem03)
- [SEM 04: Modelagem de Dados](https://github.com/coffeecodepucpr/coffee-code-sem04)
- [SEM 05: API RESTful Central (Parte 1: CRUD)](https://github.com/coffeecodepucpr/coffee-code-sem05)

Trilha completa e próximas semanas: [perfil do Coffee & Code](https://github.com/coffeecodepucpr)

---

```text
HTTP 418: I'm a teapot
> ready to code
```

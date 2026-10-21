# Entregável, Semana 06

Português · [English](../docs-eng/deliverable.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

Use este arquivo como checklist final antes de considerar a Semana 06 concluída. Ele reúne o que é **obrigatório**; os desafios extras em `desafios.md` e os Módulos 15 a 17 da trilha veterano são opcionais.

## // O que você deve ter em mãos agora

Se você seguiu os módulos em ordem, a sua pasta `projeto-fullstack` deve conter uma subpasta `api` (com o `main.py`, o `dados.py`, o `schemas.py` e o `requirements.txt`), uma subpasta `frontend` (com o `index.html`, o `estilos.css`, o `api.js`, o `ui.js` e o `app.js`) e um `README.md` na raiz. As duas pontas devem rodar ao mesmo tempo, e a página, aberta em `http://127.0.0.1:5500`, deve listar, criar, editar e apagar grupos pela API.

## // Checklist do entregável

### > Ambiente e execução

- [ ] A API tem um ambiente virtual, e o `.venv` não está no repositório (se você usa Git).
- [ ] O `requirements.txt` fixa a faixa de versões do FastAPI (`fastapi[standard]>=0.143,<0.144`).
- [ ] A API liga com `fastapi dev main.py`, e a página é servida com `python3 -m http.server 5500 --bind 127.0.0.1`.
- [ ] O `README.md` explica como rodar as **duas** pontas, em dois terminais, e quais são as duas origens.

### > CORS

- [ ] O `CORSMiddleware` está configurado com uma **lista exata** de origens (`http://127.0.0.1:5500` e `http://localhost:5500`), e não com `"*"`.
- [ ] `allow_methods` lista só os métodos que a página usa (`GET`, `POST`, `PATCH` e `DELETE`).
- [ ] `allow_headers` libera o `Content-Type`, e `expose_headers` expõe o `X-Total-Count`.
- [ ] Você testou o preflight de `POST`, `PATCH` e `DELETE` com `curl` e o cabeçalho `Origin`, e guardou os comandos.

### > A página e a integração

- [ ] A página lista os grupos da API, mostrando o nome da matéria (e não só o número).
- [ ] A busca por nome e o filtro por matéria funcionam, e voltam à página 1.
- [ ] O formulário **cria** grupos, e a página **edita** e **apaga** (com confirmação) usando `PATCH` e `DELETE`.
- [ ] Todas as chamadas à API passam pelo `api.js`, e o endereço da API aparece em **um** lugar só.
- [ ] Os dados vindos da API entram na página com `textContent`, **nunca** com `innerHTML`.

### > Estados da tela e erros

- [ ] A lista mostra os quatro estados: carregando, sucesso, vazio ("Nenhum grupo encontrado.") e erro.
- [ ] Um erro de validação (`422`) aparece **no campo certo**, e um nome repetido (`409`) tem uma mensagem clara.
- [ ] Com a API desligada, a página avisa ("API fora do ar") em vez de quebrar.
- [ ] O botão **Salvar** fica desabilitado durante o envio e volta ao normal, mesmo se der erro.
- [ ] A chamada `fetch` confere `resposta.ok` (ou usa uma função que o faz), e não confia só no `catch`.

### > Paginação

- [ ] A página usa `limit` e `offset`, e mostra "Página N de M (T grupos)", com a concordância certa.
- [ ] Os botões **Anterior** e **Próxima** são desabilitados nas pontas.
- [ ] O total vem do `X-Total-Count`, e a página trata o caso de ele chegar `null`.
- [ ] Apagar o último item da última página leva à última página que existe, e não a uma página vazia.

### > Documentação

- [ ] O `README.md` descreve como rodar, as origens, a lista de rotas usadas pela página e o que cada arquivo faz.
- [ ] O `README.md` registra os passos do roteiro de verificação do Módulo 14 que você percorreu, com o resultado de cada um.

### > Trilha veterano (opcional)

- [ ] O `IdentificadorDoPedido` e o `PegaTudo` estão na ordem certa (o `PegaTudo` por dentro do CORS), e o `500` chega à página em JSON, com o cabeçalho de CORS.
- [ ] A API devolve o envelope `{ dados, meta }` e o erro `{ erro, meta }`, com os nomes em camelCase.
- [ ] A página decide os erros pelo `erro.codigo`, e mostra o `requestId` nas mensagens de erro.
- [ ] (Bônus) Os testes da API passam com `pytest -q`, e os da página, com `npm test`.

## // O que NÃO é esperado nesta semana

- Não é esperado nenhum banco de dados: os dados ficam em memória e voltam ao estado inicial quando a API reinicia.
- Não é esperado login, cookies, tokens nem qualquer controle de acesso.
- Não é esperado publicar a aplicação na internet. Use sempre `fastapi dev` e o servidor com `--bind 127.0.0.1`.
- Não é esperado usar frameworks de front-end (React, Vue e outros): a página é HTML, CSS e JavaScript puro.
- Não é esperado um visual sofisticado: o CSS pronto do material serve.

> **A INTEGRAÇÃO CORRETA VALE MAIS QUE O VISUAL**
> Uma página simples, que mostra cada estado (carregando, vazio, erro, API fora do ar), recusa dados inválidos no campo certo e nunca escreve dados de fora com `innerHTML`, vale mais nesta avaliação do que uma tela bonita que quebra quando a API responde um erro. O que está sendo avaliado esta semana é a **conversa entre as duas pontas**.

## // Como revisar antes de entregar

> **O TESTE MAIS IMPORTANTE DESTA SEMANA**
> Em uma pasta nova e vazia, copie só os arquivos do projeto (sem o `.venv`), crie o ambiente virtual da API, instale as dependências e ligue as **duas** pontas, cada uma em um terminal. Depois, percorra os 17 itens do roteiro do Módulo 14, olhando a aba Rede e o Console. Se tudo bater, a sua entrega funciona em qualquer computador, e não só no seu.

Se algum item falhar, comece **sempre** pela aba Rede e siga a árvore de diagnóstico do Módulo 09: a primeira pergunta ("a aba mostra uma resposta da API?") divide o problema ao meio.

## // Onde tirar dúvidas

Os encontros semanais do Coffee & Code existem para isso. "A minha lista não aparece, o console fala de CORS, e na aba Rede o pedido `GET /grupos` está com status 200 e sem o cabeçalho `access-control-allow-origin`" é muito mais rápido de resolver do que "a minha página não funciona". Inclua sempre o método e o endereço do pedido, o código de status, os cabeçalhos da resposta e a mensagem do Console.

Se quiser se aprofundar além do que foi pedido, veja `desafios.md` e a trilha veterano, nos Módulos 15 a 17.

Bom trabalho até aqui.

`Material de Estudo // Coffee & Code`

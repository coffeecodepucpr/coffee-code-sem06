# Módulo 03, A API que Vamos Usar

Português · [English](../docs-eng/03-the-api-we-will-use.md)

`SEM 06 // API RESTful Central, Parte 2: Integração`

---

## // Antes de começar

Esta semana é sobre ligar uma página a uma API, e a API **já vem pronta**: você não vai escrevê-la, só executá-la, testá-la e, no Módulo 09, acrescentar uma configuração. Este módulo mostra como colocá-la no ar e como conhecê-la bem antes de chamá-la pela página. Conhecer o outro lado da conversa evita metade dos problemas de integração.

## // O problema: não dá para integrar com o que não se conhece

Para chamar uma API, a página precisa saber quais endereços existem, que métodos aceitam, que dados esperam e que respostas devolvem. Descobrir isso **pela página** mistura dois problemas (a API e o JavaScript) e torna cada erro ambíguo. A solução é testar a API primeiro, sozinha, com as ferramentas que não têm CORS: o Swagger e o `curl`.

## // Colocando a API no ar

A API está na pasta `example/api-inicial` do material. Copie-a para `projeto-fullstack/api`. Você vai precisar de **Python 3.10 ou superior**. Confira a versão em um terminal:

| Sistema | Comando |
|---|---|
| macOS e Linux | `python3 --version` |
| Windows | `py --version` |

A API foi testada com o Python 3.12.3. Se a versão for menor que 3.10, instale uma mais nova em `python.org` antes de continuar.

### > 1. O ambiente virtual

Dentro da pasta `projeto-fullstack/api`, crie um ambiente virtual, uma pasta isolada para as bibliotecas do projeto, e ative-o:

| Passo | macOS e Linux | Windows |
|---|---|---|
| Criar | `python3 -m venv .venv` | `py -m venv .venv` |
| Ativar | `source .venv/bin/activate` | `.venv\Scripts\activate` |

Quando o ambiente está ativo, o terminal mostra `(.venv)` no começo da linha.

> **SOBRE O WINDOWS**
> Os comandos desta semana foram executados em **Linux** e **não foram testados no Windows nem no macOS**. A criação do ambiente segue a documentação do Python. Se a ativação falhar no PowerShell por uma regra de segurança do computador, use o Prompt de Comando (`cmd`).

### > 2. Instalar o FastAPI

O arquivo `requirements.txt` da pasta lista o que a API precisa, em uma linha:

```
fastapi[standard]>=0.143,<0.144
```

```
pip install -r requirements.txt
```

A faixa de versões está **fixada** de propósito: o FastAPI é uma biblioteca de versão `0.x`, e versões novas podem mudar comportamentos.

### > 3. Ligar a API

```
fastapi dev main.py
```

O terminal mostra algo como isto (o começo da saída; os ícones que o programa desenha foram omitidos aqui):

```
Starting FastAPI in development mode
Using import string: main:app
Server started at http://127.0.0.1:8000
Documentation at http://127.0.0.1:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

A API fica em `http://127.0.0.1:8000`. O modo `dev` recarrega sozinho quando você salva um arquivo, e atende **só o seu computador**. Para parar o servidor, pressione **Ctrl+C**. Deixe este terminal aberto: a API precisa continuar rodando.

> **USE SEMPRE FASTAPI DEV, E NÃO FASTAPI RUN**
> O comando `fastapi run` atende em `0.0.0.0`, ou seja, **toda a sua rede**, e esta API não tem nenhum controle de acesso. Enquanto você estuda, use só o `dev`.

## // O mapa da API

Abra `http://127.0.0.1:8000/docs`. Esta é a documentação interativa (o Swagger), gerada pelo próprio FastAPI. Ela precisa de internet para carregar os seus arquivos visuais: sem conexão, a página abre em branco, embora a API funcione. As rotas:

| Método | Rota | O que faz | Sucesso | Erros possíveis |
|---|---|---|---|---|
| `GET` | `/materias` | Lista as seis matérias | `200` | |
| `GET` | `/grupos` | Lista os grupos, com busca e paginação | `200` | `422` (parâmetro inválido) |
| `GET` | `/grupos/{grupo_id}` | Busca um grupo | `200` | `404`, `422` |
| `POST` | `/grupos` | Cria um grupo | `201` | `409`, `422` |
| `PATCH` | `/grupos/{grupo_id}` | Altera só alguns campos | `200` | `404`, `409`, `422` |
| `DELETE` | `/grupos/{grupo_id}` | Apaga um grupo | `204` | `404` |

O `GET /grupos` aceita quatro parâmetros opcionais, no fim da URL:

| Parâmetro | O que faz | Padrão e limites |
|---|---|---|
| `q` | Busca por parte do nome, sem diferenciar maiúsculas | Sem filtro |
| `materia_id` | Só os grupos dessa matéria | Sem filtro |
| `limit` | Quantos grupos devolver | 10, entre 1 e 100 |
| `offset` | Quantos grupos pular | 0 |

A resposta já vem **ordenada pelo nome** e traz o cabeçalho `x-total-count`, com o total de grupos que atendem aos filtros, antes de cortar a página. Os dados vivem **em memória**: sempre que a API reinicia (inclusive quando você salva um arquivo), eles voltam ao estado inicial.

## // O formato dos dados

Um grupo, como a API devolve:

```json
{
  "nome_grupo": "Modelagem e SQL",
  "materia_id": 3,
  "max_participantes": 8,
  "descricao": "Encontros online às terças e aos sábados",
  "grupo_id": 3,
  "criado_em": "2026-09-03T12:00:00Z"
}
```

Uma matéria:

```json
{"materia_id": 1, "nome": "Cálculo I", "codigo": "MAT101"}
```

E as regras que a API aplica, que a página vai precisar respeitar e tratar:

| Campo | Regra | Se for violada |
|---|---|---|
| `nome_grupo` | Entre 3 e 60 caracteres | `422` |
| `materia_id` | Precisa existir | `422` |
| `max_participantes` | Entre 2 e 50 (padrão 10) | `422` |
| `descricao` | Até 200 caracteres, opcional | `422` |
| Nome repetido na mesma matéria | Sem diferenciar maiúsculas | `409` |

No `PATCH`, os campos `nome_grupo`, `materia_id` e `max_participantes` **não aceitam** `null`: omita o campo para não alterá-lo. Só a `descricao` aceita `null`, que a apaga.

## // Testando a API sozinha

Antes de qualquer JavaScript, faça três testes:

**Pelo Swagger:** em `/docs`, expanda `GET /grupos`, clique em **Try it out** e depois em **Execute**. Leia o código `200`, o corpo e o cabeçalho `x-total-count`.

**Pela linha de comando, uma listagem:**

```
curl -i "http://127.0.0.1:8000/grupos?limit=2"
```

**Pela linha de comando, uma criação:**

```
curl -i -X POST http://127.0.0.1:8000/grupos \
  -H "Content-Type: application/json" \
  -d '{"nome_grupo": "Cálculo II na prática", "materia_id": 1}'
```

A resposta é um `201 Created`, com o cabeçalho `location: /grupos/7` e o grupo criado no corpo. Reinicie a API (ou salve o `main.py`) para devolver os dados ao estado inicial.

## // Bom exemplo × mau exemplo

**Mau exemplo**: descobrir a API pela página:

```
"Vou escrever a página inteira e ver o que a API devolve."
```

Cada erro vira um mistério: foi a API, o JavaScript, o CORS? Você perde horas para descobrir algo que um `curl` mostraria em um segundo.

**Bom exemplo**: conhecer a API primeiro, com um `curl` para cada rota:

```
1. Listar, buscar, criar, alterar e apagar com o curl.
2. Provocar cada erro de propósito (404, 409, 422) e ler a resposta.
3. Só então escrever o JavaScript, sabendo o que esperar.
```

## // Erros comuns

| Erro | Por que acontece | Como corrigir |
|---|---|---|
| `fastapi: command not found` | O ambiente virtual não está ativo | Ative o ambiente (`(.venv)` no terminal) |
| `Address already in use` | Outra coisa já usa a porta 8000 | Pare o outro servidor, ou use `fastapi dev main.py --port 8001` (e ajuste o endereço da página) |
| O Swagger abre em branco | Sem internet para carregar os arquivos visuais | Conecte-se e recarregue |
| Os grupos criados sumiram | A API reiniciou, e os dados vivem em memória | É o esperado: recrie os dados |
| `422` ao testar o `POST` pelo `curl` | Faltou `-H "Content-Type: application/json"` | Acrescente o cabeçalho |
| `ModuleNotFoundError` ao ligar | O comando foi dado fora da pasta da API | Entre na pasta que contém o `main.py` |

## // Prática guiada

1. Copie `example/api-inicial` para `projeto-fullstack/api`.
2. Crie e ative o ambiente virtual e rode `pip install -r requirements.txt`.
3. Ligue a API com `fastapi dev main.py` e abra o `/docs`.
4. Teste, pelo Swagger, cada uma das seis rotas da tabela.
5. Repita três delas pelo `curl`: a listagem com `limit` e `offset`, a criação, e o `DELETE` do grupo que você criou.
6. Provoque de propósito um `404` (`GET /grupos/99`), um `409` (crie o mesmo grupo duas vezes) e um `422` (nome com 2 letras).

## // Pratique sozinho

> **DESAFIO**
> Sem olhar a tabela, descubra pelo `curl` e pelo Swagger: quantos grupos existem ao todo; qual é o nome do grupo que aparece primeiro com `limit=1`; e quantos grupos a matéria 3 tem. Anote o comando que usou para cada resposta.

## // Aplicando no projeto da semana

1. Deixe a API instalada e funcionando em `projeto-fullstack/api`.
2. Crie, na raiz do projeto, um `README.md` com a seção "Como rodar a API" e os comandos deste módulo.
3. Se você versiona o projeto com Git, crie um `.gitignore` com a linha `.venv/` e faça um commit: `git commit -m "Adiciona a API ao projeto"`.

## // Checkpoint

> **ANTES DE SEGUIR, PENSE NISTO**
> Por que é melhor testar a API pelo `curl` e pelo Swagger **antes** de escrever o JavaScript que a chama?

Resposta: porque o `curl` e o Swagger não têm as restrições do navegador (como o CORS), e isolam a API da página. Se o `curl` funciona, você sabe que a API está certa, e qualquer erro que aparecer depois está na página ou na ligação entre as duas. Sem esse teste, um mesmo sintoma ("a lista não aparece") pode ter cinco causas diferentes.

## // Resumo do módulo

- [ ] Tenho o Python 3.10 ou superior e um ambiente virtual ativo.
- [ ] Instalei as dependências com `pip install -r requirements.txt`.
- [ ] Sei ligar a API com `fastapi dev main.py` e por que não usar `fastapi run`.
- [ ] Conheço as seis rotas, os parâmetros do `GET /grupos` e o cabeçalho `x-total-count`.
- [ ] Conheço as regras dos dados e os erros `404`, `409` e `422`.
- [ ] Sei testar a API sozinha pelo Swagger e pelo `curl`.

---

**Próximo módulo:** `04-javascript-essencial-para-integrar.md`, a API está no ar. Agora, a linguagem da outra ponta: o JavaScript.

`Material de Estudo // Coffee & Code`

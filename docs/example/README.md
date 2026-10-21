# Exemplos executáveis, Semana 06

Português · [English](../../docs-eng/example/README.md)

Esta pasta reúne tudo que pode ser executado nesta semana. É referência, e não gabarito obrigatório: a sua aplicação precisa aplicar os mesmos conceitos, não ser igual a esta.

## Ambiente em que tudo foi testado

| Item | Versão |
|---|---|
| Python | 3.12.3 (o FastAPI exige 3.10 ou superior) |
| FastAPI | 0.143.0 |
| Starlette | 1.7.0 |
| Pydantic | 2.13.5 |
| Uvicorn | 0.54.0 |
| pytest | 9.1.1 |
| httpx2 | 2.13.1 |
| Node (só para os testes da página) | 22.22.2 |
| jsdom (só para os testes da página) | 30.1.2 |
| Sistema | Linux. **Não foi testado no Windows nem no macOS** |
| Navegador | **Nenhum.** O CORS foi testado pelo lado do servidor, e o JavaScript, em um simulador (`jsdom`) |

A documentação oficial do FastAPI e a do MDN foram consultadas em **08/10/2026**. O FastAPI é uma biblioteca de versão `0.x` e muda com frequência: se algo divergir do que está aqui, a documentação oficial é a referência.

## Qual pasta usar

| Pasta | Módulos | O que é |
|---|---|---|
| `api-inicial/` | 03, 08 | A API **sem CORS**: o ponto de partida, e a que mostra o problema |
| `api/` | 09 a 14 | A mesma API, **com o CORS configurado**: o resultado do Módulo 09 |
| `frontend-inicial/` | 05, 08, 09 | O HTML e o CSS prontos, com o `app.js` vazio |
| `frontend/` | 07, 10 a 14 | A página completa: `api.js`, `ui.js` e `app.js` |
| `veterano/api/` | 15, 16 | A API com middlewares, envelope `{ dados, meta }`, erro único e camelCase |
| `veterano/frontend/` | 16 | A página adaptada ao formato da API veterano |
| `testes/` | 17 | Os testes da API (`pytest`) e da página (`jsdom`) |

## Como rodar a trilha principal

Em um terminal, dentro de `api/` (ou `api-inicial/`):

```
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

Em **outro** terminal, dentro de `frontend/`:

```
python3 -m http.server 5500 --bind 127.0.0.1
```

Abra `http://127.0.0.1:5500`. A documentação da API abre em `http://127.0.0.1:8000/docs`. Use sempre `fastapi dev`, e não `fastapi run`: o `dev` atende só o seu computador, e o `run` atende toda a rede. E use sempre o `--bind 127.0.0.1` no servidor da página.

## Como rodar a trilha veterano

Os mesmos comandos, com a API de `veterano/api/` e a página de `veterano/frontend/`. As duas precisam ser da **mesma versão**: a página veterano espera o envelope de resposta, e a página principal espera a lista crua.

## Como rodar os testes

**API** (dentro do ambiente virtual da API, com `pip install -r testes/requirements-testes.txt`). Rode **cada pasta separadamente**:

```
cd testes/api
pytest -q            # 22 testes

cd ../veterano
pytest -q            # 18 testes
```

**Página** (precisa do Node, veja a versão acima, e da API ligada em outro terminal):

```
cd testes/frontend
npm install
npm test                       # 12 passos
npm run test:fora-de-ordem     # respostas atrasadas
npm run test:api-fora          # com a API DESLIGADA
```

Para a página veterano, defina `FRONTEND=../../veterano/frontend` antes do comando (a sintaxe no Windows é diferente e não foi testada). Os testes da página mexem nos dados em memória da API: reinicie a API (salvando o `main.py`) entre duas execuções.

## O que os testes não cobrem

O teste da página usa o `fetch` do Node dentro do `jsdom`, e **o Node não aplica o CORS**. Portanto, a conferência final do CORS precisa ser feita em um **navegador de verdade**, com o roteiro do Módulo 14. Os testes da API conferem os cabeçalhos que o navegador pediria.

## Regras de segurança

- Rode a API sempre com `fastapi dev`, e o servidor da página sempre com `--bind 127.0.0.1`. Nada aqui tem controle de acesso.
- A rota `GET /diagnostico/erro`, da API veterano, existe só para estudar o `500`: em um sistema real, remova-a.
- O ambiente virtual (`.venv`) e a pasta `node_modules` nunca vão para o repositório.
- Os dados vivem em memória e voltam ao estado inicial a cada reinício da API.

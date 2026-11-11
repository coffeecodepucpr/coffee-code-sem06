# Resumo de preço com IA (Semana 08 — Smart Hub)

Adaptação do notebook da **trilha veterana** (`Copy_of_02_SEM08_Resumos_por_API.ipynb`)
pro Estom de verdade: em vez de resumir uma vaga de emprego (o notebook usa
um texto fixo de exemplo), o endpoint abaixo resume, em português, a
**variação de preço** de um produto monitorado — usando só os dados que a
coleta (Semana 07) já guardou (`coleta/banco.py::historico_do_produto`).

## Peças

| Peça | Onde | Papel |
|---|---|---|
| Ollama | processo local (`127.0.0.1:11434`) | roda o modelo (`qwen2.5:0.5b`) e gera o texto |
| Redis/Memurai | processo local (`127.0.0.1:6379`) | cache: evita gerar o mesmo resumo duas vezes |
| `api/resumo_precos.py` | código | monta o prompt, calcula a chave de cache, chama o Ollama, lê/grava no Redis |
| `api/main.py` | código | o endpoint HTTP, busca o histórico no banco e traduz os erros em status |

## Endpoint

`GET /produtos/{produto_id}/resumo-preco` → `{"resumo": str, "cache": bool}`

| Situação | Status |
|---|---|
| Produto não encontrado | 404 |
| URL do produto não aponta pra um id do Mercado Livre reconhecido | 404 |
| Ainda não há histórico de preço coletado pra esse produto | 404 |
| Ollama não respondeu (ou respondeu algo vazio) | 502 |
| Redis/Memurai não respondeu | 503 |

## Rodando com os serviços de verdade

```bash
# Ollama e Memurai já instalados e rodando (ver topo do histórico do projeto)
pip install -r requirements.txt
uvicorn api.main:app --reload
curl http://127.0.0.1:8000/produtos/1/resumo-preco
```

Variáveis de ambiente opcionais (padrões já cobrem uma instalação local
comum): `OLLAMA_URL` (padrão `http://127.0.0.1:11434`), `OLLAMA_MODELO`
(padrão `qwen2.5:0.5b`), `REDIS_HOST` (padrão `127.0.0.1`), `REDIS_PORT`
(padrão `6379`).

## Testes

```bash
pytest tests/api/test_resumo_precos.py -v
```

Nenhum teste chama Ollama/Redis de verdade — usam `fakeredis.FakeRedis()`
(biblioteca Python pura, sem servidor) e uma função fake no lugar da chamada
ao modelo, igual o padrão de `cliente_redis`/`chamar_modelo` injetáveis
descrito no topo de `resumo_precos.py`. Cobrem, entre outras coisas, os três
pontos que a entrega da trilha veterana pede:

- **"Primeiro pedido com cache falso e segundo com cache verdadeiro"** —
  `test_gerar_resumo_reaproveita_cache_na_segunda_vez` e
  `test_endpoint_devolve_resumo_quando_tudo_disponivel` (endpoint real,
  validado também manualmente contra Ollama/Memurai de verdade: primeira
  chamada `cache: false`, segunda `cache: true`).
- **"Expiração demonstrada e nova geração"** —
  `test_gerar_resumo_expira_e_gera_de_novo`: expira a chave no Redis fake
  (equivalente a esperar o TTL vencer) e confirma que o modelo é chamado de
  novo, com uma resposta nova (não uma resposta "false" vazia).
- **"Uma resposta gerada e sua avaliação de fidelidade"** — validado contra
  o Ollama de verdade: a primeira versão do prompt, com um histórico de só
  UM preço, fez o modelo inventar uma variação ("subiu 1%") que não existia
  pra calcular — infidelidade real, não hipotética. O prompt (`VERSAO_PROMPT
  "v1"` → `"v2"`) foi ajustado pra dizer explicitamente o que fazer com 1
  preço só (dizer o preço atual, sem inventar "subiu"/"caiu"), e com um
  histórico de 2+ preços o modelo voltou a citar os valores reais
  (ex.: "subiu de R$89,00 para R$99,00").

## Por que mudar o prompt precisa mudar a chave?

A chave de cache (`chave_resumo`) não é um hash só do texto do histórico —
é um hash do **pedido inteiro**: modelo, versão do prompt e as mensagens
completas que seriam enviadas (`chave_resumo` → `json.dumps({"modelo":
..., "versao_prompt": ..., "mensagens": ..., "geracao": ...})`).

Se a chave fosse só do texto do histórico, mudar o prompt (ex.: adicionar a
regra "com 1 preço só, não invente variação") faria o Redis devolver pro
usuário um resumo **gerado com o prompt antigo**, achando que é uma resposta
válida pro prompt novo — o cache ficaria "mentindo" sobre qual pergunta foi
respondida. Incluir o prompt (e o modelo, e a config de geração) na chave
garante que qualquer mudança no que é pedido ao modelo invalida
automaticamente as respostas antigas, em vez de depender de alguém lembrar
de limpar o cache manualmente.

## Adaptações em relação ao notebook

- **Sem autenticação, rate limit nem múltiplos servidores** — mesmos limites
  que o notebook já declara ("Limites" na célula de entrega); isso é uma
  prática de Smart Hub, não a versão de produção do Estom.
- **Sem teste de "entrada vazia" com status 422** — o notebook monta um
  endpoint que RECEBE um texto no corpo do pedido (a vaga), e por isso faz
  sentido perguntar "e se mandarem um corpo vazio?". O endpoint do Estom é
  um `GET` sem corpo: o texto a resumir nunca vem do cliente, vem do
  histórico que a coleta já salvou no banco — não existe "entrada vazia"
  nesse formato pra validar. O equivalente mais próximo que o Estom tem é o
  produto **sem histórico coletado ainda**, que também é um "não tenho o
  que te mostrar" — só que isso é informação ausente do lado do servidor
  (404), não um corpo de requisição inválido do lado do cliente (422); por
  isso os testes cobrem esse caso como 404
  (`test_endpoint_404_sem_historico_coletado`) em vez de forçar um 422 que
  não bate com o formato do endpoint.

# Pipeline de coleta de preços (Semana 07 — Coffee & Code)

Entregável da trilha de Data & Scraping do Coffee & Code (PUCPR), adaptado
pro nosso projeto: em vez de raspar HTML de um site de treino, consulta a
**API oficial do Mercado Livre** pra saber o preço e a disponibilidade dos
produtos monitorados, limpa os dados, grava num SQLite sem duplicar, inativa
o que sumiu do catálogo, registra cada execução e pode ser agendado.

A adaptação foi conversada com a organizadora do Coffee & Code: o que é
conferido é o checklist (boas maneiras na coleta, dados limpos, banco
idempotente, execução registrada, agendamento, testes), não a fonte exata
dos dados. Como a API devolve JSON em vez de HTML, não existe "robots.txt"
aqui — a cortesia equivalente é respeitar o token, o rate limit implícito da
API (um pequeno intervalo entre pedidos) e nunca usar mais de 20 ids por
chamada, que é o limite da própria API.

Além do robots.txt, outros dois itens do checklist foram pensados pra
scraping de HTML e mudam de forma numa API JSON — documentando aqui pra não
parecer que foram esquecidos:

- **"Paginação segue o link Próxima, com travas visitadas e MAX_PAGINAS"** —
  não existe link de página pra seguir aqui (a lista de produtos vem do
  nosso próprio `produtos_monitorados.txt`, não de navegar o site). O
  equivalente é consultar em lotes de até 20 ids por chamada
  (`TAMANHO_LOTE`), com um teto de lotes por execução (`MAX_LOTES`) fazendo
  o papel do `MAX_PAGINAS`. Não tem trava de "visitadas" nem checagem de
  ciclo porque, sendo uma lista finita e conhecida (não um link que a
  própria página devolve), não tem como entrar em ciclo.
- **"Falha temporária na página de detalhe não apaga a descrição já
  conhecida"** — o site de treino tinha uma página de lista e uma página de
  detalhe separadas; a API do Mercado Livre devolve tudo (título, preço,
  etc.) numa chamada só a `/items`, então não existe uma segunda etapa de
  "detalhe" que possa falhar separadamente. Esse item do checklist não tem
  equivalente direto no nosso pipeline.

## ⚠️ A API real do Mercado Livre está bloqueando essa consulta

Ao testar, a API devolveu, pra mais de um produto diferente:

```json
{"blocked_by":"PolicyAgent","code":"PA_UNAUTHORIZED_RESULT_FROM_POLICIES","message":"At least one policy returned UNAUTHORIZED.","status":403}
```

Isso aconteceu com produtos de vendedores diferentes, então não é um problema
de um produto específico nem do jeito que extraímos o ID. É uma política
interna do Mercado Livre bloqueando a leitura de anúncios de terceiros pela
API — achei vários relatos de outros desenvolvedores com o exato mesmo erro,
sem solução documentada oficialmente. Como eu não tenho produto cadastrado
na minha própria conta de vendedor, não deu pra confirmar se consultar os
PRÓPRIOS anúncios escapa dessa trava.

**Por isso a demonstração do checklist (e os testes automatizados) rodam
contra uma API simulada** (`coleta/api_simulada.py`), não a API real — ver
"Demonstração" abaixo. O cliente de verdade (`coleta/http_cliente.py`,
`coleta/auth.py`) está pronto e funcionando (autenticação, renovação de
token, retry) e aponta pra API real por padrão; só esbarra nessa política
externa ao tentar ler o preço de um anúncio.

## Antes de rodar: autenticação

Você já tem `ACCESS_TOKEN` e `REFRESH_TOKEN` no `.env` (do login OAuth que
você já fez). **Falta `CLIENT_ID` e `CLIENT_SECRET`** — são os dados da sua
aplicação em https://developers.mercadolivre.com.br, usados só pra renovar o
token sozinho quando ele vencer. Adicione as duas linhas no seu `.env` (veja
`.env.example`):

```
CLIENT_ID=o-id-da-sua-aplicacao
CLIENT_SECRET=o-segredo-da-sua-aplicacao
```

**Importante sobre o token do Mercado Livre:** o `access_token` dura poucas
horas, e o `refresh_token` só pode ser usado **uma vez** — a cada renovação,
o Mercado Livre devolve um `refresh_token` novo e invalida o antigo. Por
isso o pipeline não usa o `.env` como fonte de verdade depois da primeira
vez: ele mantém o token "vivo" em `dados/ml_tokens.json` (fora do Git) e
atualiza esse arquivo sozinho sempre que renova (ver `coleta/auth.py`).

## Instalar

```bash
pip install -r requirements.txt
```

Adiciona `requests`, `croniter` e `python-dotenv` ao que a API já usa.

## Escolher os produtos

Edite `coleta/produtos_monitorados.txt`: um link de produto do Mercado Livre
por linha (o mesmo link que você colaria no formulário de cadastro do
Estom). Linhas com `#` são ignoradas.

## Rodar a coleta

```bash
python -m coleta
```

Roda uma vez e termina. Código de saída: `0` sucesso, `1` parcial (algum
lote de produtos falhou ou veio quebrado), `2` falha (token sem credencial
pra renovar, ou nenhum produto configurado), `3` já existe uma execução em
andamento (trava em `dados/coleta.lock`).

## Conferir se rodou

- Log rotativo em `logs/coleta.log`.
- Tabela `execucoes` no banco (`dados/estom_coleta.db`): uma linha por
  execução, com status, contagem de novas/atualizadas/iguais/inativadas e
  um resumo em texto.
- Tabela `produtos_coletados`: o preço (em centavos), disponibilidade e
  status mais recentes de cada produto monitorado.

## Agendamento (Windows)

1. Confira a expressão antes de criar a tarefa:
   ```bash
   python agendamento/conferir_expressao.py "0 8 * * *"
   ```
2. No Agendador de Tarefas do Windows, crie uma tarefa diária chamando
   `powershell.exe -ExecutionPolicy Bypass -File "<caminho completo>\agendamento\preparar_ambiente.ps1"`.

## Demonstração (API simulada)

Como a API real está bloqueando a leitura (ver aviso no topo), a demonstração
do checklist — "rode duas vezes seguidas, depois mude algo e rode a terceira,
com as vagas novas e a inativada" — usa `coleta/api_simulada.py`, com 4
produtos fictícios (`MLB001` a `MLB004`), dos quais só 3 começam monitorados.

Precisa de duas janelas de terminal ABERTAS AO MESMO TEMPO (a API simulada
fica rodando numa, esperando pedido; os outros comandos rodam na outra) —
não dá pra rodar tudo numa janela só, uma coisa depois da outra.

Se você já fez a autorização OAuth de verdade em algum momento (o `.env` tem
`ACCESS_TOKEN`/`REFRESH_TOKEN` reais, ou já existe `dados/ml_tokens.json`),
apague o arquivo de token "vivo" antes de começar — senão o pipeline tenta
usar o token real contra a API simulada e falha com "Mercado Livre recusou a
renovação":

```powershell
Remove-Item dados\ml_tokens.json -ErrorAction SilentlyContinue
```

```powershell
# janela A: sobe a API simulada e deixa rodando
python coleta\api_simulada.py --porta 8188

# janela B: aponta o pipeline pra ela com um token de teste e roda
$env:ML_API_BASE = "http://127.0.0.1:8188"
$env:ACCESS_TOKEN = "tok-1"
$env:REFRESH_TOKEN = "ref-1"
python -m coleta      # 1ª vez: cria os 3 produtos monitorados
python -m coleta      # 2ª vez: "tudo igual"

# janela B: simula uma mudança de preço, uma remoção, E adiciona um produto novo
curl "http://127.0.0.1:8188/_dev/preco?id=MLB001&valor=239.90"
curl "http://127.0.0.1:8188/_dev/remover?id=MLB002"
Add-Content coleta\produtos_monitorados.txt "`nhttps://produto.mercadolivre.com.br/MLB-004-fone-bluetooth"

# janela B: 3ª execução — mostra a atualização, a inativação E a nova
python -m coleta
```

Validei esse roteiro de ponta a ponta: 1ª execução cria os 3 produtos, 2ª dá
"tudo igual", 3ª mostra 1 nova (MLB004) + 1 atualizada (preço) + 1 inativada
(removida) — é exatamente a demonstração "dia 1 / dia 2" que o checklist
pede, com as vagas novas e a inativada.

## Ligando com o front (api/coleta_integracao.py)

Pra mostrar que a coleta não é só um script isolado, os produtos 1 ("Monitor"),
2 ("Cadeira do escritório") e 5 ("Teclado mecânico") do front/`api/dados.py`
têm URL apontando pros ids MLB001/MLB002/MLB003 da API simulada (ver
`coleta/produtos_monitorados.txt`). Quando a coleta roda, `GET /produtos`
passa a devolver o preço e a data que a coleta salvou no banco, em vez do
dado de demonstração fixo — a sobreposição é feita em
`api/coleta_integracao.py` (função `aplicar_precos_coletados`), sem alterar
os dados de demonstração em memória nem o banco da coleta.

Os produtos 3 ("Apple AirPods 4") e 4 ("PlayStation 5 Slim") continuam puro
dado de demonstração — não têm URL reconhecida pela coleta, então nunca são
sobrescritos. E se o banco da coleta não existir ainda (nenhuma coleta
rodou), `GET /produtos` simplesmente devolve os dados de demonstração sem
erro.

Pra ver funcionando (repetindo o roteiro da seção anterior, mais a API):

```bash
# terminal 1: API simulada (como acima)
python coleta/api_simulada.py --porta 8188

# terminal 2: roda a coleta apontando pra ela
set ML_API_BASE=http://127.0.0.1:8188
python -m coleta

# terminal 3: sobe a API de verdade do projeto
uvicorn api.main:app --reload

# terminal 4 (ou o navegador): confere o preço coletado aparecendo
curl http://127.0.0.1:8000/produtos
```

Os nomes dos produtos no front ("Monitor", "Cadeira do escritório", "Teclado
mecânico") não precisam bater com os nomes dos produtos na API simulada
("Teclado mecânico", "Mouse sem fio", "Produto quebrado") — é só uma prova de
conceito de que o link funciona, não uma curadoria de catálogo.

## Testes

```bash
pytest tests/coleta tests/api -v
```

44 testes da coleta em si, rodando contra uma **API falsa local**
(`coleta/api_simulada.py`, a mesma usada na demonstração acima) que imita o
formato de `/items` e `/oauth/token` — não usam a internet nem o seu token
real. Mais 4 testes do link com o front (`tests/api/test_coleta_integracao.py`),
que populam um banco de coleta temporário e confirmam que `GET /produtos`
sobrepõe o preço certo, sem mexer no produto original nem sobrescrever
produto sem id reconhecido/inativo/sem coleta nenhuma ainda.

### O que foi testado

- Limpeza: preço em centavos (incluindo arredondamento de ponto flutuante),
  quantidade `0` tratada como valor real (não ausência), campo essencial
  ausente vira item inválido.
- Extração do ID do Mercado Livre a partir da URL do produto.
- Autenticação: token lido do arquivo de estado, renovação automática em
  cadeia (um refresh_token só funciona uma vez), falha clara sem
  `CLIENT_ID`/`CLIENT_SECRET`.
- Cliente HTTP: renovação automática num 401, retry com backoff em
  429/502/503/504, 404 não é repetido, timeout configurado.
- Coleta em lotes (máx. 20 ids por chamada), limite de lotes, produto que
  não existe mais (404) não derruba a coleta.
- Banco: unicidade, upsert, classificação nova/atualizada/igual, inativação
  e reativação.
- Pipeline completo: primeira execução, execução repetida ("tudo igual"),
  produto removido do catálogo (inativado sem apagar), preço mudando
  (classificado como atualizada), lista de produtos vazia (falha sem
  inativar nada por engano), trava contra execução concorrente.
- Link com o front: produto com id reconhecido tem o preço sobreposto (sem
  alterar o dict original), produto sem id reconhecido/inativo/sem nenhuma
  coleta ainda fica com o dado de demonstração.

### O que NÃO foi testado

- Checar se consultar os PRÓPRIOS anúncios (sendo vendedor cadastrado)
  escapa do bloqueio PA_UNAUTHORIZED_RESULT_FROM_POLICIES — não tenho
  produto na minha conta pra testar isso.
- Rodar de verdade no Agendador de Tarefas do Windows (só a expressão foi
  conferida com `croniter`).
- Produtos com preço em faixa, promoção ou variações (cor, tamanho) — a API
  de multiget devolve o preço "principal" do anúncio; variações ficariam
  pra uma etapa futura.
- Trilha veterano (assíncrono, JavaScript, medição de performance) — fora
  do escopo desta entrega.

## Estrutura

```text
coleta/
├── config.py                  # URL da API, caminhos, credenciais (lidas do .env)
├── auth.py                    # token: lê, renova e persiste em dados/ml_tokens.json
├── http_cliente.py            # injeta o token, timeout, retry/backoff, renova em 401
├── mapeamento.py               # extrai o ID da URL + organiza o JSON da API
├── limpeza.py                  # dados brutos -> dados limpos e tipados (preço em centavos etc.)
├── coletores.py                # consulta em lotes de até 20 ids, valida cada item
├── banco.py                    # esquema SQLite, upsert idempotente, inativação
├── executar.py                 # trava, log rotativo, pipeline, códigos de saída
├── __main__.py                 # python -m coleta
├── api_simulada.py              # API falsa p/ demonstração (usada nos testes e aqui)
└── produtos_monitorados.txt    # edite aqui os produtos que quer acompanhar

agendamento/
├── preparar_ambiente.ps1       # chamado pelo Agendador de Tarefas (caminhos absolutos)
└── conferir_expressao.py       # valida a expressão de agendamento com croniter

api/coleta_integracao.py        # liga o preço coletado aos produtos do front (ver acima)

tests/coleta/                   # pytest + API falsa local (ver seção Testes)
tests/api/                      # pytest do link com o front
dados/                          # banco SQLite, trava e token "vivo" (fora do Git)
logs/                           # log rotativo (fora do Git)
```

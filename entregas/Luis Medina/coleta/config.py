import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lê o .env na raiz do projeto (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)

RAIZ = Path(__file__).resolve().parent.parent

FONTE = "mercado-livre"

API_BASE = os.environ.get("ML_API_BASE", "https://api.mercadolibre.com")

PRODUTOS_MONITORADOS_CAMINHO = RAIZ / "coleta" / "produtos_monitorados.txt"

# Identificação honesta nas requisições (além do token, de bom tom dizer quem é).
USER_AGENT = (
    "EstomColetaBot/1.0 "
    "(+https://github.com/luissmedina-dev/price-watcher; contato via issues do repositório)"
)

TIMEOUT_SEGUNDOS = 10
ESPERA_ENTRE_PEDIDOS_SEGUNDOS = 0.3  # cortesia: não bater pedidos em cima uns dos outros

MAX_TENTATIVAS = 5
ESPERA_INICIAL_SEGUNDOS = 1.0
FATOR_BACKOFF = 2.0

TAMANHO_LOTE = 20     # a API aceita no máximo 20 ids por chamada de multiget
MAX_LOTES = 10        # trava de segurança (20 * 10 = 200 produtos no máximo por execução)

BANCO_CAMINHO = RAIZ / "dados" / "estom_coleta.db"
LOG_CAMINHO = RAIZ / "logs" / "coleta.log"
LOCK_CAMINHO = RAIZ / "dados" / "coleta.lock"
TOKENS_CAMINHO = RAIZ / "dados" / "ml_tokens.json"

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ACCESS_TOKEN_INICIAL = os.environ.get("ACCESS_TOKEN")
REFRESH_TOKEN_INICIAL = os.environ.get("REFRESH_TOKEN")

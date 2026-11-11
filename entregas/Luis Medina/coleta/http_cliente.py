from __future__ import annotations

import logging
import time

import requests

from coleta import auth, config

logger = logging.getLogger("coleta.http")

CODIGOS_REPETIVEIS = {429, 502, 503, 504}


class ClienteML:

    def __init__(self, url_base: str | None = None):
        self.url_base = (url_base if url_base is not None else config.API_BASE).rstrip("/")
        self.sessao = requests.Session()
        self.sessao.headers["User-Agent"] = config.USER_AGENT
        self._ultimo_pedido = 0.0

    def _esperar_intervalo(self) -> None:
        falta = config.ESPERA_ENTRE_PEDIDOS_SEGUNDOS - (time.monotonic() - self._ultimo_pedido)
        if falta > 0:
            time.sleep(falta)

    def get(self, caminho: str, **kwargs) -> requests.Response:
        
        url = f"{self.url_base}/{caminho.lstrip('/')}"
        espera = config.ESPERA_INICIAL_SEGUNDOS
        ultimo_erro: Exception | None = None
        ja_tentou_renovar = False

        for tentativa in range(1, config.MAX_TENTATIVAS + 1):
            self._esperar_intervalo()
            self._ultimo_pedido = time.monotonic()
            self.sessao.headers["Authorization"] = f"Bearer {auth.access_token_atual()}"

            try:
                resposta = self.sessao.get(url, timeout=config.TIMEOUT_SEGUNDOS, **kwargs)
            except requests.exceptions.RequestException as exc:
                ultimo_erro = exc
                logger.warning("erro de rede em %s (tentativa %d/%d): %s", caminho, tentativa, config.MAX_TENTATIVAS, exc)
            else:
                if resposta.status_code == 401 and not ja_tentou_renovar:
                    logger.info("token vencido, renovando")
                    ja_tentou_renovar = True
                    auth.renovar()
                    continue  # tenta de novo já com o token novo, sem gastar uma "tentativa" de retry

                if resposta.status_code not in CODIGOS_REPETIVEIS:
                    if resposta.status_code >= 400:
                        logger.warning(
                            "status %d em %s (sem repetir) — corpo: %s",
                            resposta.status_code, caminho, resposta.text[:300],
                        )
                    resposta.raise_for_status()
                    return resposta

                ultimo_erro = requests.exceptions.HTTPError(f"{resposta.status_code} em {caminho}", response=resposta)
                logger.warning("status %d em %s (tentativa %d/%d)", resposta.status_code, caminho, tentativa, config.MAX_TENTATIVAS)
                retry_after = resposta.headers.get("Retry-After")
                if retry_after:
                    try:
                        espera = max(espera, float(retry_after))
                    except ValueError:
                        pass

            if tentativa < config.MAX_TENTATIVAS:
                time.sleep(espera)
                espera *= config.FATOR_BACKOFF

        assert ultimo_erro is not None
        raise ultimo_erro

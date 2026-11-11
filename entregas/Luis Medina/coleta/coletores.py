from __future__ import annotations

import logging
from dataclasses import dataclass, field

from coleta import config, limpeza, mapeamento
from coleta.http_cliente import ClienteML

logger = logging.getLogger("coleta.coletores")

CAMPOS_ESSENCIAIS_PRODUTO = ["id_externo", "titulo"]


@dataclass
class ResultadoColeta:
    itens: list[dict] = field(default_factory=list)
    completa: bool = True
    motivo_incompleta: str | None = None
    itens_quebrados: int = 0

    def marcar_incompleta(self, motivo: str) -> None:
        self.completa = False
        self.motivo_incompleta = self.motivo_incompleta or motivo


def _lotes(sequencia: list, tamanho: int):
    for inicio in range(0, len(sequencia), tamanho):
        yield sequencia[inicio: inicio + tamanho]


def coletar_produtos(cliente: ClienteML, ids_externos: list[str]) -> ResultadoColeta:
    resultado = ResultadoColeta()

    todos_os_lotes = list(_lotes(ids_externos, config.TAMANHO_LOTE))
    if len(todos_os_lotes) > config.MAX_LOTES:
        logger.error("limite de %d lotes atingido (%d produtos monitorados)", config.MAX_LOTES, len(ids_externos))
        resultado.marcar_incompleta("limite_lotes")
        todos_os_lotes = todos_os_lotes[: config.MAX_LOTES]

    for lote in todos_os_lotes:
        try:
            resposta = cliente.get(f"/items?ids={','.join(lote)}")
        except Exception as exc:
            logger.error("falha ao buscar o lote %s: %s", lote, exc)
            resultado.marcar_incompleta("pagina_falhou")
            continue

        for id_pedido, entrada in zip(lote, resposta.json()):
            if entrada.get("code") == 404:
                logger.info("produto %s não existe mais na API (404)", id_pedido)
                continue  # some do catálogo: inativa naturalmente se a coleta terminar completa

            if entrada.get("code") != 200:
                logger.warning("item com código inesperado: %r", entrada)
                resultado.itens_quebrados += 1
                resultado.marcar_incompleta("item_quebrado")
                continue

            bruto = mapeamento.mapear_item(entrada["body"])
            if not limpeza.item_valido(bruto, CAMPOS_ESSENCIAIS_PRODUTO):
                logger.warning("produto quebrado (campo essencial ausente): %r", bruto)
                resultado.itens_quebrados += 1
                resultado.marcar_incompleta("item_quebrado")
                continue

            resultado.itens.append(limpeza.limpar_produto(bruto))

    return resultado

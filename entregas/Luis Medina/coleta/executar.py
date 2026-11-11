from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from coleta import banco, config, mapeamento
from coleta.coletores import coletar_produtos
from coleta.http_cliente import ClienteML

logger = logging.getLogger("coleta.executar")


class JaEmExecucao(Exception):
    pass


class _Trava:

    def __init__(self, caminho=None):
        self.caminho = caminho if caminho is not None else config.LOCK_CAMINHO

    def __enter__(self):
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        try:
            descritor = os.open(self.caminho, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except FileExistsError as exc:
            raise JaEmExecucao(f"já existe uma execução em andamento ({self.caminho})") from exc
        os.write(descritor, str(os.getpid()).encode())
        os.close(descritor)
        return self

    def __exit__(self, *_exc):
        self.caminho.unlink(missing_ok=True)


def configurar_log() -> None:
    config.LOG_CAMINHO.parent.mkdir(parents=True, exist_ok=True)
    manipulador = RotatingFileHandler(config.LOG_CAMINHO, maxBytes=500_000, backupCount=5, encoding="utf-8")
    manipulador.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.getLogger("coleta").setLevel(logging.INFO)
    logging.getLogger("coleta").addHandler(manipulador)


def executar() -> int:
    """Roda uma coleta completa. Devolve o código de saída (0/1/2)."""
    conexao = banco.conectar()
    execucao_id = banco.iniciar_execucao(conexao)
    logger.info("execução %d iniciada", execucao_id)

    ids = mapeamento.ler_produtos_monitorados(config.PRODUTOS_MONITORADOS_CAMINHO)
    if not ids:
        motivo = f"nenhum produto em {config.PRODUTOS_MONITORADOS_CAMINHO.name} (edite o arquivo e tente de novo)"
        logger.error(motivo)
        banco.finalizar_execucao(conexao, execucao_id, "falha", 0, 0, 0, 0, motivo)
        return 2

    try:
        cliente = ClienteML()
    except Exception:
        logger.exception("não foi possível iniciar o cliente da API")
        banco.finalizar_execucao(conexao, execucao_id, "falha", 0, 0, 0, 0, "cliente da API não iniciou")
        return 2

    resultado = coletar_produtos(cliente, ids)
    contagem = banco.salvar_produtos(conexao, config.FONTE, resultado.itens)
    # Loga esta coleta no histórico mesmo em execução parcial: os itens que
    # vieram são válidos, só a coleta como um todo que ficou incompleta.
    banco.registrar_historico(conexao, config.FONTE, resultado.itens)

    inativadas = 0
    if resultado.completa:
        ids_vistos = {item["id_externo"] for item in resultado.itens}
        inativadas = banco.inativar_sumidos(conexao, config.FONTE, ids_vistos)

    novas, atualizadas, iguais = contagem["nova"], contagem["atualizada"], contagem["igual"]

    if not resultado.itens and not resultado.completa:
        status, codigo = "falha", 2
    elif not resultado.completa:
        status, codigo = "parcial", 1
    else:
        status, codigo = "sucesso", 0

    resumo = (
        f"{len(ids)} produtos monitorados, {len(resultado.itens)} coletados "
        f"(completa={resultado.completa}, motivo={resultado.motivo_incompleta}); "
        f"novas={novas} atualizadas={atualizadas} iguais={iguais} inativadas={inativadas}"
    )
    logger.info("execução %d finalizada: status=%s | %s", execucao_id, status, resumo)
    banco.finalizar_execucao(conexao, execucao_id, status, novas, atualizadas, iguais, inativadas, resumo)
    conexao.close()
    return codigo


def main() -> int:
    configurar_log()
    try:
        with _Trava():
            return executar()
    except JaEmExecucao as exc:
        logger.warning(str(exc))
        return 3


if __name__ == "__main__":
    sys.exit(main())

"""Confere a expressão de agendamento com croniter antes de criar a tarefa.

O Agendador de Tarefas do Windows não usa a sintaxe de cron, mas o croniter
serve pra confirmar que a ideia do agendamento (uma vez por dia) está
correta antes de configurar a tarefa na mão — e documenta, em um único
lugar, com que frequência a coleta deveria rodar.

Uso: python agendamento/conferir_expressao.py "0 8 * * *"
"""
import sys
from datetime import datetime, timedelta

from croniter import croniter

PADRAO = "0 8 * * *"  # todo dia às 8h


def conferir(expressao: str, quantos: int = 5) -> list[datetime]:
    if not croniter.is_valid(expressao):
        raise ValueError(f"expressão inválida: {expressao!r}")

    base = datetime.now()
    it = croniter(expressao, base)
    proximos = [it.get_next(datetime) for _ in range(quantos)]

    intervalos = {(b - a) for a, b in zip(proximos, proximos[1:])}
    if intervalos != {timedelta(days=1)}:
        raise ValueError(
            f"a expressão {expressao!r} não roda exatamente uma vez por dia "
            f"(intervalos encontrados: {intervalos})"
        )
    return proximos


if __name__ == "__main__":
    expressao = sys.argv[1] if len(sys.argv) > 1 else PADRAO
    proximos = conferir(expressao)
    print(f"expressão {expressao!r} confere: roda 1x por dia. Próximas execuções:")
    for quando in proximos:
        print(" -", quando.strftime("%Y-%m-%d %H:%M"))

import pytest

from agendamento.conferir_expressao import conferir


def test_expressao_diaria_confere():
    proximos = conferir("0 8 * * *", quantos=3)
    assert len(proximos) == 3


def test_expressao_que_nao_e_diaria_falha():
    with pytest.raises(ValueError):
        conferir("0 */4 * * *")


def test_expressao_invalida_falha():
    with pytest.raises(ValueError):
        conferir("isso não é um cron")

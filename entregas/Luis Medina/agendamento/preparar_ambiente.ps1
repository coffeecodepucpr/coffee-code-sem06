# Prepara o ambiente e chama o pipeline de coleta com caminhos absolutos.
# Pensado pro Agendador de Tarefas do Windows: aponte uma tarefa para
# "powershell.exe -ExecutionPolicy Bypass -File <caminho completo deste arquivo>".
#
# $PSScriptRoot já é um caminho absoluto (a pasta onde este script está),
# então o resto dos caminhos (venv, pacote coleta) vira absoluto também,
# não importa de onde o Agendador disparar o processo.

$ErrorActionPreference = "Stop"

$RaizDoRepo = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RaizDoRepo ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Não achei o Python do venv em $Python. Rode 'python -m venv .venv' e instale requirements.txt primeiro."
    exit 2
}

Set-Location $RaizDoRepo
& $Python -m coleta
exit $LASTEXITCODE

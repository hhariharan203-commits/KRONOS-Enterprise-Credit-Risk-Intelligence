param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VirtualEnvironment = Join-Path $Root ".venv"
$VirtualPython = Join-Path $VirtualEnvironment "Scripts\python.exe"

& $Python -m venv $VirtualEnvironment
& $VirtualPython -m pip install --upgrade pip
& $VirtualPython -m pip install -r (Join-Path $Root "requirements.txt") -r (Join-Path $Root "requirements-dev.txt")

Push-Location $Root
try {
    & $VirtualPython -m src.enterprise_data.pipeline
    & $VirtualPython -m src.enterprise_data.etl.scheduler
    & $VirtualPython -m src.enterprise_data.risk_marts.runner
    & $VirtualPython scripts\verify_repository.py
}
finally {
    Pop-Location
}

Write-Host "KRONOS setup complete. Run .\.venv\Scripts\streamlit.exe run app\main.py"

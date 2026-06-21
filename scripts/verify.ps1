$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VirtualPython = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $VirtualPython)) {
    throw "Missing .venv. Run .\scripts\setup.ps1 first."
}

Push-Location $Root
try {
    $env:PYTHONDONTWRITEBYTECODE = "1"
    & $VirtualPython scripts\verify_repository.py
    & $VirtualPython -m pytest -q -p no:cacheprovider
}
finally {
    Pop-Location
}

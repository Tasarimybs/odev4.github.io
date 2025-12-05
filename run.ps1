<#
Run this script in PowerShell to create a virtual environment, install dependencies and start the app.
Usage: Open PowerShell in the repo folder and run:
  .\run.ps1

If your execution policy prevents running scripts, run as admin:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

$venv = Join-Path $PSScriptRoot '.venv'
if (-not (Test-Path $venv)) {
    python -m venv $venv
}

& "$venv\Scripts\Activate.ps1"

pip install -r "$PSScriptRoot\requirements.txt"

python "$PSScriptRoot\elektro.py"

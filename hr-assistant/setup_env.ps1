# Sets up a Python virtual environment in this directory and installs requirements.txt into it.
# Run from anywhere: powershell -File setup_env.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir "venv"
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"

if (-not (Test-Path $RequirementsFile)) {
    throw "requirements.txt not found at $RequirementsFile"
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at $VenvDir"
    python -m venv $VenvDir
} else {
    Write-Host "Virtual environment already exists at $VenvDir"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "Upgrading pip"
& $VenvPython -m pip install --upgrade pip

Write-Host "Installing packages from requirements.txt"
& $VenvPython -m pip install -r $RequirementsFile

Write-Host "Done. Activate with: $VenvDir\Scripts\Activate.ps1"

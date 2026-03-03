Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
# Avoid terminating on native stderr noise; rely on exit codes instead.
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv..."
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = (Get-Command python).Source
        if ($pythonCmd -like "*\WindowsApps\python.exe") {
            throw "Only Windows Store python alias detected. Install Python 3 from python.org and disable App Execution Alias for python.exe."
        }
        python -m venv .venv
    } else {
        throw "Python launcher not found. Install Python 3 and ensure 'py' or 'python' is on PATH."
    }
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python not found at $venvPython"
}

Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

Write-Host "Installing dependencies..."
& $venvPython -m pip install -r requirements.txt

Write-Host "Running local test..."
$testCmd = "`"$venvPython`" test_local.py 2>&1"
$testOutput = & cmd /d /c $testCmd
$exitCode = $LASTEXITCODE
$testOutput | ForEach-Object { $_ }
$testOutputText = ($testOutput | Out-String)
if ($exitCode -ne 0) {
    throw "test_local.py failed with exit code $exitCode"
}

$outPath = Join-Path $root "out.png"
if (-not (Test-Path $outPath)) {
    throw "out.png was not created"
}

$outInfo = Get-Item $outPath
if ($outInfo.Length -le 0) {
    throw "out.png is empty"
}

if ($testOutputText -notmatch "(?m)^PNG_SIGNATURE_OK=True\s*$") {
    throw "PNG signature check did not pass according to test_local.py output"
}

$sigHex = (& $venvPython -c "from pathlib import Path; print(Path('out.png').read_bytes()[:8].hex().upper())").Trim()
if ($sigHex -ne "89504E470D0A1A0A") {
    throw "Unexpected out.png signature: $sigHex"
}

Write-Host "Local test passed. out.png size=$($outInfo.Length) bytes signature=$sigHex"

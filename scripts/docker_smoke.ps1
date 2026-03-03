Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found on PATH. Install Docker Desktop and retry."
}

docker build -t snapcontact-bg-serverless:local .
if ($LASTEXITCODE -ne 0) {
    throw "docker build failed"
}

docker run --rm snapcontact-bg-serverless:local python3 -c "import handler; print('handler import OK')"
if ($LASTEXITCODE -ne 0) {
    throw "docker import smoke test failed"
}

Write-Host "Docker smoke test passed."

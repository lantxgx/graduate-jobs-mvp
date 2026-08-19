$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeDir = "C:\Users\lantx\AppData\Local\Temp\jobs_server_pkgs_20260808"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$pythonExe = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "C:\Users\lantx\AppData\Local\Programs\Python\Python310\python.exe" }

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Python was not found: $pythonExe"
}

if ($pythonExe -eq $venvPython) {
    $env:PYTHONPATH = $root
} elseif (-not (Test-Path -LiteralPath (Join-Path $runtimeDir "fastapi"))) {
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    & $pythonExe -m pip install --disable-pip-version-check --target $runtimeDir `
        fastapi==0.116.1 uvicorn==0.35.0 playwright==1.54.0 `
        beautifulsoup4==4.13.4 httpx==0.28.1 python-dateutil==2.9.0.post0
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install local server dependencies."
    }
    $env:PYTHONPATH = $runtimeDir
}

# Invoke the runner directly so this works with both the project venv and the
# fallback runtime used by older installations.
& $pythonExe -c "import uvicorn; uvicorn.run('app.main:app', host='127.0.0.1', port=8000, ws='none')"

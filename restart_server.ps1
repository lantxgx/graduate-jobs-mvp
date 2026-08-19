$ErrorActionPreference = "Stop"

# Restart only the verified local listener owned by this MVP on 127.0.0.1:8000.
# This script never targets a broad process name or a remote service.
$listener = Get-NetTCPConnection -LocalAddress "127.0.0.1" -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1

if ($listener -and $listener.OwningProcess -gt 0) {
    Stop-Process -Id $listener.OwningProcess -Force
    Start-Sleep -Milliseconds 800
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stdout = Join-Path $root "server.stdout.log"
$stderr = Join-Path $root "server.stderr.log"
Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $root "start_server.ps1") `
    -WorkingDirectory $root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($health.StatusCode -eq 200) {
            Write-Output "牛投马面服务已启动：http://127.0.0.1:8000/"
            exit 0
        }
    } catch {
        # Keep polling until the bounded startup window expires.
    }
}

throw "服务未能在 15 秒内通过 /health"

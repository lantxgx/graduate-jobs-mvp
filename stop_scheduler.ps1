$ErrorActionPreference = "Stop"

# Stop only the PID recorded by start_scheduler.ps1 after verifying that the
# target is still this project's scheduler process.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $root "scheduler.pid"
if (-not (Test-Path -LiteralPath $pidFile)) {
    Write-Output "Scheduler is not running (no PID file)."
    exit 0
}

foreach ($schedulerPid in @(Get-Content -LiteralPath $pidFile | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ })) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$schedulerPid" -ErrorAction SilentlyContinue
    if ($process -and $process.CommandLine -like "*crawler.scheduler*--loop*") {
        Stop-Process -Id $schedulerPid -Force
        Write-Output "Scheduler stopped: PID $schedulerPid"
    } elseif ($process) {
        throw "PID file does not identify the project scheduler; refusing to stop PID $schedulerPid"
    } else {
        Write-Output "Scheduler process already exited: PID $schedulerPid"
    }
}

Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue

$ErrorActionPreference = "Stop"

# Start only this project's low-frequency scheduler.  The scheduler itself
# selects one due, integrated source at a time and applies source locks/cooldowns.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $root ".venv\Scripts\python.exe"
$pidFile = Join-Path $root "scheduler.pid"
$stdout = Join-Path $root "scheduler.stdout.log"
$stderr = Join-Path $root "scheduler.stderr.log"

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Project Python was not found: $pythonExe"
}

if (Test-Path -LiteralPath $pidFile) {
    $existingPid = [int]((Get-Content -LiteralPath $pidFile | Select-Object -First 1).Trim())
    $existing = Get-CimInstance Win32_Process -Filter "ProcessId=$existingPid" -ErrorAction SilentlyContinue
    if ($existing -and $existing.CommandLine -like "*crawler.scheduler*--loop*") {
        Write-Output "Scheduler already running: PID $existingPid"
        exit 0
    }
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
}

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList "-m", "crawler.scheduler", "--loop" `
    -WorkingDirectory $root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru

Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ascii
Start-Sleep -Milliseconds 500
$check = Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id)" -ErrorAction SilentlyContinue
if (-not $check -or $check.CommandLine -notlike "*crawler.scheduler*--loop*") {
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    throw "Scheduler did not remain running. Check $stderr"
}

$child = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($process.Id)" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*crawler.scheduler*--loop*" } |
    Select-Object -First 1
if ($child) {
    # The Windows venv launcher can remain as a parent while the actual
    # Python process owns the scheduler loop. Record both for safe shutdown.
    Set-Content -LiteralPath $pidFile -Value "$($child.ProcessId)`n$($process.Id)" -Encoding ascii
    Write-Output "Scheduler started: PID $($child.ProcessId) (launcher $($process.Id))"
} else {
    Write-Output "Scheduler started: PID $($process.Id)"
}

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython = 'C:\Users\19139\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { $taskPython = (Get-Command python -ErrorAction Stop).Source }
Write-Host 'ViralLoop: http://127.0.0.1:8877'
Write-Host 'Human blind review: http://127.0.0.1:8877/blind'
& $taskPython 'src/server.py'

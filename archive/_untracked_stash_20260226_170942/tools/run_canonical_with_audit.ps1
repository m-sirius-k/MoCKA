Param()

$ErrorActionPreference = "Stop"

$root = "C:\Users\sirok\MoCKA"
$py = Join-Path $root ".venv\Scripts\python.exe"

Set-Location $root

& $py (Join-Path $root "tools\assert_canonical_root.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $py (Join-Path $root "run_with_audit.py")
exit $LASTEXITCODE
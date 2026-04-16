Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[OK] canonical cwd"
Write-Host ("cwd: " + (Get-Location).Path)

$root = (Get-Location).Path

$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
  $py = $venvPy
} else {
  $py = "python"
}

$script = Join-Path $root "audit\ed25519\verify_pack\verify_full_chain_and_signature.py"
if (!(Test-Path $script)) {
  throw ("missing canonical verify script: " + $script)
}

& $py $script
exit $LASTEXITCODE
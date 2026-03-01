Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Run-Step([string]$name, [scriptblock]$fn) {
  Write-Host ""
  Write-Host ("== " + $name)
  & $fn
  Write-Host ("OK: " + $name)
}

cd "C:\Users\sirok\MoCKA"

Run-Step "Sample05 RFC3161 verify" {
  powershell -ExecutionPolicy Bypass -File ".\transparency\sample05\verify_sample05.ps1"
}

Run-Step "Sample01 verify (TODO)" {
  Write-Host "TODO: wire Sample01 verifier command here"
}

Run-Step "Sample02 verify (TODO)" {
  Write-Host "TODO: wire Sample02 verifier command here"
}

Run-Step "Sample03 verify (TODO)" {
  Write-Host "TODO: wire Sample03 verifier command here"
}

Run-Step "Sample04 verify (TODO)" {
  Write-Host "TODO: wire Sample04 verifier command here"
}

Write-Host ""
Write-Host "ALL DONE (Sample05 enforced; Sample01-04 TODO slots)"

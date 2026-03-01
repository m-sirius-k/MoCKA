Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Run-Step([string]$name, [scriptblock]$fn) {
  Write-Host ""
  Write-Host ("== " + $name)
  & $fn
  if($LASTEXITCODE -ne 0) { throw ("Non-zero exit code: " + $LASTEXITCODE) }
  Write-Host ("OK: " + $name)
}

function Require-File([string]$path) {
  if(-not (Test-Path $path)) { throw ("Missing required file: " + $path) }
}

cd "C:\Users\sirok\MoCKA"

$py = "python"

Require-File ".\transparency\sample05\verify_sample05.ps1"
Require-File ".\audit\ed25519\verify_full_chain_and_signature.py"

Run-Step "Sample05 RFC3161 verify" {
  powershell -ExecutionPolicy Bypass -File ".\transparency\sample05\verify_sample05.ps1"
}

Run-Step "Sample01 Tamper-Proof Decision Log verify (chain+sig baseline)" {
  & $py ".\audit\ed25519\verify_full_chain_and_signature.py"
}

Run-Step "Sample02 Chain Integrity verify (chain+sig baseline)" {
  & $py ".\audit\ed25519\verify_full_chain_and_signature.py"
}

Run-Step "Sample03 Key Rotation verify (chain+sig baseline)" {
  & $py ".\audit\ed25519\verify_full_chain_and_signature.py"
}

Run-Step "Sample04 Observer Recovery Pack export" {
  if(Test-Path ".\audit\ed25519\export_verify_pack.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\audit\ed25519\export_verify_pack.ps1"
  } elseif(Test-Path ".\export_verify_pack.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\export_verify_pack.ps1"
  } else {
    throw "Missing export_verify_pack.ps1 (audit/ed25519 or repo root)"
  }
}

Run-Step "Sample04 Observer Recovery Pack verify_pack" {
  Require-File ".\audit\ed25519\verify_pack\verify_full_chain_and_signature.py"
  & $py ".\audit\ed25519\verify_pack\verify_full_chain_and_signature.py"
}

Write-Host ""
Write-Host "ALL DONE (Sample01-05 wired; Sample04 includes pack verify)"

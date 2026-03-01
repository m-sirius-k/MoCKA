Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

cd "C:\Users\sirok\MoCKA"

if(Test-Path ".\audit\ed25519\export_verify_pack.ps1") {
  powershell -ExecutionPolicy Bypass -File ".\audit\ed25519\export_verify_pack.ps1"
} elseif(Test-Path ".\export_verify_pack.ps1") {
  powershell -ExecutionPolicy Bypass -File ".\export_verify_pack.ps1"
} else {
  throw "Missing export_verify_pack.ps1"
}

python ".\audit\ed25519\verify_pack\verify_full_chain_and_signature.py"

cd C:\Users\sirok\MoCKA

$target = "C:\Users\sirok\MoCKA\infield\ai_save\runtime\accept_ledger.active.csv"

if (!(Test-Path $target)) {
    Write-Host "Sample02 FAIL: target not found"
    exit 1
}

Write-Host "Sample02 target:" $target

$hash = Get-FileHash $target -Algorithm SHA256
Write-Host "SHA256:" $hash.Hash

python .\audit\ed25519\verify_full_chain_and_signature.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Sample02 FAIL: signature/chain verification failed"
    exit 1
}

Write-Host "Sample02 PASS"
exit 0

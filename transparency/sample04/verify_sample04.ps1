Write-Host "== Sample04 verify =="

python ./audit/ed25519/verify_full_chain_and_signature.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Sample04 FAIL"
    exit 1
}

Write-Host "Sample04 PASS"
exit 0

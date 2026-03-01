Write-Host "== Sample04 verify =="

# build verify pack
python ./verify/runtime_ledgers_verify.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Sample04 FAIL: build step failed"
    exit 1
}

# run chain verification
python ./audit/ed25519/verify_full_chain_and_signature.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Sample04 FAIL"
    exit 1
}

Write-Host "Sample04 PASS"
exit 0

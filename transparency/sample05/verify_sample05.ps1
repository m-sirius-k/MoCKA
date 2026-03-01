Write-Host "== Sample05 verify =="

openssl ts -verify `
  -data ./transparency/transparency_v2_manifest.json `
  -in ./transparency/sample05/manifest_v2.tsr `
  -CAfile ./transparency/sample05/tsa_cert.pem `
  -untrusted ./transparency/sample05/tsa_cert.pem

if ($LASTEXITCODE -ne 0) {
    Write-Host "Sample05 FAIL"
    exit 1
}

Write-Host "Sample05 PASS"
exit 0

Write-Host "== Sample05 verify =="

$ci = $env:CI

if ($ci -eq "true") {

    if (!(Test-Path "./transparency/transparency_v2_manifest.json")) {
        Write-Host "Sample05 FAIL: manifest missing"
        exit 1
    }

    if (!(Test-Path "./transparency/sample05/manifest_v2.tsr")) {
        Write-Host "Sample05 FAIL: timestamp response missing"
        exit 1
    }

    $size = (Get-Item "./transparency/sample05/manifest_v2.tsr").Length
    if ($size -le 0) {
        Write-Host "Sample05 FAIL: timestamp file empty"
        exit 1
    }

    Write-Host "Sample05 CI PASS (structure verified)"
    exit 0
}

# Local full verification
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

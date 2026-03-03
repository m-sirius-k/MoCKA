Write-Host "=== Transparency v2 Full Verification Start ==="

$ci = $env:CI

if ($ci -ne "true") {

    Write-Host ""
    Write-Host "== Sample01 verify =="
    powershell ./transparency/sample01/verify_sample01.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }

    Write-Host ""
    Write-Host "== Sample02 verify =="
    powershell ./transparency/sample02/verify_sample02.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }

    Write-Host ""
    Write-Host "== Sample03 verify =="
    powershell ./transparency/sample03/verify_sample03.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }

    Write-Host ""
    Write-Host "== Sample04 verify =="
    powershell ./transparency/sample04/verify_sample04.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }

} else {
    Write-Host "CI mode: runtime samples skipped (Sample01-04)"
}

Write-Host ""
Write-Host "== Sample05 verify =="
powershell ./transparency/sample05/verify_sample05.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "=== Transparency v2 PASS ==="
exit 0

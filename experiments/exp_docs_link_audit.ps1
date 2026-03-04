Write-Host "RUN_EXPERIMENT: docs_link_audit"

python .\MoCKA\tools\link_audit.py
if($LASTEXITCODE -ne 0){
  Write-Host "FAIL: docs_link_audit"
  exit 1
}

Write-Host "OK_EXPERIMENT: docs_link_audit"
exit 0

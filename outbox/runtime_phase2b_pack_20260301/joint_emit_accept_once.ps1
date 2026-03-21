param(
  [string]$RuntimeDir = "infield/ai_save/runtime"
)

$ErrorActionPreference = "Stop"

$emitPath   = Join-Path $RuntimeDir "emit_ledger.csv"
$acceptPath = Join-Path $RuntimeDir "accept_ledger.csv"

if(-not (Test-Path $emitPath)){
  "ts,emit_id,payload_sha256,prev_chain_hash,chain_hash,sender_fpr,sender_sig" | Set-Content -Path $emitPath -Encoding ASCII
}
if(-not (Test-Path $acceptPath)){
  "ts,emit_id,received_sha256,match_flag,receiver_fpr,receiver_sig" | Set-Content -Path $acceptPath -Encoding ASCII
}

$ts = Get-Date
$emitId = ("emit_" + $ts.ToUniversalTime().ToString("yyyyMMdd_HHmmss_fff"))

# payload is always per-emit
$payloadPath = Join-Path $RuntimeDir ($emitId + ".payload.json")
@"
{"emit_id":"$emitId","intent":"joint test","body":"runtime payload"}
"@ | Set-Content -Path $payloadPath -Encoding UTF8

$payloadSha = (Get-FileHash -Algorithm SHA256 -Path $payloadPath).Hash.ToLower()

# prev_chain_hash from last row
$prev = "GENESIS"
$lastLine = Get-Content $emitPath -Tail 1
if($lastLine -and ($lastLine -notmatch '^ts,')){
  $cols = $lastLine.Split(',')
  if($cols.Count -ge 5 -and $cols[4]){ $prev = $cols[4] }
}

$chainInput = ($prev + ":" + $payloadSha)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($chainInput)
$chainHash = ([System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join ""

# fingerprint
$fprLine = (gpg --list-secret-keys --with-colons 2>$null | Select-String "^fpr:" | Select-Object -First 1).Line
if(-not $fprLine){ throw "NO_GPG_FPR" }
$fpr = ($fprLine.Split(':')[9]).ToUpper()

# sign emit record
$emitRecordCore = "$($ts.ToString("s")),$emitId,$payloadSha,$prev,$chainHash,$fpr,"
$emitTxt = Join-Path $RuntimeDir ($emitId + ".emit.txt")
$emitAsc = $emitTxt + ".asc"
$emitRecordCore | Set-Content -Path $emitTxt -Encoding ASCII
gpg --armor --detach-sign --output $emitAsc $emitTxt
($emitRecordCore + (Split-Path $emitAsc -Leaf)) | Add-Content -Path $emitPath -Encoding ASCII

# accept uses actual payload file sha
$recvSha = (Get-FileHash -Algorithm SHA256 -Path $payloadPath).Hash.ToLower()
$match = "false"
if($recvSha -eq $payloadSha){ $match = "true" }

$ts2 = Get-Date
$acceptCore = "$($ts2.ToString("s")),$emitId,$recvSha,$match,$fpr,"
$accTxt = Join-Path $RuntimeDir ($emitId + ".accept.txt")
$accAsc = $accTxt + ".asc"
$acceptCore | Set-Content -Path $accTxt -Encoding ASCII
gpg --armor --detach-sign --output $accAsc $accTxt
($acceptCore + (Split-Path $accAsc -Leaf)) | Add-Content -Path $acceptPath -Encoding ASCII

# verify
powershell -ExecutionPolicy Bypass -File infield/ai_save/phase2/verify_joint_integrity.ps1 -EmitPath $emitPath -AcceptPath $acceptPath

Write-Host "JOINT_ONCE_OK"
Write-Host ("EMIT_ID=" + $emitId)
Write-Host ("PAYLOAD=" + $payloadPath)
Write-Host ("PAYLOAD_SHA256=" + $payloadSha)
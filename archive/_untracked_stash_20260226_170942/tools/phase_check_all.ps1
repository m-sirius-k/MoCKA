Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$msg) {
  Write-Host ""
  Write-Host "FAIL: $msg"
  exit 1
}

function Ok([string]$msg) {
  Write-Host "OK: $msg"
}

function Run([string]$label, [scriptblock]$cmd) {
  Write-Host ""
  Write-Host "RUN: $label"
  $out = (& $cmd 2>&1 | Out-String)
  $code = $LASTEXITCODE
  $out = $out.Trim()
  if ($out.Length -gt 0) { Write-Host $out }
  if ($code -ne 0) {
    Fail("$label (exit=$code)")
  }
  return $out
}

$root = (Get-Location).Path
$auditDir = Join-Path $root "audit"

Write-Host ""
Write-Host "=== MoCKA Phase Cross Check Start ==="

# 1) Policy existence
$policyPath = Join-Path $root "docs\PHASE9C_PARTIAL_CHAIN_POLICY.md"
if (!(Test-Path $policyPath)) { Fail("missing policy: $policyPath") }
Ok("policy exists")

# 2) audit directory existence
if (!(Test-Path $auditDir)) { Fail("missing audit dir: $auditDir") }
Ok("audit dir exists")

# 3) last_event_id.txt check
$lastEventPath = Join-Path $auditDir "last_event_id.txt"
if (!(Test-Path $lastEventPath)) { Fail("missing last_event_id.txt: $lastEventPath") }

$bytes = [System.IO.File]::ReadAllBytes($lastEventPath)
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
  Fail("last_event_id.txt has UTF-8 BOM")
}
Ok("last_event_id.txt has no BOM")

$tipFromLast = (Get-Content $lastEventPath -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($tipFromLast)) { Fail("last_event_id.txt empty") }
Ok("tip read from last_event_id.txt")

# 4) regenesis.json check
$regenesisPath = Join-Path $auditDir "recovery\regenesis.json"
if (!(Test-Path $regenesisPath)) { Fail("missing regenesis.json: $regenesisPath") }

try {
  $regenesis = Get-Content $regenesisPath -Raw | ConvertFrom-Json
} catch {
  Fail("regenesis.json is not valid JSON")
}

$tipFromRegenesis = [string]$regenesis.regensis_event_id
if ([string]::IsNullOrWhiteSpace($tipFromRegenesis)) {
  Fail("regenesis.json missing regensis_event_id")
}

if ($tipFromRegenesis -ne $tipFromLast) {
  Fail("tip mismatch: last_event_id.txt=$tipFromLast regenesis.json=$tipFromRegenesis")
}
Ok("regenesis tip matches last_event_id.txt")

# 5) Schema migrate check (non-fatal)
Write-Host ""
Write-Host "RUN: schema migrate check (non-fatal)"

$schemaLog = Join-Path $auditDir "phase_check_migrate_schema.log"

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
  $schemaOut = (& python -m src.mocka_audit.migrate_schema 2>&1 | Out-String).Trim()
  $schemaCode = $LASTEXITCODE
} finally {
  $ErrorActionPreference = $oldEAP
}

if ($schemaOut.Length -gt 0) { Write-Host $schemaOut }
$schemaOut | Out-File -Encoding utf8 $schemaLog

if ($schemaCode -ne 0) {
  Write-Host "WARN: schema migrate check failed (non-fatal)"
  Write-Host "      see $schemaLog"
} else {
  Ok("schema check passed")
}

# 6) verify_chain (file)
$out1 = Run "verify_chain (file)" { python -m src.mocka_audit.verify_chain }

if ($out1 -notmatch "OK:\s*partial allowed") {
  Fail("verify_chain did not report partial allowed")
}
if ($out1 -notmatch [Regex]::Escape($tipFromLast)) {
  Fail("verify_chain output missing canonical tip")
}
Ok("verify_chain passed")

# 7) verify_chain_v2 (reachable)
$out2 = Run "verify_chain_v2 (reachable)" { python -m src.mocka_audit.verify_chain_v2 }

if ($out2 -notmatch "OK:\s*reachable chain verified from TIP=") {
  Fail("verify_chain_v2 missing OK header")
}
if ($out2 -notmatch [Regex]::Escape($tipFromLast)) {
  Fail("verify_chain_v2 output missing canonical tip")
}
if ($out2 -notmatch "reachable length=14") {
  Fail("verify_chain_v2 reachable length is not 14")
}
if ($out2 -notmatch "missing prev=GENESIS") {
  Fail("verify_chain_v2 did not stop at missing prev=GENESIS")
}
Ok("verify_chain_v2 passed")

# 8) DB dump check
$out3 = Run "db_ledger_dump" { python tools\db_ledger_dump.py }

$tsvPath = Join-Path $auditDir "db_ledger_dump.tsv"
if (!(Test-Path $tsvPath)) { Fail("missing db_ledger_dump.tsv: $tsvPath") }

$lines = Get-Content $tsvPath
if ($lines.Count -lt 2) { Fail("db_ledger_dump.tsv has no rows") }

$rowCount = $lines.Count - 1
if ($rowCount -ne 14) {
  Fail("db_ledger_dump.tsv rowCount expected 14 but got $rowCount")
}

$hasTip = $false
for ($i = 1; $i -lt $lines.Count; $i++) {
  $cols = $lines[$i].Split("`t")
  if ($cols.Count -ge 1 -and $cols[0] -eq $tipFromLast) { $hasTip = $true }
}
if (-not $hasTip) { Fail("db_ledger_dump.tsv does not contain canonical tip") }
Ok("db ledger dump matches canonical chain")

# 9) DB file existence
$dbPath = Join-Path $auditDir "ed25519\audit.db"
if (!(Test-Path $dbPath)) { Fail("missing audit db: $dbPath") }
Ok("audit db exists")

Write-Host ""
Write-Host "ALL PASS: Phase cross-check completed"
exit 0
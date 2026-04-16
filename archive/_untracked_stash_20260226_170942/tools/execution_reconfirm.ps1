$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$utc = (Get-Date).ToUniversalTime().ToString("o")
$utcTag = $utc.Replace(":","").Replace("-","").Replace(".","").Replace("Z","+0000")

$sotTxt   = Join-Path $root "src\source_of_truth.lock"
$sotJson  = Join-Path $root "src\source_of_truth.lock.json"
$execJson = Join-Path $root "execution.lock.json"

$inventory = Join-Path $root "inventory"
if(!(Test-Path $inventory)){ throw "KPA_FAIL inventory missing" }
if(!(Test-Path $sotTxt)){ throw "KPA_FAIL missing src\source_of_truth.lock" }

function Sha256File([string]$p){
  (Get-FileHash -Algorithm SHA256 -Path $p).Hash.ToUpper()
}

# read legacy SOT lock and normalize newlines
$raw = Get-Content -LiteralPath $sotTxt -Raw -ErrorAction Stop
$raw = $raw -replace "`r`n", "`n"
$raw = $raw -replace "`r", "`n"
$lines = $raw -split "`n"

$files = @{}

foreach($line0 in $lines){
  $line = $line0.Trim()
  if([string]::IsNullOrWhiteSpace($line)){ continue }

  if($line -match "SHA256=([0-9A-Fa-f]{64})"){
    $hash = $Matches[1].ToUpper()

    if($line.StartsWith("source_of_truth:")){
      $files["mocka_ai.py"] = $hash
      continue
    }

    if($line.StartsWith("source_of_truth_dep:")){
      $rest = $line.Substring("source_of_truth_dep:".Length).Trim()
      $name = $rest.Split("@")[0].Trim()
      if([string]::IsNullOrWhiteSpace($name)){ throw "KPA_FAIL invalid dep name line" }
      $files[$name] = $hash
      continue
    }
  }
}

if($files.Keys.Count -lt 1){ throw "KPA_FAIL legacy SOT lock parse produced 0 files" }

# verify current src files match hashes in legacy lock
foreach($k in $files.Keys){
  $p = Join-Path $root ("src\" + $k)
  if(!(Test-Path $p)){ throw ("KPA_FAIL missing src file: " + $k) }
  $act = Sha256File $p
  $exp = $files[$k]
  if($act -ne $exp){
    throw ("KPA_FAIL SHA mismatch: " + $k + " expected=" + $exp + " actual=" + $act)
  }
}

# write JSON atomically
$tmpSot  = $sotJson + ".tmp"
$tmpExec = $execJson + ".tmp"

$objSot = @{
  format    = "json"
  locked_at = $utc
  files     = $files
}

($objSot | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $tmpSot -Encoding UTF8
Move-Item -LiteralPath $tmpSot -Destination $sotJson -Force

$objExec = @{
  format        = "json"
  fixed_at      = $utc
  sot_lock_ref  = "src/source_of_truth.lock.json"
  sot_locked_at = $objSot.locked_at
}

($objExec | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $tmpExec -Encoding UTF8
Move-Item -LiteralPath $tmpExec -Destination $execJson -Force

# inventory ritual log (atomic-ish)
$ritualDir = Join-Path $inventory ("phase7_reconfirm_" + $utcTag)
New-Item -ItemType Directory -Path $ritualDir -ErrorAction Stop | Out-Null

Copy-Item -LiteralPath $sotJson  -Destination (Join-Path $ritualDir "source_of_truth.lock.json") -Force
Copy-Item -LiteralPath $execJson -Destination (Join-Path $ritualDir "execution.lock.json") -Force

$scriptPath = Join-Path $root "tools\execution_reconfirm.ps1"
$meta = @(
  "utc=" + $utc,
  "script_path=" + $scriptPath,
  "script_sha256=" + (Sha256File $scriptPath),
  "sot_json_sha256=" + (Sha256File $sotJson),
  "exec_json_sha256=" + (Sha256File $execJson)
) -join "`n"
Set-Content -LiteralPath (Join-Path $ritualDir "ritual_meta.txt") -Value ($meta + "`n") -Encoding UTF8

Write-Host ("OK: execution reconfirmed UTC=" + $utc)
Write-Host ("WROTE: " + $sotJson)
Write-Host ("WROTE: " + $execJson)
Write-Host ("LOG:  " + $ritualDir)
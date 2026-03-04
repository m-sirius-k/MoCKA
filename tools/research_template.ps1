param(
    [string]$ExperimentID
)

$root = Resolve-Path "."
$tools = Join-Path $root "MoCKA\tools"
$expDir = Join-Path $root "MoCKA\experiments"

if(!(Test-Path $expDir)){
    New-Item -ItemType Directory $expDir | Out-Null
}

$script = Join-Path $expDir ("exp_" + $ExperimentID + ".ps1")

@"
Write-Host "RUN_EXPERIMENT: $ExperimentID"

# NOTE:
# ここに実験ロジックを書く

Write-Host "OK_EXPERIMENT: $ExperimentID"
exit 0
"@ | Set-Content -Encoding UTF8 $script

Write-Host "CREATED:" $script

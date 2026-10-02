################################################################################
# step_c_precheck.ps1
# Phase 5.0 STEP C - Real Runtime Boundary Verification Pre-Check
#
# Purpose:
#   Verify Windows environment is ready for STEP C execution
#   Check MCP Server, commit alignment, and test readiness
#
# Execute on Windows:
#   PowerShell -ExecutionPolicy Bypass -File runtime/step_c_precheck.ps1
################################################################################

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PHASE 5.0 STEP C - REAL RUNTIME BOUNDARY VERIFICATION PRE-CHECK" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$MoCKAPath = "C:\Users\sirok\MoCKA"
$MCP_URL = "http://localhost:5002"
$APP_URL = "http://localhost:5000"

# ============================================================================
# 1. VERIFY MOCKA PATH
# ============================================================================
Write-Host "[1/5] Verifying MoCKA Path..." -ForegroundColor Yellow

if (-not (Test-Path $MoCKAPath)) {
    Write-Host "ERROR: MoCKA path not found: $MoCKAPath" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: MoCKA path exists" -ForegroundColor Green
Write-Host "  Path: $MoCKAPath"
Write-Host ""

# ============================================================================
# 2. CHECK CURRENT COMMIT
# ============================================================================
Write-Host "[2/5] Checking Current Commit..." -ForegroundColor Yellow

cd $MoCKAPath

$currentBranch = git rev-parse --abbrev-ref HEAD
$currentCommit = git rev-parse --short HEAD
$expectedBranch = "claude/mocka-runtime-enforcement-evidence-k22fs8"

Write-Host "  Current Branch: $currentBranch" -ForegroundColor Cyan
Write-Host "  Current Commit: $currentCommit" -ForegroundColor Cyan

if ($currentBranch -ne $expectedBranch) {
    Write-Host "  WARNING: Expected branch '$expectedBranch' but on '$currentBranch'" -ForegroundColor Yellow
} else {
    Write-Host "  OK: On correct branch" -ForegroundColor Green
}

# Check for uncommitted changes
$untracked = git status --porcelain
if ($untracked) {
    Write-Host "  WARNING: Uncommitted changes detected:" -ForegroundColor Yellow
    Write-Host $untracked -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# 3. CHECK MCP SERVER STATUS
# ============================================================================
Write-Host "[3/5] Checking MCP Server Status..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "$MCP_URL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  OK: MCP Server responding (port 5002)" -ForegroundColor Green
    Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Cyan
} catch {
    Write-Host "  ERROR: MCP Server not responding at $MCP_URL" -ForegroundColor Red
    Write-Host "  Action: Start MCP Server with: MoCKA-START.bat" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# ============================================================================
# 4. CHECK COMMAND CENTER STATUS
# ============================================================================
Write-Host "[4/5] Checking COMMAND CENTER Status..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "$APP_URL/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  OK: COMMAND CENTER responding (port 5000)" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: COMMAND CENTER not responding at $APP_URL" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# 5. VERIFY TEST SCRIPTS
# ============================================================================
Write-Host "[5/5] Verifying Test Scripts..." -ForegroundColor Yellow

$testScripts = @(
    "runtime/enforcement_verification.py",
    "runtime/live_enforcement_evidence.py",
    "runtime/step_c_precheck.ps1"
)

$allPresent = $true
foreach ($script in $testScripts) {
    $fullPath = Join-Path $MoCKAPath $script
    if (Test-Path $fullPath) {
        Write-Host "  OK: $script" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $script" -ForegroundColor Red
        $allPresent = $false
    }
}
Write-Host ""

# ============================================================================
# READINESS SUMMARY
# ============================================================================
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PRE-CHECK SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

if (-not $allPresent) {
    Write-Host "STATUS: NOT READY - Missing test scripts" -ForegroundColor Red
    exit 1
}

Write-Host "STATUS: READY FOR STEP C EXECUTION" -ForegroundColor Green
Write-Host ""
Write-Host "Next Step:" -ForegroundColor Cyan
Write-Host "  python runtime/enforcement_verification.py" -ForegroundColor White
Write-Host ""
Write-Host "This will execute:" -ForegroundColor Cyan
Write-Host "  - CASE A: Valid Human Gate Approval -> ALLOW" -ForegroundColor White
Write-Host "  - CASE B: No Authorization -> GL7_EXECUTION_BLOCKED" -ForegroundColor White
Write-Host "  - CASE C: Scope Mismatch -> SCOPE_DENIED" -ForegroundColor White
Write-Host "  - CASE D: Direct Path Bypass -> NO_EXTERNAL_EFFECT" -ForegroundColor White
Write-Host ""

Write-Host "Output: Human_Gate_Runtime_Enforcement_Evidence_v1_RUNTIME.json" -ForegroundColor Cyan
Write-Host ""

exit 0

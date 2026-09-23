# T2 E2E Test Runner
# HAB/JARVIS → Human Gate → Authorization → Runtime → Execution

Write-Host "=" * 80
Write-Host "T2 E2E CONNECTION TEST RUNNER"
Write-Host "=" * 80
Write-Host ""

$MoCKA_DIR = "C:\Users\sirok\MoCKA"
$PYTHON = "python"

# Check if databases exist
Write-Host "[CHECK] Database files..."
$DB_PATH = "$MoCKA_DIR\data\mocka_events.db"
if (Test-Path $DB_PATH) {
    Write-Host "  ✓ mocka_events.db found"
} else {
    Write-Host "  ✗ mocka_events.db not found - will be created on first access"
}
Write-Host ""

# Run test
Write-Host "[RUN] Starting HAB/JARVIS Connector E2E Test..."
Write-Host "-" * 80
Write-Host ""

Set-Location $MoCKA_DIR

# Execute test
& $PYTHON test_hab_jarvis_connector.py

Write-Host ""
Write-Host "=" * 80
Write-Host "TEST COMPLETE"
Write-Host "=" * 80

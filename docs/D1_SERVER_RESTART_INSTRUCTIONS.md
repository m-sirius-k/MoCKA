# D1 MCP Server Restart Instructions

## Prerequisite for D1 Runtime Verification

The D1 code changes are implemented and committed, but the MCP Server process
currently has the OLD code loaded in memory. The server must be restarted to
load the updated `structural/execution_governance.py` with BINARY_EXTENSIONS.

---

## Server Identification

**Process**: mocka_mcp_server.py
**Port**: localhost:5002
**Environment**: Windows machine (C:\Users\sirok\MoCKA\)
**Auto-start**: Via MoCKA-START.bat (Desktop)

---

## Restart Procedure

### Option 1: Automated Restart (Recommended)

If MoCKA-START.bat is available:
```
1. Press Ctrl+C in command windows running MCP server
   (Terminates both COMMAND CENTER and MCP server)
2. Run MoCKA-START.bat from Desktop
   (This restarts all services including MCP server)
3. Wait for console output to show:
   "MCP server: HTTP 5002 running"
```

### Option 2: Manual Restart

```bash
# Stop the server
# Option A: Ctrl+C in the Python console running mocka_mcp_server.py
# Option B: taskkill /IM python.exe /F (kills all Python processes - use with care)

# Restart the server
cd C:\Users\sirok\MoCKA
python mocka_mcp_server.py

# Expected output:
# MCP server running on http://0.0.0.0:5002
# Server ready for requests
```

### Option 3: Via PowerShell

```powershell
# Restart MCP server specifically
Stop-Process -Name python -Force
Start-Sleep -Seconds 2
cd 'C:\Users\sirok\MoCKA'
python mocka_mcp_server.py
```

---

## Verification of Server Restart

After restart, verify the server has loaded the new code:

```bash
# Check that BINARY_EXTENSIONS is loaded in the new process
# Method 1: Check MCP server logs for any errors
# Expected: No errors, server listening on :5002

# Method 2: Quick status check (if HEALTH endpoint is available)
curl http://localhost:5002/health

# Method 3: Test by attempting mocka_write_event
# If mocka_write_event succeeds → server has new code
# If GL7_EXECUTION_BLOCKED with encoding_mismatch → server still has old code
```

---

## Expected Changes After Restart

When the server loads the new code:

1. **BINARY_EXTENSIONS constant** is initialized with:
   - .sqlite, .sqlite-shm, .sqlite-wal, .db
   - .pdf, .png, .jpg, .jpeg, .gif
   - .docx, .xlsx, .pptx, .zip, .bin

2. **GL7 abort conditions** now include `encoding_mismatch`

3. **_check_encoding_mismatches() method** is available for encoding validation

4. **Binary files are excluded** from UTF-8 encoding check

---

## What Does NOT Change

- ✓ CR runtime behavior (unchanged)
- ✓ Event ledger schema (unchanged)
- ✓ Governance contracts (unchanged)
- ✓ Baseline tests (unchanged - 117 CR Trial tests still pass)
- ✓ Phase 2-1 tests (unchanged - 9 tests still pass)

---

## Timing

The restart should take < 30 seconds:
- 5 seconds: Server process shutdown
- 5 seconds: Module reload / import time
- 20 seconds: Initialization and ready

Total: ~30 seconds until server is ready for requests

---

## Troubleshooting

### Issue: Port 5002 still in use after restart

```powershell
# Find process using port 5002
netstat -ano | findstr :5002

# Kill the lingering process
taskkill /PID <PID> /F

# Then restart normally
```

### Issue: Import errors after restart

If you see `ImportError` or `ModuleNotFoundError`:
1. Verify Python path includes C:\Users\sirok\MoCKA
2. Verify structural/execution_governance.py exists and is readable
3. Check for syntax errors: `python -m py_compile structural/execution_governance.py`

### Issue: Server starts but GL7 still blocks on encoding_mismatch

This indicates the server is still running old code:
1. Verify server process was actually killed
2. Check Python process list: `tasklist /FI "IMAGENAME eq python.exe"`
3. Restart again, ensuring all old processes are gone
4. Verify file timestamp: `dir structural/execution_governance.py`
   Should show recent modification time

---

## After Successful Restart

Once server restart is confirmed complete:

1. Proceed to D1_RUNTIME_VERIFICATION_PROTOCOL_v0.1.md
2. Execute 7-item verification sequence
3. Document evidence for each item
4. Report D1 status to Human Gate

---

## Timeline

- **Restart time**: ~30 seconds
- **Verification time**: ~5 minutes (7 items)
- **Evidence collection**: ~2 minutes
- **Total**: ~37 minutes for complete D1 verification

---

## Contact Points

If server restart fails:
- Check System Event Log for errors
- Verify PYTHONPATH includes C:\Users\sirok\MoCKA
- Verify mocka_mcp_server.py exists and is readable
- Check if port 5002 is blocked by firewall

---

## References

- Implementation: Commit f7b84cb
- Audit: D1_CHANGE_EVENT_RECORDING_RECOVERY_AUDIT_v0.1.md
- Verification protocol: D1_RUNTIME_VERIFICATION_PROTOCOL_v0.1.md
- Status summary: D1_STATUS_SUMMARY_20260828.md

# HG-15 Normal Runtime Baseline Collector
## Windows Execution Guide

Date: 2026-09-05
Version: 1.0
Audience: Windows PC Administrator

---

## Overview

This guide provides step-by-step instructions for executing the HG-15 Normal Runtime Baseline Collector on Windows.

**Purpose:** Collect evidence of MoCKA-START.bat normal execution to enable F-SC-002 reassessment.

**Duration:** 5-20 minutes

**Risk Level:** MINIMAL (observation only, no modifications)

---

## Pre-Execution Checklist

Before running the Collector, verify the following:

### Checklist Item 1: PowerShell Version
```
Open PowerShell and run:
  $PSVersionTable.PSVersion

Expected Result: Version 5.0 or higher (e.g., 5.1.19041.1234)

If Version < 5.0:
  ERROR: Cannot proceed. Requires PowerShell 5.0+
  Action: Upgrade PowerShell and retry.
```

### Checklist Item 2: Python Runtime
```
Open PowerShell and run:
  python --version

Expected Result: Python 3.6 or higher (e.g., Python 3.9.13)

If Python not found:
  WARNING: Assuming Python in PATH or MoCKA directory
  Action: Verify MoCKA-START.bat can find Python, or install Python
```

### Checklist Item 3: Existing MoCKA Processes
```
Open PowerShell and run:
  Get-Process -Name python -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -match "tech_watcher|risk_scorer" }

Expected Result: No results (empty output)

If processes found:
  ERROR: Cannot proceed. Existing processes will cause BAT to abort.
  Action (Option A): Manually terminate processes
    - Identify PIDs from output
    - Run: Stop-Process -Id <PID> -Force
    - Then retry Collector
  
  Action (Option B): Wait for processes to complete naturally
    - Monitor with: Get-Process -Name python
    - When no tech_watcher/risk_scorer processes remain, retry
```

### Checklist Item 4: MoCKA-START.bat Exists
```
Open PowerShell and run:
  Test-Path C:\Users\sirok\MoCKA\MoCKA-START.bat

Expected Result: True

If False (file not found):
  ERROR: BAT file missing
  Action: Verify path and ensure MoCKA is installed correctly
```

### Checklist Item 5: Output Directory
```
Verify directory exists or will be created:
  C:\Users\sirok\MoCKA\BASELINE_EVIDENCE

Expected: Directory accessible for writing

If access denied:
  ERROR: Cannot write to directory
  Action: Check file permissions or create directory manually
```

### Checklist Item 6: Disk Space
```
Open PowerShell and run:
  Get-Volume -DriveLetter C | Select-Object SizeRemaining

Expected: At least 50 MB free

If < 50 MB:
  WARNING: Low disk space (collection may still proceed)
  Action: Free up disk space or accept risk of incomplete collection
```

**BEFORE PROCEEDING:** All checklist items must show "Expected Result" (or have approved exception).

---

## Step 1: Download / Locate Collector Script

The Collector script is:
```
HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1
```

Options for acquiring the script:

**Option A: From Claude Code**
1. Download file from Claude Code artifact
2. Save to: `C:\Users\sirok\Desktop\HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1`

**Option B: From Email/Share**
1. Receive script from email or shared drive
2. Save to: `C:\Users\sirok\Desktop\HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1`

**Option C: Copy-Paste into PowerShell ISE**
1. Open PowerShell ISE
2. Copy-paste entire script into editor
3. Save as: `C:\Users\sirok\Desktop\HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1`

**Verification:** After saving, check file exists:
```
Test-Path C:\Users\sirok\Desktop\HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1
```
Expected: True

---

## Step 2: Open PowerShell (Administrator)

1. Click Start Menu
2. Search for "PowerShell"
3. Right-click "Windows PowerShell"
4. Select "Run as Administrator"
5. Click "Yes" when prompted for User Account Control

Expected: PowerShell window opens with title "[Administrator]"

---

## Step 3: Set Execution Policy

PowerShell has security restrictions on running scripts. Temporarily allow script execution:

```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

When prompted, type: `Y` and press Enter

Expected: Command completes with no error

This setting is temporary (current PowerShell session only) and will revert when you close the terminal.

---

## Step 4: Navigate to Script Location

```
cd C:\Users\sirok\Desktop
```

Verify you are in the correct directory:
```
pwd
```

Expected output:
```
Path
----
C:\Users\sirok\Desktop
```

---

## Step 5: Execute the Collector Script

**CRITICAL:** Before executing, ensure:
- [ ] Pre-execution checklist completed
- [ ] No existing tech_watcher or risk_scorer processes
- [ ] PowerShell running as Administrator

Execute:
```
.\HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1
```

Expected output will show:
```
======== HG-15 NORMAL RUNTIME BASELINE COLLECTOR ========
Target: C:\Users\sirok\MoCKA\MoCKA-START.bat
Output Directory: C:\Users\sirok\MoCKA\BASELINE_EVIDENCE
Collection Time: 2026-09-05T13:00:00.000Z

[PHASE 0] Precondition Verification...
  OK: BAT file found
  OK: BAT SHA-256: abc123...
  ...
```

---

## Step 6: Monitor Execution

The Collector will execute through multiple phases:

### Phase 0: Precondition Verification (5 seconds)
```
Expected: All checks pass (OK)
If ERROR: Script aborts (read error message for guidance)
```

### Phase 1-3: Pre-Collection Setup (5 seconds)
```
Expected: Directory creation, monitoring job started
If WARNING: Note warning but continue
```

### Phase 4: MoCKA-START.bat Execution (5-20 minutes)
```
Expected: Script shows "Execution Start" message
Action: WAIT - Do NOT interrupt execution
Status: Script is now running your BAT file
Observation: PowerShell will capture output in background
```

### Phase 5-10: Post-Collection Analysis (10 seconds)
```
Expected: Snapshots captured, manifests generated
Status: Script is processing collected evidence
```

### Final Output: Summary Report
```
Expected output:
======== COLLECTION COMPLETE ========

Collection ID: HG15-BASELINE-20260905-123456
Status: ACQUIRED
Exit Code: 0
Duration: 12.5 seconds

Evidence Directory: C:\Users\sirok\MoCKA\BASELINE_EVIDENCE

Files Generated:
  OK: 00_PROCESS_LIST_BEFORE.csv (25.3 KB)
  OK: 02_PROCESS_MONITOR_SAMPLES.csv (15.7 KB)
  OK: 03_STDOUT.txt (2.1 KB)
  OK: 04_STDERR.txt (0.0 KB)
  OK: 05_PROCESS_LIST_AFTER.csv (25.4 KB)
  OK: 06_PROCESS_DIFF.csv (0.5 KB)
  OK: 07_EVENTLOG_APPLICATION.txt (45.3 KB)
  OK: 08_EVENTLOG_SYSTEM.txt (43.1 KB)
  OK: 09_COLLECTION_MANIFEST.json (2.0 KB)

======== NEXT STEPS ========
```

---

## Step 7: Verify Collection Success

After the script completes, verify evidence files were created:

```
ls C:\Users\sirok\MoCKA\BASELINE_EVIDENCE
```

Expected output: 9 files listed (00_* through 09_*)

If files are missing or script aborted:
- Note the abort reason from script output
- Refer to **Abort Scenarios** section below

---

## Step 8: Check for Errors in STDOUT/STDERR

The Collector captured the MoCKA-START.bat output. Review for errors:

```
type C:\Users\sirok\MoCKA\BASELINE_EVIDENCE\03_STDOUT.txt
```

Expected: Application output (varies based on MoCKA implementation)

If errors visible:
- Note error messages
- Check if exit code indicates success (0) or failure (non-zero)

---

## Step 9: Close PowerShell

```
exit
```

Or simply close the PowerShell window.

---

## Step 10: Provide Evidence Files to KUROKO

Next step is analysis by KUROKO. Provide the 9 evidence files from:
```
C:\Users\sirok\MoCKA\BASELINE_EVIDENCE\
```

Methods to share:
1. **Email:** Zip and email files to KUROKO contact
2. **Shared Drive:** Copy files to shared network location
3. **Upload to Claude Code:** Share with KUROKO via web interface

Files to share:
```
00_PROCESS_LIST_BEFORE.csv
02_PROCESS_MONITOR_SAMPLES.csv
03_STDOUT.txt
04_STDERR.txt
05_PROCESS_LIST_AFTER.csv
06_PROCESS_DIFF.csv
07_EVENTLOG_APPLICATION.txt
08_EVENTLOG_SYSTEM.txt
09_COLLECTION_MANIFEST.json
```

---

## Abort Scenarios

If the Collector aborts during execution, one of the following scenarios occurred:

### Scenario A: Preconditions Not Met
```
Message: "PRECONDITIONS_UNMET"
Examples:
  - BAT file not found
  - Python runtime not available
  - PowerShell version < 5.0
  - Existing MoCKA processes detected

Action:
1. Read the specific error message from script output
2. Fix the precondition (install Python, clean up processes, etc.)
3. Retry execution (Step 5)
```

### Scenario B: Existing Process Conflict
```
Message: "EXISTING_PROCESS_CONFLICT"
Details: python.exe [PID: XXXX] running tech_watcher or risk_scorer

Action:
1. The script detected existing processes that will interfere
2. MoCKA-START.bat will abort with Exit Code 1 (double-execution protection)
3. Choose one of:
   Option A: Terminate existing processes manually
     - Run: taskkill /PID <PID> /F (replace XXXX with actual PID)
     - Retry Collector (Step 5)
   Option B: Wait for processes to complete naturally
     - Check status: Get-Process -Name python
     - When empty, retry Collector
   Option C: Understand this is expected behavior
     - The abort IS the evidence (shows protection works)
     - F-SC-002 reassessment will be: ABORTED_DOUBLE_EXECUTION
     - Baseline not acquired in this case
```

### Scenario C: Observation Method Failed
```
Message: "OBSERVATION_FAILED" or missing output files

Possible Causes:
  - Event Log service not running
  - Permission denied on monitoring
  - Insufficient disk space

Action:
1. Verify disk space: Get-Volume -DriveLetter C
2. Verify Event Log running: Get-Service EventLog
3. Re-run script to retry observation
```

### Scenario D: Partial Evidence
```
Message: "PARTIAL" or some files created but others missing

Action:
1. Review which files were created
2. Check if MoCKA-START.bat executed (check 03_STDOUT.txt)
3. KUROKO will analyze partial evidence and note gaps
4. Provide files to KUROKO for analysis
```

---

## Troubleshooting

### "PowerShell: command not found"
- PowerShell not installed
- Action: Install PowerShell 5.1 or higher

### "Access Denied" when running script
- PowerShell Execution Policy still restricted
- Action: Run "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process" again

### "MoCKA-START.bat not found"
- Wrong path
- Action: Verify path is correct and BAT file exists

### "Python version not found" but tech_watcher runs
- Python may be installed locally or in PATH differently
- Action: Proceed; Collector will attempt execution anyway

### "Disk space too low"
- Not enough space for evidence files
- Action: Delete unnecessary files and retry, or proceed with reduced collection

### "Existing processes detected - cannot continue"
- MoCKA already running
- Action: Wait for it to complete, or manually terminate (see Abort Scenario B)

### "Script hangs during Phase 4"
- MoCKA-START.bat is running; this is normal
- Action: WAIT - do not interrupt. Execution can take 5-20 minutes
- Only interrupt if certain BAT has frozen (check with Task Manager)

---

## Success Indicators

Collection was **SUCCESSFUL** if:
1. Script output shows "ACQUIRED" in Status
2. All 9 files created in C:\Users\sirok\MoCKA\BASELINE_EVIDENCE\
3. 09_COLLECTION_MANIFEST.json shows "status": "ACQUIRED"
4. Exit Code in final report shows 0 (success) or 1 (expected abort for double-execution)
5. BAT file SHA-256 unchanged (proof no modification occurred)

Collection was **PARTIAL** if:
- Some files created but not all 9
- Status shows "PARTIAL" or "ABORTED_DOUBLE_EXECUTION"
- KUROKO will analyze what evidence exists

---

## Important Reminders

**DO:**
- Run PowerShell as Administrator
- Verify pre-execution checklist
- Wait for full execution (do not interrupt)
- Review exit code and error messages
- Provide all 9 evidence files to KUROKO

**DO NOT:**
- Modify any MoCKA files during collection
- Terminate processes without understanding consequences
- Run multiple Collectors simultaneously
- Edit evidence files after collection
- Assume "no errors" means success (check exit code)

---

## Final Check

Before submitting evidence to KUROKO, verify:
```
dir C:\Users\sirok\MoCKA\BASELINE_EVIDENCE\ /S
```

Expected: 9 files (00_* through 09_*) totaling 100-200 KB

If fewer files or smaller size than expected:
- Likely scenario: MoCKA-START.bat aborted early or did not run
- Check 03_STDOUT.txt and 04_STDERR.txt for error messages
- Provide files to KUROKO for analysis (even if partial)

---

## Contact

If collector script fails to run or produces unexpected results:
1. Collect the error messages from PowerShell window
2. Screenshot the final output
3. Check Task Manager for any MoCKA processes still running
4. Provide output and screenshots to KUROKO for troubleshooting

---

END OF EXECUTION GUIDE

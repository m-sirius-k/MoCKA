# HG-15 Normal Runtime Baseline Acquisition Plan
## Strategic Plan for F-SC-002 Runtime Baseline Evidence Collection

Date: 2026-09-05
Version: 1.0
Target: C:\Users\sirok\MoCKA environment

---

## 1. Strategic Objectives

### 1.1 Primary Objective
Establish a Normal Runtime Baseline for MoCKA-START.bat execution that enables direct reassessment of F-SC-002:
```
F-SC-002 Claim: tech_watcher.py exits before risk_scorer.py starts
Current Status: UNRESOLVED / EVIDENCE_GAP (initial T2-P1 attempt aborted)
Baseline Purpose: Acquire time-series evidence where normal execution succeeds
```

### 1.2 Secondary Objectives
- Understand normal process sequence and timing for future baseline comparisons
- Document preconditions under which normal execution is possible
- Establish evidence integrity mechanisms to detect any modifications
- Create reproducible observation methodology for potential re-verification

---

## 2. Current State Analysis

### 2.1 What We Know (CONFIRMED from T2-P1 ABORT)
```
Event: MoCKA-START.bat execution attempt on 2026-09-05 at 12:12:12Z
Result: Exit Code 1
Reason: Double-execution detection triggered
Evidence: 01_SNAPSHOT_BEFORE.csv, 04_SNAPSHOT_AFTER.csv indicate existing MoCKA processes
Status: This is EXPECTED behavior (protection mechanism working)
```

### 2.2 What We Do NOT Know (EVIDENCE GAP)
```
F-SC-002 Claim: tech_watcher EXIT → risk_scorer START
Current Evidence: NONE (BAT aborted before reaching this phase)
Gap Type: PRECONDITION_FAILURE (could not attempt normal runtime)
Baseline Needs: Clean execution from T1 through T6
```

### 2.3 Why Standard Execution Failed
```
Windows PC has active MoCKA process(es) from prior operation
MoCKA-START.bat includes anti-double-execution logic (good design)
Protection triggered: Exit Code 1 instead of normal startup
Next Attempt: Must clear existing processes OR verify protection behavior is intended
```

---

## 3. Baseline Acquisition Strategy

### 3.1 Three-Path Strategy

**Path A: Clean Execution (Preferred)**
- Prerequisite: No existing MoCKA processes
- Observation: Full T1-T6 sequence
- Duration: 5-15 minutes (depends on tech_watcher and risk_scorer runtimes)
- Success Criteria: All A-H satisfied
- Risk: Low (observation only)
- Authorization Required: None (monitoring does not modify system)

**Path B: Detect Protection Behavior (Fallback)**
- Prerequisite: Allow existing processes to remain
- Observation: Capture MoCKA-START.bat detecting double-execution
- Result: Exit Code 1 (expected)
- Duration: 5-30 seconds
- Success Criteria: A-none (normal chain not executed)
- Risk: Minimal
- Authorization Required: None
- Note: This confirms protection logic works, but does NOT satisfy F-SC-002 baseline

**Path C: Forced Clean (Manual Intervention)**
- Prerequisite: User manually terminates existing MoCKA processes
- Authority Boundary: User responsible for cleanup
- Observation: Proceed with Path A
- Risk: Moderate (requires external knowledge of process state)
- Authorization Required: User decision (not automatic)

### 3.2 Default Path Selection
**Recommended: Path A or Path C**

Path B (observe protection behavior) is not sufficient for F-SC-002 reassessment.

Collector behavior:
```
1. Check for existing processes (tech_watcher, risk_scorer)
2. If found: Report status as ABORT / EXISTING_PROCESS_CONFLICT
   - Do NOT auto-kill
   - Guide user to manual cleanup
   - Propose Path C if user consents
3. If not found: Execute Path A
   - Launch MoCKA-START.bat
   - Observe full execution sequence
   - Record all events T0-T6
```

---

## 4. Preconditions and Environment Verification

### 4.1 Must-Have Preconditions
Before attempting baseline acquisition, verify:

**4.1.1 MoCKA Source Files Exist and Unmodified**
```
Path: C:\Users\sirok\MoCKA\MoCKA-START.bat
Check: File exists
Check: File not modified since last verification
Check: SHA-256 matches baseline (to be established on first run)
Action: Abort if file modified (indicates unauthorized changes)
```

**4.1.2 Python Runtime Available**
```
Check: python.exe is accessible in PATH or MoCKA directory
Check: Python version compatible (3.6+)
Action: Abort if Python not found (precondition failure)
```

**4.1.3 Windows Services Running**
```
Service: Windows Event Log service (for observation method 2)
Status: Must be running (required for evidence collection)
Service: Process Trace Session (for observation method 1 - ETW)
Status: Should be available (optional, enhances precision)
Action: Warn if Event Log disabled; abort if cannot collect evidence at all
```

**4.1.4 PowerShell Version**
```
Minimum: PowerShell 5.0
Recommended: PowerShell 5.1 or higher
Check: $PSVersionTable.PSVersion
Action: Abort if PowerShell < 5.0 (insufficient ETW/event log query capabilities)
```

### 4.2 Should-Have Preconditions

**4.2.1 No Competing Processes**
```
Command: Get-Process python -ErrorAction SilentlyContinue | 
         Where-Object { $_.CommandLine -match "tech_watcher|risk_scorer" }
Expected: No results
Action: If found: Report and abort (unless user consents to cleanup)
```

**4.2.2 Sufficient Disk Space**
```
Minimum: 100 MB free in C:\Users\sirok\MoCKA
Purpose: Evidence output files (typically 50-100 MB)
Action: Warn if disk space < 100 MB; continue if > 50 MB
```

**4.2.3 Working Directory Accessible**
```
Path: C:\Users\sirok\MoCKA
Check: User has read/write permissions
Check: No file locks or access denied
Action: Abort if directory not accessible
```

### 4.3 Precondition Verification Checklist
The Collector performs this checklist automatically:
```
[ ] MoCKA-START.bat exists and unmodified
[ ] Python runtime available
[ ] Windows Event Log service running
[ ] PowerShell version >= 5.0
[ ] No competing MoCKA processes (or user confirmed cleanup)
[ ] Disk space >= 50 MB
[ ] Working directory accessible
[ ] UAC/permissions allow process monitoring
```

---

## 5. Observation Method Selection

### 5.1 Primary Method: ETW (Event Tracing for Windows)
**Why ETW?**
- Kernel-level observation (most accurate)
- Millisecond precision
- Captures command-line arguments
- Non-invasive (monitoring only)

**How ETW Works:**
1. Create temporary trace session: `logman create trace HG15_Baseline -ow`
2. Enable Process Tracing provider (includes process creation/termination events)
3. Start trace before BAT execution
4. Execute MoCKA-START.bat
5. Stop trace after BAT exits
6. Parse .etl file for process events

**Fallback if ETW Unavailable:**
- ETW requires Admin privileges
- Some Windows versions may have restricted ETW
- Fall back to Method 2 (Event Log) or Method 3 (Process Monitor)

### 5.2 Secondary Method: Windows Event Log
**Why Event Log?**
- Available on all Windows systems
- Persistent storage (survives reboot)
- Lower precision but usually sufficient

**How Event Log Works:**
1. Query Application event log for process creation/termination (Event ID 4688)
2. Cross-reference with timestamps
3. Extract command-lines and PIDs

**Limitation:**
- Depends on Audit Policy enabling process creation events
- May not be enabled by default
- 1-second precision (vs milliseconds for ETW)

### 5.3 Tertiary Method: PowerShell Process Monitor
**Why Fallback to PowerShell?**
- Works on all Windows systems
- No special setup required
- Reliable detection of process appearance/disappearance

**How Process Monitor Works:**
1. Start background job: Get-Process -Name python repeatedly
2. Sample process list at 500ms intervals
3. Detect appearance/disappearance of python.exe
4. Record process name, PID, parent PID

**Limitation:**
- Discrete sampling (may miss very short processes < 500ms)
- Lower precision
- Cannot capture exact exit time

### 5.4 Method Selection Logic
```
if (ETW available and Admin privileges) {
    Use Method 1 (ETW)
} else if (Event Log process audit enabled) {
    Use Method 2 (Event Log)
} else {
    Use Method 3 (PowerShell Process Monitor)
}
```

Collector attempts Method 1 first; automatically falls back if unavailable.

---

## 6. Evidence Collection Workflow

### 6.1 Pre-Collection Phase (T-1 minute)
```
1. Verify preconditions (checklist from 4.3)
2. Check for existing processes
3. Establish observation baseline (snapshot of process state)
4. Create output directory: C:\Users\sirok\MoCKA\BASELINE_EVIDENCE
5. Initialize trace session (if using ETW)
6. Record observation start timestamp (T0)
```

### 6.2 Collection Phase (T0 to T6)
```
[T0] Observation Started
     └─ Timestamp recorded
     └─ ETW trace enabled (or Event Log monitoring)
     
[T1] MoCKA-START.bat Execution
     └─ Command: cd C:\Users\sirok\MoCKA && MoCKA-START.bat
     └─ Observe: cmd.exe process creation
     └─ Record: start time, PID, command-line
     
[T2-T6] Continuous Observation
     └─ ETW events streaming to trace buffer
     └─ Process monitor sampling running
     └─ Event log configured to capture events
     
[T6] MoCKA-START.bat Exit
     └─ Observe: cmd.exe process termination
     └─ Record: exit time, exit code
     
[T6+1s] Observation Ended
        └─ Stop trace session
        └─ Query event log for final events
        └─ Generate evidence summary
```

### 6.3 Post-Collection Phase (T6+5s to T6+60s)
```
1. Parse ETW trace file / Event Log queries
2. Extract process events in chronological order
3. Build event timeline (T0-T6 sequence)
4. Compute time intervals
5. Verify evidence integrity
6. Check for modifications (SHA-256 verification)
7. Generate manifest file
8. Validate success criteria (A-H)
9. Save all evidence files
10. Generate final report
```

---

## 7. Failure Modes and Abort Conditions

### 7.1 ABORT Condition 1: Existing Process Conflict
```
Detection: Get-Process finds existing tech_watcher.py or risk_scorer.py
Result: MoCKA-START.bat will exit with code 1 (protection triggered)
Action: Report and abort
Status: ABORTED / EXISTING_PROCESS_CONFLICT
F-SC-002 Evidence: NOT_ACQUIRED (cannot observe normal chain)
Recommendation: Clean up processes and retry
```

### 7.2 ABORT Condition 2: Precondition Failure
```
Detection: Required file/service not available
Examples: BAT file missing, Python runtime not found, Event Log disabled
Action: Report and abort
Status: ABORTED / PRECONDITIONS_UNMET
F-SC-002 Evidence: NOT_ACQUIRED
Recommendation: Fix precondition and retry
```

### 7.3 ABORT Condition 3: Observation Method Failure
```
Detection: All observation methods fail
Examples: ETW denied, Event Log inaccessible, Process Monitor fails
Action: Report and abort
Status: ABORTED / OBSERVATION_FAILED
F-SC-002 Evidence: NOT_ACQUIRED
Recommendation: Investigate Windows permissions and retry
```

### 7.4 INCOMPLETE: Partial Evidence
```
Detection: Some events observed (A-E met) but not all criteria (F-H failed)
Examples: Processes observed but timestamps have insufficient precision
Status: INCOMPLETE / PARTIAL_EVIDENCE
F-SC-002 Evidence: UNRESOLVED / INSUFFICIENT_PRECISION
Recommendation: Retry with Method 1 (ETW) for higher precision
```

### 7.5 SUCCESS: All Criteria Met
```
Status: ACQUIRED
Success Criteria: A-H all satisfied
F-SC-002 Evidence: DIRECTLY_OBSERVABLE
Next Step: Proceed to HG-15 reassessment
```

---

## 8. Authorization and Modification Boundaries

### 8.1 What This Plan DOES Authorize
- External observation of process creation/termination
- Reading from Windows Event Log
- Creating trace session (temporary, read-only)
- Writing evidence files to output directory
- Computing SHA-256 hashes for integrity verification

### 8.2 What This Plan DOES NOT Authorize
- Modifying MoCKA-START.bat
- Modifying any Python files
- Modifying configuration files
- Modifying database files
- Modifying Windows registry (except temporary ETW session)
- Terminating existing processes
- Restarting services
- Implementation of fixes
- Escalating to implementation phase

### 8.3 State After Baseline Acquisition
Regardless of success/failure:
```
Phase 15 = BLOCKED (no change)
Implementation Authorization = NOT ISSUED (no change)
Modification Count = 0 (verified)
Candidate Selection = DEFERRED (no change)
F-SC-002 Status = UNRESOLVED → DIRECTLY_OBSERVABLE (only if successful)
```

**Important:** Acquiring baseline evidence does NOT constitute authorization for implementation.

---

## 9. Success Criteria (A-H Mapping to Acquisition Plan)

| Criterion | What to Observe | Plan Section | Pass If |
|-----------|-----------------|--------------|---------|
| A: BAT Start | cmd.exe spawns MoCKA-START.bat | 6.2 | ETW or Event Log detects process creation |
| B: tech_watcher Start | python.exe executes tech_watcher.py | 6.2 | ETW or Event Log detects process creation with args |
| C: tech_watcher Exit | tech_watcher.py process terminates | 6.2 | ETW or Event Log detects process exit |
| D: risk_scorer Start | python.exe executes risk_scorer.py | 6.2 | ETW or Event Log detects process creation with args |
| E: risk_scorer Exit | risk_scorer.py process terminates | 6.2 | ETW or Event Log detects process exit |
| F: T3 < T4 | tech_watcher EXIT timestamp < risk_scorer START timestamp | 6.2 | Timestamps compared: T3_timestamp < T4_timestamp |
| G: PID/PPID/CmdLine | Each event has process metadata | 5 (Method 1-3) | All fields populated (or "unavailable" documented) |
| H: Reproducible | Evidence saved, manifest created | 6.3 | All files in BASELINE_EVIDENCE directory with checksums |

---

## 10. Timeline and Resource Estimates

### 10.1 Collector Execution Timeline
```
Pre-collection checks:    30 seconds
Observation duration:     5-20 minutes (depends on tech_watcher/risk_scorer runtime)
Post-collection parsing:  10-30 seconds
Report generation:        10 seconds
Total Time:              6-21 minutes
```

### 10.2 Resource Requirements
```
Disk Space: 50-100 MB (for trace files + evidence)
Memory: 50-200 MB (PowerShell + ETW buffer)
CPU: Minimal (monitoring overhead < 5%)
Network: None
Admin Rights: Required (for ETW trace session)
```

### 10.3 Collector Restart Capability
If collection is interrupted:
- Trace session remains active (must be manually stopped)
- Evidence files may be incomplete
- Re-run Collector (it will clean up and restart)

---

## 11. Deliverables from This Plan

Upon successful baseline acquisition:
```
BASELINE_EVIDENCE/
├── 001_OBSERVATION_MANIFEST.json
├── 002_PROCESS_EVENTS_ETW.csv
├── 003_PROCESS_LINEAGE.txt
├── 004_EVENT_LOG_EXTRACT.txt
├── 005_F_SC_002_TIMELINE_ANALYSIS.json
└── README.txt
```

All files include:
- Timestamp of collection
- Observation method used
- Success/failure status
- Evidence quality metrics
- Known limitations

---

## 12. Next Steps After Baseline Acquisition

**If ACQUIRED (Success):**
1. KUROKO analyzes evidence using HG15_NORMAL_RUNTIME_BASELINE_EVIDENCE_SCHEMA.md
2. Reassess F-SC-002 with direct evidence
3. Produce HG-15 Reassessment Package
4. Submit to Human Gate for implementation decision

**If ABORTED / INCOMPLETE:**
1. Document abort reason
2. Propose corrective action (fix precondition or use higher-precision method)
3. Plan retry (manual process cleanup, or re-run with ETW)
4. Maintain F-SC-002 = UNRESOLVED until baseline acquired

---

END OF ACQUISITION PLAN

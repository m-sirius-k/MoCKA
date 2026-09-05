# HG-15 Normal Runtime Baseline Acquisition Protocol
## External Observation Methodology for F-SC-002 Runtime Chaining Verification

Date: 2026-09-05
Status: Design Complete - Ready for Implementation
Target: Windows PC C:\Users\sirok\MoCKA environment
Scope: External process observation (non-invasive)

---

## 1. Protocol Overview

This protocol establishes the methodology for acquiring a "Normal Runtime Baseline" of MoCKA-START.bat execution without modifying any system files, configurations, or runtime environments.

The protocol is specifically designed to:
- Observe the complete execution sequence of MoCKA-START.bat
- Capture process creation/termination events with millisecond-precision timestamps
- Establish direct evidence for F-SC-002 Runtime Chaining assertion: tech_watcher.py EXIT before risk_scorer.py START
- Detect and document situations where normal execution cannot be observed (existing process conflicts)
- Maintain strict separation between "observation not performed" and "behavior not observed"

---

## 2. Observation Architecture

### 2.1 External Observer Pattern
The Collector operates as an external observer with NO modification rights:
- Reads from: Windows Event Log, Process creation events, Process Monitor traces
- Writes to: Evidence directory only (no system changes)
- Modifies: Nothing (zero modification guarantee)

### 2.2 Time-Series Event Capture
Instead of BEFORE/AFTER snapshots, the Collector captures DURING-phase events:

```
T0 (Observation Start)
  └─ Timestamp: [ISO 8601 with milliseconds]
  └─ Action: Enable event monitoring
  
T1 (MoCKA-START.bat Execution)
  └─ Event: cmd.exe spawns MoCKA-START.bat
  └─ Timestamp: [BAT start time]
  └─ Parent: cmd.exe [PID]
  
T2 (tech_watcher.py Process Start)
  └─ Event: python.exe executes tech_watcher.py
  └─ Timestamp: [process creation time]
  └─ Parent: MoCKA-START.bat (via cmd.exe)
  └─ Command: python.exe tech_watcher.py [args]
  
T3 (tech_watcher.py Process Exit)
  └─ Event: tech_watcher.py terminates
  └─ Timestamp: [process exit time]
  └─ Exit Code: [value]
  └─ Duration: T3 - T2
  
T4 (risk_scorer.py Process Start)
  └─ Event: python.exe executes risk_scorer.py
  └─ Timestamp: [process creation time]
  └─ Parent: MoCKA-START.bat (via cmd.exe)
  └─ Command: python.exe risk_scorer.py [args]
  
T5 (risk_scorer.py Process Exit)
  └─ Event: risk_scorer.py terminates
  └─ Timestamp: [process exit time]
  └─ Exit Code: [value]
  └─ Duration: T5 - T4
  
T6 (MoCKA-START.bat Exit)
  └─ Event: MoCKA-START.bat returns control
  └─ Timestamp: [BAT exit time]
  └─ Exit Code: [value]
```

### 2.3 F-SC-002 Direct Evidence Requirement
For F-SC-002 reassessment, this protocol MUST establish:
- T3 < T4 (tech_watcher EXIT timestamp is BEFORE risk_scorer START timestamp)
- Temporal gap between T3 and T4 (if any)
- Both T3 and T4 are directly observed (not inferred from process lists)

---

## 3. Observation Methods (Priority Order)

### Method 1: Windows Event Tracing for Processes (ETW)
**Precision:** Millisecond-level
**Coverage:** Process creation/termination with command-line arguments
**Invasiveness:** None (read-only monitoring)

Process:
1. Enable Trace Session: `logman create trace HG15_Baseline -ow`
2. Configure Process Tracing Provider
3. Start trace collection at T0
4. Capture all events during BAT execution
5. Stop trace at T6
6. Parse .etl file for process events

Advantages:
- Kernel-level observation
- Extremely precise timestamps
- No file modifications required
- Non-intrusive (trace mode only)

Limitations:
- Requires PowerShell 5.0+
- ETL parsing may be complex
- Short-lived processes might not appear if not traced early

### Method 2: Windows Event Log (Application / System)
**Precision:** Second-level
**Coverage:** Process creation events (if audit policy enabled)
**Invasiveness:** None (read-only)

Process:
1. Query Application event log for process creation
2. Query System event log for service/process events
3. Cross-reference with timestamps

Advantages:
- No special setup required
- Already available on all Windows systems
- Persistent storage

Limitations:
- Lower time precision (seconds, not milliseconds)
- May not capture all process events
- Depends on audit policy configuration

### Method 3: PowerShell Process Monitoring (Real-Time)
**Precision:** Second-level
**Coverage:** Process name, PID, parent PID
**Invasiveness:** None (read-only enumeration)

Process:
1. At T0, start background job monitoring Get-Process
2. Enumerate process state at fixed intervals (500ms)
3. Detect process appearance/disappearance
4. Cross-reference with event log

Advantages:
- No additional tools required
- Works on all Windows versions
- Easy to implement

Limitations:
- Discrete sampling (may miss short-lived processes)
- Lower precision than ETW
- May not capture exact start/exit timestamps

---

## 4. Preconditions for Normal Runtime Observation

### 4.1 System State Requirements
Before attempting normal runtime baseline acquisition, verify:

**4.1.1 Existing MoCKA Process Check**
```
Get-Process -Name python -ErrorAction SilentlyContinue | 
  Where-Object { $_.CommandLine -match "tech_watcher|risk_scorer" }
```

If existing processes are found:
- Document their PIDs, start times, command lines
- Determine if they are from a previous MoCKA execution
- DO NOT automatically kill them
- Report status as: "Existing process prevents normal startup"
- Mark evidence as: ABORTED / EXISTING_PROCESS_CONFLICT

**4.1.2 MoCKA Double-Execution Detection**
MoCKA-START.bat includes protection against double execution (as evidenced by previous ABORT with Exit Code 1).

If normal startup would trigger this protection:
- Document the detection
- Mark as: ABORTED / DOUBLE_EXECUTION_DETECTED
- Report existing process state
- DO NOT attempt to bypass protection

**4.1.3 Required Services**
Verify Windows services are running:
- Windows Event Log service (if using Method 2)
- Process Trace Session support (if using Method 1)
- Python runtime (if tech_watcher/risk_scorer depend on system Python)

**4.1.4 Environment State**
- MoCKA source directory: C:\Users\sirok\MoCKA
- BAT file: C:\Users\sirok\MoCKA\MoCKA-START.bat (must exist, unmodified)
- Python installation: System PATH or MoCKA-local
- Working directory: C:\Users\sirok\MoCKA (assumed)

### 4.2 Authorization Boundary
This protocol acquires BASELINE EVIDENCE ONLY.
Acquiring the baseline does NOT automatically authorize implementation.

State after baseline acquisition (regardless of success/failure):
```
Phase 15 = BLOCKED (maintained)
Implementation Authorization = NOT ISSUED (maintained)
Modification Count = 0 (maintained, observation only)
Candidate Selection = DEFERRED (maintained)
```

---

## 5. Evidence Integrity Mechanisms

### 5.1 Hash-Based Integrity
Each collected evidence file receives:
- SHA-256 checksum (computed at collection time)
- Timestamp of collection (ISO 8601)
- Collector version identifier
- Host information (Windows version, hostname, user)

### 5.2 Modification Counter
Before and after evidence collection:
- File count in C:\Users\sirok\MoCKA
- File modification times
- Registry key checksums (if applicable)
- Comparison ensures Modification Count = 0

### 5.3 Evidence Manifest
All evidence stored with:
```json
{
  "collection_id": "HG15-BASELINE-20260905-001",
  "observation_start": "2026-09-05T13:00:00.000Z",
  "observation_end": "2026-09-05T13:05:00.000Z",
  "target": "C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
  "status": "ACQUIRED | ABORTED | INCOMPLETE",
  "abort_reason": "null | EXISTING_PROCESS_CONFLICT | DOUBLE_EXECUTION_DETECTED | ...",
  "files": [
    { "name": "...", "sha256": "...", "size": ..., "timestamp": "..." }
  ],
  "preconditions_met": true | false,
  "f_sc_002_observable": true | false,
  "evidence_gaps": ["..."]
}
```

---

## 6. Non-Invasiveness Guarantees

### 6.1 Absolute Prohibitions
The Collector WILL NOT:
- Modify MoCKA-START.bat
- Modify any Python files
- Modify configuration files
- Modify database files
- Modify Windows registry (except temporary ETW trace session)
- Terminate existing processes
- Restart services
- Change runtime environment variables
- Execute implementation code

### 6.2 Read-Only Operations Only
The Collector WILL:
- Read from Event Log
- Read from Process Monitor
- Read file metadata
- Read process command-lines
- Read registry keys (query only)
- Write to evidence directory only

### 6.3 Post-Collection Verification
After collection completes:
- Re-check file integrity of MoCKA-START.bat (compare against T0 hash)
- Re-check file counts in target directories
- Verify no unexpected files created
- Generate modification count report (must be 0)

---

## 7. Success Criteria (A-H Validation)

Evidence collection is considered SUCCESSFUL if ALL of the following are met:

**A. MoCKA-START.bat Normal Execution Confirmed**
- Direct observation of BAT process start
- Command-line matches expected pattern
- Exit code in success range (0)

**B. tech_watcher.py START Confirmed**
- Direct observation of python.exe spawning tech_watcher.py
- Timestamp T2 recorded
- PID recorded
- Parent PID = MoCKA-START.bat process (or cmd.exe under BAT)

**C. tech_watcher.py EXIT Confirmed**
- Direct observation of tech_watcher.py process termination
- Timestamp T3 recorded
- Exit code recorded
- Process not detected in subsequent snapshots

**D. risk_scorer.py START Confirmed**
- Direct observation of python.exe spawning risk_scorer.py
- Timestamp T4 recorded
- PID recorded
- Parent PID = MoCKA-START.bat process (or cmd.exe under BAT)

**E. risk_scorer.py EXIT Confirmed**
- Direct observation of risk_scorer.py process termination
- Timestamp T5 recorded
- Exit code recorded
- Process not detected in subsequent snapshots

**F. Temporal Ordering Confirmed (T3 < T4)**
- tech_watcher.py EXIT timestamp (T3) is mathematically less than risk_scorer.py START timestamp (T4)
- Difference: T4 - T3 = gap duration (in milliseconds)
- This is direct observation, NOT inference from process lists

**G. Process Identification Complete (PID, Parent PID, Command Line)**
- For each event T1-T6:
  - PID available
  - Parent PID available (or documented as unavailable)
  - Command-line available (or documented as unavailable)
  - Confidence level recorded

**H. Evidence Reproducible and Persistent**
- All evidence files saved to C:\Users\sirok\MoCKA\BASELINE_EVIDENCE\
- Manifest file documents collection parameters
- Re-collection using same parameters should yield similar results
- Evidence immutable (SHA-256 checksums prevent tampering)

---

## 8. Failure Modes and Evidence Classification

### 8.1 Abort Conditions (F-SC-002 Cannot Be Reassessed)
Collection is ABORTED and marked for human review if:

**Condition 1: Existing Process Prevents Startup**
- Existing tech_watcher.py or risk_scorer.py detected at T0
- MoCKA-START.bat detects existing process and exits with code 1
- Status: ABORTED / EXISTING_PROCESS_CONFLICT
- F-SC-002 Evidence: NOT_ACQUIRED
- Action: Wait for manual user intervention to clean up processes

**Condition 2: Preconditions Unmet**
- Required Windows services not running
- Python runtime not available
- BAT file not found or modified
- Status: ABORTED / PRECONDITIONS_UNMET
- F-SC-002 Evidence: NOT_ACQUIRED

**Condition 3: Collection Technique Failure**
- ETW trace collection failed
- Event log unavailable
- Process monitoring failed
- Status: ABORTED / OBSERVATION_FAILED
- F-SC-002 Evidence: NOT_ACQUIRED

### 8.2 Partial Evidence (F-SC-002 Indeterminate)
Collection succeeds for some events but not all:

**Example: A-E Success, F Failure**
- All processes observed individually
- Timestamps not comparable (precision too low, or events from different sources)
- Status: INCOMPLETE / TEMPORAL_ORDER_INDETERMINATE
- F-SC-002 Evidence: UNRESOLVED / INSUFFICIENT_PRECISION
- Gap: Cannot determine if T3 < T4 with required precision

### 8.3 Complete Success (F-SC-002 Reassessable)
All A-H criteria met:
- Status: ACQUIRED
- F-SC-002 Evidence: DIRECTLY_OBSERVABLE
- Next step: Reassess F-SC-002 with baseline evidence

---

## 9. Key Definitions (Precise Language)

**"Observed"**
- Event directly detected by monitoring system (ETW, event log, or process monitor)
- Timestamp recorded at detection time
- Not inferred or assumed

**"Not Observed"**
- Monitoring system did not detect event
- May indicate: event did not occur, monitoring gap, insufficient precision, or wrong observation method

**"Not Observed" ≠ "Did Not Occur"**
- Lack of observation is NOT proof of non-occurrence
- Must be classified as EVIDENCE GAP or OBSERVATION_FAILURE

**"CONFIRMED"**
- Evidence directly supports the claim
- Observation timestamp exists
- Confidence level ≥ HIGH

**"NOT CONFIRMED"**
- Evidence does not support the claim
- OR evidence is absent
- Classified separately: NOT_OBSERVED vs CONTRADICTORY_EVIDENCE

**"UNRESOLVED"**
- Evidence is insufficient for definitive claim
- Either precision too low, or observation gap
- Requires clarification (manual review or re-observation)

---

## 10. Post-Collection Reassessment Framework

After evidence collection (successful or failed), KUROKO performs:

1. **Evidence Integrity Validation**
   - Verify SHA-256 checksums
   - Verify file counts (modification count = 0)
   - Verify timestamps are monotonic

2. **Event Sequence Analysis**
   - Extract T0-T6 events from evidence
   - Construct process lineage (parent-child relationships)
   - Verify consistency across multiple evidence sources

3. **F-SC-002 Assessment**
   - Attempt to determine: T3 < T4?
   - If T3 and T4 both directly observed: PASS or FAIL on timing
   - If only partial observation: UNRESOLVED / EVIDENCE_GAP
   - If contradictory evidence: Flag for manual review

4. **Evidence Gap Documentation**
   - List each success criterion (A-H) and pass/fail status
   - Document why any criteria failed
   - Propose corrective actions (if any)

5. **Human Gate Decision Package**
   - F-SC-002 Status (RESOLVED/UNRESOLVED)
   - Evidence quality assessment
   - Remaining gaps
   - Recommendation for next steps

---

## 11. References

- Windows Event Tracing: https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
- Process Creation Audit: https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688
- PowerShell Get-Process: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process

---

END OF PROTOCOL

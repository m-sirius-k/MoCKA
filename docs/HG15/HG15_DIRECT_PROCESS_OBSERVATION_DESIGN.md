# HG-15 Direct Process Observation Design
## Minimum Evidence Requirements for F-SC-002 Temporal Proof

Date: 2026-09-05
Version: 2.0 (Re-architecture Post-Audit)
Scope: Design-only specification for direct T3 < T4 observation

---

## Executive Summary

The previous Collector design claimed ETW direct observation but implemented only 500ms sampling-based process monitoring. This design re-architects the approach to:

1. Explicitly distinguish WHAT CAN BE DIRECTLY OBSERVED from WHAT IS INFERRED
2. Define minimum evidence requirements for T3 < T4 proof that are ACTUALLY ACHIEVABLE
3. Identify which observation methods provide direct timestamps vs sampling-based approximations
4. Prevent false T3 < T4 claims from 500ms sampling windows that overlap
5. Handle existing process contamination without process termination

---

## Definition: DIRECT PROCESS OBSERVATION

A process event is "DIRECTLY OBSERVED" when:

```
Event occurs → Windows kernel generates event record → Observation system captures record with kernel timestamp → Evidence includes original kernel timestamp (not observer wall-clock time)
```

DIRECT OBSERVATION requires:
- Kernel-level event capture (ETW or Event Log with enabled audit)
- Millisecond precision timestamp from kernel
- Event ID or event type identification (creation vs exit)
- Process metadata (PID, name, command-line)
- Traceability: which observation method provided timestamp

---

## INFERRED Process Observation (NOT DIRECT)

An event is "INFERRED" when:

```
Process state changes between observations → Observer detects state difference → Observer assigns timestamp based on observation interval → Actual event time is UNKNOWN (only bounded by interval)
```

INFERRED OBSERVATION (sampling-based):
- Process list snapshot at T0: process X NOT PRESENT
- Process list snapshot at T0+500ms: process X PRESENT
- Inference: process X started somewhere in [T0, T0+500ms]
- Actual start time: UNKNOWN within window
- Temporal certainty: ±500ms

**CRITICAL DISTINCTION**: 500ms sampling cannot prove T3 < T4 if both events fall within a single 500ms window. Example:
```
Snapshot 0: 13:00:16.000Z - tech_watcher PRESENT, risk_scorer ABSENT
Snapshot 1: 13:00:16.500Z - tech_watcher ABSENT, risk_scorer PRESENT

Both T3 and T4 occurred in [16.000, 16.500Z]. Ordering is UNKNOWN.
```

---

## F-SC-002 Evidence Requirements: T3 < T4

### T3: tech_watcher.py Process Termination

**What needs to be observed:**
- Process with name matching tech_watcher (via command-line)
- Termination event (process exit, not just absence)
- Timestamp of termination (kernel-generated, not inferred)
- Exit code (optional, useful for confirming normal vs crash exit)

**Direct observation methods:**
1. ETW Process Tracing (Event Type: Process Terminated)
   - Kernel timestamp: ms precision
   - Includes: PID, process name, exit code, parent PID
   - Status: DIRECT OBSERVATION

2. Event Log (Event ID 4689: Process Terminated)
   - Kernel timestamp: 1-second precision
   - Includes: process ID, process name, exit code
   - Status: DIRECT OBSERVATION (if audit enabled)
   - Note: Requires "Audit Process Tracking" policy enabled

3. Process List Sampling (detect disappearance)
   - Observer timestamp: ms precision, but event time is unknown
   - Bounds event to: [last detection, next non-detection]
   - Status: INFERRED (not direct)

**Acceptable for F-SC-002 reassessment:** ETW or Event Log (direct), NOT sampling alone

---

### T4: risk_scorer.py Process Creation

**What needs to be observed:**
- Process with name matching risk_scorer (via command-line)
- Creation event (process start, not just presence)
- Timestamp of creation (kernel-generated, not inferred)
- Parent PID (to confirm launched from MoCKA-START.bat context)
- Command-line (to distinguish from any other python.exe processes)

**Direct observation methods:**
1. ETW Process Tracing (Event Type: Process Created)
   - Kernel timestamp: ms precision
   - Includes: PID, process name, command-line, parent PID
   - Status: DIRECT OBSERVATION

2. Event Log (Event ID 4688: Process Creation)
   - Kernel timestamp: 1-second precision
   - Includes: process ID, image filename, command-line, parent process ID
   - Status: DIRECT OBSERVATION (if audit enabled)
   - Note: Requires "Audit Process Creation" policy enabled

3. Process List Sampling (detect appearance)
   - Observer timestamp: ms precision, but event time is unknown
   - Bounds event to: [last non-detection, current detection]
   - Status: INFERRED (not direct)

**Acceptable for F-SC-002 reassessment:** ETW or Event Log (direct), NOT sampling alone

---

## Critical Requirement: Timestamp Source Separation

The previous design mixed three timestamp sources without labeling them:

1. **Observation Timestamp** (`observation_time`): When the observer took a snapshot or polled for events
   - Source: PowerShell Get-Date at moment of capture
   - Precision: 100ns (but system clock may have lower precision)
   - Meaning: When did we CHECK, not when did event occur

2. **Kernel Event Timestamp** (`event_time`): When Windows kernel recorded the event
   - Source: ETW event timestamp or Event Log timestamp
   - Precision: Varies (ms for ETW, 1s for Event Log)
   - Meaning: When did process actually start/exit

3. **Process.StartTime / Process.ExitTime** (PowerShell property): When process object recorded in snapshot
   - Source: PowerShell Get-Process property (delayed, sampled)
   - Precision: 1ms (but represents delayed observation)
   - Meaning: When did we first DETECT process was running, not when it started

**NEW DESIGN REQUIREMENT:**
Each timestamp in evidence MUST include SOURCE LABEL:
```json
{
  "timestamp": "2026-09-05T13:00:16.789Z",
  "timestamp_source": "ETW_EVENT_TIMESTAMP" | "EVENT_LOG_TIMESTAMP" | "OBSERVATION_TIMESTAMP" | "PROCESS_STARTTIME",
  "precision_ms": 1 | 1000,
  "meaning": "When kernel recorded process termination"
}
```

**REJECTED APPROACH**: Single ISO 8601 timestamp without source context (masks precision loss and causation)

---

## Path 1: ETW Direct Observation (HIGHEST CONFIDENCE)

### Capability
- Capture process creation and termination events at kernel level
- ms-precision timestamps
- Full command-line and parent PID available
- Requires: Windows Event Tracing session, admin rights, logman availability

### Implementation Requirement
```powershell
# MUST actually implement (not claim in manifest):

logman create trace HG15_Baseline -ow -rt -b 10mb -bs 1mb
logman update trace HG15_Baseline -p "Microsoft-Windows-Kernel-Process" 0xff -ets
logman start HG15_Baseline -ets

# Execute MoCKA-START.bat while trace is running

logman stop HG15_Baseline -ets
# Parse .etl file to extract events
```

### Timestamp Quality
- Event timestamp: kernel-generated, ms precision
- Separable from observation time
- Direct proof of T3 < T4 if both events captured

### Contamination Handling
- Pre-execution baseline: capture all running processes with command-line
- Execution phase: trace only events during observation window
- Post-execution: compare traced PIDs against baseline (exclude pre-existing)
- Result: new events only

### Feasibility: POSSIBLE (requires logman setup)

---

## Path 2: Event Log Direct Observation (MEDIUM CONFIDENCE)

### Capability
- Capture process creation (Event ID 4688) and termination (Event ID 4689) from Windows audit log
- 1-second precision timestamps (vs ms for ETW)
- Command-line and parent process ID available
- Requires: Audit Policy configured, Event Log running (usually on by default)

### Implementation Requirement
```powershell
# MUST actually implement (not just dump event log):

# Before execution:
Get-WinEvent -LogName Security -FilterXPath "EventID=4688 or EventID=4689" -MaxEvents 1000 | 
  Select-Object TimeCreated, ID, Properties | 
  Export-Csv baseline_events.csv

# After execution:
Get-WinEvent -LogName Security -FilterXPath "EventID=4688 or EventID=4689" -MaxEvents 1000 | 
  Select-Object TimeCreated, ID, Properties | 
  Export-Csv baseline_events_after.csv

# Difference: events that occurred during observation window
```

### Timestamp Quality
- Event timestamp: kernel-generated, 1-second precision
- Separable from observation time
- Sufficient to prove T3 < T4 if gap > 1 second

### Limitation
- Requires audit policy enabled (may not be by default)
- 1-second precision may miss sub-second process chains
- Event ID 4689 (termination) not guaranteed on all Windows versions

### Contamination Handling
- Pre-execution: capture event log tail timestamp
- Execution phase: collect new events only (after tail timestamp)
- Post-execution: filter events within observation window
- Result: new events only (time-bounded)

### Feasibility: LIKELY POSSIBLE (requires audit config check)

---

## Path 3: Process Monitor / Sampling (LOWEST CONFIDENCE)

### Capability
- 500ms interval process list snapshots
- Detect process appearance and disappearance
- Infer event within sampling window

### Timestamp Quality
- Observation timestamp: when snapshot taken (not event time)
- Event time: BOUNDED by [snapshot N, snapshot N+1]
- Resolution: ±500ms
- Cannot directly prove T3 < T4 if both events within same 500ms window

### Critical Flaw for F-SC-002
```
Snapshot at 16.000Z: tech_watcher RUNNING, risk_scorer NOT FOUND
Snapshot at 16.500Z: tech_watcher NOT FOUND, risk_scorer RUNNING
Inference: Both T3 and T4 occurred in [16.000, 16.500Z]
Temporal certainty: UNKNOWN — CANNOT PROVE T3 < T4
```

### Acceptable Uses (NOT for T3 < T4 ordering)
- Confirm process existence during execution window
- Detect anomalies (unexpected processes running)
- Rough timeline if gap between snapshots > 1000ms

### Feasibility: EASY (no special setup), but INSUFFICIENT for T3 < T4 proof

### Contamination Handling
- Pre-execution: baseline snapshot of all processes with command-line and start time
- Execution: continuous sampling
- Post-execution: compare new PIDs against baseline
- Result: distinguish new processes from pre-existing

---

## MANDATORY DECISION POINT

**To satisfy F-SC-002 reassessment, Collector MUST implement Path 1 OR Path 2:**

- **Path 1 (ETW)**: Full direct observation, ms precision, can prove T3 < T4 definitively if both events captured
- **Path 2 (Event Log)**: Direct observation, 1-second precision, sufficient if time gap > 1s
- **Path 3 (Sampling)**: Insufficient for temporal ordering proof; inferred bounds only

**If Path 1 not feasible** (ETW disabled, logman unavailable):
- Fall back to Path 2 (Event Log with audit policy check)
- If Path 2 also not available: evidence insufficient, F-SC-002 remains UNRESOLVED

**NOT ACCEPTABLE**: Rely on Path 3 sampling alone and claim direct T3 < T4 proof

---

## Evidence Integrity Boundaries

### ALLOWED (Non-invasive observation)
- Read-only ETW trace setup (logman create trace)
- Query Event Log (read-only access)
- Process list snapshots (Get-Process)
- Compute timestamps differences
- Write evidence files to output directory

### PROHIBITED (Would contaminate evidence)
- Terminate existing processes
- Restart Windows services
- Modify process environment
- Modify BAT file, Python files, configs
- Filter or suppress event log entries
- Alter process creation order

---

## Success Criteria Redefined (Post-Audit)

| Criterion | Previous Design | Revised Design |
|-----------|-----------------|-----------------|
| A: BAT Start | Detect cmd.exe | Direct ETW/Event Log observation OR sampling confirmation |
| B: tech_watcher Start | Detect python.exe in list | Direct ETW (4688) or Event Log event, NOT sampling alone |
| C: tech_watcher Exit | Infer from disappearance | Direct ETW (Process Terminated) or Event Log (4689), NOT sampling alone |
| D: risk_scorer Start | Detect python.exe in list | Direct ETW (4688) or Event Log event, NOT sampling alone |
| E: risk_scorer Exit | Infer from disappearance | Direct ETW or Event Log, NOT sampling alone |
| F: T3 < T4 | Compare sample timestamps (PROBLEMATIC) | Compare direct ETW/Event Log timestamps only; disallow sampling-based inference |
| G: PID Info | Captured | Captured + Parent PID (required for lineage) |
| H: Reproducible | Manifest + files | Manifest + files + timestamp source labels + contamination exclusion log |

---

## NEXT STEP: Implementation Path Selection

This design is COMPLETE when following questions are answered:

1. **ETW (Path 1) Availability**: Can logman create trace, and Microsoft-Windows-Kernel-Process provider be enabled, on target Windows system?
   - If YES: Implement Path 1 as primary method
   - If NO: Check Path 2

2. **Event Log (Path 2) Availability**: Is audit policy configured to capture Event ID 4688/4689?
   - If YES: Implement Path 2 as primary method
   - If NO: Event Log may be available but requires policy enabling (documented as precondition)

3. **Fallback to Sampling (Path 3)**: If both Path 1 and 2 unavailable, accept that T3 < T4 cannot be DIRECTLY PROVEN, only inferred with ±500ms uncertainty?
   - If YES: Document this as evidence gap; proceed with best-effort sampling
   - If NO: F-SC-002 baseline acquisition BLOCKED until direct observation method available

---

END OF DIRECT PROCESS OBSERVATION DESIGN

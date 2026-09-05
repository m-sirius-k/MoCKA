# HG-15 Process Event Source Comparison
## Comparative Analysis of Observation Methods Against 11 Evaluation Criteria

Date: 2026-09-05
Version: 1.0
Scope: Formal evaluation of ETW, Event Log, and sampling-based methods

---

## Executive Summary

Three observation methods are available on Windows for capturing T3 (tech_watcher exit) and T4 (risk_scorer start). This analysis evaluates each against 11 criteria to determine which can DIRECTLY PROVE T3 < T4 temporal ordering.

**Conclusion**: Only ETW and Event Log can provide DIRECT observations. Sampling-based monitoring can detect process presence but cannot prove termination events or resolve sub-second ordering ambiguities.

---

## Evaluation Criteria

1. **Direct T3 Observation** (Can detect process TERMINATION, not just absence)
2. **Direct T4 Observation** (Can detect process CREATION event, not just appearance)
3. **Timestamp Precision** (Milliseconds vs seconds vs sampling window bounds)
4. **Temporal Ordering Capability** (Can prove T3 < T4 without inference)
5. **Command-line Capture** (Can identify tech_watcher.py vs random python.exe)
6. **Parent PID Capture** (Can verify MoCKA context lineage)
7. **Setup Complexity** (Admin rights, policy configuration, logman availability)
8. **Reliability / Availability** (Works on all Windows 10/11 systems by default)
9. **Non-Invasiveness** (Read-only observation, no process modifications)
10. **Evidence Integrity** (Tamper-proof kernel source, not user-space inference)
11. **Fallback Behavior** (Alternative if method unavailable)

---

## Method 1: ETW (Event Tracing for Windows)

### Description
Kernel-level process tracing session that captures process creation and termination events with millisecond-level precision.

### How It Works
```powershell
# Create trace session
logman create trace HG15_Baseline -ow -rt

# Enable process events provider
logman update trace HG15_Baseline -p "Microsoft-Windows-Kernel-Process" 0xff -ets

# Start trace
logman start HG15_Baseline -ets

# ... Execute MoCKA-START.bat ...

# Stop trace
logman stop HG15_Baseline -ets

# Parse .etl file to extract process events
```

### Evaluation Results

| Criterion | Rating | Details |
|-----------|--------|---------|
| Direct T3 Observation | YES | Kernel "Process Terminated" event captured with PID, exit code, exit timestamp |
| Direct T4 Observation | YES | Kernel "Process Created" event captured with PID, command-line, parent PID, creation timestamp |
| Timestamp Precision | 1 MILLISECOND | Kernel-generated timestamp with 1ms resolution; no sampling uncertainty |
| Temporal Ordering | DEFINITIVE | T3 and T4 timestamps compared directly; T3 < T4 provable with certainty |
| Command-line Capture | FULL | Complete command-line available in event; no truncation; identifies tech_watcher.py / risk_scorer.py unambiguously |
| Parent PID Capture | INCLUDED | Process creation event includes parent PID; can verify cmd.exe context |
| Setup Complexity | MODERATE | Requires: admin privileges, logman command availability, possibly Windows Feature enable |
| Reliability | VARIES | Microsoft-Windows-Kernel-Process provider not enabled by default on all Windows versions; may require configuration |
| Non-Invasiveness | YES | Read-only tracing; no process modification; temporary session (auto-cleanup) |
| Evidence Integrity | HIGHEST | Kernel-level events; cryptographically immutable; cannot be spoofed from user-space |
| Fallback Behavior | CONDITIONAL | If logman unavailable or provider disabled, trace session fails; must fall back to Event Log or sampling |

### VERDICT: DIRECT OBSERVATION (YES)

**Capability for F-SC-002**: Can DIRECTLY PROVE T3 < T4 if both events captured and trace file parsed successfully

**Risk**: Setup failures (logman not available, provider disabled) would cause collection abort; fallback required

---

## Method 2: Event Log (Windows Event ID 4688 / 4689)

### Description
Windows Security event log captures process creation (Event ID 4688) and process termination (4689) with 1-second precision, audit-log level events.

### How It Works
```powershell
# Check audit policy
Get-WinEvent -LogName Security -MaxEvents 1 | Select-Object TimeCreated

# Query events during observation window
Get-WinEvent -LogName Security -FilterXPath "
  (EventID=4688 or EventID=4689) 
  and TimeCreated>='2026-09-05T13:00:00.000Z' 
  and TimeCreated<='2026-09-05T13:00:25.000Z'
" | Select-Object TimeCreated, ID, Properties

# Parse Properties to extract PID, process name, command-line, parent PID
```

### Evaluation Results

| Criterion | Rating | Details |
|-----------|--------|---------|
| Direct T3 Observation | YES | Event ID 4689 (Process Terminated) captured with PID and exit timestamp; if enabled |
| Direct T4 Observation | YES | Event ID 4688 (Process Created) captured with PID, command-line, parent PID, creation timestamp |
| Timestamp Precision | 1 SECOND | Kernel timestamp recorded at 1-second granularity; sub-second ordering ambiguous if events in same second |
| Temporal Ordering | MOSTLY | T3 < T4 provable if time gap ≥ 1 second; ambiguous if same-second timestamps |
| Command-line Capture | FULL | Event 4688 includes full command-line; sufficient to identify tech_watcher.py / risk_scorer.py |
| Parent PID Capture | INCLUDED | Event 4688 includes parent process ID; can verify cmd.exe context |
| Setup Complexity | LOW | Event Log service running by default; query via Get-WinEvent (no special setup) |
| Reliability | CONDITIONAL | Event ID 4688/4689 requires "Audit Process Creation" policy enabled (not default on all systems) |
| Non-Invasiveness | YES | Read-only query; no modifications; Event Log is persistent system service |
| Evidence Integrity | HIGH | Kernel-level audit events; tamper-resistant; signed by Windows audit subsystem |
| Fallback Behavior | GOOD | If 4689 (termination) unavailable, can still rely on 4688 (creation) alone; graceful degradation |

### VERDICT: DIRECT OBSERVATION (YES, with caveats)

**Capability for F-SC-002**: Can DIRECTLY PROVE T3 < T4 if time gap > 1 second OR if millisecond timestamps available from other events

**Risk**: Event ID 4689 may not be available; policy configuration required; 1-second granularity may be insufficient if T3 and T4 close in time

---

## Method 3: Process Monitor (Sampling-Based Process List Snapshots)

### Description
Polling-based approach: query Get-Process every 500ms, detect process appearance/disappearance, infer event timing from interval.

### How It Works
```powershell
# Snapshot before: Get-Process, look for tech_watcher, risk_scorer
# Snapshots during: Get-Process every 500ms
# Snapshot after: Get-Process, look for remaining processes

# Detection logic:
# - If process in snapshot N but not in snapshot N-1 → inferred CREATION in [N-1, N]
# - If process in snapshot N-1 but not in snapshot N → inferred TERMINATION in [N-1, N]
```

### Evaluation Results

| Criterion | Rating | Details |
|-----------|--------|---------|
| Direct T3 Observation | NO | Detects ABSENCE of process, not termination event; timing unknown within 500ms window |
| Direct T4 Observation | NO | Detects PRESENCE of process, not creation event; timing unknown within 500ms window |
| Timestamp Precision | ±500ms | Event time bounded by [snapshot_N-1, snapshot_N]; actual time unknown; unacceptable for sub-500ms ordering |
| Temporal Ordering | INSUFFICIENT | If T3 and T4 occur within same 500ms window, order UNKNOWN; sampling-based inference insufficient |
| Command-line Capture | YES | Get-Process includes command-line; can identify tech_watcher.py / risk_scorer.py |
| Parent PID Capture | YES | Get-Process includes parent PID; can verify lineage |
| Setup Complexity | MINIMAL | Get-Process built-in; no special configuration needed |
| Reliability | EXCELLENT | Works on all Windows systems, no dependencies, no special permissions |
| Non-Invasiveness | YES | Read-only snapshots; no process modification |
| Evidence Integrity | MEDIUM | User-space polling; subject to system load delays, snapshot jitter, missed processes if exit occurs between snapshots |
| Fallback Behavior | GOOD | If all direct methods fail, sampling provides best-effort process timeline (with caveats) |

### CRITICAL LIMITATION for F-SC-002

```
Example Sampling Scenario:
Snapshot 0 (16.000Z): tech_watcher RUNNING, risk_scorer NOT FOUND
Snapshot 1 (16.500Z): tech_watcher NOT FOUND, risk_scorer RUNNING

Inference:
  T3 (tech_watcher exit) occurred in window [16.000Z, 16.500Z]
  T4 (risk_scorer start) occurred in window [16.000Z, 16.500Z]
  
  Both events bounded to same 500ms window.
  Ordering T3 < T4 CANNOT BE PROVEN.
  Possible scenarios:
    - T3 at 16.123Z, T4 at 16.234Z (T3 < T4) (YES)
    - T3 at 16.234Z, T4 at 16.123Z (T3 > T4) (NO)
    - T3 at 16.250Z, T4 at 16.250Z (simultaneous) (?)

Result: UNRESOLVED, not CONFIRMED
```

### VERDICT: INFERENCE ONLY, NOT DIRECT OBSERVATION (NO)

**Capability for F-SC-002**: CANNOT definitively prove T3 < T4 if both events within same 500ms window; only acceptable as backup if gap between snapshots > 1000ms

**Risk**: Temporal ordering ambiguity; false positives if processes exit and restart rapidly; insufficient precision for scientific rigor

---

## Comparative Summary Table

| Criterion | ETW | Event Log | Sampling |
|-----------|-----|-----------|----------|
| T3 Direct Observation | YES | YES | NO |
| T4 Direct Observation | YES | YES | NO |
| Precision | 1ms | 1s | ±500ms |
| T3 < T4 Proof | DEFINITIVE | IF GAP>1s | INSUFFICIENT |
| Setup Complexity | MODERATE | LOW | MINIMAL |
| Reliability | VARIES | CONDITIONAL | EXCELLENT |
| Non-Invasive | YES | YES | YES |
| Evidence Integrity | HIGHEST | HIGH | MEDIUM |
| Fallback Available | Event Log | Sampling | NONE |
| F-SC-002 Acceptable | YES | MAYBE | NO |

---

## Recommendation for Collector Implementation

### PRIMARY APPROACH: ETW (Preferred)
- Implement logman trace session setup
- Capture "Microsoft-Windows-Kernel-Process" provider events
- Parse .etl output to extract process creation and termination events
- Outcome: DIRECT observation with 1ms precision; definitive T3 < T4 proof

### FALLBACK #1: Event Log (Acceptable Alternative)
- If ETW logman unavailable or permissions denied
- Query Security event log for Event ID 4688 (creation) and 4689 (termination)
- Check "Audit Process Creation" policy is enabled
- Outcome: DIRECT observation with 1s precision; T3 < T4 provable if gap > 1s

### FALLBACK #2: Sampling (Best-Effort, Documentation Required)
- If both ETW and Event Log unavailable
- Use Get-Process snapshots every 500ms
- Clearly document that T3 < T4 is INFERRED, not DIRECTLY OBSERVED
- Add evidence gap notice: "Temporal ordering within sampling window is ambiguous"
- Outcome: Process activity detected, but F-SC-002 remains UNRESOLVED

### REJECTION: Do NOT claim "F-SC-002 CONFIRMED" based on sampling alone

---

## Implementation Validation Checklist

Before accepting Collector output as evidence:

- [ ] Collector attempted ETW trace setup (logman create trace...)
- [ ] If ETW succeeded: Parse .etl file for Process Terminated and Process Created events
- [ ] If ETW failed: Check fallback to Event Log was attempted
- [ ] If Event Log used: Verify Event ID 4688/4689 events present in output
- [ ] If both failed: Confirm sampling snapshots used and documented as "INFERRED, NOT DIRECT"
- [ ] T3 timestamp source clearly labeled (ETW_TERMINATED / EVENT_LOG_4689 / INFERRED_SAMPLING)
- [ ] T4 timestamp source clearly labeled (ETW_CREATED / EVENT_LOG_4688 / INFERRED_SAMPLING)
- [ ] Confidence levels match source (ETW/Event Log = HIGH, Sampling = LOW for ordering)
- [ ] Evidence gap documented if only sampling available
- [ ] F-SC-002 status reflects method used: "CONFIRMED" only if ETW/Event Log; "UNRESOLVED" if sampling

---

END OF PROCESS EVENT SOURCE COMPARISON

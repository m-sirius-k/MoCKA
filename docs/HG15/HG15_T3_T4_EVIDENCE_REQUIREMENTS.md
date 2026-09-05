# HG-15 T3 and T4 Evidence Requirements Specification
## Explicit Definition of Direct Observation and Temporal Proof

Date: 2026-09-05
Version: 1.0
Scope: Minimum evidence requirements to satisfy F-SC-002 reassessment

---

## F-SC-002 Claim Statement

**ORIGINAL CLAIM**: "tech_watcher.py exits before risk_scorer.py starts"

**TEMPORAL EXPRESSION**: T3 < T4

Where:
- T3 = tech_watcher.py process termination timestamp
- T4 = risk_scorer.py process creation timestamp

**REASSESSMENT GOAL**: Determine whether T3 < T4 is CONFIRMED, NOT_CONFIRMED, or UNRESOLVED based on baseline execution evidence

---

## Part 1: T3 Evidence Requirements

### Event: tech_watcher.py Process Termination

### Definition
tech_watcher.py Python process exits (terminates), either normally or abnormally, and process handle becomes invalid.

### Evidence Requirement: T3 Timestamp

To satisfy "DIRECT OBSERVATION of T3", evidence MUST include:

1. **Process Identification**
   - Process ID (PID)
   - Process name or executable path
   - Command-line (MUST include "tech_watcher.py" or equivalent identifier)
   - Parent PID (optional but preferred for lineage verification)
   - User context (process ran under what user account)

2. **Termination Event Confirmation**
   - Event type = PROCESS_TERMINATED or equivalent
   - Source = ETW kernel event OR Event Log event id 4689
   - NOT: inferred from process list comparison (sampling-based)
   - NOT: guessed from stdout "process ending" message

3. **Timestamp T3**
   - Value: ISO 8601 format (e.g., "2026-09-05T13:00:16.789Z")
   - Precision: Milliseconds for ETW, 1-second for Event Log
   - Source LABEL: "ETW_PROCESS_TERMINATED" or "EVENT_LOG_4689"
   - Confidence: HIGH (kernel-level event)

4. **Exit Code (Highly Desired)**
   - Numeric value (0 = success, non-zero = failure or user-requested exit)
   - Confirms normal termination vs crash

5. **Duration Information (Optional but Useful)**
   - Start time T2 (when tech_watcher.py created)
   - Exit time T3 (when tech_watcher.py terminated)
   - Duration = T3 - T2 (runtime of tech_watcher)
   - Confirms process ran for expected duration

### Example Evidence Record (Acceptable)

```json
{
  "event_id": "EVT_20260905_130016_003",
  "event_type": "PROCESS_TERMINATED",
  "timestamp_t3": "2026-09-05T13:00:16.789Z",
  "timestamp_source": "ETW_PROCESS_TERMINATED",
  "timestamp_precision_ms": 1,
  "process": {
    "pid": 3421,
    "name": "python.exe",
    "executable": "C:\\Python39\\python.exe",
    "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py --config config.ini",
    "parent_pid": 2401,
    "user": "sirok"
  },
  "exit_code": 0,
  "duration_ms": 3544,
  "confidence": "HIGH",
  "observation_method": "ETW"
}
```

### Rejection Criteria (UNACCEPTABLE EVIDENCE)

- NOT: "Process disappeared from Get-Process output at 13:00:16.500Z" (sampling, not direct)
- NOT: "Assuming tech_watcher.py exited based on risk_scorer.py appearing" (circular reasoning)
- NOT: "Event Log shows no events for tech_watcher between 13:00:15 and 13:00:18" (absence of evidence)
- NOT: "Inferred from manifest.success_criteria A-E" (manifest cannot BE the evidence)

### Expected Evidence Files Contributing to T3
- ETW trace .etl file (raw kernel events)
- Event Log Security log extract (Event ID 4688, 4689)
- Process timeline CSV (with ETW/Event Log timestamps, NOT sampling timestamps)
- Process event manifest (structured JSON with T3 timestamp and source)

---

## Part 2: T4 Evidence Requirements

### Event: risk_scorer.py Process Creation

### Definition
risk_scorer.py Python process is spawned (created) as child of MoCKA-START.bat context and begins execution.

### Evidence Requirement: T4 Timestamp

To satisfy "DIRECT OBSERVATION of T4", evidence MUST include:

1. **Process Identification**
   - Process ID (PID) — will be DIFFERENT from T3 process (new process)
   - Process name or executable path
   - Command-line (MUST include "risk_scorer.py" or equivalent identifier)
   - Parent PID (MUST be cmd.exe or batch process context)
   - User context (process ran under what user account)

2. **Creation Event Confirmation**
   - Event type = PROCESS_CREATED or equivalent
   - Source = ETW kernel event OR Event Log event id 4688
   - NOT: inferred from process list comparison
   - NOT: guessed from log message "starting risk scorer"

3. **Timestamp T4**
   - Value: ISO 8601 format (e.g., "2026-09-05T13:00:17.123Z")
   - Precision: Milliseconds for ETW, 1-second for Event Log
   - Source LABEL: "ETW_PROCESS_CREATED" or "EVENT_LOG_4688"
   - Confidence: HIGH (kernel-level event)

4. **Parent Process Verification (REQUIRED for F-SC-002)**
   - Parent PID should match cmd.exe (MoCKA-START.bat context)
   - OR: Parent process name verification
   - Confirms risk_scorer spawned from batch context, not random python.exe

5. **Command-line Verification (REQUIRED)**
   - Full command-line captured (not truncated)
   - Contains "risk_scorer.py" or script path
   - No ambiguity with other python processes

### Example Evidence Record (Acceptable)

```json
{
  "event_id": "EVT_20260905_130017_004",
  "event_type": "PROCESS_CREATED",
  "timestamp_t4": "2026-09-05T13:00:17.123Z",
  "timestamp_source": "ETW_PROCESS_CREATED",
  "timestamp_precision_ms": 1,
  "process": {
    "pid": 3512,
    "name": "python.exe",
    "executable": "C:\\Python39\\python.exe",
    "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\risk_scorer.py --config config.ini",
    "parent_pid": 2401,
    "parent_name": "cmd.exe",
    "user": "sirok"
  },
  "confidence": "HIGH",
  "observation_method": "ETW"
}
```

### Rejection Criteria (UNACCEPTABLE EVIDENCE)

- NOT: "Process appeared in Get-Process output at 13:00:17.500Z" (sampling, not direct)
- NOT: "Assuming risk_scorer.py started after tech_watcher.py ended" (assumes outcome)
- NOT: "Process list at 13:00:17 shows python.exe with unknown parent" (no parent PID, ambiguous)
- NOT: "risk_scorer started sometime after 13:00:16" (no precise timestamp)

### Expected Evidence Files Contributing to T4
- ETW trace .etl file (raw kernel events)
- Event Log Security log extract (Event ID 4688)
- Process timeline CSV (with ETW/Event Log timestamps)
- Process event manifest (structured JSON with T4 timestamp and source)

---

## Part 3: T3 < T4 Comparison Requirement

### Temporal Ordering Claim

**CLAIM**: T3 < T4 (tech_watcher exit BEFORE risk_scorer start)

### Mathematical Definition

```
IF (timestamp_t3 < timestamp_t4)
  AND (timestamp_source_t3 = "ETW_PROCESS_TERMINATED" OR "EVENT_LOG_4689")
  AND (timestamp_source_t4 = "ETW_PROCESS_CREATED" OR "EVENT_LOG_4688")
THEN
  Claim is CONFIRMED with HIGH confidence
ELSE IF (timestamp_t3 >= timestamp_t4)
THEN
  Claim is NOT_CONFIRMED (violated: risk_scorer started before tech_watcher exited)
ELSE IF (timestamp_source missing OR sampling-based)
THEN
  Claim is UNRESOLVED (insufficient precision or inference)
```

### Precision Requirements

For T3 < T4 comparison to be meaningful:

- **ETW to ETW**: Millisecond-level comparison
  - Time gap threshold: Any gap > 0 ms proves order
  - Example: T3 = 16.789Z, T4 = 17.123Z, gap = 334 ms → CONFIRMED

- **Event Log to Event Log**: Second-level comparison
  - Time gap threshold: Gap must be > 1 second to prove order
  - Example: T3 = 16Z, T4 = 17Z, gap = 1s → CONFIRMED
  - Ambiguous: T3 = 16Z, T4 = 16Z (same second) → UNRESOLVED

- **Mixed ETW + Event Log**: Use millisecond precision from ETW
  - Precedence: Rely on ms-precision timestamp for order

### Rejection Criteria (NOT ACCEPTABLE)

- NOT: "T3 inferred as 16.000-16.500Z window, T4 inferred as 16.500-17.000Z window" (sampling-based with uncertainty)
- NOT: "tech_watcher.py had runtime of 3.5s, so must have exited before risk_scorer" (circular reasoning)
- NOT: "Process monitor shows risk_scorer at T4=16.789Z but that's when it was DETECTED" (detection ≠ creation)
- NOT: "Manifest shows success_criteria[F] = CONFIRMED" (manifest is not evidence)

### Expected Comparison Output

```json
{
  "f_sc_002_temporal_claim": {
    "claim": "tech_watcher (T3) exits BEFORE risk_scorer (T4) starts",
    "temporal_expression": "T3 < T4",
    "t3_timestamp": "2026-09-05T13:00:16.789Z",
    "t3_timestamp_source": "ETW_PROCESS_TERMINATED",
    "t4_timestamp": "2026-09-05T13:00:17.123Z",
    "t4_timestamp_source": "ETW_PROCESS_CREATED",
    "time_gap_ms": 334,
    "timestamp_precision_ms": 1,
    "calculation": "T4_unix_ms - T3_unix_ms = 1725543617123 - 1725543616789 = 334",
    "result": "T3 < T4 = TRUE",
    "verdict": "CONFIRMED",
    "confidence": "HIGH",
    "reasoning": "Both events directly observed via ETW with 1ms precision. T3 occurred 334ms before T4. Order is definitive."
  }
}
```

---

## Part 4: Contamination Control Requirements

### Problem: Existing Process Confusion

**Scenario**: Windows PC has existing tech_watcher.py or risk_scorer.py running from prior execution.

**Confusion**: Baseline Collector cannot distinguish:
- T2 = NEW tech_watcher process created during this observation window
- vs. T2 = PRE-EXISTING tech_watcher process from 30 minutes ago

**Impact on T3 < T4**:
- If T3 timestamp is from PRE-EXISTING process exit (not this baseline run), comparison is meaningless
- Evidence must account for which process instances are NEW vs PRE-EXISTING

### Evidence Requirements for Contamination Control

1. **Pre-Execution Baseline Snapshot**
   - Timestamp: T0 (observation start time)
   - Capture: All running processes with PID, name, command-line, creation time
   - Focus: Identify any tech_watcher.py or risk_scorer.py already running
   - Format: CSV with columns [PID, ProcessName, CommandLine, StartTime]

2. **Lineage Tracking During Execution**
   - Requirement: Link each process event to MoCKA-START.bat execution context
   - Method: Parent PID matching (T4 risk_scorer parent should be cmd.exe running MoCKA-START.bat)
   - Evidence: Parent process details in T4 event record

3. **Post-Execution Verification**
   - Capture: All process events during window (ETW log or Event Log query)
   - Filter: Include only events AFTER observation start (T0)
   - Exclude: Any process with creation time BEFORE T0 (pre-existing)
   - Result: T3 and T4 are NEW processes spawned during this baseline window

### Example: Contamination Detection

```
Pre-execution baseline (T0 = 13:00:00Z):
  PID 1234: python.exe "tech_watcher.py" (StartTime: 2026-09-05T12:58:00Z) [PRE-EXISTING, ignore]
  PID 1235: python.exe "some_other_script.py" (StartTime: 2026-09-05T12:45:00Z) [PRE-EXISTING, ignore]

During execution:
  T1: cmd.exe MoCKA-START.bat spawned (PID 2401)
  T2: python.exe tech_watcher.py spawned (PID 3421, parent=2401) [NEW, matches MoCKA context]
  T3: python.exe (PID 3421) exits [BELONGS TO THIS BASELINE, valid T3]
  T4: python.exe risk_scorer.py spawned (PID 3512, parent=2401) [NEW, matches MoCKA context]
  T5: python.exe (PID 3512) exits [BELONGS TO THIS BASELINE, valid T5]
  T6: cmd.exe (PID 2401) exits

Filtering:
  Keep T2, T3, T4, T5 (created during observation window [T0, T6])
  Ignore PID 1234 tech_watcher.py (created before observation window)

Result: T3 and T4 are confirmed NEW processes, comparison is valid
```

### Evidence Fields for Contamination Control

Each T3/T4 event record MUST include:

```json
{
  "timestamp": "2026-09-05T13:00:16.789Z",
  "process_creation_time": "2026-09-05T13:00:13.245Z",
  "observation_window_start": "2026-09-05T13:00:00.000Z",
  "observation_window_end": "2026-09-05T13:00:25.000Z",
  "is_new_process": true,
  "is_within_observation_window": true,
  "parent_pid": 2401,
  "parent_name": "cmd.exe",
  "parent_command_line": "cmd.exe /c C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
  "parent_creation_time": "2026-09-05T13:00:12.001Z",
  "contamination_status": "NEW_PROCESS_IN_MOCKA_CONTEXT",
  "notes": "Process created during observation window, parent is MoCKA-START.bat context"
}
```

---

## Part 5: Evidence Rejection Criteria Summary

### UNACCEPTABLE Evidence for F-SC-002 Reassessment

| Evidence Type | Why Rejected | Alternative |
|---------------|------------|-------------|
| "tech_watcher disappeared from process list at 16.500Z" | Inferred from sampling, not direct observation | Use ETW (4688 termination) or Event Log (4689) |
| "time gap between snapshots suggests order" | Inferred bounds, not direct timestamps | Use direct ETW/Event Log timestamps |
| "tech_watcher ran for 3.5s, so must have exited before risk_scorer" | Circular reasoning from expected behavior | Directly observe both T3 and T4 |
| "Event Log shows process 3421 no longer running at 13:00:18" | Absence of evidence, not evidence of absence | Capture Event ID 4689 (process terminated) event |
| "risk_scorer appeared to start after tech_watcher" | Observation-time mixing with event-time | Separate timestamp sources in evidence |
| "Manifest shows success_criteria[F] = CONFIRMED" | Document is not evidence | Provide raw ETW/Event Log data supporting F |

### ACCEPTABLE Evidence for F-SC-002 Reassessment

| Evidence Type | Reason Acceptable | Quality Level |
|---------------|------------|-----------|
| ETW event: Process Terminated (tech_watcher, PID 3421, 16.789Z) | Direct kernel observation, ms precision | HIGHEST |
| ETW event: Process Created (risk_scorer, PID 3512, 17.123Z) | Direct kernel observation, ms precision | HIGHEST |
| Event Log 4689: Process Terminated (tech_watcher, 16Z) | Direct kernel observation, 1s precision | HIGH |
| Event Log 4688: Process Created (risk_scorer, 17Z) | Direct kernel observation, 1s precision | HIGH |
| Comparison: T3 (16.789Z) < T4 (17.123Z), gap 334ms | Timestamp sources both direct, math is clear | CONFIRMED |

---

## ACCEPTANCE GATE: Evidence Quality Checklist

Before KUROKO accepts evidence as satisfying F-SC-002 reassessment, verify:

- [ ] T3 Timestamp: Direct observation (ETW or Event Log, not sampling)
- [ ] T3 Source: Labeled as "ETW_PROCESS_TERMINATED" or "EVENT_LOG_4689"
- [ ] T3 Confidence: HIGH (kernel-level event)
- [ ] T4 Timestamp: Direct observation (ETW or Event Log, not sampling)
- [ ] T4 Source: Labeled as "ETW_PROCESS_CREATED" or "EVENT_LOG_4688"
- [ ] T4 Confidence: HIGH (kernel-level event)
- [ ] Parent PID: T4 event includes parent PID (confirms MoCKA context)
- [ ] Command-line: Both events include full command-lines (tech_watcher.py, risk_scorer.py)
- [ ] Contamination Control: Evidence filters PRE-EXISTING processes, includes NEW processes only
- [ ] Timestamp Separation: T3/T4 sources clearly labeled (not mixed with observation timestamps)
- [ ] Time Gap: T3 < T4 with gap > 0 (or > 1s if Event Log timestamps tied to same second)
- [ ] Calculation: T4_timestamp - T3_timestamp = time_gap_ms explicitly shown

**If ANY checkbox is unchecked**: Evidence is INSUFFICIENT for reassessment

---

END OF T3/T4 EVIDENCE REQUIREMENTS

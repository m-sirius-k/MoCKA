# HG-15 Existing Process Contamination Control
## Design for Preventing Pre-Existing Process Confusion with New Baseline

Date: 2026-09-05
Version: 1.0
Scope: Contamination exclusion methodology

---

## Problem Statement

**Scenario**: Windows PC may have MoCKA processes running from prior execution:
- tech_watcher.py (PID 1234) started at 12:58:00Z (30 minutes ago)
- risk_scorer.py (PID 1235) started at 13:10:00Z (idle, not terminated)

**Challenge**: New baseline collection must NOT confuse these pre-existing processes with newly-spawned processes during observation window.

**Evidence Impact**: If T3 timestamp comes from pre-existing process termination (not this baseline), F-SC-002 reassessment is invalidated.

**Governance Impact**: Collector must DETECT (not prevent) existing processes, report status, and decide whether to proceed or abort.

---

## Contamination Detection Strategy

### Phase 0: Pre-Execution Snapshot (T0 - 5 seconds before BAT execution)

**Objective**: Establish baseline of ALL running processes at observation window start

**Data Captured**:
```json
{
  "snapshot_timestamp": "2026-09-05T13:00:00.000Z",
  "snapshot_phase": "PRE_EXECUTION_BASELINE",
  "processes": [
    {
      "pid": 1234,
      "name": "python.exe",
      "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py ...",
      "creation_time": "2026-09-05T12:58:00.000Z",
      "status": "PRE_EXISTING",
      "age_seconds": 120,
      "will_be_excluded": true
    },
    {
      "pid": 1235,
      "name": "python.exe",
      "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\risk_scorer.py ...",
      "creation_time": "2026-09-05T12:45:00.000Z",
      "status": "PRE_EXISTING",
      "age_seconds": 900,
      "will_be_excluded": true
    }
  ]
}
```

**Decision Point**: If pre-existing tech_watcher or risk_scorer found:
- Option A: ABORT collection (expected behavior when double-execution protection triggers)
- Option B: PROCEED with contamination filtering (if user confirms processes are not interfering)

**Collector Behavior** (per original design, should remain unchanged):
```
IF (existing MoCKA processes detected)
  REPORT: "EXISTING_PROCESS_CONFLICT"
  ACTION: ABORT (do not attempt execution)
  REASON: MoCKA-START.bat has double-execution protection; will exit with code 1
ELSE
  PROCEED to Phase 1 (execution)
```

### Phase 1-3: Observation Window (T0 to T6)

**Objective**: Collect all process events during execution

**ETW Events Captured**:
```
[T0] Observation start: 13:00:00.000Z
[T1] cmd.exe spawn (MoCKA-START.bat) -> PID 2401
[T2] python.exe spawn (tech_watcher.py) -> PID 3421 (parent PID 2401)
[T3] python.exe (PID 3421) exit -> exit code 0
[T4] python.exe spawn (risk_scorer.py) -> PID 3512 (parent PID 2401)
[T5] python.exe (PID 3512) exit -> exit code 0
[T6] cmd.exe (PID 2401) exit -> exit code 0
[T6+1s] Observation end: 13:00:21.000Z
```

**CRITICAL**: Filter by timestamps DURING window [T0, T6+1s], not just process names.

### Phase 4-6: Post-Execution Filtering (T6+1s to T6+60s)

**Objective**: Remove pre-existing processes from evidence; retain NEW processes only

**Filter Algorithm**:

```python
def is_new_process(event, pre_exec_snapshot, observation_window_start):
    """
    Determine if a process event belongs to NEW process (not pre-existing)
    
    Args:
        event: Process event (creation or termination)
        pre_exec_snapshot: List of processes running at T0
        observation_window_start: T0 timestamp
    
    Returns:
        True if process created during observation window (new)
        False if process existed before observation window (pre-existing)
    """
    
    # Extract PIDs of pre-existing processes
    preexisting_pids = set(p['pid'] for p in pre_exec_snapshot['processes'])
    
    # Check 1: PID in pre-existing list?
    if event['pid'] in preexisting_pids:
        return False  # PRE-EXISTING process
    
    # Check 2: Process creation time before observation window?
    if event.get('process_creation_time') < observation_window_start:
        return False  # PRE-EXISTING process
    
    # Check 3: Parent PID matches MoCKA context?
    if event.get('parent_pid') == batch_process_pid:  # cmd.exe running MoCKA-START.bat
        return True  # NEW process in MoCKA context
    
    # Otherwise: inconclusive
    return None  # UNKNOWN
```

**Filter Results**:

```json
{
  "filter_phase": "CONTAMINATION_EXCLUSION",
  "observation_window": {
    "start": "2026-09-05T13:00:00.000Z",
    "end": "2026-09-05T13:00:21.000Z"
  },
  "pre_existing_processes": [
    {
      "pid": 1234,
      "name": "python.exe",
      "command_line": "...tech_watcher.py...",
      "creation_time": "2026-09-05T12:58:00.000Z",
      "status": "EXCLUDED (created before observation window)"
    }
  ],
  "new_processes": [
    {
      "pid": 2401,
      "event_type": "PROCESS_CREATED",
      "timestamp": "2026-09-05T13:00:12.001Z",
      "command_line": "cmd.exe /c C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
      "status": "INCLUDED (created during observation window)"
    },
    {
      "pid": 3421,
      "event_type": "PROCESS_CREATED",
      "timestamp": "2026-09-05T13:00:13.245Z",
      "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py",
      "parent_pid": 2401,
      "status": "INCLUDED (created during observation window, parent is MoCKA context)"
    },
    {
      "pid": 3421,
      "event_type": "PROCESS_TERMINATED",
      "timestamp": "2026-09-05T13:00:16.789Z",
      "status": "INCLUDED (matches NEW process PID 3421)"
    },
    {
      "pid": 3512,
      "event_type": "PROCESS_CREATED",
      "timestamp": "2026-09-05T13:00:17.123Z",
      "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\risk_scorer.py",
      "parent_pid": 2401,
      "status": "INCLUDED (created during observation window, parent is MoCKA context)"
    }
  ],
  "excluded_events_count": 0,
  "included_events_count": 6,
  "evidence_valid": true
}
```

---

## Contamination Control Implementation Details

### Step 1: Command-line Normalization

**Problem**: Process names may be shortened or truncated in different observation contexts.

**Solution**: Extract script name from command-line with flexibility:

```python
def extract_script_name(command_line):
    """Extract tech_watcher or risk_scorer from command-line"""
    
    # Normalize: remove quotes, extract filename
    parts = command_line.split()
    for part in parts:
        if 'tech_watcher' in part.lower():
            return 'tech_watcher'
        if 'risk_scorer' in part.lower():
            return 'risk_scorer'
    
    return None  # Not a known MoCKA script
```

### Step 2: Parent Process Lineage Verification

**Requirement**: Each process must verify its parent is cmd.exe (or ultimately MoCKA-START.bat context)

**Implementation**:

```json
{
  "event": {
    "process_name": "python.exe",
    "process_pid": 3421,
    "process_command_line": "python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py",
    "parent_pid": 2401,
    "parent_name": "cmd.exe",
    "parent_command_line": "cmd.exe /c C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
    "grandparent_pid": 1200,
    "lineage_verified": true,
    "lineage_path": "grandparent(1200) -> parent_cmd(2401) -> child_python(3421)",
    "mocka_context_confirmed": true,
    "notes": "Parent is cmd.exe running MoCKA-START.bat; child is python.exe with tech_watcher.py. Lineage established."
  }
}
```

**Verification Logic**:
- Parent PID in process creation event MUST match cmd.exe PID
- cmd.exe command-line MUST include "MoCKA-START.bat"
- Result: Confirms process was spawned by MoCKA, not pre-existing

### Step 3: Timeline Validity Check

**Requirement**: Process creation time must fall within observation window

**Implementation**:

```json
{
  "timeline_validity": {
    "observation_window_start": "2026-09-05T13:00:00.000Z",
    "observation_window_end": "2026-09-05T13:00:25.000Z",
    "events": [
      {
        "event_id": "EVT_2",
        "event_type": "PROCESS_CREATED",
        "timestamp": "2026-09-05T13:00:13.245Z",
        "pid": 3421,
        "is_within_window": true,
        "calculation": "13:00:13.245Z is between [13:00:00, 13:00:25] (YES)"
      },
      {
        "event_id": "EVT_PRE",
        "event_type": "PROCESS_ALREADY_RUNNING",
        "timestamp": "2026-09-05T12:58:00.000Z",
        "pid": 1234,
        "is_within_window": false,
        "calculation": "12:58:00.000Z is BEFORE 13:00:00 (NO)"
      }
    ]
  }
}
```

---

## Contamination Scenarios and Handling

### Scenario A: No Pre-Existing Processes (Ideal Case)

**Pre-execution snapshot shows**:
- No python.exe processes with tech_watcher or risk_scorer

**Handling**:
- Proceed with baseline collection
- No filtering needed
- All captured processes are NEW
- Evidence contamination: ZERO

---

### Scenario B: Pre-Existing tech_watcher (From Prior Execution)

**Pre-execution snapshot shows**:
- PID 1234: python.exe tech_watcher.py (started 12:58:00Z)

**Execution happens**:
- PID 1234 continues running (not terminated by BAT)
- PID 3421: NEW python.exe tech_watcher.py spawned (started 13:00:13Z)
- PID 1234 terminates at 13:00:16Z (T3, but from PRE-EXISTING process)
- PID 3421 terminates at 13:00:18Z (TRUE T3, from NEW process)

**Issue**:
- Two T3 timestamps exist
- T3_preexisting = 13:00:16Z (PRE-EXISTING process exit)
- T3_new = 13:00:18Z (NEW process exit)
- F-SC-002 comparison must use T3_new, NOT T3_preexisting

**Filter Results**:
```json
{
  "excluded_events": [
    {
      "pid": 1234,
      "event_type": "PROCESS_TERMINATED",
      "timestamp": "2026-09-05T13:00:16.000Z",
      "reason": "EXCLUDED: Pre-existing process (created before observation window start at 13:00:00Z). Created at 12:58:00Z."
    }
  ],
  "included_events": [
    {
      "pid": 3421,
      "event_type": "PROCESS_CREATED",
      "timestamp": "2026-09-05T13:00:13.245Z",
      "reason": "INCLUDED: New process created during observation window"
    },
    {
      "pid": 3421,
      "event_type": "PROCESS_TERMINATED",
      "timestamp": "2026-09-05T13:00:18.000Z",
      "reason": "INCLUDED: Termination of new process (PID 3421)"
    }
  ]
}
```

**Impact on F-SC-002**:
- T3 = 13:00:18Z (from NEW process, PID 3421)
- T4 = 13:00:19Z (NEW process, PID 3512)
- T3 < T4 = TRUE
- Evidence valid: YES

---

### Scenario C: Double-Execution Protection Triggers (Expected Abort)

**Pre-execution snapshot shows**:
- PID 1234: python.exe tech_watcher.py (active)
- PID 1235: python.exe risk_scorer.py (active)

**Collector behavior**:
- Detects existing MoCKA processes
- Reports status: "EXISTING_PROCESS_CONFLICT"
- Aborts execution (MoCKA-START.bat will fail with exit code 1)
- No baseline evidence collected (expected)

**Outcome**:
- F-SC-002 baseline: NOT ACQUIRED (aborted as expected)
- Evidence contamination: N/A (no execution)
- Next step: Manual process cleanup or wait for completion

---

## Manifest Recording Requirements

**Every baseline evidence collection MUST include** a contamination control report:

```json
{
  "contamination_control": {
    "pre_execution_processes": [
      {
        "pid": 1234,
        "command_line": "python.exe ...tech_watcher.py...",
        "creation_time": "2026-09-05T12:58:00.000Z",
        "status": "PRE_EXISTING"
      }
    ],
    "pre_execution_process_count": 1,
    "observation_window_start": "2026-09-05T13:00:00.000Z",
    "observation_window_end": "2026-09-05T13:00:21.000Z",
    "events_included": 6,
    "events_excluded": 0,
    "excluded_pids": [],
    "contamination_status": "CLEAN",
    "contamination_notes": "No pre-existing tech_watcher or risk_scorer processes detected. All captured events are new processes created during observation window."
  }
}
```

---

## Acceptance Criteria for Clean Evidence

Evidence is considered "CONTAMINATION-FREE" if:

1. YES Pre-execution baseline captured at T0
2. YES All process events during window [T0, T6+1s] identified as NEW (creation time >= T0)
3. YES No PIDs from pre-execution snapshot appear in event stream
4. YES Parent PID lineage verified for T2, T3, T4, T5 events
5. YES Manifest includes contamination control report
6. YES Filter algorithm documented and applied
7. YES Excluded events (if any) clearly labeled with exclusion reason
8. YES F-SC-002 T3 timestamp comes from NEW process (not pre-existing)

---

END OF EXISTING PROCESS CONTAMINATION CONTROL

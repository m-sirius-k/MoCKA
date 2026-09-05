# HG-15 Normal Runtime Baseline Evidence Schema
## Data Structure Definition for F-SC-002 Runtime Baseline Evidence

Date: 2026-09-05
Version: 1.0
Scope: External observation data format

---

## 1. Collection Manifest Schema

```json
{
  "manifest": {
    "collection_id": "HG15-BASELINE-20260905-001",
    "collection_type": "NORMAL_RUNTIME_BASELINE",
    "collection_timestamp": "2026-09-05T13:00:00.000Z",
    "collector_version": "1.0",
    "collector_script": "HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1",
    "host_info": {
      "hostname": "SIROK-PC",
      "windows_version": "Windows 11 21H2",
      "powershell_version": "5.1.19041.1234",
      "current_user": "sirok"
    },
    "target": {
      "path": "C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
      "sha256_before": "abc123...",
      "sha256_after": "abc123...",
      "modification_detected": false
    },
    "observation_window": {
      "start": "2026-09-05T13:00:00.000Z",
      "end": "2026-09-05T13:05:15.000Z",
      "duration_seconds": 315
    },
    "status": "ACQUIRED",
    "abort_reason": null,
    "preconditions": {
      "existing_mocka_process": false,
      "double_execution_detected": false,
      "required_services_running": true,
      "python_available": true,
      "bat_unmodified": true
    },
    "evidence_quality": {
      "observation_method": "ETW_PROCESS_TRACING",
      "timestamp_precision_ms": 1,
      "process_lineage_available": true,
      "command_line_available": true,
      "exit_codes_available": true
    },
    "success_criteria": {
      "A_mocka_start_confirmed": true,
      "B_tech_watcher_start_confirmed": true,
      "C_tech_watcher_exit_confirmed": true,
      "D_risk_scorer_start_confirmed": true,
      "E_risk_scorer_exit_confirmed": true,
      "F_temporal_order_confirmed": true,
      "G_pid_info_complete": true,
      "H_evidence_reproducible": true
    },
    "f_sc_002_observable": true,
    "f_sc_002_status": "DIRECTLY_OBSERVABLE",
    "evidence_gaps": [],
    "files": [
      {
        "filename": "001_OBSERVATION_MANIFEST.json",
        "sha256": "...",
        "size_bytes": 2048,
        "creation_timestamp": "2026-09-05T13:05:15.000Z"
      },
      {
        "filename": "002_PROCESS_EVENTS_ETW.csv",
        "sha256": "...",
        "size_bytes": 8192,
        "creation_timestamp": "2026-09-05T13:05:15.000Z"
      }
    ]
  }
}
```

---

## 2. Process Event Record Schema

Each process event is recorded with:

```json
{
  "event_id": "EVT_20260905_130012_001",
  "event_type": "PROCESS_CREATE | PROCESS_EXIT | OBSERVATION_START | OBSERVATION_END",
  "event_category": "T1_MOCKA_START | T2_TECH_WATCHER_START | T3_TECH_WATCHER_EXIT | T4_RISK_SCORER_START | T5_RISK_SCORER_EXIT | T6_MOCKA_EXIT",
  "timestamp": {
    "iso8601": "2026-09-05T13:00:15.123Z",
    "unix_timestamp_ms": 1725543615123,
    "precision_ms": 1,
    "source": "ETW | EVENT_LOG | PROCESS_MONITOR"
  },
  "process": {
    "name": "python.exe",
    "exe_path": "C:\\Python39\\python.exe",
    "pid": 4521,
    "parent_pid": 3012,
    "command_line": "python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py --config config.ini",
    "working_directory": "C:\\Users\\sirok\\MoCKA",
    "user": "sirok",
    "creation_time": "2026-09-05T13:00:15.123Z",
    "exit_time": "2026-09-05T13:00:18.456Z",
    "exit_code": 0
  },
  "duration_ms": 3333,
  "parent_process": {
    "name": "cmd.exe",
    "pid": 3012,
    "exe_path": "C:\\Windows\\System32\\cmd.exe",
    "command_line": "cmd.exe /c C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat"
  },
  "observation_status": "DIRECTLY_OBSERVED | INFERRED | PARTIALLY_OBSERVED | NOT_OBSERVED",
  "confidence": "HIGH | MEDIUM | LOW",
  "notes": "Direct ETW observation with command-line capture"
}
```

---

## 3. CSV Export Format (for F-SC-002 Timeline Analysis)

```
event_id,event_type,event_category,timestamp_iso,timestamp_unix_ms,process_name,pid,parent_pid,command_line,exit_code,duration_ms,observation_source,confidence,notes

EVT_20260905_130000_000,OBSERVATION_START,OBSERVATION_START,2026-09-05T13:00:00.000Z,1725543600000,MONITOR,0,0,HG15_Baseline_Collector,,,ETW,HIGH,Observation window opened

EVT_20260905_130012_001,PROCESS_CREATE,T1_MOCKA_START,2026-09-05T13:00:12.001Z,1725543612001,cmd.exe,2401,1200,cmd.exe /c C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat,,,ETW,HIGH,MoCKA-START.bat execution begins

EVT_20260905_130013_002,PROCESS_CREATE,T2_TECH_WATCHER_START,2026-09-05T13:00:13.245Z,1725543613245,python.exe,3421,2401,python.exe C:\\Users\\sirok\\MoCKA\\tech_watcher.py,,,ETW,HIGH,tech_watcher.py process spawned

EVT_20260905_130016_003,PROCESS_EXIT,T3_TECH_WATCHER_EXIT,2026-09-05T13:00:16.789Z,1725543616789,python.exe,3421,2401,,0,3544,ETW,HIGH,tech_watcher.py process terminated normally

EVT_20260905_130017_004,PROCESS_CREATE,T4_RISK_SCORER_START,2026-09-05T13:00:17.123Z,1725543617123,python.exe,3512,2401,python.exe C:\\Users\\sirok\\MoCKA\\risk_scorer.py,,,ETW,HIGH,risk_scorer.py process spawned

EVT_20260905_130019_005,PROCESS_EXIT,T5_RISK_SCORER_EXIT,2026-09-05T13:00:19.456Z,1725543619456,python.exe,3512,2401,,0,2333,ETW,HIGH,risk_scorer.py process terminated normally

EVT_20260905_130020_006,PROCESS_EXIT,T6_MOCKA_EXIT,2026-09-05T13:00:20.890Z,1725543620890,cmd.exe,2401,1200,,0,8889,ETW,HIGH,MoCKA-START.bat execution completed

EVT_20260905_130021_007,OBSERVATION_END,OBSERVATION_END,2026-09-05T13:00:21.000Z,1725543621000,MONITOR,0,0,HG15_Baseline_Collector,,,ETW,HIGH,Observation window closed
```

---

## 4. Evidence Classification Schema

### 4.1 Observation Status (per event)

**DIRECTLY_OBSERVED**
- Event detected by monitoring system (ETW, event log, process monitor)
- Timestamp recorded with high precision (millisecond-level)
- Confidence: HIGH
- Example: ETW detected process creation event with command-line

**INFERRED**
- Event deduced from related observations
- Not directly observed by monitoring system
- Confidence: MEDIUM or LOW
- Example: Inferred process exit from process list comparison

**PARTIALLY_OBSERVED**
- Some aspects of event observed, others missing
- Example: Process name and PID observed, but exit code not available
- Confidence: MEDIUM

**NOT_OBSERVED**
- Monitoring system did not detect event
- Reason: either event did not occur, or monitoring gap
- Confidence: LOW

### 4.2 Evidence Assertion Classification

**CONFIRMED**
- Evidence directly supports assertion
- Observation status: DIRECTLY_OBSERVED
- Confidence: HIGH
- Falsity criterion: contradictory evidence exists
- Example: "tech_watcher.py started" confirmed if ETW detected process creation

**NOT_CONFIRMED**
- Evidence does NOT support assertion
- Reason: contradictory data OR no supporting data
- Sub-types:
  - NOT_OBSERVED: No evidence detected
  - CONTRADICTED: Evidence shows opposite
  - INDETERMINATE: Precision insufficient

**UNRESOLVED**
- Evidence insufficient to confirm or deny assertion
- Reason: precision gap, partial observation, or conflicting sources
- Action: Manual review or re-observation with higher precision
- Example: "tech_watcher EXIT before risk_scorer START" unresolved if timestamps have 1-second precision

**EVIDENCE_GAP**
- No evidence exists for this assertion
- Reason: observation method does not cover this scenario
- Action: Document gap and propose alternative observation method

---

## 5. F-SC-002 Specific Assessment Schema

```json
{
  "f_sc_002_assessment": {
    "claim": "tech_watcher.py exits before risk_scorer.py starts",
    "temporal_expression": "T3 < T4",
    
    "assertion_1": {
      "claim": "tech_watcher.py process creation observed",
      "status": "CONFIRMED | NOT_CONFIRMED | UNRESOLVED",
      "timestamp_t2": "2026-09-05T13:00:13.245Z",
      "pid": 3421,
      "evidence": "ETW process creation event",
      "confidence": "HIGH"
    },
    
    "assertion_2": {
      "claim": "tech_watcher.py process termination observed",
      "status": "CONFIRMED | NOT_CONFIRMED | UNRESOLVED",
      "timestamp_t3": "2026-09-05T13:00:16.789Z",
      "pid": 3421,
      "exit_code": 0,
      "evidence": "ETW process exit event",
      "confidence": "HIGH"
    },
    
    "assertion_3": {
      "claim": "risk_scorer.py process creation observed",
      "status": "CONFIRMED | NOT_CONFIRMED | UNRESOLVED",
      "timestamp_t4": "2026-09-05T13:00:17.123Z",
      "pid": 3512,
      "evidence": "ETW process creation event",
      "confidence": "HIGH"
    },
    
    "assertion_4": {
      "claim": "risk_scorer.py process termination observed",
      "status": "CONFIRMED | NOT_CONFIRMED | UNRESOLVED",
      "timestamp_t5": "2026-09-05T13:00:19.456Z",
      "pid": 3512,
      "exit_code": 0,
      "evidence": "ETW process exit event",
      "confidence": "HIGH"
    },
    
    "temporal_claim": {
      "claim": "T3 (tech_watcher EXIT) is BEFORE T4 (risk_scorer START)",
      "status": "CONFIRMED | NOT_CONFIRMED | UNRESOLVED",
      "t3_timestamp": "2026-09-05T13:00:16.789Z",
      "t4_timestamp": "2026-09-05T13:00:17.123Z",
      "time_gap_ms": 334,
      "precision_ms": 1,
      "calculation": "T4 - T3 = 17123 - 16789 = 334 ms",
      "result": "T3 < T4 = TRUE",
      "confidence": "HIGH"
    },
    
    "overall_status": "CONFIRMED | CONTRADICTED | UNRESOLVED",
    "reassessment_recommendation": "F-SC-002 can now be re-evaluated with baseline evidence"
  }
}
```

---

## 6. Evidence Integrity Record

```json
{
  "evidence_integrity": {
    "collection_id": "HG15-BASELINE-20260905-001",
    "modification_count_before": 0,
    "modification_count_after": 0,
    "modification_detected": false,
    "files_created": [
      "001_OBSERVATION_MANIFEST.json",
      "002_PROCESS_EVENTS_ETW.csv",
      "003_PROCESS_LINEAGE.txt",
      "004_EVENT_LOG_EXTRACT.txt",
      "005_BASELINE_EVIDENCE_MANIFEST.json"
    ],
    "files_modified": [],
    "files_deleted": [],
    "registry_modified": false,
    "bat_integrity": {
      "file_path": "C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
      "sha256_before_collection": "...",
      "sha256_after_collection": "...",
      "match": true
    },
    "python_files_integrity": {
      "modified_files": [],
      "integrity_status": "UNCHANGED"
    },
    "config_integrity": {
      "modified_files": [],
      "integrity_status": "UNCHANGED"
    },
    "database_integrity": {
      "modified_files": [],
      "integrity_status": "UNCHANGED"
    }
  }
}
```

---

## 7. Evidence Gap Documentation

```json
{
  "evidence_gaps": [
    {
      "gap_id": "GAP_001",
      "criterion": "G_pid_info_complete",
      "description": "Parent PID for risk_scorer.py could not be determined",
      "reason": "Command-line parsing ambiguous; assumes cmd.exe but not confirmed",
      "severity": "LOW",
      "impact_on_f_sc_002": "None (temporal order still confirmed)",
      "proposed_resolution": "Use Process Monitor to capture parent PID directly"
    },
    {
      "gap_id": "GAP_002",
      "criterion": "B_tech_watcher_start_confirmed",
      "description": "tech_watcher.py START not observed",
      "reason": "Process list check showed process absent at T2-100ms and present at T2+100ms",
      "severity": "CRITICAL",
      "impact_on_f_sc_002": "Cannot confirm START/EXIT sequence",
      "proposed_resolution": "Use ETW tracing to capture exact creation time"
    }
  ]
}
```

---

## 8. Reproducibility Metadata

For evidence reproducibility in future verifications:

```json
{
  "reproducibility": {
    "collection_method": "HG15_NORMAL_RUNTIME_BASELINE_COLLECTOR.ps1 v1.0",
    "observation_parameters": {
      "observation_start": "2026-09-05T13:00:00.000Z",
      "observation_duration_seconds": 315,
      "etw_trace_enabled": true,
      "event_log_query_enabled": true,
      "process_monitor_enabled": true,
      "timestamp_precision_ms": 1
    },
    "target_parameters": {
      "bat_path": "C:\\Users\\sirok\\MoCKA\\MoCKA-START.bat",
      "expected_processes": ["cmd.exe", "python.exe"],
      "expected_args": ["tech_watcher.py", "risk_scorer.py"]
    },
    "precondition_check": {
      "existing_processes_excluded": true,
      "services_verified": ["Windows Event Log"],
      "environment_clean": true
    },
    "result_reproducible": true,
    "notes": "Can be reproduced with identical parameters; expect similar timestamps within 5% variance"
  }
}
```

---

END OF EVIDENCE SCHEMA

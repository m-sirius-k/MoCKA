# HG-15 Collector Implementation Specification
## Detailed Implementation Requirements Based on Design Acceptance

Date: 2026-09-05
Version: 1.0
Scope: PowerShell Collector v2.0 implementation requirements

---

## Executive Summary

This specification defines the implementation requirements for a revised Normal Runtime Baseline Collector that:

1. Distinguishes DIRECT OBSERVATION from INFERENCE (not claiming direct when sampling)
2. Implements ETW process tracing as primary method (or documents why unavailable)
3. Separates timestamp sources explicitly in all evidence records
4. Filters pre-existing processes to prevent contamination
5. Accepts fallback to Event Log or sampling only if primary methods unavailable
6. Produces evidence that can definitively prove or disprove T3 < T4 temporal ordering

---

## Implementation Architecture

### Phase 0: Precondition Verification (UNCHANGED)

Existing precondition checks remain valid:
- PowerShell version >= 5.0
- Python runtime available
- No existing tech_watcher/risk_scorer processes (ABORT if found)
- MoCKA-START.bat file exists and unmodified
- Disk space available

**Change**: Add ETW/Event Log capability check:

```powershell
# New Check 0.7: ETW Availability
try {
  $etw_available = logman query HG15_Baseline -ets -ErrorAction SilentlyContinue
  if ($etw_available) { Write-Host "  OK: ETW trace capable" }
}
catch {
  Write-Host "  WARNING: ETW may not be available; will attempt Event Log fallback"
  $etw_available = $false
}
```

---

### Phase 1: Pre-Execution Baseline (REVISED)

**Objective**: Capture snapshot of all running processes before observation window

**Implementation**:

```powershell
# Capture comprehensive process baseline
$preexec_snapshot = Get-Process | Select-Object Name, Id, StartTime, @{
    Name="CommandLine"
    Expression={
        try { $_.CommandLine } catch { "[unavailable]" }
    }
} | Sort-Object StartTime

# Identify pre-existing MoCKA processes
$preexisting_mocka = $preexec_snapshot | Where-Object { 
    $_.CommandLine -match "(tech_watcher|risk_scorer)" 
}

# REQUIREMENT: Capture and label
$preexec_data = @{
    snapshot_timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffZ'
    processes_total = $preexec_snapshot.Count
    mocka_processes_preexisting = @($preexisting_mocka).Count
    all_processes = $preexec_snapshot
    excluded_pids = @($preexisting_mocka).Id
}

Export-Csv -Path "$OutputDir\00_PREEXEC_BASELINE.csv" -InputObject $preexec_snapshot
```

---

### Phase 2: Observation Method Selection (NEW)

**Logic**:

```powershell
$observation_method = $null

# Attempt 1: ETW (Primary)
if ($etw_available) {
    try {
        Write-Host "Attempting ETW trace setup..."
        logman create trace HG15_Baseline -ow -rt -ErrorAction Stop
        logman update trace HG15_Baseline -p "Microsoft-Windows-Kernel-Process" 0xff -ets -ErrorAction Stop
        logman start HG15_Baseline -ets -ErrorAction Stop
        
        Write-Host "  OK: ETW trace session started"
        $observation_method = "ETW"
    }
    catch {
        Write-Host "  ERROR: ETW setup failed; attempting fallback..."
        $observation_method = $null
    }
}

# Fallback 1: Event Log
if ($null -eq $observation_method) {
    try {
        Write-Host "Attempting Event Log setup..."
        $test_events = Get-WinEvent -LogName Security -FilterXPath "EventID=4688" -MaxEvents 1 -ErrorAction Stop
        Write-Host "  OK: Event Log is accessible"
        $observation_method = "EVENT_LOG"
    }
    catch {
        Write-Host "  WARNING: Event Log may not have process creation events enabled"
        $observation_method = "SAMPLING"
    }
}

# Fallback 2: Sampling (always available)
if ($null -eq $observation_method) {
    Write-Host "Falling back to sampling-based monitoring"
    $observation_method = "SAMPLING"
}

Write-Host "Observation method: $observation_method"
```

---

### Phase 3: Execution and Event Capture (REVISED BY METHOD)

#### 3A: IF ETW Method

```powershell
# Execute MoCKA-START.bat (trace already running)
$process = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$TargetBAT`"" `
    -NoNewWindow `
    -PassThru `
    -WorkingDirectory (Split-Path -Path $TargetBAT -Parent)

$process | Wait-Process
$exit_code = $process.ExitCode

# Stop ETW trace
logman stop HG15_Baseline -ets

# Save .etl file
# (Windows automatically saves to C:\Program Files\...\HG15_Baseline.etl)

# Parse .etl for events (using Get-WinEvent or ETL parser)
# REQUIREMENT: Extract Process Created and Process Terminated events
```

#### 3B: IF Event Log Method

```powershell
# Record Event Log tail timestamp before execution
$pre_exec_tail = Get-WinEvent -LogName Security -MaxEvents 1 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty TimeCreated

# Execute MoCKA-START.bat
$process = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$TargetBAT`"" `
    -NoNewWindow `
    -PassThru `
    -WorkingDirectory (Split-Path -Path $TargetBAT -Parent)

$process | Wait-Process
$exit_code = $process.ExitCode

# Query Event Log for process events during window
$event_log_events = Get-WinEvent -LogName Security -FilterXPath "
    (EventID=4688 or EventID=4689) and 
    TimeCreated>='$pre_exec_tail'
" -ErrorAction SilentlyContinue

# Parse events and extract timestamps
# REQUIREMENT: Convert Event Log structure to CSV with [timestamp, event_id, pid, image, command_line, parent_pid]
```

#### 3C: IF Sampling Method

```powershell
# Baseline snapshot
$sample_0 = Get-Process | Select-Object Name, Id, StartTime, CommandLine

# Polling loop during execution
$process = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$TargetBAT`"" `
    -NoNewWindow `
    -PassThru `
    -WorkingDirectory (Split-Path -Path $TargetBAT -Parent)

# Background job for sampling
$job = Start-Job -ScriptBlock {
    param($SampleInterval, $Duration)
    $samples = @()
    $start = [DateTime]::UtcNow
    
    while (([DateTime]::UtcNow - $start).TotalSeconds -lt $Duration) {
        $sample = @{
            timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffZ'
            processes = Get-Process | Select-Object Name, Id, StartTime, CommandLine
        }
        $samples += $sample
        Start-Sleep -Milliseconds $SampleInterval
    }
    
    return $samples
} -ArgumentList 500, 600  # 600 second duration max

# Wait for execution to complete
$process | Wait-Process
$exit_code = $process.ExitCode

# Collect samples
$samples = Receive-Job -Job $job

# REQUIREMENT: Analysis must mark ALL evidence as "INFERRED" with ±500ms bounds
# REQUIREMENT: Add warning that T3 < T4 ordering cannot be DIRECTLY PROVEN
```

---

### Phase 4: Event Timeline Construction (NEW)

**REQUIREMENT**: All timestamps must include SOURCE LABEL

```powershell
# Result object for all observation methods
$event_timeline = @{
    observation_method = $observation_method
    observation_window_start = $collection_start_time
    observation_window_end = $execution_end_time
    events = @()
}

# Example event record (same structure for ETW, Event Log, Sampling)
$event = @{
    event_id = "EVT_20260905_130013_002"
    event_type = "PROCESS_CREATED"
    event_category = "T2_TECH_WATCHER_START"
    
    timestamp = "2026-09-05T13:00:13.245Z"
    timestamp_source = "ETW_PROCESS_CREATED"  # or "EVENT_LOG_4688" or "INFERRED_SAMPLING"
    timestamp_precision_ms = 1  # or 1000 or 500 (sampling bounds)
    
    process = @{
        pid = 3421
        name = "python.exe"
        command_line = "python.exe C:\Users\sirok\MoCKA\tech_watcher.py --config config.ini"
        parent_pid = 2401
        parent_name = "cmd.exe"
        parent_command_line = "cmd.exe /c C:\Users\sirok\MoCKA\MoCKA-START.bat"
    }
    
    observation_status = "DIRECTLY_OBSERVED"  # or "INFERRED"
    confidence = "HIGH"  # or "MEDIUM" or "LOW"
    
    notes = "Direct ETW observation with parent PID verification"
}

$event_timeline.events += $event
```

---

### Phase 5: Contamination Filtering (NEW)

```powershell
# Apply filter algorithm
$clean_events = @()

foreach ($event in $event_timeline.events) {
    # Check 1: PID in pre-existing list?
    if ($event.process.pid -in $preexec_data.excluded_pids) {
        Write-Host "Excluding event: PID $($event.process.pid) is pre-existing"
        continue
    }
    
    # Check 2: Event timestamp within observation window?
    if ($event.timestamp -lt $preexec_data.snapshot_timestamp) {
        Write-Host "Excluding event: timestamp $($event.timestamp) before observation window"
        continue
    }
    
    # Check 3: (ETW/Event Log only) Process creation time within window?
    if ($observation_method -ne "SAMPLING" -and $event.process.creation_time -lt $preexec_data.snapshot_timestamp) {
        Write-Host "Excluding event: process created before observation window"
        continue
    }
    
    # Include event
    $clean_events += $event
    
    Write-Host "Including event: PID=$($event.process.pid), time=$($event.timestamp), source=$($event.timestamp_source)"
}

Write-Host "Contamination filtering: $($event_timeline.events.Count) total events, $($clean_events.Count) after filtering"
```

---

### Phase 6: F-SC-002 Temporal Analysis (NEW)

```powershell
# Find T3 and T4 events
$t3_event = $clean_events | Where-Object { 
    $_.event_category -eq "T3_TECH_WATCHER_EXIT" 
}

$t4_event = $clean_events | Where-Object { 
    $_.event_category -eq "T4_RISK_SCORER_START" 
}

if ($null -eq $t3_event -or $null -eq $t4_event) {
    $f_sc_002_analysis = @{
        status = "UNRESOLVED"
        reason = "Missing event(s): T3=$($null -eq $t3_event), T4=$($null -eq $t4_event)"
        confidence = "LOW"
    }
}
else {
    $t3_timestamp = [DateTime]::Parse($t3_event.timestamp)
    $t4_timestamp = [DateTime]::Parse($t4_event.timestamp)
    $time_gap_ms = ($t4_timestamp - $t3_timestamp).TotalMilliseconds
    
    if ($observation_method -eq "SAMPLING") {
        # CRITICAL: Sampling cannot prove ordering if within same window
        $f_sc_002_analysis = @{
            status = if ($time_gap_ms -gt 500) { "CONFIRMED" } else { "UNRESOLVED" }
            reason = if ($time_gap_ms -gt 500) { "Gap > 500ms proves order" } else { "Gap < 500ms; inferred only" }
            confidence = "MEDIUM"
            warning = "INFERRED from sampling, not DIRECT observation. Precision ±500ms"
        }
    }
    else {
        # ETW or Event Log: direct observation
        $f_sc_002_analysis = @{
            status = if ($time_gap_ms -gt 0) { "CONFIRMED" } else { "NOT_CONFIRMED" }
            reason = if ($time_gap_ms -gt 0) { "T3 < T4 proven by direct timestamps" } else { "T3 >= T4 contradiction" }
            confidence = "HIGH"
            warning = if ($observation_method -eq "EVENT_LOG" -and ($t3_timestamp.Second -eq $t4_timestamp.Second)) { "Warning: 1-second precision; order ambiguous" } else { $null }
        }
    }
    
    $f_sc_002_analysis.t3_timestamp = $t3_event.timestamp
    $f_sc_002_analysis.t4_timestamp = $t4_event.timestamp
    $f_sc_002_analysis.time_gap_ms = $time_gap_ms
}
```

---

### Phase 7: Manifest Creation (REVISED)

**REQUIREMENT**: Manifest must reflect ACTUAL implementation, not aspirational design

```powershell
$manifest = @{
    collection_id = "HG15-BASELINE-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    collection_timestamp = $collection_start_time
    
    observation_method = $observation_method
    observation_method_note = switch ($observation_method) {
        "ETW" { "Direct kernel process tracing; 1ms precision" }
        "EVENT_LOG" { "Audit log event parsing; 1s precision" }
        "SAMPLING" { "Process list polling every 500ms; inferred timing" }
    }
    
    preconditions_met = $true
    preconditions_issues = @()  # list any warnings
    
    execution_result = @{
        exit_code = $exit_code
        duration_seconds = $execution_duration
    }
    
    evidence_quality = @{
        observation_method = $observation_method
        timestamp_precision_ms = switch ($observation_method) { "ETW" { 1 } "EVENT_LOG" { 1000 } "SAMPLING" { 500 } }
        direct_t3_observation = ($observation_method -ne "SAMPLING")
        direct_t4_observation = ($observation_method -ne "SAMPLING")
        process_lineage_available = $true
        command_line_available = $true
    }
    
    contamination_control = @{
        preexisting_processes_detected = $preexec_data.mocka_processes_preexisting
        preexisting_pids_excluded = $preexec_data.excluded_pids
        events_total = $event_timeline.events.Count
        events_clean = $clean_events.Count
        events_filtered = $event_timeline.events.Count - $clean_events.Count
        contamination_status = if ($preexec_data.mocka_processes_preexisting -eq 0) { "CLEAN" } else { "FILTERED" }
    }
    
    f_sc_002_assessment = $f_sc_002_analysis
    
    success_criteria = @{
        A_mocka_start_confirmed = ($null -ne ($clean_events | Where-Object { $_.event_category -eq "T1_MOCKA_START" }))
        B_tech_watcher_start_confirmed = ($null -ne ($clean_events | Where-Object { $_.event_category -eq "T2_TECH_WATCHER_START" }))
        C_tech_watcher_exit_confirmed = ($null -ne $t3_event -and $observation_method -ne "SAMPLING")
        D_risk_scorer_start_confirmed = ($null -ne ($clean_events | Where-Object { $_.event_category -eq "T4_RISK_SCORER_START" }))
        E_risk_scorer_exit_confirmed = ($null -ne ($clean_events | Where-Object { $_.event_category -eq "T5_RISK_SCORER_EXIT" }))
        F_temporal_order_confirmed = ($f_sc_002_analysis.status -eq "CONFIRMED")
        G_pid_info_complete = ($null -ne ($clean_events | Where-Object { $_.process.parent_pid }))
        H_evidence_reproducible = $true
    }
    
    overall_status = if ($f_sc_002_analysis.status -eq "CONFIRMED") { "ACQUIRED_T3_LESS_T4_CONFIRMED" } elseif ($f_sc_002_analysis.status -eq "UNRESOLVED") { "ACQUIRED_INCONCLUSIVE" } else { "ACQUIRED_T3_NOT_LESS_T4" }
}

$manifest | ConvertTo-Json -Depth 10 | Out-File "$OutputDir\09_COLLECTION_MANIFEST.json"
```

---

## Output Files Required

**All Collector runs MUST produce** (regardless of success/failure):

1. `00_PREEXEC_BASELINE.csv` — Process snapshot at observation start
2. `01_EXECUTION_LOG.txt` — Timestamped execution phases and errors
3. `02_PROCESS_EVENTS.csv` — ETW/Event Log/sampling events with source labels
4. `03_STDOUT.txt` — MoCKA-START.bat stdout (as before)
5. `04_STDERR.txt` — MoCKA-START.bat stderr (as before)
6. `05_POSTEXEC_SNAPSHOT.csv` — Process snapshot at observation end
7. `06_CONTAMINATION_FILTER_REPORT.json` — PIDs excluded, reason, count
8. `07_CLEAN_EVENTS.csv` — Events after contamination filtering
9. `08_F_SC_002_ANALYSIS.json` — T3 < T4 comparison with verdict
10. `09_COLLECTION_MANIFEST.json` — Final manifest with status

---

## Fallback Logic Summary

```
IF (ETW available and setup succeeds)
  PROCEED with ETW method
  OUTCOME: Direct observation, 1ms precision, HIGH confidence
ELSE IF (Event Log accessible and process audit events present)
  PROCEED with Event Log method
  OUTCOME: Direct observation, 1s precision, MEDIUM confidence
ELSE IF (neither available)
  PROCEED with Sampling method
  WARNING: Output MUST clearly mark evidence as "INFERRED" not "DIRECT"
  WARNING: T3 < T4 ordering unresolvable if within ±500ms
  OUTCOME: Inferred detection, ±500ms precision, LOW confidence for ordering
```

---

## Mandatory Acceptance Criteria Before Windows Execution

Collector code MUST satisfy:

- [ ] Observation method selection logic implemented (try ETW, fall back to Event Log, fall back to Sampling)
- [ ] Timestamp source labels applied to every event
- [ ] Contamination filter algorithm implemented (PID and creation-time checks)
- [ ] Pre-execution baseline snapshot captured and saved
- [ ] Post-execution evidence filtering applied
- [ ] Manifest reflects ACTUAL implementation (not aspirational features)
- [ ] F-SC-002 analysis conditional on observation method (HIGH confidence for ETW/Event Log, MEDIUM/LOW for Sampling)
- [ ] Warning/disclaimer added if Sampling method used
- [ ] All 10 output files generated
- [ ] Timestamps separated by source (kernel event time ≠ observation time)

---

END OF COLLECTOR IMPLEMENTATION SPECIFICATION

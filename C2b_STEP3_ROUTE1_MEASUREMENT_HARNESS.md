# C2-b STEP 3: ROUTE 1 Clock Synchronization — Measurement Harness Design

**Document Number:** EBGA-C2B-AUD-PH3-001
**Date:** 2026-09-12 08:45 UTC
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Phase:** STEP 3 — ROUTE 1 Measurement Harness Specification

---

## Executive Summary

**ROUTE 1 Requirement:** 1000+ event samples collected over 24-hour continuous measurement period, demonstrating that timestamp ordering is strictly monotonic with no reversals and drift remains within acceptable bounds.

**Current Status:** Measurement harness DESIGNED and DOCUMENTED; execution status = NOT_ATTEMPTED (cannot execute 24-hour measurement in current session)

**Design Complete?** YES — All procedures, sample collection, validation, and drift calculation documented

**Execution Complete?** NO — Real 24-hour measurement cannot be completed in current session scope

**ROUTE 1 Status:** NOT_PROVEN (design documented, runtime execution required for PASS)

---

## ROUTE 1 Verification Criteria

### Requirement Summary

| Criterion | Requirement | Unit | Threshold |
|---|---|---|---|
| Sample Size | Minimum event count | samples | >= 1000 |
| Measurement Duration | Continuous time window | hours | >= 24 |
| Timestamp Ordering | Strict monotonicity | boolean | PASS if no reversals |
| Clock Drift | Time deviation | milliseconds | <= threshold (TBD) |
| Monotonicity Rate | Non-reversal proportion | percent | >= 99.9% |
| Evidence Completeness | All 1000+ samples timestamped | boolean | PASS |

**Verification Method:** Real-time event collection with timestamp validation post-collection.

---

## Measurement Harness Design

### 3.1 Sample Collection Procedure

#### Collection Points (1000+ Samples Over 24 Hours)

**Required Sampling Strategy:**

| Phase | Duration | Target Samples | Frequency | Rationale |
|---|---|---|---|---|
| Phase 1: Baseline | Hour 0-6 | 100+ | Every 6-10 min | Establish baseline ordering |
| Phase 2: Load | Hour 6-18 | 400+ | Every 1-2 min | Stress test under load |
| Phase 3: Recovery | Hour 18-24 | 500+ | Every 1-2 min | Verify sustained monotonicity |

**Total:** 1000+ samples minimum over 24-hour continuous window

#### Sample Collection Method

**Event Trigger Mechanism:**

1. **Automation Approach (Preferred):**
   - Trigger events via `/api/gate/event` endpoint using HTTP POST requests
   - Collect timestamp from response: `when_ts` (UTC ISO8601)
   - Record event_id from response for tracking
   - Sample interval: 1 minute average across collection window

2. **Script-Based Collection:**
   - Create `scripts/route1_collector.py` to automate HTTP POST requests
   - Sample payload template:
     ```json
     {
       "what_type": "ROUTE1_SAMPLE",
       "title": "Clock Synchronization Sample",
       "event_source": "test_route1",
       "tags": "route1_measurement,phase1|2|3"
     }
     ```
   - Collect response timestamps: `event_id`, `when_ts`

3. **Manual Collection (Fallback):**
   - Use `curl` to POST samples at regular intervals
   - Log response timestamps to CSV
   - Parse CSV post-collection for analysis

#### Sample Completeness Criteria

**Collection Success Criteria:**
- [ ] Minimum 1000 unique event_ids collected
- [ ] All events have when_ts values (ISO8601 UTC)
- [ ] Timestamp range spans >= 24 hours
- [ ] No gaps > 10 minutes in collection window (except planned maintenance)
- [ ] Collection completion timestamp recorded

**Completeness Check (Post-Collection):**

```python
# Pseudo-code for sample validation
samples = [
    {"event_id": "E20260912_000012ab", "when_ts": "2026-09-12T00:00:05Z"},
    # ... 1000+ samples
]

assert len(samples) >= 1000, f"Sample size {len(samples)} < 1000"

timestamps = [datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00')) for s in samples]
min_ts = min(timestamps)
max_ts = max(timestamps)
duration = (max_ts - min_ts).total_seconds() / 3600

assert duration >= 24, f"Duration {duration}h < 24h"
```

**Status:** DESIGN_COMPLETE (not executed)

### 3.2 Timestamp Validation Procedure

#### Monotonicity Check

**Definition:** Timestamps are strictly monotonic if T(i) < T(i+1) for all consecutive samples.

**Algorithm:**

```python
def check_monotonicity(samples):
    """
    Check timestamp ordering. Return (is_monotonic, reversals, anomalies).
    """
    timestamps = [(s['event_id'], datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00'))) 
                  for s in samples]
    
    reversals = []
    for i in range(len(timestamps) - 1):
        id_i, ts_i = timestamps[i]
        id_j, ts_j = timestamps[i + 1]
        if ts_j <= ts_i:  # Equal or reverse
            reversals.append({
                "index": i,
                "event_i": id_i,
                "ts_i": ts_i.isoformat(),
                "event_j": id_j,
                "ts_j": ts_j.isoformat(),
                "delta_ms": (ts_j - ts_i).total_seconds() * 1000,
                "severity": "REVERSAL" if ts_j < ts_i else "EQUAL_TIMESTAMP"
            })
    
    is_monotonic = len(reversals) == 0
    monotonicity_rate = (len(samples) - len(reversals)) / len(samples) * 100 if samples else 0
    
    return {
        "is_monotonic": is_monotonic,
        "reversals": reversals,
        "total_samples": len(samples),
        "reversal_count": len(reversals),
        "monotonicity_rate_percent": monotonicity_rate,
    }
```

**Verification Criteria:**
- PASS: No reversals (monotonicity_rate = 100%)
- WARN: <= 0.1% reversals (monotonicity_rate >= 99.9%)
- FAIL: > 0.1% reversals (monotonicity_rate < 99.9%)

**Status:** DESIGN_COMPLETE (algorithm documented, not executed)

#### Timestamp Ordering Analysis

**Expected Ordering Pattern:**

Given: Samples collected at ~1-minute intervals over 24 hours

```
Sample 1:  2026-09-12T00:00:05.123456Z
Sample 2:  2026-09-12T00:01:05.789012Z  (delta = ~60s)
Sample 3:  2026-09-12T00:02:05.345678Z  (delta = ~60s)
...
Sample 1440: 2026-09-13T00:00:05.999999Z (24 hours later, delta = ~60s)
```

**Validation Checks:**
1. **Ordering:** T(i) < T(i+1) for all i
2. **Consistency:** delta_time(i) ~= 60 seconds (within ±5s tolerance per sample)
3. **No Outliers:** No unexpected large jumps (> 5 minutes between consecutive samples)
4. **Timezone:** All timestamps in UTC (Z suffix or +00:00)

**Status:** DESIGN_COMPLETE (patterns documented, not executed)

### 3.3 Clock Drift Analysis

#### Drift Definition

**Clock Drift:** Systematic deviation of measured time from true elapsed time.

**Formula:**
```
measured_duration = T(last) - T(first)
expected_duration = 24 hours (86400 seconds)
drift_ms = (measured_duration - expected_duration) * 1000
drift_rate_ppm = (drift_ms / expected_duration) * 1000000
```

#### Drift Calculation Procedure

```python
def calculate_drift(samples):
    """
    Calculate clock drift from sample timestamps.
    """
    if len(samples) < 2:
        return None
    
    timestamps = [datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00')) for s in samples]
    first_ts = timestamps[0]
    last_ts = timestamps[-1]
    
    measured_duration_s = (last_ts - first_ts).total_seconds()
    expected_duration_s = 24 * 3600  # 86400
    
    drift_s = measured_duration_s - expected_duration_s
    drift_ms = drift_s * 1000
    drift_rate_ppm = (drift_s / expected_duration_s) * 1000000 if expected_duration_s > 0 else 0
    
    return {
        "first_sample_ts": first_ts.isoformat(),
        "last_sample_ts": last_ts.isoformat(),
        "measured_duration_s": measured_duration_s,
        "expected_duration_s": expected_duration_s,
        "drift_seconds": drift_s,
        "drift_milliseconds": drift_ms,
        "drift_rate_ppm": drift_rate_ppm,
        "drift_assessment": (
            "PASS" if abs(drift_ms) <= 1000 else  # <= 1 second drift
            "WARN" if abs(drift_ms) <= 5000 else  # <= 5 second drift
            "FAIL"
        )
    }
```

#### Drift Thresholds

| Threshold | Value | Assessment | Action |
|---|---|---|---|
| Excellent | < 100 ms | PASS | Meets ROUTE 1 requirement |
| Good | 100-1000 ms | PASS | Meets ROUTE 1 requirement |
| Acceptable | 1-5 seconds | WARN | Meets requirement with note |
| Poor | > 5 seconds | FAIL | Does not meet requirement |

**Status:** DESIGN_COMPLETE (thresholds defined, not executed)

### 3.4 Measurement Completeness Verification

#### Data Quality Checks

```python
def verify_measurement_completeness(samples, expected_duration_hours=24, expected_sample_count=1000):
    """
    Verify that collected measurement meets completeness criteria.
    """
    
    issues = []
    
    # Check 1: Sample count
    if len(samples) < expected_sample_count:
        issues.append({
            "check": "sample_count",
            "result": "FAIL",
            "detail": f"Collected {len(samples)} samples, expected >= {expected_sample_count}"
        })
    else:
        issues.append({
            "check": "sample_count",
            "result": "PASS",
            "detail": f"Collected {len(samples)} samples (>= {expected_sample_count})"
        })
    
    # Check 2: Timestamp range
    if len(samples) >= 2:
        timestamps = [datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00')) for s in samples]
        duration_h = (max(timestamps) - min(timestamps)).total_seconds() / 3600
        if duration_h < expected_duration_hours:
            issues.append({
                "check": "duration",
                "result": "FAIL",
                "detail": f"Measurement span {duration_h:.1f}h < {expected_duration_hours}h"
            })
        else:
            issues.append({
                "check": "duration",
                "result": "PASS",
                "detail": f"Measurement span {duration_h:.1f}h >= {expected_duration_hours}h"
            })
    
    # Check 3: Missing timestamps
    samples_with_ts = sum(1 for s in samples if s.get('when_ts'))
    if samples_with_ts < len(samples):
        issues.append({
            "check": "timestamp_completeness",
            "result": "FAIL",
            "detail": f"{len(samples) - samples_with_ts} samples missing when_ts"
        })
    else:
        issues.append({
            "check": "timestamp_completeness",
            "result": "PASS",
            "detail": f"All {len(samples)} samples have when_ts"
        })
    
    # Check 4: Collection continuity
    if len(samples) >= 2:
        timestamps = [datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00')) for s in samples]
        gaps = []
        for i in range(len(timestamps) - 1):
            gap_s = (timestamps[i+1] - timestamps[i]).total_seconds()
            if gap_s > 600:  # > 10 minutes
                gaps.append({"index": i, "gap_seconds": gap_s})
        
        if gaps:
            issues.append({
                "check": "continuity",
                "result": "WARN",
                "detail": f"Found {len(gaps)} gaps > 10min: {gaps}"
            })
        else:
            issues.append({
                "check": "continuity",
                "result": "PASS",
                "detail": "No gaps > 10 minutes detected"
            })
    
    return {
        "is_complete": all(i["result"] != "FAIL" for i in issues),
        "checks": issues,
        "summary": "COMPLETE" if all(i["result"] != "FAIL" for i in issues) else "INCOMPLETE"
    }
```

**Status:** DESIGN_COMPLETE (completeness checks defined, not executed)

---

## Execution Plan (If Environment Allows)

### 3.5 Collection Execution Steps (NOT PERFORMED)

**Step 1: Preparation Phase**

```bash
# Create collection directory
mkdir -p data/route1_measurement/
cd data/route1_measurement/

# Create collection script (scripts/route1_collector.py)
# - POST requests to /api/gate/event endpoint
# - Log responses to CSV: event_id, when_ts, collected_at
# - Run for 24 hours continuously
```

**Step 2: Baseline Phase (Hours 0-6)**

```bash
# Start collector
python scripts/route1_collector.py --duration 6 --interval 360 \
  --output data/route1_measurement/phase1_baseline.csv

# Expected: ~60 samples (1 sample every 6 minutes)
```

**Step 3: Load Phase (Hours 6-18)**

```bash
# Increase sampling frequency
python scripts/route1_collector.py --duration 12 --interval 60 \
  --output data/route1_measurement/phase2_load.csv

# Expected: ~720 samples (1 sample every 1 minute)
```

**Step 4: Recovery Phase (Hours 18-24)**

```bash
# Maintain sampling frequency
python scripts/route1_collector.py --duration 6 --interval 60 \
  --output data/route1_measurement/phase3_recovery.csv

# Expected: ~360 samples (1 sample every 1 minute)
```

**Step 5: Analysis Phase**

```bash
# Combine samples
cat phase1_baseline.csv phase2_load.csv phase3_recovery.csv > all_samples.csv

# Run validation
python scripts/route1_analyzer.py --input all_samples.csv \
  --output data/route1_measurement/analysis_report.json

# Generate report
python scripts/route1_report.py --input analysis_report.json \
  --output C2b_ROUTE1_MEASUREMENT_RESULTS.md
```

**Status:** DESIGN_COMPLETE (execution not attempted; environment constraint)

### 3.6 Why 24-Hour Measurement Cannot Be Completed

**Constraint 1: Session Duration**
- Current session is temporary (remote execution environment)
- Session will be terminated after task completion
- Cannot sustain 24-hour continuous data collection

**Constraint 2: Database Not Initialized**
- data/mocka_events.db does not exist
- No schema for persistent event storage
- Collection would require DB initialization outside Implementation Authorization scope

**Constraint 3: Testing Environment**
- This is a code review and design audit, not a deployment environment
- ROUTE 1 execution requires production-like conditions with sustained 24-hour operation
- Simulation or partial measurement would violate "Don't fake 24h measurement" requirement

**Decision:** Do not attempt partial measurement or simulation. Record ROUTE 1 status as NOT_EXECUTED with clear rationale.

**Status:** NOT_EXECUTED (environment constraint, not design gap)

---

## Measurement Harness Code Templates

### 3.7 Collection Script Template (For Future Execution)

**File: `scripts/route1_collector.py` (Template)**

```python
#!/usr/bin/env python3
"""
ROUTE 1 Measurement Collector
Collects 1000+ event samples over 24-hour period for clock synchronization verification.

Usage:
    python route1_collector.py --duration 24 --interval 60 --output samples.csv
"""

import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests")
    sys.exit(1)


def collect_sample(api_url, sample_num):
    """
    Collect single sample via HTTP POST to /api/gate/event.
    Returns: {"event_id": ..., "when_ts": ..., "status": ...}
    """
    payload = {
        "what_type": "ROUTE1_SAMPLE",
        "title": f"Clock Synchronization Sample #{sample_num}",
        "event_source": "test_route1_measurement",
        "tags": f"route1_measurement,sample_{sample_num}",
        "who_actor": "KUROKO_MEASUREMENT",
    }
    
    try:
        response = requests.post(f"{api_url}/api/gate/event", json=payload, timeout=5)
        data = response.json()
        return {
            "event_id": data.get("event_id", ""),
            "when_ts": data.get("when_ts", ""),
            "status": data.get("status", ""),
            "http_status": response.status_code,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "event_id": "",
            "when_ts": "",
            "status": "error",
            "error": str(e),
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


def main():
    parser = argparse.ArgumentParser(description="ROUTE 1 Measurement Collector")
    parser.add_argument("--api-url", default="http://localhost:5000",
                        help="Flask API base URL")
    parser.add_argument("--duration", type=int, default=24,
                        help="Collection duration in hours")
    parser.add_argument("--interval", type=int, default=60,
                        help="Sample interval in seconds")
    parser.add_argument("--output", default="route1_samples.csv",
                        help="Output CSV file")
    args = parser.parse_args()
    
    samples_to_collect = (args.duration * 3600) // args.interval
    print(f"Collecting ~{samples_to_collect} samples over {args.duration}h at {args.interval}s interval")
    print(f"Output: {args.output}")
    print(f"API: {args.api_url}")
    print()
    
    samples = []
    start_time = time.time()
    sample_num = 0
    
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > args.duration * 3600:
                break
            
            sample_num += 1
            sample = collect_sample(args.api_url, sample_num)
            samples.append(sample)
            
            # Log progress
            eta_samples = args.duration * 3600 / args.interval
            progress = (sample_num / eta_samples) * 100
            print(f"[{sample_num:4d}/{int(eta_samples):4d}] {progress:5.1f}% - "
                  f"event_id={sample['event_id']} status={sample['status']}")
            
            # Wait for next sample
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print(f"\nCollection interrupted. Collected {len(samples)} samples.")
    
    # Write CSV
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["event_id", "when_ts", "status", "collected_at", "http_status"])
        writer.writeheader()
        writer.writerows(samples)
    
    print(f"\nSaved {len(samples)} samples to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Status:** TEMPLATE_DOCUMENTED (ready for future execution; not executed now)

### 3.8 Analysis Script Template (For Future Execution)

**File: `scripts/route1_analyzer.py` (Template)**

```python
#!/usr/bin/env python3
"""
ROUTE 1 Measurement Analyzer
Analyzes collected samples for clock synchronization verification.

Usage:
    python route1_analyzer.py --input samples.csv --output analysis.json
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path


def load_samples(csv_file):
    """Load samples from CSV."""
    samples = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        samples = list(reader)
    return samples


def check_monotonicity(samples):
    """Check timestamp monotonicity."""
    timestamps = []
    for i, s in enumerate(samples):
        try:
            ts = datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00'))
            timestamps.append((i, s['event_id'], ts))
        except:
            pass
    
    reversals = []
    for i in range(len(timestamps) - 1):
        idx_i, id_i, ts_i = timestamps[i]
        idx_j, id_j, ts_j = timestamps[i + 1]
        if ts_j <= ts_i:
            reversals.append({
                "index": idx_i,
                "event_i": id_i,
                "ts_i": ts_i.isoformat(),
                "event_j": id_j,
                "ts_j": ts_j.isoformat(),
                "delta_ms": (ts_j - ts_i).total_seconds() * 1000,
                "severity": "REVERSAL" if ts_j < ts_i else "EQUAL",
            })
    
    monotonicity_rate = ((len(timestamps) - len(reversals)) / len(timestamps) * 100) if timestamps else 0
    
    return {
        "total_samples": len(timestamps),
        "reversals": len(reversals),
        "monotonicity_rate_percent": monotonicity_rate,
        "is_monotonic": len(reversals) == 0,
        "reversal_details": reversals,
    }


def calculate_drift(samples):
    """Calculate clock drift."""
    timestamps = []
    for s in samples:
        try:
            ts = datetime.fromisoformat(s['when_ts'].replace('Z', '+00:00'))
            timestamps.append(ts)
        except:
            pass
    
    if len(timestamps) < 2:
        return None
    
    first_ts = min(timestamps)
    last_ts = max(timestamps)
    
    measured_duration_s = (last_ts - first_ts).total_seconds()
    expected_duration_s = 24 * 3600
    
    drift_s = measured_duration_s - expected_duration_s
    drift_ms = drift_s * 1000
    drift_rate_ppm = (drift_s / expected_duration_s) * 1000000 if expected_duration_s > 0 else 0
    
    return {
        "first_sample_ts": first_ts.isoformat(),
        "last_sample_ts": last_ts.isoformat(),
        "measured_duration_s": measured_duration_s,
        "expected_duration_s": expected_duration_s,
        "drift_seconds": drift_s,
        "drift_milliseconds": drift_ms,
        "drift_rate_ppm": drift_rate_ppm,
        "drift_assessment": (
            "PASS" if abs(drift_ms) <= 1000 else
            "WARN" if abs(drift_ms) <= 5000 else
            "FAIL"
        )
    }


def main():
    parser = argparse.ArgumentParser(description="ROUTE 1 Analyzer")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", default="analysis.json", help="Output JSON file")
    args = parser.parse_args()
    
    print(f"Loading samples from {args.input}...")
    samples = load_samples(args.input)
    print(f"Loaded {len(samples)} samples")
    
    print("Checking monotonicity...")
    monotonicity = check_monotonicity(samples)
    
    print("Calculating drift...")
    drift = calculate_drift(samples)
    
    analysis = {
        "sample_count": len(samples),
        "monotonicity": monotonicity,
        "drift": drift,
        "route1_status": (
            "PASS" if (monotonicity['is_monotonic'] and 
                      drift and drift['drift_assessment'] in ('PASS', 'WARN'))
            else "FAIL"
        )
    }
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"Analysis saved to {args.output}")
    print(f"\nROUTE 1 Status: {analysis['route1_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Status:** TEMPLATE_DOCUMENTED (ready for future execution; not executed now)

---

## ROUTE 1 Measurement Harness Summary

### Design Completeness Checklist

- [x] Sample collection procedure documented (1000+ over 24 hours)
- [x] Sampling strategy defined (3 phases: baseline, load, recovery)
- [x] Collection method specified (HTTP POST to /api/gate/event)
- [x] Timestamp validation algorithm designed (monotonicity check)
- [x] Clock drift analysis formula documented
- [x] Drift thresholds defined (< 1s = PASS, < 5s = WARN)
- [x] Measurement completeness checks specified (4 criteria)
- [x] Collection script template provided (route1_collector.py)
- [x] Analysis script template provided (route1_analyzer.py)
- [x] Execution plan documented (steps 1-5)

### Execution Readiness

**Blockers for Execution:**
1. Session duration (24-hour measurement requires sustained environment)
2. Database not initialized (no storage for measurements)
3. Testing environment (not production-like for 24-hour operation)

**Decision:** Record ROUTE 1 as NOT_PROVEN with clear execution plan for future implementation phase.

**Status:** DESIGN_COMPLETE / EXECUTION_NOT_ATTEMPTED

---

## ROUTE 1 Status: Design Verification Complete

**ROUTE 1 Requirement:** 1000+ samples over 24 hours with timestamp monotonicity verification

**Design Status:** COMPLETE
- Sample collection procedure: DESIGNED
- Timestamp validation: DESIGNED
- Drift analysis: DESIGNED
- Measurement harness: COMPLETE with templates

**Execution Status:** NOT_ATTEMPTED
- Reason: Environment constraint (24-hour measurement not feasible in session scope)
- Not a design gap; design is complete and executable
- Execution blocked by environment, not by missing design

**ROUTE 1 Assessment:** NOT_PROVEN (design complete; runtime execution required for PASS)

**Next Step:** STEP 4 — AUTH_GAP_001 Role Registry Design

---

**Event Recording:** Pending mocka_write_event call (CHANGE_DONE)
**Authority:** Implementation Authorization Phase
**Custodian:** KUROKO Monitor (Claude-Haiku-4.5)
**Session:** claude/kuroko-c2b-route-audit-n51wgf


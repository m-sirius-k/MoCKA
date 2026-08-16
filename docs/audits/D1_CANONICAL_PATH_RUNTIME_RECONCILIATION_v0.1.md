# D-1 Canonical Path / Runtime Reconciliation: Technical Analysis
## Version 0.1 (Investigation - READ-ONLY)

**Date**: 2026-08-16  
**Task**: D-1 Canonical Path Investigation (No Code Changes, No Approvals)  
**Status**: COMPLETE - Path Mismatch Confirmed, Technical Blocker Identified

---

## PART 1: FACT - Path Analysis Results

### 1.1 Code-Level Path Constants

**File**: `/home/user/MoCKA/tools/mocka_restrictions.py`

```python
# Lines 7-11
INCIDENTS_DIR = r"C:\Users\sirok\MoCKA\docs\incidents"
OUTPUT = r"C:\Users\sirok\MoCKA\docs\governance\GPT_RESTRICTIONS.md"
INC_LIFECYCLE_DIR = r"C:\Users\sirok\MoCKA\data\inc_lifecycle"
HUMAN_GATE_REQUEST_PREFIX = "INC-LIFECYCLE-"
```

**Path Type**: Hardcoded Windows absolute paths
**Format**: Raw strings (r'' prefix)
**OS Specificity**: Windows only
**Environment Variable Usage**: NONE
**Dynamic Resolution**: NONE
**Repository-Relative**: NO

---

### 1.2 Runtime Environment

```
OS: Linux (sys.platform = 'linux')
Python: 3.11.15 (/usr/local/bin/python3)
Working Directory: /home/user/MoCKA (repository root)
Repository Location: /home/user/MoCKA (Linux absolute path)
```

---

### 1.3 Path Mismatch Summary

| Component | Code Path (Hardcoded) | Actual Location (Linux) | Match |
|-----------|----------------------|------------------------|-------|
| **Incidents** | `C:\Users\sirok\MoCKA\docs\incidents` | `/home/user/MoCKA/docs/incidents` | ❌ NO |
| **Output** | `C:\Users\sirok\MoCKA\docs\governance\GPT_RESTRICTIONS.md` | `/home/user/MoCKA/docs/governance/GPT_RESTRICTIONS.md` | ❌ NO |
| **Lifecycle** | `C:\Users\sirok\MoCKA\data\inc_lifecycle` | `/home/user/MoCKA/data/inc_lifecycle` | ❌ NO |

**Mismatch Type**: Windows vs Linux path format

---

## PART 2: EVIDENCE - Detailed Investigation

### 2.1 is_publishable() Path Resolution

**Code Path** (line 37):
```python
path = os.path.join(INC_LIFECYCLE_DIR, f"{inc_id}.json")
```

**Runtime Behavior**:
```
Input: 
  INC_LIFECYCLE_DIR = "C:\Users\sirok\MoCKA\data\inc_lifecycle"
  inc_id = "INC-20260401-001"

os.path.join() output:
  "C:\Users\sirok\MoCKA\data\inc_lifecycle/INC-20260401-001.json"

os.path.exists() check:
  Returns: False (Windows path doesn't exist on Linux filesystem)
```

**Test Results**:

```python
# Test 1: Code's hardcoded Windows path
windows_path = r"C:\Users\sirok\MoCKA\data\inc_lifecycle\INC-20260401-001.json"
os.path.exists(windows_path)  # Result: False

# Test 2: Actual file created by Task #13
linux_path = "/home/user/MoCKA/data/inc_lifecycle/INC-20260401-001.json"
os.path.exists(linux_path)  # Result: True
```

**Conclusion**: The infrastructure created in Task #13 is unreachable from is_publishable() due to hardcoded Windows paths.

---

### 2.2 glob.glob() Pattern Matching

**Code** (line 74):
```python
incidents = glob.glob(os.path.join(INCIDENTS_DIR, "INC-*.md"))
```

**Hardcoded Pattern**:
```
C:\Users\sirok\MoCKA\docs\incidents\INC-*.md
```

**Runtime Behavior on Linux**:

```python
# Test 1: Windows pattern
pattern_win = r"C:\Users\sirok\MoCKA\docs\incidents\INC-*.md"
glob.glob(pattern_win)  # Result: [] (empty list)

# Test 2: Linux pattern  
pattern_linux = "/home/user/MoCKA/docs/incidents/INC-*.md"
glob.glob(pattern_linux)  # Result: [INC-20260401-001.md, INC-20260401-002.md]
```

**Impact**: generate_restrictions() finds ZERO incidents (even though 2 exist on disk)

**Evidence of Impact**: Earlier test runs showed:
```
[インシデント数] 0件
[掲載] 0件 / [非掲載] 0件
```

The code discovers zero incidents because glob.glob() fails on Windows paths.

---

### 2.3 Code Portability Characteristics

| Aspect | Observation |
|--------|------------|
| **Path Format** | Hardcoded Windows absolute paths only |
| **OS Detection** | No sys.platform checks |
| **Environment Variables** | No $HOME, $PWD, or custom env vars used |
| **Dynamic Resolution** | No pathlib, no os.path.expanduser(), no repository-relative logic |
| **Fallback Paths** | None (only Windows paths) |
| **Cross-Platform Logic** | Absent entirely |

**Code Portability Assessment**: Windows-only (no Linux/macOS support)

---

### 2.4 Repository-Relative Path Analysis

**Observation**: Line 24 in human_gate_get_state() uses:
```python
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

This DOES resolve the repository root dynamically. However:
- This is only used in human_gate_get_state() (subsidiary function)
- The main path constants (INCIDENTS_DIR, INC_LIFECYCLE_DIR, OUTPUT) are hardcoded
- There is no fallback or repository-relative resolution for the critical paths

---

## PART 3: UNKNOWN - Deployment Context

### 3.1 Intended Runtime Environment

**Question**: Is the code designed ONLY for Windows, or should it be cross-platform?

**Evidence Available**:
- All hardcoded paths are Windows format
- No cross-platform logic present
- Code runs successfully on Windows (implied by hardcoded paths being specific)

**Evidence NOT Available**:
- No configuration file specifying target OS
- No comments explaining Windows-only design
- No documentation on deployment requirements
- No environment setup instructions in repository

**Assessment**: UNKNOWN - Unclear whether Windows-only is intentional or oversight

---

### 3.2 Prior Successful Execution

**Question**: Has this code ever run successfully on the current system?

**Evidence**:
- GPT_RESTRICTIONS.md exists (generated 2026-07-31 18:07:02)
- Contents show INC-001 was processed (restriction content present)
- But current code would produce empty output

**Hypothesis**: 
- GPT_RESTRICTIONS.md was generated on Windows system (where hardcoded paths valid)
- File was then committed to git (now available on Linux)
- Code itself never runs successfully on Linux environment

---

## PART 4: CRITICAL FINDINGS

### Finding 1: Hardcoded Windows Paths Prevent All Operations

**Severity**: CRITICAL - Code completely non-functional on Linux

**Affected Functions**:
- generate_restrictions() - cannot find incidents (glob.glob returns empty)
- is_publishable() - cannot find state files (os.path.exists returns False)
- Any file I/O in is_publishable() - all path checks fail

**Impact**:
- Case 4 cannot be tested on current Linux environment
- Infrastructure created in Task #13 is unreachable
- Code must run on Windows, or paths must be fixed

---

### Finding 2: Task #13 Infrastructure Created Correctly (for Linux)

**Verification**:
```
Files created:
  /home/user/MoCKA/data/inc_lifecycle/INC-20260401-001.json  ✓ EXISTS
  /home/user/MoCKA/data/inc_lifecycle/INC-20260401-002.json  ✓ EXISTS

Files are valid:
  ✓ JSON syntax correct
  ✓ Schema version 0.1 valid
  ✓ incident_id matches filename
  ✓ state values in valid domain

Files are accessible (from Linux):
  ✓ Can read with open(linux_path)
  ✓ Can parse with json.load()
  ✓ Can verify content
```

**Conclusion**: Infrastructure is well-formed and accessible on Linux, but unreachable from Windows-hardcoded code.

---

## PART 5: ROOT CAUSE ANALYSIS

### Q1: What is the canonical lifecycle directory for is_publishable()?

**Answer**: 
- **Code says**: `C:\Users\sirok\MoCKA\data\inc_lifecycle` (Windows absolute path)
- **Linux filesystem has**: `/home/user/MoCKA/data/inc_lifecycle`
- **Canonical path depends on**: WHETHER code runs on Windows or Linux
  - If Windows: `C:\Users\sirok\MoCKA\data\inc_lifecycle`
  - If Linux: `/home/user/MoCKA/data/inc_lifecycle`
- **Current runtime**: Linux
- **Current canonical path**: `/home/user/MoCKA/data/inc_lifecycle`

---

### Q2: Are Task #13 JSON files actually accessible from current runtime?

**Answer**: 
- **Yes**: They ARE accessible via Linux paths: `/home/user/MoCKA/data/inc_lifecycle/INC-*.json`
- **No**: They are NOT accessible via is_publishable() because is_publishable() looks at Windows paths

**Conclusion**: File accessibility depends on which paths you check through.

---

### Q3: What is the root cause of the path mismatch?

**Answer**: **CODE PORTABILITY DEFECT**

| Aspect | Status |
|--------|--------|
| Infrastructure placement | ✓ Correct (Linux paths) |
| Runtime environment | ✓ Linux (correct for current system) |
| Code paths | ❌ Windows hardcoded (incorrect for Linux) |
| Root cause | CODE - hardcoded Windows paths |

**Diagnosis**: Code assumes Windows environment, but runtime is Linux. This is a code issue, not an infrastructure issue.

---

### Q4: Does this require code modification to solve?

**Answer**: **YES - Code modification is required**

**Options**:

**Option A: Modify code to detect runtime OS and use appropriate paths** (REQUIRES CODE CHANGE)
```python
# Proposed (not implemented - Task #14 is READ-ONLY)
if sys.platform == "win32":
    INC_LIFECYCLE_DIR = r"C:\Users\sirok\MoCKA\data\inc_lifecycle"
else:  # Linux/macOS
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INC_LIFECYCLE_DIR = os.path.join(repo_root, "data", "inc_lifecycle")
```

**Option B: Only deploy code to Windows** (NO CODE CHANGE)
```
Deploy environment: Windows system where C:\Users\sirok\MoCKA\ path exists
Current environment: Linux - not compatible
```

**Option C: Use repository-relative paths for all paths** (REQUIRES CODE CHANGE)
```python
# Proposed (not implemented - Task #14 is READ-ONLY)
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INC_LIFECYCLE_DIR = os.path.join(repo_root, "data", "inc_lifecycle")
INCIDENTS_DIR = os.path.join(repo_root, "docs", "incidents")
OUTPUT = os.path.join(repo_root, "docs", "governance", "GPT_RESTRICTIONS.md")
```

---

## PART 6: BLOCKING CONDITION CLASSIFICATION

### For Case 4 Execution: What is blocking it?

**Classification**:

| Blocker | Type | Status | Needs |
|---------|------|--------|-------|
| **Technical: Path Mismatch** | TECHNICAL BLOCKER | ACTIVE | Code modification OR Windows deployment |
| **Human: Approval Decision** | HUMAN AUTHORITY BLOCKER | PENDING | R01 authorization |

**Critical Distinction**:
- **Technical blocker**: Can be solved by fixing code paths (not by creating approvals)
- **Human blocker**: Can only be solved by R01 making approval decision (not by infrastructure setup)

### Current Status for Case 4 Execution:

```
Prerequisites:
  1. Infrastructure (directory, JSON files, database table): ✓ READY
  2. Path resolution (code can find infrastructure): ❌ BLOCKED
  3. Human approval (R01 decides incidents are publishable): ❌ PENDING

Result: Case 4 CANNOT EXECUTE
Reason: Technical blocker (hardcoded Windows paths) prevents even reaching human approval stage
```

---

## PART 7: EVIDENCE SUMMARY TABLE

| Finding | Evidence | Confidence |
|---------|----------|-----------|
| Code has Windows hardcoded paths | Direct code inspection (lines 7-11) | 100% |
| Runtime is Linux | sys.platform = 'linux', /home/user/MoCKA | 100% |
| Path mismatch exists | os.path.exists(windows_path) = False | 100% |
| Task #13 files are accessible (Linux) | os.path.exists(linux_path) = True | 100% |
| Task #13 files are NOT accessible (code) | is_publishable() would hit FC-1 | 100% |
| glob.glob() finds zero incidents | Test: glob.glob(windows_pattern) = [] | 100% |
| glob.glob() would find incidents (correct path) | Test: glob.glob(linux_pattern) = [2 files] | 100% |
| Code is Windows-only | No OS detection, no fallback paths | High |
| GPT_RESTRICTIONS.md from earlier (Windows) | Commit history, timestamps | Medium |

---

## PART 8: RECONCILIATION ASSESSMENT

### R01判断 - Path Status

**Classification**: **B. PATH MISMATCH REQUIRES TECHNICAL FIX**

**Evidence**:
1. ✓ Code canonical path identified: `C:\Users\sirok\MoCKA\data\inc_lifecycle`
2. ✓ Runtime path identified: Linux `/home/user/MoCKA/data/inc_lifecycle`
3. ✓ Mismatch confirmed: Windows vs Linux absolute paths
4. ✓ Root cause identified: Hardcoded Windows paths in code
5. ✓ Impact verified: is_publishable() cannot find files on Linux
6. ✓ Requirement determined: Code modification needed OR Windows deployment required

---

## PART 9: RECOMMENDATIONS FOR R01

### Immediate Decision Required

**Question**: Is this codebase meant to run on Windows only, or should it be cross-platform?

**If Windows-only**:
- Deployment environment: Windows system with `C:\Users\sirok\MoCKA\` path
- Current Linux investigation: For documentation/design purposes only
- Case 4 execution: Proceed on Windows environment

**If Cross-platform intended**:
- Code modification: Paths must be made repository-relative or OS-aware
- Examples:
  ```python
  # Option 1: Repository-relative (recommended)
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  INC_LIFECYCLE_DIR = os.path.join(repo_root, "data", "inc_lifecycle")
  
  # Option 2: OS detection
  if sys.platform == "win32":
      INC_LIFECYCLE_DIR = r"C:\Users\sirok\MoCKA\data\inc_lifecycle"
  else:
      repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      INC_LIFECYCLE_DIR = os.path.join(repo_root, "data", "inc_lifecycle")
  ```
- Scope: Affects mocka_restrictions.py lines 7-11 (and similar in mocka_risk_engine.py if applicable)

### For Case 4 Validation

**Current Path Mismatch**: BLOCKING

**To Proceed with Case 4 on Current Linux Environment**:
1. ⚠️ Code modification required (outside Task #14 scope)
2. OR redeploy to Windows environment where paths are valid

**Prerequisites for Case 4** (after resolving technical blocker):
1. ✓ Infrastructure created (Task #13): DONE
2. ⏳ Path resolution fixed: PENDING
3. ⏳ Human approval (R01): PENDING

---

## PART 10: FINAL ASSESSMENT

### Status: **B. PATH MISMATCH REQUIRES TECHNICAL FIX**

### Summary

**Infrastructure Layer** (Task #13):
- ✅ READY: Directory created, JSON files valid, database initialized
- ✅ VERIFIED: Files accessible via Linux paths
- ✅ CORRECT: Schema, incident_id, state values all valid

**Code Layer** (Task #14 finding):
- ❌ BLOCKED: Hardcoded Windows paths make code non-functional on Linux
- ❌ VERIFIED: glob.glob() returns empty, os.path.exists() returns False
- ❌ CRITICAL: is_publishable() cannot reach Task #13 infrastructure

**Approval Layer**:
- ⏳ PENDING: Human Authority (R01) decision on INC-001/INC-002 publication

### What Must Happen Before Case 4

```
Current Status:
  Infrastructure         ✓ READY
  Code Path Resolution   ❌ BLOCKED (technical, requires code fix)
  Human Approval         ⏳ PENDING (policy, requires R01 decision)

Blocker Sequence:
  1. Resolve path mismatch (technical) ← FIRST BLOCKER
  2. Obtain R01 approval (policy) ← SECOND BLOCKER
  3. Execute Case 4 ← CAN PROCEED after both

What blocks advancement: Step 1 (code must be fixed for current environment)
```

---

## CONCLUSION

The infrastructure setup in Task #13 is **technically sound and well-formed**. However, it is **unreachable from the current codebase** due to hardcoded Windows paths.

**Technical Blocker Found**: Code assumes Windows environment (`C:\Users\sirok\...`), but runtime is Linux (`/home/user/MoCKA/...`)

**Resolution Required**: Either modify code for cross-platform support, or deploy to Windows environment where hardcoded paths are valid.

**Human Authority Still Pending**: R01 must authorize publication of INC-001/INC-002 (separate issue from path mismatch).


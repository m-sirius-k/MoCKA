# Stage 2: Connection Matrix Analysis - Broken/Missing Connections

**Execution Date:** 2026-09-26
**Phase:** KUROKO WEB先遣隊フェーズ - Systematic Topology Mapping
**Related Commits:** d5ba1d5 (HAB implementation), 3d79101 (HAB gateway integration)

---

## Summary of Findings

Total issues identified: **6 broken/missing connections**
Fixed this session: **1** (HAB integration)
Pending repairs: **5**

---

## Detailed Connection Map

### 1. ✓ FIXED: HAB (Human Authority Boundary) - Orphaned to Integrated

**Status:** RESOLVED
**Commit:** 3d79101

**What was broken:**
- HAB Common Core existed in `gateway/hab_bridge.py` (d5ba1d5)
- But NOT imported or called by any Flask endpoint
- HAB entry point: none (orphaned)

**What was fixed:**
- Added import in `gateway/gateway.py`: `from hab_bridge import create_hab_core`
- Initialized HAB core with adapter registry
- Added new endpoint: `POST /api/v1/hab/dispatch`
  - Accepts JARVIS requests
  - Routes through `hab_core.dispatch_to_ai()`
  - Returns trace_id and socket routing information

**Connection now established:**
```
JARVIS request → gateway.py:/api/v1/hab/dispatch
                 → hab_core.dispatch_to_ai()
                 → AISocket (GPT/Gemini/etc.)
```

**Test verification:** Endpoint responds to POST requests, dispatches to available sockets

---

### 2. OPEN: JARVIS Engine - Isolated (No Instantiation)

**Status:** BROKEN
**Location:** `runtime/jarvis/core/engine.py`
**Severity:** HIGH - breaks JARVIS→HAB chain

**What's broken:**
- File exists with JarvisEngine class
- Constructor is defined but **never called** anywhere in codebase
- Zero references to `JarvisEngine()` outside of its own module
- Only reference is internal definition in `engine.py:4`

**Current code:**
```python
class JarvisEngine:
    def __init__(self):
        self.gate = HumanGate()
    def evaluate(self, decision_id):
        return self.gate.request(decision_id)
```

**Impact:**
- JARVIS decision evaluation logic unreachable
- No entry point for external callers
- Human Gate never invoked from JARVIS path

**Repair approach:**
- Need endpoint in app.py or gateway.py to instantiate JarvisEngine
- Likely: `POST /api/v1/jarvis/evaluate` with decision_id parameter
- Connect to existing human_gate_bp once fixed

---

### 3. OPEN: Human Gate Blueprint - Not Registered

**Status:** BROKEN
**Location:** `phi_os/human_gate.py` (line 18)
**Severity:** HIGH - blocks all decision approvals

**What's broken:**
- Blueprint defined: `human_gate_bp = Blueprint('human_gate', __name__)`
- Defines Flask routes for decision state transitions
- **NOT imported** in `app.py`
- **NOT registered** with `app.register_blueprint()`
- Result: All `/api/human_gate/*` endpoints unreachable

**Current registration list in app.py (lines 72-82):**
```python
app.register_blueprint(ai_session_bp)
app.register_blueprint(handshake_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reflection_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(mentor_bp)
app.register_blueprint(commission_bp)
app.register_blueprint(context_bp)
app.register_blueprint(gate_bp)
app.register_blueprint(integrity_bp)
app.register_blueprint(time_api_bp)
# MISSING: human_gate_bp
```

**Impact:**
- Decision approval workflow inaccessible
- State transitions (PENDING→APPROVED/REJECTED) can't be triggered
- Human Gate review process offline

**Repair approach:**
- Add import: `from phi_os.human_gate import human_gate_bp` to app.py
- Add registration: `app.register_blueprint(human_gate_bp)` with other blueprints
- Minimal change (2 lines)

---

### 4. OPEN: Memory Pipeline - Not Integrated

**Status:** BROKEN
**Location:** `memory/memory_pipeline.py`
**Severity:** MEDIUM - breaks memory enrichment layer

**What's broken:**
- MemoryPipeline class exists and is well-structured
- Implements full pipeline: Writer → Store → Index → Retriever → Context Builder
- **Zero instantiation** in app.py or gateway.py
- No endpoints to invoke memory operations
- Only reference: `memory/memory_reinforcer.py` mentions it in a comment

**Current isolation:**
```
memory/ subsystem is completely isolated
↓
not called by app.py
↓
not called by gateway.py
↓
not called by any event processing path
```

**Impact:**
- Memory enrichment layer disconnected from event flow
- Context building blocked
- Decision/Semantic enrichment cannot access historical memory

**Repair approach:**
- Determine if memory should be:
  - Option A: Instantiated in app.py globally and exposed via endpoints
  - Option B: Integrated into event_buffer flush pipeline
  - Option C: Lazy-loaded via integration with event_gate
- Likely Option B: Memory enrichment as step in event processing

---

### 5. OPEN: Orchestra - Not Connected

**Status:** BROKEN
**Location:** `orchestra/` directory
**Severity:** MEDIUM - breaks conflict resolution layer

**What's broken:**
- `orchestra/conflict_interpreter.py` exists with ConflictInterpreter class
- **Zero imports** in app.py or gateway.py
- **Zero instantiation** anywhere in main flow
- Described as single conflict resolution entry point but unreachable

**Current isolation:**
```
orchestra/ subsystem is completely isolated
↓
not imported by app.py
↓
not imported by gateway.py
↓
not part of any event processing chain
```

**Impact:**
- Conflict interpretation layer offline
- No resolution path for decision conflicts
- Orchestra-level coordination unavailable

**Repair approach:**
- Determine when Orchestra should be invoked:
  - After decision conflicts detected? (in event_gate?)
  - Separate endpoint for conflict queries?
- Likely: integrate as decision conflict handler in phi_os/event_gate.py

---

### 6. OPEN: Event Buffer Fallback Path - OS Hardcoded (Platform Incompatibility)

**Status:** BROKEN
**Location:** `interface/event_buffer.py` (line 27)
**Severity:** MEDIUM - blocks fallback persistence in cloud/Linux

**What's broken:**
- Line 27: `FALLBACK_PATH = Path(r"C:\Users\sirok\MoCKA\data\event_buffer_fallback.jsonl")`
- Windows-specific absolute path hardcoded
- **Will fail** in Linux/cloud environment
- Used in `_load_fallback()` and `_persist_fallback()` methods

**Current behavior:**
```
Linux environment:
  Path("C:\Users\sirok\...").exists() → False
  → Fallback loading fails silently (graceful degradation, but NOT ideal)

When Gate is down:
  _persist_fallback() tries to write to C:\ → Path creation fails
  → Events lost (should have been persisted)
```

**Impact:**
- Event fallback persistence fails in Linux/cloud
- If PHI-OS Gate is unavailable, events can be lost
- Only affects failure scenarios, but critical for resilience

**Repair approach:**
- Use relative path from repo root: `data/event_buffer_fallback.jsonl`
- Code: `FALLBACK_PATH = Path(__file__).parent.parent / "data" / "event_buffer_fallback.jsonl"`
- Minimal change (1 line)

---

## Connection Matrix - Current State

| Component | Imported By | Instantiated By | Endpoints | Status |
|-----------|------------|-----------------|-----------|--------|
| HAB | gateway.py | gateway.py | ✓ /api/v1/hab/dispatch | CONNECTED |
| JARVIS | - | - | ✗ NONE | ORPHANED |
| Human Gate BP | - | - | ✗ NOT REGISTERED | ORPHANED |
| Memory Pipeline | - | - | ✗ NONE | ORPHANED |
| Orchestra | - | - | ✗ NONE | ORPHANED |
| Event Buffer | app.py, gateway.py | app.py | ✓ push()/flush() | CONNECTED |
| Event Gate | app.py (as gate_bp) | - | ✓ /api/gate/* | CONNECTED |
| Relay Kernel | app.py | via _get_relay_kernel() | ✓ /collect | CONNECTED |
| Auth | gateway.py | - | ✓ require_api_key() | CONNECTED |

---

## Repair Priority (Minimal Path to Full Integration)

**Priority 1 (Critical):**
1. Register human_gate_bp in app.py (2 lines, unblocks decision approval)

**Priority 2 (High):**
2. Fix event_buffer FALLBACK_PATH (1 line, enables cloud resilience)
3. Add JARVIS Engine instantiation endpoint (requires design decision on routing)

**Priority 3 (Medium):**
4. Integrate Memory Pipeline (requires design decision on where/when)
5. Connect Orchestra (requires design decision on when to invoke)

---

## Evidence & Notes

- Stage 1 (Component Inventory): All major components found in filesystem
- Stage 2 (Connection Matrix): Import/instantiation analysis reveals 5 orphaned components
- Next Stage 3: Runtime Verification - test actual E2E chains with these repairs

**Generated by:** KUROKO WEB先遣隊フェーズ (Systematic Topology Mapping)
**Related TODO:** None yet - awaiting approval for repairs


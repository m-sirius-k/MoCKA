# Stage 2: Comprehensive Broken Connections Report

**Status:** KUROKO WEB先遣隊フェーズ - Systematic Topology Mapping
**Report Date:** 2026-09-26
**Methodology:** Automated codebase search + manual verification
**Total Issues Found:** 20+ broken/missing connections
**Repairs Completed This Session:** 5
**Repairs Still Pending:** 15+

---

## Executive Summary

Full codebase analysis reveals a distributed system with 3 ports (5000=app, 5010=gateway, 5002=mcp) that are **NOT fully connected**. Critical layers (Memory, Human Gate approvals, Orchestra reasoning) exist but are isolated from the main event loop.

**Key finding:** Event buffer → Event gate → Database path is solid. Everything beyond the database (enrichment, reasoning, approval) is disconnected.

---

## Completed Repairs (5 Fixed)

### ✓ REPAIR 1: HAB Integration (commit 3d79101)
- **What was fixed:** HAB orphaned in gateway/hab_bridge.py
- **How:** Added `/api/v1/hab/dispatch` endpoint in gateway.py
- **Impact:** JARVIS can now route to AI sockets via HAB

### ✓ REPAIR 2: Human Gate Blueprint Registration (commit e5cff2d)
- **What was fixed:** phi_os/human_gate.py blueprint not registered in app.py
- **How:** Added import + register_blueprint() in app.py
- **Impact:** Decision approval endpoints (`/api/human_gate/*`) now accessible

### ✓ REPAIR 3: Event Buffer Fallback Path (commit e5cff2d)
- **What was fixed:** Hardcoded Windows path in interface/event_buffer.py:27
- **How:** Changed to cross-platform relative path
- **Impact:** Event fallback persistence now works in cloud/Linux environments

### ✓ REPAIR 4: JARVIS Engine Instantiation (commit c2401c4)
- **What was fixed:** JarvisEngine exists but never instantiated/called
- **How:** Created runtime/jarvis/api.py blueprint with `/api/jarvis/evaluate` endpoint
- **Impact:** JARVIS decision evaluation accessible via HTTP

### ✓ REPAIR 5: Import Path Correction (commit a4853a8)
- **What was fixed:** db_helper.py:14 wrong import path
- **How:** Changed `phi_os.event.event_gate` → `phi_os.event_gate`
- **Impact:** process_event fallback path now works correctly

---

## Critical Issues Still Open (15+ Repairs Pending)

### ISSUE #1: Memory Pipeline - Completely Isolated

**Severity:** HIGH
**Location:** `memory/memory_pipeline.py` + app.py
**Status:** BROKEN - Zero integration with event loop

**What's broken:**
```
memory_pipeline exists with full pipeline structure:
  Writer → Store → Index → Retriever → Context Builder

BUT:
  - Not imported by app.py
  - Not imported by gateway.py
  - No Flask blueprint
  - No event_buffer callbacks
  - MemoryPipeline class exists but never instantiated
```

**Impact:**
- Memory enrichment layer offline
- Decision/Semantic operations can't access historical memory
- Context building blocked

**Repair approach:**
- Option A: Create memory_api.py blueprint with endpoints
- Option B: Integrate memory flush into event_gate processing
- Recommendation: **Option B** - memory should enrich events as they flow through gate

**Lines of code needed:** ~50-100

---

### ISSUE #2: Orchestra - Isolated Conflict Resolver

**Severity:** MEDIUM
**Location:** `orchestra/conflict_interpreter.py` + no app integration
**Status:** BROKEN - Only used in test/validation code

**What's broken:**
```
orchestra/ subsystem exists but:
  - Not imported by app.py
  - Not imported by gateway.py
  - No Flask blueprint
  - No HTTP endpoints
  - Only referenced in architecture_verify.py and test code
```

**Impact:**
- Conflict resolution logic unreachable from event loop
- Orchestra reasoning unavailable at runtime
- No way to query/resolve decision conflicts

**Repair approach:**
- Integrate as decision conflict handler in phi_os/event_gate.py
- When event has CONFLICT state, invoke orchestra.interpret_conflict()
- Return conflict resolution guidance to workflow

**Lines of code needed:** ~30-50

---

### ISSUE #3: Relay - Partially Connected (Receive Only)

**Severity:** MEDIUM
**Location:** `relay/relay_kernel.py` (line 1005 in app.py)
**Status:** BROKEN - Initialized but not actively fed events

**What's broken:**
```
RelayKernel created and stored in _RELAY_KERNEL_SINGLETON
  BUT
  - event_buffer.push() sends to event_gate, NOT relay_kernel
  - relay_kernel.ingest() only called from /collect endpoint (side effect)
  - No active integration with main event processing loop
```

**Impact:**
- Relay state projections don't reflect main event flow
- Event replay path disconnected from forward path
- RelayKernel acting as dead code for most event processing

**Repair approach:**
- After event_gate.process_event(), call relay_kernel.ingest()
- Ensure relay maintains parallel state projection with event stream
- Enable event replay/temporal queries

**Lines of code needed:** ~10-20

---

### ISSUE #4: Port Isolation - Three Separate Flask Apps

**Severity:** MEDIUM
**Location:** app.py (5000) / gateway.py (5010) / mocka_mcp_server.py (5002)
**Status:** BROKEN - No unified event processing chain

**What's broken:**
```
Port 5000: app.py (main orchestration)
  - Handles decisions, governance, approvals
  - Registers 13+ blueprints
  - Uses event_buffer for persistence

Port 5010: gateway.py (AI adapter layer)
  - Handles AI provider connections
  - HAB dispatcher (newly added)
  - Separate event_buffer instance

Port 5002: mocka_mcp_server.py (MCP protocol layer)
  - Tools for governance layer
  - Conditional event processing
  - Separate integration points

PROBLEM: Each port has its own context, no unified event flow
```

**Impact:**
- Events from different ports don't share consistent ordering
- Decision context from port 5000 invisible to port 5010 AI calls
- No unified approval state across all ports

**Repair approach:**
- Requires architectural decision on event unification
- Either: centralize event_buffer (shared between ports)
- Or: implement inter-port HTTP callbacks for event sync
- Complex - requires discussion with governance

**Estimated effort:** 50-100 lines + architectural review

---

### ISSUE #5: MCP Server Conditional Imports (3+ broken paths)

**Severity:** HIGH
**Location:** `mocka_mcp_server.py` lines 33, 48, 217, 225
**Status:** BROKEN - Multiple import failures

**Broken imports:**
```python
Line 33: from governance_pipeline import DecisionPipeline  # CONDITIONAL
Line 48: from registry_store import RegistryStore  # CONDITIONAL
Line 217: from phi_os.context.working_context import WorkingContext  # CONDITIONAL
Line 225: from phi_os.context.context_scheduler import maybe_snapshot  # CONDITIONAL
```

**Impact:**
- MCP tools may fail to initialize
- Governance pipeline not accessible from MCP
- Context snapshotting may fail
- Tool availability unpredictable

**Repair approach:**
- Remove conditional imports, use proper module paths
- Replace with try/except with specific error logging
- Ensure all MCP tools fail clearly (not silently)

**Lines of code needed:** ~20-30

---

### ISSUE #6: Missing Blueprint Registrations (2+ remaining)

**Severity:** HIGH
**Location:** app.py blueprint registration section (lines 72-83)
**Status:** BROKEN - Unknown blueprints missing

**What's missing:**
- Memory-related blueprints (if they exist)
- Semantic pipeline blueprints (if they exist)
- Audit blueprint (phi_os.audit_trigger if it has routes)

**Impact:**
- Endpoints may be unreachable
- Routes for enrichment layers inaccessible

**Repair approach:**
- Audit all phi_os/*.py and semantic/*.py for Blueprint definitions
- Register all defined blueprints in app.py

**Lines of code needed:** ~5-15 (per blueprint)

---

## Detailed Issue Breakdown

| Issue # | Component | Type | Severity | Status | ETA |
|---------|-----------|------|----------|--------|-----|
| 1 | Memory Pipeline | Integration | HIGH | OPEN | 2-3 hrs |
| 2 | Orchestra | Integration | MEDIUM | OPEN | 1-2 hrs |
| 3 | Relay | Integration | MEDIUM | OPEN | 30 min |
| 4 | Port Isolation | Architecture | MEDIUM | OPEN | Review |
| 5 | MCP Imports | Bug | HIGH | OPEN | 30 min |
| 6 | Missing Blueprints | Integration | HIGH | OPEN | 30 min |
| 7 | event_bus import | Path | LOW | CHECK | 5 min |
| 8 | orchestra_context_bridge | Missing | LOW | CHECK | 5 min |
| 9 | audit_trigger import | Path | LOW | CHECK | 5 min |
| 10-20 | Various conditional imports | Bug | LOW | CHECK | 30 min |

---

## Current Architecture Map

```
USER
  ↓
[app.py:5000]
  ↓
Blueprint handlers (13+)
  ├─ decision_pipeline
  ├─ semantic_pipeline
  ├─ reflection_engine
  ├─ event_gate ← ✓ connected
  ├─ human_gate ← ✓ JUST fixed
  ├─ integrity
  ├─ time_api
  ├─ ai_session
  ├─ relay (partial)
  └─ jarvis ← ✓ JUST connected
  ↓
event_buffer.push() ← ✓ connected
  ↓ (async)
/api/gate/event/batch
  ↓
[event_gate.py] ← ✓ connected
  ↓
[sqlite events.db] ← ✓ connected
  ↓
[memory_pipeline] ← ✗ DISCONNECTED
  ↓
[orchestra] ← ✗ DISCONNECTED
  ↓
[relay_kernel] ← ⚠ partially connected
  
[gateway.py:5010] ← SEPARATE PORT
  ├─ HAB dispatcher ← ✓ JUST connected
  └─ AI Socket adapters → event_buffer (separate instance)

[mocka_mcp_server.py:5002] ← SEPARATE PORT
  ├─ Tool definitions
  └─ Conditional event paths
```

---

## Stage 3: Next Steps (Runtime Verification)

Once repairs are complete:

1. **Test Memory Enrichment Path**
   - Push event → verify memory stores it
   - Query memory → verify retrieval works
   - Check context enrichment in decision pipeline

2. **Test Orchestra Conflict Resolution**
   - Create conflicting decisions
   - Verify orchestra.interpret_conflict() invoked
   - Check resolution guidance flows back

3. **Test Relay Event Projection**
   - Push events through main flow
   - Verify relay_kernel.ingest() receives them
   - Check temporal query capabilities work

4. **Test Inter-Port Communication**
   - AI request from gateway
   - Decision approval from app
   - Verify context flows correctly between ports

5. **Test MCP Tool Availability**
   - List available MCP tools
   - Execute governance tools
   - Verify all conditional imports resolve

---

## Summary Table: Broken Connections by Category

| Category | Count | Severity | Examples |
|----------|-------|----------|----------|
| Missing Integration (not connected to event loop) | 3 | HIGH | Memory, Orchestra, Relay (partial) |
| Import Path Errors | 2 | MEDIUM | event.event_gate, event_bus |
| Missing Blueprint Registration | 2+ | HIGH | Unknown (audit all phi_os/*) |
| Port Isolation | 3 | MEDIUM | app/gateway/mcp not unified |
| Conditional Import Failures | 8+ | MEDIUM | governance_pipeline, context modules |
| Missing Module Exports | 3+ | LOW | Various phi_os submodules |
| **TOTAL** | **20+** | **MIXED** | **See detailed list above** |

---

**Report Generated By:** KUROKO WEB先遣隊フェーズ  
**Related Documentation:** 
- STAGE_2_CONNECTION_MATRIX.md (initial findings)
- Explore Agent comprehensive analysis (130KB+ research)
- Commits: 3d79101, e5cff2d, c2401c4, a4853a8

**Next Phase:** Systematic repair of High-priority issues (Memory, Blueprints, MCP imports)

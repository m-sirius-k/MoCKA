# Stage 3 Phase 2: Comprehensive Investigation Plan

**Created:** 2026-09-26  
**Scope:** 25 items to investigate across system topology  
**Reuse Strategy:** Leverage Stage 2 findings; avoid duplication  
**Classification Method:** WEB可能 / FIXATION_REQUIRED / PC実行 / Freeze候補

---

## 25 Investigation Items: Classified & Sequenced

### Category A: Runtime Path & Connectivity (8 items)

**A1. Endpoint Reachability**
- **Definition:** All 109 app.route + 13 blueprint routes respond to requests
- **Stage 2 Status:** HAB/Human Gate/JARVIS fixed; others assumed reachable
- **WEB Scope:** ✓ CAN INVESTIGATE - code inspection + light testing
- **Approach:** Trace each @app.route to (a) function exists, (b) no missing imports, (c) response defined
- **Output:** ENDPOINT_REACHABILITY_MATRIX.md

**A2. Import Graph**
- **Definition:** All imports resolve; no circular dependencies
- **Stage 2 Status:** Fixed db_helper import path (commit a4853a8)
- **WEB Scope:** ✓ CAN INVESTIGATE - static code analysis
- **Approach:** grep all imports; verify all refer to existing modules
- **Output:** IMPORT_DEPENDENCY_GRAPH.md

**A3. Process / Port Relationship**
- **Definition:** Port 5000 (app.py), 5010 (gateway.py), 5002 (mcp) correctly configured
- **Stage 2 Status:** Partially analyzed (gateway exists as standalone)
- **WEB Scope:** ✓ CAN INVESTIGATE - configuration review
- **Approach:** Review listening ports, startup sequence, inter-process communication
- **Output:** PORT_CONFIGURATION_MATRIX.md

**A4. Health Endpoint**
- **Definition:** All 3 processes have /health or equivalent
- **Stage 2 Status:** Found in app.py, gateway.py
- **WEB Scope:** ✓ CAN INVESTIGATE - endpoint audit
- **Approach:** Find all /health, /status, /ping endpoints; verify they return expected format
- **Output:** HEALTH_ENDPOINTS_AUDIT.md

**A5. Event Gate Routing**
- **Definition:** All event sources correctly route to event_gate.process_*
- **Stage 2 Status:** event_buffer, /collect, event_gate.py analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - routing path trace
- **Approach:** Follow event from 5 sources to event_gate; verify no losses
- **Output:** EVENT_ROUTING_PATHS.md

**A6. PHI-OS Route**
- **Definition:** HAB AI responses correctly reach PHI-OS event_gate
- **Stage 2 Status:** HAB has route_to_phi_os() method defined
- **WEB Scope:** ✓ CAN INVESTIGATE - method call trace
- **Approach:** Verify HAB → receive_from_ai() → route_to_phi_os() → Event Buffer → event_gate
- **Output:** JARVIS_HAB_PHIOS_ROUTE_TRACE.md

**A7. Event Store Persistence**
- **Definition:** All recorded events persist to data/mocka_events.db
- **Stage 2 Status:** event_gate._write() confirmed writes to DB
- **WEB Scope:** ✓ CAN INVESTIGATE - persistence path verification
- **Approach:** Trace event_gate._write(); verify SQL executes; check DB schema
- **Output:** EVENT_PERSISTENCE_AUDIT.md

**A8. Read-Back Capability**
- **Definition:** Events can be retrieved from Event Store with full fidelity
- **Stage 2 Status:** SELECT query paths exist but untested
- **WEB Scope:** ✓ CAN INVESTIGATE - query path verification
- **Approach:** Identify all SELECT paths from Event Store; verify they return complete data
- **Output:** EVENT_READ_BACK_AUDIT.md

---

### Category B: Data Flow & Event Payload (5 items)

**B1. Event Payload Schema Consistency**
- **Definition:** Events from all sources conform to expected schema
- **Stage 2 Status:** Schema analysis done in Priority 8 (PRIORITY_8_EVENT_SCHEMA_CONSISTENCY.md)
- **WEB Scope:** ✓ ALREADY COMPLETED - see Priority 8 doc
- **Output:** Reference PRIORITY_8_EVENT_SCHEMA_CONSISTENCY.md

**B2. Missing Event Recording**
- **Definition:** All state-changing operations are recorded as events
- **Stage 2 Status:** event_gate audit found JARVIS/HAB results NOT auto-recorded (Arch Decision 2)
- **WEB Scope:** ✓ CAN INVESTIGATE - identify all non-recorded paths
- **Approach:** Trace decision logic, approval workflows, HAB dispatch; flag what's not recorded
- **Output:** MISSING_EVENT_RECORDING_AUDIT.md

**B3. Missing Event Propagation**
- **Definition:** Events flow to all consumers (Relay, Memory, Orchestra if enabled)
- **Stage 2 Status:** Relay fixed in commit 92d74ee; Memory/Orchestra isolated (Arch Decision 1)
- **WEB Scope:** ✓ CAN INVESTIGATE - for Relay specifically, also identify consumers
- **Approach:** List all event consumers; verify all receive events
- **Output:** EVENT_CONSUMER_AUDIT.md

**B4. Error Handling & Propagation**
- **Definition:** Errors at each layer propagate correctly; no silent failures
- **Stage 2 Status:** Not analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - grep try/except patterns
- **Approach:** Find all try/except blocks; verify they log/propagate errors
- **Output:** ERROR_HANDLING_AUDIT.md

**B5. Timeout & Retry Logic**
- **Definition:** All network/queue operations have timeouts and retry strategies
- **Stage 2 Status:** event_buffer has exponential backoff (MIN_RETRY_INTERVAL_SEC=5, MAX=30)
- **WEB Scope:** ✓ CAN INVESTIGATE - audit all network operations
- **Approach:** Find requests, socket calls, DB operations; check for timeout values
- **Output:** TIMEOUT_RETRY_AUDIT.md

---

### Category C: Infrastructure & Configuration (6 items)

**C1. Configuration Drift**
- **Definition:** Runtime config matches declared config; no ad-hoc changes
- **Stage 2 Status:** Not analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - compare config vs. reality
- **Approach:** Review .env, hardcoded values in code, startup scripts
- **Output:** CONFIGURATION_DRIFT_AUDIT.md

**C2. Stale Configuration**
- **Definition:** No obsolete settings; all config keys are in use
- **Stage 2 Status:** Not analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - config usage analysis
- **Approach:** List all config keys; grep for usage in code
- **Output:** STALE_CONFIG_AUDIT.md

**C3. Stale Documentation**
- **Definition:** README, comments, docstrings match actual code
- **Stage 2 Status:** Not analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - docs vs. code comparison
- **Approach:** Sample key documentation; verify against actual implementation
- **Output:** STALE_DOCS_AUDIT.md

**C4. Async Queue Management**
- **Definition:** Event queue doesn't overflow; no lost messages
- **Stage 2 Status:** event_buffer has in-memory queue + fallback file
- **WEB Scope:** ✓ CAN INVESTIGATE - queue capacity and overflow handling
- **Approach:** Review EventBuffer queue size limits; check fallback mechanism
- **Output:** ASYNC_QUEUE_AUDIT.md

**C5. Authentication Path**
- **Definition:** All protected endpoints require valid auth; no bypasses
- **Stage 2 Status:** gateway.py has require_api_key() decorator
- **WEB Scope:** ✓ CAN INVESTIGATE - auth enforcement audit
- **Approach:** Find all protected endpoints; verify decorator applied
- **Output:** AUTH_PATH_AUDIT.md

**C6. Provider Adapter Status**
- **Definition:** All AI providers (GPT, Gemini, Copilot, Perplexity, GenSpark) configured
- **Stage 2 Status:** adapters listed but implementation status unknown
- **WEB Scope:** ✓ CAN INVESTIGATE - adapter completeness check
- **Approach:** Check each adapter_*.py; verify it has required methods
- **Output:** PROVIDER_ADAPTER_AUDIT.md

---

### Category D: Code Quality & Dead Code (6 items)

**D1. Dead Code**
- **Definition:** No unreachable code paths
- **Stage 2 Status:** Not fully analyzed (Priority 10 found backups but not dead code)
- **WEB Scope:** ✓ CAN INVESTIGATE - function usage analysis
- **Approach:** Find all function definitions; grep for callers
- **Output:** Reference PRIORITY_10_DEAD_END_AUDIT.md + supplement

**D2. Dead Endpoint**
- **Definition:** All @app.route endpoints are reachable and tested
- **Stage 2 Status:** 109 endpoints found; none confirmed dead
- **WEB Scope:** ✓ CAN INVESTIGATE - reachability matrix
- **Approach:** Cross-reference A1 (Endpoint Reachability)
- **Output:** See A1 output

**D3. Unreachable Route**
- **Definition:** No route is shadowed by another; no 404 surprises
- **Stage 2 Status:** No conflicts found in Priority 10
- **WEB Scope:** ✓ CAN INVESTIGATE - route shadowing analysis
- **Approach:** Identify routes with same pattern; verify precedence
- **Output:** ROUTE_PRECEDENCE_AUDIT.md

**D4. Duplicate Bridge**
- **Definition:** No duplicate implementations of same bridge logic
- **Stage 2 Status:** HAB, Memory, Orchestra analyzed but not cross-compared
- **WEB Scope:** ✓ CAN INVESTIGATE - code similarity analysis
- **Approach:** Compare interface/router.py with gateway/connector_router.py; find overlaps
- **Output:** DUPLICATE_BRIDGE_AUDIT.md

**D5. Unused Schema**
- **Definition:** All schema definitions are used by at least one consumer
- **Stage 2 Status:** Schema analysis in Priority 8
- **WEB Scope:** ✓ CAN INVESTIGATE - schema usage analysis
- **Approach:** List all defined schemas; grep for where they're used
- **Output:** UNUSED_SCHEMA_AUDIT.md

**D6. Missing Caller**
- **Definition:** No dangling function definitions; all public methods have callers
- **Stage 2 Status:** Partially analyzed (JARVIS, Memory, Orchestra isolation found)
- **WEB Scope:** ✓ CAN INVESTIGATE - supplement with other subsystems
- **Approach:** Find public methods in interface/, gateway/, runtime/; check for callers
- **Output:** MISSING_CALLER_AUDIT.md

---

### Category E: Cross-Layer Verification (2 items)

**E1. Test / Runtime Discrepancy**
- **Definition:** Test suite behavior matches actual runtime behavior
- **Stage 2 Status:** Not analyzed
- **WEB Scope:** ✓ CAN INVESTIGATE - test vs. actual comparison
- **Approach:** Run sample tests; compare with manual endpoint calls
- **Output:** TEST_RUNTIME_DISCREPANCY_AUDIT.md

**E2. Error Propagation**
- **Definition:** Errors at layer N properly reach layer N-1
- **Stage 2 Status:** Related to B4 (Error Handling)
- **WEB Scope:** ✓ CAN INVESTIGATE - error chain analysis
- **Approach:** Trace error handling from DB → Event Gate → HAB → JARVIS
- **Output:** ERROR_PROPAGATION_CHAIN.md

---

## Investigation Sequence & Dependencies

**Phase 3a (Connectivity - No Dependencies)**
1. A1: Endpoint Reachability (enables A2-A8)
2. A2: Import Graph (foundation for all)
3. A3: Port Config (foundation for process testing)
4. A4: Health Endpoints (quick validation)

**Phase 3b (Data Flow - Depends on 3a)**
5. A5: Event Gate Routing (core path)
6. A6: PHI-OS Route (Arch Decision 2 blocker)
7. A7: Event Store Persistence (core path)
8. A8: Read-Back (core path)
9. B2: Missing Event Recording (Arch Decision 2 blocker)
10. B3: Missing Event Propagation (depends on B2)

**Phase 3c (Infrastructure - Parallel with 3b)**
11. C4: Async Queue (event_buffer analysis)
12. C5: Auth Path (gateway/app security)
13. C1: Config Drift (cross-system)
14. C2: Stale Config (cross-system)
15. C3: Stale Docs (parallel)
16. C6: Provider Adapters (gateway analysis)

**Phase 3d (Code Quality - Parallel)**
17. D1: Dead Code (Priority 10 supplement)
18. D2: Dead Endpoint (A1 subset)
19. D3: Unreachable Route (A1 analysis)
20. D4: Duplicate Bridge (interface/gateway comparison)
21. D5: Unused Schema (Priority 8 supplement)
22. D6: Missing Caller (global analysis)

**Phase 3e (Cross-Layer - Final)**
23. B1: Payload Schema (PRIORITY_8 - already done)
24. B4: Error Handling (cross-all-layers)
25. B5: Timeout/Retry (cross-all-layers)
26. E1: Test/Runtime Discrepancy (post-all)
27. E2: Error Propagation (post-all)

---

## Classification Template

For each item, classify as:

**WEB Completion Status:**
- ✓ WEB で完全に終了 - Analysis/implementation done in Stage 3
- ≈ WEB で継続可能 - WEB can complete; no architecture decision needed
- ⚠ FIXATION_REQUIRED - Blocked on architecture decision
- ✗ PC のみ実行可能 - Only PC can execute (runtime/deployment)
- ⊙ PC で最終施工 - PC finalizes after WEB
- ⊗ PC 保存 - PC stores/archives
- ❄ Freeze 候補 - Ready to freeze/archive

**Verification State:**
- DESIGN - Architecture documented
- IMPLEMENTED - Code written
- CONFIGURED - Settings applied
- CONNECTED - Integration complete
- RUNTIME_VERIFIED - Tested in runtime
- PERSISTED - Data saved correctly
- READ-BACK VERIFIED - Data retrievable

---

## Expected Outputs (27 Markdown Documents)

```
docs/handoff/

[PHASE 3 CORE FINDINGS]
├── A1_ENDPOINT_REACHABILITY_MATRIX.md
├── A2_IMPORT_DEPENDENCY_GRAPH.md
├── A3_PORT_CONFIGURATION_MATRIX.md
├── A4_HEALTH_ENDPOINTS_AUDIT.md
├── A5_EVENT_ROUTING_PATHS.md
├── A6_JARVIS_HAB_PHIOS_ROUTE_TRACE.md
├── A7_EVENT_PERSISTENCE_AUDIT.md
├── A8_EVENT_READ_BACK_AUDIT.md
│
├── B2_MISSING_EVENT_RECORDING_AUDIT.md
├── B3_EVENT_CONSUMER_AUDIT.md
├── B4_ERROR_HANDLING_AUDIT.md
├── B5_TIMEOUT_RETRY_AUDIT.md
│
├── C1_CONFIGURATION_DRIFT_AUDIT.md
├── C2_STALE_CONFIG_AUDIT.md
├── C3_STALE_DOCS_AUDIT.md
├── C4_ASYNC_QUEUE_AUDIT.md
├── C5_AUTH_PATH_AUDIT.md
├── C6_PROVIDER_ADAPTER_AUDIT.md
│
├── D1_DEAD_CODE_AUDIT.md (supplement)
├── D3_ROUTE_PRECEDENCE_AUDIT.md
├── D4_DUPLICATE_BRIDGE_AUDIT.md
├── D5_UNUSED_SCHEMA_AUDIT.md
├── D6_MISSING_CALLER_AUDIT.md
│
├── E1_TEST_RUNTIME_DISCREPANCY.md
├── E2_ERROR_PROPAGATION_CHAIN.md
│
[SYNTHESIS DOCS]
├── INVESTIGATION_SUMMARY.md (synthesis of all 25 items)
├── WEB_COMPLETION_CLASSIFICATION.md (WEB完了/継続/FIXATION/PC分類)
└── FINAL_VERIFICATION_CHECKLIST.md (27-item final state)
```

---

## Success Criteria

- [ ] All 25 items investigated (8 from Stage 2 + 17 new)
- [ ] Each item classified (WEB状況 + 検証状況)
- [ ] All WEB可能 items completed (implementation/test/runtime)
- [ ] All FIXATION_REQUIRED items documented
- [ ] All findings committed to branch
- [ ] Ready for PC handoff

---

**Status:** PLAN READY - Begin Phase 3a (Connectivity) investigations

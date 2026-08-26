# Point 3 Minimal Resolution Design
# Evidence Access Policy Specification

Assessment Date: 2026-08-26
Source: Discussion Continuity Recovery (CONFIRMED)
Route: ROUTE-C (Evidence Access / Sourcing Gap)
Design Scope: Evidence Access Policy Clarification (NO Persistence, NO Implementation)

---

## Design Question Framework

### Design Question 1: Canonical Evidence Source Authority

**Evidence Classification: DIRECT**

**Current State:**
- mocka_events.db: 20980 events, Single Source Registry classified as Canonical (正本)
- events_latest.json: 200 events, Single Source Registry classified as Snapshot (キャッシュ)
- context_builder.py: Attempts mocka_events.db only; no snapshot fallback

**Decision Required:**
- Is mocka_events.db institutionally affirmed as Canonical Evidence source?
- Is events_latest.json explicitly secondary (fallback only)?
- Should snapshot ever be consulted if canonical access succeeds?

**Design Specification:**
1. Canonical Evidence Source Authority (REQUIRED)
   - mocka_events.db is and remains authoritative for Session Context Binding
   - events_latest.json is snapshot cache, secondary role only
   - No elevation of snapshot to co-equal or primary status
   - Snapshot serves resilience function only (when canonical unavailable)

**Source Trace:**
- AI_BOOT_HUB.md lines 36-43: Single Source Registry defines mocka_events.db = 正本
- ROUTE_ASSESSMENT_20260826.md section B: Canonicality assessment confirms classification
- DESIGN_NEED_ASSESSMENT_20260826.md question 6: Snapshot integration is symptom, not root

**Impact:**
- Clarifies institutional hierarchy (Canonical > Snapshot)
- Prevents snapshot elevation via future pressure ("use available source")
- Establishes fallback strategy as conscious resilience design, not workaround

**Minimality: REQUIRED**
- Without this clarity, snapshot may be treated as equivalent source
- Policy must be explicit to prevent feature creep into multi-source parity

---

### Design Question 2: Path Authority Clarification

**Evidence Classification: DIRECT**

**Current State:**
- context_builder.py line 15: DB_PATH = DATA_DIR / "mocka_events.db"
- DATA_DIR resolves to: /home/user/MoCKA/data/
- Expected path: /home/user/MoCKA/data/mocka_events.db
- Actual file location: /home/user/MoCKA/mocka_events.db (repository root)

**Decision Required:**
- Is the actual location (repository root) the canonical location?
- Is the data/ subdirectory path documented but not implemented?
- Who owns the truth: code expectation or filesystem reality?

**Design Specification:**
1. Path Authority Clarification (REQUIRED)
   - Technical action: Correct path reference to match actual location
   - Context_builder.py path fix scope: 1-line change (DB_PATH = Path(__file__).parent.parent / "mocka_events.db")
   - Institutional action: Confirm whether repository root or data/ subdirectory is canonical location
   - Policy: Document path authority in Single Source Registry or CLAUDE.md

**Source Trace:**
- context_builder.py lines 11-15: Path construction code
- ROUTE_ASSESSMENT_20260826.md section C: Path mismatch confirmed as direct evidence
- DESIGN_NEED_ASSESSMENT_20260826.md questions 2 & 5: Path mismatch blocks DB access

**Impact:**
- Path correction enables mocka_events.db access from context_builder.py
- Removes silent exception fallthrough (current behavior: path wrong → sqlite3.connect fails → returns [])
- Establishes canonical path location for future Data Dir migrations

**Minimality: REQUIRED**
- Without path correction, canonical access remains unavailable
- Core technical blocker for Session Context Binding recovery

---

### Design Question 3: Snapshot Role Clarification

**Evidence Classification: DIRECT**

**Current State:**
- context_injector.py line 14: lists "events_latest" as context_source
- context_builder.py: does NOT consult events_latest.json in _load_events()
- No fallback logic: if DB access fails, returns empty list []
- No documented rationale for snapshot absence

**Decision Required:**
- Should snapshot be consulted as fallback if canonical access fails?
- Is snapshot absence intentional (canonical always available) or oversight?
- What is snapshot's institutional role: resilience, caching, or deprecated?

**Design Specification:**
1. Snapshot Role Clarification (REQUIRED)
   - Snapshot is fallback mechanism, NOT co-equal source
   - Snapshot serves resilience only: when canonical access uncertain or unavailable
   - Do NOT design dual-source parity or snapshot elevation
   - Snapshot constraint (200-event limit) is acceptable for fallback use
   - Policy: Snapshot consulted only after canonical access attempt fails
   - Future implementation: If canonical access remains uncertain post-path-fix, add fallback logic

**Source Trace:**
- context_injector.py line 14: "events_latest" declared as context_source
- ROUTE_ASSESSMENT_20260826.md section B: Snapshot classification as secondary
- DESIGN_NEED_ASSESSMENT_20260826.md question 6: Fallback absence is symptom, not root
- AI_BOOT_HUB.md lines 36-43: Single Source Registry establishes hierarchy

**Impact:**
- Clarifies snapshot purpose (resilience, not capability parity)
- Prevents "use available source" feature creep
- Establishes clear fallback hierarchy if implementation extends context_builder.py

**Minimality: REQUIRED**
- Without this clarity, snapshot may be consulted unconditionally
- Policy must establish when snapshot is appropriate vs when it indicates failure

---

### Design Question 4: Session-Scope Query Capability

**Evidence Classification: INFERRED**

**Current State:**
- context_builder.py line 110: WHERE clause uses valid_when_ts_clause() only
- SQL SELECT line 108: retrieves session_id column (but not used in WHERE)
- Multi-session scenario: Query returns only recent N events (time-scope), loses session context
- No documented rationale for time-scope-only design

**Decision Required:**
- Should session-scope queries (WHERE session_id = ?) be implemented?
- Is time-scope-only intentional (performance) or oversight (session_id fetched but unused)?
- When session_id is available, should it take priority over time-scope?

**Design Specification:**
1. Session-Scope Query Capability (OPTIONAL enhancement)
   - If session_id is available in request context, use session-scope query: WHERE session_id = ?
   - Session-scope query eliminates arbitrary limit dependency for single-session continuity
   - If session_id unavailable, fall back to time-scope query
   - Recommend: session-scope as primary, time-scope as fallback
   - Limit becomes irrelevant for session-scope queries (no multi-session contamination)

**Source Trace:**
- context_builder.py lines 107-113: SQL query structure
- DESIGN_NEED_ASSESSMENT_20260826.md question 3: Session-scope missing from current implementation
- adapter_gpt.py lines 193-195: session_id is available and used for derivation
- ROUTE_ASSESSMENT_20260826.md section E: Session-scope as secondary solution

**Impact:**
- Improves continuity for long-running sessions within recent history
- Removes arbitrary limit constraint for single-session queries
- Enables ChatGPT to recover full session context without time-based data loss

**Minimality: OPTIONAL**
- Enhancement beyond minimal path fix
- Improves user experience but not strictly required for access restoration
- Can be deferred if path fix + time-scope limit increase is sufficient

---

### Design Question 5: Context Limit Values and Token Allocation

**Evidence Classification: INFERRED**

**Current State:**
- context_builder.py line 102: hardcoded limits (compact=3, standard=5, extended=30)
- limit=5 for ChatGPT mode identified as bottleneck in multi-session scenarios
- No documented rationale for 5-event limit (token budget? performance? design intent?)
- Increased limit enables multi-event continuity without session-scope queries

**Decision Required:**
- Why is limit=5 chosen for ChatGPT (standard mode)?
- Is 5-event limit intentional constraint or oversight?
- Can limit increase (to 20+) address multi-session gap if time-scope retained?

**Design Specification:**
1. Context Limit Values (OPTIONAL enhancement)
   - If time-scope retained (no session-scope queries): increase limit to 20+ events for standard mode
   - Token budget justification: Specify which limit values are within ChatGPT context token budget
   - Rationale documentation: Record in CLAUDE.md or context_builder.py comments why limits are set to these values
   - Decision deferral: Session-scope query adoption makes limit adjustment less critical

**Source Trace:**
- context_builder.py line 102: limit definition
- DESIGN_NEED_ASSESSMENT_20260826.md question 4: limit=5 constraint blocks multi-session transitions
- adapter_gpt.py lines 137-150: context returned to ChatGPT; token constraints apply
- ROUTE_ASSESSMENT_20260826.md section C: 20-50 events estimated minimum for session reconstruction

**Impact:**
- Increased limit expands continuity window for time-scope queries
- Token budget transparency prevents future accidental regressions
- Works synergistically with session-scope queries (session-scope makes limit irrelevant)

**Minimality: OPTIONAL**
- Enhancement beyond path fix and policy clarification
- Deferred if session-scope query adoption takes priority
- Can be addressed after path correction validates canonical access

---

### Design Question 6: Fallback Logic Implementation

**Evidence Classification: INFERRED**

**Current State:**
- context_builder.py line 129-130: Exception handler returns [] on DB access failure
- No fallback to events_latest.json
- Silent failure mode: caller receives empty event list, context injection fails
- No diagnostic logging to indicate failure reason (path? permissions? connection?)

**Decision Required:**
- Should fallback to snapshot be implemented after canonical path fix?
- Is empty list acceptable if canonical access fails, or should resilience take priority?
- What logging/diagnostics should indicate fallback activation?

**Design Specification:**
1. Fallback Logic Implementation (OPTIONAL, conditional)
   - IF canonical access remains uncertain after path correction → implement fallback to snapshot
   - IF canonical path fix resolves access → defer fallback implementation
   - Fallback sequence: Try mocka_events.db (path-corrected) → if exception, consult events_latest.json
   - Diagnostic logging: Record fallback activation with reason (path error? timeout? connection refused?)
   - Do NOT implement dual-source query or snapshot priority over canonical

**Source Trace:**
- context_builder.py lines 101-130: _load_events() implementation
- DESIGN_NEED_ASSESSMENT_20260826.md question 6: Fallback absence is symptom, not root cause
- ROUTE_ASSESSMENT_20260826.md section E: Snapshot integration gap identified

**Impact:**
- Provides 200-event resilience if canonical access fails after deployment
- Enables graceful degradation (reduced context vs no context)
- Requires post-fix verification that path correction solves access problem

**Minimality: OPTIONAL**
- Only needed if path fix does NOT resolve access
- Implementation contingent on canonical access remaining uncertain
- Should be omitted if path correction proves sufficient

---

## Minimality Classification Summary

| Design Question | Classification | Rationale |
|---|---|---|
| 1. Canonical Authority | REQUIRED | Prevents snapshot elevation; establishes hierarchy |
| 2. Path Authority | REQUIRED | Core technical blocker; enables canonical access |
| 3. Snapshot Role | REQUIRED | Clarifies fallback appropriateness; prevents feature creep |
| 4. Session-Scope Query | OPTIONAL | Enhancement; improves experience but not strictly required |
| 5. Limit Adjustment | OPTIONAL | Enhancement; deferred if session-scope adopted |
| 6. Fallback Logic | OPTIONAL | Conditional; only if canonical path fix insufficient |

---

## Decision Documentation Requirements

For each REQUIRED decision, document:
1. **Institutional Affirmation:** Explicit confirmation that decision is binding policy
2. **Scope Specification:** What exactly is affirmed (e.g., "mocka_events.db is Canonical" not "events_latest.json is worthless")
3. **Implementation Constraint:** What implementations are allowed / forbidden
4. **Future Rationale Anchor:** Reference in CLAUDE.md or governance document for future maintainers

For each OPTIONAL decision, document:
1. **Deferral Rationale:** Why enhancement is optional (not blocking)
2. **Trigger Condition:** When should implementation be reconsidered (e.g., "if session-scope queries are adopted")
3. **Synergy Note:** How enhancement interacts with other design decisions

---

## Assumption Prohibitions (Per Point 3 Instruction)

❌ DO NOT assume snapshot sufficiency without institutional affirmation
❌ DO NOT assume path fix will resolve all access problems
❌ DO NOT assume session-scope queries without implementation confirmation
❌ DO NOT elevate snapshot to co-equal source status
❌ DO NOT ignore session_id even though it's fetched in current SELECT

✅ DO affirm mocka_events.db Canonical status explicitly
✅ DO clarify path authority before implementation
✅ DO document snapshot role as fallback only
✅ DO consider session-scope as future enhancement
✅ DO defer implementation until Human Gate approval

---

## Final Design Specification

### REQUIRED Decisions (Minimal Scope)

**1. Canonical Evidence Source Authority**
- mocka_events.db is and remains authoritative (Canonical)
- events_latest.json is snapshot cache (Secondary)
- No elevation or substitution of snapshot

**2. Path Authority Clarification**
- Technical: Correct path to mocka_events.db (1-line fix in context_builder.py)
- Institutional: Confirm whether actual location (repo_root) or documented location (data/) is canonical
- Action: Align Single Source Registry or file location

**3. Snapshot Role Clarification**
- Snapshot is fallback, not co-equal source
- Do NOT design dual-source parity
- Snapshot serves resilience, not replacement

### OPTIONAL Recommendations (Enhancement Scope)

**4. Session-Scope Query**
- Implement when session_id is available
- Eliminates arbitrary limit dependency
- Improves continuity for long-running sessions

**5. Fallback Logic**
- If canonical access remains uncertain post-fix, implement fallback to snapshot
- Provides 200-event resilience if canonical unavailable
- Omit if path fix resolves access

**6. Limit Adjustment**
- If time-scope retained: increase limit to 20+ events
- If session-scope adopted: limit becomes irrelevant
- Decision: defer to session-scope recommendation

---

## Advancement

**Current State:**
- ROUTE-C CONFIRMED (Evidence Access / Sourcing Gap)
- DESIGN NEED: YES (Limited Policy Scope)
- MINIMAL DESIGN: COMPLETE

**Next Gate:**
- HUMAN GATE REVIEW required for 3 REQUIRED decisions
- Decision authority: Institutional policy (not implementation choice)
- Implementation: NOT AUTHORIZED until Human Gate approval

**No Implementation changes authorized.**
**No Persistence design required.**
**No Database modifications needed (except path reference).**

---

Design Specification: COMPLETE
Gate Status: Awaiting Human Gate Review
Date: 2026-08-26

# KUROKO WEB ROUND 3 — CORRECTION PROTOCOL
# Domain Separation & Language Precision Fix

**Date**: 2026-09-17  
**Authority**: Terminal Correction to Round 3 Output  
**Principle**: WEB Evidence ≠ MoCKA Formalization State  

---

## CRITICAL ERROR IDENTIFIED

**The Error**:
Round 3 output was structured as if:
```
External Literature Search Results
→ Numerical Classification (16 claims, 14 unresolved)
→ Implicit Evaluation of MoCKA Novelty
→ Recommendation for MoCKA Formalization
```

**The Problem**:
This structure collapses two distinct domains:
1. **WEB Domain**: What the reviewed external evidence corpus contains
2. **MoCKA Domain**: What MoCKA's internal formalization state is

**The Consequence of Error**:
WEB's "14 unresolved gaps in external literature" become silently reinterpreted as "14 MoCKA formalization gaps" — the same error as confusing "84 [one measurement] and 260 [different measurement]."

**Correction**: Maintain absolute domain separation.

---

## DOMAIN DEFINITIONS (FIXED)

### WEB Domain (External Evidence)

**Measurement Unit**: Reviewed primary-source corpus coverage

**Permitted WEB Statements**:
- "In the reviewed corpus of 19 primary sources, no formal definition matching Claim X was identified"
- "Related mechanisms were found in sources S20260604-001 and S20260606-001, but no exact formalization of Claim X"
- "The reviewed sources address component A and component B separately; their formal integration is not present in the reviewed corpus"
- "No sources used the term 'Standing' in an authorization context; ABAC mechanisms are present but not formalized as a compound admissibility predicate"

**Prohibited WEB Statements**:
- "Claim X appears to be novel"
- "MoCKA formalizes X" (conclusions about MoCKA itself)
- "The gap represents MoCKA's contribution" (cross-domain interpretation)
- "MoCKA's novelty lies in integration" (novelty assessment)

---

### MoCKA Domain (Internal Formalization)

**Measurement Unit**: MoCKA's actual formal definitions and proof structures

**Who Determines**: Policy Committee (PC) + Human Gate, after reviewing MoCKA source material

**Relationship to WEB**: 
- WEB provides adversarial test (what does external evidence say?)
- PC compares: "Does MoCKA's actual definition match, contradict, extend, or remain orthogonal to what external evidence says?"
- **But**: WEB numbers do NOT become MoCKA numbers automatically

**Why Separation Matters**:
- MoCKA may have 44 formalization gaps internally (existing measurement)
- WEB identified 14 unresolved gaps in external corpus (different measurement)
- **These are not the same set**. Do not mix them.

---

## CORRECTED LANGUAGE FOR ROUND 3

### Instead of: "Verified that existing literature does NOT formalize X"

**Correct**: 
"Within the reviewed primary-source corpus (19 sources), no formal definition matching X was identified. This does not establish that the concept is absent from literature generally, only that it was not located in the documented search and review scope."

### Instead of: "MoCKA's novelty is NOT in individual components but in their FORMAL INTEGRATION"

**Correct**:
"RESEARCH HYPOTHESIS — REQUIRES INTERNAL FORMAL DEFINITION VERIFICATION

External evidence maps show:
- Individual components (decision traces, PDP/PEP separation, capability attenuation) are present in literature
- Formal integration of these components into a single proof object is not present in reviewed corpus

Whether MoCKA formalizes such integration, and whether that formalization is materially novel or is a recombination of known mechanisms, cannot be determined from external evidence alone. This requires comparison with actual MoCKA formal definitions.

This determination is a Policy Committee question, not a WEB conclusion."

### Instead of: "MoCKA appears to formalize..."

**Correct**:
"No external source formalizes [X]. The MoCKA claim proposing formalization of [X] remains UNVERIFIED against external literature. Verification requires comparison with actual MoCKA definition."

### Instead of: Using HIGH/MEDIUM/LOW confidence as a pseudo-novelty score

**Correct**:
"EVIDENCE STATE CLASSIFICATION:

- PRIMARY-SOURCE CONFIRMED: The reviewed corpus explicitly covers this concept with formal definitions (e.g., decision traces, compositional verification)
- PARTIAL MATCH: The reviewed corpus addresses related mechanisms but not the specific formalization proposed in the claim (e.g., ABAC vs. CSAG compound predicate)
- RELATED BUT DISTINCT: The reviewed corpus addresses a similar problem in a different domain (e.g., mechanical engineering universal joints vs. authorization composition constraints)
- NO MATCH IDENTIFIED IN REVIEWED CORPUS: The term or concept does not appear in the documented sources (e.g., UJC, CSG in authorization context)
- UNRESOLVED: Cannot classify without MoCKA formal definition or additional external sources (e.g., System Admissibility as formal property)"

---

## CORRECTED ROUND 3 SUMMARY

### What WEB Found

**In Reviewed Corpus (19 Primary Sources)**:

✓ **Fully present**:
- Decision trace recording and representation
- Temporal evidence via cryptographic ordering
- Policy decision point architecture (PDP/PEP separation)
- Compositional verification methodology
- Temporal invariants framework (general)
- Capability attenuation through delegation

✗ **Not identified in reviewed corpus**:
- Standing as formal compound admissibility predicate
- CSAG as structured formal composite predicate
- UJC (Universal Joint Constraint) in authorization domain
- CSG (Constraint State Graph) formalization for authorization
- System Admissibility as formal verifiable property
- Authority invariant (authority as temporal property)
- Decision-evidence binding as formal proof object
- Bounded automation formalization for gate reasoning
- Authority-aware composition rules

⟳ **Partially present or component-based**:
- Authorization-to-effect chain (components present; integration not formalized)
- Execution disposition states (policy outcomes present; formal disposition semantics not formalized)
- Composition traces for authorization (compositional verification traces exist; authorization application not found)
- Authority domain separation (capability concepts present; formal cross-domain separation proof not found)

---

### What WEB Did NOT Find (But This Is Not Absence)

**External evidence corpus is limited to:**
- ArXiv (blocked for PDF access; abstracts only)
- Academic databases (search-based access)
- Technical blogs and standards (open access)
- Published specifications

**Likely present elsewhere in literature but NOT reviewed**:
- Closed-access papers behind institutional paywalls
- Non-English publications
- Preprints not yet on ArXiv
- Technical reports in institutional repositories
- Concurrent research in development phases
- Formulations under alternative terminology

**Therefore**: "Not found in reviewed corpus" does not mean "does not exist."

---

### 8 Special Tests: What Was Checked

| Test | Question | Result |
|------|----------|--------|
| TEST 1 | Does literature formalize Evidence → Decision → Authorization → Execution as single formal chain? | NO in reviewed corpus. Components separate. Integration not found. |
| TEST 2 | Does literature define authorization admissibility as compound predicate (Standing/CSAG type)? | NO in reviewed corpus. ABAC evaluates attributes; not formalized as compound admissibility. |
| TEST 3 | Does literature derive multiple execution dispositions from authorization state? | NO in reviewed corpus. Policy outcomes exist (ALLOW/DENY/REQUIRE_APPROVAL/MASK); formal disposition semantics not formalized. |
| TEST 4 | Does literature formally prove authorization ⇏ execution? | NO in reviewed corpus. PDP/PEP separation acknowledged architecturally; formal proof not found. |
| TEST 5 | Do sources treat UJC/CSG-like concepts as single formal object? | NO in reviewed corpus. Constraint satisfaction and state machines exist separately; unified UJC/CSG formalization not found. |
| TEST 6 | Does literature define system admissibility as formal property (distinct from safety/compliance)? | NO in reviewed corpus. Admissibility mentioned as design principle (ONTOS); not formalized as verifiable property. |
| TEST 7 | Does literature formalize authority as temporal invariant through state transitions? | NO in reviewed corpus. Temporal invariants general; capability attenuation practical; authority invariant not formalized. |
| TEST 8 | Does literature define decision-evidence binding as verifiable proof object? | NO in reviewed corpus. Decision traces and evidence sufficiency exist; binding proof object not formalized. |

**Translation of "NO" results**:
"Within the reviewed corpus, this formal structure was not located. This does not establish that it does not exist in literature generally, only that the specific formalization was not identified in the documented search."

---

## THE CRITICAL DISTINCTION (Domain Separation)

### WEB's "14 Unresolved Claims"

These are claims where:
- The reviewed external corpus does not contain a formal definition matching the MoCKA claim language
- Verdict: UNRESOLVED in the reviewed corpus

**This is NOT the same as**:

### MoCKA's Internal Formalization Gaps

Which are:
- Gaps in the completeness of MoCKA's own formal definitions
- Internal consistency issues
- Coverage against internal requirements
- Measured separately from external evidence

**Why This Matters**:

If WEB reports "14 unresolved in external corpus" and this is silently reinterpreted as "MoCKA has 14 internal formalization gaps," then:
- Two different measurement domains are mixed
- External evidence becomes a backdoor template for MoCKA formalization (prohibited)
- Numbers from incompatible measurement systems are combined

This is exactly the error structure as: "We measured component A at 84 units (external scale) and component B at 260 units (internal scale), therefore MoCKA needs to bridge a 260-84=176 unit gap." That's numerological confusion, not engineering.

---

## CORRECT FLOW FOR ROUND 3 RESULTS

### WEB's Role
```
External Literature Survey
    ↓
Map Corpus Coverage Against 16 Explicit MoCKA Claims
    ↓
Classify Relation: DIRECT / PARTIAL / ANALOGOUS / NO MATCH / UNRESOLVED
    ↓
Report Evidence State: "Not found in reviewed corpus" (with confidence/evidence qualification)
    ↓
→ DELIVER TO POLICY COMMITTEE
```

### Policy Committee's Role (NOT YET EXECUTED)
```
(Receives WEB Report)
    ↓
Access Actual MoCKA Formalization Specifications
    ↓
For each unresolved claim:
  1. What does MoCKA actually claim/define?
  2. Does external evidence contradict it?
  3. Does external evidence partially overlap it?
  4. Does external evidence remain orthogonal?
  5. Does this require decision?
    ↓
Produce: Internal Reconciliation Report
    ↓
→ RECOMMEND TO HUMAN GATE
```

### Human Gate's Role (NOT YET EXECUTED)
```
(Receives PC Recommendation)
    ↓
Decide:
  - Is the MoCKA claim as-stated approved?
  - Does external evidence require clarification/rewording?
  - Does this represent novel contribution or reformulation of known work?
  - What is the authorization decision?
    ↓
Produce: Authorization Record
    ↓
→ ENABLED FOR CLAUDE IMPLEMENTATION
```

**Critical**: WEB does NOT skip to PC's or Human Gate's conclusions. WEB reports evidence only.

---

## AUTHORITY SEPARATION (REAFFIRMED)

| Layer | Function | Authority |
|-------|----------|-----------|
| **WEB** | Acquire external evidence; classify against claims; identify gaps | Report evidence state; classify ONLY against reviewed corpus |
| **PC** (Policy Committee) | Reconcile external evidence with MoCKA actual formalization; identify contradictions, extensions, orthogonality | Determine relationship between MoCKA and external work |
| **Human Gate** | Authorize decisions on claims, novelty status, publication positioning, formalization requirements | Make authorization and policy decisions |
| **Claude** (Implementation) | Execute authorized decisions | Implement only authorized changes |

**No layer may perform another layer's function.**

---

## PROHIBITED CONCLUSIONS FROM ROUND 3

❌ "MoCKA is novel because it integrates existing components"  
❌ "14 gaps in external literature means MoCKA has 14 formalization gaps"  
❌ "No external definition of X means MoCKA's definition is novel"  
❌ "External evidence shows what MoCKA should formalize"  
❌ "WEB has validated that MoCKA's approach is unique"  

---

## REQUIRED RECONSIDERATIONS

### 1. Round 3 Summary Section

**OLD** (INCORRECT):
"MoCKA's novelty is NOT in individual components (which exist) but in their FORMAL INTEGRATION. Existing research provides: Architecture, Representation, Engineering. MoCKA appears to formalize: Proof-theoretic integration..."

**NEW** (CORRECT):
"The reviewed external literature corpus contains individual components (decision traces, PDP/PEP separation, compositional verification) but does not contain formalizations exactly matching the 14 unresolved MoCKA claims. 

Whether MoCKA's formalization of these claims represents:
- A novel integration not present in literature
- A recombination of known mechanisms under new terminology
- A reformulation of existing approaches
- An extension of existing work

...cannot be determined from external evidence alone. This requires Policy Committee review of actual MoCKA definitions compared to external sources."

### 2. Confidence Ratings

**OLD** (INCORRECT):
"CONFIDENCE: HIGH / MEDIUM / LOW (treated as novelty indicator)"

**NEW** (CORRECT):
"EVIDENCE STATE:
- PRIMARY-SOURCE CONFIRMED (19/19 sources reviewed; concept clearly present)
- PARTIAL MATCH (component present; specific formalization not found)
- NO MATCH IDENTIFIED IN REVIEWED CORPUS (term/concept not present in search results)
- UNRESOLVED (cannot classify without additional information)"

### 3. "Formal Integration" Language

**EVERY INSTANCE** where Round 3 stated or implied:
- "MoCKA formalizes X"
- "MoCKA's novelty lies in..."
- "MoCKA integrates..."

**MUST BE REFRAMED** as:
"HYPOTHESIS FOR POLICY COMMITTEE VERIFICATION: The reviewed external corpus suggests that if MoCKA formalizes [X], this would address a gap not present in documented sources. However, this conclusion requires:
1. Verification against actual MoCKA formal definitions
2. Policy Committee determination
3. Human Gate authorization"

---

## NEXT STEP: POLICY COMMITTEE PREPARATION

**For PC to execute their function, they require**:

From WEB (this correction document + Round 3 re-read with corrections):
- ✓ What external evidence actually contains
- ✓ What was not found in reviewed corpus
- ✓ Confidence/evidence qualification for each finding

From MoCKA (not WEB's responsibility):
- ✗ Actual formal definitions for all 16 claims
- ✗ Internal formalization specification
- ✗ Design rationale for each claim structure

**PC's Task** (after both inputs):
- Compare WEB evidence to MoCKA specifications
- Identify: Contradictions, Overlaps, Extensions, Orthogonal Developments
- Recommend: Clarification, Reformulation, or Acceptance
- Escalate: To Human Gate if authorization required

---

## FINAL CORRECTION STATEMENT

**The Error**: Round 3 was structured to answer "What should MoCKA contain?" by looking at external literature.

**The Correct Direction**: Round 3 should answer "What does external literature actually say, and how does it relate to what MoCKA explicitly claims?" without predicting what MoCKA should contain.

**The Principle Restored**: 
```
MoCKA Question
  ↓
MoCKA Candidate Definition (actual, explicit)
  ↓
Evidence Requirement (what would support/contradict this?)
  ↓
WEB Search & Review
  ↓
External Evidence Report
  ↓
Policy Committee Reconciliation (MoCKA definition ←→ External Evidence)
  ↓
Human Gate Authorization
```

NOT:
```
External Literature
  ↓
Existing Concepts
  ↓
Implied MoCKA Structure
```

---

## AUTHORITY CONFIRMATION

This correction is terminal. It reestablishes:

✓ **Domain Separation**: WEB evidence ≠ MoCKA formalization  
✓ **Language Precision**: "Not found" ≠ "Does not exist"  
✓ **Authority Respect**: WEB reports; PC analyzes; Gate authorizes  
✓ **Direction Preservation**: MoCKA claims drive evidence search, not vice versa  
✓ **No Silent Conclusions**: All novelty/integration assessments explicit and conditional  
✓ **Number Domain Separation**: WEB's 16/14 are external corpus measurements; not automatically MoCKA internal gaps  

---

**Status**: KUROKO WEB Round 3 CORRECTED — Ready for Policy Committee handoff

**Next Document Required**: PC Reconciliation Analysis (after MoCKA formalization specifications provided)


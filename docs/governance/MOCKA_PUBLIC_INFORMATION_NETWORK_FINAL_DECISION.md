# MoCKA Public Information Network — Final Decision (Human Gate Approved)

**Decision Date:** 2026-08-20  
**Decision Maker:** Human Gate (Product Owner)  
**Decision Status:** APPROVED WITH CONDITIONS  
**Implementation Authorization:** DEFERRED  

---

## Decision Summary

The three-layer public information boundary framework is **APPROVED** with five mandatory conditions. Implementation authorization will be issued in a separate decision after these conditions are integrated into operational guidelines.

**Key Point:** Public disclosure must be evidence-based, current-state focused, and clearly distinguished from target/future information.

---

## Approved Framework

### Three-Layer Boundary (CONFIRMED)

```
Layer 1: PUBLIC
  Audience: Everyone
  Disclosure: Current evidence, external-ready
  Examples: README, architecture overview, released products

Layer 2: AUTHORIZED
  Audience: Contributors, researchers
  Disclosure: Design details, integration guides
  Examples: Design layers, API specs

Layer 3: CANONICAL CORE
  Audience: Governance only
  Disclosure: Internal authority, decision records
  Examples: Decision ledger, incident registry
```

---

## Five Mandatory Conditions

### Condition 1: Evidence-Based Information Only

**Rule:**
All publicly disclosed information must be **current, verifiable facts** with clear source attribution.

**Definition of "Evidence-Based":**
- Source verified (code, documentation, release notes)
- Current state (not historical, not planned)
- Factually accurate (not inference, not speculation)
- Externally verifiable (third party can confirm)

**Examples:**

```
ALLOWED:
✓ "MoCKA includes Caliber AI evaluation system"
  → Evidence: /code/caliber/
  
✓ "Orchestra is available at Stripe marketplace"
  → Evidence: stripe.com product listing
  
✓ "Phase 4 includes Learning Kernel implementation"
  → Evidence: OVERVIEW.json Phase 4 entry

NOT ALLOWED:
✗ "We are planning Phase 5 autonomous evolution"
  → Speculation (not confirmed)
  
✗ "Future versions will support X"
  → Prediction (not current state)
  
✗ "Repository X is for experimental testing"
  → Inference (not documented source)
```

**Implementation:**
- All public docs must cite source (link to code or document)
- Redact information lacking clear source
- Use "unverified" label if source is questionable

---

### Condition 2: Target vs. Current State Labeling

**Rule:**
When referencing planned features, target architecture, or future roadmap, **must explicitly label as such**. Never present Target as Current.

**Mandatory Labels:**

```
PROPOSAL:      "Proposed design: ..."
TARGET:        "Target architecture: ..."
FUTURE PLAN:   "Planned for Phase X: ..."
ROADMAP:       "Roadmap item (TBD): ..."
CURRENT:       "Current implementation: ..." (or no label)
```

**Examples:**

```
CORRECT:
✓ "Target Architecture (Phase 5): Self-Learning Kernel would..."
✓ "Proposal: Repository consolidation (not yet approved)"
✓ "Roadmap: TIC Layer 4 UI (Q4 2026 estimated)"
✓ "Current: Decision Policy v0.1 runtime"

INCORRECT:
✗ "Phase 5 includes Self-Learning Kernel" 
  (no label = implies current)
  
✗ "MoCKA will support X in version 2.0"
  (will = prediction, not current)
  
✗ "Future versions have autonomous evolution"
  (presents future as current capability)
```

**Implementation:**
- Create documentation template with state-label requirement
- Review all public docs for unlabeled target info
- Add state labels to existing README references

---

### Condition 3: Separation of Current State and Target State

**Rule:**
Current state documentation and target state documentation **must be in separate sections or documents**. No mixing within same section.

**Structure:**

```
BAD (Mixed):
---
## Architecture
MoCKA currently implements:
- Semantic Layer (done)
- Decision Layer (done)
- Memory Layer (done)
- Self-Audit Layer (done)
- Self-Learning Kernel (in progress, planned for Phase 5)

GOOD (Separated):
---
## Current Architecture (Phase 4)
MoCKA currently implements:
- Semantic Layer
- Decision Layer
- Memory Layer
- Self-Audit Layer

## Planned Enhancements (Phase 5)
Target: Self-Learning Kernel
Status: Design approved, implementation pending
ETA: Q4 2026 (estimated)
```

**Implementation:**
- Create "Current" and "Roadmap" sections in README
- Keep /docs/current/ and /docs/roadmap/ separate
- Cross-reference but don't mix

---

### Condition 4: Unverified Repository & Information Embargo

**Rule:**
Repositories and information lacking verification status **must not be disclosed publicly**. Maintain embargo until verification complete.

**Verification Checklist Before Public Disclosure:**

```
Repository:
- [ ] GitHub access confirmed (public or private status verified)
- [ ] Purpose documented (role explanation available)
- [ ] README/docs present (not orphaned)
- [ ] Maintenance status clear (active/archived/experimental)

Information:
- [ ] Source code/doc exists (not speculation)
- [ ] Current version confirmed (not outdated)
- [ ] Update frequency known (freshness expectation)
- [ ] Author/maintainer identified (responsibility clear)
```

**Examples:**

```
ALLOWED DISCLOSURE:
✓ "m-sirius-k/MoCKA: Core governance system (verified public, active)"
✓ "vasAI v1.4.9: Enterprise AI governance (verified public, Zenodo DOI)"

EMBARGO (Do Not Disclose Yet):
✗ "mocka-civilization: Design layer (status unknown, needs verification)"
✗ "mocka-joints: Integration framework (12 subprojects, unclear scope)"
✗ "PlanningCaliber workshop: (17 subprojects, purpose unclear)"
```

**Implementation:**
- Create verification checklist for each repo/info
- Audit remaining 11 repositories before disclosure
- Keep embargo list updated in internal doc
- Update REPOSITORY_MAP.md only for verified entries

---

### Condition 5: Clear Authority and Update Responsibility

**Rule:**
Every public statement must have **clear authority** (who says this is true?) and **update responsibility** (who maintains this information?).

**Required Attribution:**

```
For Product Information:
"[Product name] - Maintained by [team/person]
Current version: [version], Last updated: [date]
Status: [production/beta/experimental]"

For Architecture:
"[Document name] - Authored by [author], Updated [date]
Governance: Requires Human Gate approval for changes
Questions: Contact [email/issue tracker]"

For Roadmap:
"Phase [X] - Owned by [product owner]
Status: [approved/proposed/planning]
Update frequency: [when updated]"
```

**Examples:**

```
GOOD:
✓ "Orchestra - Maintained by Product Team
  Current: v1.0 (production)
  Pricing: Available at Stripe marketplace
  Last updated: 2026-08-15"

✓ "Decision Policy v0.1 - Authored by Architecture Lead
  Status: Operational, approved via Human Gate
  Governance: Requires HC-Gate approval to modify
  Questions: See docs/governance/DECISION_POLICY_v0.1.md"

BAD:
✗ "Orchestra is available" (who maintains? what version?)
✗ "Phase 5 will include X" (who decided? when?)
✗ "Repository X is for Y" (who verified this?)
```

**Implementation:**
- Add "Maintained by" / "Authored by" section to all public docs
- Include version/date stamps
- Link to responsible party/issue tracker
- Document update frequency

---

## Integrated Decision: Public Information Classification

### PUBLIC DISCLOSURE APPROVED FOR:

**Evidence-Verified, Current-State Information:**

- ✓ MoCKA core philosophy (README, bilingual)
- ✓ Current architecture layers (Semantic, Decision, Memory, Self-Audit, Feedback)
- ✓ Released products (Orchestra, Relay, Memory, PHI-OS)
- ✓ Academic publications (AIES 2026, Zenodo DOIs)
- ✓ Governance framework overview (Decision Policy, External Knowledge Policy, Activation Policy)
- ✓ Contributing guidelines (when created)
- ✓ Architecture overview (6 embedded diagrams)

### PUBLIC DISCLOSURE FORBIDDEN FOR (Under Embargo):

- ✗ Unverified repositories (11 pending audit)
- ✗ Phase 5+ target architecture (until approved for release)
- ✗ Unfinished features (PR-OS credentials pending, TIC Layer 2-4 incomplete)
- ✗ Decision ledger entries (internal governance only)
- ✗ Incident registry (operational security)
- ✗ Governance audit trail (internal authority only)

### AUTHORIZED DISCLOSURE (Contributors/Researchers):

- ✓ Design layer documentation (Semantic, Decision, Memory, etc.)
- ✓ Integration guides (API specs, product integration)
- ✓ Governance baseline details (when contributor access approved)
- ✓ Repository architecture rationale (why 12 repos?)

---

## Operational Rules (Effective Immediately)

### Rule 1: Evidence Citation
Every public statement requires source link or citation. If source cannot be cited, information is not ready for public disclosure.

### Rule 2: State Labeling
Use mandatory labels (PROPOSAL, TARGET, FUTURE PLAN, ROADMAP, CURRENT) when referencing anything other than current implementation.

### Rule 3: Section Separation
Current state and target state documentation must occupy separate sections. Never mix within same paragraph/section.

### Rule 4: Verification First
Repositories and information must pass verification checklist before any public mention. Maintain embargo list.

### Rule 5: Responsibility Attribution
Every public document must name author/maintainer and include last-update date. Link to responsible party for questions.

---

## Implementation Status & Timeline

**Current Status:** APPROVED (conditions in place)  
**Implementation Authorization:** PENDING (issued in separate decision)  

**Before Implementation Can Begin:**

1. [ ] Product owner confirms conditions understood
2. [ ] Documentation lead creates guidelines (state labels, verification checklist, responsibility template)
3. [ ] Engineering lead audits 12 repositories (complete verification checklist)
4. [ ] Architecture lead reviews existing docs for unlabeled target info
5. [ ] All public docs updated per guidelines

**Timeline:**
- Week 1: Review conditions + create guidelines
- Week 2: Audit repositories + redact non-compliant docs
- Week 3: Update README + create REPOSITORY_MAP
- Week 4+: Phase 1-3 implementation per roadmap

**Blockers:**
- Repository audit must complete before repo map published
- Guidelines must exist before product docs written
- Conditions must be verified in all existing public docs

---

## Distinction: Approval vs. Authorization

**APPROVED (Today):**
- Three-layer framework: ✓ APPROVED
- Five conditions: ✓ APPROVED
- Public disclosure criteria: ✓ APPROVED
- Embargo list: ✓ APPROVED

**NOT YET AUTHORIZED (Separate Decision Required):**
- Publish updated README: ⏳ PENDING
- Create REPOSITORY_MAP: ⏳ PENDING
- Release product documentation: ⏳ PENDING
- Update mocka.nsjp.org: ⏳ PENDING
- Public disclosure of specific information: ⏳ PENDING (item-by-item)

**Reason for Separation:**
Conditions must be integrated into guidelines and existing docs must be audited *before* publishing. Approval of conditions does not mean approval to immediately publish.

---

## Alignment: PC and WEB Policies

### PC Policy (Canonical)
- Decision Policy v0.1: Authority hierarchy (Human Gate → Decision → Execution)
- External Knowledge Policy v0.1: Five conditions for adoption (Adopt/Hold/Experiment/Reject/Re-evaluate)
- Activation Policy v0.1: Knowledge asset reference timing

### WEB Policy (Public Boundary)
- Evidence-based information requirement: Consistent with Decision Policy (source verification)
- State labeling requirement: Consistent with External Knowledge Policy (distinguish proposal from current)
- Responsibility attribution: Consistent with Human Gate authority principle
- Verification before disclosure: Consistent with Activation Policy (gate information access)

**Alignment Result:** ✓ CONSISTENT — WEB conditions reinforce PC governance principles.

---

## Next Steps

**For Product Owner:**
1. [ ] Confirm conditions understood and acceptable
2. [ ] Authorize formation of implementation working group
3. [ ] Schedule repository audit kickoff (engineering lead)

**For Documentation Lead:**
1. [ ] Create "Public Documentation Guidelines" (state labels, verification template, responsibility format)
2. [ ] Audit existing public docs for unlabeled target info
3. [ ] Schedule redaction/update per conditions

**For Engineering Lead:**
1. [ ] Begin 12-repository audit (verification checklist)
2. [ ] Report current public/private status
3. [ ] Identify repositories ready for disclosure vs. embargo

**For Architecture Lead:**
1. [ ] Review design docs for unlabeled target architecture
2. [ ] Ensure GitHub architecture docs pass verification
3. [ ] Coordinate with engineering on repository rationale

**For All Leads:**
1. [ ] Read and confirm understanding of five conditions
2. [ ] Flag any implementation concerns
3. [ ] Coordinate timeline (target: guidelines ready by Week 1)

---

## Conclusion

**Status:** MOCKA_PUBLIC_INFORMATION_NETWORK_FINAL_DECISION_READY

The public information boundary is now **governed by evidence-based, current-state, responsibility-clear principles**. Implementation will proceed in phases, with conditions verified at each step.

The five conditions transform vague "transparency" into concrete, verifiable requirements:
1. Evidence-based (source verification)
2. State-labeled (current vs. target distinction)
3. Separated (current and roadmap sections)
4. Verified (embargo unverified info)
5. Attributed (clear responsibility)

These conditions align with MoCKA's core governance principle: **"System over trust."** Evidence, labels, and verification replace assumptions and inference.

---

**Decision Approved:** 2026-08-20  
**Effective Date:** 2026-08-20  
**Implementation Start:** 2026-08-22 (pending separate authorization)  
**Status:** READY FOR IMPLEMENTATION PLANNING  


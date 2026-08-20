# MoCKA Public Information Network — Implementation Authorization Proposal (WEB)

**Proposal Date:** 2026-08-20  
**Prepared For:** Human Gate (Product Owner)  
**Classification:** Implementation Planning & Authorization Request  
**Status:** Ready for Review & Authorization Decision  
**References:** MOCKA_PUBLIC_INFORMATION_NETWORK_FINAL_DECISION.md (Approved Framework)

---

## Executive Summary

This proposal outlines **how to operationalize** the five conditions approved by Human Gate Decision 2026-08-20. It presents specific actions for each condition, maps them to documentation and infrastructure changes, and defines the authorization boundary separating approved framework from authorized implementation.

**Key Point:** This is a proposal for **HOW** to implement the approved framework, not **WHETHER** to implement it.

**Decision Required:** Authorize the implementation plan (yes/no) and commit resources for Week 1-8 timeline.

---

## Part 1: Operationalizing the Five Conditions

### Condition 1: Evidence-Based Information Only

**Approved Rule (Final Decision):**
All publicly disclosed information must be **current, verifiable facts** with clear source attribution.

**How to Operationalize:**

#### 1.1 — Public Documentation Verification Template

Create a "Public Documentation Checklist" that will be applied to every public-facing document before publication:

```
Document: [title]
Author: [name]
Date: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

VERIFICATION CHECKLIST:
[ ] Source Verified — Each statement links to source (code, doc, or external reference)
[ ] Current State — Information describes present implementation, not planned
[ ] Factually Accurate — Statement is correct as of last-update date
[ ] Externally Verifiable — Third party can confirm this statement

Examples of Acceptable Evidence:
  ✓ "Code exists: /code/semantic_layer/" — shows directory presence
  ✓ "Released v1.0: 2026-08-15" — shows GitHub release date
  ✓ "Academic paper: Zenodo DOI xxxxx" — shows published reference
  ✓ "Available at Stripe marketplace" — shows external listing

Examples of Unacceptable Evidence:
  ✗ "We are planning X" — prediction, not current state
  ✗ "Future versions will support Y" — speculation
  ✗ "Repository X is for testing" — inference without documented purpose
  ✗ "Research in progress" — ongoing work, not verified completion

DECISION GATE:
  ✓ All checks passed → Document ready for publication
  ✗ Any check failed → Document held until evidence is updated or statement removed
```

#### 1.2 — Evidence Citation Format

Every public statement must include an inline citation or reference section:

```markdown
GOOD (Current State with Evidence):
"MoCKA includes Caliber AI evaluation system (source: /code/caliber/ directory, 
last verified 2026-08-20)"

"Orchestra is available at Stripe marketplace (evidence: https://stripe.com/products/orchestra, 
verified 2026-08-15)"

BAD (No Source or Prediction):
"MoCKA will include autonomous evolution in Phase 5"
  → Missing: When it will be included, who approved it
  → Missing: Evidence that Phase 5 is approved/active

"Repository X is an experimental testbed"
  → Missing: Where this is documented
  → Missing: Who maintains it
```

#### 1.3 — Source Audit Process (Pre-Publication)

Before any README/documentation update is pushed to public:

1. Extract all factual claims from the document
2. For each claim, identify the source (code, file, external reference)
3. Verify source is still valid as of current date
4. Add citation inline or in reference section
5. Mark document with last-verified date
6. If any source is missing or outdated, flag for documentation lead review

**Responsible:** Documentation lead + Architecture lead (joint review)

---

### Condition 2: Target vs. Current State Labeling

**Approved Rule (Final Decision):**
Use mandatory labels (PROPOSAL, TARGET, FUTURE PLAN, ROADMAP, CURRENT) when referencing anything other than current implementation.

**How to Operationalize:**

#### 2.1 — Mandatory Label Enforcement

Update all public documentation templates to require state labels:

```markdown
TEMPLATE: Current State Documentation

## Current Architecture (Phase 4, as of 2026-08-20)

MoCKA currently implements:
- Semantic Layer (stable)
- Decision Layer (stable)
- Memory Layer (stable)
- Self-Audit Layer (stable)
- Feedback mechanisms (stable)

---

## Planned Enhancements (Future Phases)

**Target Architecture (Phase 5, estimated Q4 2026):**
- Self-Learning Kernel: Converts feedback into weight updates
  - Status: Design approved, implementation pending
  - Dependencies: Phase 4 complete (✓), governance approval (pending)
  
**Proposal (Phase 6, under discussion):**
- Autonomous Evolution Protocol: System modifies own governance rules
  - Status: Proposed, decision pending
  - Blockers: Requires Phase 5 completion + additional governance approval

**Roadmap (unconfirmed):**
- TIC Layer 4: COMMAND CENTER UI (Q4 2026, estimated)
- PR-OS Credential system (blocking: credentials setup required)

---

LABELING RULES:
* No label = Current implementation (stable/operational)
* "Target:" = Planned but not yet active
* "Proposal:" = Under consideration, not yet approved
* "Roadmap:" = Future possibility, timeline/approval unclear
* "Phase X:" = Always specify phase number for future work
```

#### 2.2 — Dual-Section Structure (Current vs. Target)

Split documentation into separate "Current" and "Roadmap" sections:

```
BAD (Mixed):
## Architecture
MoCKA implements layers A, B, C, D, E, and plans F and G...

GOOD (Separated):
## Current Architecture
MoCKA currently implements:
- Layer A
- Layer B
- Layer C
- Layer D
- Layer E

## Planned Features (Roadmap)
Target (Phase 5): Layer F
Target (Phase 6): Layer G
```

#### 2.3 — Documentation Audit Template

Before publication, check all references to Phase 5+, features in progress, or unfinished work:

```
Audit: Document state labeling compliance

Document: [filename]
Scan for: "will support", "planned", "Phase 5+", "in progress", "future"

CHECKLIST:
[ ] No unlabeled future references (all have TARGET/PROPOSAL/ROADMAP labels)
[ ] Current section contains only stable/operational features
[ ] Roadmap section is clearly separated with headers
[ ] Phase numbers are specified for all planned features
[ ] Estimated dates are marked as "estimated" (not committed)

Compliance: [PASS / NEEDS_REMEDIATION]
```

**Responsible:** Documentation lead (audit), Product owner (approval of target features)

---

### Condition 3: Separation of Current State and Target State

**Approved Rule (Final Decision):**
Current state and target state documentation **must be in separate sections or documents**. No mixing.

**How to Operationalize:**

#### 3.1 — Directory Structure for Documentation

```
/docs/public/
  README.md (gateway document, links to below)
  
  /current/
    ARCHITECTURE_CURRENT.md (Layers 1-5, stable)
    PRODUCTS_CURRENT.md (Released: Orchestra, Relay, Memory, PHI-OS)
    GOVERNANCE_BASELINE.md (Active policies: Decision Policy v0.1, etc.)
    API_REFERENCE.md (Current API specification)
    
  /roadmap/
    PHASES_5_6_ROADMAP.md (Future planned work)
    LEARNING_KERNEL_PROPOSAL.md (Phase 5 design, pending approval)
    TIC_LAYER_EXPANSION.md (Layer 2-4 plans, in development)
    PRODUCT_PIPELINE.md (Coming-soon features)

/docs/authorized/ (Contributor access)
  DESIGN_LAYERS.md (Architecture rationale)
  INTEGRATION_GUIDES.md (API integration details)
  REPOSITORY_MAP.md (Why 12 repos? Architecture explanation)

/docs/internal/ (Governance only)
  DECISION_LEDGER.md (Decision records, approval authority)
  INCIDENT_REGISTRY.md (Operational incidents, security info)
```

#### 3.2 — No Cross-Contamination Rule

Enforce through documentation guidelines:

```
RULE: Do not reference future features in current state docs

BAD (violates):
README says: "MoCKA supports Semantic, Decision, Memory, Self-Audit, 
and Self-Learning (Phase 5)"
  → Implies Phase 5 is current
  → Violates "current state only" in this section

GOOD (compliant):
README says: "MoCKA currently supports Semantic, Decision, Memory, 
Self-Audit layers"
[Link to ROADMAP_PHASES_5_6.md for future features]
```

#### 3.3 — Cross-Reference Without Mixing

Linking between current and roadmap is allowed, but must be clear:

```markdown
## Current Products

Orchestra v1.0 (production) — available at Stripe marketplace
Relay v1.1 (production)
Memory v2.0 (production)
PHI-OS (Chrome Web Store)

For planned enhancements, see [Roadmap: Product Pipeline](../roadmap/PRODUCT_PIPELINE.md)

---

## Roadmap: Planned Features

[See current section above for production releases]

Target (Phase 5): Enhanced Learning features
Target (Phase 6): Autonomous updating capability
```

**Responsible:** Documentation lead (structure), Technical writer (content)

---

### Condition 4: Unverified Repository & Information Embargo

**Approved Rule (Final Decision):**
Repositories and information lacking verification **must not be disclosed publicly**. Maintain embargo until verification complete.

**How to Operationalize:**

#### 4.1 — Repository Verification Checklist

Before any repository is mentioned in public documentation, complete this checklist:

```
Repository: [name]
Owner: [org/person]
Current Status: [Public / Private / Unknown]

VERIFICATION CHECKLIST:
[ ] GitHub Access Status Confirmed
    ✓ Is repository publicly accessible?
    ✓ URL confirmed to resolve (https://github.com/...)
    
[ ] Purpose Documented
    ✓ README exists
    ✓ README explains what this repository is for
    ✓ Relationship to MoCKA explained (core/extension/research)
    
[ ] Maintenance Status Clear
    ✓ Last commit date: [YYYY-MM-DD]
    ✓ Is it actively maintained? (last commit < 6 months ago = active)
    ✓ Is it experimental/archived? (marked in README)
    
[ ] Content State Verified
    ✓ Code is current (not stale/abandoned)
    ✓ Documentation is current
    ✓ No proprietary/confidential information leaked

VERIFICATION RESULT:
  ✓ ALL CHECKS PASSED → Repository approved for public disclosure
  ✗ ANY CHECK FAILED → Repository remains under embargo

EMBARGO REASON (if failed):
  [ ] GitHub status unknown
  [ ] Purpose undocumented
  [ ] Maintenance status unclear
  [ ] Content outdated or confidential
  
EMBARGO LIFT DATE: [when verification will complete]
```

#### 4.2 — Embargo List (Internal Only)

Maintain an internal-only embargo tracking document:

```
EMBARGO LIST — Updated 2026-08-20
(Not for public disclosure, for governance tracking only)

UNDER EMBARGO:
- mocka-civilization (status: verification pending, lead: eng-team)
- mocka-joints (status: needs content review, lead: arch-lead)
- planningcaliber (status: relationship unclear, lead: product-owner)

CLEARED FOR PUBLIC DISCLOSURE:
- m-sirius-k/MoCKA (core, public, active)
- vasAI (research, Zenodo DOI, public)
- mocka-public (documentation hub, verified)
- [others as verified...]

VERIFICATION STATUS:
- 2 repos cleared
- 10 repos pending audit
- Update frequency: Weekly during audit phase
```

#### 4.3 — Repository Audit Process

Create a formal audit workflow:

```
WEEK 1-2 AUDIT PLAN (2026-08-22 to 2026-09-04):

Day 1-2: Gather Repository List
  - Extract all repos from OVERVIEW.json
  - Verify each repo URL resolves
  - Confirm GitHub access (public/private status)
  
Day 3-5: Document Review
  - Check each repo's README
  - Understand purpose + relationship to MoCKA
  - Identify maintenance status (active/archived/experimental)
  
Day 6-7: Content Audit
  - Scan for confidential information
  - Verify code currency (no stale/dead branches)
  - Check for version info/documentation timestamps
  
Day 8-10: Verification Checklist Completion
  - Complete verification checklist for each repo
  - Document embargo lift requirements (if any)
  - Create REPOSITORY_MAP.md entry (see below)
  
Day 11-14: Report + Clearing
  - Present audit results to product owner
  - Identify which repos are cleared for public disclosure
  - Note embargo reasons for repos not cleared
  - Recommend timeline for embargo lift

RESPONSIBLE: Engineering lead
OWNER: Product owner (approval of clearance)
BLOCKERS: Cannot publish REPOSITORY_MAP until audit is 100% complete
```

#### 4.4 — REPOSITORY_MAP.md (To Be Created)

This document will be public, but **only published after embargo audit is complete**:

```markdown
# MoCKA Repository Ecosystem

Last Updated: [date after audit completion]
Audit Status: Complete as of [date]

## Tier 1: Core System

**m-sirius-k/MoCKA**
- Purpose: Core governance and operational framework
- Status: Production-active
- Last Updated: [date]
- Maintainer: [team/person]
- Public: Yes
- Documentation: README, /docs/

**vasAI**
- Purpose: AI governance research framework (academic publication)
- Status: Research (production code available)
- Last Updated: [date]
- Maintainer: [author], published Zenodo DOI
- Public: Yes
- Documentation: Academic paper + GitHub docs

## Tier 2: Extensions & Integrations

**mocka-public** (Documentation Hub)
- Purpose: Holds public-facing documentation assets
- Status: Active
- Last Updated: [date]
- Maintainer: Documentation lead
- Public: Yes

[Additional entries only after verification checklist passes...]

---

## How to Contribute

See CONTRIBUTING.md for involvement process
```

**Responsible:** Engineering lead (audit), Documentation lead (REPOSITORY_MAP creation)

---

### Condition 5: Clear Authority and Update Responsibility

**Approved Rule (Final Decision):**
Every public statement must have **clear authority** (who says this is true?) and **update responsibility** (who maintains this?).

**How to Operationalize:**

#### 5.1 — Attribution Header Template

Every public-facing document must include attribution:

```markdown
# [Document Title]

**Maintained by:** [Name/Team]  
**Current Version:** [version number]  
**Last Updated:** [YYYY-MM-DD]  
**Status:** [Production / Beta / Experimental]  
**Governance:** [Authority that approves changes]

**Questions or Updates:** Contact [email] or see [issue tracker URL]

---

[Document content begins...]
```

#### 5.2 — Product Information Attribution

For each product entry in public docs:

```markdown
## Orchestra v1.0

**Maintained by:** Product Team  
**Current Status:** Production (released 2026-08-15)  
**Availability:** Stripe marketplace (https://stripe.com/products/orchestra)  
**Last Verified:** 2026-08-20  
**Updates:** Contact [support email] or see GitHub issues

Feature Details:
- [feature 1] — current implementation
- [feature 2] — current implementation

For roadmap and future features, see [Roadmap: Orchestra Pipeline](../roadmap/ORCHESTRA_PIPELINE.md)
```

#### 5.3 — Governance Authority Attribution

For architecture and policy documents:

```markdown
# Decision Policy v0.1

**Authored by:** Architecture Lead  
**Approved by:** Human Gate (2026-06-15)  
**Effective Date:** 2026-06-20  
**Status:** Active (Operational)  
**Last Updated:** 2026-08-20  

**Governance Process:** Changes to this policy require Human Gate approval
(see [DECISION_POLICY_v0.1.md](governance/DECISION_POLICY_v0.1.md))

**Questions:** See [governance/issues](https://github.com/m-sirius-k/MoCKA/issues?q=label:governance)

---
[Policy content...]
```

#### 5.4 — Update Responsibility Tracking

Create a responsibility matrix:

```
Public Documentation Update Responsibility:

README.md
  ├─ Maintainer: Product Owner
  ├─ Update Frequency: When major features released
  ├─ Approval Required: Product owner
  └─ Last Updated: 2026-08-20

CURRENT/ARCHITECTURE.md
  ├─ Maintainer: Architecture Lead
  ├─ Update Frequency: When layer changes approved
  ├─ Approval Required: Human Gate (for significant changes)
  └─ Last Updated: 2026-08-20

ROADMAP/PHASES_5_6.md
  ├─ Maintainer: Product Owner
  ├─ Update Frequency: As phase status changes
  ├─ Approval Required: Product owner (draft), Human Gate (final)
  └─ Last Updated: 2026-08-20

REPOSITORY_MAP.md
  ├─ Maintainer: Documentation Lead (after engineering audit)
  ├─ Update Frequency: After repository changes (quarterly review)
  ├─ Approval Required: Engineering lead + Product owner
  └─ Last Updated: [TBD - after audit completion]

CONTRIBUTING.md
  ├─ Maintainer: Community Lead
  ├─ Update Frequency: When contribution process changes
  ├─ Approval Required: Product owner
  └─ Last Updated: [TBD]
```

**Responsible:** Each document maintainer (named above)

---

## Part 2: Implementation Plan (Four Phases)

### Phase 0: Framework Setup (Week 1, 2026-08-22 to 2026-08-28)

**Goal:** Create guidelines and documentation templates before any public changes.

**Tasks:**

1. **Create Documentation Guidelines**
   - File: `/docs/governance/PUBLIC_DOCUMENTATION_GUIDELINES.md`
   - Content: Evidence verification template, state label requirements, review checklist
   - Responsible: Documentation lead
   - Time: 2 days

2. **Create Public Documentation Template**
   - File: `/docs/templates/PUBLIC_DOCUMENT_TEMPLATE.md`
   - Content: Required headers (maintainer, version, date, status), section structure
   - Responsible: Documentation lead
   - Time: 1 day

3. **Update Documentation Review Process**
   - Document: Communication to team on new review gate
   - Process: All public doc updates must pass evidence/labeling/authority checklist before commit
   - Responsible: Product owner
   - Time: 1 day

4. **Verify MCP Tool Integration (Decision Point 3 Requirement)**
   - Check: Does mocka.nsjp.org currently exist?
   - Verify: Is it HTTPS-enabled? What is current content?
   - Responsible: Product owner
   - Time: 0.5 day
   - **Blocking Factor:** Cannot decide mocka.nsjp.org role until verified

**Deliverables:**
- PUBLIC_DOCUMENTATION_GUIDELINES.md
- PUBLIC_DOCUMENT_TEMPLATE.md
- mocka.nsjp.org verification report (for product owner decision)

**Gate to Next Phase:** All guidelines created + mocka.nsjp.org verified

---

### Phase 1: Audit & Assessment (Week 2-3, 2026-08-29 to 2026-09-11)

**Goal:** Complete repository audit and identify all public/private/embargo status.

**Tasks:**

1. **Repository Verification Audit**
   - Audit all 12 repositories using verification checklist
   - Complete status for each: Public/Private/Embargo
   - Document embargo lift requirements
   - Responsible: Engineering lead
   - Time: 1 week

2. **Current Documentation Scan**
   - Extract all factual claims from existing README.md
   - Identify sources (code, external reference) for each claim
   - Flag statements lacking sources or outdated information
   - Responsible: Architecture lead
   - Time: 3 days

3. **Governance Document Audit**
   - Review existing public governance references
   - Identify any decision-ledger or incident-registry leaks
   - Confirm internal-only documents are not accidentally public
   - Responsible: Governance lead
   - Time: 2 days

**Deliverables:**
- REPOSITORY_AUDIT_REPORT.md (internal, summarizes verification checklist results)
- EMBARGO_LIST.md (internal, tracking unverified repos)
- DOCUMENTATION_GAPS_REPORT.md (internal, sources needing verification/update)

**Gate to Next Phase:** Audit complete + embargo list finalized + product owner approves repository strategy (Decision Point 4)

---

### Phase 2: Remediation & Preparation (Week 4-5, 2026-09-12 to 2026-09-25)

**Goal:** Create/update documentation to comply with five conditions (without publishing to public).

**Tasks:**

1. **Create REPOSITORY_MAP.md (Draft)**
   - Based on audit results from Phase 1
   - Include only verified/cleared repositories
   - Note embargo status for others
   - Responsible: Documentation lead + Engineering lead
   - Time: 3 days

2. **Create Current/Roadmap Directory Structure**
   - Create `/docs/public/current/` section
   - Create `/docs/public/roadmap/` section
   - Create `/docs/authorized/` section
   - Move/copy existing docs into appropriate sections (no GitHub push yet)
   - Responsible: Documentation lead
   - Time: 4 days

3. **Update/Verify Existing Public Docs**
   - Add evidence citations to README (current state only)
   - Separate Phase 5+ references to roadmap section
   - Add state labels (CURRENT/TARGET/PROPOSAL) where needed
   - Add attribution headers (maintainer, version, date, status)
   - Responsible: Documentation lead + Architecture lead
   - Time: 5 days

4. **Create Product Documentation**
   - Add public docs for Orchestra, Relay, Memory, PHI-OS
   - Include evidence, authority, update responsibility
   - Separate current features from roadmap
   - Responsible: Product lead + Documentation lead
   - Time: 3 days

5. **Create CONTRIBUTING.md**
   - How to get involved with MoCKA
   - Where to ask questions
   - Contributor workflow
   - Responsible: Community lead
   - Time: 2 days

**Deliverables:**
- Updated README.md (draft, not yet published)
- `/docs/public/current/` directory (draft docs)
- `/docs/public/roadmap/` directory (draft docs)
- REPOSITORY_MAP.md (draft)
- Product documentation (draft)
- CONTRIBUTING.md (draft)

**All drafts staged locally; no commits to public-facing branches yet**

**Gate to Next Phase:** Product owner reviews all draft docs and approves content before public publication

---

### Phase 3: Authorization & Publication (Week 6-8, 2026-09-26 to 2026-10-09)

**Goal:** Obtain Human Gate authorization and execute publication.

**Tasks (Contingent on Human Gate "GO" Authorization):**

1. **Human Gate Authorization Review**
   - Present all draft documents from Phase 2
   - Confirm conditions are operationalized correctly
   - Request authorization to publish
   - Responsible: Product owner + Documentation lead
   - Time: 1 day

2. **Final Verification Pass (Upon Authorization)**
   - Documentation lead performs final evidence/label/authority audit on all docs
   - Verify no decision-ledger/incident-registry information leaked
   - Confirm all attribution headers complete
   - Responsible: Documentation lead + Architecture lead
   - Time: 2 days

3. **Git Workflow Preparation (Upon Authorization)**
   - Stage all documentation changes
   - Prepare commit message referencing Decision 2026-08-20
   - Prepare pull request for public docs
   - Responsible: Documentation lead + Engineering lead
   - Time: 1 day

4. **Staged Commit (Upon Authorization)**
   - Commit all public documentation changes to development branch
   - Push to GitHub for internal review
   - Responsible: Engineering lead
   - Time: 0.5 day

5. **mocka.nsjp.org Setup (If Option A Approved from Decision Point 3)**
   - Configure domain (if it doesn't exist)
   - Set up as public gateway (landing page)
   - Link to GitHub repositories
   - Responsible: Infrastructure lead + Product owner
   - Time: 3 days

6. **Final Merge to Public (Upon Authorization + Review Approval)**
   - Merge documentation pull request to main
   - Update website/domain if applicable
   - Publish REPOSITORY_MAP.md (after embargo audit complete)
   - Responsible: Engineering lead
   - Time: 1 day

**Deliverables (Only if Authorization Granted):**
- Committed and pushed public documentation
- Published README.md (updated)
- Published `/docs/public/current/` section
- Published `/docs/public/roadmap/` section
- Published REPOSITORY_MAP.md
- Published CONTRIBUTING.md
- mocka.nsjp.org live (if applicable)

**Risk Control:** No changes are committed until Human Gate explicitly authorizes "proceed to Phase 3"

---

## Part 3: Authorization Boundary

### What IS Approved (Framework Level)

✓ **APPROVED:** Five conditions for public information disclosure  
✓ **APPROVED:** Three-layer boundary framework (PUBLIC/AUTHORIZED/CANONICAL CORE)  
✓ **APPROVED:** Evidence-based information requirement  
✓ **APPROVED:** State labeling (CURRENT/TARGET/PROPOSAL/ROADMAP)  
✓ **APPROVED:** Separation of current and target documentation  
✓ **APPROVED:** Verification checklist for repositories  
✓ **APPROVED:** Attribution and update responsibility requirement  

### What is NOT Yet Authorized (Implementation Level)

⏳ **NOT YET AUTHORIZED:** Publish updated README.md  
⏳ **NOT YET AUTHORIZED:** Create `/docs/public/current/` section  
⏳ **NOT YET AUTHORIZED:** Create `/docs/public/roadmap/` section  
⏳ **NOT YET AUTHORIZED:** Publish REPOSITORY_MAP.md  
⏳ **NOT YET AUTHORIZED:** Publish CONTRIBUTING.md  
⏳ **NOT YET AUTHORIZED:** Set up mocka.nsjp.org  
⏳ **NOT YET AUTHORIZED:** Disclose any specific repositories  

### Why Separation Matters

**APPROVED:** "We will follow these five rules when publishing"  
**NOT YET AUTHORIZED:** "We will now publish these specific documents"

This separation prevents the conditions from being interpreted as a de facto authorization to immediately publish everything. Instead:

1. Conditions define HOW to do public disclosure safely
2. Phase 0-2 (Guideline creation, audit, remediation) show WHAT would be published
3. Phase 3 request asks WHETHER to publish
4. Human Gate decides GO/HOLD on Phase 3 independent of condition approval

---

## Part 4: Risk Control Measures

### Risk 1: Accidental Publication of Unimplemented Features

**Risk:** Someone publishes "Phase 5 Self-Learning Kernel" without noting it's not yet implemented.

**Control 1a:** Mandatory state labels (CONDITION 2)
- Every feature entry must be marked CURRENT/TARGET/PROPOSAL
- Code review checks for unlabeled future features

**Control 1b:** Separate current/roadmap sections (CONDITION 3)
- Current features in one section, future in another
- Reduces chance of mixing

**Control 1c:** Update responsibility assignment (CONDITION 5)
- Named maintainer is accountable for accuracy
- Can be reached if information becomes outdated

---

### Risk 2: Attribution of Authority to Unvetted Repositories

**Risk:** Someone mentions "mocka-joints" as part of MoCKA ecosystem without verifying its purpose/maintenance.

**Control 2a:** Repository verification checklist (CONDITION 4)
- Must complete checklist before ANY public mention
- Embargo enforced until checklist passes

**Control 2b:** REPOSITORY_MAP audit gate (CONDITION 4)
- Cannot publish repo map until all repos verified
- Prevents incomplete ecosystem disclosure

**Control 2c:** Clear authority attribution (CONDITION 5)
- "Maintained by [name]" clarifies who is accountable
- Missing maintainer = cannot be published

---

### Risk 3: Speculation Presented as Current State

**Risk:** "MoCKA will support X in version 2.0" gets published as if it's decided.

**Control 3a:** Evidence-based requirement (CONDITION 1)
- Must cite source code/document confirming feature
- Prediction has no source code = cannot be published

**Control 3b:** State labeling (CONDITION 2)
- "will support" = PROPOSAL/TARGET label required
- Label itself signals this is not current

**Control 3c:** Clear authority (CONDITION 5)
- "Planned by [product owner], approved [date]" shows decision status
- Missing approval date = not yet authorized

---

### Risk 4: Internal Decision Ledger Accidentally Leaked to Public

**Risk:** GitHub docs accidentally reference "per Human Gate Decision XYZ" or incident details.

**Control 4a:** Documentation audit in Phase 1
- Scan for "decision ledger", "incident", "confidential", "internal"
- Flag any references before publication

**Control 4b:** Separate documentation layers
- `/docs/internal/` for decision records (never public)
- `/docs/public/` for public information only
- Reduces chance of mislocation

**Control 4c:** Content classification training
- Documentation guidelines clarify what IS/ISN'T public
- Review process verifies classification

---

### Risk 5: Outdated Information Becomes "Official" Public Claim

**Risk:** README says "Orchestra v1.0 is production-ready" but v1.1 is now available.

**Control 5a:** Update responsibility assigned (CONDITION 5)
- Named maintainer must update docs when product updates
- "Last Updated: 2026-08-20" signals staleness

**Control 5b:** Evidence-based requirement (CONDITION 1)
- If source is outdated, information cannot be published
- Forces re-verification after product changes

**Control 5c:** Verification checklist
- "Current version confirmed" item in checklist
- Must check release dates/version numbers before commit

---

## Part 5: Success Metrics

### Phase 0 Success Criteria
- [ ] PUBLIC_DOCUMENTATION_GUIDELINES.md created and circulated
- [ ] mocka.nsjp.org verification completed
- [ ] All team leads acknowledge understanding of guidelines

### Phase 1 Success Criteria
- [ ] All 12 repositories have completed verification checklist
- [ ] Embargo list finalized and approved by product owner
- [ ] Current documentation gaps identified and logged

### Phase 2 Success Criteria
- [ ] All draft documentation has evidence citations
- [ ] All state labels (CURRENT/TARGET/PROPOSAL) applied correctly
- [ ] All attribution headers (maintainer, version, date) complete
- [ ] Product owner has reviewed and approved all draft docs

### Phase 3 Success Criteria
- [ ] Human Gate authorizes Phase 3 (GO decision)
- [ ] Final verification pass completes with zero findings
- [ ] All documentation committed and pushed
- [ ] REPOSITORY_MAP.md published (embargo audit complete)
- [ ] mocka.nsjp.org live (if Option A approved)

---

## Part 6: Resource Requirements

**Timeline:** 8 weeks (2026-08-22 to 2026-10-09)

**Team Allocation:**

- **Product Owner:** 2 days (Week 1 guidelines, Week 6 authorization decision)
- **Documentation Lead:** 3 weeks (Guidelines creation, content migration, review)
- **Architecture Lead:** 1.5 weeks (Current state documentation, design rationale)
- **Engineering Lead:** 2.5 weeks (Repository audit, git workflow, deployment)
- **Community Lead:** 4 days (CONTRIBUTING.md creation)
- **Infrastructure Lead:** 3 days (mocka.nsjp.org setup, if applicable)

**Total Effort:** ~16 person-weeks (equivalent to one person for 4 months, or distributed across team)

**Blockers Requiring External Input:**
- Product owner decision on mocka.nsjp.org (Decision Point 3)
- Product owner decision on repository disclosure level (Decision Point 4)
- Engineering audit completion (before REPOSITORY_MAP publication)
- Human Gate authorization for Phase 3 (before any public changes)

---

## Part 7: Contingency & Hold Conditions

### Scenario: Embargo Audit Reveals Significant Issues

**If discovered:** Critical repositories are unverifiable or contain confidential information

**Action:**
1. Document issues in EMBARGO_LIST.md
2. Request product owner decision on hold/remediate/exclude
3. Extend Phase 2 if remediation needed
4. Cannot proceed to Phase 3 until embargo list is finalized

**Impact:** 1-2 week timeline extension possible

---

### Scenario: Public Documentation Review Finds Policy Violations

**If discovered during Phase 2:** Docs contain decision-ledger references or unlabeled future features

**Action:**
1. Halt Phase 2 → remediate violating docs
2. Update guidelines to prevent recurrence
3. Resume Phase 2 after fix verification
4. Cannot proceed to Phase 3 until zero violations found

**Impact:** 3-5 day timeline extension possible

---

### Scenario: Human Gate Declines Phase 3 Authorization

**If Human Gate says "HOLD" instead of "GO":**

**Actions:**
1. Incorporate feedback from Human Gate into Phase 2 drafts
2. Update draft docs as directed
3. Re-present revised drafts to Human Gate
4. Re-request Phase 3 authorization

**Impact:** 1-3 weeks possible, depending on scope of changes

**This does not invalidate the approved conditions** — it only defers publication. The framework remains available for future authorization request.

---

## Part 8: Decision Points Requiring Human Gate Input

### Decision 3a: mocka.nsjp.org Verification (Required for Phase 0 Completion)

**Question:** Does mocka.nsjp.org currently exist? Is it HTTPS? What is its current purpose?

**Input Needed From:** Product owner

**Timeline:** Must be resolved by end of Week 1 (2026-08-28)

**Impact:** Determines whether mocka.nsjp.org setup is included in Phase 3

---

### Decision 4a: Repository Disclosure Level (Required for Phase 1 Completion)

**Question:** Of the repositories cleared by engineering audit, how many should be publicly listed in REPOSITORY_MAP.md?

**Options:**
- **Strategy A:** All verified repos (9+ public, others private)
- **Strategy B:** Core only (3 public: MoCKA, vasAI, mocka-public)
- **Strategy C:** Wait until all repos verified (embargo everything initially)

**Input Needed From:** Product owner

**Timeline:** Must be resolved by end of Week 3 (2026-09-11)

**Impact:** Determines REPOSITORY_MAP.md scope and publication readiness

---

### Decision Phase 3: Authorization to Proceed (Required for Phase 3 Start)

**Question:** Approve implementation of the operationalization plan? (Yes/No/Revise)

**Inputs to Present:**
- Phase 2 draft documents (README, docs structure, REPOSITORY_MAP, CONTRIBUTING)
- Phase 1 audit results (repository verification status)
- Risk control measures (safeguards against information leakage)
- Resource commitment (16 person-weeks over 8 weeks)

**Input Needed From:** Human Gate

**Timeline:** Must be resolved by end of Week 5 (2026-09-25)

**Impact:** Whether actual publication proceeds or Phase 3 is held

---

## Conclusion

This proposal operationalizes the five approved conditions into a concrete four-phase plan:

**Phase 0:** Create guidelines and verify prerequisites  
**Phase 1:** Complete repository audit and documentation assessment  
**Phase 2:** Create/update documentation to comply with conditions (draft only)  
**Phase 3:** Obtain authorization and execute publication (if approved)

**Key Safeguards:**

✓ Guidelines created before any public changes  
✓ Comprehensive repository audit before disclosure  
✓ Full draft review by product owner before publication  
✓ Human Gate authorization gate before actual public changes  
✓ Five risk controls embedded in process to prevent violations  

**Authorization Boundary:**

✓ APPROVED: Framework and conditions (effective now)  
✗ NOT YET AUTHORIZED: Implementation and publication (requires Phase 3 decision)

This separation ensures that condition approval does not automatically trigger publication, and that implementation decisions are made transparently with product owner and Human Gate input.

**Status:** READY FOR HUMAN GATE AUTHORIZATION DECISION

---

**Proposal Submitted:** 2026-08-20  
**Prepared By:** MoCKA Governance  
**Next Steps:** Human Gate reviews this proposal and decides on Phase 3 authorization


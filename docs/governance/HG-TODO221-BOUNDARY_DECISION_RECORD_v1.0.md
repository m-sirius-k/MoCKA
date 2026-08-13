# HG-TODO221-BOUNDARY Decision Record v1.0

**Created**: 2026-08-13  
**Mode**: CONTROLLED REVIEW  
**Authority**: Human Gate Pending  
**Status**: Judgment Material for Approval  
**Classification**: Internal Decision Resource (Not Yet Committed)

---

## Executive Summary

This record articulates the responsibility boundary between TODO_221 (Product Surface Preparation) and Product Entry Point Definition (User Journey Design) to enable MoCKA's transition from Phase 4 (制度化) to Phase 5 (利用体験設計).

**Proposed Decision**: APPROVE OPTION B
- TODO_221 remains focused on Product Surface (LP + Content)
- Product Entry Point Definition becomes independent responsibility
- Boundary enables clear phase separation and risk mitigation

---

## 1. Current State Assessment

### 1.1 TODO_221 Technical Completion Status

**Evidence**: E20260812_7206767102548 (EVIDENCE_READY: TODO_221 Technical Completion Evidence v1.0)

| Component | Status | Verification |
|-----------|--------|--------------|
| LP Content Generated | ✅ COMPLETE | WordPress page ID:61 deployed |
| Hero Section | ✅ PRESENT | Catchcopy + Overview confirmed |
| Pricing Table | ✅ PRESENT | Free/Pro/One/Launch plans |
| Installation Guide | ✅ PRESENT | Setup instructions documented |
| FAQ Section | ✅ PRESENT | Q&A implemented |
| CTA Elements | ✅ PRESENT | Buttons present (link validation pending) |
| Stripe Integration | ✅ CONFIRMED | Payment links working (per E20260601_062) |
| Multi-language Support | ✅ CONFIRMED | 5-language i18n verified |

**Technical Status**: ✅ COMPLETE

### 1.2 Institutional Status (Not Closure)

| Aspect | Current State | Type |
|--------|--------------|------|
| Technical Work | COMPLETE | Implementation done |
| Institutional Approval | PENDING | Human Gate review required |
| TODO Status | 進行中 (In Progress) | Unchanged (no auto-close) |
| Evidence Preservation | ACTIVE | Technical completion ≠ Status change |

**Institutional Status**: ⏳ PENDING (Awaits Closure Decision)

---

## 2. The Critical Boundary: "作ること" vs "届ける仕組み"

### 2.1 Distinction

```
PHASE 4 BOUNDARY CLARITY

製造 (Manufacturing)              配信 (Delivery)
─────────────────────────────────────────────
✅ LP Content Creation        → ⏳ User Journey Design
✅ Stripe Integration         → ⏳ Onboarding Flow  
✅ Multi-language Support     → ⏳ First Value Definition
✅ Technical Verification     → ⏳ Success Criteria
```

### 2.2 Historical Risk

Without clear boundary separation:
- MoCKA reverts to "infinite refinement" mode
- Polishing replaces progression
- Phase 5 entry delayed indefinitely
- "First value delivery" remains aspirational

**This decision prevents that regression.**

---

## 3. Responsibility Boundary Definition

### 3.1 TODO_221: "Product Surface Preparation"

**Purpose**: Establish viable product entry point at discovery layer

**Scope Included**:
- LP content generation (Hero, Pricing, HowTo, FAQ, CTA)
- Stripe payment link integration
- Multi-language support
- Content deployment to WordPress
- Discovery-layer accessibility verification

**Scope Excluded**:
- Onboarding flow design
- First-run experience definition
- Installation journey mapping
- Continued usage design
- Decision lifecycle mapping

**Completion Criteria**:
```
TODO_221 COMPLETE when:
1. LP deployed and publicly accessible
2. Stripe payment routing verified
3. All sections (Hero/Pricing/HowTo/FAQ/CTA) functional
4. 5-language support operational
5. No blocker errors in console
6. Remediation plan (CTA/SyntaxError/URL path) closed
```

**Not Completion Criteria**:
- User actually completes purchase
- User successfully installs Orchestra
- User experiences first value
- User continues using product

---

### 3.2 Product Entry Point Definition: "User Journey Design"

**Purpose**: Design complete path from Discovery to First Success

**Scope Included**:
- User Journey mapping (Discovery → First Success layers)
- Installation flow documentation
- First-run experience design
- Success criteria definition
- Decision lifecycle at each stage
- Risk mitigation for drop-off points

**Scope Excluded**:
- LP code/content changes
- Stripe payment mechanism
- WordPress deployment
- Multi-language translation

**Ownership**:
- Analysis: Claude (proposal)
- Decision: きむら博士 (approval)

**Timing**:
- Start: After TODO_221 Remediation complete + Human Closure
- Completion Target: Before Phase 5 implementation begins

---

## 4. Rationale for Option B (Boundary Separation)

### 4.1 Reason 1: TODO_221 Mission Already Achieved

**Original TODO_221 Definition**:
```
mocka.nsjp.org — /mini-mocka/orchestra
コンテンツ投入（LP+説明書+Q&A）
```

**Translation**: "Content deployment to mocka.nsjp.org/mini-mocka/orchestra (LP + User Guide + FAQ)"

**Verification**: All committed
- ✅ Hero section (product intro)
- ✅ Pricing table (plan clarity)
- ✅ FAQ (common questions)
- ✅ Installation guide (setup steps)
- ✅ CTA buttons (action prompts)
- ✅ Stripe links (payment routing)
- ✅ Multi-language (5-language i18n)

**Characterization**: TODO_221 = **Product Surface Creation**

**Problem if Expanded**:
- Adding "Onboarding design" changes the TODO's fundamental responsibility
- Shifts from "making surface exist" to "designing entire journey"
- Original stakeholders may miss expanded scope
- Risks duplicate effort (Onboarding might get handled elsewhere)

### 4.2 Reason 2: Product Entry Point ≠ LP

**Common Misconception**:
```
Product Entry Point = Landing Page
```

**Reality**:
```
Product Entry Point = User Journey from Discovery to First Success
```

**Structural Difference**:

```
DISCOVERY LAYER (TODO_221 scope)
    LP exists → User reads content → User sees pricing
                                        ↓
ENTRY POINT LAYER (New scope)
    ↓
    User decides to purchase → User installs product
    User launches Orchestra → User completes first workflow
    User realizes first value → User decides to continue
```

**TODO_221 Coverage**: Discovery layer only

**New Scope Coverage**: Full journey from Discovery to First Success

**Why Separate?**:
- Different design disciplines (marketing vs UX vs product)
- Different approval cycles
- Different success metrics
- Different risk profiles

### 4.3 Reason 3: Phase Boundary Clarity

**MoCKA's Strategic Transition**:

```
PHASE 4 (Current)           PHASE 5 (Next)
制度化の完成            利用体験設計の開始
───────────────────────────────────
Goal:                       Goal:
"How to know?"              "How to use?"
Mechanism:                  Mechanism:
Record + Verify             Design + Deliver

Key Question:               Key Question:
Can we trust the system?    Can users succeed immediately?
```

**If Product Entry Point ⊂ TODO_221**:
- No clear phase boundary
- Phase 4 expands indefinitely
- Phase 5 start becomes unclear

**If Product Entry Point = Independent**:
- TODO_221 closure = Phase 4 completion
- Product Entry Point start = Phase 5 launch
- Clear progression path

---

## 5. Implementation Roadmap (Revised Order)

### Current (Incorrect) Sequence
```
Product Entry Point (uncertain scope)
    ↓
TODO_221 Close (dependencies unclear)
    ↓
TIC Layer (downstream blocked)
```

### Recommended Sequence

```
STEP 1: HG-TODO221-BOUNDARY Decision
├─ Approve Option B
├─ Formalize boundary
└─ Enable next steps

STEP 2: TODO_221 Remediation
├─ CTA Link Verification (Stripe Payment Link confirmation)
├─ SyntaxError Investigation (console error diagnosis)
├─ URL Path Consolidation (/mini-mocka/ vs /mini-mocka-2/)
└─ Technical closure ready

STEP 3: TODO_221 Human Gate Closure
├─ きむら博士 reviews remediation evidence
├─ Approves closure OR requests changes
└─ Marks Technical Complete + Institutionally Approved

STEP 4: Product Entry Point Definition START
├─ Design phase begins
├─ User journey mapping
├─ Onboarding flow specification
├─ Success criteria definition
└─ Decision lifecycle documentation

STEP 5: TIC Layer Design (can proceed in parallel with Step 4)
├─ Layer 2: Sandbox (tech_lab/)
├─ Layer 3: impact_analyzer.py
├─ Layer 4: COMMAND CENTER TIC panel

STEP 6: JARVIS E2E Testing
├─ E2E test suite design
├─ Critical path validation
└─ Remediation readiness check
```

**Key**: No step starts until clear boundary upstream.

---

## 6. Remaining Work in TODO_221 (Remediation)

From `TODO_221_REMEDIATION_PLAN_v0.2.md` (R01-approved):

### 6.1 Target 1: CTA Link Restoration (Critical)

**Issue**: Pro/One buttons have `href="#cta"` (dead link)

**Evidence**:
- Event E20260709_7361161464514: Browser console confirms dead link
- No Stripe network traffic when clicked
- Backend (Stripe Webhook/Cloudflare Worker) confirmed working (E20260601_062)

**Work Required**:
1. Retrieve current valid Stripe Payment Link URLs from Stripe Dashboard
2. Locate button href in WordPress page ID:61 or page-orchestra.php
3. Replace `#cta` with correct Stripe Payment Link
4. Verify: Click button → Stripe Checkout page loads
5. Optional: Test payment with test card (per きむら博士 approval)

**Ownership**: SSH access controlled by きむら博士

**Risk Level**: Medium (payment critical path)

### 6.2 Target 2: SyntaxError Investigation (Secondary)

**Issue**: Console error at `/mini-mocka-2/orchestra/:669:1335`

**Evidence**:
- Event E20260709_7361161464514: "SyntaxError: Invalid or unexpected token"
- Appears in inline script within page rendering
- Cause-effect with CTA dead link: **unconfirmed**

**Work Required**:
1. Identify source code at HTML line 669, column 1335
2. Diagnose syntax issue (potential PHP 8 incompatibility)
3. Fix if needed, re-verify console clean
4. Confirm: Does fix affect CTA behavior? Yes/No?

**Priority**: After Target 1 closure (independent verification)

**Risk Level**: Low (console error, not payment-blocking)

### 6.3 Target 3: URL Path Consolidation (Infrastructure)

**Issue**: `/mini-mocka/orchestra/` redirects to `/mini-mocka-2/orchestra/`

**Evidence**:
- Event E20260709_7361161464514: Browser navigation confirms 302 redirect
- Likely cause: wp_setup.sh double-run creating `-2` duplicate pages
- May relate to TODO_WP_DUPLICATE_PAGES_CLEANUP

**Work Required**:
1. Identify redirect source (.htaccess, plugin, theme hook, reverse proxy)
2. Determine: Which path is canonical? `/mini-mocka/` or `/mini-mocka-2/`?
3. Consolidate: 301 redirect to canonical, or delete old path
4. Update: Internal links (menu, other page refs)
5. Verify: `/mini-mocka/orchestra/` accessible at canonical path

**Priority**: Before Target 1 implementation (must know correct file path)

**Risk Level**: Medium (affects all page access)

---

## 7. Closure Criteria for TODO_221

**Technical Closure** (Already established: E20260812_7206767102548):
- LP content deployed ✅
- All sections present ✅
- Stripe integration confirmed ✅
- Multi-language working ✅

**Institutional Closure** (Requires Human Gate approval):

```
TODO_221 ready for closure when:

1. Remediation Plan Execution
   ☐ CTA links pointing to valid Stripe Payment URLs
   ☐ SyntaxError investigated (cause determined)
   ☐ URL path canonical and accessible
   
2. Evidence Verification
   ☐ ブラウザ実機確認: Button click → Stripe Checkout
   ☐ ブラウザ実機確認: No console errors blocking UX
   ☐ ブラウザ実機確認: Multi-language pages functional
   
3. きむら博士 Approval
   ☐ Remediation evidence reviewed
   ☐ Risk assessment completed
   ☐ Closure decision rendered
   
4. Record & Archive
   ☐ CHANGE_DONE event recorded
   ☐ Evidence documented
   ☐ TODO status → 完了
```

---

## 8. Risk Mitigation

### 8.1 Risks if Boundary Unclear

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Scope creep | TODO_221 never closes | Clear definition + periodic review |
| Phase boundary blur | Phase 5 start delayed | Decision record commitment |
| Duplicate effort | Onboarding designed twice | Explicit exclusion from TODO_221 |
| Unclear ownership | Decisions delayed | きむら博士 designates Product Entry Point owner |

### 8.2 Risks if Boundary Clear

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Premature closure | User journey unmapped | Sequential start: 221 close → Entry Point start |
| Dependency missed | Phase 5 blocked late | Architecture review before Phase 5 kickoff |
| Scope mismatch | Product Entry Point defined poorly | Prototype first (design doc only, no code) |

**Conclusion**: Risks of clarity < Risks of ambiguity

---

## 9. Appendix: Boundary Definition Matrix

```
┌──────────────────────────┬─────────────────┬──────────────────────┐
│ Area                     │ TODO_221 (Phase │ Product Entry Point  │
│                          │ 4)              │ (Phase 4/5 Bridge)   │
├──────────────────────────┼─────────────────┼──────────────────────┤
│ LP Content               │ ✅ YES          │ ❌ NO                │
│ Stripe Integration       │ ✅ YES          │ ❌ NO                │
│ Multi-language i18n      │ ✅ YES          │ ❌ NO                │
│ WordPress Deployment     │ ✅ YES          │ ❌ NO                │
│                          │                 │                      │
│ User Discovery Flow      │ ✅ Include only │ ✅ Include (map)    │
│                          │    surface      │                      │
│ Purchase Decision        │ ✅ Include (CTA │ ✅ Include (design  │
│                          │    verify)      │    journey)          │
│ Installation Flow        │ ❌ NO           │ ✅ YES               │
│ First Run Experience     │ ❌ NO           │ ✅ YES               │
│ Continued Usage Design   │ ❌ NO           │ ✅ YES               │
│ Decision Lifecycle       │ ❌ NO           │ ✅ YES               │
│ Success Criteria         │ ❌ NO           │ ✅ YES               │
│                          │                 │                      │
│ Risk: Over-scope         │ ⚠️ HIGH         │ ⚠️ MEDIUM            │
│ Risk: Under-scope        │ ⚠️ LOW          │ ⚠️ LOW               │
└──────────────────────────┴─────────────────┴──────────────────────┘
```

---

## 10. Decision Request

**For きむら博士 Approval**:

```
┌─────────────────────────────────────────────────────────┐
│ HG-TODO221-BOUNDARY DECISION REQUEST                   │
│                                                         │
│ Proposal: APPROVE OPTION B                             │
│                                                         │
│ TODO_221 Action:                                        │
│ ✅ KEEP: "Product Surface Preparation"                 │
│ ✅ SCOPE: LP + Content + Stripe Integration             │
│ ✅ EXCLUDE: Onboarding + Journey Design                 │
│                                                         │
│ Product Entry Point Definition Action:                  │
│ ✅ CREATE: Independent responsibility                   │
│ ✅ SCOPE: User journey Discovery → First Success        │
│ ✅ TIMING: Start after TODO_221 institutional closure   │
│                                                         │
│ Approvals Required:                                     │
│ ☐ Phase 4/5 boundary clarity accepted                   │
│ ☐ TODO_221 closure timing confirmed                     │
│ ☐ Product Entry Point independent status confirmed      │
│ ☐ Remediation plan execution approved                   │
│                                                         │
│ Status: Ready for きむら博士 Decision                    │
└─────────────────────────────────────────────────────────┘
```

---

## Record Status

**Version**: 1.0  
**Created**: 2026-08-13T[timestamp]  
**Mode**: READ-ONLY (Judgment Material Only)  
**Committed**: NO (Awaiting きむら博士 Decision)  
**Next**: Human Gate Decision Record formalization

**Constraint Maintained**:
- ✅ No TODO changes
- ✅ No status updates
- ✅ No Decision Ledger writes
- ✅ No git commits
- ✅ Read-only documentation only

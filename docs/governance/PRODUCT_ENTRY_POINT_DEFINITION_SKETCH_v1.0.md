# Product Entry Point Definition — Initial Sketch v1.0

**Created**: 2026-08-13  
**Mode**: REFERENCE MATERIAL (Pre-Design Phase)  
**Purpose**: Support HG-TODO221-BOUNDARY decision by showing scope of independent Product Entry Point  
**Status**: Concept sketch (NOT approved, NOT committed)  
**Classification**: Judgment Material

---

## Purpose

This sketch demonstrates what "Product Entry Point Definition" would encompass if approved as independent responsibility. It supports the Human Gate decision by clarifying scope boundaries.

**This is NOT an implementation plan.**  
**This is NOT approved.**  
**This will NOT be committed.**

It exists solely to clarify what the decision enables.

---

## 1. Scope Overview

### 1.1 What It Covers

```
User Journey: Discovery → First Success

Layer 1: DISCOVERY
    └─ User finds Orchestra LP
    └─ User reads product description
    └─ User sees pricing
    └─ Decision point: Interested?

Layer 2: INTEREST
    └─ User compares with alternatives
    └─ User reads FAQ
    └─ User checks installation requirements
    └─ Decision point: Worth trying?

Layer 3: DECISION
    └─ User clicks upgrade button
    └─ User sees Stripe checkout
    └─ User enters payment info
    └─ Decision point: Confirm purchase?

Layer 4: PURCHASE
    └─ Stripe processes payment
    └─ User receives license key via email
    └─ User stores license
    └─ Decision point: Proceed to install?

Layer 5: INSTALLATION
    └─ User downloads Orchestra
    └─ User configures API keys
    └─ User runs first setup
    └─ Decision point: Setup complete?

Layer 6: FIRST RUN
    └─ User launches Orchestra
    └─ User sees onboarding tour (if any)
    └─ User creates first project/workspace
    └─ User performs first action
    └─ Decision point: Did it work?

Layer 7: FIRST SUCCESS
    └─ User sees their first result
    └─ User understands value
    └─ User decides: Continue using or abandon?
```

### 1.2 What It Excludes

- ❌ LP code changes (that's TODO_221)
- ❌ Stripe payment mechanism (that's Caliber/Worker layer)
- ❌ WordPress deployment (that's infrastructure)
- ❌ Feature development beyond "first run"
- ❌ Long-term retention strategy (that's Phase 5+)

---

## 2. Discovery Layer (TODO_221 provides the surface)

### 2.1 User Touches

```
User Experience Checkpoint:

1. User navigates to mocka.nsjp.org/mini-mocka/orchestra/
   ✓ Page loads without errors
   ✓ Hero message is clear
   
2. User scans pricing
   ✓ Plans visible: Free/Pro/One
   ✓ Price points clear: $5/$10 pricing
   
3. User reads description
   ✓ "What is Orchestra?" section understandable
   ✓ Benefit to user clear
   
4. User considers action
   ✓ CTA button visible
   ✓ CTA button accessible (not dead link)
   
Decision Gate: "Should I try this?"
```

**TODO_221 Provides**: Polished, multilingual, working LP

**Product Entry Point Adds**: User mental journey understanding

---

## 3. Interest Layer

### 3.1 FAQ & Documentation Sufficiency

**Questions User Asks**:
- "How is Orchestra different from [competitor]?"
- "What do I need to install it?"
- "Is my system compatible?"
- "How long does setup take?"
- "What if I have issues?"

**Current State**: ✅ FAQ exists (TODO_221)

**Entry Point Scope**: 
- ☐ Are FAQ answers sufficient to move user to purchase decision?
- ☐ If not, what information gaps must be filled?
- ☐ Should there be a presales checklist?
- ☐ Should there be system requirement verification?

---

## 4. Decision Layer

### 4.1 Purchase Decision Point

**Current State**: 
- ✅ Stripe payment link embedded (TODO_221 ensures this)
- ⚠️ CTA button functional (Remediation in progress)

**Entry Point Responsibility**:
- ☐ User can click upgrade button without hesitation
- ☐ Stripe Checkout experience clear (price, plan details)
- ☐ Payment success path obvious (redirects to confirmation, email receipt)
- ☐ What if payment fails? (error handling, retry options)

---

## 5. Installation Layer (Gap to Fill)

### 5.1 Current State

**What exists**: Installation instructions in FAQ/HowTo (TODO_221)

**What's missing**:
```
Gap Analysis:

1. Platform-Specific Setup
   ❌ macOS installation walkthrough
   ❌ Windows installation walkthrough
   ❌ Linux installation walkthrough
   
2. API Key Configuration
   ❌ How to get Anthropic API key (step-by-step)
   ❌ Where to paste it in Orchestra
   ❌ How to verify it's correct
   
3. Dependency Verification
   ❌ "Do I have Python 3.9+?" check
   ❌ "Do I have Node.js?" check
   ❌ What if I don't have prerequisites?
   
4. Troubleshooting During Install
   ❌ "Installation succeeded but app won't launch"
   ❌ "API key rejected"
   ❌ "Permission denied" errors
   
5. First Run Success Verification
   ❌ How do I know installation worked?
   ❌ What's the first test I should run?
```

**Entry Point Ownership**:
- Define: What should user experience during installation?
- Specify: What's the first thing user sees?
- Measure: How do we know user succeeded?

---

## 6. First Run Experience (Critical Gap)

### 6.1 The Moment of Truth

```
Timeline:

User opens Orchestra
       ↓ (5 seconds)
Does the app appear?
       ├─ YES → Onboarding tour?
       │         ↓
       │         "Welcome to Orchestra!"
       │         "Here's what you can do"
       │         "Try this first action"
       │         ↓
       │         User performs action
       │         ↓
       └─ Does it work?
       │
       └─ NO → Error message?
               ↓
               Can user self-help?
               Can user reach support?
```

**Current State**: 
- ❌ Unknown (not defined in TODO_221)

**Questions to Answer**:
- Does Orchestra show a welcome screen?
- Is there an interactive tutorial?
- What's the first workflow user should try?
- How long does first action take?
- Is result immediately visible?

---

## 7. First Success Definition

### 7.1 What Constitutes "Success"?

```
Success Scenarios (to define):

Scenario A (Deep User):
  → User creates full project
  → User runs comprehensive analysis
  → User explores all features
  → User realizes "this is powerful"
  
Scenario B (Quick Win User):
  → User completes one small task
  → User sees immediate result
  → User thinks "OK this works"
  → User decides "worth exploring more"
  
Scenario C (Skeptical User):
  → User tries minimal workflow
  → User gets expected output
  → User verifies accuracy
  → User decides "I trust this tool"
```

**Entry Point Responsibility**:
- ☐ Which scenario is realistic for first-time user?
- ☐ How do we design first run to achieve it?
- ☐ What's the minimum viable first success?

---

## 8. Decision Lifecycle at Each Layer

### 8.1 User Decision Points

```
Layer → User Question → Decision → If YES, next → If NO, result
───────────────────────────────────────────────────────────────

DISCOVERY
        ↓
"Is this for me?"
        ↓                 ↓                ↓
       YES → INTEREST   NO → Bounce

INTEREST
        ↓
"Worth trying?"
        ↓                 ↓                ↓
       YES → DECISION   NO → Bounce

DECISION
        ↓
"Ready to pay?"
        ↓                 ↓                ↓
       YES → PURCHASE   NO → Save for later

PURCHASE
        ↓
"How do I set this up?"
        ↓                 ↓                ↓
       CLEAR → INSTALL   CONFUSED → Support needed

INSTALLATION
        ↓
"Is setup working?"
        ↓                 ↓                ↓
       WORKS → FIRST RUN FAILS → Debug/Support

FIRST RUN
        ↓
"Did Orchestra work?"
        ↓                 ↓                ↓
       WORKS → RETENTION FAILED → Uninstall/Refund?
```

**Entry Point Responsibility**:
- ☐ At each decision point, what user needs to decide?
- ☐ What information do they need to decide confidently?
- ☐ What could prevent them from saying YES?
- ☐ How do we mitigate friction?

---

## 9. Success Criteria (to Define)

### 9.1 Metrics

```
Metric Categories:

DISCOVERY LAYER:
  ☐ Page load time < 3 seconds?
  ☐ Information completeness score?
  ☐ User can identify pricing in < 10 seconds?

PURCHASE LAYER:
  ☐ CTA button click rate?
  ☐ Stripe Checkout completion rate?
  ☐ Payment failure rate?

INSTALLATION LAYER:
  ☐ % of users completing install within [X] minutes?
  ☐ % of users blocked during install?
  ☐ Common failure modes (top 5)?

FIRST RUN LAYER:
  ☐ % of users launching app on first install?
  ☐ Time to first action < [X] minutes?
  ☐ First action success rate?

FIRST SUCCESS LAYER:
  ☐ % of users completing first workflow?
  ☐ % of users understanding the result?
  ☐ % of users retained after first success?
```

---

## 10. Risk Map

### 10.1 Known Drop-off Points

```
Layer          Risk                    Severity    Known Issue
───────────────────────────────────────────────────────────────
DISCOVERY      LP unclear              MEDIUM      Remediation
               Pricing confusing       LOW         Content review
               
INTEREST       Installation prereqs    HIGH        Undefined
               API key setup           HIGH        Undefined
               Platform differences    HIGH        Undefined
               
DECISION       Payment fails           MEDIUM      Remediation
               CTA dead link           HIGH        Remediation
               
INSTALLATION   Wrong Python version    HIGH        Undefined
               Missing dependencies    HIGH        Undefined
               Permission issues       MEDIUM      Undefined
               
FIRST RUN      App won't launch        HIGH        Undefined
               Onboarding missing      MEDIUM      Undefined
               First action unclear    MEDIUM      Undefined
               
FIRST SUCCESS  No visible result       HIGH        Undefined
               Result wrong/unclear    MEDIUM      Undefined
               Takes too long          MEDIUM      Undefined
```

---

## 11. Comparison: TODO_221 vs Entry Point

```
┌─────────────────┬──────────────────┬──────────────────────┐
│ Aspect          │ TODO_221         │ Entry Point Def      │
├─────────────────┼──────────────────┼──────────────────────┤
│ Focus           │ Surface exists   │ User succeeds        │
│ Artifacts       │ Deployed LP      │ Journey map          │
│ Metrics         │ Code quality     │ User completion      │
│ Success = ?     │ No errors        │ User reaches First   │
│                 │                  │ Success              │
│ Approval Path   │ きむら博士       │ UX review +          │
│                 │ technical check  │ Product decision     │
│ Duration        │ Done (remediate) │ 2-4 week design      │
│ Deliverable     │ Deployed LP      │ Journey spec doc     │
│ Leads to        │ Entry Point      │ Phase 5              │
│                 │ Design           │ Implementation       │
└─────────────────┴──────────────────┴──────────────────────┘
```

---

## 12. Next Steps (If Approved)

```
IF HG-TODO221-BOUNDARY approves Option B:

PHASE 4 (Continue):
  1. TODO_221 Remediation complete
  2. TODO_221 Human Gate closure
  3. Product Entry Point Definition begins (design phase)
  4. TIC Layer design begins (parallel)

PHASE 4/5 BRIDGE:
  5. Product Entry Point Definition review (きむら博士)
  6. If approved: Architecture for Phase 5 confirmed

PHASE 5 (Future):
  7. Product Entry Point Implementation
     → Onboarding UX
     → Installation guide refinement
     → First-run experience design
     → Success measurement dashboard
```

---

## 13. Judgment Call Assistance

**For きむら博士 Decision**:

If this sketch seems:
- ✅ **Reasonable**: Then Option B makes sense. Product Entry Point is real work.
- ⚠️ **Unclear**: Then ask Claude for specific clarifications before deciding.
- ❌ **Too much**: Then Product Entry Point should be scoped down.
- ❌ **Too little**: Then more layers should be added.

The point: **This is NOT trivial work.** It deserves separate ownership.

---

## Record Status

**Version**: 1.0  
**Created**: 2026-08-13  
**Purpose**: Reference material for decision  
**Committed**: NO (Sketch only, not approved)  
**Next**: きむら博士 review & HG-TODO221-BOUNDARY decision

**Key Constraint**: This sketch is NOT a commitment. It's illustrative only.

If きむら博士 approves Option B, then detailed Product Entry Point planning can begin.
If きむら博士 selects Option A, then these considerations fold into expanded TODO_221.

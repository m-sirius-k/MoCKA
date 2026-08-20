# MoCKA Public Information Network — Human Gate Decision Package (WEB)

**Package Date:** 2026-08-20  
**Prepared For:** Human Gate (Product Owner)  
**Classification:** Decision Support Material  
**Status:** Ready for Review & Decision  

---

## Executive Brief

This package presents the critical decisions required to finalize MoCKA's external public information boundary. All analysis is complete. Five decision points are identified with three requiring immediate attention.

**Time to Decision:** ~30 minutes for review + decision  
**Decision Deadline:** Recommend 2026-08-21  
**Implementation Impact:** Determines Layer 1-3 publication scope for Phase 1-3 roadmap  

---

## Decision Point 1: PUBLIC LAYER Definition — "What Should Everyone See?"

### The Question

Should MoCKA's public-facing information prioritize:
- **A: Maximum Transparency** — Publish everything except decision ledger/incidents
- **B: Focused Clarity** — Publish only essential (philosophy, products, architecture overview)
- **C: Minimal Disclosure** — Publish only README + links to academic papers

### Context

**Current State:**
- README.md exists (bilingual, comprehensive)
- Products exist but undocumented (8 products)
- Architecture documented locally but not published
- Repository strategy unexplained (12 repos unknown)

**Analysis:**

| Approach | External Trust | Maintenance Cost | Discoverability | Risk |
|----------|---|---|---|---|
| **A: Maximum** | HIGH | MEDIUM | HIGH | Some internal info might leak |
| **B: Focused** | MEDIUM-HIGH | LOW | MEDIUM-HIGH | Product docs missing |
| **C: Minimal** | LOW | LOW | LOW | MoCKA appears incomplete |

**Comparison to Peer Systems:**

| System | Disclosure Level | Typical Approach |
|--------|---|---|
| Apache project | Maximum transparency | Full docs public, decisions public, design reasoning shared |
| Academic research | Selective disclosure | Papers public, code public, internal notes private |
| Commercial SaaS | Focused clarity | Product docs public, architecture private, decisions private |
| Government systems | Minimal disclosure | Security-first, limited docs, decision process private |

### Recommendation

**Recommend: Approach B (Focused Clarity)**

**Rationale:**
1. MoCKA's core philosophy is already clear (README does this well)
2. Product ecosystem is production-ready (needs documentation to be valuable)
3. Architecture documents can be published without leaking decision process
4. Balanced approach: transparency about *what* without exposing *how we decide*

**Risk Mitigation:**
- If in doubt about what's safe to publish, defer to Layer 2 (authorized) or Layer 3 (internal)
- Create guidelines before writing product docs (prevent accidental information leakage)
- Review all public docs for references to private decision records

---

## Decision Point 2: Layer 2 (AUTHORIZED) Access Model — "Who Gets Architecture Details?"

### The Question

Should detailed architecture documentation be:
- **A: Public** (no login required, same as README)
- **B: Contributor-only** (GitHub login required)
- **C: Restricted** (email allowlist or explicit approval)
- **D: Deferred** (keep internal for now, publish later)

### Context

**What's in Layer 2:**
- GOVERNANCE_BASELINE.md (governance framework)
- SEMANTIC_LAYER.md through LEARNING_KERNEL.md (design layers)
- Integration guides (API specs, product integration)
- Repository architecture explanation

**Why This Matters:**
- External researchers need specs to build compatible systems
- Contributors need architecture to understand code
- Commercial integrators need integration guides
- Academics need design rationale for citations

**Risk Assessment:**

| Content | Security Risk | Business Risk | Confidentiality Risk |
|---------|---|---|---|
| GOVERNANCE_BASELINE.md | NONE | LOW (shows architecture) | NONE (design, not decisions) |
| SEMANTIC/Decision/Memory layers | NONE | LOW (shows thinking process) | NONE (design, not secrets) |
| Integration guides | NONE | NONE | NONE |
| **Decision rationale** | NONE | MEDIUM (competitive) | HIGH (reveals thinking) |
| **Incident registry** | HIGH | HIGH | HIGH |
| **Decision ledger** | NONE | HIGH (lobbying target) | HIGH (internal authority) |

**Key Insight:** Architecture documents have **zero confidentiality risk** if decision rationale is redacted.

### Recommendation

**Recommend: Approach A (Public)**

**Rationale:**
1. Architecture is design (no secrets, no decisions)
2. Publishing attracts researchers and contributors
3. Transparency about *how it works* builds trust
4. No security or business risk identified
5. Easy to revise if risk later emerges (GitHub history preserved)

**Conditions:**
1. Create "Product Documentation Guidelines" before writing product docs
2. Guidelines must prevent leakage of decision process / incident details
3. All public docs reviewed for decision-ledger references
4. Redact any references to "who decided what"

---

## Decision Point 3: mocka.nsjp.org Integration — "What Is the Web Domain For?"

### The Question

Should mocka.nsjp.org serve as:
- **A: Public Gateway** (landing page, redirects to GitHub)
- **B: Documentation Portal** (hosts architecture docs, with or without login)
- **C: Product Platform** (product store, Stripe checkout, Slack integration)
- **D: Do Not Use** (remove from public reference, keep internal only)
- **E: Clarify First** (verify existence + current purpose before deciding)

### Context

**Current Status:**
- Listed in OVERVIEW.json server_config as localhost:5000
- No public URL documented
- Accessible status: **UNVERIFIED**
- Current purpose: **UNKNOWN**

**Design Options Analysis:**

#### Option A: Public Gateway
```
mocka.nsjp.org → Landing page
  ├→ "What is MoCKA?" (explanation)
  ├→ "Products" (Orchestra, Relay, etc.)
  ├→ "Documentation" (→ GitHub /docs or wiki)
  └→ "Community" (→ GitHub issues)

Benefits:
- Single URL for non-technical audiences
- Marketing-friendly (mobile-optimized)
- Decouples from GitHub (can survive repo restructure)

Costs:
- Requires HTTPS + domain management
- Needs SEO optimization
- Redirect overhead
```

#### Option B: Documentation Portal
```
mocka.nsjp.org/docs → Architecture docs
  ├→ Semantic Layer docs
  ├→ Decision Layer docs
  ├→ Memory Layer docs
  └→ Integration guides

Benefits:
- Faster load than GitHub wiki
- Can implement syntax highlighting
- Version history per doc
- Search across all docs

Costs:
- Requires static site generator or CMS
- Sync with GitHub (docs live here or there?)
- Access control if restricted (OAuth setup)
```

#### Option C: Product Platform
```
mocka.nsjp.org → Product store
  ├→ Orchestra ($5/mo checkout)
  ├→ Relay ($10/mo checkout)
  ├→ PHI-OS (Chrome Web Store link)
  └→ Memory (Chrome Web Store link)

Benefits:
- Direct monetization (Stripe already integrated)
- Product landing pages
- Documentation per product

Costs:
- OVERVIEW says Stripe integration exists but no docs
- Requires product marketing copy
- Domain serves marketing, not docs
```

#### Option D: Do Not Use
```
Remove mocka.nsjp.org from public references
Keep internal-only for localhost:5000

Benefits:
- No domain management overhead
- No confusion about multiple entry points

Costs:
- GitHub becomes only entry point
- No marketing landing page
- External users must navigate GitHub
```

#### Option E: Clarify First
```
Verify:
1. Does mocka.nsjp.org currently exist and resolve?
2. Is it HTTPS or HTTP?
3. What content currently exists?
4. Who manages it?

Then decide A/B/C/D above based on current state.
```

### Recommendation

**Recommend: Option E (Clarify First) → Option A (Public Gateway)**

**Rationale for Option E:**
- Current status is genuinely unknown
- Decision should be based on facts, not assumptions
- Takes 5 minutes to verify, informs all downstream decisions

**Rationale for Option A (after verification):**
- MoCKA's audience includes non-technical users (product adopters)
- GitHub is intimidating for non-developers
- Landing page is standard practice for technology projects
- Low cost (GitHub Pages could serve the gateway)

**Action Required:**
1. Product owner to verify mocka.nsjp.org (exist? HTTPS? current use?)
2. If exists: decide A/B/C/D above
3. If doesn't exist: decision is "create as A" or "skip"

---

## Decision Point 4: Repository Visibility — "Which Repos Should Be Public?"

### The Question

Of the 12 repositories managed by MoCKA, how many should be public?

**Known Repositories (from OVERVIEW.json):**

| Repo | Current Status | Tier Proposed | Public? | Documented? |
|------|---|---|---|---|
| m-sirius-k/MoCKA | Listed | Tier 1 (core) | YES | YES (README) |
| mocka-civilization | Listed | Tier 2 | UNKNOWN | NO |
| mocka-transparency | Listed | Tier 2 | UNKNOWN | NO |
| mocka-external-brain | Listed | Tier 2 | UNKNOWN | NO |
| mocka-core-private | Listed | Tier 3 (private) | UNKNOWN | NO |
| mocka-public | Listed | Tier 1 (public docs) | UNKNOWN | NO |
| mocka-knowledge-gate | Listed | Tier 2 | UNKNOWN | NO |
| mocka-outfield | Listed | Tier 2 (public network) | UNKNOWN | NO |
| vasAI | Listed | Tier 1 | YES (claimed v1.4.9) | PARTIAL (Zenodo DOI) |
| planningcaliber | Listed | Tier 3 (workshop) | UNKNOWN | NO |
| mocka-joints | Listed | Tier 2 (integration) | UNKNOWN | NO |
| mocka-archive | Listed? | Unknown | UNKNOWN | NO |

**Three Strategies:**

### Strategy A: Maximize Disclosure
- Make all non-sensitive repos public
- Pros: Maximum transparency, easier collaboration
- Cons: Must document all 12 repos, explains "why some are private"
- Recommendation: PUBLIC = MoCKA, mocka-civilization, mocka-transparency, mocka-external-brain, mocka-public, mocka-knowledge-gate, mocka-outfield, vasAI, mocka-joints (9 repos)

### Strategy B: Core + Essential Only
- Public: MoCKA (core), mocka-public (docs), vasAI (research)
- Authorized: Others (contributor access)
- Private: mocka-core-private, planningcaliber (internal)
- Pros: Reduces complexity, easier to manage
- Cons: External users see limited ecosystem
- Recommendation: PUBLIC = 3 repos

### Strategy C: Core Only
- Public: MoCKA, vasAI
- Everything else: Private or internal
- Pros: Simplest to maintain
- Cons: MoCKA appears isolated, ecosystem invisible
- Recommendation: PUBLIC = 2 repos

### Recommendation

**Recommend: Strategy A (Maximize Disclosure)**

**Rationale:**
1. Repository names suggest publication readiness (mocka-public, mocka-outfield)
2. OVERVIEW lists all 12, suggesting they're managed artifacts
3. Research/academic access needs visibility
4. Transparency builds ecosystem trust
5. Can be revised later if issues emerge

**Action Required:**
1. Audit all 12 repositories: GitHub → check "Public" setting
2. For each: decide public/private based on content
3. Create REPOSITORY_MAP.md explaining each tier
4. Link Tier 1/2 repos from main README

---

## Decision Point 5: Unknown Items Disclosure — "How Explicit Should 'Unknown' Be?"

### The Question

When documenting unknowns (Phase 5/6 features, unfinished layers, etc.), how detailed should disclosure be?

**Three Levels:**

### Level 1: Minimal
```
"Phase 5: Coming soon"
"Phase 6: Future roadmap"
```
- Pros: Simple, no overcommitment
- Cons: Users can't plan around unknowns

### Level 2: Moderate (Recommended)
```
"Phase 5: Post-Learning Kernel (autonomous evolution)"
"Phase 6: TBD (awaiting Phase 5 completion)"
"TIC Layer 2-4: Sandbox, impact analyzer, human gate UI (in development)"
"PR-OS WordPress: Credentials setup pending"
```
- Pros: Transparent without overcommitting
- Cons: Requires updating as things progress

### Level 3: Detailed
```
"Phase 5 (est. Q4 2026): Self-Learning Kernel
  - Turns feedback into weight updates
  - Learning queue (approval required)
  - Kernel update with rollback capability
  
Phase 6 (est. Q1 2027): Unknown
  - Proposal: Autonomous evolution protocol
  - Dependencies: Phase 5 complete + governance approval
  
TIC Layer 2-4 (Q3 2026):
  - Layer 2: Sandbox environment
  - Layer 3: Impact analyzer
  - Layer 4: COMMAND CENTER UI
  
PR-OS WordPress (blocking):
  - Issue: Credentials configuration required
  - Workaround: None (feature incomplete)
  - ETA: TBD
```
- Pros: Full transparency, users can plan/contribute
- Cons: Requires accuracy, frequent updates needed

### Recommendation

**Recommend: Level 2 (Moderate)**

**Rationale:**
1. More informative than Level 1, less maintenance than Level 3
2. Balances transparency with flexibility
3. Easy to update per-commit
4. Matches academic research paper standards

---

## Risk Assessment: External User Perspective

### Misunderstanding Risk

**Scenario 1: User visits GitHub, sees 12 repos**
- Current: No explanation of relationship → Confusion
- With Strategy A + REPOSITORY_MAP: Clear explanation → No confusion
- Risk: **HIGH** → **LOW** (with REPOSITORY_MAP)

**Scenario 2: User reads README, wants to contribute**
- Current: No CONTRIBUTING.md → Unclear how to start
- With guidelines: Explicit entry points → Clear
- Risk: **MEDIUM** → **LOW** (with CONTRIBUTING.md)

**Scenario 3: User reads "Phase 5 TBD" in docs**
- Current: Appears unfinished/abandoned
- With Level 2 disclosure: Clear it's planned → Realistic expectations
- Risk: **MEDIUM** → **LOW** (with moderate disclosure)

**Scenario 4: User finds Zenodo paper, reads 2-year-old version**
- Current: No version-lock documented → Confusion about code state
- With version-lock + date notes: Clear version → No confusion
- Risk: **MEDIUM** → **LOW** (with documentation)

### Provenance Risk

**Scenario 1: User asks "Is this still maintained?"**
- Current: Last commit date visible → Easy to check
- Risk: **LOW** (GitHub shows activity)

**Scenario 2: User asks "Which docs are current?"**
- Current: No date stamps → Unclear
- With date stamps: Clear freshness → No confusion
- Risk: **MEDIUM** → **LOW** (with date stamps)

**Scenario 3: User asks "Is the paper version same as code?"**
- Current: No link/version → Unclear
- With version-lock: Clear relationship → No confusion
- Risk: **MEDIUM** → **LOW** (with documentation)

---

## Summary: Five Decisions → One Implementation Path

### Decisions Required

| # | Decision | Options | Recommended | Blocker? |
|---|----------|---------|-------------|----------|
| 1 | PUBLIC LAYER scope | A/B/C | **B (Focused Clarity)** | NO |
| 2 | AUTHORIZED LAYER access | A/B/C/D | **A (Public)** | NO |
| 3 | mocka.nsjp.org role | A/B/C/D/E | **E then A** | YES (needs verify first) |
| 4 | Repository visibility | A/B/C | **A (Maximize Disclosure)** | YES (needs audit) |
| 5 | Unknown disclosure level | 1/2/3 | **2 (Moderate)** | NO |

### Critical Path (What Blocks Implementation)

```
Decision 3 (mocka.nsjp.org) requires verification
    ↓ (product owner action)
Decision 4 (Repository audit) requires enumeration
    ↓ (engineering lead action)
Decisions 1, 2, 5 can proceed immediately
    ↓
Create documentation guidelines (prevents leakage)
    ↓
Phase 1-3 implementation can begin
```

### Timeline

**Today (2026-08-20):** Approve Decisions 1, 2, 5  
**Tomorrow (2026-08-21):** Verify Decision 3, audit Decision 4  
**This week:** Create guidelines, finalize repo strategy  
**Weeks 3-8:** Execute Phase 1-3 per roadmap  

---

## Appendix: Reference Materials

### Documents Supporting This Decision Package

1. **MOCKA_INFORMATION_NETWORK_ASSESSMENT_WEB.md** — Current state analysis (B-level visibility)
2. **MOCKA_PUBLIC_INFORMATION_MAP.md** — Three-layer framework + implementation roadmap
3. **MOCKA_INFORMATION_NETWORK_INTEGRATION_REVIEW_WEB.md** — Policy alignment confirmation

### Decision Records to Create

After Human Gate decisions are made:
1. Create REPOSITORY_MAP.md (explains all 12 repos)
2. Create CONTRIBUTING.md (how to get involved)
3. Create Product Documentation Guidelines (prevent leakage)
4. Update README.md (link to new docs per decision)
5. Finalize mocka.nsjp.org setup (per Decision 3)

---

## Next Steps

**For Product Owner (きむら博士):**

1. [ ] **Review this package** (30 min)
2. [ ] **Verify mocka.nsjp.org** (5 min)
3. [ ] **Make Decisions 1, 2, 3, 5** (10 min)
4. [ ] **Approve proceeding to Phase 1** (2 min)

**For Engineering Lead:**

1. [ ] **Audit 12 repositories** (1 hour)
2. [ ] **Report public/private status**
3. [ ] **Confirm vasAI v1.4.9 is public**

**For Documentation Lead:**

1. [ ] **Create Product Documentation Guidelines**
2. [ ] **Create REPOSITORY_MAP.md**
3. [ ] **Create CONTRIBUTING.md**

**Total Time to Implementation:** ~2 hours (with parallel actions)

---

**Package Status:** READY FOR HUMAN GATE DECISION  
**Target Approval Date:** 2026-08-21  
**Implementation Start:** 2026-08-22  


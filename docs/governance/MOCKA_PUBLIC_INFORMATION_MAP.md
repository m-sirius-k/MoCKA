# MoCKA Public Information Map — Three-Layer Boundary Definition

**Document Date:** 2026-08-20  
**Classification:** Policy Document (Public)  
**Status:** Draft for Human Gate Review  
**Based On:** MOCKA_INFORMATION_NETWORK_ASSESSMENT_WEB.md  

---

## Executive Summary

This document defines the three-layer public information boundary for MoCKA, establishing which information should be public, which requires authorization, and which remains in canonical (internal) control.

The framework enables MoCKA to:
1. Build external trust through transparent discoverability
2. Protect critical governance decisions from external noise
3. Maintain architectural coherence across distributed knowledge
4. Create clear entry points for external audiences

---

## Part 1: Three-Layer Information Architecture

### Layer 1: PUBLIC LAYER — Unrestricted External Access

**Purpose:** Make MoCKA discoverable, understandable, and trustworthy to external audiences.

**Audience:** Everyone (GitHub visitors, academic researchers, potential contributors, product users)

**Control:** GitHub public repositories + public web domain (mocka.nsjp.org)

**Principle:** Information in this layer should answer "What is MoCKA?" and "Why should I care?"

#### Layer 1 Contents — Current & Proposed

| Content Type | Current | Public? | Proposed Status | Responsibility |
|--------------|---------|---------|-----------------|-----------------|
| **README.md** | m-sirius-k/MoCKA | YES | KEEP PUBLIC | GitHub |
| **Architecture diagrams** (6x SVG) | Embedded in README | YES | KEEP PUBLIC | GitHub |
| **Quick Start guide** | README section | YES | KEEP PUBLIC | GitHub |
| **Governance Charter v2.0** | Referenced, local file | NO | PUBLISH (extract summary) | Product owner |
| **Product overview** | Not documented | NO | CREATE + PUBLISH | Product owner |
| **AIES 2026 paper** | Zenodo DOI | YES | KEEP PUBLIC + LINK | GitHub |
| **vasAI v1.4.9** | GitHub repo (claimed) | UNKNOWN | VERIFY + LINK | GitHub |
| **Problem statement** | README section | YES | KEEP PUBLIC | GitHub |
| **Civilization loop diagram** | Embedded in README | YES | KEEP PUBLIC | GitHub |
| **Use cases** | Not documented | NO | CREATE (optional) | Product owner |

#### Layer 1 Success Metrics

- [ ] External visitor can answer "What is MoCKA?" within 3 minutes
- [ ] README mentions all 8 products (Orchestra, Relay, etc.)
- [ ] Links to product-specific documentation exist
- [ ] Unknown/future work is explicitly marked
- [ ] Governance philosophy is explained (not just referenced)
- [ ] Contribution guidelines exist
- [ ] License is clear (CC BY-NC? MIT? Custom?)

---

### Layer 2: AUTHORIZED LAYER — Conditional Access

**Purpose:** Share detailed architectural and operational knowledge with stakeholders who need depth without exposing decision-making processes.

**Audience:** Contributors, research partners, commercial integrators, academia

**Control:** GitHub private repositories (if needed) + documentation portals with access controls

**Principle:** Information in this layer should answer "How does MoCKA work?" and "Can I build on it?"

#### Layer 2 Contents — Current & Proposed

| Content Type | Current | Public? | Proposed Status | Responsibility |
|--------------|---------|---------|-----------------|-----------------|
| **Architecture documentation** (Semantic/Decision/Memory/Self-Audit/Feedback/Learning layers) | Local files (20+) | NO | PUBLISH AS AUTHORIZED (option A: public, option B: contributor access) | Architecture lead |
| **Governance Baseline v1.1** | Referenced, local | NO | PUBLISH AS AUTHORIZED | Governance lead |
| **GL1-7 Integration Test results** | Local tests | NO | PUBLISH SUMMARY (redacted) | QA lead |
| **Design decision rationale** | Internal only | NO | PUBLISH SUBSET (key decisions, not all) | Architecture lead |
| **API specifications** | Not documented | NO | CREATE IF PUBLIC APIs exist | API owner |
| **Integration guide** | Not documented | NO | CREATE (Orchestra, Relay, etc.) | Product owner |
| **Phase 2-4 Roadmap** | OVERVIEW.json only | NO | PUBLISH (high-level, no timelines) | Product owner |
| **Security audit reports** (if any) | Not public | NO | PUBLISH SUMMARY (redacted for OPSEC) | Security lead |
| **Repository architecture** (12 repos) | OVERVIEW.json only | NO | PUBLISH STRATEGY + RELATIONSHIP MAP | Engineering lead |
| **Test coverage metrics** | Local only | NO | PUBLISH DASHBOARD (optional) | QA lead |

#### Layer 2 Success Metrics

- [ ] Potential contributors understand MoCKA architecture
- [ ] Research partners can design compatible systems
- [ ] Product integrators have technical specifications
- [ ] Design decisions are traceable to rationale
- [ ] Repository strategy is clear and documented

---

### Layer 3: CANONICAL CORE — Internal Governance (NOT PUBLIC)

**Purpose:** Maintain institutional integrity by keeping decision-making, incident analysis, and governance evidence internal.

**Audience:** MoCKA governance bodies (Product owner, Architecture Lead, Governance Lead)

**Control:** Local filesystem + private MCP services (mocka_mcp_server)

**Principle:** Information in this layer is the source of truth but remains strategically private to prevent external influence on internal governance.

#### Layer 3 Contents — MUST REMAIN INTERNAL

| Content Type | Current | Status | Rationale |
|--------------|---------|--------|-----------|
| **Decision Ledger** (mocka_decision_write/get) | events.db | STAY INTERNAL | Source of governance truth; publishing creates external lobbying incentive |
| **Incident registry** (mocka_get_incidents) | events.db | STAY INTERNAL | Security/vulnerability disclosures require strategic timing |
| **Living Context snapshots** (ESSENCE, PHILOSOPHY) | infield/outfield | STAY INTERNAL | Operational state; premature disclosure can mislead |
| **All governance audit logs** | governance/anchor_record.json | STAY INTERNAL | Audit trail is for institutional accountability, not public consumption |
| **Phase 5/6+ design documents** | In-progress | STAY INTERNAL | Unfinalized decisions should not constrain external ecosystem |
| **Personnel/team decisions** (who owns what) | Not documented | STAY INTERNAL | Role clarity is internal, not external branding |
| **Private key material** (GPG, signatures) | governance/ | STAY INTERNAL | Cryptographic secrets must be protected |
| **Full recurrence registry** (87+ entries) | data/recurrence_registry.csv | STAY INTERNAL | Pattern analysis could leak implementation insights |
| **Complete commit history analysis** | git log | STAY INTERNAL | Development history may reveal vulnerabilities |

#### Layer 3 Success Metrics

- [ ] No decision-ledger entries are accidentally published
- [ ] Incident registry remains internal-only
- [ ] Governance audit trail is not exposed
- [ ] Future roadmap (Phase 5/6) does not leak
- [ ] Architectural secrets (if any) are protected

---

## Part 2: Content Mapping — Which Document Goes Where?

### Public Layer (GitHub) — Immediate Actions

**Already Public (KEEP):**
- README.md (bilingual)
- 6 embedded SVG diagrams
- LICENSE file (verify clarity)

**Should Be Public (CREATE):**

1. **PRODUCTS_OVERVIEW.md**
   - Brief overview: Orchestra, Relay, PHI-OS, Memory, PR-OS, SEO-OS
   - Link to individual product READMEs (create stubs if needed)
   - 200 words per product

2. **ARCHITECTURE_INDEX.md**
   - Roadmap to architecture documentation
   - "Public" vs "Authorized" markup
   - Why certain docs are internal

3. **UNKNOWNS_AND_ROADMAP.md**
   - Phase 5/6 placeholders (no spoilers)
   - Timeline for new documentation
   - Repository expansion strategy
   - How to report issues/improvements

4. **CONTRIBUTING.md**
   - Contribution guidelines
   - Code of conduct
   - Setup instructions

5. **REPOSITORY_MAP.md**
   - Explain 12-repository structure
   - Dependency graph
   - Which repos are canonical vs experimental

### Authorized Layer (Documentation Portal) — Create New Portal

**To Be Published (conditional access):**
- GOVERNANCE_BASELINE.md (full text)
- SEMANTIC_LAYER.md (full text)
- DECISION_LAYER.md (full text)
- MEMORY_LAYER.md (full text)
- SELF_AUDIT_LAYER.md (full text)
- FEEDBACK_LOOP.md (full text)
- LEARNING_KERNEL.md (full text)
- EVENT_INTEGRITY_v1.md (full text)
- GATE_ARCHITECTURE_v1.md (full text)
- GL_INTEGRATION_TEST results (summary)
- API specifications (when available)
- Integration guides (per product)
- Phase 2-4 High-level Roadmap

**Option A:** Publish as public (same as Layer 1) — GitHub wiki or `/docs` subdirectory  
**Option B:** Publish as authorized (contributor access) — GitHub private docs or external portal with login

**Recommendation:** Option A (public) — Transparency over secrecy builds trust. Authorize via contribution, not via access control.

### Canonical Core (Internal) — DO NOT PUBLISH

- Decision Ledger (mocka_decision_write records)
- Incident Registry (mocka_get_incidents)
- Event database (events.db)
- Governance anchors (anchor_record.json)
- Living Context snapshots (ESSENCE, PHILOSOPHY)
- Private keys / signatures
- Complete commit history (keep git history, don't analyze publicly)

---

## Part 3: Domain Integration — mocka.nsjp.org

### Current State

- **Status:** Mentioned in server_config (localhost:5000)
- **Accessibility:** UNVERIFIED (not linked from GitHub)
- **Purpose:** UNKNOWN

### Proposed Integration

#### Option A: mocka.nsjp.org as PUBLIC Layer Gateway

```
User lands on mocka.nsjp.org
    ↓
Main landing page (what is MoCKA?)
    ├→ Quick start (→ GitHub README)
    ├→ Product pages (Orchestra, Relay, etc.)
    ├→ Documentation (→ GitHub /docs or wiki)
    ├→ Academic papers (→ Zenodo DOI links)
    ├→ Community (→ GitHub issues/discussions)
    └→ Contact (→ info@nsjp.org?)

Benefits:
- Single entry point for non-technical audiences
- Decouples marketing from code repository
- Mobile-friendly, SEO-optimized
- Legal disclaimers & terms of service (if needed)

Requirements:
- https:// only
- HTTPS redirect from GitHub link
- Analytics (optional, privacy-respecting)
- No cookies / tracking (minimal)
```

#### Option B: mocka.nsjp.org as Authorized Layer Portal

```
User lands on mocka.nsjp.org/docs
    ↓
Architecture documentation portal (conditional access)
    ├→ Semantic/Decision/Memory/Self-Audit layers
    ├→ Governance baseline
    ├→ Integration guides
    ├→ Research papers & citations
    └→ API documentation

Requirements:
- GitHub OAuth login (contributors only)
- Or: email allowlist (researchers)
- Or: public with "beta" label (transparency)

Recommendation:
- Start with public (no login required)
- Add analytics to see who reads what
- Consider login only if sensitive content appears
```

#### Option C: mocka.nsjp.org as Product Platform

```
User lands on mocka.nsjp.org
    ↓
Product store / marketplace
    ├→ Orchestra (pricing, features, docs)
    ├→ Relay (pricing, features, docs)
    ├→ PHI-OS (Chrome Web Store link)
    ├→ Memory (Chrome Web Store link)
    └→ PR-OS / SEO-OS (future)

Requirements:
- Payment processing (Stripe, already integrated per OVERVIEW)
- Product documentation (currently missing)
- API keys / authentication management
- Support portal

Note: OVERVIEW mentions Orchestra already has Stripe integration.
```

### Recommended Plan

**Immediate (Q3 2026):**
1. Clarify whether mocka.nsjp.org currently exists and is live
2. Document its current purpose in REPOSITORY_MAP.md
3. Link it from GitHub README if public-ready

**Short-term (Q4 2026):**
1. Decide: Gateway (A) or Portal (B) or Product Platform (C)?
2. Create placeholder content
3. Set up HTTPS and security headers
4. Implement analytics (privacy-respecting)

**Medium-term (Q1 2027):**
1. Publish public-layer documentation to mocka.nsjp.org
2. Link back to GitHub for source code
3. Create SEO-optimized landing page

---

## Part 4: Repository Visibility Map

### Current Repository Status (From OVERVIEW.json)

| Repository | Public? | Role | Verified? | Recommendation |
|------------|---------|------|-----------|-----------------|
| m-sirius-k/MoCKA | YES | Core (heart) | YES | Keep public, enhance README |
| mocka-civilization | UNKNOWN | Blueprint layer | NO | Clarify & link from README |
| mocka-transparency | UNKNOWN | Tamper detection | NO | Clarify & link from README |
| mocka-external-brain | UNKNOWN | AI orchestration | NO | Clarify & link from README |
| mocka-core-private | MARKED PRIVATE | Experimental | N/A | Keep private (as marked) |
| mocka-public | UNKNOWN | Public docs layer | NO | Clarify & link from README |
| mocka-knowledge-gate | UNKNOWN | Institutional memory | NO | Clarify & link from README |
| mocka-outfield | UNKNOWN | Public network layer | NO | Clarify & link from README |
| vasAI | CLAIMED PUBLIC | Enterprise AI system | PARTIAL | Verify & link (v1.4.9 claimed) |
| planningcaliber | MARKED PRIVATE | Workshop/manufacturing | N/A | Keep private (as marked) |
| mocka-joints (various) | UNKNOWN | Integration layer | NO | Clarify & link from README |
| mocka-archive | UNKNOWN | Historical | NO | Clarify & link from README |

### Repository Visibility Strategy

**Tier 1 (MUST be public):**
- m-sirius-k/MoCKA (core)
- vasAI (academic release already public)

**Tier 2 (SHOULD be public):**
- mocka-civilization (architecture/design)
- mocka-transparency (research/demo)
- mocka-external-brain (AI capabilities)
- mocka-public (documentation layer)
- mocka-knowledge-gate (institutional memory)
- mocka-outfield (public network)

**Tier 3 (Keep private):**
- mocka-core-private (experimental/sandbox)
- planningcaliber (manufacturing/workshop)

**Tier 4 (Clarify):**
- mocka-joints subfolder repos
- mocka-archive (if it exists)

### Action Items

1. [ ] Audit all 12 repositories for access level (product owner)
2. [ ] Create REPOSITORY_MAP.md explaining each
3. [ ] Update GitHub organization settings (visibility)
4. [ ] Link Tier 1 & 2 repos from main README
5. [ ] Add badges showing repo relationships (optional)

---

## Part 5: Governance Transparency vs. Secrecy Trade-off

### Decision: What Principles Guide Public/Private?

**Principle 1: Trustworthiness**
- Higher transparency → Higher external trust
- But: Unfinalized decisions appear chaotic
- Balance: Publish past decisions, not future ones

**Principle 2: Operational Security**
- Some decisions must stay private (e.g., incident response)
- Security through obscurity is weak
- Balance: Publish architecture, not vulnerabilities

**Principle 3: External Noise**
- Published decisions become lobbying targets
- "Why didn't you choose option X?"
- Balance: Document rationale, not process

**Principle 4: Institutional Integrity**
- Decision Ledger is source of truth
- Keeping it internal prevents external influence
- Balance: Publish summaries, keep voting records private

### Recommended Stance

**For MoCKA:**
```
TRANSPARENT on architecture (answer: how does it work?)
TRANSPARENT on philosophy (answer: why MoCKA?)
TRANSPARENT on products (answer: what can I use?)

PRIVATE on decision process (answer: who decides? vote counts?)
PRIVATE on incident responses (answer: what broke?)
PRIVATE on future roadmap (answer: what's next?)
```

### Publication Guidelines

| Question | Public Answer | Private Reason |
|----------|---------------|-----------------|
| "What is MoCKA?" | Full philosophical framework | N/A (always public) |
| "How does it work?" | Architecture diagrams + design docs | N/A (transparent) |
| "Can I integrate?" | API specs + integration guide | N/A (transparent) |
| "Why did you choose X over Y?" | Design rationale document | Save the full decision ledger (internal) |
| "What's the roadmap?" | "Phase 5 (TBD), Phase 6 (TBD)" | Avoid external pressure on timelines |
| "What broke?" | "We had an incident, fixed it" | Redact technical details (security) |
| "Who decides?" | "Product owner + Architecture lead" | Don't publish voting records |

---

## Part 6: Information Boundary Integrity

### How to Enforce Boundaries

#### Automated Checks (GitHub Actions)

```yaml
# Prevent accidental commits to Tier 3 (private repos)
# Prevent publishing decision_ledger entries
# Validate no private keys in public commits
# Check: all public README links are valid
```

#### Manual Reviews (Human Gate)

```
Before publishing to Layer 1 or 2:
1. Security review (no keys/secrets)
2. Completeness check (no dangling references)
3. Consistency review (does it match architecture?)
4. Audience check (is it accessible to intended readers?)
```

#### Documentation Standards

- All public docs must have "This is public" header
- All Layer 2 docs must have "Authorized access required" header
- No Layer 3 (private) info should appear in public docs

### Audit Trail

**Record:** Every public documentation publish should be logged:
- What: document name, content summary
- When: date/time
- Who: author (human or AI)
- Why: purpose/rationale
- Event: mocka_write_event entry

---

## Part 7: Transition Plan — From B to A

### Current State (B: Distributed but Traceable)
- Central hub: m-sirius-k/MoCKA ✓
- Distributed echoes: Zenodo, academia ✓
- Product ecosystem: invisible ✗
- Unknowns: implicit ✗
- Repository strategy: unexplained ✗

### Target State (A: Single Source Clear)
- Central hub: m-sirius-k/MoCKA + mocka.nsjp.org
- Information layer clarity: Public/Authorized/Internal marked
- Product ecosystem: documented & discoverable
- Unknowns: explicitly stated ("Phase 5 TBD")
- Repository strategy: explained & linked

### Implementation Roadmap

**Week 1-2 (Immediate):**
1. [ ] Verify mocka.nsjp.org status (product owner)
2. [ ] Audit repository visibility (engineering lead)
3. [ ] Categorize all 20+ documentation files (architecture lead)

**Week 3-4 (Short-term):**
1. [ ] Create PRODUCTS_OVERVIEW.md (product owner)
2. [ ] Create REPOSITORY_MAP.md (engineering lead)
3. [ ] Create UNKNOWNS_AND_ROADMAP.md (product owner)
4. [ ] Enhance main README.md (all)

**Week 5-8 (Medium-term):**
1. [ ] Create/publish product READMEs (product owner per product)
2. [ ] Publish ARCHITECTURE_INDEX.md (architecture lead)
3. [ ] Set up mocka.nsjp.org gateway (infrastructure lead)
4. [ ] Link all Layer 1 & 2 docs (documentation owner)

**Week 9+ (Long-term):**
1. [ ] Monitor external feedback (product owner)
2. [ ] Iterate on documentation (all)
3. [ ] Plan Phase 5 communication (product owner)

---

## Part 8: Success Metrics

### Discoverability (External Perspective)

```
Test: Random developer finds MoCKA on GitHub
- Can they understand what it is? (Y/N)
- Can they find all products? (Y/N)
- Can they find integration guides? (Y/N)
- Can they find decision rationale? (Y/N)
- Can they see the roadmap (without spoilers)? (Y/N)
```

**Target:** 5/5 "Yes" answers

### Accessibility (Reading Level)

```
Test: Readability audit
- README: 12th grade level (target for technical)
- Products: 10th grade level (target for users)
- Architecture: University level (target for developers)
- Philosophy: High school level (target for anyone)
```

**Tool:** readability checker (Flesch-Kincaid or similar)

### Completeness (Coverage)

```
Test: Documentation gaps
- Product docs: 8/8 exist (Orchestra, Relay, PHI-OS, Memory, etc.)
- Architecture docs: 10/10 core layers documented
- Repository docs: 12/12 repos explained
- Integration docs: 5/5 major integrations covered
- Roadmap: Phase 5/6 explicitly marked as "TBD" or "Coming"
```

**Target:** 95%+ coverage

### Trust (External Signals)

```
Test: Community indicators
- GitHub stars: growing (Y/N)
- Academic citations: present (Y/N)
- Commercial interest: visible (Y/N)
- Contribution PRs: increasing (Y/N)
- Security audits: published (Y/N)
```

**Target:** 3+ signals increasing by Q1 2027

---

## Conclusion

This information map establishes three clear boundaries:

1. **PUBLIC LAYER** — Unrestricted access (philosophy, architecture, products, roadmap placeholders)
2. **AUTHORIZED LAYER** — Contributor/research access (design rationale, detailed specs, integration guides)
3. **CANONICAL CORE** — Internal only (decision ledger, incident records, governance audit trail)

This structure allows MoCKA to:
- Be discoverable and trustworthy (via transparency)
- Maintain institutional integrity (via governance privacy)
- Protect operational security (via information compartmentalization)
- Scale external ecosystem (via clear entry points)

**Next phase:** Human Gate review by product owner (きむら博士) for approval before implementation.

---

**Status:** DRAFT — Awaiting Human Gate Review  
**Target Decision Date:** 2026-08-21  
**Stakeholders:** Product Owner, Architecture Lead, Engineering Lead, Documentation Lead  


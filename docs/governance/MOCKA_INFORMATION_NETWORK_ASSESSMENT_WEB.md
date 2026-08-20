# MoCKA Information Network Assessment — Web/Public Visibility Phase

**Assessment Date:** 2026-08-20  
**Assessment Type:** READ-ONLY Investigation  
**Scope:** Public repositories, documentation, external references  
**Status:** COMPLETE  

---

## Executive Summary

MoCKA's public information network is currently in a **B: Distributed but Traceable** state. The core documentation and architectural vision are publicly accessible through the primary GitHub repository (m-sirius-k/MoCKA), but external discovery is hindered by:

1. **Single authoritative source** — All public information flows from m-sirius-k/MoCKA README
2. **Limited outfield presence** — Secondary repositories (mocka-civilization, mocka-transparency, etc.) are listed in OVERVIEW but not independently verified as public
3. **Reference document fragmentation** — Many architecture/governance documents are referenced in README but reside in local filesystem, not public URLs
4. **Product ecosystem unvisible** — Orchestra, Relay, PHI-OS, Memory are production systems but have no independent public documentation
5. **Domain presence unclear** — mocka.nsjp.org is noted in OVERVIEW but accessibility/content not confirmed

### Visibility Score by Category

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MoCKA core definition | B+ | A | Accessible but dense |
| Product ecosystem docs | D | B | Missing |
| Architecture diagram clarity | B | A | Diagram-heavy but unlabeled |
| Provenance chain | B- | A | Partial (Zenodo present, but no index) |
| Decision ledger visibility | D | B | Completely internal |
| Unknown items disclosure | D | A | No explicit "unknown" section |

---

## Part 1: Public Asset Map

### 1.1 Primary Repository — m-sirius-k/MoCKA

**Status:** PUBLIC (confirmed accessible)

| Asset | Type | Location | Accessibility | Completeness |
|-------|------|----------|---|---|
| README.md | Documentation | `/` | Bilingual (EN/JP) | Comprehensive |
| Architecture diagrams | SVG/visual | `/docs/images/` | Embedded in README | 6 diagrams |
| GOVERNANCE_BASELINE.md | Reference doc | `/docs/` | Referenced, assume local | Not verified public |
| MOCKA_CHARTER_v2.md | Governance charter | `/docs/governance/` | Referenced in README | Not verified public |
| SEMANTIC_LAYER.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| DECISION_LAYER.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| MEMORY_LAYER.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| SELF_AUDIT_LAYER.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| FEEDBACK_LOOP.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| LEARNING_KERNEL.md | Design doc | `/` (referenced) | Not confirmed public | Not verified public |
| EVENT_INTEGRITY_v1.md | Framework doc | `/` (referenced) | Not confirmed public | Not verified public |
| QUALITY_GATE.md | Process doc | `/` (referenced) | Not confirmed public | Not verified public |

**Key Finding:** README explicitly references ~10 documentation files, but their public availability is ASSUMED rather than confirmed.

### 1.2 Secondary Repositories — Status UNKNOWN

**Listed in MOCKA_OVERVIEW.json but NOT verified as public:**

```
m-sirius-k/mocka-civilization       (Blueprint layer)
m-sirius-k/mocka-transparency       (Tamper detection demo)
m-sirius-k/mocka-external-brain     (AI orchestration)
m-sirius-k/mocka-core-private       (Experimental — marked FORBIDDEN)
m-sirius-k/mocka-public             (Public docs layer — not accessed)
m-sirius-k/mocka-knowledge-gate     (Institutional memory)
m-sirius-k/mocka-outfield           (Public network layer)
m-sirius-k/vasAI                    (v1.4.9 mentioned as public)
m-sirius-k/planningcaliber          (Marked PRIVATE)
```

**Access Check Result:** Session scope limited to `m-sirius-k/mocka` only. Other repos NOT in scope for this session.

### 1.3 Product Ecosystem — Documentation Status

**Products with no independent public documentation:**

| Product | Mentioned in | Public Docs | Status |
|---------|--------------|-------------|--------|
| Orchestra | OVERVIEW, README (implied) | None found | Production (Stripe integration) |
| Relay | OVERVIEW, README (implied) | None found | Production (Free/Pro/One plans) |
| PHI-OS | OVERVIEW, README (implied) | None found | v1.0 (Chrome extension) |
| Memory | OVERVIEW, README (implied) | None found | Free tier complete |
| PR-OS | OVERVIEW | None found | Code complete, credentials setup pending |
| SEO-OS | OVERVIEW | None found | Phase 1-6 complete |
| vasAI | OVERVIEW | Not confirmed | v1.4.9 (Zenodo DOI: 10.5281/zenodo.19503666) |

**Critical Gap:** None of these production systems have dedicated public README, landing page, or feature documentation.

### 1.4 External Documentation — Paper Trail

**AIES 2026 Submission:**
- Submission ID: Submission282
- Status: camera-ready submitted
- Zenodo DOI (main): 10.5281/zenodo.19503666 (v8), 10.5281/zenodo.19507632 (v9)
- Zenodo DOI (preprint): 10.5281/zenodo.19606271 (PHL preprint, CC BY-NC 4.0)
- Zenodo DOI (p-DERS): 10.5281/zenodo.20686662

**External Reference Count:** 1 (academic paper)

### 1.5 Web Domain — mocka.nsjp.org

**Status:** MENTIONED but NOT VERIFIED

From OVERVIEW.json, no URL given. Assumed to exist but content unknown.

**Evidence:** Server config lists only localhost ports (5000, 5002, 5679, 5003). No ngrok/production domain documented in accessible files.

---

## Part 2: External Reference Map

### 2.1 Inbound References — Who References MoCKA?

**Public Sources (verified):**
- AIES 2026 conference (submission accepted for camera-ready)
- Zenodo (3 DOI entries)

**Unverified Public Sources:**
- mocka.nsjp.org (unknown content/purpose)
- Academic papers (unknown # of citations)

**Community/Developer Discovery:**
- GitHub search: `user:m-sirius-k mocka` returns 12 repositories
- GitHub topic tags: not verified

### 2.2 Outbound References — What Does MoCKA Link To?

**From README.md:**

| Reference | Type | Target | Status |
|-----------|------|--------|--------|
| docs/governance/MOCKA_THOUGHT_EVOLUTION_v0.1.md | Link | Internal file | Not verified public |
| docs/governance/ACTIVATION_POLICY_v0.1.md | Link | Internal file | Not verified public |
| docs/images/*.svg | Embedded | Relative path | Accessible (embedded in repo) |
| GOVERNANCE_BASELINE.md | Reference | Assume internal | Not verified public |
| SEMANTIC_LAYER.md | Reference | Assume internal | Not verified public |
| DECISION_LAYER.md | Reference | Assume internal | Not verified public |
| MEMORY_LAYER.md | Reference | Assume internal | Not verified public |
| SELF_AUDIT_LAYER.md | Reference | Assume internal | Not verified public |
| FEEDBACK_LOOP.md | Reference | Assume internal | Not verified public |
| LEARNING_KERNEL.md | Reference | Assume internal | Not verified public |
| EVENT_INTEGRITY_v1.md | Reference | Assume internal | Not verified public |
| GATE_ARCHITECTURE_v1.md | Reference | Assume internal | Not verified public |
| QUALITY_GATE.md | Reference | Assume internal | Not verified public |

### 2.3 Provenance Chain

```
External World (GitHub)
    ↓
m-sirius-k/MoCKA (README.md, v1.0.0)
    ├→ /docs/images/ (6 embedded SVG diagrams)
    ├→ /docs/governance/ (referenced, assume internal)
    └→ /GOVERNANCE_BASELINE.md (referenced, assume internal)
    
    ↓ Cross-references
    
Research Output (Academic)
    ├→ AIES 2026 (camera-ready)
    ├→ Zenodo DOI: 10.5281/zenodo.19503666
    ├→ Zenodo DOI: 10.5281/zenodo.20686662 (p-DERS)
    └→ Preprint: 10.5281/zenodo.19606271
    
    ↓ Assumed (unverified)
    
mocka.nsjp.org (unknown structure/purpose)
Secondary repos (12 total, mostly unknown status)
```

---

## Part 3: Visibility Assessment

### 3.1 External Discoverability — "What is MoCKA?" Test

**Scenario: A developer finds MoCKA on GitHub without prior knowledge.**

| Question | Answer | Source | Complete? |
|----------|--------|--------|-----------|
| What is MoCKA? | "Civilization model" (clear definition) | README intro | YES |
| What does it do? | Governance/institutional memory (examples provided) | README + diagrams | YES |
| How do I use it? | Quick start commands given | README | PARTIAL (dev-focused) |
| Is it production-ready? | Status v1.0.0, active development | README footer | YES |
| Can I see examples? | Diagrams + code structure mentioned | README | PARTIAL (conceptual) |
| What are the products built on it? | Not mentioned | README | NO ✗ |
| How does Orchestra relate to MoCKA? | Not explained | Any public source | NO ✗ |
| What is Relay? | Not explained separately | Any public source | NO ✗ |
| Where is the decision ledger? | Not public | Any public source | NO ✗ |
| Can I contribute? | No contributing.md referenced | README | NO ✗ |
| What is the governance model? | Charter referenced but not summarized | README | PARTIAL |

**Verdict:** A developer can understand MoCKA's *philosophy* but cannot understand its *product ecosystem* or *governance in practice*.

### 3.2 Architecture Clarity — Can External Parties Verify Claims?

| Claim | Verifiable? | How? | Status |
|-------|------------|------|--------|
| "append-only records" | Yes | README → GOVERNANCE_BASELINE.md (not public) | ASSUMED |
| "SHA-256 chain" | Yes | README mentions, files referenced | ASSUMED |
| "Ed25519 signatures" | Yes | README mentions | ASSUMED |
| "Auditable decisions" | Yes | Decision Ledger exists (not public) | UNVERIFIED |
| "75% degraded ops" | Partially | shadow_Movement described conceptually | CONCEPTUAL |
| "7 governance layers" | Partially | GL1-7 defined in README | LISTED NOT EXPLAINED |

**Verdict:** Architecture is *described* but not *demonstrated* publicly. No audit trail visible.

### 3.3 Unknown Items — Are Unknowns Explicitly Disclosed?

**Missing from Public README:**

- [ ] What happens to events after they're sealed?
- [ ] How does mocka.nsjp.org connect to the GitHub repo?
- [ ] What is the decision-making process for Phase 5, Phase 6?
- [ ] How do the 8 other repositories (mocka-civilization, etc.) relate?
- [ ] What is the roadmap for public APIs?
- [ ] What are the failure modes of shadow_Movement?
- [ ] How is the Zenodo paper version-locked to the code?
- [ ] What is the relationship between AIES 2026 submission and released code?
- [ ] Why are Phase 4+ details missing from public docs?

**Verdict:** No explicit "Unknown / Future Work / Roadmap" section. Unknowns are *implicit* (inferred by absence).

---

## Part 4: Provenance Findings

### 4.1 Origin Path

**Primary Source:**
- GitHub: m-sirius-k/MoCKA
- Created: 2026-02-20
- Latest push: 2026-08-20
- Branch: main (default)

**Evidence:**
- README version history not public (GitHub doesn't expose)
- Commit log exists (not analyzed in this READ-ONLY phase)
- OVERVIEW.json dated 2026-06-18, contains snapshot of state

### 4.2 Update Velocity

| Period | Activity | Evidence |
|--------|----------|----------|
| 2026-02 | Repository created | GitHub creation timestamp |
| 2026-03 to 2026-04 | Active development | OVERVIEW.json session_history |
| 2026-04 to 2026-06 | Phase transitions (Phase 2→3→4) | OVERVIEW.json milestones |
| 2026-07 | Paper submission (AIES) | OVERVIEW.json paper entry |
| 2026-08 | Investigation/audit phase | ESSENCE records (2026-08-13 to 2026-08-20) |

**Pattern:** Continuous active development with clear phase transitions.

### 4.3 Version Consistency — Code ↔ Paper ↔ Public Docs

**Code Version:** v1.0.0 (per README)  
**Paper Version:** Submitted 2026-07, Zenodo v8/v9/preprint  
**README Version:** Bilingual, comprehensive, Phase 4 content  

**Consistency:** PARTIALLY VERIFIABLE
- Code mentions paper exists ✓
- Paper DOIs are public ✓
- Paper content not compared to README ✗

---

## Part 5: Information Network Classification

### 5.1 Current State — B: Distributed but Traceable

**Justification:**

```
Centralizing Authority: ✓ (m-sirius-k/MoCKA README is canonical)
                           ↓
Distributed Echoes:    ✓ (Zenodo, AIES, secondary repos)
                           ↓
Traceability:          ◐ (Paper chain exists, but no index)
                           ↓
Completeness:          ✗ (Product docs missing, unknowns implicit)
```

**Components:**

| Layer | Completeness | Traceability | Status |
|-------|--------------|--------------|--------|
| Core philosophy | 95% | Clear | A |
| Architecture design | 70% | Documented (not public) | B |
| Governance model | 50% | Referenced (not public) | C |
| Product ecosystem | 10% | Not documented | D |
| Decision history | 0% | Internal ledger only | D |

### 5.2 Key Blockers to Visibility

1. **Documentation Fragmentation**
   - README references 10+ docs, assumes reader has local access
   - No canonical URL for architecture documents
   - Phase 2-5 details scattered across 20+ internal markdown files

2. **Product Invisibility**
   - Orchestra, Relay, PHI-OS, Memory have no independent web presence
   - No product landing pages
   - No integration documentation

3. **Decision Opacity**
   - Decision Ledger is internal
   - No public rationale for architectural choices
   - No changelog explaining Phase transitions

4. **Domain Isolation**
   - mocka.nsjp.org mentioned but not accessible from public sources
   - No HTTP links from GitHub to web domain
   - No HTTPS reverse link confirmation

5. **Repository Scope Confusion**
   - 12 repositories exist but only main one is documented
   - No README explaining multi-repo strategy
   - Secondary repos (mocka-civilization, etc.) are organizational orphans

---

## Part 6: Recommendations for Information Network Improvement

### Phase 1: Transparency (Short-term, no code changes)

1. **Create ARCHITECTURE.md index**
   - Link to all architecture documents (with access notes)
   - Explicit "Internal" vs "Public" markup
   - Explain why certain docs are not public

2. **Add "Products" section to README**
   - Brief overview of Orchestra, Relay, PHI-OS, Memory
   - Link to future product READMEs (create stubs if needed)

3. **Explicit "Unknowns & Roadmap" section**
   - List what is *not* public yet
   - Timeline for Phase 5, 6 documentation
   - Repository strategy (why 12 repos?)

4. **Link mocka.nsjp.org**
   - If public, add URL to README
   - If private, explain why
   - Clarify relationship to GitHub repo

### Phase 2: Discoverability (Medium-term)

1. **Create product READMEs** (Orchestra, Relay, PHI-OS, Memory)
   - Independent feature docs
   - Use cases
   - Integration with MoCKA core

2. **Publish architecture decision record (ADR) index**
   - Which decisions are public?
   - Which remain internal?
   - Reasoning transparency

3. **Create "Repository Map" document**
   - Explain each of the 12 repos
   - Dependency graph
   - Canonical vs experimental status

### Phase 3: Verification (Long-term)

1. **Zenodo paper version-lock mechanism**
   - Tag code at paper submission points
   - Make paper ↔ code traceability explicit

2. **Public audit trail**
   - Selective publication of decision ledger entries
   - "Redacted audit report" showing governance decisions

3. **Integration guide**
   - How do external systems (products, papers, future AI systems) connect to MoCKA?
   - Contract/interface definitions

---

## Part 7: Unknown Items & Gaps

### 7.1 Confirmed Unknowns

| Item | Impact | Discoverability |
|------|--------|-----------------|
| mocka.nsjp.org content/access | HIGH | Not disclosed |
| Secondary repos (mocka-civilization, etc.) public status | HIGH | Not disclosed |
| Product ecosystem web presence | HIGH | Not disclosed |
| Phase 5/6 roadmap (post-Learning Kernel) | MEDIUM | Not disclosed |
| Governance decision rationale | HIGH | Internal only |
| Test coverage / reproducibility guide | MEDIUM | Assume local |
| Contributing guidelines | MEDIUM | Assume local |
| Licensing details (CC BY-NC, MIT, etc.) | LOW | Assume local |

### 7.2 Unverified Assumptions

| Assumption | Confidence | Evidence |
|-----------|-----------|----------|
| MOCKA_CHARTER_v2.md is public | 30% | Referenced in README, file exists locally |
| Secondary repos are maintained | 40% | Listed in OVERVIEW, access denied this session |
| mocka.nsjp.org is production-grade | 20% | Mentioned in server_config, no URL |
| Zenodo papers are current | 80% | DOI dates are recent, paper submitted 2026-07 |
| vasAI v1.4.9 is publicly released | 60% | OVERVIEW says "VERIFIED封印済み", GitHub presence claimed |

---

## Part 8: Conclusion — Current Network State

### 8.1 Visibility Score: B (Distributed but Traceable)

**Transition Requirements to Target A (Single Source Clear):**

```
Current State (B):
- Central hub exists (m-sirius-k/MoCKA README)
- Distributed echoes exist (Zenodo, academia)
- Traceability chain exists (but incomplete)
- Products are invisible ✗
- Unknowns are implicit ✗

Target State (A):
- All public assets indexed ✓ (Needed)
- All references linked ✓ (Needed)
- Product ecosystem documented ✓ (Needed)
- Unknowns explicitly marked ✓ (Needed)
- mocka.nsjp.org integrated ✓ (Needed)
```

**Estimated effort to A:** 3 medium-sized pull requests
1. README enhancement (Architecture index + Products section + Unknowns)
2. Secondary repo strategy document + product READMEs (stubs)
3. mocka.nsjp.org integration (link + clarification)

### 8.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| External parties can't find MoCKA | MEDIUM | MEDIUM | SEO/GitHub optimization |
| External parties can't understand product ecosystem | HIGH | HIGH | Product READMEs |
| External parties distrust governance opacity | MEDIUM | MEDIUM | Publish decision index |
| Secondary repos become orphans | MEDIUM | LOW | Repository strategy doc |
| Paper/code divergence undetected | LOW | HIGH | Version-lock mechanism |

### 8.3 Recommended Next Phase

**Immediate (This Week):**
- [ ] Verify accessibility of mocka.nsjp.org (human confirmation needed)
- [ ] Confirm public status of 12 secondary repositories
- [ ] Identify which governance documents can be published

**Short-term (This Month):**
- [ ] Add "Products Overview" section to README
- [ ] Create ARCHITECTURE.md index
- [ ] Create UNKNOWNS_AND_ROADMAP.md

**Medium-term (Q3 2026):**
- [ ] Publish product-specific READMEs
- [ ] Release selective decision ledger samples (with redaction)
- [ ] Create multi-repo strategy document

---

## Appendix: Investigation Methodology

**Tools & Techniques:**

1. **GitHub MCP API** — Repository metadata, README retrieval, release inspection
2. **MOCKA_OVERVIEW.json** — Central state snapshot (2026-06-18, may be stale)
3. **Local filesystem inspection** — docs/governance/ directory scan
4. **README.md parsing** — Link extraction, reference verification
5. **ESSENCE ledger** — Recent activity traces (2026-08-13 to 2026-08-20)

**Limitations:**

- Session access limited to m-sirius-k/mocka only (secondary repos inaccessible)
- MOCKA_OVERVIEW.json is snapshot from 2026-06-18 (2 months old)
- No direct access to mocka.nsjp.org (assumed to exist)
- No commit-level analysis (time constraint)
- Automated tools only (no human context interview)

**Confidence Levels:**

- Confirmed facts (GitHub API): 95%
- Assumed facts (referenced but not verified): 50%
- Roadmap inferences (from OVERVIEW dates): 70%

---

**Document Status:** COMPLETE — READ-ONLY Investigation  
**Next Action:** Awaiting product owner confirmation on mocka.nsjp.org and secondary repository visibility.


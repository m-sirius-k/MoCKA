# Track B Investigation: MoCKA's Governance Function G Against Track A's Theory v0.1

Document ID: PDERS_TRACK_B_GOVERNANCE_G_INVESTIGATION_v0.1
Version: 0.1
Status: Read-only investigation report. No MoCKA implementation, configuration, Governance Policy, or Decision Ledger content was changed by this task.
Track: Track B investigation, commissioned from Track A (p-DERS Formal Theory Track) - first task in this series to examine MoCKA's actual implementation rather than theorize about it conditionally
Predecessors: docs/formal/pDERS_compositional_safety_v0.1.md, docs/formal/pDERS_sound_local_approximation_v0.1.md, DC_20260730_001, DC_20260730_002
Independence / honesty note: where this document could not find clear evidence one way or the other, it says so explicitly rather than inferring from the theory what "should" be true. Every classification below is tied to a specific file, code location, or Decision Ledger/git artifact; where no such artifact was found, this document reports that absence rather than filling the gap with plausible-sounding narrative.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase)

---

## 1. Investigation Scope

**Files and directories examined:**
- `docs/CONSTITUTION.md`, `docs/INSTITUTION_ARCHITECTURE.md` (the stated Constitution/Institution/Operation 3-layer architecture)
- `structural/execution_governance.py`, `structural/governance_pipeline.py` (GL7 - the actual execution-control kernel), and `docs/governance/gl7_execution_kernel_spec_v1.md` (an existing, independently-produced spec of the same code)
- `governance/` directory in full listing: `approval_flow.json`, `file_protection_registry.json`, `keys/role_policy.json`, `verify_role_policy.py`, and related `verify_*.py` scripts
- `docs/ai/claude.json`, `docs/ai/gemini.json`, `docs/ai/chatgpt.json` (per-agent role/capability declarations)
- `docs/governance/GPT_RESTRICTIONS.md` (a GPT-specific restriction list)
- `docs/governance/GOVERNANCE_INVENTORY_v0.1.md`, `docs/governance/GOVERNANCE_CLASSIFICATION_v0.1.md` (MoCKA's own internal audits of its governance documents, used here as third-party-style corroboration rather than this document's own classification)
- `data/institution/` (referenced by `INSTITUTION_ARCHITECTURE.md` as the Institution Contract's location) - checked for existence
- `interface/ai_capability_registry.py`, `core_kernel/core_store/capability_registry.py`, `docs/contracts/capability_registry_v1.md`
- git history (`git log --follow`, `git log`) for the above files, with the limitation noted in Section 4 that this checkout is a **shallow clone** (`git rev-parse --is-shallow-repository` returns `true`), so only recent history is visible

**Tools used:** `Grep`/`grep`, `find`, `git log`, `Read`; `mocka_search` (read-only full-text search over events.db) for Decision Ledger / event history relating to policy updates. No MCP write tool was called. No MoCKA file was edited.

**Search terms used (repo grep, and `mocka_search` queries):** `Governance Function`, `Governance Invariant`, `governance_pipeline`, `GL7`, `GPT_RESTRICTIONS`, `role_policy.json`, `独立に`, `各AI`, `Institution Contract`, `institution_contract`, `ai_role_registry`, `capability_registry`, `Constitution 憲法 改定 amendment revision`, `GPT_RESTRICTIONS 更新 Constitution 改定 restriction policy update`.

**What was not checked:** this investigation did not read `structural/consensus.py`, `phi_os/event_gate.py`, `phi_os/gate_validator.py`, or the full ~600-line `GOVERNANCE_INVENTORY_v0.1.md`/`GOVERNANCE_CLASSIFICATION_v0.1.md` documents beyond the sections quoted below - a full audit of MoCKA's governance surface was not attempted, and this document's findings should be read as based on a targeted sample, not an exhaustive review.

---

## 2. Branch 1 vs Branch 2: What MoCKA's Governance Function G Actually Does

The evidence found points to **two structurally different layers**, not one, which behave differently with respect to the Branch 1 / Branch 2 question. This document reports both rather than forcing a single answer, per the instructing memo's own instruction to report "unclear" or "mixed" honestly.

### 2.1 The structural/mechanical layer (GL7) - looks Branch-1-shaped

`structural/execution_governance.py` and `structural/governance_pipeline.py` (documented independently in `docs/governance/gl7_execution_kernel_spec_v1.md`, which this investigation treats as a prior, separately-produced source rather than something this document is originating) implement a **single, shared execution gate** that every MCP tool call passes through, regardless of which AI agent issued it: `GovernancePipeline.before_tool()` is described as "全Tool呼び出しの単一窓口" (the single window for all tool calls). It performs a Dry Run, checks a fixed set of `ABORT_CONDITIONS` (`grounding_not_completed`, `deletion_outside_scope`, `new_directory_detected`, `unexpected_file_count` - per the spec document, only these four actually fire; a fifth, `encoding_mismatch`, is defined but never triggered), and denies by default (`READ_ONLY_TOOLS` is the only explicit allowlist; everything else is gated).

This is a **single, centrally-evaluated function**, not `n` separate per-agent predicates - there is one `execution_governance.py`, invoked identically no matter which agent is calling. In p-DERS terms, this does not even present as "Branch 1" (many `Omega_i` derived from one shared source) so much as a still-simpler case: there is effectively one `Omega`, evaluated once, centrally, with no per-node instantiation at all. `governance/file_protection_registry.json` (a single, shared hash registry of files - `interface/router.py`, `mocka_mcp_server.py`, `app.py`, `index.html`, `tools/mocka_orchestra_v10.py` - each marked `"editable_by": "きむら博士のみ"`) is a second example of the same pattern: one shared registry, applied uniformly, not authored per agent.

Also worth noting precisely, since it bears on how much weight to put on GL7 as evidence: `gl7_execution_kernel_spec_v1.md` itself documents (Section 10 of that file) that `FORBIDDEN_EXECUTIONS` (an 8-item list) and the `encoding_mismatch` abort condition are defined in code but never actually referenced by any enforcement path, and that the "Human Gate approval after Dry Run" step the code's own comments describe is not wired to any actual Human Gate mechanism in `structural/`. This document did not re-verify these specific claims independently (they come from a pre-existing spec document, not from this investigation's own code reading), but reports them because, if accurate, they mean GL7's real enforcement surface is narrower than its own docstrings and `ABORT_CONDITIONS`/`FORBIDDEN_EXECUTIONS` lists suggest.

### 2.2 The role/capability declaration layer (per-agent JSON files) - looks Branch-2-shaped, with mixed and partly-missing provenance

`docs/ai/claude.json`, `docs/ai/gemini.json`, and `docs/ai/chatgpt.json` share one JSON schema (`agent`, `role`, `authority`, `read`, `write`, `restrictions`, `version`) but each contains **different content**, tailored to that agent's role:

- Claude (role `R02`): authority `["Documentation", "Audit", "Paper Lead"]`, restrictions `["Do not write to MoCKA Core without Human Gate approval", "Do not merge branches to main directly", "Record all changes via mocka_write_event"]`.
- Gemini (role "Adversarial Reviewer"): authority `["Challenge claims", "Identify weaknesses"]`, restrictions `["Review only — no implementation", "Flag logical inconsistencies", "Cannot approve Decisions"]`.
- ChatGPT (role `R01`): authority `["Design Audit", "Institution Review", "Paper Sub"]`, restrictions `["Audit only — no implementation", "All decisions require Human Gate approval", "Do not override R02 documentation"]`.

This is a real, concrete instance of what Track A called Branch 2 in structure (each node has its own distinct predicate, not a uniform application of one shared function) - though whether it is Branch 2 in the *problematic* sense Track A analyzed (independently authored with no common derivation, and thus at risk of undetectable disagreement) depends on provenance this investigation could only partly establish:

- **`docs/governance/GPT_RESTRICTIONS.md`** carries an explicit self-declared provenance: "生成日時：2026-04-01... ソース：docs/incidents/INC-*.md" - it states it is auto-generated from specific incident reports, and its own "適用ルール" section says "新規インシデント発生時は自動更新される" (it updates automatically when new incidents occur). This is a reactive, incrementally-accreted, agent-specific document, not a derivation from one shared, ratified policy.
- **This is independently corroborated by two of MoCKA's own internal governance audits**, not just this document's reading of the file: `docs/governance/GOVERNANCE_INVENTORY_v0.1.md` classifies `GPT_RESTRICTIONS.md`'s "制定状況" (enactment/ratification status) as "記載なし（インシデント由来の禁止事項リスト）" - literally "not recorded" - distinct from other entries in the same table that do show a ratification record (e.g. "博士裁定2026-06-28"). `docs/governance/GOVERNANCE_CLASSIFICATION_v0.1.md` separately classifies `GPT_RESTRICTIONS.md` under "記録層" (Record Layer) rather than "ガバナンス層" (Governance Layer) - i.e., MoCKA's own governance taxonomy treats this specific document as a log/record artifact, not as an enacted policy instrument.
- **The Institution Contract that `INSTITUTION_ARCHITECTURE.md` describes as the shared source these role declarations should validate against does not exist as a file in this repository.** `INSTITUTION_ARCHITECTURE.md` states: "Institution Contract（TODO_280/281）... ファイル: data/institution/". This investigation checked: `data/institution/` does not exist anywhere in this checkout. This does not prove the Institution Contract was never implemented anywhere (it could exist outside this repo, or under a different path this investigation did not find), but no such artifact was located.
- **For `claude.json` and `gemini.json` specifically, this investigation found no equivalent "auto-generated from incidents, unratified" provenance marker, and no equivalent evidence that they *were* derived from a shared source either.** They read as directly-authored, static role declarations. Whether they were produced by a process resembling `GPT_RESTRICTIONS.md`'s (informal, per-agent, reactive) or by some other, more disciplined process this investigation did not find evidence of, is genuinely unknown from what was examined.

### 2.3 Verdict: mixed, not a single answer

Consistent with the instructing memo's explicit permission to report "unclear" or "mixed" rather than force a classification: **the structural/mechanical layer (GL7, file protection registry) looks like a single, uniformly-applied function, closer to what Branch 1's discipline would want than to Branch 2's problem. The role/capability declaration layer (per-agent JSON files, and especially the GPT-specific restriction list) shows real, evidenced characteristics of Branch 2 - different content per agent, with at least one instance (`GPT_RESTRICTIONS.md`) independently confirmed by MoCKA's own audits to be an unratified, incident-driven, agent-specific accretion rather than a derivation from a shared, ratified policy - while the shared reference (Institution Contract) that would make this Branch-1-compatible instead does not exist as a locatable file.** This investigation does not have enough evidence to say whether `claude.json`/`gemini.json` follow the same pattern as `GPT_RESTRICTIONS.md` or a more disciplined one; it reports the asymmetry in available evidence rather than assuming symmetry.

---

## 3. Sound Local Approximation's 4 Properties Against MoCKA's Reality

Evaluating each of `pDERS_sound_local_approximation_v0.1.md` Section 1's four formalized properties against what Section 2 found. As throughout, this section evaluates degree of fit with evidence, not a binary yes/no.

**P1 (Single Public Reference).** Partially present, split across layers. At the structural layer, `governance/file_protection_registry.json` and the GL7 kernel *are* single, shared, published-in-the-sense-of-being-one-file references. At the role-declaration layer, no single reference was found that `claude.json`/`gemini.json`/`chatgpt.json`/`GPT_RESTRICTIONS.md` are shown to derive from - the architecturally-intended single reference (`data/institution/`'s Institution Contract) does not exist as a file. So: P1 holds for the mechanical layer; it does **not** demonstrably hold for the role-declaration layer, where no single published reference was located.

**P2 (Independent Soundness Proof).** Not found to hold, in the formal sense `pDERS_sound_local_approximation_v0.1.md` Section 1.3 defines it (a one-time proof, discharged per node, that a node's own predicate implies a shared reference). No proof artifact - formal or informal - was found showing that `claude.json`'s restrictions, `gemini.json`'s restrictions, or `GPT_RESTRICTIONS.md`'s restrictions were checked against any single reference and shown to be a *sound* (conservative, never-more-permissive) narrowing of it. What was found instead, for `GPT_RESTRICTIONS.md`, is a reactive process (incident occurs -> incident is analyzed -> a new prohibition is appended) - this is a real mechanism, but it is not the same thing as a soundness proof against a fixed reference; it is closer to incremental patching in response to observed failures.

**P3 (No Runtime Coordination).** This appears to hold, in the sense that GL7's runtime decision (`before_tool()`) does not, per the spec document, perform any cross-agent query or wait on another agent's response before accepting or rejecting a tool call - it evaluates structural conditions (scope, change count, directory novelty) that do not require consulting another node. This is consistent with P3, though this investigation notes it did not verify this by reading `execution_governance.py` directly line-by-line - it relies on the pre-existing `gl7_execution_kernel_spec_v1.md` document's account of the code.

**P4 (Scalability to Variable Node Sets).** Not directly tested - no evidence of an actual node/agent join event (a new AI agent being onboarded) was found or searched for with enough precision to say whether joining costs anything for existing agents' declarations. The schema-based, per-agent JSON file pattern (Section 2.2) would, structurally, allow a new agent to be given a new JSON file without touching `claude.json`/`gemini.json`/`chatgpt.json` - which is at least *consistent* with P4's spirit - but no soundness-proof-on-join event was found to confirm this happens with any rigor, as opposed to simply "someone writes a new JSON file with plausible-looking restrictions."

**Summary for Section 3:** of the four properties, P3 is the best-supported by available evidence, P1 is split (holds mechanically, not at the role-declaration layer), and P2/P4 were not found to be actively practiced in the formal sense Track A defined them - what exists instead, for at least one agent (GPT), is an informal, reactive, incident-driven process that resembles neither clean Branch 1 discipline nor a rigorous Sound Local Approximation soundness proof.

---

## 4. Lemma S2 Asymmetry Check

The instructing memo asked specifically whether MoCKA's Governance Policy has been updated in the past, whether such updates were weakenings or strengthenings, and whether a strengthening update (if any) triggered re-verification at any agent.

**What this investigation found:** very little directly usable evidence, and this section reports that limitation rather than guessing.

- `docs/CONSTITUTION.md` states a single "確定日: 2026-06-12" (ratification date) with no revision history section and no superseded-version references within the file itself.
- `git log --follow` for `docs/CONSTITUTION.md`, `docs/INSTITUTION_ARCHITECTURE.md`, `docs/governance/GPT_RESTRICTIONS.md`, `docs/ai/chatgpt.json` all show only a single relevant commit each in the history available to this checkout (`72c163e "auto sync 2026-07-21T06:45:58Z"`, and for two of the `docs/ai/` files, an additional `a9c4589 "feat: add MoCKA Publisher + docs/ output"` commit). **This checkout is a shallow clone** (`git rev-parse --is-shallow-repository` = `true`), so this is not evidence that no earlier revisions exist - only that this investigation could not see them. The single visible commit for each file also reads as a bulk "sync" event rather than a targeted, individually-authored policy revision, which further limits what can be inferred about the *actual* editorial history from git alone.
- `mocka_search` (full-text search over events.db) for `"GPT_RESTRICTIONS 更新 Constitution 改定 restriction policy update"` and separately for `"Constitution 憲法 改定 amendment revision"` returned zero hits in both events and knowledge-gate results.
- No Decision Ledger entry was found (via the searches above) discussing a Constitution, Institution Contract, or per-agent restriction-file revision as a governance event in its own right.

**Conclusion for this section:** this investigation did not find clear evidence of a documented Governance Policy update event to classify as weakening or strengthening, and therefore cannot report whether Lemma S2's asymmetry (weakenings preserve existing proofs automatically; strengthenings do not) has actually manifested as a real bottleneck in MoCKA's operation. This is reported as "not found," not as "did not happen" - the shallow clone and the absence of a dedicated policy-revision-tracking mechanism (as distinct from the general append-only event ledger) both limit what this investigation could establish. `GPT_RESTRICTIONS.md`'s own stated update mechanism ("新規インシデント発生時は自動更新される") is itself a case worth flagging conceptually: appending a *new* prohibition to a restriction list is a strengthening in Track A's sense (the restricted agent can now do strictly less than before), and if this occurs "automatically" without a stated re-verification step for whatever existing behavior the agent had previously been considered compliant under, it would be a concrete instance of exactly the gap Lemma S2 warns about - but this investigation did not find a specific historical instance of this happening to confirm or refute it, only the general mechanism description.

---

## 5. Findings and Open Questions

**Findings (evidence-based, not inferred):**

1. MoCKA's governance surface has at least two structurally different layers with respect to Branch 1/Branch 2: a single, shared, mechanically-enforced layer (GL7, file protection registry) and a per-agent, differently-authored declaration layer (role/capability JSON files, restriction lists).
2. For one specific agent-facing document (`GPT_RESTRICTIONS.md`), MoCKA's own internal governance audits (not this investigation's inference) already document that it is unratified and incident-driven rather than derived from a ratified shared policy.
3. The architecturally-designed single shared reference for role declarations (the Institution Contract, `data/institution/`) does not exist as a locatable file in this repository.
4. No evidence was found, in the time available, of a documented Governance Policy revision event that could be classified as weakening or strengthening under Lemma S2's framework - this is a gap in available evidence, not a claim that no such event has occurred.

**Open Questions (none resolved by this document; matters for Human Gate or a further Track B task, not for Track A to settle):**

1. Whether `claude.json` and `gemini.json` were produced by a process similar to `GPT_RESTRICTIONS.md`'s (informal, reactive, per-agent) or by something more disciplined - this investigation found no provenance markers either way for these two files specifically.
2. Whether the Institution Contract (`data/institution/`) exists somewhere outside this repository, was planned but never implemented, or was implemented and later removed - this investigation only confirms it is not present in this checkout.
3. Whether MoCKA has, in fact, had Governance Policy revisions that this investigation's limited git history and event-search access could not surface - given the shallow clone, this remains a real possibility this document cannot rule out.
4. Whether the specific gap Lemma S2 warns about (a strengthening update with no re-verification step) has already occurred somewhere in MoCKA's actual incident-driven restriction updates (Section 4's closing point) - flagged as a concrete risk shape worth checking for, not confirmed to have happened.
5. Whether GL7's documented enforcement gaps (`FORBIDDEN_EXECUTIONS` and `encoding_mismatch` defined but not wired to any enforcement path, per the pre-existing `gl7_execution_kernel_spec_v1.md`) affect how much weight the "single shared mechanical layer" finding (Section 2.1) should actually carry - this investigation relied on that pre-existing document's account rather than independently re-verifying the code, and did not assess whether these gaps are safety-relevant beyond noting they exist.
6. **This document does not propose fixing any of the above.** Per its scope, any apparent improvement opportunity (e.g., formally ratifying `GPT_RESTRICTIONS.md`, implementing the Institution Contract, or adding a policy-revision tracking mechanism) is recorded here as an open question for Human Gate's judgment, not as a recommendation this document is making or would implement.

# Investigation: Where (if anywhere) do R_i / Omega_i / Psi_i Come From? v0.1

Document ID: PDERS_RI_OMEGA_PSI_SOURCE_INVESTIGATION_v0.1
Version: 0.1
Status: Investigation complete; conclusion is "unresolved" for part of the question, not a clean yes/no (see Section 3)
Track: Track A (Formal Theory Track, p-DERS)
Purpose: determine, with evidence, whether a canonical formal source for R_i, Omega_i, Psi_i (and S_i_spec) exists anywhere - inside or outside this repository - rather than continuing to carry forward the predecessor documents' assumption that it exists but is merely uncommitted.
Independence note: this document is independent of Track B (MoCKA Write Path v1.0 / DC-WP). Nothing here is wired into, or intended to be wired into, any MoCKA implementation, the Decision Ledger, or any MCP write path. Read-only investigation; no existing files changed; no Decision Ledger write performed by this document.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase)

---

## 1. Investigation Scope (files, tools, and search terms used)

### 1.1 Search terms used throughout (repo, Decision Ledger, events.db, Notion)

`R_i`, `Omega_i` / `Ω_i`, `Psi_i` / `Ψ_i`, `pi_i` / `π_i`, `S_i_spec`, `S_spec`, "local relation", "local invariant", "causal slice", "happens-before", "concurrent transition", "vector clock", "Local Invariant Gate", "decentralized verification", "localized verification spaces", "p-DERS", "pDERS", "Projective Dual-Execution Refinement Systems", "Persistent Distributed Event Record System".

### 1.2 Repository (m-sirius-k/mocka, this checkout)

- Repo-wide `grep`/Grep sweeps (not limited to `docs/`) for every term in 1.1, across all file types.
- Targeted re-check of `docs/`, `docs/mocka3/`, `data/`, `PlanningCaliber/`, and repo root, since the instructing memo specifically asked whether the predecessor document's search might have missed something in `docs/`/`mocka3/`.
- `find` across the whole filesystem (not just the repo) for filenames containing `AAAI`, `MoCKA2027`, `zenodo`, `20686662`, `p-DERS`/`pDERS` - to check whether the actual paper file or preprint had been saved locally anywhere outside git.
- `git log --follow -p` on `docs/ai/notebooklm.md` to find where its "Formal Core: S_DTS = (E, P, V)" line came from, and a grep of `mocka_publisher.py` (the script that generates that file) for the same string.

### 1.3 Decision Ledger (via `mocka_decision_get` / `mocka_decision_list`)

- Direct lookups: `DC_20260719_005`, `DC_20260718_002`, `DC_20260718_001` (the three decisions that, between them, settled the AAAI2027 paper's Formal Core).
- A full dump of `mocka_decision_list` (187 decision records, all statuses) grepped for every term in 1.1.

### 1.4 events.db (via `mocka_search`, full-text)

Queries run: "R_i Omega_i Psi_i local relation local invariant"; "p-DERS"; "Persistent Distributed Event Record System"; "Projective Dual-Execution Refinement Systems Local Invariant Gate"; "decentralized verification localized verification spaces control-flow information-flow constraints"; "S_i_spec local relation R_i definition".

### 1.5 Notion workspace (via `notion-search` / `notion-fetch`)

Queries run: "p-DERS R_i Omega_i Psi_i local invariant causal projection"; "p-DERS Local Invariant Gate pi_i projection formal definition"; "Projective Dual-Execution Refinement Systems". The single Notion page found to contain the actual AAAI2027 LaTeX source (`MoCKA2027.tex`, page id `3a33be67-ea2f-800a-af26-c1202a51766f`) was fetched in full (84,504 characters) and searched for every term in 1.1.

### 1.6 External (outside MoCKA entirely)

- `WebFetch` on `https://zenodo.org/records/20686662` (HTML page), `https://zenodo.org/api/records/20686662` (REST API), and `https://doi.org/10.5281/zenodo.20686662` (DOI resolver).
- `WebSearch` for `"Projective Dual-Execution Refinement Systems" p-DERS zenodo` and `"Local Invariant Gate" "p-DERS" zenodo OR preprint`.
- Because TODO_314 (Section 2.6 below) claims a Rust prototype of p-DERS was published to GitHub under a "SiriusLab" account: checked the two most plausible candidate repositories already visible in this account's repository list (`m-sirius-k/execution-runtime-system`, `m-sirius-k/sirius-lab`) directly. A GitHub-wide code/repo search for the prototype was deliberately **not** performed, because this session's GitHub access is scoped to specific repositories and a wide search would exceed that authorized scope.

---

## 2. Findings

### 2.1 Found: the AAAI2027 paper's actual Formal Core, and confirmation it does not contain R_i/Omega_i/Psi_i

The AAAI2027 submission (`MoCKA2027.tex` / `MoCKA2027_RECON_v1.tex`, titled "MoCKA: An Evidence-Bound Governance Architecture for Runtime AI Decision Transition Auditing") is not committed to this git repository (independently confirmed both by this investigation and by Decision Ledger entry `DC_20260718_001`, which records the same absence after its own exhaustive repo + full git-history search). It was located and read in full via the Notion workspace. Its Formal Core is `S_DTS = <E, P, V>` (E = Evidence sufficiency, P = Provenance integrity, V = Verification boundary state, with a Governance Invariant Eq.1/Eq.2 producing Verified/Unverified/Conflicted states). A full-text search of the fetched LaTeX source (84,504 characters) for every term in Section 1.1 returned **zero matches** for `R_i`, `Omega_i`, `Psi_i`, `pi_i`, "local relation", "local invariant", "happens-before", "vector clock", "concurrent", "projection", or even "p-DERS" itself. This paper's formal system is entirely unrelated, in subject matter, to a distributed local-projection formalism.

### 2.2 Found: `notebooklm.md`'s "Formal Core" line is a hardcoded template string, not a live-sourced field - but the underlying S_DTS notation is well-documented elsewhere

`docs/ai/notebooklm.md` is entirely generated by `mocka_publisher.py` (confirmed by `git log --follow`: the file first appears fully-formed in commit `a9c4589`, "feat: add MoCKA Publisher + docs/ output"). Inside `mocka_publisher.py`, the line `- Formal Core: S_DTS = (E, P, V)` (script line 365) is a **literal hardcoded string** in the output template - unlike the adjacent lines in the same template (`Total Events: {stats['total_events']:,}`, `Decisions: {stats['total_decisions']}`), which are dynamically interpolated from live data. So this specific summary line is not itself evidence of anything beyond "someone typed this string into the publisher script."

That said, the underlying `S_DTS = <E,P,V>` notation it refers to **is** independently and extensively documented through the Decision Ledger: `DC_20260718_001` (rejected the symbol `S_DTS` for the *Phase 7* paper specifically, after an exhaustive search found no definition source for it there) -> `DC_20260718_002` (clarified that this rejection did not apply to the separate `MoCKA2027.tex`, where `S_DTS=<E,P,V>` was found, upon direct inspection of the user-provided source file, to be a legitimately and consistently used notation) -> `DC_20260719_005`/`006`/`013`/`016` and others (repeatedly reconfirmed `S_DTS=<E,P,V>` as final, through a fully compiled, hash-verified submission PDF). None of this trail, at any point, introduces or discusses `R_i`, `Omega_i`, or `Psi_i`.

### 2.3 Found: the Decision Ledger discusses p-DERS as a product, never as a source of formal notation

Across all 187 Decision Ledger entries (full text grepped), p-DERS is never mentioned as a decision subject at all - not once, in either direction (no decision proposes, defines, ratifies, or rejects any p-DERS-specific formal symbol). This contrasts sharply with the AAAI2027/`S_DTS` case, where the Decision Ledger contains an extensive, traceable, multi-decision history. Events (not decisions) discuss p-DERS as a publication milestone (Zenodo preprint announcement, AIES 2026 submission, Rust prototype release) - see 2.4-2.6 below - but no governance-level record of its internal formal content exists.

### 2.4 Found: one authentic excerpt of the actual p-DERS preprint's own language

One events.db event, `E20260614_024` (2026-06-14, `who_actor: kimura`, a voice-capture of what reads as the actual LinkedIn/announcement text for the Zenodo preprint), contains this description of the framework, in prose:

> p-DERS (Projective Dual-Execution Refinement Systems) introduces a decentralized verification approach that: Projects global system behavior into localized verification spaces (πi); Enforces safety through a Local Invariant Gate before state transitions; Maintains control-flow and information-flow constraints without global synchronization; Enables post-execution auditability through structured verification logs; Scales verification with local projection complexity rather than system size.

This is the **only** place across the entire searched corpus (repo, Decision Ledger, events.db, and the searched Notion pages) where anything resembling a per-node projection symbol (written here as "πi", no underscore, no LaTeX) and a p-DERS-specific local-invariant concept ("a Local Invariant Gate") appear together. Two things about it are worth being precise about: it names one projection object (πi) and one invariant-enforcement mechanism ("a Local Invariant Gate," singular, described in prose, no symbol given) - it does not, in this text, split the invariant side into two separately named objects the way `Omega_i` and `Psi_i` do, and it never uses the symbol `R_i` for anything.

### 2.5 Found (discrepancy, not resolved by this investigation): the acronym's expansion is internally inconsistent

`MOCKA_OVERVIEW.json` (via `mocka_get_overview`) states the paper's title as "Persistent Distributed Event Record System (p-DERS)". The authentic source text in 2.4 (the original 2026-06-14 announcement) states it as "Projective Dual-Execution Refinement Systems (p-DERS)". These are different phrases with a different meaning, sharing only the acronym. This investigation did not attempt to determine which (if either) is authoritative or how the discrepancy arose; it is recorded here because it directly bears on how much confidence to place in any single internal MoCKA record's characterization of "what p-DERS is," including the instructing memos for this Track A series.

### 2.6 Found: corroborating TODOs for "Local Invariant Gate" and a claimed Rust prototype

`data/MOCKA_TODO_ARCHIVE.json` contains TODO_312/313/314 (all `status: 完了`, i.e. marked complete): TODO_312 (AIES 2026 formal submission of the p-DERS paper, Zenodo DOI 20686662, matches the DOI used throughout this investigation), TODO_313 ("Local Invariant Gateのレイテンシ計測..." - benchmarking work for the camera-ready version, independently corroborating "Local Invariant Gate" as a real, named, singular component of the actual work, consistent with 2.4), and TODO_314 ("p-DERSのRustプロトタイプをGitHubに公開する。SiriusLab組織アカウント配下" - a Rust prototype of p-DERS was reportedly published to GitHub under a "SiriusLab" account).

TODO_314's claim was checked directly (not just searched for) against the two most plausible candidate repositories already visible in this GitHub account: `m-sirius-k/execution-runtime-system` (a Python/FastAPI "Execution Runtime System" whose own README states "MoCKA is explicitly excluded and has no dependency or reference" - unrelated) and `m-sirius-k/sirius-lab` (a marketing/landing-page site for MoCKA's products - Orchestra, Relay, Memory, PHI-OS - with no Rust code and no p-DERS content). Neither matches. The actual prototype repository's name/location was not determined, and a GitHub-wide search was not performed (out of this session's authorized scope, per Section 1.6). **This lead is unresolved, not negative** - the prototype may exist under a name this investigation did not guess, or under an account this session cannot search.

### 2.7 Not found: R_i / Omega_i / Psi_i / pi_i anywhere in the internal MoCKA corpus, except this Track A series' own prior output

Across the full search described in Section 1 (repo-wide, all of `docs/`/`mocka3/`/`data/`/`PlanningCaliber/`, 187/187 Decision Ledger entries, multiple `events.db` full-text queries, and the Notion pages returned by multiple targeted searches including the full AAAI2027 LaTeX source itself), `R_i`, `Omega_i`/`Ω_i`, `Psi_i`/`Ψ_i`, and `pi_i`/`π_i` as formally defined symbols occur **only** inside this Track A series' own two prior deliverables (`docs/formal/pDERS_causal_projection_v0.1.md`, `docs/formal/pDERS_overlap_consistency_v0.1.md`) - which are not a canonical source; they were written by following instructing memos that asserted these symbols already existed, and both documents already disclosed (in their own Section 0) that no canonical source had been located. One additional repo match, `PlanningCaliber/fp/MoCKA_KN004_System_Map.md`, was checked directly and is a false positive: it uses the generic English phrase "local invariants" (lowercase, no subscript) to describe an unrelated schema-validation layer in a completely different system (KN-004), with no connection to p-DERS.

### 2.8 Unresolved: direct access to the actual external p-DERS artifacts

`WebFetch` against all three URL forms for the Zenodo record (page, API, DOI resolver) returned HTTP 403 in every case - consistent with this environment's documented behavior for a destination blocked by network/egress policy (see `/root/.ccr/README.md`: "403/407 from the proxy: the destination host is not allowed by your organization's egress policy for this session... report the blocked host," rather than a same-error signal for "page does not exist"). `WebSearch` for the paper's exact title and for a distinctive phrase from its own abstract returned no relevant results at all - which is weak evidence at best (obscure/recent preprints are often poorly indexed) and is not treated here as proof of anything. **Whether the actual, full p-DERS preprint contains a canonical formal definition of R_i/Omega_i/Psi_i beyond the one-sentence prose description found in 2.4 remains genuinely unknown** - this investigation could not reach that source to check.

---

## 3. Conclusion

This document does not give a single flat "exists" / "does not exist" answer, because the evidence supports different confidence levels for different scopes of the question. Stated precisely:

**Within MoCKA's internal corpus (this git repository, the full Decision Ledger, events.db, and the Notion pages reachable by the searches in Section 1) - confirmed absent, with high confidence.** The search was broad (whole-repository grep, not just `docs/`; all 187 Decision Ledger entries; multiple targeted event and Notion queries; the actual final AAAI2027 LaTeX source read and searched directly) and consistent (every search converged on the same two unrelated formal systems - AAAI2027's `S_DTS=<E,P,V>` and the rejected Phase 7 `S/delta/Dom(delta)` - neither of which is a distributed local-projection formalism, and neither of which contains `R_i`/`Omega_i`/`Psi_i`). The predecessor documents' working assumption ("not committed here, but presumably exists somewhere, most likely the AAAI2027 draft") is now known to be specifically wrong about *where*: the AAAI2027 paper was located and read in full, and it is not there either.

**Within the actual external p-DERS artifacts (the Zenodo preprint itself, and the claimed Rust prototype) - unresolved, not confirmed either way.** Both were pointed to by legitimate internal records as real, existing things (a real DOI, a real AIES submission, a real TODO marking a GitHub publication complete), but this investigation could not reach either one directly: the Zenodo record is blocked by this session's network policy (a policy block, not a not-found signal), and the prototype's repository could not be located within this session's authorized GitHub scope.

**A suggestive, non-conclusive signal:** the one piece of the actual paper's own language this investigation *could* reach (Section 2.4, the original 2026-06-14 announcement text) describes the framework using a single projection symbol ("πi") and a single, unnamed "Local Invariant Gate" - not the three separately-named objects `R_i`, `Omega_i`, and `Psi_i` that the instructing memos for this Track A series have used throughout. This is consistent with (but does not prove) the possibility that `R_i`/`Omega_i`/`Psi_i` were introduced later, as a paraphrase or elaboration written when this Track A series' instructing memos were drafted, rather than carried over verbatim from the actual p-DERS paper. This document takes no position on whether that possibility is true; it is recorded because it is the most concrete lead this investigation produced, not because it settles the question.

In the terms the instructing memo asked for: **not "存在する," not confidently "存在しない" either - "不明," with the specific, evidenced qualification that the internal half of the question is settled (absent) and the external half is not (blocked/unreached).**

---

## 4. Implications for Next Steps (options only, not performed here)

This section presents options for Human Gate to choose between. It does not recommend one, and no definitional work is performed by this document, consistent with this task's scope.

1. **Close the external gap first.** If Human Gate (kimura hakase) can supply the actual p-DERS preprint text directly (e.g. paste it, attach a local copy, or identify the exact GitHub repository/organization the Rust prototype was published under), a follow-up investigation could check that source specifically for `R_i`/`Omega_i`/`Psi_i` with a real chance of a conclusive answer, without needing to define anything new. This is the option that could still turn "unresolved" into "found" without new formal work.

2. **Treat the canonical source as unavailable and define new.** If Option 1 is not pursued, or is pursued and still turns up nothing, then closing Lemma 2 of the Overlap Consistency sketch (`docs/formal/pDERS_overlap_consistency_v0.1.md`, Section 3.3, prerequisite 1) will require `R_i`/`Omega_i`/`Psi_i` (or a deliberately chosen replacement, e.g. building directly on the "Local Invariant Gate" language actually found in Section 2.4) to be **newly defined** as part of this Track A work, under explicit Human Gate direction - not merely located. This is a materially different kind of task than any of the three Track A documents produced so far, all of which have explicitly declined to invent these definitions themselves.

Both options are presented as a fork in the road only; this document performs neither.

# p-DERS Overlap Consistency - Revision Grounded in the Published Paper v0.2

Document ID: PDERS_OVERLAP_CONSISTENCY_v0.2
Version: 0.2 (supersedes the analysis approach of v0.1 for this document; v0.1 is retained unmodified as revision history, not deleted or overwritten)
Status: DECISION_RECORDED (Candidate B selection, inherited from v0.1) - Assumption 4's provability is now stated as bifurcated (Section 3), not open in the undifferentiated sense v0.1 left it
Track: Track A (Formal Theory Track, p-DERS)
Predecessor: docs/formal/pDERS_overlap_consistency_v0.1.md (v0.1) - not overwritten; this is a new file
Grounding source: docs/formal/references/pders_main_reference.md (transcription of the actual p-DERS paper; see that file's provenance/caveats section before treating any quote below as beyond-doubt exact)
Independence note: this document is independent of Track B (MoCKA Write Path v1.0 / DC-WP). Nothing here is wired into, or intended to be wired into, any MoCKA implementation, the Decision Ledger, or any MCP write path. Read-only research artifact; no Decision Ledger write performed by this document.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase)

## Why this revision exists, in one paragraph

`pDERS_overlap_consistency_v0.1.md` built an "Overlap Consistency" proposition, a from-scratch definition of "globally safe," and a two-lemma proof sketch entirely from first principles, because at the time this Track A series had no access to the actual p-DERS paper and had explicitly disclosed that gap (`pDERS_causal_projection_v0.1.md` Section 0, and confirmed by `pDERS_Ri_Omega_Psi_source_investigation_v0.1.md`). The paper is now available (`docs/formal/references/pders_main_reference.md`). It turns out the paper already states almost exactly the proposition v0.1 was reconstructing - as **Assumption 4 (Projection Consistency)**, feeding into **Theorem 4 (Decentralized Safety Preservation)**. This document replaces v0.1's ground-up construction with a grounded reading of the paper's own Assumption 4 / Theorem 4, and asks the question the paper itself leaves open: under the paper's own adversarial model (C1, C2), how much of Assumption 4 can actually be established, and how much stays a bare assumption.

---

## 1. Grounding in the Published Paper

This section replaces v0.1's Sections 2.1-2.4 (which built pi_i^causal candidates and an Overlap Consistency Proposition from scratch). Everything in this section is a citation to `docs/formal/references/pders_main_reference.md`, not a new definition.

### 1.1 The objects, as the paper actually defines them

- **Ri (Local Simulation Relations)**: `Ri ⊆ S^i_eff × S^i_spec`, required to satisfy `δ^i_eff ⊑Ri πi(δspec)` ("Local Simulation Relations"). Not a per-transition boolean predicate by itself; it is the refinement relation between node i's physical execution state and its projected specification state.
- **Omega_i (Node Safety Invariant, Definition 1)**: `Ωi : S^i_eff → {0, 1}`. A state predicate: is the current state safe.
- **Psi_i (Transition Safety Invariant, Definition 2)**: `Ψi : S^i_eff × L × S^i_eff → {0, 1}`. A transition predicate: is this specific state change safe.
- **Local Invariant Gate**: the runtime acceptance rule that ties all three together: `Accept(s, l, s') ⇐⇒ Ri ∧ Ωi(s') = 1 ∧ Ψi(s, l, s') = 1`. This is the paper's own name for exactly the "single unified gate" that the predecessor investigation (`pDERS_Ri_Omega_Psi_source_investigation_v0.1.md`, Section 2.4-2.5) had flagged as a possible alternative to a three-way split, found only in kimura hakase's own promotional text. The paper resolves that open question directly: it is both - one named runtime gate (`Accept(...)`), built from three separately-defined, separately-typed formal objects (Ri, Omega_i, Psi_i). Neither of the two readings that investigation left open ("three-way split" vs. "single gate") was fully right in isolation; the paper has both, at different levels of description.

### 1.2 Assumption 4 (Projection Consistency), verbatim

> Let S^ij = πi(Sspec) ∩ πj(Sspec). For every transition within S^ij, Ωi = Ωj and Ψi = Ψj over the shared domain.

This is, as the instructing memo for this revision observed, substantively the same content v0.1 tried to construct independently as its "Overlap Consistency Proposition." The paper states it as a **named, numbered assumption** feeding into Theorem 4 - not as something the paper itself proves.

### 1.3 Theorem 4 (Decentralized Safety Preservation), verbatim

> Assume Assumptions 1-4, local refinement for all nodes, and an independently verified global specification. For every accepted trace σ^i_eff, ∃ σspec ∈ T(δspec) s.t. σ^i_eff ≈i πi(σspec), and Ωi(sk) = 1 for every state sk in the accepted trace.

Per Section 2 of this document (task item 4 of the instructing memo), this statement is adopted here as the target property, replacing v0.1's independently-constructed notion of "globally safe." No new definition of safety is introduced in this revision.

### 1.4 The Adversarial Model clauses relevant to this document

> **C1. Partial Observability Exploitation.** No execution node possesses complete knowledge of the global execution graph. The adversary exploits inconsistent local observations by scheduling transitions whose individual legality differs from their collective global consequence.
>
> **C2. Causal Reordering.** Because communication is asynchronous, messages may arrive in different orders across different nodes. An adversary may intentionally exploit network latency to construct alternative causal histories.

C3 (Semantic Composition) and C4 (Autonomous Behavioral Drift) are part of the paper's full threat model but are not the focus of this revision, which is scoped (per the instructing memo) to what C1 and C2 specifically imply for Assumption 4's verifiability.

---

## 2. What Assumption 4 Already Gives Us

Granting Assumptions 1-4 as hypotheses (i.e. not questioning them yet - that is Section 3), Theorem 4's proof (as transcribed) establishes, by induction on trace length, that every state in an accepted trace at node i satisfies `Ωi(sk) = 1`, and that the whole trace stays observation-equivalent to some valid global specification trace. This is a genuinely useful, non-trivial guarantee: it says node i's own accepted history never drifts into a state its own safety invariant rejects, and it always corresponds to *some* legitimate global run.

A precise thing worth stating plainly, because it matters for Section 3: **as transcribed, Theorem 4's proof is a single-node statement.** It is quantified per node i ("for every accepted trace σ^i_eff... Ωi(sk) = 1"), not across a pair of nodes i, j. The inductive step invokes the Local Invariant Gate and Lemma 2 (`Ωi(sk)=1 ∧ Ψi(sk,l,sk+1)=1 ⟹ Ωi(sk+1)=1`) - both of which are purely about node i's own predicates, applied to node i's own trace. Nowhere in the transcribed proof of Theorem 4 is a second node j, or Assumption 4's cross-node equality (`Ωi = Ωj`), explicitly invoked as a proof step.

Assumption 4 is listed among Theorem 4's stated hypotheses, but on the evidence of the transcribed proof text, its *work* is not visible inside that specific single-node argument. Where the paper's own narrative *does* point to a role for Assumption 4 is the Figure 1 description's composition story ("Cryptographic composition: H(Ti) ‖ H(Tj) ‖ H(Tk) → global safety proof... propagates local safety guarantees globally without requiring a shared simulation relation R") and Corollary 5's framing ("cannot extend the accepted execution history" - which reads naturally as a claim about the *system's* accepted history, not one node's). Both of these gesture at a multi-node composition claim that is narratively present in the paper but - as far as this transcription shows - is not itself stated as a separate, numbered theorem with its own proof. This is recorded as an open question in Section 5, not resolved here: it is possible the actual PDF has a composition theorem this transcription's "sketch"-level proofs compressed out (conference page limits routinely do this), or it is possible Assumption 4's cross-node content is genuinely used only informally/narratively and not formally discharged anywhere in the paper as given. Either way, **what Theorem 4 as transcribed actually delivers is a per-node safety guarantee conditioned on Assumption 4 holding; it does not, by itself, show how or why Assumption 4 would hold.**

---

## 3. The Open Gap: Can Assumption 4 Be Verified Under C1/C2?

This is the core of this revision. The question is not "is Assumption 4 true" (a property depends on what a given deployment plugs in for Omega_i/Psi_i/pi_i, discussed below) but "can a deployment establish that it holds, given the paper's own adversarial model." The answer bifurcates cleanly into two cases, depending on a design choice the paper itself leaves unspecified.

### 3.1 First, a fact independent of C1/C2: Assumption 4 does not follow from Assumptions 1-3 or from the type signatures alone

Omega_i is typed only as `S^i_eff → {0,1}` (Definition 1); Psi_i only as `S^i_eff × L × S^i_eff → {0,1}` (Definition 2). Nothing in these type signatures, nor in Assumptions 1-3 (Projection Homomorphism, Monotonic Refinement, Observation Consistency - all of which are properties of the projection functions pi_i, not of Omega_i/Psi_i's content), constrains what Omega_i and Omega_j actually compute. A trivial, type-correct instantiation - `Omega_i ≡ 1` (node i considers every state safe) and `Omega_j ≡ 0` (node j considers every state unsafe) - satisfies Definitions 1-2 and Assumptions 1-3 while violating Assumption 4 on any non-empty overlap `S^ij`. This shows Assumption 4 is a genuinely independent constraint: nothing internal to the paper's other definitions guarantees it "for free" for an arbitrary choice of the per-node predicate family `{Omega_i}`, `{Psi_i}`. This holds regardless of C1/C2 - it is a fact about the framework's degrees of freedom, not about the adversarial model - and it is why the paper correctly presents Assumption 4 as an assumption rather than a derived lemma.

### 3.2 Branch 1: Omega_i/Psi_i systematically derived from one shared specification-level definition

Suppose a deployment does not author `Omega_i` independently per node, but instead derives every `Omega_i` (and `Psi_i`) from a single, shared global safety policy at the `Sspec` level via one fixed, deterministic recipe applied identically at every node - e.g., `Omega_i(s) := GlobalPolicy(lift_i(s))` for some consistent lifting `lift_i` tied to `pi_i`. Under this discipline, whether `Omega_i = Omega_j` on the shared domain `S^ij` becomes a static property of the shared recipe and the projection functions, checkable once, offline, by inspecting the definitions - not something that needs to be observed or reconciled at runtime.

Under this branch, **C1 and C2 do not threaten Assumption 4's establishability**, because C1 (no node has complete runtime knowledge of the global execution graph) and C2 (asynchronous message reordering) are both threats to what a node can observe *during execution*; they say nothing about a property that a designer can prove once, at design time, by comparing two function definitions. This is consistent with how Lemma 1's proof sketch treats Assumption 4 - as a given premise used to argue about invariant evaluations, not as something the proof itself needs to verify operationally.

**Verdict for Branch 1: provable, conditionally.** The condition is that the deployment actually follows a shared-derivation discipline for `{Omega_i}`/`{Psi_i}`. The paper's own text does not state this condition as a requirement - see Section 5, item 1.

### 3.3 Branch 2: Omega_i/Psi_i independently authored or independently updated per node

Suppose instead - and nothing in the paper rules this out - that different nodes' `Omega_i` are authored, configured, or updated independently (different agent owners, different teams, different deployment timelines, independently patched safety policies). Now Assumption 4 is a genuinely at-risk runtime property, not a static one, and this is exactly where C1 bites:

- **C1 (Partial Observability Exploitation)** is stated as "no execution node possesses complete knowledge of the global execution graph." For node i to confirm `Omega_i = Omega_j` on `S^ij`, it would need to evaluate `Omega_j` on states in the overlap and compare - but `Omega_j` is node j's own local predicate; node i has no architectural channel to invoke it. Nothing in the Local Invariant Gate (`Ri ∧ Omega_i(s')=1 ∧ Psi_i(s,l,s')=1`, Section 1.1) references any other node's predicates at all - the Gate is, by its own formula, a single-node check.
- The only architectural component that touches cross-node/cross-history consistency at all is the **Async Drift Compensator** ("monitoring trace histories for observation equivalence drift, forcing rollbacks to verified projection anchors if out-of-order anomalies are detected" - `docs/formal/references/pders_main_reference.md`, Reference Runtime Architecture). Two things about it matter here: (a) it is explicitly **asynchronous**, operating after acceptance, not before; and (b) it is described as reconciling **observation-equivalence drift** in trace histories, not as directly comparing `Omega_i` and `Omega_j`'s outputs against each other - it is not obviously the same check Assumption 4 asks for, only plausibly related to it.
- This creates a direct tension with the paper's own **Security Objective** paragraph, which states every accepted transition must "preserve all required node-level safety invariants" as one of three simultaneous, pre-acceptance conditions. If Assumption 4 is false at runtime for a Branch-2 deployment, nothing in the Local Invariant Gate (the only synchronous, pre-mutation checkpoint) would detect it, because the Gate never looks at a second node's predicates. Detection, if it happens at all, happens only later, asynchronously, in the Drift Compensator - after the state mutation the Security Objective says should have been prevented.

**Verdict for Branch 2: not provable from what the paper gives; a concrete counterexample-shaped instantiation (3.1) shows it can fail; and the paper's own architecture provides no synchronous mechanism that would catch a failure before the Security Objective is already violated.** This is not a claim that the paper is wrong - Assumption 4 is presented as an assumption, and the paper's Limitations section explicitly says "p-DERS assumes... that projection functions satisfy the consistency properties of Section 4" - it is a claim that, for Branch-2-style deployments, nothing currently discharges that assumption, and C1 is a specific, named reason no node could discharge it unilaterally even if it tried.

### 3.4 A complication that survives even in Branch 1: C2 and state correspondence

Branch 1's design-time argument (3.2) shows `Omega_i` and `Omega_j` can be the *same function*. It does not by itself show that node i and node j, operating asynchronously, will apply that function to *states they agree correspond to the same point in the shared history*. Under C2 (Causal Reordering), node i and node j may observe messages affecting the shared region `S^ij` in different orders, so even with identical `Omega_i ≡ Omega_j`, the states each node currently associates with "the current shared state" could diverge, at least transiently, from asynchronous message delivery alone - making a would-be comparison between "node i's view" and "node j's view" ill-posed unless there is a way to establish which local observations correspond to which causal point. This is precisely the problem Track A's own predecessor document was built around (`pDERS_causal_projection_v0.1.md` Section 1.3, "Order-loss" and "Concurrency-collapse"), and it is addressed further in Section 4 below.

---

## 4. Role of Vector Clocks (Candidate B) in This Gap

The paper already uses vector clocks, in the **Formal Trace Recorder**: "Append-only, lock-free concurrent buffer recording accepted execution traces against logical vector clocks, ensuring linear history capture without global clock synchronization" (`docs/formal/references/pders_main_reference.md`, Reference Runtime Architecture). Per Figure 2's description, the Trace Recorder sits *after* the Local Invariant Gate, on the accept path, feeding into the asynchronous Cryptographic Proof Log and Drift Compensator - not into the Gate's own `Accept(...)` decision.

This matters directly for the question this document is asking. Track A's own Candidate B (`pDERS_causal_projection_v0.1.md` Section 2.3), adopted by Human Gate (`pDERS_overlap_consistency_v0.1.md` Section 1), proposed `pi_i^causal(s) = (pi_i(s), V_i)` - embedding vector-clock metadata directly into the **projection function's own output**. Under Mode M2 (`pDERS_causal_projection_v0.1.md` Section 3.1), this would make causal/concurrency metadata available to Ri/Omega_i/Psi_i's own evaluation - i.e., potentially part of the synchronous, pre-mutation Gate decision itself.

These are the same underlying data structure (vector clocks) used at two different points in the same conceptual pipeline, and it is worth being precise that they are not simply the same proposal under two names:

| | Paper's Formal Trace Recorder | Track A's Candidate B (pi_i^causal, Mode M2) |
|---|---|---|
| Position in pipeline | After acceptance (post-Gate) | Inside the projection, potentially consulted by the Gate itself |
| Timing | Asynchronous | Synchronous, if Mode M2 is adopted |
| Stated purpose | "linear history capture," feeding audit/cryptographic accountability and drift reconciliation | Making causal-order/concurrency information available to the acceptance decision itself |
| Relationship to Assumption 4 | Not currently connected to it at all - the Drift Compensator's "observation-equivalence drift" check is the closest thing, and it is post-hoc (Section 3.3) | Directly motivated by closing exactly the state-correspondence problem in Section 3.4, if Mode M2 is pursued |

Given Section 3.4's finding - that even a Branch-1-style deployment (identical `Omega_i`/`Omega_j` by design) can still face an ill-posed cross-node comparison under C2 unless causal correspondence is established - the paper's own reference architecture, as described, does not appear to close that particular gap: its vector clocks are positioned to support audit and drift-correction *after* the fact, not to inform the accept/reject decision *at* the fact. Track A's Candidate B, if extended to Mode M2, is aimed exactly at the point in the pipeline the paper's Security Objective says matters (before state mutation) rather than the point the paper's existing Trace Recorder actually occupies (after it).

This is stated carefully as a **motivation**, not a validated result: this document does not claim Track A's Candidate B, even under Mode M2, actually closes the gap. The predecessor document's own Lemma 2 (`pDERS_overlap_consistency_v0.1.md` Section 3.3) remains unproven, for reasons that substantially overlap with Section 3.3 of this document (the M1/M2 choice was one of Lemma 2's four named missing prerequisites - and it is now clearer that, as given, the paper's own `Accept(...)` formula is Mode-M1-shaped: `Ri`, `Omega_i(s')`, and `Psi_i(s,l,s')` take no clock argument at all, so if the paper's definitions are taken literally, Mode M1 is what currently exists, and Mode M2 is a proposed extension the paper itself does not make).

---

## 5. Open Questions (updated)

### 5.1 New, arising from this revision

1. **Does the paper require, anywhere, that `{Omega_i}`/`{Psi_i}` be derived from one shared specification-level policy (Branch 1, Section 3.2), or is this left to deployment discretion (permitting Branch 2, Section 3.3)?** As transcribed, the paper does not state this requirement explicitly; the Limitations section's "projection functions satisfy the consistency properties of Section 4" reads as stating the *outcome* required (Assumption 4 holding) without mandating a *method* (a derivation discipline) for achieving it. This is worth checking against the actual PDF directly, since a requirement stated elsewhere in the paper (a section this transcription may not have captured in full) would resolve Section 3's bifurcation in Branch 1's favor for compliant deployments.
2. **Is there an unstated (or transcription-compressed) multi-node composition theorem this document hasn't seen?** Section 2 noted that Theorem 4's transcribed proof is single-node, while Figure 1's description and Corollary 5's phrasing gesture at a system-wide composition claim. Whether the actual paper has a further, separately-numbered theorem making that composition explicit (and using Assumption 4's cross-node content directly) is unknown from this transcription alone.
3. **Does the Async Drift Compensator's "observation equivalence drift" check actually test Assumption 4, or something related but distinct?** Section 3.3 treated these as only "plausibly related," not identical, because the paper's description of the Drift Compensator is in terms of trace/observation equivalence, not in terms of directly comparing `Omega_i` and `Omega_j`'s outputs. This distinction matters for how much protection Branch-2 deployments actually get from the existing architecture, and this document does not resolve it.
4. **Transcription fidelity** (carried from `docs/formal/references/pders_main_reference.md`'s own flagged list): the exact reading of `⊑Ri`, whether "Ωi = Ωj" in Assumption 4 is literal function equality or a per-argument biconditional, and whether the Figure 1/2 descriptions are reliable paraphrases of the real captions. None of these were resolved here.

### 5.2 Inherited from v0.1, restated with what has changed

- **Dynamic node membership** (v0.1 Open Question 4 / 7 area): still unaddressed. The paper's system model fixes `N = {1,...,n}` as a finite set with no discussion of nodes joining or leaving; this document's Section 3 analysis (and v0.1's Lemma 1, on vector-clock overlap comparability) both still implicitly assume a static node set.
- **Merge/conflict-resolution semantics for concurrent updates** (v0.1 Open Question 5): still not given by the paper. `Psi_i` is a per-node transition predicate; nothing in the transcribed text specifies how two nodes' concurrent, causally-unordered transitions touching the same shared region should be reconciled, beyond the post-hoc Drift Compensator's rollback-to-anchor behavior (which resolves a detected conflict by discarding, not by a stated merge rule).
- **M1 vs. M2 compatibility mode** (v0.1 Open Question 7): now more concrete rather than fully resolved. As transcribed, the paper's own `Accept(...)` formula is Mode-M1-shaped (Section 4 above) - `Ri`/`Omega_i`/`Psi_i` do not take causal-metadata arguments. Whether a Mode-M2 extension is desirable, and if so how it should be specified, remains open and is not attempted here.
- **"Globally safe" definition** (v0.1 Open Question, and v0.1's own from-scratch construction generally): superseded per this revision's Section 1.3 - Theorem 4's statement is adopted as the target property. v0.1's own definition is not used going forward, but is not deleted; it remains available for comparison in v0.1.
- **Canonical content of R_i/Omega_i/Psi_i** (v0.1 Open Question 1, and the entire subject of `pDERS_Ri_Omega_Psi_source_investigation_v0.1.md`): resolved at the level of *type signatures and the Gate formula* (Section 1.1 above), but not at the level of *logical content* - Section 3.1 shows this is inherent to the framework (Omega_i/Psi_i are deliberately left parametric/uninstantiated), not a gap in this investigation. Any concrete deployment's Assumption 4 status depends on its own choice of `{Omega_i}`, which the paper does not fix.

This document does not close any of the items above; they are handed forward as-is or as newly sharpened.

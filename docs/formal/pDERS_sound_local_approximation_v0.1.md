# Sound Local Approximation - A Formal Deep Dive v0.1

Document ID: PDERS_SOUND_LOCAL_APPROXIMATION_v0.1
Version: 0.1
Status: New theoretical development, deliberately scoped to a general design pattern; Section 4 is conditional only and asserts nothing about MoCKA's actual implementation
Track: Track A (Formal Theory Track, p-DERS) - first task in this series to deliberately approach the Track B boundary, under explicit Human Gate authorization following DC_20260730_001
Predecessors: docs/formal/pDERS_compositional_safety_v0.1.md (Section 3.3, where Sound Local Approximation was first named), docs/formal/pDERS_overlap_consistency_v0.2.md, docs/formal/references/pders_main_reference.md
Independence / scope note: this document performs no investigation of, and makes no claim about, MoCKA's actual Governance Function `G`, its implementation, or Track B code. Section 4 is written entirely as a conditional ("if a system has property X, then...") - whether MoCKA satisfies any stated condition is left to Human Gate or a separate Track B task. No Decision Ledger write is performed by this document (`DC_20260730_001` was an explicitly one-time exception, per its own text). No MoCKA MCP tools were used to produce this document - it needed no current MoCKA data, per the instructing memo's scope.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase)

---

## 1. Formal Definition of Sound Local Approximation

`pDERS_compositional_safety_v0.1.md` Section 3.3 introduced Sound Local Approximation informally, as a state-level definition (`Omega_i(s)=1 implies Omega_G(sigma)=1`) with a paragraph of prose describing four claimed properties. This section turns each of those four properties into an explicit proposition, and extends the original state-level (`Omega`) definition to the transition-level (`Psi`) predicate the paper's own Local Invariant Gate also requires.

### 1.1 Base definitions (extending the original to Psi)

**Definition (Sound Local Approximation, Omega).** `Omega_i` is a sound local approximation of a reference `Omega_G : Sspec -> {0,1}` (with respect to `pi_i`) if, for every `s in S^i_spec` and every `sigma` with `pi_i(sigma) = s`: `Omega_i(s) = 1 implies Omega_G(sigma) = 1`. (Unchanged from `pDERS_compositional_safety_v0.1.md`.)

**Definition (Sound Local Approximation, Psi).** `Psi_i` is a sound local approximation of a reference `Psi_G : Sspec x L x Sspec -> {0,1}` (with respect to `pi_i`) if, for every `(s,l,s')` in `S^i_spec x L x S^i_spec` and every `(sigma,l,sigma')` with `pi_i(sigma)=s`, `pi_i(sigma')=s'`: `Psi_i(s,l,s') = 1 implies Psi_G(sigma,l,sigma') = 1`.

Both are one-directional: `Omega_i`/`Psi_i` may be strictly *more conservative* than `Omega_G`/`Psi_G` (rejecting states or transitions the reference would allow) but must never *accept* what the reference would reject. This is the property that does the actual safety work below.

### 1.2 Property 1 (Single Public Reference) - formalized

**P1.** There exists exactly one pair `(Omega_G, Psi_G)` in force at any given time `t`, denoted `(Omega_G^(t), Psi_G^(t))`, such that: (a) it is *published* - readable by whoever is verifying any node's soundness, independent of that node's own runtime execution state; (b) it is *singular* - there is no second, competing reference in force for the same node set at the same time; (c) it is *versioned* - `(Omega_G^(t), Psi_G^(t))` may change over time, but at every instant there is exactly one currently-in-force reference, identified unambiguously.

P1 is doing real work: without singularity, "sound with respect to the reference" is not even well-posed (sound with respect to *which* reference, if two compete). Without publication, Property 2 below cannot be discharged by an independent verifier who lacks runtime access to the node. Versioning is addressed further in Section 2.2.

### 1.3 Property 2 (Independent Soundness Proof) - formalized

**P2.** For every node `i in N`, there is a proof obligation, discharged once (at node i's design or onboarding time), that `Omega_i` is a sound local approximation of `Omega_G^(t)` (and `Psi_i` of `Psi_G^(t)`) for the reference version `t` in force at that time. Crucially, this proof obligation is a predicate over `(Omega_i, Psi_i, pi_i, Omega_G^(t), Psi_G^(t))` alone - it does not quantify over, or require any information about, any other node `j in N \ {i}`.

This is the precise sense in which Sound Local Approximation requires "no pairwise checks" (contrasted with Candidate (b), pairwise onboarding contracts, in `pDERS_compositional_safety_v0.1.md` Section 3.2): P2's proof obligation for node i literally does not mention node j anywhere in its statement, whereas (b)'s pairwise contract is, by definition, a two-node predicate.

### 1.4 Property 3 (No Runtime Coordination) - formalized

**P3.** The Local Invariant Gate's runtime acceptance decision at node i, `Accept_i(s,l,s') := Ri and Omega_i(s')=1 and Psi_i(s,l,s')=1` (the paper's own formula, unchanged - `docs/formal/references/pders_main_reference.md`, "Local Invariant Gate"), does not take as input any data originating from another node `j` at execution time, and its evaluation involves no message exchange with any other node.

This is worth stating precisely because it means Sound Local Approximation requires **zero change to the paper's own runtime Gate**. All of P2's work happens at the design/onboarding-time proof-obligation layer; nothing about the synchronous, per-transition decision changes at all. This distinguishes Sound Local Approximation sharply from Candidate (a) (synchronous cross-node gate, `pDERS_compositional_safety_v0.1.md` Section 3.1), which *does* require changing `Accept_i` itself to a new formula involving a cross-node query.

### 1.5 Property 4 (Scalability to Variable Node Sets) - formalized, with a proven sub-lemma

**P4.** Let `N(t)` denote the (possibly time-varying) node set. For a new node `i*` joining at time `t*` (i.e. `i* not in N(t)` for `t < t*`, `i* in N(t)` for `t >= t*`), discharging P2 for `i*` requires only `(Omega_{i*}, Psi_{i*}, pi_{i*}, Omega_G^(t*), Psi_G^(t*))` - it requires neither re-verifying, nor even enumerating, any existing node `j in N(t)` for `t < t*`.

This lets us state, and actually prove, a small monotonicity result that was only asserted informally in `pDERS_compositional_safety_v0.1.md`:

**Lemma S1 (Join-Monotonicity) - proven.** Suppose every `i in N(t)` satisfies P2 with respect to `(Omega_G^(t), Psi_G^(t))`, and a new node `i*` joins at `t* > t` with `(Omega_{i*}, Psi_{i*})` independently verified sound with respect to the *same* `(Omega_G^(t), Psi_G^(t))` (no reference change at `t*`). Then every `i in N(t*) = N(t) union {i*}` satisfies P2.

*Proof.* P2 is, by construction (Section 1.3), a per-node predicate with no quantification over other nodes. Adding `i*` to the node set does not alter the statement or the proof of P2 for any `j != i*` - their proofs never mentioned `i*`, or any other node, in the first place. `i*` satisfies P2 by the join-time proof supplied. Hence every member of `N(t*)` satisfies P2. `[]`

This is a genuine, clean, fully proven result - not a hedge. It is also, deliberately, a small one: it shows joining is cheap *when the reference does not change at join time*. What happens when the reference itself changes is a separate, harder question, addressed in Section 2.2, where the proof does not go through as cleanly.

---

## 2. Conditions for Soundness under Branch 2

Section 1 formalizes what Sound Local Approximation *is*. This section addresses the instructing memo's specific question: what does P1's "single public reference" itself require, for the whole scheme to actually deliver a safety guarantee?

### 2.1 Who guarantees the reference's own correctness? (Unresolved, and not unique to this document)

Sound Local Approximation, exactly as defined in Section 1, only ever shows `Omega_i(s)=1 implies Omega_G(sigma)=1`. It says nothing about whether `Omega_G` itself correctly encodes whatever the *true* intended safety property is. If `Omega_G` is wrong - too permissive, say - every node soundly approximating it will faithfully, uniformly, and undetectably accept the same unsafe class of states. This is a real, honest limitation worth stating plainly: **Sound Local Approximation does not eliminate the correctness burden that existed under raw Branch 2 (independently-authored, potentially inconsistent `Omega_i`'s); it relocates it** - from "N potentially-differently-wrong local predicates" to "one reference, uniformly wrong if wrong at all." Whether concentrating the risk this way is an improvement is not evaluated here; it is a different risk shape, not an eliminated one.

This is not a gap unique to Sound Local Approximation or to this document. Theorem 4 itself (`docs/formal/references/pders_main_reference.md`) states its hypotheses as "Assume Assumptions 1-4, local refinement for all nodes, **and an independently verified global specification**" - i.e., the paper's own headline theorem already presupposes, without discharging, that `Sspec`/`delta_spec` are correct. Sound Local Approximation inherits exactly the same kind of undischarged assumption, one level down, for `Omega_G`/`Psi_G` specifically. This document does not attempt to supply what the paper itself never supplies.

### 2.2 What happens when the reference is updated?

This is where Sound Local Approximation's story is more interesting than a simple restatement of "someone has to keep it correct" - the answer to "does an existing node's proof survive a reference update" depends on the *direction* of the update, and this can be shown precisely rather than left as a vague concern.

**Lemma S2 (Update Monotonicity under Weakening) - proven.** Suppose the reference is updated from `Omega_G^(v)` to `Omega_G^(v+1)`, where the update is a *weakening*: `Omega_G^(v)(sigma) = 1 implies Omega_G^(v+1)(sigma) = 1` for all `sigma in Sspec` (the new reference accepts everything the old one did, and possibly more). If `Omega_i` was sound with respect to `Omega_G^(v)`, then `Omega_i` is automatically sound with respect to `Omega_G^(v+1)`, with no re-proof required.

*Proof.* Fix `s` and `sigma` with `pi_i(sigma)=s` and `Omega_i(s)=1`. By the existing soundness proof, `Omega_G^(v)(sigma)=1`. By the weakening hypothesis, `Omega_G^(v)(sigma)=1 implies Omega_G^(v+1)(sigma)=1`. Chaining these, `Omega_G^(v+1)(sigma)=1`. `[]` (Identical argument for `Psi`.)

**Counterexample showing the converse (strengthening) does not preserve soundness automatically.** Suppose instead the update is a *strengthening*: `Omega_G^(v+1)(sigma)=1 implies Omega_G^(v)(sigma)=1`, but not conversely - some `sigma_0` has `Omega_G^(v)(sigma_0)=1` while `Omega_G^(v+1)(sigma_0)=0` (the new reference is more restrictive; a state it used to consider safe, it no longer does). If `Omega_i(pi_i(sigma_0)) = 1` (node i's predicate, verified sound against the old, looser reference, happily accepts the observation corresponding to `sigma_0`), then after the update, `Omega_i(pi_i(sigma_0)) = 1` still holds (nothing about node i's own predicate changed), but `Omega_G^(v+1)(sigma_0) = 0` - so `Omega_i` is **no longer sound** with respect to the new reference. Re-verification (or re-authoring of `Omega_i`) is required.

**Consequence.** Reference *weakenings* are free (Lemma S2); reference *strengthenings* require every existing node's soundness to be re-established - which reintroduces, for the strengthening case only, exactly the O(n)-per-update cost that Property 4 was supposed to avoid for node joins. This is a precise, asymmetric finding this document had not previously stated anywhere in this Track A series: Sound Local Approximation's scalability advantage (Section 1.5) is real for *node growth* but does not, on its own, extend to *reference change* in the strengthening direction. Whether governance policies in practice change more often by weakening or by strengthening is not something this document assesses.

---

## 3. Relationship to Lemma A / Lemma B

The instructing memo asks directly: is Sound Local Approximation a substitute for Condition F + Condition C (which together give Lemma A in `pDERS_compositional_safety_v0.1.md`), or a complement operating at a different layer? And does it sidestep Lemma B's lifting/completeness gap, or run into the same wall?

### 3.1 A clean, provable per-node upgrade - what Sound Local Approximation actually gives for free

**Proposition (Local Upgrade under Sound Approximation) - proven.** If `Omega_i`, `Psi_i` are sound local approximations of `Omega_G`, `Psi_G`, then for every accepted trace `sigma^i_eff` at node i (Theorem 4's own object), not only does `Omega_i(sk) = 1` hold at every state (Theorem 4's conclusion, unconditionally, from the paper itself), but `Omega_G` holds at the corresponding projected-specification witness state at every step as well.

*Proof.* Immediate composition of Theorem 4's own conclusion (`Omega_i(sk)=1` for every `sk` in the trace) with the Sound Approximation implication (Section 1.1) applied at each step. No additional machinery - not Lemma A, not Condition F or C, not the Causal Alignment Hypothesis - is needed. `[]`

This is a genuine, clean result, and it is worth being precise about exactly what it delivers: **it strictly upgrades a single node's own guarantee** - from "safe with respect to my own, possibly idiosyncratic `Omega_i`" to "safe with respect to the one true published `Omega_G`" - **without touching the multi-node question at all.**

### 3.2 What it does not give: it is not a substitute for Lemma A

Lemma A (`pDERS_compositional_safety_v0.1.md` Section 2.2) establishes `Omega_i = Omega_j` - a literal, two-node *agreement* - on the shared overlap `S^ij`. Sound Local Approximation establishes no such thing. Two nodes `i, j`, both independently sound with respect to the *same* `Omega_G`, can still be differently conservative and can still disagree with each other on a specific shared observation `s in S^ij`: node i might have `Omega_i(s) = 0` (rejecting, conservatively, something `Omega_G` would actually allow) while node j has `Omega_j(s) = 1` (accepting, and correctly so, since `Omega_G(sigma)=1` for the corresponding `sigma`). Neither node is *wrong* - both are sound - but they disagree, which is exactly what Assumption 4 / Lemma A rules out and Sound Local Approximation does not.

**Consequence for the Compositional Safety Theorem's proof structure** (`pDERS_compositional_safety_v0.1.md` Section 2.5): that proof's Step 1 (pairwise state-and-order compatibility) used Lemma A specifically to rule out semantic disagreement on the overlap. Sound Local Approximation, used in place of Lemma A, does **not** get Step 1 to go through - it gives each node's *own* trace a genuine safety upgrade (Section 3.1), but it establishes no relationship at all between what two different nodes would say about a state they both observe. So Sound Local Approximation is **not a cheaper way to reach the same place Lemma A reaches** - it answers a different, strictly weaker question (per-node correctness against one ground truth) than the question Lemma A answers (cross-node agreement). This is the precise sense in which it is neither a substitute nor, exactly, a complement in the sequential sense the instructing memo's phrasing might suggest - it operates on an entirely separate axis from Lemma A, upgrading a different guarantee, and simply does not engage with the cross-node agreement problem Lemma A was built to solve.

### 3.3 Lemma B's gap is untouched

Lemma B (`pDERS_compositional_safety_v0.1.md` Section 2.5, Step 2) - whether pairwise-compatible local traces guarantee the existence of one single global witness trace realizing all of them - sits at a still further remove from anything Sound Local Approximation addresses. Sound Local Approximation operates entirely within a single node's own relationship to `Omega_G`; it says nothing about `delta_spec`'s lifting/completeness properties, which is what Lemma B is about. Even in the best case - every node in `N` independently sound with respect to the same `(Omega_G, Psi_G)` - Lemma B's gap remains exactly as open as it was in `pDERS_compositional_safety_v0.1.md`: nothing here supplies, or even bears on, the missing completeness property of `{pi_i}` with respect to `delta_spec`.

### 3.4 Summary position

Sound Local Approximation is best understood as a **third, independent axis**, not a point on the Branch 1 / Branch 2 spectrum and not a substitute for either Lemma A or Lemma B:

| | Addresses | Cost | Status here |
|---|---|---|---|
| Condition F + C (-> Lemma A) | Cross-node agreement on shared observations | Requires shared-derivation discipline or pairwise checking | Proven (Lemma A), given F+C |
| Causal Alignment (v0.1 Lemma 1) | Cross-node agreement on event ordering | Requires Candidate B + static membership | Proven, inherited |
| Lemma B | Existence of one global witness trace | Unknown - no proposed mechanism anywhere in this series | Unproven, open |
| Sound Local Approximation | Per-node correctness against one ground truth | One-time proof per node, no cross-node data at all | Proven (Section 3.1), but answers a different question |

Achieving all of the top three simultaneously is what the full Compositional Safety Theorem (`pDERS_compositional_safety_v0.1.md` Section 2.4) would require; Sound Local Approximation does not shortcut any of them - it is a genuinely useful, independent guarantee about a question those three do not ask (is each node's own local judgment actually correct, not merely mutually consistent with its peers).

---

## 4. Conditional Mapping to MoCKA's Governance Function G

**Scope note, restated once more for emphasis:** everything in this section is conditional. No claim is made, and no investigation was performed, about whether MoCKA's actual Governance Function `G`, or its actual multi-agent operation (Claude / Codex / Gemini / Human Operator), satisfies any condition stated below. This document takes the existing Track A/B correspondence table's headline mapping (`Omega_i <-> Governance Invariant`, as referenced in the instructing memo) as a given starting point supplied by that memo, not as something this document has independently verified against MoCKA's Track B materials - this document has not read those materials for this task, per its own scope restriction.

**If** a multi-agent governance system has the following four properties, **then** the Sound Local Approximation framework (Sections 1-3 above) applies to it, with the stated guarantees and the stated limitations:

- **(C1) Single Published Policy**: there exists one, singularly-identified, published Governance Policy (playing the role of `Omega_G`/`Psi_G`) that every participating agent (playing the role of a node `i in N`) is expected to comply with - as opposed to each agent operating against its own, independently-conceived notion of acceptable behavior with no common reference point at all.
- **(C2) Independently-Implemented Compliance**: each agent's own mechanism for deciding whether to take a given action (playing the role of `Omega_i`/`Psi_i`) is implemented independently per agent - plausible on its face for a heterogeneous set of agents (different underlying models, different tooling, a human operator) that are unlikely to share one literal codebase for this decision - **and** each agent's compliance mechanism is intended to be a *sound* (possibly conservative, never permissive-beyond-the-policy) approximation of the single published policy from (C1), rather than an unrelated, freestanding judgment.
- **(C3) No-Coordination Onboarding**: when a new agent or operator is added to the system, establishing that its own compliance mechanism is sound with respect to the published policy does not require pairwise coordination with, or knowledge of, every other currently-participating agent.
- **(C4) A Defined Policy-Update Process**: the published policy itself has a well-defined versioning and update mechanism, ideally one that is aware of the weakening/strengthening asymmetry identified in Section 2.2 - i.e., that update events that make the policy *more* permissive can be treated as low-cost, while updates that make it *more* restrictive are understood to require re-establishing every existing agent's compliance, not merely the new agent's.

**Given (C1)-(C4)**, the theoretical guarantees available would be, per Sections 1 and 3 of this document: every agent's own actions individually verified never to violate the one published ground-truth policy (Section 3.1's Local Upgrade), achieved without any runtime coordination between agents (Section 1.4), and scaling cleanly to a changing roster of agents joining (Section 1.5, Lemma S1) so long as the policy itself is not being strengthened at the same moment (Section 2.2, Lemma S2 and its counterexample).

**Equally, given (C1)-(C4) alone**, what would *not* be established, per Section 3: any guarantee that two different agents, both individually policy-compliant, would reach the *same* verdict on an identical piece of shared governance-relevant state or context (Lemma A's question, unanswered here); nor any guarantee that the individual agents' action histories can be reconstructed into one single, coherent global governance history (Lemma B's question, entirely untouched). If either of those stronger properties is actually desired of a system satisfying (C1)-(C4), Sound Local Approximation alone is not sufficient to deliver them, per Section 3.2-3.3 above.

Whether MoCKA's actual Governance Function `G` and its actual multi-agent operation satisfy (C1)-(C4) - in whole, in part, or not at all - is not assessed here. That determination belongs to Human Gate or to a separately-authorized Track B investigation.

---

## 5. Open Questions

1. **Reference correctness** (Section 2.1): who verifies `Omega_G`/`Psi_G` are themselves correct, and when - carried forward as unresolved, and noted to be structurally the same undischarged assumption the paper's own Theorem 4 already carries for `Sspec`/`delta_spec` ("an independently verified global specification"). Not resolved here or, as far as this series has found, in the paper itself.
2. **Whether real governance-update practice tends toward weakening or strengthening** (Section 2.2) - this document establishes the asymmetry formally but does not know, and does not investigate, which direction is more common in practice for any real system, including MoCKA (out of scope here).
3. **Whether Sound Local Approximation's weaker guarantee is what is actually wanted**, or whether Lemma A's stronger cross-node agreement is genuinely necessary for some purpose this document has not identified - carried directly from `pDERS_compositional_safety_v0.1.md` Section 5, items 3-4, still unresolved, now sharpened by Section 3.2's precise account of exactly what is given up.
4. **Formal "proof" of soundness for non-formally-specified agents.** Section 1's entire apparatus assumes `Omega_i` is a mathematical predicate that can be formally shown to imply `Omega_G`. Whether, or how, this notion of proof translates to an actual heterogeneous multi-agent setting where at least some participants (LLM-based agents) do not have their own decision criteria specified as formal predicates in the first place, is a real gap between this document's formalism and any concrete application - not addressed here, and not something this document has a proposal for.
5. **Lemma B remains completely untouched**, as established in Section 3.3 - nothing in this document makes any progress on it, and this document does not attempt to.
6. **Whether a hybrid mechanism exists** combining Sound Local Approximation (for per-node ground-truth correctness) with some lighter-weight approximate cross-agent consistency check (short of full Condition F/C) - not proposed, not explored, flagged only as a direction this document did not attempt.
7. **The exact content of the "existing Track A/B correspondence table"** the instructing memo refers to (`Omega_i <-> Governance Invariant`, etc.) was taken as given from the memo's own text; this document did not independently locate, read, or verify that table, consistent with its scope restriction against consulting Track B materials for this task.

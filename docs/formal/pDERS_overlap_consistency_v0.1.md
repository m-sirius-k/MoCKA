# p-DERS Overlap Consistency Theorem - Sketch (Candidate B basis) v0.1

Document ID: PDERS_OVERLAP_CONSISTENCY_v0.1
Version: 0.1 (Draft / Sketch)
Status: DECISION_RECORDED (candidate selection only, this document) - theorem itself NOT closed
Track: Track A (Formal Theory Track, p-DERS)
Predecessor: docs/formal/pDERS_causal_projection_v0.1.md (v0.1)
Independence note: this document is independent of Track B (MoCKA Write Path v1.0 / DC-WP). Nothing here is wired into, or intended to be wired into, any MoCKA implementation, the Decision Ledger, or any MCP write path. Read only research artifact.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase)

Scope reminder (inherited from the predecessor document, Section 0 there): this repository has no committed canonical source for R_i, Omega_i, Psi_i, S_i_spec, or the "Decomposed Trace Safety" theorem referenced in the instructing memo for this task. Everything below that touches those objects is built strictly from how the instructing memo characterizes them, not from a canonical text this document's author has read. This is repeated at the point in Section 3 where it becomes load-bearing, not just here.

---

## 1. Human Gate Decision Record

This section records, inside this document only, the candidate selection communicated in the instructing memo for this task. It is not a Decision Ledger entry. Whether this record should additionally be written to the Decision Ledger (data/decisions/decision_ledger.jsonl) is itself left open - it is a Human Gate / Track B judgment call, not decided or assumed by this document or by the Track A process it belongs to.

Decision, as given:

- Candidate A (Lamport clock): not adopted. Reason (as given): Lamport clocks linearize concurrent transitions via an arbitrary tie-break, so they cannot structurally satisfy P2 (Concurrency non-forcing, docs/formal/pDERS_causal_projection_v0.1.md Section 4), which disqualifies them as a foundation for an Overlap Consistency theorem.
- Candidate B (Vector clock): adopted as the basis for this document. Reason (as given): Candidate B satisfies P1-P4 in the straightforward way, and its metadata bound (O(n), n = number of nodes) is explicit, which lets the theory close (or at least sketch-close) now rather than later.
- Candidate C (Causal slice): deferred as a future-extension candidate, not used as a premise here. Reason (as given): Candidate C best fits audit/replay use cases, but its event set E_i has no defined growth bound (horizon/pruning policy - Open Question 6 of the predecessor document), so it cannot currently satisfy P4 (Boundedness). Revisiting a move from B to C is conditional on a horizon policy being defined separately, which has not happened as of this document.

This document uses only Candidate B from here on. Candidate A is not used even for contrast beyond this record. Candidate C is not used as a premise anywhere below; where a future extension to C is worth flagging, it is placed in Section 5 as an open question, not folded into the proof sketch.

---

## 2. Formal Statement of Overlap Consistency

### 2.1 Scope decision for this sketch (stated up front)

This sketch works over a single fixed global state s (one snapshot of S_spec), not over an evolving trace / sequence of transitions. This is a deliberate scope reduction, not an oversight: the instructing memo asks for a sketch, and a single-snapshot statement is the smallest setting in which "do two nodes' overlapping views agree" is already a nontrivial question. A trace-level (time-indexed, inductive) version of this theorem is not attempted and is listed in Section 5 as a new open question. Property P5 (Append-only / monotonicity) is therefore invoked below only as a background assumption about how V_i(s) was constructed, not exercised as an inductive argument over successive states.

### 2.2 Setup (carried over from the predecessor document, Candidate B only)

- E: the global event set; <= (subset of E x E): the global happens-before partial order; e1 -> e2 means e1 <= e2 and e1 != e2; e1 || e2 (concurrent) means neither e1 <= e2 nor e2 <= e1.
- I = {1, ..., n}: a fixed, static set of node indices (Candidate B, per the predecessor document Section 2.3, requires a bounded index set; Section 3.3 below and Section 5 return to what breaks if I is not static).
- VC : E -> N^n: the canonical vector clock function. Each node k in I maintains a running clock; a local event at k increments component k; on receiving/observing an event e' with attached clock VC(e'), a node updates its own running clock to the componentwise max of its current clock and VC(e'), then (if this is itself a new local event) increments its own component. VC(e) is the vector assigned to event e once, at its creation, and is a fixed property of e - not something recomputed differently by different observers.
- E_i (subset of E): the events causally relevant to node i (as in the predecessor document; this document does not define this set precisely either - see Section 5).
- V_i(s): node i's Candidate B causal metadata at state s, i.e. pi_i^causal(s) = (pi_i(s), V_i(s)). Following the standard vector clock construction, V_i(s) = VC(f_i(s)) where f_i(s) is the most recently observed ("frontier") event of E_i as of s. By construction, V_i(s) already dominates (is componentwise >=) VC(e) for every e in E_i observed up to s, because the running-clock update rule folds in every causal predecessor's clock via componentwise max.

### 2.3 Overlap

For nodes i, j in I, define the overlap O_ij = E_i intersect E_j: the events that are causally relevant to both nodes (informally, shared ancestor events - e.g. events that causally precede both node i's and node j's current frontier). This document assumes O_ij is nonempty when discussing "overlap"; the empty case is vacuous and not discussed further.

### 2.4 The Overlap Consistency Proposition (formal statement)

**Proposition (Overlap Consistency under Candidate B).** For any i, j in I with O_ij nonempty, and for any e, e' in O_ij:

```
e -> e'   iff   VC(e) < VC(e')   (strict componentwise dominance)
e || e'   iff   VC(e), VC(e') incomparable under componentwise <=
```

and this equivalence is the same regardless of whether VC(e), VC(e') are read off via node i's record (V_i(s), and the history it summarizes) or via node j's record (V_j(s)). Equivalently: there is no pair e, e' in O_ij about which node i and node j disagree on order-vs-concurrency.

This is the formal content of P3 (Overlap comparability) as applied to Candidate B specifically: it says the comparison operation P3 requires exists, and moreover that the operation gives the same answer no matter which of the two overlapping nodes performs it.

Note precisely what this Proposition does and does not claim. It claims agreement on ordering/concurrency facts about shared events. It does not claim anything about whether node i's local relation R_i and node j's local relation R_j, each separately satisfied, jointly imply the absence of a safety violation spanning E_i union E_j. That stronger claim is what Section 3 attempts and fails to close - it is the actual "Overlap Consistency Theorem" the instructing memo is aiming at, of which the Proposition above is a necessary ingredient, not the whole thing.

---

## 3. Proof Sketch

### 3.1 The theorem this is meant to repair, as characterized (not as canonically verified)

The instructing memo refers to a pre-existing p-DERS theorem, here called Decomposed Trace Safety, in the schematic form:

```
Theorem (Decomposed Trace Safety), as characterized:
  for all i in I: R_i holds on pi_i(s)   implies   s is (globally) safe.
```

As stated in the header of this document, this document has not read a canonical formal statement of this theorem, of R_i, or of "globally safe." Everything in this section that refers to Decomposed Trace Safety uses only the schematic form above, exactly as the instructing memo gives it, and the "known gap" language below is likewise restricted to what the instructing memo characterizes, not an independently verified critique of a proof this document has not seen.

The characterized gap: checking R_i on node i's own local view alone, node by node, does not by itself account for what happens when two nodes' views causally overlap. Concretely (informal illustration, not a formal counterexample since S_i_spec's actual content is unknown to this document): it is conceivable that R_i holds at node i and R_j holds at node j individually, while node i and node j have each built their locally-valid view on top of a shared ancestor event in a way that is only mutually inconsistent when the two views are compared against each other - a violation visible only at the seam between i and j, not inside either node's own local check. This is the generic "local consistency does not imply global consistency" problem familiar from compositional/modular reasoning in distributed systems; it is not specific to p-DERS, and this document does not claim it is.

The question this document's task is to answer: does upgrading pi_i to pi_i^causal (Candidate B) close this gap, partially close it, or leave it open? The answer, developed below, is: it closes exactly the "can the two nodes even compare notes about the overlap" part of the gap (Lemma 1), and leaves the "does comparing notes actually rule out a joint violation" part open (Lemma 2).

### 3.2 Lemma 1 (Clock Agreement on Overlap) - proven

**Lemma 1.** Under the setup of Section 2.2-2.3, with I fixed and static, the Overlap Consistency Proposition (Section 2.4) holds.

Proof. VC : E -> N^n is a function of E alone: it is assigned once, at the creation of each event, by the standard vector-clock update rule (increment-on-local-event, componentwise-max-on-receipt). Nothing in that construction makes VC(e) depend on which node later reads or reports it - V_i(s) and V_j(s) are both computed by folding (via componentwise max, transitively) the VC values of every event either node has observed, and for any event e in O_ij = E_i intersect E_j, VC(e) is by definition the same value whether it entered node i's fold or node j's fold. The standard vector-clock correctness property (sometimes called the strong clock condition: e1 -> e2 if and only if VC(e1) < VC(e2) componentwise, with incomparability corresponding exactly to concurrency) is a property of VC itself, not of any particular observer, and applies unchanged to any pair e, e' in O_ij. Hence node i's and node j's answers to "is e before e', after e', or concurrent with e'" for e, e' in O_ij are both just restatements of the same VC-level fact, so they cannot disagree. QED (modulo the standard vector-clock correctness property being taken as given background theory, not re-derived here; this is a well-established property of the Fidge/Mattern vector clock construction, not a novel claim of this document).

Caveat on Lemma 1's scope (important, see Section 5): the proof above uses "the same N^n" for both V_i(s) and V_j(s) - i.e., it assumes I is a fixed, shared index set known to both nodes throughout. If node membership is dynamic (nodes join or leave, so the index set node i used to build V_i(s) differs from the index set node j used to build V_j(s)), then V_i(s) and V_j(s) may not even be elements of the same space, and "VC(e) < VC(e')" is not well-defined without an explicit reindexing/embedding map between the two index sets. No such map is defined in the predecessor document or here. Lemma 1 as proved above therefore holds only under the static-membership assumption; this is exactly Open Question 4 of the predecessor document, and Section 5 notes that it bears on Lemma 1, not only (as might be assumed) on Lemma 2.

### 3.3 Lemma 2 (Local-to-Global Bridge) - NOT proven

**Attempted Theorem (Overlap Consistency, main claim).** For i, j in I with O_ij nonempty: if R_i holds on pi_i^causal(s) and R_j holds on pi_j^causal(s), then no safety violation exists on E_i union E_j that is invisible to both R_i and R_j individually.

Proof attempt and where it stalls:

By Lemma 1, node i and node j agree on the order/concurrency of every pair of events inside O_ij. So if a joint violation were to exist on E_i union E_j despite R_i and R_j both holding, it could not be a disagreement about ordering within the overlap itself (Lemma 1 rules that out). The remaining way such a violation could exist is a pair of events straddling the overlap - e.g. an event e in O_ij and an event e' in E_i \ E_j (visible to i, not to j) - whose relationship matters for safety but is not something R_i's own check happens to look at, or is not something R_j can see at all because e' is outside E_j.

Closing this case requires knowing:

1. What R_i and R_j actually constrain - i.e. the canonical content of R_i, not just its existence (Open Question 1 of the predecessor document; this document did not gain access to it either). Without this, there is no way to argue that R_i's satisfaction is sensitive to exactly the cross-node information a straddling pair would require.
2. Which compatibility mode, M1 or M2 (predecessor document Section 3.1, property P6), governs R_i's relationship to V_i. Under M1 (forgetful: R_i is applied to U(pi_i^causal(s)) = pi_i(s), discarding the vector clock entirely), R_i by construction never looks at V_i at all - so Lemma 1's agreement guarantee, however solid, is simply irrelevant to what R_i checks, and the bridge argument fails at its very first step, not at some deeper case. Under M2, R_i could in principle be extended to use V_i, but the predecessor document does not fix what that extension is (Open Question 7), so there is nothing concrete here to reason about.
3. An explicit merge or conflict-resolution semantics for concurrent updates (Open Question 5 of the predecessor document). Lemma 1 tells us when two events are concurrent; it does not say what a safety-relevant combination of two concurrent, causally-overlapping updates is supposed to look like. Without this, "no violation on the straddling pair" has no operational meaning to check against - there's no combining rule whose consistency could be verified.
4. A definition of "globally safe" itself, i.e. a canonical (not schematic) statement of what Decomposed Trace Safety's conclusion actually asserts - which, per Section 3.1, this document does not have.

**Lemma 2 (Local-to-Global Bridge) is therefore recorded as unproven.** It is not merely "not yet written out" - the proof attempt above identifies four specific, named prerequisites (R_i's canonical content, the M1/M2 choice, a merge semantics, and a definition of global safety) none of which this document has access to or is in a position to invent. Closing Lemma 2 requires those four items to be supplied from outside this Track A sketch; only then can Lemma 2 be attempted again.

### 3.4 Corollary (degenerate case) - informal, not separately verified in detail

Informally: in the degenerate case with no concurrency at all (a single, totally-ordered writer history, as in P7 of the predecessor document), O_ij's ordering questions all have a definite happens-before answer and no concurrent pairs exist to cause the ambiguity Lemma 2's proof attempt stalls on. In this case the original (pre-causal) Decomposed Trace Safety schema is plausible on its own terms, consistent with pi_i^causal reducing to pi_i (P7). This is stated as an expectation, not a proof: it has not been checked against R_i's actual content (still unavailable), so it should be read as "the one case where the Lemma 2 gap is expected to be vacuous," not as an established result.

### 3.5 Summary: what is closed, what is open

- Closed (Lemma 1): under Candidate B, with static node membership, two nodes whose causal histories overlap cannot disagree about the order or concurrency of the shared events. This is P3 made concrete for Candidate B.
- Open (Lemma 2): whether locally-satisfied R_i and R_j, combined with Lemma 1's agreement, together rule out a jointly-invisible safety violation. Four specific missing prerequisites are named in Section 3.3. This is the actual content the instructing memo's "Overlap Consistency Theorem" is aiming at, and it is not closed by this document.
- Conditionally closed (Corollary, 3.4): plausible in the degenerate no-concurrency case, not verified in detail.

---

## 4. P1-P7 Checklist Verification

Reference: P1-P7 as listed in docs/formal/pDERS_causal_projection_v0.1.md, Section 4.

| Property | Used in this sketch? | How |
|---|---|---|
| P1 (Order faithfulness) | Used | Directly underlies Lemma 1: Candidate B satisfies P1 exactly (per the predecessor document), which is what makes "VC(e) < VC(e') iff e -> e'" available as a premise. |
| P2 (Concurrency non-forcing) | Used | Cited in Section 1 as the structural reason Candidate A was rejected; also implicitly required for the "e \|\| e' iff incomparable" half of the Overlap Consistency Proposition to be a meaningful (non-vacuous) statement rather than an artifact of an imposed tie-break. |
| P3 (Overlap comparability) | Used - this document's central subject | Section 2.4's Proposition and Section 3.2's Lemma 1 together are a concrete verification that Candidate B provides the comparison operation P3 requires, and that it is observer-independent. |
| P4 (Boundedness) | Used, and its limits are load-bearing | Assumed as background (fixed n) throughout Section 2-3; it is also the stated reason Candidate C was deferred in Section 1; and its failure mode (dynamic membership breaking the fixed index set) is flagged in Section 3.2's caveat as threatening Lemma 1 itself, not only Lemma 2. |
| P5 (Append-only / monotonicity) | Invoked, not exercised | Used only as background justification for how V_i(s) is constructed (Section 2.2); this sketch is explicitly single-snapshot (Section 2.1) and does not attempt the inductive, trace-level argument that would actually exercise P5. See Section 5. |
| P6 (Explicit, uniform compatibility mode) | Central to why Lemma 2 stalls | Section 3.3 identifies the M1/M2 choice as one of the four named prerequisites for closing Lemma 2: under M1, R_i is blind to V_i by construction, which breaks the bridge argument immediately regardless of Lemma 1. |
| P7 (Degenerate-case identity) | Used informally | Basis for the Corollary in Section 3.4; not separately proven here, only stated as an expectation consistent with the predecessor document's P7. |

---

## 5. Open Questions

### 5.1 New (discovered while writing this document)

1. Canonical statement of Decomposed Trace Safety. This document worked only from the schematic form given in the instructing memo (Section 3.1). Whether the actual canonical theorem (if it exists as characterized) matches this schema, and what "globally safe" precisely means in it, is unknown and was not available to this document's author. This is a sharper instance of Open Question 1 from the predecessor document, specific to this theorem rather than to R_i/Omega_i/Psi_i generally.

2. Single-snapshot vs. trace-level scope. This sketch deliberately restricts to one fixed state s (Section 2.1) rather than an evolving trace. Whether "Overlap Consistency" as intended by the instructing memo is meant to be a single-snapshot property or an inductive, time-indexed one (in which case P5 would need to be exercised, not just invoked) is not addressed here and is left for a follow-up instruction to specify.

3. Lemma 1's dependency on static membership. Section 3.2 shows that dynamic node membership (Open Question 4, inherited, see 5.2 below) threatens Lemma 1 - the "easy," already-proven half of this sketch - and not only Lemma 2 as might be assumed from the ordering of the sections in this document. This reframes the severity of Open Question 4: it is not solely a Lemma-2-side concern.

4. No embedding/reindexing map for differing index sets. Concretely growing out of item 3: if dynamic membership is ever to be supported, some explicit map relating a vector clock built under index set I to one built under a different index set I' would be needed for Lemma 1 to be restated. No such map is proposed anywhere in this document or the predecessor document.

### 5.2 Inherited from the predecessor document (still unresolved, and how they bite here specifically)

- Open Question 1 (canonical source gap for R_i/Omega_i/Psi_i/S_i_spec). Bites here as the single largest reason Lemma 2 cannot be attempted further (Section 3.3, prerequisite 1).
- Open Question 4 (dynamic node membership / vector clock dimension). Bites here against Lemma 1 directly (Section 3.2 caveat), not only against Lemma 2 as one might have expected before this document was written.
- Open Question 5 (merge/conflict-resolution policy location for concurrent updates). Bites here as prerequisite 3 of Lemma 2's proof attempt (Section 3.3): Lemma 1 detects concurrency but supplies no combining rule to check safety against.
- Open Question 7 (M1 vs. M2 compatibility mode). Bites here as prerequisite 2 of Lemma 2's proof attempt (Section 3.3): under M1, the entire bridge argument is moot regardless of anything else, since R_i never observes V_i.
- Open Question 2 (which candidate) is resolved for the purposes of this document only, by the Human Gate decision recorded in Section 1; it is not resolved as a general matter for any future document that might revisit Candidate C once a horizon policy exists.

Nothing in Section 5.1 or 5.2 is answered by this document; both lists are handed forward as-is.

---

## 6. Next Step (out of scope for this document)

Closing Lemma 2 - and with it, an actual Overlap Consistency Theorem rather than a sketch - requires the four prerequisites named in Section 3.3 to be supplied from outside this Track A process (most plausibly: the canonical R_i/Omega_i/Psi_i source, a Human Gate ruling on M1 vs. M2, and a merge-semantics decision for concurrent updates). This document does not attempt to supply any of them. Any follow-up instruction that wants Lemma 2 attempted again should first resolve at least one of the four.

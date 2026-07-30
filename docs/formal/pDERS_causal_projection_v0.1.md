# p-DERS Causal Projection pi_i^causal - Formal Definition v0.1

Document ID: PDERS_CAUSAL_PROJECTION_v0.1
Version: 0.1 (Draft)
Status: DECISION_RECORDED pending - awaiting Human Gate selection
Track: Track A (Formal Theory Track, p-DERS)
Independence note: this document is independent of Track B (MoCKA Write Path v1.0 / DC-WP). Nothing in this document is wired into, or intended to be wired into, any MoCKA implementation, the Decision Ledger, or any MCP write path. Read only research artifact.
Author: Claude Code (S02, "kuroko"), instructed by Claude (R02)
Reviewer: Human Gate (kimura hakase) - selection pending

---

## 0. Scope and a disclosed limitation

Before the formal content: a repository-wide search of this codebase (MoCKA, m-sirius-k/mocka) turned up no committed formal source for pi_i, R_i, Omega_i, or Psi_i. The only in-repo trace of the p-DERS formal core is the summary line

```
Formal Core: S_DTS = (E, P, V)
```

in docs/ai/notebooklm.md, and the paper title/DOI references in MOCKA_OVERVIEW.json (p-DERS, Zenodo DOI 10.5281/zenodo.20686662). The actual definitions of pi_i, R_i, Omega_i, Psi_i, and S_i_spec most likely live in the AAAI2027 paper draft or the author's external working notes, neither of which is present in this git repository.

Consequence for this document: everything below that references R_i, Omega_i, Psi_i, S_spec, or S_i_spec is built strictly from the characterization given in the instructing memo (Section 1 of that memo, reproduced in Section 1 below), not from a canonical source this document's author was able to read. Where the memo's characterization is underspecified, this is stated explicitly as an open question in Section 5 rather than filled in by assumption. This limitation is repeated in Section 5 so it is not lost if this document is read out of order.

---

## 1. Motivation

### 1.1 Current definition (as given)

The current p-DERS local projection is stated as a plain coordinate projection:

```
pi_i : S_spec -> S_i_spec
```

i.e. a function that takes the global specification state and returns node i's local component of it, with no additional structure attached.

### 1.2 Audit finding (as given)

The audit finding motivating this work is that this definition:

- carries no mechanism for preserving causal ordering (happens-before) between the events that produced S_spec, and
- carries no mechanism for representing concurrent (unordered, potentially conflicting) transitions among nodes,

and that this loss of structure, rather than being a harmless simplification, is itself a risk: the information compression performed by pi_i widens the attack surface.

### 1.3 Why coordinate-only projection widens the attack surface (restated precisely)

Two distinct failure modes follow directly from pi_i having no causal structure in its codomain:

1. Order-loss: if event e1 causally precedes event e2 (e1 -> e2 in the happens-before sense) and both affect node i's local coordinate, a consumer of S_i_spec = pi_i(S_spec) cannot distinguish "e1 then e2" from "e2 then e1" from "e1 and e2 concurrent". Any downstream logic that assumes freshness, sequencing, or non-replay (e.g. a consumer checking "this is the latest value") has nothing in pi_i's output to check against. A replayed or reordered event stream that reconstructs the same final coordinate value is indistinguishable from a legitimate one.

2. Concurrency-collapse: when multiple nodes j concurrently produce transitions that are visible at node i, a scalar/tuple coordinate projection collapses all of them into one final value with no record of which subset of writes were genuinely concurrent (no causal relationship) versus causally dependent (one built on the other). This is exactly the "information compression" the audit flags: the compression is not merely lossy in a neutral sense, it specifically discards the evidence needed to tell a legitimate concurrent update apart from an injected, causally-fabricated one.

Both failure modes point at the same requirement: pi_i^causal must have a codomain that is at least as expressive as "coordinate value + enough causal metadata to answer order and concurrency questions about the events that produced it."

---

## 2. Formal Definition of pi_i^causal

### 2.1 Common setup

Let E be the global event set (consistent with the S_DTS = (E, P, V) formal core referenced in docs/ai/notebooklm.md; this document does not know the internal structure of P or V and does not depend on it beyond E being the event universe). Assume a global happens-before relation

```
<= (subset of E x E)
```

that is a partial order (reflexive, antisymmetric, transitive), not necessarily total. Write e1 -> e2 for "e1 <= e2 and e1 != e2" (strict causal precedence). Two events e1, e2 are concurrent, written e1 || e2, iff neither e1 <= e2 nor e2 <= e1.

For node i, let E_i (subset of E) be the set of events causally relevant to node i (informally: events whose effect is, directly or transitively, visible in S_i_spec). This document does not fix how E_i is computed; Candidates A-C below make different implicit assumptions about E_i's shape, and the precise definition of "causally relevant" is left as an open question (Section 5).

A causal projection is a function

```
pi_i^causal : S_spec -> S_i_spec^causal
```

where S_i_spec^causal extends S_i_spec with causal metadata. The three candidates below differ in what that metadata is, and consequently in what happens-before questions can be answered from pi_i^causal(s) alone.

For each candidate, this section states (a) the definition, (b) the answer to the memo's explicit question of whether concurrent transitions are forced into an order or left partially unordered, (c) properties, and (d) tradeoffs. No candidate is recommended over another; selection is Human Gate's decision (Section 6 of the instructing memo).

### 2.2 Candidate A - Lamport scalar clock projection

Definition:

```
pi_i^causal(s) = ( pi_i(s), L_i )
```

where L_i is a Lamport logical clock value: an integer assigned to the event that most recently updated node i's coordinate, incremented on each local event and updated to max(local, received) + 1 on receipt of a causally-prior event from elsewhere, per the standard Lamport clock rule.

Concurrency handling: forced into a total order. Lamport clocks guarantee e1 -> e2 implies L(e1) < L(e2), but not the converse: L(e1) < L(e2) does not imply e1 -> e2. When e1 || e2, the clock (plus a deterministic tie-break, typically node id) still produces a total order between them. Candidate A therefore answers the memo's ordering-vs-concurrency question by choosing to linearize: genuinely concurrent transitions are assigned an arbitrary but deterministic order, and that order is indistinguishable, from the outside, from true causal order.

Properties:
- O(1) metadata per state (a single integer).
- Cheap to compute and to compare (integer comparison).
- Sound in one direction only: L(e1) < L(e2) is necessary but not sufficient for e1 -> e2.

Tradeoffs:
- Reintroduces a version of the original problem at a smaller scale: because concurrent events are linearized indistinguishably from causally-ordered ones, a consumer of pi_i^causal(s) still cannot tell "these two writes were independent" from "this write causally depended on that one." This directly undercuts requirement 2 of the instructing memo (explicit handling of concurrent transitions) unless the total order Candidate A produces is documented as an arbitrary tie-break, not a causal claim.
- Cheapest candidate to implement and to reason about computationally.

### 2.3 Candidate B - Vector clock projection

Definition:

```
pi_i^causal(s) = ( pi_i(s), V_i )
```

where V_i is a vector clock: a vector indexed by (a bounded set of) nodes, such that for events e1, e2 with vectors V(e1), V(e2):

```
e1 -> e2   iff   V(e1) <= V(e2) componentwise and V(e1) != V(e2)
e1 || e2   iff   neither V(e1) <= V(e2) nor V(e2) <= V(e1)
```

Concurrency handling: partial order preserved. Genuinely concurrent events remain formally incomparable under Candidate B; pi_i^causal(s) can truthfully report "these two updates are concurrent" rather than being forced to pick an order. This directly satisfies requirement 2 of the instructing memo (explicit, non-forced treatment of concurrency) in a way Candidate A does not.

Properties:
- Exact reconstruction of the happens-before/concurrent relation restricted to the events reflected in V_i (no false ordering, no false concurrency).
- O(n) metadata per state, where n is the size of the index set (nodes considered causally relevant to i).

Tradeoffs:
- Vector dimension n must be fixed or bounded; under dynamic node membership (nodes joining/leaving), maintaining a correct, bounded vector clock is a known hard problem (see e.g. dynamic/interval-tree clocks in the distributed systems literature) and is not resolved by this document (Section 5).
- Preserving "these are concurrent" is not the same as resolving what to do about it: Candidate B tells node i that two updates conflict/are unordered, but does not itself specify a merge or conflict-resolution policy. Whether such a policy belongs inside pi_i^causal or in a separate layer is left open (Section 5).
- More metadata and more implementation complexity than Candidate A.

### 2.4 Candidate C - Explicit happens-before graph (causal slice / causal cone) projection

Definition:

```
pi_i^causal(s) = ( pi_i(s), G_i )
```

where G_i = (E_i, <=_i) is the local causal slice: the sub-DAG of the global happens-before relation restricted to E_i (the events causally relevant to node i), retaining explicit edges (which specific prior event(s) each event depends on), not merely a per-event summary value.

Concurrency handling: partial order preserved, and represented explicitly rather than via a comparison-only encoding. Where Candidate B lets a consumer test whether two events are ordered or concurrent, Candidate C additionally exposes the dependency structure itself (which event depends on which), so a consumer can, for example, ask "what is the full causal history behind this specific update" rather than only "are these two updates ordered."

Properties:
- Strictly the most expressive of the three: G_i determines the answer Candidate A and Candidate B would each give, but not vice versa (a scalar or a vector clock cannot in general be replayed back into the full dependency graph that produced it).
- Directly addresses the audit's "information compression widens the attack surface" concern at its root: under Candidate C, pi_i is no longer compressing the causal structure at all, only slicing it down to the events relevant to node i. Nothing about ordering or concurrency among those events is discarded.
- Supports audit/replay use cases (reconstructing exactly why a given local state has the value it has) that Candidates A and B cannot support directly.

Tradeoffs:
- Highest metadata cost, and metadata cost that is not obviously bounded: E_i can grow without limit unless some horizon or garbage-collection policy prunes it. This document does not define such a policy (Section 5).
- "Causally relevant to node i" needs a precise, decidable definition for E_i to be well-defined and computable; the instructing memo does not supply one, and this document does not invent one (Section 5).
- Heaviest implementation and storage burden of the three candidates.

### 2.5 Summary comparison

| Property | Candidate A (Lamport) | Candidate B (Vector clock) | Candidate C (Causal slice) |
|---|---|---|---|
| Metadata size | O(1) | O(n), n = relevant nodes | O(\|E_i\|), unbounded absent a horizon policy |
| Concurrent transitions | forced into total order (arbitrary tie-break) | left explicitly unordered (comparable/incomparable) | left explicitly unordered, with full dependency structure exposed |
| Detects true concurrency | no | yes | yes |
| Reconstructs full dependency chain | no | no | yes |
| Requires bounded/known node set | no | yes (for vector dimension) | yes (for E_i to terminate) |
| Addresses audit's compression concern | partially (smaller compression, same kind of loss) | mostly (no false order, but per-event summary only) | most directly (structure itself is preserved, not summarized) |

This table restates, rather than resolves, the tradeoffs in 2.2-2.4; no ranking or recommendation is intended by its ordering.

---

## 3. Compatibility with R_i / Omega_i / Psi_i

As stated in Section 0, this document works only from the memo's characterization of R_i (an existing local relation) and Omega_i / Psi_i (existing local invariant conditions), not from a canonical formal source located in this repository. The analysis below is therefore domain-level (about what changes in signature/domain, not about the internal content of R_i, Omega_i, Psi_i, which this document does not have access to).

### 3.1 The domain-impact question

Under the current definition, R_i, Omega_i, Psi_i are presumed to be defined over (or in terms of) S_i_spec, the codomain of pi_i. Replacing pi_i with pi_i^causal changes that codomain to S_i_spec^causal = S_i_spec plus causal metadata (Candidate-dependent: an integer, a vector, or a graph). Anything downstream that consumed pi_i's output now faces a codomain it was not defined against.

Two compatibility modes follow, and this document presents both without choosing between them, consistent with the instructing memo's requirement not to converge prematurely:

Mode M1 - forgetful compatibility. Define a forgetful map

```
U : S_i_spec^causal -> S_i_spec
U( (v, meta) ) = v
```

that discards the causal metadata, and require R_i, Omega_i, Psi_i to be applied as R_i(U(x), U(y)), Omega_i(U(x)), Psi_i(U(x)). Under M1, R_i / Omega_i / Psi_i are literally unchanged; only a projection step (U) is inserted before they are evaluated. This is the minimal-disruption option: it requires no change to R_i / Omega_i / Psi_i themselves, at the cost of those relations/invariants remaining blind to causal information (they cannot themselves detect an order violation or a suspicious concurrency pattern; only components upstream of them, reading S_i_spec^causal directly, could).

Mode M2 - causal-aware extension. Extend R_i, Omega_i, Psi_i themselves to be defined over S_i_spec^causal, e.g. a causal-aware R_i^causal that additionally requires the causal metadata of its arguments to be consistent with <= (for instance, refusing to relate x to y if y's recorded causal metadata claims to precede x's). Under M2, R_i / Omega_i / Psi_i's definitions themselves must be revisited and re-stated over the richer domain; this is a strictly larger change than M1, but is the only mode under which R_i / Omega_i / Psi_i can participate in enforcing the ordering/concurrency guarantees Section 2 discusses.

### 3.2 Interaction with the choice of Candidate (2.2-2.4)

- Under Candidate A, M2 extension is limited by what Candidate A's metadata can support: since Candidate A cannot itself distinguish true concurrency from an imposed tie-break, an M2 extension of R_i/Omega_i/Psi_i built on Candidate A inherits that blindness.
- Under Candidate B or C, M2 extension can meaningfully condition on genuine concurrency (e.g. Psi_i could be extended to require that concurrent updates satisfy some join/merge property), which is not possible under Candidate A.
- Under any Candidate, M1 is available as a strictly safe fallback that changes nothing about R_i / Omega_i / Psi_i's existing guarantees; it only adds a discard step.

### 3.3 What this document does not determine

This document does not determine: (a) whether R_i / Omega_i / Psi_i in their canonical (out-of-repo) form are stated in a way that is even compatible with a forgetful map U (i.e. whether M1 is actually available without further changes), or (b) which of M1 / M2 is preferable. Both require reading the canonical source referenced in Section 0, which was not available to this document's author, and both are Human Gate decisions in any case.

---

## 4. Required Properties for Overlap Consistency

The instructing memo asks for a list of properties this definition should satisfy as a precondition for the next-stage Overlap Consistency Theorem, properties only, no proof attempted here.

- P1 (Order faithfulness). If e1 -> e2 (global happens-before) and both events are reflected in node i's causal metadata, pi_i^causal must not report an order inconsistent with e1 -> e2. (Candidate A satisfies this one-directionally; Candidates B and C satisfy it exactly.)
- P2 (Concurrency non-forcing, where claimed). For any Candidate that claims to preserve concurrency (B, C), genuinely concurrent events must not be reported as ordered. For Candidate A, this property does not hold by construction and any Overlap Consistency argument built on Candidate A must not assume it.
- P3 (Overlap comparability). For any two nodes i, j whose causally-relevant event sets E_i, E_j overlap (share ancestor events), the causal metadata each node records for the shared events must be comparable via a well-defined operation, so that Overlap Consistency has something to compare pi_i^causal(s) against pi_j^causal(s) on the intersection. Without this, "overlap consistency" has no operational meaning.
- P4 (Boundedness). The causal metadata attached by pi_i^causal must be finitely representable, and, ideally, boundable in terms of a stated parameter (e.g. number of causally relevant nodes for Candidate B, or an explicit horizon for Candidate C), so that a proof of Overlap Consistency does not have to reason about unbounded structures without a stated bound.
- P5 (Append-only / monotonicity under composition). Applying pi_i^causal after further global transitions must only extend previously recorded causal metadata, never retract or mutate it. (This mirrors the MoCKA constitution principle "Event ledger is append only" referenced at the repository level in MOCKA_OVERVIEW.json; it is listed here as a property this specific projection should satisfy, not as an appeal to that document's authority over this independent theory track.)
- P6 (Explicit, uniform compatibility mode). Whichever of M1 / M2 (Section 3.1) is adopted, it must be adopted uniformly across all nodes; a proof of Overlap Consistency cannot mix a node reasoning under M1 with a node reasoning under M2.
- P7 (Degenerate-case identity). When node i's causally relevant history is totally ordered with a single writer (no concurrency ever occurs), pi_i^causal must be observationally equivalent to the original pi_i (recoverable by applying U from Section 3.1). This is a backward-compatibility requirement: the causal upgrade must not change behavior in the case that motivated no upgrade at all.

This list is a precondition list, not a completeness claim: Overlap Consistency's actual proof may need additional properties not anticipated here. Human Gate / whoever drafts the Overlap Consistency sketch should treat P1-P7 as a starting checklist, not a closed set.

---

## 5. Open Questions

Recorded as unresolved; none of these are answered by this document, and none should be inferred as answered.

1. Canonical source gap. This document could not locate a committed formal definition of R_i, Omega_i, Psi_i, or S_i_spec anywhere in this repository (see Section 0). All of Section 3's analysis is therefore domain-level and provisional pending review against the canonical source (most likely the AAAI2027 paper draft, not present in this repo). It is unknown whether that canonical source already assumes a codomain shape incompatible with one or more of the three candidates in Section 2.

2. Which candidate. Section 2 presents three candidates without recommendation, per the instructing memo's explicit prohibition on premature convergence. Which of A / B / C (or a hybrid not detailed here) is adopted is a Human Gate decision.

3. Definition of E_i ("causally relevant to node i"). Candidates B and C both depend on a precise, decidable notion of which events belong to E_i. This document uses the term informally (Section 2.1) and does not define it. Left open.

4. Node membership model. Candidate B's vector clock dimension and Candidate C's E_i both implicitly assume some notion of the participant node set. Whether that set is static (fixed at system design time) or dynamic (nodes join/leave at runtime) is not addressed by the instructing memo and is not resolved here; this materially affects which candidate is even implementable as stated.

5. Conflict/merge policy scope. Candidates B and C can detect that two updates are concurrent, but detecting concurrency is not the same as resolving what a node should do when it observes it (e.g. last-writer-wins, application-level merge, reject-and-flag). Whether such a policy is in scope for pi_i^causal itself, or belongs to a separate layer that consumes pi_i^causal's output, is unresolved.

6. History horizon / pruning for Candidate C. G_i in Candidate C can grow without bound absent a garbage-collection or horizon policy. No such policy is proposed here; whether one is needed, and what it should be, is open.

7. M1 vs M2 (Section 3.1). Whether R_i / Omega_i / Psi_i should remain untouched behind a forgetful map (M1) or be extended to be causal-aware (M2) is explicitly left as a Human Gate choice, contingent also on question 1 above (what the canonical R_i / Omega_i / Psi_i actually look like).

8. Relationship to Track B. This document's Independence note (top of file) states no connection to Track B (MoCKA Write Path v1.0). Whether the eventual Overlap Consistency work, once it exists, should ever inform or be informed by Track B's event-ordering mechanisms (e.g. the append-only events_v2 schema in docs/mocka3/EVENT_FOUNDATION_v1.md, which independently deals with event provenance and ordering at the implementation level) is not addressed and not assumed either way.

---

## 6. Next Step (out of scope for this document)

Per the instructing memo, once Human Gate selects a definition (or requests a hybrid, or requests revision), the Overlap Consistency Theorem sketch is drafted as a separate, later-issued instruction. This document does not attempt that sketch.

# Reference: p-DERS Main Paper (Transcribed Full Text)

Document ID: PDERS_MAIN_REFERENCE_v1
Purpose: canonical reference copy of the p-DERS paper's text, for citation by Track A formal documents (`docs/formal/*.md`). This is a supporting reference artifact, not itself a Track A analysis document.
Source: "Projective Dual-Execution Refinement Systems (p-DERS): Formally Enforcing Safety Governance in Asynchronous Multi-Agent Orchestration" (Anonymous submission). Zenodo DOI 10.5281/zenodo.20686662.

## Provenance and reliability caveats (read before citing)

- This file was **not** produced by this session (kuroko / S02) reading the PDF directly. Kuroko's session cannot access the PDF (it was uploaded in a separate Claude web / R02 session). This text is a **transcription performed by Claude (R02)** from the PDF kimura hakase (Human Gate) uploaded there, relayed into this session as Appendix A of the instructing memo, and copied here verbatim.
- This is therefore a **second-hand transcription**, not a direct machine-read of the source file. OCR/transcription error risk is not zero, particularly for: mathematical symbols and subscripts (e.g. `⊑Ri`, `≈i`, `S^ij`, `S^i_eff`), numbered cross-references, and the two figure descriptions (Figure 1, Figure 2), which R02's transcription explicitly presents as *descriptions* of the figures rather than literal caption text extracted from the PDF.
- Per the instructing memo (`0d0e8def-KUROKO_INSTRUCTIONS_pDERS_overlap_consistency_v0.2_revision.md`, Section 3): where this session found a spot plausibly affected by transcription error, it is flagged below as "transcription-doubtful" rather than silently corrected or silently trusted. See "Transcription-doubtful spots" at the end of this file.
- This file preserves the mathematical notation exactly as transcribed (∈, ⊆, ⟺, ≈, ⊑, ∀, ∃, ∩, →, etc.) rather than converting it to ASCII, because the point of this file is faithful quotation of a specific source; Track A's own analysis documents (which are original writing, not quotation) continue to use plain ASCII spellings (`Omega_i`, `Psi_i`, `R_i`, `pi_i`) as established in `pDERS_causal_projection_v0.1.md` and `pDERS_overlap_consistency_v0.1.md`.
- No content below has been edited, summarized, or reordered relative to what the instructing memo's Appendix A provided, other than adding this provenance header and the "Transcription-doubtful spots" section at the end.

---

## Title

Projective Dual-Execution Refinement Systems (p-DERS): Formally Enforcing Safety Governance in Asynchronous Multi-Agent Orchestration
(Anonymous submission)

## Abstract

Autonomous multi-agent systems present a fundamental governance challenge: execution sequences that are locally valid at every participating node may collectively violate global safety objectives when composed across asynchronous communication channels. We present the Projective Dual-Execution Refinement System (p-DERS), a decentralized formal verification framework that addresses this challenge by modeling safety governance as the preservation of execution geometry across distributed agent networks. Rather than maintaining an uncomputable monolithic simulation relation, p-DERS decomposes refinement into localized projection spaces governed by projection functions πi, local simulation relations Ri, and dual-layer invariants Ωi and Ψi. Safety is verified at each node independently using only its observable projection of the global specification. To accommodate asynchronous execution, p-DERS replaces global bisimulation with trace inclusion under observation equivalence, preserving both Control-Flow Integrity (CFI) and Information-Flow Control (IFC) without requiring globally synchronized state transitions. We establish soundness under adversarial asynchronous execution and present a reference runtime architecture that separates real-time invariant enforcement from asynchronous cryptographic accountability. Together, these contributions provide a unified mathematical foundation for formally verified safety governance that scales with autonomous agent ecosystems without requiring global synchronization.

## Introduction

Autonomous AI systems are rapidly evolving from isolated inference engines into collaborative computational ecosystems composed of multiple interacting agents. Modern deployments increasingly distribute reasoning, planning, tool execution, memory management, and coordination across specialized agents that communicate through asynchronous messaging infrastructures. While this architectural shift improves scalability and modularity, it fundamentally changes the security properties that must be enforced.

Traditional security mechanisms primarily regulate who may access a resource. In contrast, multi-agent orchestration requires reasoning about how independently valid execution steps compose into global execution trajectories. An execution sequence that is locally valid at every participating node may nevertheless produce an unsafe global state when combined with concurrent actions occurring elsewhere in the distributed system.

This mismatch exposes a structural limitation shared by conventional access-control mechanisms, runtime authorization policies, and identity-centric governance models. These approaches evaluate permissions on individual operations but do not constrain the evolving geometry of distributed execution itself. Consequently, attackers need not exploit software vulnerabilities or bypass authentication mechanisms; they may compose semantically legitimate transitions into execution paths that violate safety constraints while remaining individually compliant with local authorization policies.

Formal verification offers an attractive alternative because safety properties can be expressed as invariants over execution systems rather than permissions over individual resources. However, existing refinement-based verification techniques typically assume a globally observable transition system in which a single simulation relation can be maintained between implementation and specification. Such assumptions rarely hold in practical multi-agent deployments, where execution is distributed across independently scheduled nodes with incomplete knowledge of the overall system state.

This paper addresses this gap through the Projective Dual-Execution Refinement System (p-DERS). Rather than attempting to reconstruct an instantaneous global execution state, p-DERS decomposes verification into localized projection spaces. Every execution node verifies only the portion of the specification observable within its operational scope, while maintaining formal consistency with the global governance model through projection-preserving refinement.

The primary contributions of this paper are:
1. A projection-based refinement framework that replaces monolithic global simulation with decentralized local simulation relations.
2. A formal projection consistency model establishing sufficient conditions for sound decentralized verification.
3. A trace-based verification framework using observation equivalence instead of global bisimulation, making formal governance compatible with asynchronous execution.
4. A dual-frame invariant architecture separating node-state safety from transition-level information-flow governance.
5. A reference runtime architecture demonstrating how formal verification can be integrated into high-throughput multi-agent runtime systems while minimizing execution overhead.

## Multi-Agent Threat Landscape

### Motivation

The security assumptions underlying conventional distributed software systems become increasingly inadequate as autonomous AI agents acquire greater decision-making capabilities and operate with higher degrees of independence. Unlike traditional service-oriented architectures, multi-agent ecosystems continuously generate new execution paths through autonomous planning, tool invocation, delegated reasoning, and dynamic inter-agent communication.

In these environments, the primary attack surface shifts from resource access toward execution composition. Individual actions may satisfy every local authorization policy while their combined effect violates global safety objectives. Consequently, the correctness of the overall orchestration cannot be inferred from the correctness of isolated execution steps.

### System Model

We consider a distributed multi-agent system consisting of a finite collection of autonomous execution nodes N = {1, . . . , n}, where each node maintains its own local execution state and communicates asynchronously with neighboring nodes through message-passing channels.

Each node executes independently under local scheduling without assuming globally synchronized clocks, instantaneous message delivery, deterministic execution ordering, or complete visibility of remote states. Instead, every participant observes only a partial projection of the overall execution system.

### Adversarial Model

We assume an adversary A capable of interacting with the system using only syntactically valid operations. Rather than exploiting undefined behavior or malformed inputs, the adversary constructs harmful execution trajectories through legal compositions of individually valid transitions. The adversary possesses the following capabilities.

**C1. Partial Observability Exploitation.** No execution node possesses complete knowledge of the global execution graph. The adversary exploits inconsistent local observations by scheduling transitions whose individual legality differs from their collective global consequence.

**C2. Causal Reordering.** Because communication is asynchronous, messages may arrive in different orders across different nodes. An adversary may intentionally exploit network latency to construct alternative causal histories.

**C3. Semantic Composition.** The adversary is permitted to compose arbitrary sequences of valid transitions l1, l2, . . . , lk, provided every individual transition satisfies the local execution interface. Unsafe behavior emerges from the composition of individually valid execution decisions rather than from malformed inputs.

**C4. Autonomous Behavioral Drift.** Autonomous agents may gradually diverge from intended operational behavior through imperfect planning, stale contextual information, or hallucinated intermediate reasoning. p-DERS treats accidental behavioral divergence and malicious manipulation using the same formal verification framework.

### Security Objective

The objective of p-DERS is not to prevent agents from executing valid operations. Instead, the framework guarantees that every admissible execution remains structurally consistent with a formally verified safety specification. Every accepted local transition must simultaneously: (1) conform to the projected specification observable by the executing node; (2) preserve all required node-level safety invariants; and (3) preserve all transition-level information-flow invariants.

## Mathematical Foundations

### Global Specification

Let Sspec denote the abstract state space describing all admissible behaviors of the system. The specification transition relation is defined as

δspec ⊆ Sspec × L × Sspec,

where L is the finite alphabet of execution labels. The pair (Sspec, δspec) constitutes the authoritative governance model against which every execution is verified.

### Distributed Execution Model

Each node i ∈ N maintains an independent physical execution state S^i_eff together with its own local transition relation δ^i_eff ⊆ S^i_eff × L × S^i_eff. No assumption is made that local state spaces can be merged into a single globally observable implementation state.

### Projection Spaces

Each node is assigned a projection function πi: Sspec → S^i_spec, where S^i_spec denotes the projected specification visible to node i. Figure 1 illustrates how local projections collectively preserve global safety without requiring any node to hold a complete view of the global state space.

### Projective Dual-Execution Model

The complete p-DERS model is defined by the tuple:

M_p-DERS = ( {S^i_eff}i∈N , Sspec, L, {δ^i_eff}i∈N , δspec, {πi}i∈N , {Ωi}i∈N , {Ψi}i∈N ).

### Local Simulation Relations

p-DERS replaces the global simulation relation with a family of localized refinement relations Ri ⊆ S^i_eff × S^i_spec. The local refinement requirement is:

∀i ∈ N, δ^i_eff ⊑Ri πi(δspec).

**[Figure 1 description, as transcribed by R02 - not literal caption text]:** "Why local projections suffice." Each node holds only a partial view of the global state space S. Three nodes i, j, k each have a partial view Si, Sj, Sk with πi(s), πj(s), πk(s) checked (visible), while the rest is hidden/crossed out. Trace inclusion under observation equivalence: Ti ⊆ Tspec ∧ Tj ⊆ Tspec ∧ Tk ⊆ Tspec. Cryptographic composition: H(Ti) ‖ H(Tj) ‖ H(Tk) → global safety proof. Caption: "Trace inclusion under observation equivalence propagates local safety guarantees globally without requiring a shared simulation relation R." Footer note: "Global R is uncomputable in async distributed settings — local πi projections are sufficient and affordable."

### Local Refinement Rule

A transition s^i_eff --l--> s'^i_eff is admissible if and only if there exist projected specification states s^i_spec, s'^i_spec such that:

(s^i_eff, s^i_spec) ∈ Ri, s^i_spec --l-->_{πi(δspec)} s'^i_spec, (s'^i_eff, s'^i_spec) ∈ Ri.

### Formal Assumptions and Projection Consistency

**Assumption 1 (Projection Homomorphism).** For every i ∈ N, whenever (s, l, s') ∈ δspec, (πi(s), l, πi(s')) ∈ πi(δspec) whenever both projected states are defined.

**Assumption 2 (Monotonic Refinement).** For any S1 ⊆ S2, πi(S1) ⊆ πi(S2).

**Assumption 3 (Observation Consistency).** σ1 ≈i σ2 ⇐⇒ obsi(σ1) = obsi(σ2).

**Assumption 4 (Projection Consistency).** Let S^ij = πi(Sspec) ∩ πj(Sspec). For every transition within S^ij, Ωi = Ωj and Ψi = Ψj over the shared domain.

**Lemma 1 (Projection Preservation).** Assume Assumptions 1–4. If δ^i_eff ⊑Ri πi(δspec), then every locally admissible transition preserves the refinement ordering induced by the global specification.

*Proof Sketch.* Assumption 1 preserves transition semantics under projection. Assumption 2 ensures specification strengthening cannot enlarge the admissible execution space. Assumption 3 guarantees verification operates over locally available information. Assumption 4 prevents incompatible invariant evaluations across overlapping regions. □

## Trace Inclusion and Dual-Frame Invariants

### Trace Inclusion under Observation Equivalence

Let T(δ^i_eff) denote the set of all finite execution traces generated at node i. The system guarantees global alignment safety if:

∀i ∈ N, ∀σ^i_eff ∈ T(δ^i_eff), ∃σspec ∈ T(δspec) s.t. σ^i_eff ≈i πi(σspec).

This condition is intentionally weaker than bisimulation, permitting asynchronous scheduling without invalidating verification.

### Dual-Frame Safety Model

**Definition 1 (Node Safety Invariant).** Ωi : S^i_eff → {0, 1} evaluates whether the current state satisfies all locally enforceable safety constraints. A state is admissible whenever Ωi(s) = 1.

**Definition 2 (Transition Safety Invariant).** Ψi : S^i_eff × L × S^i_eff → {0, 1} evaluates behavioral changes across a transition edge. A transition is admissible only when Ψi(s, l, s') = 1.

### Local Invariant Gate

Every proposed transition is evaluated before local state mutation. A transition is accepted if and only if:

Accept(s, l, s') ⇐⇒ Ri ∧ Ωi(s') = 1 ∧ Ψi(s, l, s') = 1.

## Soundness and Invariant Preservation

**Lemma 2 (Local Invariant Preservation).** Let s --l--> s' be accepted at node i. If Ωi(s) = 1 and Ψi(s, l, s') = 1, then Ωi(s') = 1.

*Proof Sketch.* Acceptance requires successful evaluation of both invariant predicates before state modification, guaranteeing the destination state satisfies the node invariant. □

**Lemma 3 (Trace Preservation).** Every accepted trace σ^i_eff satisfies σ^i_eff ≈i πi(σspec) for some σspec ∈ T(δspec).

*Proof Sketch.* By induction over trace length, each accepted step corresponds to a valid projected specification transition. □

**Theorem 4 (Decentralized Safety Preservation).** Assume Assumptions 1–4, local refinement for all nodes, and an independently verified global specification. For every accepted trace σ^i_eff,

∃ σspec ∈ T(δspec) s.t. σ^i_eff ≈i πi(σspec),

and Ωi(sk) = 1 for every state sk in the accepted trace.

*Proof.* By induction on trace length. Base case: The initial state satisfies local refinement by construction. Inductive step: An accepted transition sk --l--> sk+1 satisfies refinement, Ωi, and Ψi by the Local Invariant Gate. By Lemma 2, Ωi(sk+1) = 1. By the local refinement rule, a corresponding projected specification transition exists, so the extended trace remains observation-equivalent to a projected specification trace. □

**Corollary 5 (Adversarial Robustness).** An adversary GA generating syntactically valid but specification-violating transitions cannot extend the accepted execution history: every such transition is rejected by the Local Invariant Gate before state mutation occurs.

## Reference Runtime Architecture

### Architectural Overview

Only the Local Invariant Gate participates directly in runtime execution (Figure 2). All remaining components execute asynchronously and do not delay ordinary agent computation.

**[Figure 2 description, as transcribed by R02 - not literal caption text]:** p-DERS node architecture flow diagram. "Agent request" (syntactically valid transition, goal: advance local execution state) flows into "Local Invariant Gate" (① πi ② Ri ③ Ωi ④ Ψi — all checked before execution, synchronous). Reject path → "Dropped" (no state mutation). Accept path (runtime execution path) → "Local Execution Engine" → "Trace Recorder" (append-only, vector clocks) → async → "Cryptographic Proof Log" (H(s ‖ l ‖ s' ‖ Proof(πi))) → "Async Drift Compensator" (trace inclusion, rollback). Caption: "Only the Local Invariant Gate is synchronous. All downstream components execute asynchronously without blocking agent computation."

### Component Specification

**Local Invariant Gate.** Inline pre-transition middleware compiling Ωi and Ψi into optimized boolean evaluation routines, enforcing a structural barrier before any local state mutation occurs.

**Formal Trace Recorder.** Append-only, lock-free concurrent buffer recording accepted execution traces against logical vector clocks, ensuring linear history capture without global clock synchronization.

**Post-Facto Cryptographic Proof Log.** Asynchronous pipeline generating block hashes H(s ‖ l ‖ s' ‖ Proof(πi)) for post-facto verification of the trace inclusion calculus.

**Async Drift Compensator.** Reconciliation daemon monitoring trace histories for observation equivalence drift, forcing rollbacks to verified projection anchors if out-of-order anomalies are detected.

**Table 1: Asymptotic complexity of p-DERS components.**

| Component | Operation | Complexity |
|---|---|---|
| Local Invariant Gate | Predicate eval | O(di) |
| Trace Recorder | Append | O(1) amortized |
| Proof Pipeline | Hash batch | O(b) async |
| Drift Compensator | Trace compare | O(k) async |

## Prototype and Engineering Evaluation

### Computational Characteristics

Here di is the projected transition out-degree, b the batch size, and k the reconciliation window (Table 1). Verification overhead scales with local projection size rather than global agent count.

### Prototype Implementation

A research prototype was developed in Rust. Each node instantiates five independent components: Local Invariant Gate, Local Execution Engine, Append-Only Trace Recorder, Cryptographic Proof Pipeline, and Asynchronous Drift Compensator. Nodes communicate exclusively through asynchronous message passing, avoiding global synchronization, centralized schedulers, and shared global state.

### Results

Across all workloads, every accepted execution remained consistent with the projected specification. Under adversarial workloads, all specification-violating attempts were intercepted before state mutation. Verification latency remained effectively independent of total node count, scaling with projected specification size. These observations are consistent with the theoretical properties established in Sections 3 and 6.

## Related Work

**Refinement-Based Verification.** Classical techniques [Hoare(1985), Milner(1989), Sangiorgi(2012)] assume globally observable transition systems. p-DERS replaces monolithic simulation with projection-consistent local refinement relations.

**Runtime Verification.** Existing approaches [Falcone, Havelund, and Reger(2019), Leucker and Schallhart(2009)] monitor centralized streams or completed traces. p-DERS intercepts unsafe transitions before state mutation.

**Distributed Verification.** Consensus-based methods [Lynch(1996)] become restrictive under autonomous multi-agent execution. p-DERS establishes correctness through projection consistency without global consensus.

**Information-Flow Security.** Classical IFC [Denning(1976), Sabelfeld and Myers(2003)] evaluates isolated states. p-DERS transition invariants evaluate behavioral changes, enabling simultaneous CFI and IFC enforcement.

**AI Safety.** Safety research [Russell(2019), Amodei et al.(2016)] increasingly targets multi-agent interaction. p-DERS governs execution topology, making safety a formally verifiable property of distributed execution.

## Limitations and Future Work

p-DERS assumes the global specification is correct and that projection functions satisfy the consistency properties of Section 4. The current formulation addresses finite execution traces; probabilistic verification and temporal logic extensions are deferred. p-DERS governs externally observable execution rather than internal reasoning, complementing rather than replacing alignment techniques inside AI models.

Future work will investigate automatic projection synthesis, machine-assisted invariant generation, hierarchical governance models, and large-scale empirical evaluation across heterogeneous agent ecosystems.

## Conclusion

This paper introduced p-DERS, a decentralized formal verification framework for safety governance in asynchronous multi-agent orchestration. By replacing monolithic global simulation with projection-based refinement, observation-equivalent trace inclusion, and dual-frame invariant enforcement, p-DERS enables formally verified safety without requiring globally synchronized execution. The reference runtime architecture demonstrates practical integration through localized invariant enforcement, append-only trace recording, asynchronous cryptographic accountability, and distributed drift reconciliation. These contributions establish a unified mathematical foundation connecting formal methods, distributed systems, runtime verification, and AI safety governance for autonomous multi-agent ecosystems.

## References

[Amodei et al.(2016)] Amodei, D.; Olah, C.; Steinhardt, J.; Christiano, P.; Schulman, J.; and Mane, D. 2016. Concrete Problems in AI Safety. arXiv preprint arXiv:1606.06565.
[Denning(1976)] Denning, D. E. 1976. A Lattice Model of Secure Information Flow. Communications of the ACM, 19(5): 236–243.
[Falcone, Havelund, and Reger(2019)] Falcone, Y.; Havelund, K.; and Reger, G. 2019. A Tutorial on Runtime Verification. In Engineering Dependable Software Systems, 141–175. IOS Press.
[Hoare(1985)] Hoare, C. A. R. 1985. Communicating Sequential Processes. Prentice Hall.
[Leucker and Schallhart(2009)] Leucker, M.; and Schallhart, C. 2009. A Brief Account of Runtime Verification. Journal of Logic and Algebraic Programming, 78(5): 293–303.
[Lynch(1996)] Lynch, N. A. 1996. Distributed Algorithms. Morgan Kaufmann.
[Milner(1989)] Milner, R. 1989. Communication and Concurrency. Prentice Hall.
[Russell(2019)] Russell, S. 2019. Human Compatible: Artificial Intelligence and the Problem of Control. Viking.
[Sabelfeld and Myers(2003)] Sabelfeld, A.; and Myers, A. C. 2003. Language-Based Information-Flow Security. IEEE Journal on Selected Areas in Communications, 21(1): 5–19.
[Sangiorgi(2012)] Sangiorgi, D. 2012. Introduction to Bisimulation and Coinduction. Cambridge University Press.

---

## Transcription-doubtful spots (flagged per instructing memo Section 3, not resolved here)

These are noted because they are the kind of detail an OCR/manual-transcription pass is most likely to get subtly wrong, and because later analysis (`pDERS_overlap_consistency_v0.2.md`) leans on their exact reading. None of these are corrected or resolved here - they are flagged as-is, for whoever can check against the actual PDF directly.

1. **"⊑Ri" notation** (Local Simulation Relations section, and Lemma 1's premise): transcribed as a subscripted refinement symbol (sqsubseteq with Ri as a subscript label naming which relation the refinement ordering is with respect to). Whether the source actually subscripts the relation this way, or uses different notation (e.g. a separate "refines" predicate applied to Ri as an argument), could not be independently verified in this session.
2. **"Ωi = Ωj" and "Ψi = Ψj" in Assumption 4**: transcribed as plain equality between the two predicates on the shared domain. Given Ωi/Ψi are typed as functions into {0,1} (Definitions 1-2), equality-of-functions-on-a-shared-domain is a coherent reading, but this session cannot rule out the source instead using an equivalence/biconditional notation (e.g. "Ωi ⟺ Ωj" per-argument) that got flattened to "=" during transcription. This distinction does not change this document's analysis materially (both readings amount to "same boolean output on the shared domain"), but is flagged for completeness.
3. **Figure 1 and Figure 2 "descriptions"**: explicitly presented by R02's transcription as descriptions/paraphrases of the figures' visual content, not extracted caption text. The specific claim "Cryptographic composition: H(Ti) ‖ H(Tj) ‖ H(Tk) → global safety proof" in Figure 1's description is treated in `pDERS_overlap_consistency_v0.2.md` as informative context about the paper's intended multi-node composition story, but explicitly **not** as a formally stated theorem, since it appears only in a figure description, not in the body text's Definitions/Lemmas/Theorem statements.
4. **Numbering discontinuity between the Mathematical Foundations section and the Dual-Frame Invariants section**: Assumption 4 and Lemma 1 (Mathematical Foundations) both refer to Ωi/Ψi conceptually before Definitions 1-2 (which formally introduce Ωi/Ψi) appear later, in "Trace Inclusion and Dual-Frame Invariants." This may simply be the paper's own expository ordering (stating assumptions about objects that are formally defined shortly after), which is common and not itself a transcription error - but it is flagged because it means Assumption 4's own statement is read here using the *type* given later in Definitions 1-2, not a type given at the point Assumption 4 itself is stated.

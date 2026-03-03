MoCKA Shadow: Deterministic, Verifiable, Evolution-Safe

MoCKA includes a dual-layer Shadow architecture designed for verifiable provenance and non-interference.
It separates immutable, byte-stable documentation (sealed by SHA256 and signed commits) from an evolution-safe runtime sandbox.

Layer 1: shadow_pj (Immutable, Descriptive)
shadow_pj contains purely descriptive artifacts only.
It is byte-stable, deterministic, and intentionally non-executable.
No runtime hooks, no CI linkage, and no operational secrets.

Layer 2: shadow_runtime (Evolvable, Runtime-Safe)
shadow_runtime is a sandbox for experiments, prototypes, and data-oriented artifacts.
It is explicitly uncoupled from MoCKA core execution paths and CI.
Volatile outputs must go to shadow_runtime/outbox/ and should not be committed.

Why this exists

- Deterministic artifacts: byte-stable files and controlled encodings
- Verifiable provenance: SHA256 registries and cryptographic signing
- Non-interference governance: strict boundary rules to protect core integrity
- Innovation without contamination: experiments can evolve safely outside the immutable layer

Keywords

verifiable AI, deterministic artifacts, provenance, signed commits, byte-stable, non-interference, audit trail, reproducible governance

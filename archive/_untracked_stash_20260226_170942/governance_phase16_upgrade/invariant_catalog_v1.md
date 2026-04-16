\# NOTE: Invariant Catalog v1 (Phase16.1 baseline)

\# NOTE: Undefined invariant violation SHALL be FAIL.

\# NOTE: Classification is mandatory: STRUCT / CRYPTO / OPS / ARTIFACT / REPRO.

\# NOTE: Severity is mandatory: BLOCKER / HIGH / MEDIUM.



\# Invariant Catalog v1



\## Schema

Fields: id, classification, severity, verifier\_scope, description



\## Structural Invariants



ID: INV-STRUCT-001

Classification: STRUCT

Severity: BLOCKER

VerifierScope: governance\_verify, final\_check

Description: GENESIS event must be unique.



ID: INV-STRUCT-002

Classification: STRUCT

Severity: BLOCKER

VerifierScope: governance\_verify, audit\_verify, final\_check

Description: TIP must always be reachable from GENESIS.



ID: INV-STRUCT-003

Classification: STRUCT

Severity: BLOCKER

VerifierScope: governance\_verify, final\_check

Description: branch\_registry.classification must NOT be NULL.



ID: INV-STRUCT-004

Classification: STRUCT

Severity: HIGH

VerifierScope: governance\_verify, final\_check

Description: quarantine branch must never be selectable as TIP.



\## Crypto Invariants



ID: INV-CRYPTO-001

Classification: CRYPTO

Severity: BLOCKER

VerifierScope: audit\_verify, final\_check

Description: Signature input must be deterministic and canonical.



ID: INV-CRYPTO-002

Classification: CRYPTO

Severity: BLOCKER

VerifierScope: audit\_verify, final\_check

Description: Envelope signature must bind event\_id, chain\_hash, timestamp\_utc, payload\_hash\_sha256, key\_id.



\## Operational Invariants



ID: INV-OPS-001

Classification: OPS

Severity: HIGH

VerifierScope: audit\_verify, final\_check

Description: All reconciliation and attestation workflows must converge to a terminal state.



ID: INV-OPS-002

Classification: OPS

Severity: BLOCKER

VerifierScope: final\_check

Description: No undefined error classification is allowed.



\## Artifact Invariants



ID: INV-ARTIFACT-001

Classification: ARTIFACT

Severity: HIGH

VerifierScope: final\_check

Description: All outbox artifacts must be present in a manifest with sha256.



\## Reproducibility Invariants



ID: INV-REPRO-001

Classification: REPRO

Severity: HIGH

VerifierScope: final\_check

Description: Verification results must not vary across environments for identical inputs.


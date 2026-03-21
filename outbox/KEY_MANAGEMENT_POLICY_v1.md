KEY MANAGEMENT POLICY v1.0



1\. Purpose

This policy defines how cryptographic keys are generated, stored, used, rotated, revoked, and audited for MoCKA.



2\. Scope

Applies to all signing keys used for: outbox seals, verify reports, chain artifacts, and policy-grade attestations.



3\. Roles and Keys

3.1 Outfield Signing Key

Role: execution pack attestation (SEAL, VERIFY, OUTBOX\_INDEX).

Key type: Ed25519 OpenPGP

Fingerprint: FFA3AD2322B094AFEC12CA886BA095C48E3315F2

Usage: sign only. No encryption requirement.



3.2 Verifier Signing Key

Role: independent verification attestation (Phase2-C report and beyond).

Key type: Ed25519 OpenPGP

Ownership: operator verifier identity.

Usage: sign only.



3.3 Policy Authority Key

Role: policy document release signing (Phase3+).

Key type: Ed25519 OpenPGP

Usage: sign only.



4\. Storage Policy

4.1 Private Keys

Store private keys offline whenever possible.

If online storage is unavoidable, enforce OS account separation and disk encryption.



4.2 Public Keys

Public keys must be exported in ASCII armor and stored under repository-controlled locations.



5\. Key Separation

Keys MUST be separated by role.

Outfield key MUST NOT sign verifier reports.

Verifier key MUST NOT sign outfield execution artifacts.



6\. Rotation

Rotation interval: 12 months (default) or immediately on suspected compromise.

Rotation requires:

\- generating a new key

\- exporting and sealing the new public key

\- updating fingerprints in policy docs

\- cross-signing transition statement with old and new keys when possible



7\. Revocation

A revocation certificate MUST be generated at key creation time.

Revocation certificate storage must be offline and redundant (at least two physical locations).



8\. Audit Logging

All key operations must be logged:

\- key creation date

\- fingerprint

\- who performed operation

\- machine identifier (non-secret)

\- purpose of operation

Logs must be sealed and signed.



9\. Verification Requirements

Any artifact claim is valid only if:

\- referenced hashes match computed hashes

\- signatures verify against the recorded fingerprint

\- the verifying public key is stored and traceable



10\. Incident Response

On suspected compromise:

\- stop signing immediately

\- revoke key

\- rotate key

\- publish incident note with timestamps and affected artifacts list


\# NOTE: key\_policy\_v1.md (Phase16.4 baseline)

\# NOTE: Objective: key rotation and revocation must not break historical verification.

\# NOTE: All signatures MUST carry key\_id. key\_id MUST match a keyring entry.

\# NOTE: Revoked keys MUST NOT be used for new signing.



\# Key Policy v1



\## 1. Scope

This policy governs Ed25519 keys used for Phase16 envelope signatures.



\## 2. Definitions

\- key\_id: stable identifier for a public key (recommended: fingerprint)

\- keyring: a list of trusted public keys indexed by key\_id

\- revocation: marking a key\_id as disallowed for new signatures



\## 3. Key Material Locations (Windows)

\- Active signing key directory (restricted):

&nbsp; C:\\Users\\sirok\\MoCKA\\secrets\\phase16\\

\- Public key path environment variable (current):

&nbsp; MOCKA\_PHASE16\_PUBKEY\_PATH=C:\\Users\\sirok\\MoCKA\\secrets\\phase16\\ed25519\_public.pem



\## 4. Keyring File (required)

A keyring file MUST exist and be referenced by verifiers.



Recommended location:

C:\\Users\\sirok\\MoCKA\\secrets\\phase16\\keyring.json



Minimum schema:

\- version

\- keys: list of { key\_id, public\_key\_pem\_path, created\_utc, status }



Status values:

\- ACTIVE

\- RETIRED

\- REVOKED



\## 5. Revocation File (required)

A revocation list MUST exist.



Recommended location:

C:\\Users\\sirok\\MoCKA\\secrets\\phase16\\revocation.json



Minimum schema:

\- version

\- revoked: list of { key\_id, revoked\_utc, reason }



\## 6. Verification Rules

1\. Extract key\_id from envelope.

2\. Lookup key\_id in keyring.json.

3\. If key\_id is not found: FAIL with ERR-CRYPTO-003 (KEY\_NOT\_FOUND).

4\. If key\_id is in revocation.json: verification may still validate historical signatures, but:

&nbsp;  - New issuance MUST be blocked.

&nbsp;  - Verifier MUST emit a warning-class record (policy event) for audit trace.

5\. Verify signature using the resolved public key.



\## 7. Rotation Procedure (Emergency or Planned)

1\. Generate new keypair in restricted directory.

2\. Compute new key\_id and add to keyring.json with status ACTIVE.

3\. Mark previous ACTIVE key as RETIRED (not revoked).

4\. Update signing process to use new ACTIVE key.

5\. Run audit\_verify on a new v2 envelope proof.

6\. Keep retired keys in keyring indefinitely for historical verification.



\## 8. Emergency Compromise Procedure

1\. Mark compromised key\_id as REVOKED in keyring.json.

2\. Add key\_id to revocation.json with revoked\_utc and reason.

3\. Block new issuance using compromised key.

4\. Rotate to a new key as in Section 7.

5\. Record a governance event describing the revocation decision (Phase14.6 linkage).



\## 9. Non-Negotiable Constraints

\- key\_id MUST be present in every v2 envelope.

\- Verifiers MUST use keyring.json, not a single hardcoded key path.

\- Revocation MUST not erase historical verifiability.


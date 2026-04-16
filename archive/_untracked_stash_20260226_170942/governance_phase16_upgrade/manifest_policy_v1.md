\# NOTE: Manifest Policy v1

\# NOTE: All outbox artifacts MUST appear in manifest with sha256.

\# NOTE: Manifest itself SHOULD be signed using Envelope v2 scheme.



\# Manifest Policy v1



\## 1. Scope

Applies to:

C:\\Users\\sirok\\MoCKA\\outbox\\\*



\## 2. Required Fields per Artifact

\- path

\- size\_bytes

\- sha256

\- created\_utc

\- schema\_version



\## 3. Hash Rule

sha256 MUST be calculated over raw file bytes.

No newline normalization.

No text decoding.



\## 4. Manifest Integrity

The manifest file:

phase16\_fixed\_artifacts.json



MUST:

1\. Match manifest\_schema\_v1.json

2\. Be included as an artifact entry

3\. Be signed using Envelope v2



\## 5. Verification Rule

Verification MUST:

1\. Recompute sha256 for each artifact

2\. Compare against manifest entry

3\. Fail with ERR-ARTIFACT-002 if mismatch

4\. Fail with ERR-ARTIFACT-001 if file missing



\## 6. Non-Negotiable

An artifact outside the manifest SHALL be treated as untrusted.


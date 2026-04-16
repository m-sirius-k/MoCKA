\# NOTE: Reproducibility Profile v1

\# NOTE: Verification MUST be reproducible across environments.

\# NOTE: All verifiers MUST emit a verify\_report.json for every run.



\# Reproducibility Profile v1



\## 1. Required Environment Recording

Each verification run MUST record:

\- utc\_now

\- hostname

\- os\_version

\- python\_version

\- package\_versions (at minimum: cryptography, pynacl if used)

\- repo\_commit (if available)

\- verifier\_name and version



\## 2. Determinism Rules

\- Signed bytes must follow canonicalization\_and\_bytespec\_v2.md exactly.

\- Hashes are computed from raw bytes.

\- Locale and timezone must not affect results (UTC only).



\## 3. Output Report

A JSON report MUST be emitted:

\- verify\_report.json



Recommended location:

C:\\Users\\sirok\\MoCKA\\outbox\\verify\_report.json



\## 4. Pass/Fail Policy

\- Any environment variance for identical inputs MUST be ERR-REPRO-001 and FAIL.

\- Missing required environment fields MUST FAIL.



\## 5. Non-Negotiable

No silent success. Every run MUST emit a report.


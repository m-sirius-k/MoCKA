\# MoCKA Operational Runbook SOP v1.0



\## 1. Purpose



This document defines the minimum operational procedure for MoCKA Production Governance Lite.



The purpose is not automatic recovery, but preserving evidence integrity and enabling human-authorized decisions.



\## 2. Core Principles



\### FAIL-CLOSED Absolute



When integrity verification fails, the system must halt.



The following actions are prohibited:



\- Auto Repair

\- Fallback

\- Silent Recovery

\- Human Gate Bypass



\### Evidence > Availability



Evidence integrity has priority over system availability.



\### Human Authority



AI systems may assist evidence organization and presentation.



Only Human Authority may:



\- determine cause

\- approve recovery

\- record final decisions



\## 3. FAIL-CLOSED Response Flow





FAIL-CLOSED Trigger

|

v

Evidence Preservation

|

v

Incident Correlation ID Identification

|

v

Human Audit

|

v

Decision Ledger Record

|

v

Human Resume Authorization





\## 4. Evidence Handling



Required order:



1\. Halt

2\. Preserve

3\. Copy

4\. Analyze



Original evidence must remain unchanged.



Analysis must be performed on copied evidence only.



\## 5. Decision Record Requirements



Human decision records must include:



\- Incident Correlation ID

\- Evidence Reference Hash

\- Operator Identity

\- Decision Result

\- Decision Reason

\- Timestamp



\## 6. Resume Authorization



System resume is permitted only after Human Authority records an approved decision.



No automated resume is allowed.


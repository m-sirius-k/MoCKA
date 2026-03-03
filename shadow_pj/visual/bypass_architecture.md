# VAR-001: Shadow Bypass Architecture

```mermaid
flowchart TD

A[Primary Core\n100% Operation] -->|Normal| B[Business Output]

A -->|Failure Detected| C[Shadow Core\n75% Bypass Mode]

C --> D[Read Operations Continue]
C --> E[Write Operations Restricted]
C --> F[Queue Isolation]

C --> G[Signal Layer]
C --> H[Ledger Layer]
C --> I[Repair Proposal Layer]
Concept

Primary = Main Heart
Shadow = Bypass Heart
Signal = Monitor
Ledger = Medical Record
Repair = Treatment Plan

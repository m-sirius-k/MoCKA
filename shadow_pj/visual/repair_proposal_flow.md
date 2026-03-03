VAR-005: Repair Proposal Flow

Overview

Repair Proposal Flow defines how Shadow creates a repair plan without executing it blindly.

Shadow observes.
Shadow analyzes.
Shadow proposes.
A human approves.

This separation prevents self-attack loops and preserves governance.

Flow Structure

Anomaly Detected
↓
Impact Scope Analysis
↓
Generate Repair Proposal
↓
Assign Repair_ID
↓
Append Proposal to Ledger
↓
Await Manual Approval

Optional Conditioned Automation

Limited auto-repair may execute only if all conditions are satisfied:

1. Impact is limited and scoped
2. Proposal is signed and verified
3. Cooldown window is satisfied
4. Allowlist rule is matched
5. Execution is fully logged

Principles

1. No blind auto-repair.
2. Every proposal is traceable via Repair_ID.
3. Execution requires explicit approval unless constrained automation is permitted.
4. All steps emit Signal and append Ledger.
5. A repair action must never erase its own evidence.

Repair_ID Concept

Repair_ID is the system "safe word" for self-modification.

It identifies:
- what is being repaired
- why it is being repaired
- under which conditions it is allowed

Beginner Explanation

Shadow writes a treatment plan.
A human approves the treatment.
The system does not operate on itself without consent.

Asset Management pj Context

This experiment focuses on building Shadow as a bypass heart.

Repair Proposal Flow is the backbone of controlled recovery.
It enables safe evolution without sacrificing continuity.

VAR-006: Bypass Switching Architecture

Overview

Bypass Switching Architecture defines the control plane that routes traffic
between Primary and Shadow.

Primary is the main heart.
Shadow is the bypass heart.

Switching must be:
- Explicit
- Logged
- Reversible
- Safe by default

Components

1. Front Door
   Entry point for requests (API gateway, router, or dispatcher)

2. Primary Lane
   Normal route for full operation

3. Shadow Lane
   Bypass route for degraded but continuous operation

4. Switch Controller
   Decision unit that selects the lane

5. Signal and Ledger
   Observability and immutable trace for every switch

Switch States

STATE_PRIMARY
- Route to Primary Lane
- Shadow stays warm but does not serve as default

STATE_SHADOW
- Route to Shadow Lane
- Primary may remain running but is not trusted for writes

Switch Rules

1. Transition to STATE_SHADOW requires an Integrity Trigger or Manual Switch.
2. Transition to STATE_PRIMARY requires Recovery Verification and Manual Approval.
3. Every switch emits Signal and appends Ledger.
4. Default policy in ambiguity is STATE_SHADOW (fail-safe).

Operational Guarantees

In STATE_SHADOW:
- Read operations continue.
- Write operations are restricted.
- Writes may be redirected to an isolated queue.

Beginner Explanation

Imagine a highway with two lanes.

Lane A is the normal lane.
Lane B is the emergency lane.

When the road is damaged,
the controller redirects cars to the emergency lane,
and records exactly when and why.

Asset Management pj Context

This is the operational skeleton that turns Shadow into a real bypass system.

It is the routing architecture that enables the 75% survival promise.

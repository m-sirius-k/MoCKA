"""TIM_MOCKA_COMPARATIVE_TEST v0.1 - isolated experiment.

Status: EXPERIMENTAL / ISOLATED / NOT CONNECTED TO PRODUCTION.

What this is
------------
A minimal, self-contained experiment on ONE question:

    Can a past decision be reused now, and on what evidence?

The controlling principle, stated in the instruction that commissioned it:

    "past decision was ALLOW" must never, by itself, be the ground for
    "the decision is ALLOW now".

What this is NOT
----------------
- Not a model of anyone's stated position. No external discussion material was
  supplied to this session; the case matrix implemented here comes from the
  commissioning instruction itself. See
  docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md.
- Not connected to the Constitutional Runtime Trial. This package imports
  nothing from experiments/constitutional_runtime_trial and shares no vocabulary
  with it.
- Not evidence about any original Constitutional Runtime. That remains
  NOT OBSERVED / UNKNOWN.

Isolation rules
---------------
- Standard library only.
- No import of MoCKA production modules.
- No write to events.db, Decision Ledger, Human Gate, or any production store.
- The names defined here are LOCAL TO THIS EXPERIMENT. They are not proposed as
  formal MoCKA primitives; adopting any of them requires a separate Human Gate.
"""

EXPERIMENT_NAME = "TIM_MOCKA_COMPARATIVE_TEST_v0.1"
EXPERIMENT_STATUS = "EXPERIMENTAL / ISOLATED"

__all__ = ["temporal", "cases", "run_comparative"]

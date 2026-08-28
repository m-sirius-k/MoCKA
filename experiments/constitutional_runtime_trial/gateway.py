"""Execution gateway for the MoCKA CR Trial.

The gateway is deliberately trivial and deliberately separate from the runtime.
Its only job is to make one property impossible to lose in refactoring:

    UNKNOWN != ALLOW

The runtime keeps three internal decision states. The gateway collapses them to
two execution outcomes, and the collapse is one-directional: only ALLOW
executes.
"""

from .primitives import Decision, Execution

_GATE = {
    Decision.ALLOW: Execution.EXECUTE,
    Decision.BLOCK: Execution.STOP,
    Decision.UNKNOWN: Execution.STOP,
}


def gate(decision):
    """Map an internal Decision to an Execution outcome.

    An unrecognized decision object stops execution. There is no default that
    executes.

    The isinstance check is load-bearing, not defensive noise. Decision is a
    str enum, so the bare string "ALLOW" compares and hashes equal to
    Decision.ALLOW. Without the type check, an untyped label would open the
    gate. A label is not a decision.
    """
    if not isinstance(decision, Decision):
        return Execution.STOP
    return _GATE.get(decision, Execution.STOP)


# Permissiveness lattice. A decision may only ever move down this order.
_RANK = {Decision.BLOCK: 0, Decision.UNKNOWN: 1, Decision.ALLOW: 2}

_VERDICT_AS_DECISION = {
    "BLOCK": Decision.BLOCK,
    "UNKNOWN": Decision.UNKNOWN,
    "ALLOW": Decision.ALLOW,
}


def apply_bound_verdict(decision, bound_verdict):
    """Let a bound RE verdict lower a decision, never raise it.

    A verdict is not an execution authority. This is a meet (greatest lower
    bound) over BLOCK < UNKNOWN < ALLOW: a bound denial is honored, a bound
    UNKNOWN degrades, and a bound ALLOW grants nothing on its own.

    bound_verdict must be None when the verdict is not bound. An unbound
    verdict never reaches this function.
    """
    if not isinstance(decision, Decision):
        # Same str-enum hazard as in gate(): an untyped decision is not a
        # decision, and it degrades rather than passing through.
        return Decision.UNKNOWN
    if bound_verdict is None:
        return decision
    as_decision = _VERDICT_AS_DECISION.get(bound_verdict)
    if as_decision is None:
        # A verdict outside the typed vocabulary is not interpreted. It cannot
        # raise the decision, and it is not silently discarded either.
        return Decision.UNKNOWN if decision is Decision.ALLOW else decision
    return decision if _RANK[decision] <= _RANK[as_decision] else as_decision

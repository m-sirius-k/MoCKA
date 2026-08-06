import pytest

from phi_os.context.access_gate import (
    enforce_observe,
    AccessDeniedError,
)
from phi_os.context.permissions import ACTOR_SCOPED


def test_actor_scoped_observe_self_allowed():
    enforce_observe(
        "actor-A",
        "actor-A",
        ACTOR_SCOPED,
    )


def test_actor_scoped_observe_other_rejected():
    with pytest.raises(AccessDeniedError):
        enforce_observe(
            "actor-A",
            "actor-B",
            ACTOR_SCOPED,
        )


def test_actor_scoped_observe_empty_actor_rejected():
    with pytest.raises(AccessDeniedError):
        enforce_observe(
            "",
            "actor-A",
            ACTOR_SCOPED,
        )

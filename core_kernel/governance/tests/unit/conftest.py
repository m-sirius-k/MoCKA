"""Shared fixtures for Governance unit tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core_kernel.governance.contracts.validation_contract import VALIDATION_SCOPE


@pytest.fixture
def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def full_validation_evidence() -> dict:
    """All VALIDATION_SCOPE items present -> Validation Engine returns VALID."""
    return {scope: True for scope in VALIDATION_SCOPE}

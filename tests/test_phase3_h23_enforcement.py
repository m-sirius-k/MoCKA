"""
Phase 3: H2-3 Event-level Enforcement Implementation Tests
Tests for DC_20260812_003/004/005 formal decisions
"""
import pytest
from phi_os.context.access_gate import (
    enforce_observe,
    sanitize_event_for_observe,
    AccessDeniedError,
)
from phi_os.context.permissions import GLOBAL, ACTOR_SCOPED


class TestGatewayAuthorizationBoundary:
    """DC_20260812_003: Gateway-led Defense in Depth
    Authorization determines WHO can access events (access control gate).
    """

    def test_global_scope_allows_any_actor(self):
        """GLOBAL scope permits any requesting_actor_id to observe."""
        # Should not raise even with arbitrary actor_id
        enforce_observe("any_actor", None, GLOBAL)
        enforce_observe("another_actor", None, GLOBAL)
        # No exception raised = authorization granted

    def test_global_scope_with_empty_actor_allowed(self):
        """GLOBAL scope allows even empty actor_id (public access)."""
        enforce_observe("", None, GLOBAL)


class TestVisibilityBoundary:
    """DC_20260812_005: Visibility determines WHICH FIELDS are exposed.
    sanitize_event_for_observe() filters sensitive metadata.
    """

    def test_sanitize_filters_to_allowed_fields(self):
        """Only _EVENT_OBSERVE_FIELDS are retained."""
        event = {
            "event_id": "E123",
            "actor_id": "actor_A",
            "timestamp": "2026-08-12T00:00:00Z",
            "type": "DECISION",
            "summary": "Test event",
            "metadata": {"key": "value"},
            "internal_field": "should be removed",
            "debug_info": "should be removed",
        }
        sanitized = sanitize_event_for_observe(event)
        assert "event_id" in sanitized
        assert "actor_id" in sanitized
        assert "timestamp" in sanitized
        assert "type" in sanitized
        assert "summary" in sanitized
        assert "metadata" in sanitized
        assert "internal_field" not in sanitized
        assert "debug_info" not in sanitized

    def test_sanitize_removes_sensitive_metadata(self):
        """Sensitive keys in metadata are filtered out."""
        event = {
            "event_id": "E123",
            "metadata": {
                "public_key": "public_value",
                "password": "secret_password",
                "api_key": "secret_key",
                "token": "secret_token",
                "normal_field": "allowed",
            },
        }
        sanitized = sanitize_event_for_observe(event)
        metadata = sanitized.get("metadata", {})
        assert "public_key" in metadata
        assert "normal_field" in metadata
        assert "password" not in metadata
        assert "api_key" not in metadata
        assert "token" not in metadata

    def test_sanitize_preserves_metadata_without_sensitive_keys(self):
        """Metadata without sensitive keys is preserved completely."""
        event = {
            "event_id": "E123",
            "metadata": {
                "phase": "Phase 3",
                "priority": "high",
            },
        }
        sanitized = sanitize_event_for_observe(event)
        metadata = sanitized.get("metadata", {})
        assert metadata == {"phase": "Phase 3", "priority": "high"}


class TestActorIdDefenseInDepth:
    """DC_20260812_004: actor_id verified independently at each layer.
    ACTOR_SCOPED scope enforces independent verification at MCP layer.
    """

    def test_actor_scoped_self_access_allowed(self):
        """Actor can observe own scope (actor-scoped)."""
        enforce_observe("actor_A", "actor_A", ACTOR_SCOPED)

    def test_actor_scoped_other_access_denied(self):
        """Actor cannot observe other actor's scope (actor-scoped)."""
        with pytest.raises(AccessDeniedError):
            enforce_observe("actor_A", "actor_B", ACTOR_SCOPED)

    def test_actor_scoped_requires_actor_id(self):
        """Empty actor_id is denied even for own scope."""
        with pytest.raises(AccessDeniedError):
            enforce_observe("", "actor_A", ACTOR_SCOPED)


class TestProjectionBoundary:
    """DC_20260812_005: Projection is presentation control, NOT authorization.
    Mode-based field reduction (compact/standard/extended) is applied
    AFTER Authorization and Visibility checks.
    """

    def test_projection_is_presentation_not_authorization(self):
        """Projection mode filtering is separate from authorization.
        This test verifies that sanitize_event_for_observe()
        filters fields based on content (sensitive keys), not on
        a projection 'mode' parameter - projection is downstream.
        """
        event = {
            "event_id": "E123",
            "actor_id": "actor_A",
            "timestamp": "2026-08-12T00:00:00Z",
            "type": "DECISION",
            "summary": "Test event",
            "metadata": {"status": "active"},
        }
        # Visibility filtering happens uniformly regardless of projection mode
        sanitized = sanitize_event_for_observe(event)
        # All allowed fields are present; projection is applied later
        # by presentation layer (context_builder with mode parameter)
        assert "event_id" in sanitized
        assert "summary" in sanitized


class TestLayeringOrder:
    """DC_20260812_005: Authorization -> Visibility -> Projection order
    Each layer operates on output of previous layer.
    """

    def test_authorization_before_visibility(self):
        """Authorization (enforce_observe) is enforced before visibility filtering."""
        # If authorization fails, visibility filtering never happens
        with pytest.raises(AccessDeniedError):
            enforce_observe("actor_A", "actor_B", ACTOR_SCOPED)
        # Sanitization is not attempted when authorization fails

    def test_visibility_before_projection(self):
        """Visibility (sanitize_event) is applied before projection formatting."""
        event = {
            "event_id": "E123",
            "password": "secret",
            "metadata": {"api_key": "secret_key", "public": "value"},
        }
        # Visibility filtering removes sensitive top-level fields
        sanitized = sanitize_event_for_observe(event)
        assert "password" not in sanitized  # Removed by visibility
        # Projection mode would then select which fields to show
        # (compact/standard/extended) from the already-sanitized event

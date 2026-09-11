"""
H2-1/H2-2 強制インターセプト層(7.1c) — observe/write境界をコードで強制する。
control境界は別モジュール control_gate.py に分離する(7.1b)。
M18 追加: Feature-level authorization resolver integration (multi-layer defense).
"""
from __future__ import annotations
from typing import Optional

from . import permissions

# Event層 global observe で許可するフィールド(7.1d)。raw payload直接公開は禁止。
_EVENT_OBSERVE_FIELDS = {"event_id", "actor_id", "timestamp", "type", "summary", "metadata"}

# metadata内のsensitiveキー判定(部分一致・大小無視)。
_SENSITIVE_KEY_PATTERNS = (
    "password", "secret", "token", "api_key", "apikey",
    "credential", "private_key", "authorization",
)


class AccessDeniedError(Exception):
    pass


def before_event_write(actor_id: str, event_payload: dict) -> dict:
    """Event書き込み直前の強制チェック。actor_id未指定の書き込みは許可しない。"""
    if not actor_id:
        raise AccessDeniedError("Event書き込みにはactor_idが必須")
    return event_payload


def before_context_update(
    actor_id: str,
    target_actor_id: str,
    authorization_id: Optional[str] = None,
    sealed_auth: Optional[object] = None,
    resolver: Optional[object] = None,
) -> None:
    """
    WorkingContext更新直前の強制チェック。

    Multi-layer defense:
    1. Actor-level permission check (existing: permissions.check_write)
    2. Feature-level authorization check (new: resolver via M18)

    Both must ALLOW for execution to proceed.

    Args:
        actor_id: Requesting actor
        target_actor_id: Target actor being modified
        authorization_id: Optional sealed authorization ID
        sealed_auth: Optional SealedAuthorizationObject instance
        resolver: Optional AuthorizationResolver instance
    """
    # Layer 1: Actor-level RBAC (existing)
    if not permissions.check_write(actor_id, target_actor_id):
        raise AccessDeniedError(
            f"actor '{actor_id}' は actor '{target_actor_id}' のWorkingContextを更新できない"
        )

    # Layer 2: Feature-level Authorization (M18)
    if authorization_id and sealed_auth and resolver:
        try:
            from phi_os.runtime.authorization_resolver import (
                AuthorizationResolutionContext, ResolutionStatus
            )

            # Build resolution context
            context = AuthorizationResolutionContext(
                requesting_identity=actor_id,
                requesting_role="unknown",  # Role not yet determined at this layer
                operation="write",
                resource_type="working_context",
                resource_id=f"actor:{target_actor_id}",
            )

            # Resolve authorization
            result = resolver.resolve(sealed_auth, context)

            # Must ALLOW (not BLOCK, not UNKNOWN, not EXPIRED, not REVOKED)
            if not result.allow or result.status != ResolutionStatus.ALLOW:
                raise AccessDeniedError(
                    f"Authorization denied: {result.status.value}. "
                    f"Reason: {result.reasoning}"
                )
        except ImportError as ie:
            # Resolver unavailable is a FATAL error - FAIL-CLOSED
            raise AccessDeniedError(
                f"Authorization system unavailable (ImportError: {str(ie)}). "
                f"Cannot execute without resolver."
            )
        except Exception as e:
            # Any resolver error should block execution
            raise AccessDeniedError(f"Authorization check failed: {str(e)}")


def enforce_observe(requesting_actor_id: str, target_actor_id: str | None, scope: str) -> None:
    """observe境界の強制チェック。許可されない場合はAccessDeniedErrorを発生させる。"""
    if not permissions.check_observe(requesting_actor_id, target_actor_id, scope):
        raise AccessDeniedError(
            f"actor '{requesting_actor_id}' は actor '{target_actor_id}' の"
            f"{scope}スコープを観測できない"
        )


def sanitize_event_for_observe(event: dict) -> dict:
    """global observe向けにEventを構造化・sensitive情報をフィルタリングする(3.1)。"""
    sanitized = {k: v for k, v in event.items() if k in _EVENT_OBSERVE_FIELDS}
    metadata = sanitized.get("metadata")
    if isinstance(metadata, dict):
        sanitized["metadata"] = {
            k: v for k, v in metadata.items()
            if not any(p in k.lower() for p in _SENSITIVE_KEY_PATTERNS)
        }
    return sanitized

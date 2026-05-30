"""
vasAI SDK: 3行で使えるクライアント。
    from vasai import VasAIClient
    client = VasAIClient(endpoint="http://localhost:6000", caliber_id="my_company_v1")
    event_id = client.record(who="Claude", what="CHANGE_DONE", content={...})
"""
import json
from typing import Any, Optional
from urllib import request as urllib_request
from urllib.error import URLError

from sdk.vasai.exceptions import VasAIConnectionError, VasAINotFoundError
from sdk.vasai.models import AuditResult, RecordedEvent, ShadowStatus


class _AuditProxy:
    def __init__(self, client: "VasAIClient"):
        self._c = client

    def verify(self) -> AuditResult:
        data = self._c._get("/audit/verify")
        return AuditResult(**data)

    def seal(self) -> str:
        data = self._c._post("/audit/seal", {})
        return data.get("seal_signature", "")

    def report(self) -> AuditResult:
        data = self._c._get("/audit/report")
        return AuditResult(**data)


class _ShadowProxy:
    def __init__(self, client: "VasAIClient"):
        self._c = client

    def status(self) -> ShadowStatus:
        data = self._c._get("/shadow/status")
        return ShadowStatus(
            is_degraded=data.get("is_degraded", False),
            available_pct=data.get("available_pct", 1.0),
            active_stages=[s if isinstance(s, str) else s.get("value", str(s))
                           for s in data.get("active_stages", [])],
            reason=data.get("reason", ""),
        )

    def enter_degraded(self, reason: str = "manual") -> ShadowStatus:
        data = self._c._post("/shadow/enter-degraded", {"reason": reason})
        return ShadowStatus(**{k: data[k] for k in ShadowStatus.model_fields if k in data})

    def exit_degraded(self) -> ShadowStatus:
        data = self._c._post("/shadow/exit-degraded", {})
        return ShadowStatus(**{k: data[k] for k in ShadowStatus.model_fields if k in data})


class VasAIClient:
    """
    vasAI企業向けSDK。
    3行で使えることが設計目標。
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:6000",
        caliber_id: str = "",
        timeout: int = 10,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.caliber_id = caliber_id
        self.timeout = timeout
        self.audit = _AuditProxy(self)
        self.shadow = _ShadowProxy(self)

    # ── Core API ──────────────────────────────────────────

    def record(
        self,
        who: str,
        what: str,
        content: Optional[dict] = None,
        where: str = "",
        why: str = "",
        how: str = "SDK",
        stage: str = "",
    ) -> str:
        """イベントを記録してevent_idを返す。"""
        payload = {
            "who": who, "what": what,
            "content": content or {},
            "where": where, "why": why, "how": how,
            "caliber_id": self.caliber_id, "stage": stage,
        }
        data = self._post("/events", payload)
        return data["event_id"]

    def get_event(self, event_id: str) -> dict:
        return self._get(f"/events/{event_id}")

    def list_events(self, limit: int = 50, what_type: str = "") -> list[dict]:
        params = f"?limit={limit}" + (f"&type={what_type}" if what_type else "")
        data = self._get(f"/events{params}")
        return data.get("events", [])

    def health(self) -> dict:
        return self._get("/health")

    def status(self) -> dict:
        return self._get("/status")

    # ── HTTP helpers ──────────────────────────────────────

    def _get(self, path: str) -> dict:
        try:
            req = urllib_request.Request(self.endpoint + path)
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except URLError as e:
            raise VasAIConnectionError(f"Cannot connect to {self.endpoint}: {e}") from e

    def _post(self, path: str, payload: dict) -> dict:
        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib_request.Request(
                self.endpoint + path, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except URLError as e:
            raise VasAIConnectionError(f"Cannot connect to {self.endpoint}: {e}") from e

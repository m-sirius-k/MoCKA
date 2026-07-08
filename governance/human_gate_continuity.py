"""
governance/human_gate_continuity.py

Phase C-4: Deferred Human Gate Protocol (DHGP) — 縮小版。

MCP接続断を障害として扱うのではなく、Human Gate承認待ちという正式な
状態(WAITING_FOR_HUMAN_GATE)として記録し、Pending Decision Unitとして
永続化する。Core System Fileのcommitを自動化・代替承認することは
一切行わない。

責務(本ファイルのスコープ):
- MCP可用性の記録(check_mcp_availability)
- WAITING_FOR_HUMAN_GATE状態のPending Decision Unit生成・永続化(defer)
- MCP復旧の観測記録(record_mcp_recovery_observed) — 観測するのみで、
  governance_stateは進めない
- governance_stateをWAITING_FOR_HUMAN_GATE以外へ書き換えようとする
  試みの拒否(attempt_state_transition)

責務外(TODO_429「governance/human_gate_cli.py の制度整理」の裁定対象、
本ファイルでは実装しない。2026-07-08、博士裁定によりPhase C-4スコープ外
と確定済み):
- Human Gate再接続方式
- event_id取得経路
- 自動resume可否判定
- resume後のcommit許可条件
本ファイルはWAITING_FOR_HUMAN_GATEへ遷移した時点で処理を止める構造で
あり、governance_stateをそこから先に進める関数自体を実装しない
(「実装しない」を運用ルールではなく構造で担保する)。

Pending Decision Unitの永続化先はdata/decisions/decision_ledger.jsonl
(確定済みDecisionのみを記録する既存台帳、governance/seal_governance_gate.py
参照)とは分離し、data/decisions/pending_decision_units.jsonlへ記録する。
理由: WAITING状態は「まだ決定していない」ことを表し、決定済み記録である
Decision Ledgerに混在させるとapproved/abortedのみを前提とする既存の
集計・監査ロジックの意味が壊れるため。
"""
import json
import uuid
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_GOVERNANCE_DIR = Path(__file__).resolve().parent
_MOCKA_ROOT = _GOVERNANCE_DIR.parent

PENDING_LEDGER_PATH = _MOCKA_ROOT / "data" / "decisions" / "pending_decision_units.jsonl"
MCP_HEALTH_URL = "http://localhost:5002/health"

GOVERNANCE_STATES = {"WAITING_FOR_HUMAN_GATE"}
MCP_AVAILABILITY_VALUES = {"ONLINE", "OFFLINE", "UNKNOWN"}
HUMAN_GATE_EVENT_STATUS_VALUES = {"NOT_ISSUED"}


class HumanGateContinuityError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass
class PendingDecisionUnit:
    request_id: str
    execution_id: str
    change_start: str
    change_scope: list
    wait_reason: str
    governance_state: str
    approval_required: bool
    human_gate_event_status: str
    mcp_availability: str
    recorded_at: str
    observations: list = field(default_factory=list)


def check_mcp_availability(url: str = MCP_HEALTH_URL, timeout: float = 3.0) -> str:
    """MCPサーバーの可用性のみを確認する。到達可否の観測に限定し、
    到達できた場合でもHuman Gateへの接続・状態遷移は一切行わない。"""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return "ONLINE" if resp.status == 200 else "UNKNOWN"
    except (urllib.error.URLError, OSError, TimeoutError):
        return "OFFLINE"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _next_execution_id() -> str:
    return f"EXEC_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"


class HumanGateContinuity:
    """
    Deferred Human Gate Protocol の縮小実装。

    pending_ledger_pathはテスト時にsandbox pathへ差し替え可能。
    mcp_checkはテスト用フックで、Noneの場合は実際にcheck_mcp_availability()を
    呼ぶ(本番動作)。
    """

    def __init__(self, pending_ledger_path: Path = PENDING_LEDGER_PATH):
        self.pending_ledger_path = Path(pending_ledger_path)

    def _append(self, entry: dict) -> None:
        self.pending_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.pending_ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _read_all(self) -> list:
        if not self.pending_ledger_path.exists():
            return []
        with self.pending_ledger_path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def defer(self, change_scope: list, wait_reason: str, mcp_check=None) -> PendingDecisionUnit:
        """
        Core File変更要求をWAITING_FOR_HUMAN_GATE状態のPending Decision Unit
        として記録する。承認・却下のいずれの判断も行わない(判断の記録ではなく
        「まだ判断されていない」ことの記録)。
        """
        checker = mcp_check or check_mcp_availability
        mcp_availability = checker()

        unit = PendingDecisionUnit(
            request_id=f"PDU_{_next_execution_id()}",
            execution_id=_next_execution_id(),
            change_start=_now_iso(),
            change_scope=list(change_scope),
            wait_reason=wait_reason,
            governance_state="WAITING_FOR_HUMAN_GATE",
            approval_required=True,
            human_gate_event_status="NOT_ISSUED",
            mcp_availability=mcp_availability,
            recorded_at=_now_iso(),
        )
        self._append({
            "record_type": "PENDING_DECISION_UNIT",
            "request_id": unit.request_id,
            "execution_id": unit.execution_id,
            "change_start": unit.change_start,
            "change_scope": unit.change_scope,
            "wait_reason": unit.wait_reason,
            "governance_state": unit.governance_state,
            "approval_required": unit.approval_required,
            "human_gate_event_status": unit.human_gate_event_status,
            "mcp_availability": unit.mcp_availability,
            "recorded_at": unit.recorded_at,
        })
        return unit

    def get_state(self, request_id: str) -> dict | None:
        """request_idに対応する最新状態(元のdeferレコード + 観測イベント)を返す。
        governance_stateは常にWAITING_FOR_HUMAN_GATEのまま(本モジュールには
        それ以外の値へ遷移させる経路が存在しない)。"""
        records = [r for r in self._read_all() if r.get("request_id") == request_id]
        if not records:
            return None
        base = next(r for r in records if r["record_type"] == "PENDING_DECISION_UNIT")
        observations = [r for r in records if r["record_type"] == "MCP_RECOVERY_OBSERVED"]
        result = dict(base)
        result["observations"] = observations
        if observations:
            result["mcp_availability"] = observations[-1]["mcp_availability"]
        return result

    def record_mcp_recovery_observed(self, request_id: str, mcp_check=None) -> dict:
        """
        MCP可用性の変化を観測・記録するだけの関数。governance_stateには
        一切触れない。ここでWAITING_FOR_HUMAN_GATEから先へ進めるための
        コードは存在しない(TODO_429の裁定が出るまでの意図的な境界)。
        """
        current = self.get_state(request_id)
        if current is None:
            raise HumanGateContinuityError(f"request_id not found: {request_id}")
        if current["governance_state"] != "WAITING_FOR_HUMAN_GATE":
            raise HumanGateContinuityError(
                f"unexpected governance_state for observation: {current['governance_state']}"
            )

        checker = mcp_check or check_mcp_availability
        mcp_availability = checker()

        event = {
            "record_type": "MCP_RECOVERY_OBSERVED",
            "request_id": request_id,
            "mcp_availability": mcp_availability,
            "governance_state": "WAITING_FOR_HUMAN_GATE",
            "note": "MCP可用性の観測のみ。Human Gate再接続・resumeはTODO_429の裁定待ち、本関数では実施しない",
            "observed_at": _now_iso(),
        }
        self._append(event)
        return event

    def attempt_state_transition(self, request_id: str, target_state: str) -> None:
        """
        governance_stateをWAITING_FOR_HUMAN_GATE以外へ書き換えようとする
        あらゆる試みを拒否する。APPROVED/READY_TO_COMMIT等、Human Gateの
        実際の承認機構(phi_os/human_gate.py等)を経由しない状態遷移は、
        呼び出し元が誰であっても常にHumanGateContinuityErrorとする。
        """
        current = self.get_state(request_id)
        if current is None:
            raise HumanGateContinuityError(f"request_id not found: {request_id}")
        raise HumanGateContinuityError(
            f"illegal override rejected: governance_state cannot be advanced from "
            f"WAITING_FOR_HUMAN_GATE to '{target_state}' by human_gate_continuity.py. "
            f"State advancement requires TODO_429's Human Gate reconnect design "
            f"(not yet decided) and an actual human_gate.py approve() event."
        )

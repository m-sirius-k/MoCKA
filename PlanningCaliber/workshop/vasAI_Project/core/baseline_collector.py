"""
vasAI L5 Baseline Collector
L4.9フェーズ中からL5証拠を自動蓄積する。

収集指標:
1. Onboarding Time      新担当者の戦力化時間
2. Knowledge Recovery   過去判断の発見時間
3. Decision Reproducibility  同条件での再現率
4. Institutional Memory Retention  全員交代後の組織知残存率
"""
import json
import hashlib
import threading
from datetime import datetime, timezone
from pathlib import Path

_lock = threading.Lock()
_DEFAULT_BASELINE = Path(__file__).parent.parent / "data" / "baseline_l5.json"


def _baseline_path() -> Path:
    import os
    p = os.environ.get("VASAI_BASELINE_PATH", str(_DEFAULT_BASELINE))
    return Path(p)


def _load() -> dict:
    p = _baseline_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "onboarding_records": [],
        "knowledge_recovery_records": [],
        "reproducibility_records": [],
        "memory_retention_records": [],
    }


def _save(data: dict) -> None:
    p = _baseline_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class BaselineCollector:
    def record_onboarding(
        self,
        user_id: str,
        started_at: str,
        first_success_at: str,
    ) -> None:
        fmt = "%Y-%m-%dT%H:%M:%S"
        try:
            s = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            e = datetime.fromisoformat(first_success_at.replace("Z", "+00:00"))
            elapsed_min = (e - s).total_seconds() / 60
        except Exception:
            elapsed_min = -1

        record = {
            "user_id": user_id,
            "started_at": started_at,
            "first_success_at": first_success_at,
            "elapsed_minutes": round(elapsed_min, 2),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            data = _load()
            data["onboarding_records"].append(record)
            _save(data)

    def record_knowledge_recovery(
        self,
        query: str,
        found_at: str,
        elapsed_sec: float,
    ) -> None:
        record = {
            "query": query,
            "found_at": found_at,
            "elapsed_sec": round(elapsed_sec, 3),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            data = _load()
            data["knowledge_recovery_records"].append(record)
            _save(data)

    def record_decision_reproducibility(
        self,
        original_id: str,
        reproduced_id: str,
        match_rate: float,
    ) -> None:
        record = {
            "original_id": original_id,
            "reproduced_id": reproduced_id,
            "match_rate": round(match_rate, 4),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            data = _load()
            data["reproducibility_records"].append(record)
            _save(data)

    def record_memory_retention(
        self,
        scenario: str,
        turnover_rate: float,
        retention_rate: float,
    ) -> None:
        record = {
            "scenario": scenario,
            "turnover_rate": round(turnover_rate, 4),
            "retention_rate": round(retention_rate, 4),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            data = _load()
            data["memory_retention_records"].append(record)
            _save(data)

    def generate_baseline_report(self) -> dict:
        with _lock:
            data = _load()

        ob = data["onboarding_records"]
        kr = data["knowledge_recovery_records"]
        rp = data["reproducibility_records"]
        mr = data["memory_retention_records"]

        avg_onboarding = (
            sum(r["elapsed_minutes"] for r in ob) / len(ob) if ob else None
        )
        avg_recovery = (
            sum(r["elapsed_sec"] for r in kr) / len(kr) if kr else None
        )
        avg_match = (
            sum(r["match_rate"] for r in rp) / len(rp) if rp else None
        )
        avg_retention = (
            sum(r["retention_rate"] for r in mr) / len(mr) if mr else None
        )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "onboarding_avg_minutes": round(avg_onboarding, 2) if avg_onboarding else None,
                "knowledge_recovery_avg_sec": round(avg_recovery, 3) if avg_recovery else None,
                "decision_reproducibility_avg": round(avg_match, 4) if avg_match else None,
                "memory_retention_avg": round(avg_retention, 4) if avg_retention else None,
            },
            "sample_counts": {
                "onboarding": len(ob),
                "knowledge_recovery": len(kr),
                "reproducibility": len(rp),
                "memory_retention": len(mr),
            },
            "l5_readiness": self._assess_l5_readiness(
                avg_onboarding, avg_recovery, avg_match, avg_retention
            ),
        }

    def _assess_l5_readiness(self, onboarding, recovery, match, retention) -> str:
        if all(v is None for v in (onboarding, recovery, match, retention)):
            return "COLLECTING"
        ready = 0
        if onboarding is not None and onboarding <= 60:
            ready += 1
        if recovery is not None and recovery <= 30:
            ready += 1
        if match is not None and match >= 0.9:
            ready += 1
        if retention is not None and retention >= 0.8:
            ready += 1
        if ready == 4:
            return "L5_READY"
        return f"COLLECTING ({ready}/4 metrics met)"

    def export_for_l5(self) -> str:
        report = self.generate_baseline_report()
        with _lock:
            data = _load()
        export = {**data, "baseline_report": report}
        payload = json.dumps(export, ensure_ascii=False, sort_keys=True)
        h = hashlib.sha256(payload.encode()).hexdigest()
        return json.dumps(
            {"export": export, "hash": f"sha256:{h}"},
            indent=2,
            ensure_ascii=False,
        )

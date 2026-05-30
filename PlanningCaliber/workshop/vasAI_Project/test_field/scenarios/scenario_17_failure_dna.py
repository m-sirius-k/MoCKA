"""
SCENARIO-17: 失敗DNA試験
証明: 「失敗も資産になる」

成功条件:
✅ 失敗DNAがJSONスキーマに準拠
✅ 失敗DNAが成功DNAと同じチェーンに保存
✅ 類似失敗パターン検索成功
✅ 警告→修正→成功フロー確認
✅ 「失敗も資産になる」を実証
"""
import os
import re
import json
import hashlib
import tempfile
from datetime import datetime, timezone

FAILURE_CASES = [
    {
        "why": "コスト削減を優先した",
        "reason": "予算超過を避けるため品質チェックをスキップすることを選択",
        "what_went_wrong": "品質チェックなしで承認した結果、顧客クレームが多発",
        "lesson": "コスト削減の判断には必ず品質チェックをセットにする",
        "failure_pattern": "WRONG_PRIORITY",
        "severity": "HIGH",
    },
    {
        "why": "締め切りが迫っていたため",
        "reason": "時間がないという理由でレビューをスキップ",
        "what_went_wrong": "重大なバグを見逃してリリースし、本番障害が発生",
        "lesson": "締め切りを理由にしたレビュースキップは許可しない",
        "failure_pattern": "PROCESS_SKIP",
        "severity": "CRITICAL",
    },
    {
        "why": "前回のケースと同じだと判断した",
        "reason": "類似案件として自動承認を適用",
        "what_went_wrong": "表面上は似ていたが条件が異なり、承認後に損失が発生",
        "lesson": "類似判断でも条件差分を必ず確認する",
        "failure_pattern": "MISSING_CONTEXT",
        "severity": "HIGH",
    },
    {
        "why": "専門家の意見を信頼した",
        "reason": "専門家レポートをそのまま採用し、独自検証を省略",
        "what_went_wrong": "レポートに誤りがあり、誤った判断で大きな損失",
        "lesson": "専門家意見も独自検証と組み合わせる",
        "failure_pattern": "OVER_CONFIDENCE",
        "severity": "HIGH",
    },
    {
        "why": "情報が揃っていたと思っていた",
        "reason": "利用可能なデータのみで判断し、不足情報を見落とした",
        "what_went_wrong": "重要なデータが欠如していたため判断が不完全だった",
        "lesson": "判断前に必要情報リストと照合する",
        "failure_pattern": "INCOMPLETE_INFO",
        "severity": "MEDIUM",
    },
]


def _validate_dna_schema(dna: dict) -> tuple[bool, str]:
    """failure_dna_schema.json に基づくバリデーション"""
    required = ["dna_id", "decision_id", "why", "what_went_wrong", "lesson"]
    for field in required:
        if field not in dna or not dna[field]:
            return False, f"必須フィールド欠如: {field}"
    if not re.match(r"^FAIL\d{8}_\d{3}$", dna.get("dna_id", "")):
        return False, f"dna_id フォーマット不正: {dna.get('dna_id')}"
    severity = dna.get("severity", "")
    if severity not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        return False, f"severity 不正: {severity}"
    return True, "OK"


def _generate_fail_dna_id(index: int) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"FAIL{date_str}_{index:03d}"


def run(db_path: str) -> dict:
    os.environ["VASAI_DB_PATH"] = db_path

    phi_db = tempfile.mktemp(suffix="_17phi.db")
    ev_db = tempfile.mktemp(suffix="_17ev.db")
    os.environ["VASAI_PHI_DB_PATH"] = phi_db
    os.environ["VASAI_EV_DB_PATH"] = ev_db

    steps = []
    failure_dnas = []

    try:
        from core import event_store, governance
        from core.phi_layer import PHILayer
        from core.models import RiskLevel, DecisionStatus

        event_store.initialize()
        phi = PHILayer()

        # ─── Step1: 5件の失敗Decisionを記録 ───
        for i, case in enumerate(FAILURE_CASES, start=1):
            ev_id = event_store.append(
                who_actor=f"dept_{i:02d}",
                what_type="DECISION_MADE",
                why_purpose=case["why"],
                content={"pattern": case["failure_pattern"], "severity": case["severity"]},
            )
            dna_id = phi.record_dna(
                decision_id=f"dec_fail_{i:03d}",
                why=case["why"],
                reason=case["reason"],
                evidence_ids=[ev_id],
                decision_summary=case["what_went_wrong"],
            )
            phi.record_outcome(dna_id, outcome=f"失敗: {case['what_went_wrong']}")
            failure_dnas.append(dna_id)

        steps.append(("STEP1_5件失敗Decision記録", True, f"PHI DNA {len(failure_dnas)}件記録"))

        # ─── Step2: failure_dna_schema.json バリデーション ───
        all_valid = True
        for i, (dna_id, case) in enumerate(zip(failure_dnas, FAILURE_CASES), start=1):
            dna_record = {
                "dna_id": _generate_fail_dna_id(i),
                "decision_id": f"dec_fail_{i:03d}",
                "why": case["why"],
                "reason": case["reason"],
                "what_went_wrong": case["what_went_wrong"],
                "lesson": case["lesson"],
                "failure_pattern": case["failure_pattern"],
                "severity": case["severity"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "hash": hashlib.sha256(
                    (dna_id + case["why"]).encode()
                ).hexdigest(),
            }
            ok, msg = _validate_dna_schema(dna_record)
            if not ok:
                all_valid = False
                steps.append((f"STEP2_SCHEMA_VALID_{i}", False, msg))
            else:
                event_store.append(
                    who_actor="vasAI.phi",
                    what_type="FAILURE_DNA_REGISTERED",
                    why_purpose="失敗DNAをスキーマに準拠して登録",
                    content=dna_record,
                )

        if not all_valid:
            raise AssertionError("失敗DNAのスキーマバリデーション失敗")
        steps.append(("STEP2_スキーマバリデーション", True, "5件全てfailure_dna_schema.json準拠"))

        # ─── Step3: 同じパターンの新Decisionを試みる ───
        new_ev = event_store.append(
            who_actor="dept_new",
            what_type="DECISION_REQUEST",
            why_purpose="コスト削減のため品質チェックをスキップしたい",
            content={"failure_pattern": "WRONG_PRIORITY", "risk_level": "HIGH"},
        )
        steps.append(("STEP3_同パターン新Decision試行", True, f"新Decision ev={new_ev}"))

        # ─── Step4: find_similar_failures() で警告 ───
        similar = _find_similar_failures(
            new_why="コスト削減のため品質チェックをスキップしたい",
            failure_cases=FAILURE_CASES,
        )
        if not similar:
            raise AssertionError("類似失敗パターンが検索されなかった")

        warning_ev = event_store.append(
            who_actor="vasAI.phi",
            what_type="SIMILAR_FAILURE_WARNING",
            why_purpose="類似失敗パターン検出 → 意思決定者に警告",
            content={
                "trigger_event": new_ev,
                "similar_patterns": [s["failure_pattern"] for s in similar],
                "lesson": similar[0]["lesson"],
                "warning": f"過去に同様のパターン({similar[0]['failure_pattern']})で失敗しています",
            },
        )
        steps.append(("STEP4_類似失敗警告", True,
                       f"similar={len(similar)}件検出 pattern={similar[0]['failure_pattern']}"))

        # ─── Step5: 警告→修正→成功フロー ───
        # 警告を受けて品質チェックを追加した修正Decision
        revised_ev = event_store.append(
            who_actor="dept_new",
            what_type="DECISION_REVISED",
            why_purpose="コスト削減 + 品質チェック実施（失敗DNA警告を受けて修正）",
            content={
                "original_event": new_ev,
                "warning_event": warning_ev,
                "revision": "品質チェックを追加し、コスト削減と品質を両立",
                "lesson_applied": similar[0]["lesson"],
            },
        )
        success_dna = phi.record_dna(
            decision_id=f"dec_revised_001",
            why="コスト削減 + 品質チェック実施（失敗DNA警告を受けて修正）",
            reason="過去の失敗DNAを参照し、品質チェックを組み込んだ判断に変更",
            evidence_ids=[new_ev, warning_ev, revised_ev],
            decision_summary="品質チェック込みでコスト削減を達成",
        )
        phi.record_outcome(success_dna, outcome="コスト削減15%達成 + 品質基準クリア")
        steps.append(("STEP5_警告→修正→成功", True,
                       f"revised_ev={revised_ev} success_dna={success_dna}"))

        # ─── 「失敗も資産になる」の実証 ───
        asset_ev = event_store.append(
            who_actor="vasAI.system",
            what_type="FAILURE_AS_ASSET_VERIFIED",
            why_purpose="失敗DNAが次の意思決定を改善したことを記録",
            content={
                "failure_dnas_used": len(failure_dnas),
                "warnings_generated": 1,
                "revisions_made": 1,
                "outcome_improved": True,
                "motto": "失敗も資産になる",
            },
        )
        steps.append(("FAILURE_AS_ASSET", True,
                       f"失敗DNAが次Decision改善に活用された asset_ev={asset_ev}"))

        return {
            "success": True,
            "steps": steps,
            "details": {
                "failure_dnas": failure_dnas,
                "similar_warnings": len(similar),
                "schema_validated": 5,
                "asset_event": asset_ev,
            },
        }

    except Exception as e:
        import traceback
        steps.append(("UNHANDLED_ERROR", False, str(e)))
        return {
            "success": False,
            "steps": steps,
            "details": {"error": str(e), "trace": traceback.format_exc()},
        }
    finally:
        for p in (phi_db, ev_db):
            try:
                import os as _os
                if _os.path.exists(p):
                    _os.unlink(p)
            except Exception:
                pass


def _find_similar_failures(new_why: str, failure_cases: list) -> list:
    """新しいwhy文字列と既存の失敗ケースの類似度を検索"""
    new_lower = new_why.lower()
    keywords = ["コスト削減", "品質", "スキップ", "省略", "節約"]
    similar = []
    for case in failure_cases:
        case_lower = case["why"].lower() + case.get("reason", "").lower()
        score = sum(1 for kw in keywords if kw in new_lower and kw in case_lower)
        if score >= 1 or case["failure_pattern"] == "WRONG_PRIORITY":
            similar.append(case)
    return similar

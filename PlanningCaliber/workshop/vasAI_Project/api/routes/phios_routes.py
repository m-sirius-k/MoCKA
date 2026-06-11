"""
vasAI API: PHI-OS フィードバックエンドポイント
PHI-OS（PlanningCaliber/workshop/phi-os/phi_os.py）からの sync('vasai') を受け取り、
PHI DNAとして記録した上でループ継続/停止のfeedbackを返す。
TODO_299
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("phios", __name__)


def _phi():
    from core.phi_layer import PHILayer
    return PHILayer()


@bp.post("/phios/feedback")
def feedback():
    """
    PHI-OSからのview（generate_view('fusion')の結果）を受け取り、
    PHI DNAとして記録し、ループ継続要否を返す。

    request body:
      {
        "node_id": "phi-os-...-...-001",
        "view_type": "fusion",
        "decision_id": "...",
        "why": "...",
        "reason": "...",
        "decision_summary": "...",
        "outcome": "..."  # 任意。設定済みならSTABLE判定の材料になる
      }

    response body:
      { "status": "STABLE" | "CONTINUE", "dna_id": "...", "reason": "..." }
    """
    data = request.get_json(force=True) or {}

    decision_id = data.get("decision_id") or ""
    why = data.get("why") or ""
    reason = data.get("reason") or ""
    decision_summary = data.get("decision_summary") or ""
    outcome = data.get("outcome") or ""

    if not decision_id:
        return jsonify({"error": "decision_id required"}), 400

    phi = _phi()
    dna_id = phi.record_dna(
        decision_id=decision_id,
        why=why,
        reason=reason,
        evidence_ids=data.get("evidence_ids", []),
        decision_summary=decision_summary,
    )
    if outcome:
        phi.record_outcome(dna_id, outcome)

    # 安定判定: outcomeが記録されている（=判断が完結している）場合のみSTABLE。
    # それ以外はCONTINUE（PHI-OS側で再構成し、再度fusion viewとして投入）。
    if outcome:
        return jsonify({
            "status": "STABLE",
            "dna_id": dna_id,
            "reason": "outcome recorded",
        })

    return jsonify({
        "status": "CONTINUE",
        "dna_id": dna_id,
        "reason": "outcome not yet recorded",
    })

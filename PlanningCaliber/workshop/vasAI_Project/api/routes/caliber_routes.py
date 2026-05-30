from flask import Blueprint, jsonify, request

from caliber import base_caliber

bp = Blueprint("caliber", __name__)


@bp.get("/calibers")
def list_calibers():
    reg = base_caliber.get_registry()
    return jsonify({
        "calibers": [
            {"id": cid, "class": type(c).__name__}
            for cid, c in reg.items()
        ]
    })


@bp.post("/calibers/register")
def register_caliber():
    data = request.get_json(force=True) or {}
    caliber_id = data.get("caliber_id", "")
    # 動的登録は本番では実装しない（セキュリティ上）
    # ここではデフォルトcaliberを自動登録するデモ
    from caliber.example_medical import MedicalCALIBER
    from caliber.example_finance import FinanceCALIBER
    base_caliber.register(MedicalCALIBER())
    base_caliber.register(FinanceCALIBER())
    return jsonify({"registered": list(base_caliber.get_registry().keys())}), 201


@bp.post("/calibers/<caliber_id>/process")
def process_caliber(caliber_id):
    reg = base_caliber.get_registry()
    if caliber_id not in reg:
        return jsonify({"error": f"Caliber not found: {caliber_id}"}), 404
    data = request.get_json(force=True) or {}
    caliber = reg[caliber_id]
    result = caliber.process_intranet_request(data)
    return jsonify(result)

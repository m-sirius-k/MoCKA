from flask import Blueprint, jsonify

from core import audit_chain

bp = Blueprint("audit", __name__)


@bp.get("/audit/verify")
def verify():
    report = audit_chain.verify_chain()
    return jsonify(report.model_dump(mode="json"))


@bp.post("/audit/seal")
def seal():
    sig = audit_chain.seal()
    return jsonify({"seal_signature": sig, "status": "sealed"}), 201


@bp.get("/audit/report")
def report():
    r = audit_chain.verify_chain()
    return jsonify(r.model_dump(mode="json"))

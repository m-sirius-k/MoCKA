"""
社内イントラネット模擬サーバー (port: 6100)
3業種の社内APIをFlaskでモック。
スタンドアロン実行: python mock_intranet.py
"""
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# ── 医療 ──────────────────────────────────────────────────
MOCK_MEDICAL_RECORDS = [
    {"patient_id": "P001", "event_type": "treatment",
     "description": "血圧管理 処置判断", "physician": "山田先生", "department": "cardiology"},
    {"patient_id": "P002", "event_type": "note",
     "description": "定期問診", "physician": "鈴木先生", "department": "general"},
]

@app.get("/medical/records")
def get_medical_records():
    return jsonify({"records": MOCK_MEDICAL_RECORDS, "count": len(MOCK_MEDICAL_RECORDS)})

@app.post("/medical/records")
def post_medical_records():
    data = request.get_json(force=True) or {}
    return jsonify({"status": "written_back", "record_id": data.get("record_id", ""),
                    "received_at": datetime.now(timezone.utc).isoformat()})

# ── 金融 ──────────────────────────────────────────────────
MOCK_TRANSACTIONS = [
    {"transaction_type": "transfer", "amount": 500000, "currency": "JPY",
     "from_account": "1234-5678", "to_account": "9876-5432"},
    {"transaction_type": "transfer", "amount": 50000000, "currency": "JPY",
     "from_account": "1111-2222", "to_account": "3333-4444"},
]

@app.get("/finance/transactions")
def get_transactions():
    return jsonify({"transactions": MOCK_TRANSACTIONS, "count": len(MOCK_TRANSACTIONS)})

@app.post("/finance/decisions")
def post_finance_decision():
    data = request.get_json(force=True) or {}
    return jsonify({"status": "decision_recorded", "transaction_id": data.get("transaction_id", ""),
                    "received_at": datetime.now(timezone.utc).isoformat()})

# ── 製造 ──────────────────────────────────────────────────
MOCK_MES_DATA = [
    {"equipment_id": "EQ-001", "event_type": "sensor_data",
     "sensor_value": 98.5, "line_id": "LINE-A"},
    {"equipment_id": "EQ-002", "event_type": "equipment_stop",
     "sensor_value": 0.0, "line_id": "LINE-B"},
]

@app.get("/manufacturing/mes")
def get_mes():
    return jsonify({"equipment": MOCK_MES_DATA, "count": len(MOCK_MES_DATA)})

@app.post("/manufacturing/action")
def post_manufacturing_action():
    data = request.get_json(force=True) or {}
    return jsonify({"status": "action_sent", "equipment_id": data.get("equipment_id", ""),
                    "action": data.get("line_action", "CONTINUE"),
                    "received_at": datetime.now(timezone.utc).isoformat()})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "mock_intranet", "port": 6100})

if __name__ == "__main__":
    print("mock_intranet starting on port 6100...")
    app.run(host="0.0.0.0", port=6100, debug=False)

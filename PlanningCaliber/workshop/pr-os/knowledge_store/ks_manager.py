"""
Knowledge Store Manager
KS_NNN発番・レコード管理・ステータス更新
"""
import json
import os
from datetime import datetime, timezone

KS_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(KS_DIR, "index.json")
CONFIRMED_DIR = os.path.join(KS_DIR, "confirmed")
DRAFT_DIR = os.path.join(KS_DIR, "draft")


def _load_index() -> dict:
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_index(data: dict):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_ks_id(index: dict) -> str:
    """次のKS_NNN IDを発番"""
    counter = index.get("counter", 0) + 1
    return f"KS_{counter:03d}", counter


def create_record(title: str, source_type: str = "manual_input",
                  tags: list = None, category: str = "") -> dict:
    """
    ドラフトレコードを作成してDRAFTフォルダに保存。
    Returns: 作成したレコード
    """
    index = _load_index()
    ks_id, counter = next_ks_id(index)
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "id": ks_id,
        "title": title,
        "created_at": now,
        "confirmed_at": None,
        "status": "draft",
        "tags": tags or [],
        "category": category,
        "source_type": source_type,
        "ai_gate_log": {
            "score": None,
            "corrections": 0,
            "integrity_pass": False
        },
        "publish_status": {
            "wordpress": "not_set",
            "x": "not_set",
            "instagram": "not_set",
            "github_pages": "not_set",
            "newsletter": "not_set"
        },
        "files": {
            "original": f"draft/{ks_id}_raw.txt",
            "confirmed": None,
            "wordpress": None,
            "x_post": None
        }
    }

    # インデックス更新
    index["counter"] = counter
    index["last_updated"] = now
    index["records"].append(record)
    _save_index(index)

    print(f"[KS] Created: {ks_id} - {title}")
    return record


def confirm_record(ks_id: str, score: float, corrections: int,
                   integrity_pass: bool) -> dict:
    """
    ドラフトレコードを確定済みに昇格。
    スコア閾値 0.8 以上のみ自動確定。
    """
    index = _load_index()
    now = datetime.now(timezone.utc).isoformat()

    for rec in index["records"]:
        if rec["id"] == ks_id:
            if score < 0.6:
                rec["status"] = "rejected"
                print(f"[KS] {ks_id} REJECTED (score={score})")
            elif score < 0.8:
                rec["status"] = "pending_approval"
                print(f"[KS] {ks_id} PENDING APPROVAL (score={score})")
            else:
                rec["status"] = "confirmed"
                rec["confirmed_at"] = now
                rec["files"]["confirmed"] = f"confirmed/{ks_id}.md"
                print(f"[KS] {ks_id} CONFIRMED (score={score})")

            rec["ai_gate_log"] = {
                "score": score,
                "corrections": corrections,
                "integrity_pass": integrity_pass
            }
            index["last_updated"] = now
            _save_index(index)
            return rec

    raise ValueError(f"Record not found: {ks_id}")


def update_publish_status(ks_id: str, adapter: str, status: str):
    """媒体別公開ステータスを更新"""
    index = _load_index()
    now = datetime.now(timezone.utc).isoformat()
    for rec in index["records"]:
        if rec["id"] == ks_id:
            rec["publish_status"][adapter] = status
            index["last_updated"] = now
            _save_index(index)
            print(f"[KS] {ks_id} publish_status[{adapter}] = {status}")
            return
    raise ValueError(f"Record not found: {ks_id}")


def get_record(ks_id: str) -> dict:
    """IDでレコードを取得"""
    index = _load_index()
    for rec in index["records"]:
        if rec["id"] == ks_id:
            return rec
    raise ValueError(f"Record not found: {ks_id}")


def list_records(status: str = None) -> list:
    """全レコード一覧（statusフィルタ可）"""
    index = _load_index()
    records = index["records"]
    if status:
        records = [r for r in records if r["status"] == status]
    return records


if __name__ == "__main__":
    # 動作確認
    rec = create_record("テスト記事", tags=["test"], category="development")
    print(json.dumps(rec, ensure_ascii=False, indent=2))

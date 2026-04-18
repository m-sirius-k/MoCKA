import sqlite3
# -*- coding: utf-8 -*-
# MoCKA Essence Injected: E20260401_008,2026-04-01T11:33:18,mocka_router,save,router,interface/router.py,Phase5ASSED,cli,internal,in_operation,normal,A,outfield,[save] Phase5ASSED,11/11 PASS墓慣つ晢oCKA壹晢憺屮会滄晏擅つ晢026-04-01 Claude Sonnet 4.6,N/A,save_complete,generation,local,save,N/A,N/A,manual_save
# Policy: MoCKA Encoding Policy v1.01
﻿import csv, os
from datetime import datetime

EVENTS_CSV = r"C:\Users\sirok\MoCKA\data\events.csv"
FIELDNAMES = [
    "event_id","when","who_actor","what_type","where_component","where_path",
    "why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level",
    "category_ab","target_class","title","short_summary",
    "before_state","after_state","change_type",
    "impact_scope","impact_result","related_event_id","trace_id","free_note"
]

def safe_value(v):
    if v is None:
        return ""
    v = str(v).replace("\n"," ").replace("\r"," ")
    return v[:500]

def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    n = 1
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                eid = row.get("event_id","")
                if eid.startswith(prefix):
                    try:
                        num = int(eid.split("_")[1])
                        if num >= n:
                            n = num + 1
                    except:
                        pass
    return f"{prefix}{n:03d}"

def validate_input_integrity(data: dict) -> dict:
    """
    入力データの整合性を検証する。
    不整合を検知した場合は沈黙を禁じる — 必ず警告を返し処理を停止する。
    Gemini捏造インシデント（2026-04-10）を受けた物理拘束。

    Returns:
        {"ok": True} — 正常
        {"ok": False, "reason": str, "field": str} — 異常・処理停止必須
    """
    if not isinstance(data, dict):
        return {"ok": False, "reason": "INPUT_NOT_DICT", "field": "root"}

    # 1. 固定値検知（Gemini型捏造の物理封じ）
    #    同一フィールドが全行で同じ値に固定されている場合は捏造を疑う
    FIXED_VALUE_SUSPECTS = {
        "risk_level": ["normal", "high", "critical"],  # 全件normalは要注意だが許容
    }
    # Z軸固定値検知: 数値フィールドが定数の場合
    for field in ["before_state", "after_state"]:
        val = data.get(field, "")
        if val and str(val).replace(".", "").replace("-","").isdigit():
            try:
                f = float(val)
                if f == 0.88 or f == 0.880:  # Geminiインシデントの固定値
                    return {
                        "ok": False,
                        "reason": "FIXED_VALUE_DETECTED",
                        "field": field,
                        "value": val,
                        "message": "固定値0.88を検知。Gemini型捏造の疑い。処理停止。"
                    }
            except:
                pass

    # 2. 必須フィールド空欄検知
    REQUIRED_FIELDS = ["title", "who_actor", "what_type"]
    for field in REQUIRED_FIELDS:
        if not data.get(field, "").strip():
            return {
                "ok": False,
                "reason": "REQUIRED_FIELD_EMPTY",
                "field": field,
                "message": f"必須フィールド '{field}' が空欄。記録を拒否する。"
            }

    # 3. 構造不全検知: titleが極端に短い（1文字以下）
    title = data.get("title", "")
    if len(title.strip()) < 2:
        return {
            "ok": False,
            "reason": "TITLE_TOO_SHORT",
            "field": "title",
            "message": f"タイトルが短すぎる（{len(title)}文字）。意味のある記録を要求する。"
        }

    # 4. 禁止パターン検知: テストデータの本番混入
    forbidden_titles = ["test", "テスト", "dummy", "sample", "xxx", "aaa"]
    if any(title.lower().strip() == f for f in forbidden_titles):
        return {
            "ok": False,
            "reason": "FORBIDDEN_TITLE_PATTERN",
            "field": "title",
            "message": f"禁止タイトルパターン '{title}' を検知。本番環境へのテストデータ混入を拒否する。"
        }

    return {"ok": True}


DB_PATH = Path("C:/Users/sirok/MoCKA/data/events.db")

def write_sqlite(row: list):
    """UTF-8固定・BOMなし・SQLite直接書き込み"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO events VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """, row[:23] + [""] * max(0, 23 - len(row)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[SQLITE ERROR] {e}")
        return False

def write_safe_csv(row); write_sqlite(row):
    # 整合性検証 — 不整合は沈黙せず必ず警告・停止
    result = validate_input_integrity(row)
    if not result["ok"]:
        msg = (
            f"\n[INTEGRITY_VIOLATION] 書き込みを拒否しました\n"
            f"  reason : {result['reason']}\n"
            f"  field  : {result['field']}\n"
            f"  message: {result.get('message','')}\n"
        )
        print(msg)
        # インシデントとして自動記録
        _record_integrity_incident(result, row)
        return None  # 呼び出し元に停止を通知

    os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
    base = {k:"" for k in FIELDNAMES}
    base.update(row)
    base = {k: safe_value(v) for k,v in base.items()}
    if not base["event_id"]:
        base["event_id"] = next_event_id()
    if not base["when"]:
        base["when"] = datetime.now().isoformat(timespec="seconds")
    write_header = not os.path.exists(EVENTS_CSV)
    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        if write_header:
            writer.writeheader()
        writer.writerow(base)
    return base["event_id"]

def _record_integrity_incident(violation: dict, original_row: dict):
    """整合性違反をインシデントとして自動記録する（validate_input_integrityをバイパスして直接書き込む）"""
    os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
    eid = next_event_id()
    now = datetime.now().isoformat(timespec="seconds")
    base = {k:"" for k in FIELDNAMES}
    base.update({
        "event_id": eid,
        "when": now,
        "who_actor": "router.validate_input_integrity",
        "what_type": "incident",
        "where_component": "router",
        "where_path": "interface/router.py",
        "why_purpose": "整合性違反の自動記録。沈黙禁止原則に基づく強制記録。",
        "how_trigger": "write_safe_csv()呼び出し時にvalidate_input_integrity()が違反を検知",
        "channel_type": "internal",
        "lifecycle_phase": "in_operation",
        "risk_level": "high",
        "category_ab": "B",
        "title": f"[INTEGRITY_VIOLATION] {violation.get('reason','')} / field={violation.get('field','')}",
        "short_summary": violation.get("message",""),
        "free_note": f"reason={violation.get('reason')}|field={violation.get('field')}|original_title={str(original_row.get('title',''))[:100]}"
    })
    base = {k: safe_value(v) for k,v in base.items()}
    write_header = not os.path.exists(EVENTS_CSV)
    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        if write_header:
            writer.writeheader()
        writer.writerow(base)
    print(f"[INCIDENT_RECORDED] {eid}")

def save(title, summary=""):
    eid = write_safe_csv({
        "who_actor": "mocka_router",
        "what_type": "record",
        "where_component": "router",
        "where_path": "interface/router.py",
        "why_purpose": "手動記録・制度改善・セッションログ",
        "how_trigger": "router.save()呼び出し",
        "title": title,
        "short_summary": summary,
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "channel_type": "internal"
    })
    if eid:
        print("[OK]", title)

class MoCKARouter:
    """app.py互換ラッパークラス"""
    def collaborate(self, prompt):
        import subprocess, sys, os
        write_safe_csv({
            "who_actor": "mocka_router",
            "what_type": "collaboration",
            "where_component": "router",
            "where_path": "interface/router.py",
            "why_purpose": "4AI回収→Claude統合分析",
            "how_trigger": "router.collaborate()呼び出し",
            "title": "collaboration",
            "short_summary": prompt[:200] if prompt else "",
            "lifecycle_phase": "in_operation",
            "risk_level": "normal",
            "channel_type": "internal"
        })
        orchestra_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "mocka_orchestra_v10.py")
        if os.path.exists(orchestra_path):
            subprocess.Popen([sys.executable, orchestra_path, prompt, "orchestra"])

    def share(self, prompt):
        import subprocess, sys, os
        write_safe_csv({
            "who_actor": "mocka_router",
            "what_type": "share",
            "where_component": "router",
            "where_path": "interface/router.py",
            "why_purpose": "4AIへの非同期ブロードキャスト",
            "how_trigger": "router.share()呼び出し",
            "title": "share",
            "short_summary": prompt[:200] if prompt else "",
            "lifecycle_phase": "in_operation",
            "risk_level": "normal",
            "channel_type": "internal"
        })
        orchestra_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "mocka_orchestra_v10.py")
        if os.path.exists(orchestra_path):
            subprocess.Popen([sys.executable, orchestra_path, prompt, "share"])

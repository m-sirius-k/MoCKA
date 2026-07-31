import csv
import json
import os
import datetime
import re

EVENTS = r"C:\Users\sirok\MoCKA\data\events.csv"
INCIDENTS_DIR = r"C:\Users\sirok\MoCKA\docs\incidents"
RESTRICTIONS = r"C:\Users\sirok\MoCKA\tools\mocka_restrictions.py"

# RC-B最小実装(DC_20260731_006 / DC_20260731_007): INC進行軸の保持先。
# 承認軸(PENDING/APPROVED/REJECTED)はここに書かない。Human Gateが単一の真実源。
INC_LIFECYCLE_DIR = r"C:\Users\sirok\MoCKA\data\inc_lifecycle"
INC_STATE_SCHEMA_VERSION = "0.1"

FIELDNAMES = [
    "event_id","when","who_actor","what_type","where_component",
    "where_path","why_purpose","how_trigger","channel_type",
    "lifecycle_phase","risk_level","category_ab","target_class",
    "title","short_summary","before_state","after_state",
    "change_type","impact_scope","impact_result",
    "related_event_id","trace_id","free_note"
]

# リスク判定キーワード
CRITICAL_KEYWORDS = ["ERROR","429","RESOURCE_EXHAUSTED","quota","blocked","CRITICAL","audit_mode"]
HIGH_KEYWORDS = ["FAIL","save_only","WARNING","exceeded"]
MEDIUM_KEYWORDS = ["share_only","MEDIUM","timeout"]

def assess_risk(row):
    risk = "normal"
    reasons = []

    # 全フィールドを結合して検査
    all_text = " ".join(str(v) for v in row.values())

    # error_rateチェック
    m = re.search(r"error_rate=(\d+\.?\d*)", all_text)
    if m:
        er = float(m.group(1))
        if er > 0.5:
            risk = "CRITICAL"
            reasons.append(f"error_rate={er}")
        elif er > 0.2:
            risk = "HIGH"
            reasons.append(f"error_rate={er}")
        elif er > 0.0:
            risk = "MEDIUM"
            reasons.append(f"error_rate={er}")

    # キーワード判定
    for kw in CRITICAL_KEYWORDS:
        if kw in all_text:
            risk = "CRITICAL"
            reasons.append(kw)
            break

    if risk == "normal":
        for kw in HIGH_KEYWORDS:
            if kw in all_text:
                risk = "HIGH"
                reasons.append(kw)
                break

    if risk == "normal":
        for kw in MEDIUM_KEYWORDS:
            if kw in all_text:
                risk = "MEDIUM"
                reasons.append(kw)
                break

    return risk, list(set(reasons))

def get_lifecycle(risk):
    if risk == "CRITICAL":
        return "incident"
    elif risk in ("HIGH","MEDIUM"):
        return "warning"
    return "in_operation"

def auto_generate_incident(row, risk, reasons):
    today = datetime.datetime.now().strftime("%Y%m%d")
    existing = [f for f in os.listdir(INCIDENTS_DIR) 
                if f.startswith(f"INC-{today}") and f.endswith(".md")
                and "TEMPLATE" not in f]
    num = len(existing) + 1
    inc_id = f"INC-{today}-{num:03d}"
    path = os.path.join(INCIDENTS_DIR, f"{inc_id}.md")

    content = "\n".join([
        f"# {inc_id}",
        f"## 発生日時：{row.get('when','N/A')}",
        f"## 重大度：{risk}",
        "## 自動検知：Yes",
        "",
        "## 発生内容：",
        f"event_id: {row.get('event_id','N/A')}",
        f"what_type: {row.get('what_type','N/A')}",
        f"where: {row.get('where_component','N/A')} / {row.get('where_path','N/A')}",
        f"summary: {row.get('short_summary','N/A')[:100]}",
        "",
        "## 検知理由：",
        "\n".join(f"- {r}" for r in reasons),
        "",
        "## 再発防止：",
        "（要分析）",
        "",
        "## 憲章違反条項：",
        "（要確認）",
        "",
        "## 承認：",
        "自動生成 / 要Claude確認"
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # RC-B最小実装: INC本文の書込が成功した直後に進行軸を DETECTED で投入する。
    # 逆順にすると本文書込失敗時に state だけ残る孤児が発生するため順序を固定する。
    write_inc_state(inc_id, "DETECTED")
    return inc_id


def write_inc_state(inc_id, state):
    """INC進行軸の state ファイルを投入する(DC_20260731_006 / 設計6.11.1)。

    冪等: 既存ファイルは上書きしない(再実行で進行状態を巻き戻さないため)。
    失敗時: INC本文は残したまま続行する。当該INCは Fail Closed により公開されないが、
            無言で落ちると気づけないため必ず理由を出力する。
    """
    path = os.path.join(INC_LIFECYCLE_DIR, f"{inc_id}.json")
    try:
        if os.path.exists(path):
            print(f"[INC_STATE] skip(既存): {inc_id}")
            return True
        os.makedirs(INC_LIFECYCLE_DIR, exist_ok=True)
        record = {
            "schema_version": INC_STATE_SCHEMA_VERSION,
            "incident_id": inc_id,
            "state": state,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        }
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[INC_STATE] {inc_id} -> {state}")
        return True
    except Exception as e:
        # 承認軸(Human Gate)へは一切書き込まない。ここでの失敗は公開されない方向に働く。
        print(f"[INC_STATE][FAIL] {inc_id}: state書込に失敗しました({e})。"
              f"INC本文は残ります。当該INCはFail Closedにより公開されません")
        return False

def update_events_risk():
    rows = []
    updated = 0
    incidents_generated = []
    source_fieldnames = None

    with open(EVENTS, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        # Stage 1a(DC_20260731_004): 書き戻しで列を欠落させないため入力の列構成を保持する
        source_fieldnames = reader.fieldnames
        for row in reader:
            risk, reasons = assess_risk(row)
            lifecycle = get_lifecycle(risk)

            if row.get("risk_level") != risk:
                row["risk_level"] = risk
                row["lifecycle_phase"] = lifecycle
                updated += 1

                if risk in ("CRITICAL","HIGH") and reasons:
                    # 既存INCと重複しないか確認
                    existing_incs = [f for f in os.listdir(INCIDENTS_DIR)
                                    if row.get("event_id","") in open(
                                        os.path.join(INCIDENTS_DIR,f),
                                        encoding="utf-8",errors="replace").read()
                                    ] if os.path.exists(INCIDENTS_DIR) else []
                    if not existing_incs:
                        inc_id = auto_generate_incident(row, risk, reasons)
                        row["related_event_id"] = inc_id
                        incidents_generated.append(inc_id)

            rows.append(row)

    # Stage 1a(DC_20260731_004 / 条項E-6): 入力に存在した列をそのまま保全する。
    # 入力が空でヘッダを取得できない場合のみ FIELDNAMES へ退避する。
    out_fieldnames = source_fieldnames if source_fieldnames else FIELDNAMES

    with open(EVENTS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k,"N/A") for k in out_fieldnames})

    print(f"[risk更新] {updated}件")
    print(f"[INC自動生成] {len(incidents_generated)}件")
    for inc in incidents_generated:
        print(f"  -> {inc}")

    if incidents_generated:
        os.system(f"python {RESTRICTIONS}")
        print("[GPT_RESTRICTIONS] 自動更新完了")
        # 5W1H自動分析
        w5h1_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mocka_5w1h.py")
        os.system(f"python {w5h1_script}")
        print("[5W1H] 自動分析完了")

if __name__ == "__main__":
    print("=" * 50)
    print("MoCKA 自動リスク判定エンジン v2")
    print(f"実行時刻: {datetime.datetime.now()}")
    print("=" * 50)
    update_events_risk()
    print("=" * 50)


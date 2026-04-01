import csv
import os
import datetime
import re

EVENTS = r"C:\Users\sirok\MoCKA\data\events.csv"
INCIDENTS_DIR = r"C:\Users\sirok\MoCKA\docs\incidents"
RESTRICTIONS = r"C:\Users\sirok\MoCKA\tools\mocka_restrictions.py"

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
    return inc_id

def update_events_risk():
    rows = []
    updated = 0
    incidents_generated = []

    with open(EVENTS, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
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

    with open(EVENTS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k,"N/A") for k in FIELDNAMES})

    print(f"[risk更新] {updated}件")
    print(f"[INC自動生成] {len(incidents_generated)}件")
    for inc in incidents_generated:
        print(f"  -> {inc}")

    if incidents_generated:
        os.system(f"python {RESTRICTIONS}")
        print("[GPT_RESTRICTIONS] 自動更新完了")

if __name__ == "__main__":
    print("=" * 50)
    print("MoCKA 自動リスク判定エンジン v2")
    print(f"実行時刻: {datetime.datetime.now()}")
    print("=" * 50)
    update_events_risk()
    print("=" * 50)

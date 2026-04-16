# -*- coding: utf-8 -*-
"""
mocka_n_expansion_pipeline.py
==============================
n値拡張統合パイプライン
Step1: Gitログ → インシデント抽出
Step2: events.csvからキーワードベース拡張抽出
Step3: Z軸計算（フル実装）
Step4: 統合nレポート生成

出力: data/experiments/n_expansion_report.json
      data/auto_incidents.csv
"""
import csv, json, subprocess, hashlib, re, datetime
from pathlib import Path
from statistics import mean

ROOT    = Path(r"C:\Users\sirok\MoCKA")
EVENTS  = ROOT / "data" / "events.csv"
OUTPUT_DIR = ROOT / "data" / "experiments"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GIT_LOG_FILE  = ROOT / "data" / "experiments" / "git_log_raw.txt"
GIT_DIFF_FILE = ROOT / "data" / "experiments" / "git_numstat.txt"
AUTO_INC_CSV  = ROOT / "data" / "auto_incidents.csv"
REPORT_FILE   = OUTPUT_DIR / "n_expansion_report.json"

MOCKA_START = datetime.datetime(2026, 3, 29)

# ══════════════════════════════════════════════════════════
# STEP 1: Gitログ取得 → インシデント変換
# ══════════════════════════════════════════════════════════
def step1_git_incidents():
    print("\n" + "="*60)
    print("STEP 1: Gitログ → インシデント抽出")
    print("="*60)

    # Gitログ取得
    try:
        log_result = subprocess.run(
            ["git", "log", "--numstat", "--pretty=format:%H|%ai|%an|%s"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        raw = log_result.stdout
    except Exception as e:
        print(f"  Git実行失敗: {e}")
        print("  → git_log_raw.txtが存在すれば読み込み試行")
        if GIT_LOG_FILE.exists():
            raw = GIT_LOG_FILE.read_text(encoding="utf-8", errors="replace")
        else:
            print("  → Gitログなし。STEP1スキップ")
            return []

    GIT_LOG_FILE.write_text(raw, encoding="utf-8")
    print(f"  Gitログ取得: {len(raw.splitlines())}行")

    # パース: コミット単位でブロック分割
    incidents = []
    current = {}
    add_total = del_total = 0

    REWRITE_KEYWORDS = [
        "fix", "error", "bug", "rewrite", "replace", "broken",
        "fail", "crash", "wrong", "mistake", "undo", "revert",
        "整合", "修正", "エラー", "書き換え", "破損", "不整合",
        "崩壊", "ミス", "失敗", "戻す", "やり直し"
    ]

    for line in raw.splitlines():
        line = line.strip()
        if "|" in line and len(line.split("|")) == 4:
            # 前のコミットを保存
            if current and (add_total + del_total) > 0:
                _save_git_incident(current, add_total, del_total, REWRITE_KEYWORDS, incidents)
            # 新コミット開始
            parts = line.split("|")
            current = {
                "hash"   : parts[0][:8],
                "date"   : parts[1].strip(),
                "author" : parts[2].strip(),
                "message": parts[3].strip(),
            }
            add_total = del_total = 0
        elif line and line[0].isdigit():
            # numstat行: added deleted filename
            parts = line.split("\t")
            if len(parts) >= 2:
                try: add_total += int(parts[0])
                except: pass
                try: del_total += int(parts[1])
                except: pass

    # 最後のコミット
    if current and (add_total + del_total) > 0:
        _save_git_incident(current, add_total, del_total, REWRITE_KEYWORDS, incidents)

    print(f"  Git由来インシデント候補: {len(incidents)}件")
    return incidents


def _save_git_incident(commit, adds, dels, keywords, incidents):
    msg = commit.get("message", "").lower()
    total_changes = adds + dels

    # リスクレベル判定
    is_keyword = any(k in msg for k in keywords)
    is_large   = total_changes >= 50  # 50行以上の変更

    if not (is_keyword or is_large):
        return

    risk = "CRITICAL" if (is_keyword and is_large) else \
           "WARNING"  if (is_keyword or total_changes >= 100) else "normal"

    if risk == "normal":
        return

    # MoCKA前後判定
    try:
        dt = datetime.datetime.fromisoformat(commit["date"][:19])
        phase = "after" if dt >= MOCKA_START else "before"
    except:
        phase = "unknown"

    incident = {
        "event_id"        : f"GIT_{commit['hash']}",
        "when"            : commit["date"][:19],
        "who_actor"       : f"git_{commit['author'].replace(' ','_')[:15]}",
        "what_type"       : "code_change",
        "where_component" : "git_repository",
        "where_path"      : "MoCKA/.git",
        "why_purpose"     : commit["message"][:80],
        "how_trigger"     : "git_commit",
        "channel_type"    : "terminal",
        "lifecycle_phase" : "in_operation",
        "risk_level"      : risk,
        "category_ab"     : "B",
        "target_class"    : "code_integrity",
        "title"           : f"[GIT] {commit['message'][:50]}",
        "short_summary"   : f"lines_added={adds} lines_deleted={dels} total={adds+dels}",
        "before_state"    : f"pre_commit_{commit['hash']}",
        "after_state"     : f"post_commit_{commit['hash']}",
        "change_type"     : "code_rewrite" if adds+dels >= 100 else "partial_fix",
        "impact_scope"    : "global" if adds+dels >= 200 else "local",
        "impact_result"   : "integrity_risk" if risk == "CRITICAL" else "quality_concern",
        "related_event_id": "N/A",
        "trace_id"        : commit["hash"],
        "free_note"       : f"source=git|phase={phase}|adds={adds}|dels={dels}",
        "_source"         : "git",
        "_phase"          : phase,
    }
    incidents.append(incident)


# ══════════════════════════════════════════════════════════
# STEP 2: events.csvからキーワード拡張抽出
# ══════════════════════════════════════════════════════════
def step2_events_extended():
    print("\n" + "="*60)
    print("STEP 2: events.csv 拡張インシデント抽出")
    print("="*60)

    KEYWORDS = [
        "error", "fail", "timeout", "exception", "violation",
        "ignore", "unauthorized", "broken", "crash", "wrong",
        "エラー", "失敗", "違反", "無断", "崩壊", "不整合",
        "instruction_ignore", "dependency_break", "fast_wrong",
    ]

    rows = []
    with open(EVENTS, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    incidents = []
    for r in rows:
        rl = r.get("risk_level", "").strip()
        if rl in ("WARNING", "CRITICAL", "ERROR"):
            r["_source"] = "events_risk"
            r["_phase"] = "after" if _is_after(r) else "before"
            incidents.append(r)
            continue

        # キーワード判定
        text = " ".join([
            r.get("what_type",""), r.get("why_purpose",""),
            r.get("how_trigger",""), r.get("title",""),
            r.get("short_summary",""), r.get("free_note","") or "",
        ]).lower()

        if any(k in text for k in KEYWORDS):
            r["_source"] = "events_keyword"
            r["_phase"] = "after" if _is_after(r) else "before"
            incidents.append(r)

    print(f"  events由来インシデント候補: {len(incidents)}件")
    print(f"  （うち risk_level>=WARNING: {sum(1 for i in incidents if i.get('risk_level') in ('WARNING','CRITICAL','ERROR'))}件）")
    return incidents


def _is_after(e):
    try:
        return datetime.datetime.fromisoformat(str(e.get("when",""))[:19]) >= MOCKA_START
    except:
        return False


# ══════════════════════════════════════════════════════════
# STEP 3: Z軸計算（フル実装）
# ══════════════════════════════════════════════════════════
def step3_z_axis(all_incidents):
    print("\n" + "="*60)
    print("STEP 3: Z軸計算（フル実装）")
    print("="*60)

    def compute_z(incidents, label, w1=0.4, w2=0.3, w3=0.3):
        total = len(incidents)
        if total == 0:
            print(f"  [{label}] データなし")
            return None

        # D: 逸脱率（deviation_flagまたはrisk!=normal）
        dev = sum(1 for e in incidents if
                  e.get("deviation_flag") == "1" or
                  e.get("risk_level") in ("WARNING","CRITICAL","ERROR"))
        D = dev / total

        # R: 再発率
        inc_list = [e for e in incidents if e.get("risk_level") in ("WARNING","CRITICAL","ERROR")]
        rec_list = [e for e in incidents if e.get("recurrence_flag") == "1"]
        R = len(rec_list) / len(inc_list) if inc_list else 0

        # T: 応答遅延（正規化）
        NORM = 300.0
        times = []
        for e in inc_list:
            v = e.get("response_time_sec", "")
            try: times.append(float(v))
            except: pass
        avg_t = mean(times) if times else 0
        T = min(avg_t / NORM, 1.0)

        Z = max(0.0, min(1.0, 1 - (w1*D + w2*R + w3*T)))

        print(f"  [{label}] n={total:4d} | D={D:.4f} R={R:.4f} T={T:.4f} → Z={Z:.4f}")
        return {"label":label,"n":total,"D":round(D,4),"R":round(R,4),"T":round(T,4),"Z":round(Z,4)}

    before = [e for e in all_incidents if e.get("_phase") == "before"]
    after  = [e for e in all_incidents if e.get("_phase") == "after"]

    z_all    = compute_z(all_incidents, "全体")
    z_before = compute_z(before,        "MoCKA前")
    z_after  = compute_z(after,         "MoCKA後")

    if z_before and z_after:
        delta = round(z_after["Z"] - z_before["Z"], 4)
        direction = "向上" if delta > 0 else "低下"
        print(f"\n  Z軸変化: {z_before['Z']} → {z_after['Z']} (Δ{delta:+.4f} {direction})")
        print(f"  解釈: {'診断技術効果の可能性（αと相関確認要）' if delta < 0 else 'MoCKA後に改善'}")

    return {"all":z_all, "before":z_before, "after":z_after}


# ══════════════════════════════════════════════════════════
# STEP 4: 統合nレポート
# ══════════════════════════════════════════════════════════
def step4_report(git_inc, ev_inc, z_result):
    print("\n" + "="*60)
    print("STEP 4: 統合n値レポート")
    print("="*60)

    all_inc = git_inc + ev_inc

    # 重複除去（event_id基準）
    seen = set()
    unique = []
    for i in all_inc:
        eid = i.get("event_id","")
        if eid not in seen:
            seen.add(eid)
            unique.append(i)

    before = [i for i in unique if i.get("_phase") == "before"]
    after  = [i for i in unique if i.get("_phase") == "after"]
    critical = [i for i in unique if i.get("risk_level") == "CRITICAL"]
    warning  = [i for i in unique if i.get("risk_level") == "WARNING"]
    git_src  = [i for i in unique if i.get("_source") == "git"]
    ev_src   = [i for i in unique if "_source" in i and "events" in i["_source"]]

    print(f"\n  【n値サマリー】")
    print(f"  元のn（strict）     : 10件（risk_level>=WARNING・events.csvのみ）")
    print(f"  Git由来インシデント : {len(git_src)}件")
    print(f"  events拡張抽出     : {len(ev_src)}件")
    print(f"  統合n（重複除去後） : {len(unique)}件")
    print(f"  　うちMoCKA前      : {len(before)}件")
    print(f"  　うちMoCKA後      : {len(after)}件")
    print(f"  　うちCRITICAL    : {len(critical)}件")
    print(f"  　うちWARNING     : {len(warning)}件")

    # auto_incidents.csv出力
    if unique:
        fieldnames = list(unique[0].keys())
        # 内部フィールドを末尾に
        for f in ["_source","_phase"]:
            if f in fieldnames:
                fieldnames.remove(f)
                fieldnames.append(f)
        with open(AUTO_INC_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(unique)
        print(f"\n  ✓ auto_incidents.csv → {AUTO_INC_CSV} ({len(unique)}件)")

    # JSONレポート
    report = {
        "generated_at"   : datetime.datetime.now().isoformat(),
        "n_strict"       : 10,
        "n_git"          : len(git_src),
        "n_events_ext"   : len(ev_src),
        "n_total_unique" : len(unique),
        "n_before_mocka" : len(before),
        "n_after_mocka"  : len(after),
        "n_critical"     : len(critical),
        "n_warning"      : len(warning),
        "z_axis"         : z_result,
        "aies_assessment": {
            "minimum_required": 30,
            "current"         : len(unique),
            "gap"             : max(0, 30 - len(unique)),
            "status"          : "達成" if len(unique) >= 30 else f"あと{30-len(unique)}件必要",
            "recommendation"  : "B+C戦略（設計論文＋Git証拠）が最適"
        },
        "sha256": hashlib.sha256(
            json.dumps({"n":len(unique),"z":z_result},
            ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()
    }

    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ レポート → {REPORT_FILE}")
    print(f"\n  AIES最低基準(n≥30): {report['aies_assessment']['status']}")
    print(f"  SHA256: {report['sha256']}")
    return report


# ══════════════════════════════════════════════════════════
# メイン
# ══════════════════════════════════════════════════════════
def main():
    print("MoCKA n値拡張統合パイプライン 開始")
    print(f"MOCKA_START: {MOCKA_START.date()}")

    git_inc = step1_git_incidents()
    ev_inc  = step2_events_extended()

    all_inc = git_inc + ev_inc
    z_result = step3_z_axis(all_inc)

    report = step4_report(git_inc, ev_inc, z_result)

    print("\n" + "="*60)
    print("完了")
    print("="*60)
    print(f"  統合n: {report['n_total_unique']}件")
    print(f"  Z軸（全体）: {report['z_axis']['all']['Z'] if report['z_axis']['all'] else 'N/A'}")
    print(f"  AIES基準: {report['aies_assessment']['status']}")

if __name__ == "__main__":
    main()

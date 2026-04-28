# -*- coding: utf-8 -*-
"""
csv_cross_analysis.py
=====================
全CSVファイルの構造把握 + CSV間組み合わせ分析
既存フィールドの掛け合わせで新たな指数を導出する
"""
import csv, json, hashlib, datetime, math
from pathlib import Path
from collections import defaultdict

ROOT     = Path(r"C:\Users\sirok\MoCKA\data")
OUTPUT   = ROOT / "experiments" / "csv_cross_analysis.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def safe(v, k, d=""):
    val = v.get(k); return val if val is not None else d

def pdt(s):
    try: return datetime.datetime.fromisoformat(str(s).strip())
    except: return None

def load_csv(path, enc="utf-8-sig"):
    try:
        with open(path, encoding=enc, newline="") as f:
            rows = list(csv.DictReader(f))
        return rows
    except Exception as e:
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            return rows
        except:
            return []

# ══════════════════════════════════════════════════════════
# STEP 1: 全CSVの構造把握
# ══════════════════════════════════════════════════════════
def step1_structure():
    print("\n" + "="*60)
    print("STEP 1: 全CSVファイルの構造把握")
    print("="*60)

    files = {
        "events"             : ROOT / "events.csv",
        "recurrence_registry": ROOT / "recurrence_registry.csv",
        "trajectory_v2"      : ROOT / "trajectory_v2.csv",
        "trajectory"         : ROOT / "trajectory.csv",
        "claude_sessions"    : ROOT / "claude_sessions.csv",
        "failure_log"        : ROOT / "failure_log.csv",
    }

    summary = {}
    for name, path in files.items():
        if not path.exists():
            print(f"  {name}: 存在しない")
            continue
        rows = load_csv(path)
        if not rows:
            print(f"  {name}: 読み込み失敗または空")
            continue
        cols = list(rows[0].keys())
        print(f"\n  [{name}] {len(rows)}行 × {len(cols)}列")
        print(f"  列: {', '.join(cols[:8])}{'...' if len(cols)>8 else ''}")
        # 日付列を探す
        date_cols = [c for c in cols if any(k in c.lower() for k in ['when','date','time','at'])]
        if date_cols:
            dts = [pdt(safe(r, date_cols[0])) for r in rows if pdt(safe(r, date_cols[0]))]
            if dts:
                print(f"  期間: {min(dts).date()} 〜 {max(dts).date()}")
        summary[name] = {"rows": len(rows), "cols": cols, "path": str(path)}

    return summary

# ══════════════════════════════════════════════════════════
# STEP 2: events.csv内フィールド掛け合わせ分析
# ══════════════════════════════════════════════════════════
def step2_events_cross(events):
    print("\n" + "="*60)
    print("STEP 2: events.csv フィールド掛け合わせ分析")
    print("="*60)

    results = {}

    # 2-1: who_actor × risk_level（誰がどのレベルの問題を起こすか）
    print("\n  [2-1] who_actor × risk_level")
    actor_risk = defaultdict(lambda: defaultdict(int))
    for e in events:
        actor = safe(e,"who_actor","unknown")
        risk  = safe(e,"risk_level","unknown")
        actor_risk[actor][risk] += 1
    for actor, risks in sorted(actor_risk.items(), key=lambda x: sum(x[1].values()), reverse=True)[:5]:
        print(f"    {actor:25}: {dict(risks)}")
    results["who_actor_x_risk_level"] = {k: dict(v) for k,v in actor_risk.items()}

    # 2-2: what_type × how_trigger（何が × どのように発生するか）
    print("\n  [2-2] what_type × how_trigger")
    type_trigger = defaultdict(lambda: defaultdict(int))
    for e in events:
        wtype   = safe(e,"what_type","unknown")
        trigger = safe(e,"how_trigger","unknown")
        type_trigger[wtype][trigger] += 1
    for wtype, triggers in sorted(type_trigger.items(), key=lambda x: sum(x[1].values()), reverse=True)[:5]:
        print(f"    {wtype:20}: {dict(triggers)}")
    results["what_type_x_how_trigger"] = {k: dict(v) for k,v in type_trigger.items()}

    # 2-3: lifecycle_phase × risk_level（どのフェーズでリスクが高いか）
    print("\n  [2-3] lifecycle_phase × risk_level")
    phase_risk = defaultdict(lambda: defaultdict(int))
    for e in events:
        phase = safe(e,"lifecycle_phase","unknown")
        risk  = safe(e,"risk_level","unknown")
        phase_risk[phase][risk] += 1
    for phase, risks in sorted(phase_risk.items()):
        print(f"    {phase:20}: {dict(risks)}")
    results["lifecycle_phase_x_risk_level"] = {k: dict(v) for k,v in phase_risk.items()}

    # 2-4: channel_type × what_type（チャネル別の事象種別）
    print("\n  [2-4] channel_type × what_type（上位）")
    ch_type = defaultdict(lambda: defaultdict(int))
    for e in events:
        ch    = safe(e,"channel_type","unknown")
        wtype = safe(e,"what_type","unknown")
        ch_type[ch][wtype] += 1
    for ch, types in sorted(ch_type.items(), key=lambda x: sum(x[1].values()), reverse=True)[:4]:
        top = sorted(types.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"    {ch:15}: {dict(top)}")
    results["channel_x_what_type"] = {k: dict(v) for k,v in ch_type.items()}

    # 2-5: impact_scope × risk_level（影響範囲とリスクの関係）
    print("\n  [2-5] impact_scope × risk_level")
    scope_risk = defaultdict(lambda: defaultdict(int))
    for e in events:
        scope = safe(e,"impact_scope","unknown")
        risk  = safe(e,"risk_level","unknown")
        scope_risk[scope][risk] += 1
    for scope, risks in sorted(scope_risk.items()):
        print(f"    {scope:15}: {dict(risks)}")
    results["impact_scope_x_risk_level"] = {k: dict(v) for k,v in scope_risk.items()}

    # 2-6: 時間帯 × risk_level（いつリスクが発生するか）
    print("\n  [2-6] 時間帯（時） × risk_level")
    hour_risk = defaultdict(lambda: defaultdict(int))
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts:
            hour_risk[ts.hour][safe(e,"risk_level","normal")] += 1
    high_risk_hours = {h: v for h,v in hour_risk.items() if any(k in v for k in ["WARNING","CRITICAL","ERROR"])}
    for h in sorted(high_risk_hours.keys()):
        print(f"    {h:02d}時: {dict(hour_risk[h])}")
    results["hour_x_risk_level"] = {str(k): dict(v) for k,v in hour_risk.items()}

    return results

# ══════════════════════════════════════════════════════════
# STEP 3: events × recurrence_registry の結合分析
# ══════════════════════════════════════════════════════════
def step3_events_x_recurrence(events, recurrence):
    print("\n" + "="*60)
    print("STEP 3: events × recurrence_registry 結合分析")
    print("="*60)

    if not recurrence:
        print("  recurrence_registry: 読み込み失敗")
        return {}

    print(f"  events: {len(events)}件")
    print(f"  recurrence_registry: {len(recurrence)}件")
    print(f"  recurrence列: {list(recurrence[0].keys()) if recurrence else '不明'}")

    # recurrenceのevent_idをeventsと照合
    rec_ids = set(safe(r, list(r.keys())[0]) for r in recurrence)
    ev_ids  = set(safe(e,"event_id") for e in events)
    matched = rec_ids & ev_ids

    print(f"\n  recurrenceとeventsの照合:")
    print(f"  recurrence件数: {len(rec_ids)}")
    print(f"  events件数: {len(ev_ids)}")
    print(f"  一致件数: {len(matched)}")

    # recurrenceに記録されたイベントのrisk_level分布
    matched_events = [e for e in events if safe(e,"event_id") in matched]
    risk_dist = defaultdict(int)
    for e in matched_events:
        risk_dist[safe(e,"risk_level","unknown")] += 1
    print(f"  再発イベントのrisk_level分布: {dict(risk_dist)}")

    # recurrenceに記録されたイベントのwhat_type分布
    type_dist = defaultdict(int)
    for e in matched_events:
        type_dist[safe(e,"what_type","unknown")] += 1
    print(f"  再発イベントのwhat_type分布: {dict(type_dist)}")

    return {
        "recurrence_count": len(rec_ids),
        "events_count": len(ev_ids),
        "matched": len(matched),
        "matched_risk_dist": dict(risk_dist),
        "matched_type_dist": dict(type_dist),
    }

# ══════════════════════════════════════════════════════════
# STEP 4: events × trajectory_v2 の結合分析
# ══════════════════════════════════════════════════════════
def step4_events_x_trajectory(events, trajectory):
    print("\n" + "="*60)
    print("STEP 4: events × trajectory_v2 結合分析")
    print("="*60)

    if not trajectory:
        print("  trajectory_v2: 読み込み失敗")
        return {}

    print(f"  trajectory_v2: {len(trajectory)}件")
    print(f"  trajectory列: {list(trajectory[0].keys())[:10] if trajectory else '不明'}")

    # trajectoryの時系列とeventsの時系列を比較
    traj_dates = []
    for t in trajectory:
        for col in t.keys():
            dt = pdt(safe(t, col))
            if dt:
                traj_dates.append(dt)
                break

    ev_dates = [pdt(safe(e,"when")) for e in events if pdt(safe(e,"when"))]

    if traj_dates and ev_dates:
        print(f"\n  trajectory期間: {min(traj_dates).date()} 〜 {max(traj_dates).date()}")
        print(f"  events期間: {min(ev_dates).date()} 〜 {max(ev_dates).date()}")

    # X,Y,Z座標の統計（流動座標理論）
    x_vals, y_vals, z_vals = [], [], []
    for t in trajectory:
        cols = list(t.keys())
        for col in cols:
            if col.upper() in ['X','X_SCORE','X_VALUE','PROTOCOL_FIDELITY']:
                try: x_vals.append(float(safe(t,col)))
                except: pass
            if col.upper() in ['Y','Y_SCORE','Y_VALUE','STRUCTURAL_COMPLETENESS']:
                try: y_vals.append(float(safe(t,col)))
                except: pass
            if col.upper() in ['Z','Z_SCORE','Z_VALUE','INSTITUTIONAL_INTEGRITY']:
                try: z_vals.append(float(safe(t,col)))
                except: pass

    def st(lst):
        if not lst: return None
        return {"n":len(lst),"mean":round(sum(lst)/len(lst),4),"min":round(min(lst),4),"max":round(max(lst),4)}

    print(f"\n  座標統計:")
    print(f"  X（プロトコル忠実性）: {st(x_vals)}")
    print(f"  Y（構造完全性）      : {st(y_vals)}")
    print(f"  Z（制度整合性）      : {st(z_vals)}")

    # Z軸低下とeventsのインシデントの時間的相関
    MOCKA_START = datetime.datetime(2026, 3, 29)
    inc_after = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START
                 and safe(e,"risk_level") in {"WARNING","CRITICAL","ERROR"}]
    print(f"\n  MoCKA後インシデント({len(inc_after)}件)とZ軸低下の時間的関係:")
    for e in inc_after:
        print(f"    {safe(e,'when')[:10]} | {safe(e,'risk_level'):8} | {safe(e,'title')[:40]}")

    return {
        "trajectory_rows": len(trajectory),
        "x_stats": st(x_vals),
        "y_stats": st(y_vals),
        "z_stats": st(z_vals),
        "cols_found": list(trajectory[0].keys()) if trajectory else [],
    }

# ══════════════════════════════════════════════════════════
# STEP 5: events × claude_sessions の結合分析
# ══════════════════════════════════════════════════════════
def step5_events_x_sessions(events, sessions):
    print("\n" + "="*60)
    print("STEP 5: events × claude_sessions 結合分析")
    print("="*60)

    if not sessions:
        print("  claude_sessions: 読み込み失敗")
        return {}

    print(f"  claude_sessions: {len(sessions)}件")
    print(f"  sessions列: {list(sessions[0].keys())[:8] if sessions else '不明'}")

    # セッション数の時系列とインシデントの時系列を比較
    sess_by_date = defaultdict(int)
    for s in sessions:
        for col in s.keys():
            dt = pdt(safe(s,col))
            if dt:
                sess_by_date[dt.strftime("%Y-%m-%d")] += 1
                break

    inc_by_date = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts and safe(e,"risk_level") in {"WARNING","CRITICAL","ERROR"}:
            inc_by_date[ts.strftime("%Y-%m-%d")] += 1

    print(f"\n  セッション日別分布（上位5日）:")
    for d,c in sorted(sess_by_date.items(), key=lambda x:x[1], reverse=True)[:5]:
        inc = inc_by_date.get(d, 0)
        print(f"    {d}: sessions={c} incidents={inc}")

    return {
        "session_count": len(sessions),
        "session_cols": list(sessions[0].keys()) if sessions else [],
        "session_by_date": dict(sess_by_date),
    }

# ══════════════════════════════════════════════════════════
# STEP 6: 新指数の導出（CSV組み合わせから）
# ══════════════════════════════════════════════════════════
def step6_new_indices(events, recurrence, trajectory):
    print("\n" + "="*60)
    print("STEP 6: CSV組み合わせから導出する新指数")
    print("="*60)

    MOCKA_START = datetime.datetime(2026, 3, 29)

    # 指数1: AI危険度指数（ADI: AI Danger Index）
    # = AI起因インシデント数 / 全インシデント数
    inc_all = [e for e in events if safe(e,"risk_level") in {"WARNING","CRITICAL","ERROR"}]
    inc_ai  = [e for e in inc_all if "ai_" in safe(e,"who_actor").lower() or safe(e,"what_type")=="ai_violation"]
    ADI = round(len(inc_ai)/max(len(inc_all),1)*100, 2)
    print(f"\n  [ADI] AI危険度指数: {ADI}% ({len(inc_ai)}/{len(inc_all)}件がAI起因)")

    # 指数2: 制度応答速度指数（IRS: Institutional Response Speed）
    # = インシデント発生後に対応イベントが何件/日以内に来るか
    # related_event_idが設定されているペアを探す
    event_dict = {safe(e,"event_id"): e for e in events}
    response_times = []
    for e in events:
        rel = safe(e,"related_event_id","N/A")
        if rel != "N/A" and rel in event_dict:
            t1 = pdt(safe(event_dict[rel],"when"))
            t2 = pdt(safe(e,"when"))
            if t1 and t2 and t2 > t1:
                response_times.append((t2-t1).total_seconds()/3600)
    if response_times:
        IRS = round(sum(response_times)/len(response_times), 2)
        print(f"  [IRS] 制度応答時間（平均）: {IRS}h ({len(response_times)}ペア)")
    else:
        IRS = None
        print(f"  [IRS] 制度応答時間: 測定不能（related_event_idのペアなし）")

    # 指数3: チャネル別リスク集中度（CRC: Channel Risk Concentration）
    # = 特定チャネルにリスクが集中しているか
    ch_risk = defaultdict(int)
    for e in inc_all:
        ch_risk[safe(e,"channel_type","unknown")] += 1
    total_inc = max(len(inc_all),1)
    CRC = {ch: round(c/total_inc*100,1) for ch,c in ch_risk.items()}
    print(f"  [CRC] チャネル別リスク集中度: {CRC}")

    # 指数4: 自律実行リスク率（AER: Autonomous Execution Risk）
    # = how_trigger=ai_autonomous のインシデント率
    auto_inc = [e for e in inc_all if "autonomous" in safe(e,"how_trigger","").lower() or "auto" in safe(e,"how_trigger","").lower()]
    AER = round(len(auto_inc)/max(len(inc_all),1)*100, 2)
    print(f"  [AER] 自律実行リスク率: {AER}% ({len(auto_inc)}件が自律実行起因)")

    # 指数5: MoCKA前後の制度変化スコア（ICS: Institutional Change Score）
    # = (後期CRITICAL率 - 前期CRITICAL率) / 前期CRITICAL率
    inc_before = [e for e in inc_all if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START]
    inc_after  = [e for e in inc_all if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START]
    crit_before_rate = len([e for e in inc_before if safe(e,"risk_level")=="CRITICAL"])/max(len(inc_before),1)
    crit_after_rate  = len([e for e in inc_after  if safe(e,"risk_level")=="CRITICAL"])/max(len(inc_after),1)
    ICS = round((crit_after_rate - crit_before_rate)/max(crit_before_rate,0.001)*100, 2)
    print(f"  [ICS] 制度変化スコア: {ICS}% (CRITICAL率: {round(crit_before_rate*100,1)}%→{round(crit_after_rate*100,1)}%)")

    # 指数6: recurrence × events 結合リスクスコア（CRS）
    if recurrence:
        rec_ids = set()
        for r in recurrence:
            cols = list(r.keys())
            if cols: rec_ids.add(safe(r, cols[0]))
        rec_inc = [e for e in inc_all if safe(e,"event_id") in rec_ids]
        CRS = round(len(rec_inc)/max(len(inc_all),1)*100, 2)
        print(f"  [CRS] 再発×インシデント結合リスクスコア: {CRS}% ({len(rec_inc)}件が再発かつインシデント)")
    else:
        CRS = None
        print(f"  [CRS] 再発×インシデント結合リスクスコア: 測定不能")

    return {
        "ADI_ai_danger_index_pct": ADI,
        "IRS_institutional_response_hours": IRS,
        "CRC_channel_risk_concentration": CRC,
        "AER_autonomous_execution_risk_pct": AER,
        "ICS_institutional_change_score_pct": ICS,
        "CRS_combined_risk_score_pct": CRS,
    }

# ══════════════════════════════════════════════════════════
# メイン
# ══════════════════════════════════════════════════════════
def main():
    print("CSV横断分析 開始")

    s1 = step1_structure()

    events     = load_csv(ROOT/"events.csv")
    recurrence = load_csv(ROOT/"recurrence_registry.csv")
    trajectory = load_csv(ROOT/"trajectory_v2.csv")
    sessions   = load_csv(ROOT/"claude_sessions.csv")
    failure    = load_csv(ROOT/"failure_log.csv")

    print(f"\n読み込み完了:")
    print(f"  events: {len(events)}件")
    print(f"  recurrence: {len(recurrence)}件")
    print(f"  trajectory_v2: {len(trajectory)}件")
    print(f"  claude_sessions: {len(sessions)}件")
    print(f"  failure_log: {len(failure)}件")

    s2 = step2_events_cross(events)
    s3 = step3_events_x_recurrence(events, recurrence)
    s4 = step4_events_x_trajectory(events, trajectory)
    s5 = step5_events_x_sessions(events, sessions)
    s6 = step6_new_indices(events, recurrence, trajectory)

    print("\n" + "="*60)
    print("新指数サマリー")
    print("="*60)
    for k,v in s6.items():
        print(f"  {k}: {v}")

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "step1_structure": {k: {"rows":v["rows"],"cols_count":len(v["cols"])} for k,v in s1.items()},
        "step2_events_cross": s2,
        "step3_events_x_recurrence": s3,
        "step4_events_x_trajectory": s4,
        "step5_events_x_sessions": s5,
        "step6_new_indices": s6,
        "sha256": hashlib.sha256(json.dumps(s6,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    }

    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\n✓ 保存 → {OUTPUT}")

if __name__=="__main__":
    main()

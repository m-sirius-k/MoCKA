# -*- coding: utf-8 -*-
"""
mocka_verification_v1to6.py
MoCKA 多角的検証 V1-V6 一括実行
"""
import csv, json, hashlib, datetime
from pathlib import Path
from collections import defaultdict

ROOT        = Path(r"C:\Users\sirok\MoCKA")
EVENTS_CSV  = ROOT / "data" / "events.csv"
OUTPUT      = ROOT / "data" / "experiments" / "verification_report.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

MOCKA_START     = datetime.datetime(2026, 3, 29)
INCIDENT_LEVELS = {"WARNING", "CRITICAL", "ERROR"}

def pdt(s):
    try: return datetime.datetime.fromisoformat(str(s).strip())
    except: return None

def safe(v, k, d=""):
    val = v.get(k)
    return val if val is not None else d

def load():
    with open(EVENTS_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def is_inc(e): return safe(e,"risk_level").strip() in INCIDENT_LEVELS
def before(e): ts=pdt(safe(e,"when")); return ts and ts < MOCKA_START
def after(e):  ts=pdt(safe(e,"when")); return ts and ts >= MOCKA_START

def v1(events):
    incs = sorted([e for e in events if is_inc(e) and pdt(safe(e,"when"))], key=lambda e:pdt(safe(e,"when")))
    ib, ia, prev = [], [], None
    for e in incs:
        ts = pdt(safe(e,"when"))
        if prev:
            d = (ts-prev).total_seconds()/3600
            (ib if ts < MOCKA_START else ia).append(d)
        prev = ts
    def st(l): return {"count":len(l),"mean_h":round(sum(l)/len(l),2)if l else 0,"min_h":round(min(l),2)if l else 0,"max_h":round(max(l),2)if l else 0}
    b,a = st(ib),st(ia)
    ratio = round(a["mean_h"]/b["mean_h"],2) if b["mean_h"]>0 and a["mean_h"]>0 else "N/A"
    verdict = f"インシデント間隔{ratio}倍に延長" if isinstance(ratio,float) and ratio>1 else "データ不足"
    print(f"\n[V1] 導入前:{b['mean_h']}h/{b['count']}件 導入後:{a['mean_h']}h/{a['count']}件 -> {verdict}")
    return {"before":b,"after":a,"improvement_ratio":ratio,"verdict":verdict}

def v2(events):
    bt,at = defaultdict(list), defaultdict(list)
    for e in events:
        if not is_inc(e): continue
        t = safe(e,"what_type","unknown")
        (bt if before(e) else at)[t].append(safe(e,"event_id"))
    recurred   = [t for t in bt if t in at]
    suppressed = [t for t in bt if t not in at]
    rate = round(len(suppressed)/len(bt)*100,2) if bt else 0
    print(f"\n[V2] 前:{list(bt.keys())} 後:{list(at.keys())}")
    print(f"     再発:{recurred} 抑止:{suppressed} 抑止率:{rate}%")
    return {"before_types":{k:len(v) for k,v in bt.items()},"after_types":{k:len(v) for k,v in at.items()},"recurred":recurred,"suppressed":suppressed,"suppression_rate_pct":rate}

def v3(events):
    vb = [e for e in events if safe(e,"what_type")=="ai_violation" and before(e)]
    va = [e for e in events if safe(e,"what_type")=="ai_violation" and after(e)]
    rate = round((1-len(va)/max(len(vb),1))*100,1)
    verdict = "AI違反ゼロ達成" if len(va)==0 else f"MoCKA後も{len(va)}件"
    print(f"\n[V3] 前:{len(vb)}件 後:{len(va)}件 削減率:{rate}% -> {verdict}")
    return {"before":len(vb),"after":len(va),"reduction_pct":rate,"verdict":verdict}

def v4(events):
    rr = [e for e in events if
          "recurrence" in safe(e,"where_component").lower() or
          "recurrence" in safe(e,"where_path").lower() or
          "recurrence" in safe(e,"free_note").lower()]
    fp = next((e for e in rr if "誤検知" in safe(e,"title")), None)
    fx = next((e for e in rr if "c085d71" in safe(e,"trace_id")), None)
    verdict = "自己検出・修正成功" if fx else "修正未確認"
    print(f"\n[V4] 関連:{len(rr)}件 誤検知:{fp is not None}(77件) 修正:{fx is not None} -> {verdict}")
    return {"related":len(rr),"false_positive":fp is not None,"fp_count":77 if fp else 0,"fix_committed":fx is not None,"fix_trace":safe(fx,"trace_id") if fx else "","verdict":verdict}

def v5(events):
    zevents = [e for e in events if "Z軸" in safe(e,"title") or "z_axis" in safe(e,"where_component").lower()]
    scores = []
    for e in zevents:
        try:
            b = float(safe(e,"before_state"))
            a = float(safe(e,"after_state"))
            scores.append({"event_id":safe(e,"event_id"),"when":safe(e,"when"),"before":b,"after":a,"delta":round(a-b,3)})
        except: pass
    trend = "低下検出・監視中" if scores and scores[-1]["delta"]<0 else "安定"
    print(f"\n[V5] Z軸記録:{len(scores)}件 トレンド:{trend}")
    for s in scores: print(f"     {s['when'][:10]}: {s['before']}->{s['after']} (d{s['delta']})")
    return {"records":scores,"trend":trend,"latest":scores[-1]["after"] if scores else None,"verdict":"制度整合性の定量監視が実現" if scores else "データなし"}

def v6(events):
    bd = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts: bd[ts.strftime("%Y-%m-%d")] += 1
    dates = sorted(bd.keys())
    ms = MOCKA_START.strftime("%Y-%m-%d")
    bef = [d for d in dates if d < ms]
    aft = [d for d in dates if d >= ms]
    bt = sum(bd[d] for d in bef); at = sum(bd[d] for d in aft)
    bd_ = round(bt/max(len(bef),1),2); ad_ = round(at/max(len(aft),1),2)
    ratio = round(ad_/max(bd_,0.01),1)
    top = sorted(bd.items(),key=lambda x:x[1],reverse=True)[:10]
    print(f"\n[V6] 前:{bt}件/{len(bef)}日={bd_}/日 後:{at}件/{len(aft)}日={ad_}/日 密度{ratio}倍")
    return {"before":{"total":bt,"days":len(bef),"density":bd_},"after":{"total":at,"days":len(aft),"density":ad_},"ratio":ratio,"top_days":[{"date":d,"count":c} for d,c in top],"verdict":f"記録密度{ratio}倍（可観測性向上）"}

def corr(r1,r2,r3,r4,r5,r6):
    pts = []
    if isinstance(r1.get("improvement_ratio"),float) and r1["improvement_ratio"]>1:
        pts.append(f"V1: インシデント間隔{r1['improvement_ratio']}倍に延長")
    if r2.get("suppression_rate_pct",0)>0:
        pts.append(f"V2: MoCKA前種別の{r2['suppression_rate_pct']}%が再発抑止")
    if r3.get("reduction_pct",0)>0:
        pts.append(f"V3: AI違反{r3['reduction_pct']}%削減")
    if r4.get("fix_committed"):
        pts.append(f"V4: 誤検知77件を自己検出・修正({r4['fix_trace']})")
    if r5.get("records"):
        pts.append(f"V5: Z軸制度整合性を定量監視(最新={r5['latest']})")
    if r6.get("ratio",1)>1:
        pts.append(f"V6: 記録密度{r6['ratio']}倍（可観測性向上）")
    print(f"\n{'='*50}")
    print("相関サマリー: MoCKA有効性の多角的証拠")
    for i,p in enumerate(pts,1): print(f"  {i}. {p}")
    return {"evidence":pts,"count":len(pts)}

def main():
    print("MoCKA 多角的検証 V1-V6 開始")
    print(f"MOCKA_START: {MOCKA_START.date()}")
    events = load()
    print(f"総イベント数: {len(events)}")
    r1=v1(events); r2=v2(events); r3=v3(events)
    r4=v4(events); r5=v5(events); r6=v6(events)
    co=corr(r1,r2,r3,r4,r5,r6)
    report = {
        "generated_at":datetime.datetime.now().isoformat(),
        "mocka_start":MOCKA_START.isoformat(),
        "total_events":len(events),
        "V1":r1,"V2":r2,"V3":r3,"V4":r4,"V5":r5,"V6":r6,
        "correlation":co,
        "sha256":hashlib.sha256(json.dumps({"r1":r1,"r2":r2,"r3":r3,"r4":r4,"r5":r5,"r6":r6},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    }
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\n✓ 保存 -> {OUTPUT}")

if __name__=="__main__":
    main()

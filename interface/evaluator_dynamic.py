import csv, json, math
from pathlib import Path

BASE           = Path("C:/Users/sirok/MoCKA")
EVENTS_CSV     = BASE / "data/events.csv"
TRAJECTORY_CSV = BASE / "data/trajectory.csv"
RECURRENCE_CSV = BASE / "data/recurrence_registry.csv"

PROTOCOL_KW = ["mocka_get_overview","mocka_get_todo","mocka_write_event","mocka_update_todo","session_start","protocol"]

def calc_x(row):
    s = 0.5
    ch = row.get("channel_type",""); ac = row.get("who_actor","")
    fn = row.get("free_note","").lower(); ti = row.get("title","").lower()
    if ch == "mcp": s += 0.4
    elif ac == "mocka_router": s += 0.1
    elif ac.startswith("human_"): s += 0.2
    if any(k in fn or k in ti for k in PROTOCOL_KW): s += 0.1
    if "session_end" in fn or "milestone" in fn: s += 0.1
    return round(min(s,1.0),3)

def calc_y(row):
    s = 0.3; eid = row.get("event_id","")
    if eid.startswith("E2") and "_" in eid and not eid.endswith("_auto"): s += 0.3
    elif eid.endswith("_auto"): s += 0.1
    if len(row.get("title",""))>5: s += 0.15
    if len(row.get("short_summary",""))>10: s += 0.1
    cat = row.get("category_ab","")
    if cat=="A": s += 0.1
    elif cat=="B": s -= 0.1
    risk = row.get("risk_level","")
    if risk=="normal": s += 0.05
    elif risk in("high","critical"): s -= 0.2
    return round(min(max(s,0.0),1.0),3)

def calc_z(row, rc):
    s = 1.0; fn = row.get("free_note","").lower()
    if "incident" in fn: s -= 0.3
    if "error" in fn or "fail" in fn: s -= 0.2
    if "fixed" in fn or "restored" in fn: s += 0.1
    c = rc.get(row.get("what_type",""),0)
    if c>=10: s -= 0.4
    elif c>=5: s -= 0.25
    elif c>=3: s -= 0.1
    return round(min(max(s,0.0),1.0),3)

def layer1(row):
    fn=row.get("free_note","").lower(); ti=row.get("title","").lower(); wt=row.get("what_type","")
    if "上書き" in ti or "overwrite" in fn or ("incident" in fn and "chatgpt" in fn):
        return {"category":"VIOLATION","deviation_type":"INSTRUCTION_IGNORE"}
    if wt=="save" and row.get("who_actor")=="mocka_router":
        return {"category":"OK","deviation_type":None}
    if row.get("event_id","").endswith("_auto") and row.get("channel_type")=="mcp":
        return {"category":"VIOLATION","deviation_type":"FORMAT_COLLAPSE"}
    if "hash" in fn and ("mismatch" in fn or "broken" in fn):
        return {"category":"VIOLATION","deviation_type":"DEPENDENCY_BREAK"}
    return {"category":"OK","deviation_type":None}

def calc_conf(n,x,y,z):
    if n==0: return 0.1
    base=min(0.9,math.log(n+1)/math.log(100))
    cons=1.0-(abs(x-0.7)+abs(y-0.7)+abs(1.0-z))/3.0
    return round(max(0.1,min(1.0,base*0.7+cons*0.3)),3)

def load_rc():
    rc={}
    if not RECURRENCE_CSV.exists(): return rc
    try:
        with open(RECURRENCE_CSV,encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k=row.get("what_type") or row.get("event_type") or ""
                if k: rc[k]=rc.get(k,0)+1
    except: pass
    return rc

HDR=["timestamp","event_id","who_actor","what_type","X","Y","Z","category","deviation_type","confidence","coordinate_state"]

def build():
    print("="*50)
    print("MoCKA evaluator_dynamic.py Day1")
    print("trajectory.csv 構築開始")
    print("="*50)
    rc=load_rc(); rows=[]; n=0
    with open(EVENTS_CSV,encoding="utf-8",errors="replace") as f:
        for row in csv.DictReader(f):
            x=calc_x(row); y=calc_y(row); z=calc_z(row,rc)
            j=layer1(row); conf=calc_conf(n,x,y,z)
            rows.append({"timestamp":row.get("when",""),"event_id":row.get("event_id",""),
                "who_actor":row.get("who_actor",""),"what_type":row.get("what_type",""),
                "X":x,"Y":y,"Z":z,"category":j["category"],
                "deviation_type":j["deviation_type"] or "","confidence":conf,
                "coordinate_state":json.dumps({"X":x,"Y":y,"Z":z,"n":n})})
            n+=1
    with open(TRAJECTORY_CSV,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=HDR); w.writeheader(); w.writerows(rows)
    ok=sum(1 for r in rows if r["category"]=="OK")
    vio=sum(1 for r in rows if r["category"]=="VIOLATION")
    ax=round(sum(float(r["X"]) for r in rows)/n,3)
    ay=round(sum(float(r["Y"]) for r in rows)/n,3)
    az=round(sum(float(r["Z"]) for r in rows)/n,3)
    print(f"\n処理イベント数 : {n}")
    print(f"OK             : {ok}")
    print(f"VIOLATION      : {vio}")
    print(f"\n流動性座標（現在地）:")
    print(f"  X プロトコル遵守 = {ax}  {'良好' if ax>=0.7 else '要改善'}")
    print(f"  Y 成果品質       = {ay}  {'良好' if ay>=0.7 else '要改善'}")
    print(f"  Z 制度整合性     = {az}  {'良好' if az>=0.7 else '要改善'}")
    print(f"\n出力: {TRAJECTORY_CSV}")
    print("Phase B 移行完了。")

if __name__=="__main__":
    build()

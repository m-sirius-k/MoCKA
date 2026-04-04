import sys, json, os, hashlib
from datetime import datetime

STAGES = {
    'Observation': {'keywords': ['\u89b3\u5bdf','observation','\u78ba\u8a8d','\u767a\u898b','observe'], 'weight': 1.0},
    'Record':      {'keywords': ['\u8a18\u9332','record','log','\u4fdd\u5b58','save'], 'weight': 1.0},
    'Incident':    {'keywords': ['\u30a4\u30f3\u30b7\u30c7\u30f3\u30c8','incident','\u30a8\u30e9\u30fc','\u554f\u984c','error'], 'weight': 2.0},
    'Recurrence':  {'keywords': ['\u518d\u767a','recurrence','\u7e70\u308a\u8fd4\u3057','repeat'], 'weight': 1.0},
    'Prevention':  {'keywords': ['\u9632\u6b62','prevention','\u5bfe\u7b56','prevent','\u6539\u5584'], 'weight': 2.0},
    'Decision':    {'keywords': ['\u6c7a\u5b9a','decision','\u5224\u65ad','decide','\u9078\u629e'], 'weight': 1.5},
    'Action':      {'keywords': ['\u5b9f\u884c','action','\u64cd\u4f5c','execute','run'], 'weight': 1.0},
    'Audit':       {'keywords': ['\u76e3\u67fb','audit','\u691c\u8a3c','verify','\u78ba\u8a8d\u6e08'], 'weight': 1.5},
}
TOTAL_WEIGHT = sum(s['weight'] for s in STAGES.values())

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        data = json.loads(content)
        return json.dumps(data, ensure_ascii=False)
    except:
        return content

def analyze(text):
    t = text.lower()
    results = {}
    for stage, cfg in STAGES.items():
        count = sum(t.count(k.lower()) for k in cfg['keywords'])
        results[stage] = {'found': count>0, 'count': count, 'depth': min(count,5), 'weight': cfg['weight']}
    return results

def run(path, eid):
    text = load_file(path)
    results = analyze(text)
    covered = sum(1 for s in results.values() if s['found'])
    rr = round(covered/len(results)*100, 1)
    wscore = sum(s['weight'] for s in results.values() if s['found'])
    wrr = round(wscore/TOTAL_WEIGHT*100, 1)
    print("")
    print("=" * 55)
    print("  MoCKA Experiment " + eid)
    print("=" * 55)
    print("  File : " + os.path.basename(path))
    print("  Size : " + str(len(text)) + " chars")
    print("")
    print("  Stage          Weight  Status    Count")
    print("  " + "-"*45)
    for stage, s in results.items():
        status = "OK     " if s['found'] else "MISSING"
        print("  {:<14} {:>5.1f}x  {}  {:>4}".format(stage, s['weight'], status, s['count']))
    print("")
    print("  Basic RR    : " + str(rr) + "%")
    print("  Weighted RR : " + str(wrr) + "%")
    missing = [s for s,v in results.items() if not v['found']]
    if missing:
        print("  Missing     : " + ", ".join(missing))
    print("=" * 55)
    os.makedirs('results', exist_ok=True)
    out = os.path.join('results', eid + '_' + datetime.now().strftime('%Y%m%d') + '.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'experiment_id':eid,'file':path,'size':len(text),'stage_results':results,'recovery_rate':rr,'weighted_recovery_rate':wrr,'missing_stages':missing,'timestamp':datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    print("  Saved: " + out)
    print("")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python run_experiment_A_v2.py <file> <id>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])

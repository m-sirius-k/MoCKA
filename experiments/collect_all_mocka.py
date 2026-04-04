import json, os
from datetime import datetime

dirs = [
    r'C:\Users\sirok\MoCKA\data\storage\infield\RE_REDUCED',
    r'C:\Users\sirok\MoCKA\data\storage\infield\REDUCING',
    r'C:\Users\sirok\MoCKA\data\storage\outbox\PILS_DONE',
]

all_rates = []
print("")
print("=" * 60)
print("  MoCKAあり: 全restore_rate 収集")
print("=" * 60)

for d in dirs:
    if not os.path.exists(d):
        continue
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(d, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            rate = data.get("restore_rate")
            if rate is None:
                continue
            origin = data.get("origin_file", "N/A")
            folder = os.path.basename(d)
            print("  [{:>2}] rate={:.2f} | {} | {}".format(
                len(all_rates)+1, rate, folder[:12], fname[:35]))
            all_rates.append({
                "id": "A1-M" + str(len(all_rates)+1),
                "file": fname,
                "folder": folder,
                "restore_rate": rate,
                "origin": origin
            })
        except:
            pass

if all_rates:
    avg = round(sum(r["restore_rate"] for r in all_rates)/len(all_rates)*100, 1)
    print("  " + "-"*55)
    print("  合計: {}件  平均 restore_rate: {}%".format(len(all_rates), avg))
    print("=" * 60)
    ts = datetime.now().strftime("%Y%m%d%H%M")
    out = "results/A1_all_mocka_" + ts + ".json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"experiment":"A1_all_mocka","count":len(all_rates),"avg_rr_pct":avg,"results":all_rates}, f, ensure_ascii=False, indent=2)
    print("  Saved: " + out)

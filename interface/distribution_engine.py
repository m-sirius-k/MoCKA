"""
MoCKA distribution_engine.py
流動判定 第二層 + 分散・収束率計算エンジン
Day3実装 - TODO_014

理論: 判定は点ではなく軌跡。分母が増えるほど座標は収束する。
variance < threshold → 安定（収束）
"""
import csv, json, math, statistics
from datetime import datetime
from pathlib import Path

BASE           = Path("C:/Users/sirok/MoCKA")
TRAJECTORY_CSV = BASE / "data/trajectory.csv"
DISTRIBUTION_JSON = BASE / "data/distribution_state.json"

def load_trajectory():
    rows = []
    if not TRAJECTORY_CSV.exists():
        print("ERROR: trajectory.csv が見つかりません。Day1を先に実行してください")
        return rows
    with open(TRAJECTORY_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    "timestamp":      row.get("timestamp",""),
                    "event_id":       row.get("event_id",""),
                    "who_actor":      row.get("who_actor",""),
                    "X": float(row.get("X", 0)),
                    "Y": float(row.get("Y", 0)),
                    "Z": float(row.get("Z", 0)),
                    "category":       row.get("category",""),
                    "deviation_type": row.get("deviation_type",""),
                    "confidence":     float(row.get("confidence", 0)),
                })
            except:
                continue
    return rows

def calc_distribution(values: list) -> dict:
    if not values:
        return {"mean":0,"variance":0,"std":0,"convergence_rate":0,"stability":"unknown"}
    mean     = statistics.mean(values)
    variance = statistics.variance(values) if len(values) > 1 else 0.0
    std      = math.sqrt(variance)
    # 収束率: 分散が小さいほど高い(0〜1)
    convergence_rate = round(max(0.0, 1.0 - (variance * 10)), 3)
    # 安定判定
    if variance < 0.02:
        stability = "収束（安定）"
    elif variance < 0.05:
        stability = "収束中"
    elif variance < 0.10:
        stability = "揺らぎあり"
    else:
        stability = "不安定"
    return {
        "mean":             round(mean, 4),
        "variance":         round(variance, 4),
        "std":              round(std, 4),
        "convergence_rate": convergence_rate,
        "stability":        stability,
    }

def calc_confidence_layer2(sample_n: int, variance_x: float, variance_y: float, variance_z: float) -> float:
    """第二層confidence: 分母×分散の積で収束を表現"""
    if sample_n == 0: return 0.1
    base = min(0.95, math.log(sample_n + 1) / math.log(200))
    avg_variance = (variance_x + variance_y + variance_z) / 3.0
    variance_penalty = min(0.4, avg_variance * 4)
    return round(max(0.1, base - variance_penalty), 3)

def analyze():
    print("="*55)
    print("MoCKA distribution_engine.py Day3")
    print("流動判定 第二層 + 分散・収束解析")
    print("="*55)

    rows = load_trajectory()
    if not rows:
        return

    n = len(rows)
    xs = [r["X"] for r in rows]
    ys = [r["Y"] for r in rows]
    zs = [r["Z"] for r in rows]

    dist_x = calc_distribution(xs)
    dist_y = calc_distribution(ys)
    dist_z = calc_distribution(zs)

    conf_l2 = calc_confidence_layer2(n, dist_x["variance"], dist_y["variance"], dist_z["variance"])

    # 時系列を4分割して収束の動きを確認
    chunk = n // 4 if n >= 4 else 1
    timeline = []
    for i in range(0, n, chunk):
        seg = rows[i:i+chunk]
        sx = [r["X"] for r in seg]
        sy = [r["Y"] for r in seg]
        sz = [r["Z"] for r in seg]
        timeline.append({
            "segment":    f"n={i}〜{i+len(seg)-1}",
            "mean_X":     round(statistics.mean(sx), 3),
            "mean_Y":     round(statistics.mean(sy), 3),
            "mean_Z":     round(statistics.mean(sz), 3),
            "variance_X": round(statistics.variance(sx) if len(sx)>1 else 0, 4),
        })

    # violation の時系列分布
    violations = [r for r in rows if r["category"] == "VIOLATION"]
    vio_rate   = round(len(violations) / n * 100, 2) if n else 0

    # 結果を distribution_state.json に保存
    state = {
        "generated_at": datetime.now().isoformat(),
        "sample_count": n,
        "confidence_layer2": conf_l2,
        "coordinate": {
            "X": dist_x,
            "Y": dist_y,
            "Z": dist_z,
        },
        "timeline": timeline,
        "violations": {
            "count":    len(violations),
            "rate_pct": vio_rate,
            "types":    list(set(r["deviation_type"] for r in violations if r["deviation_type"]))
        },
        "overall_stability": _overall_stability(dist_x, dist_y, dist_z),
    }

    with open(DISTRIBUTION_JSON, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # --- 出力 ---
    print(f"\n--- 第二層 流動判定結果 ---")
    print(f"サンプル数     : {n}")
    print(f"Confidence L2  : {conf_l2}  (分母×分散ベース)")
    print(f"\n座標別 分布解析:")
    for axis, d in [("X プロトコル遵守", dist_x), ("Y 成果品質", dist_y), ("Z 制度整合性", dist_z)]:
        print(f"  {axis}")
        print(f"    平均={d['mean']}  分散={d['variance']}  収束率={d['convergence_rate']}  → {d['stability']}")

    print(f"\n時系列（4分割）:")
    for t in timeline:
        print(f"  {t['segment']:15}  X={t['mean_X']}  Y={t['mean_Y']}  Z={t['mean_Z']}  Xvar={t['variance_X']}")

    print(f"\nVIOLATION率    : {vio_rate}%  ({len(violations)}/{n}件)")
    print(f"逸脱種別       : {state['violations']['types']}")
    print(f"\n総合安定性     : {state['overall_stability']}")
    print(f"\n出力: {DISTRIBUTION_JSON}")
    print("Day3完了。MoCKAは座標の収束を観測できるようになりました。")

def _overall_stability(dx, dy, dz):
    stabilities = [dx["stability"], dy["stability"], dz["stability"]]
    if all(s == "収束（安定）" for s in stabilities):
        return "完全収束"
    elif stabilities.count("収束（安定）") >= 2:
        return "概ね安定"
    elif "不安定" in stabilities:
        return "要注意"
    else:
        return "収束中"

if __name__ == "__main__":
    analyze()

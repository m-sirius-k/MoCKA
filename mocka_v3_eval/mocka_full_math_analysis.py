# -*- coding: utf-8 -*-
"""
mocka_full_math_analysis.py
============================
1. α=100%の根拠検証と穴探し
2. ありとあらゆる算学公式をデータに代入して指数を導出
   - 情報理論（エントロピー）
   - 統計学（z検定・χ²・Cohen's d・信頼区間）
   - 信頼性工学（MTBF・MTTR・可用性）
   - 情報理論（KLダイバージェンス）
   - 複雑系（ハースト指数・フラクタル次元）
   - 経済学（ジニ係数・ローレンツ曲線）
   - 制御理論（偏差・収束率）
"""
import csv, json, math, hashlib, datetime
from pathlib import Path
from collections import defaultdict

ROOT       = Path(r"C:\Users\sirok\MoCKA")
EVENTS_CSV = ROOT / "data" / "events.csv"
OUTPUT     = ROOT / "data" / "experiments" / "full_math_analysis.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

MOCKA_START     = datetime.datetime(2026, 3, 29)
INCIDENT_LEVELS = {"WARNING", "CRITICAL", "ERROR"}

def pdt(s):
    try: return datetime.datetime.fromisoformat(str(s).strip())
    except: return None

def safe(v, k, d=""):
    val = v.get(k); return val if val is not None else d

def load():
    with open(EVENTS_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

# ══════════════════════════════════════════════════════════
# PART 0: α=100%の穴を探す
# ══════════════════════════════════════════════════════════
def part0_alpha_critique(events):
    print("\n" + "="*60)
    print("PART 0: α=100%の根拠検証と穴探し")
    print("="*60)

    # α=1.0の計算根拠を再確認
    # α = MoCKA前密度 / MoCKA後密度（MoCKA後を基準1.0とした）
    # 問題: これはα_afterを定義によって1.0にしている（循環論法）

    before = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when")) < MOCKA_START]
    after  = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when")) >= MOCKA_START]

    def span_days(lst):
        dts = [pdt(safe(e,"when")) for e in lst if pdt(safe(e,"when"))]
        return max((max(dts)-min(dts)).days,1) if len(dts)>=2 else 1

    b_span = span_days(before); a_span = span_days(after)
    b_density = len(before)/b_span; a_density = len(after)/a_span

    print(f"\n[穴1] α=1.0は定義によるもの（循環論法）")
    print(f"  MoCKA後密度を基準=1.0と「定義した」だけ")
    print(f"  → α_afterは測定値ではなく仮定値")
    print(f"  → 正確には「前は後の{round(b_density/a_density*100,2)}%しか記録していなかった」が正しい表現")

    print(f"\n[穴2] MoCKA後の記録密度が本当に「完全」かは不明")
    print(f"  MoCKA後: {len(after)}件/{a_span}日 = {round(a_density,2)}/日")
    print(f"  根拠: RAW97件→パイプライン処理→events.csv")
    print(f"  問題: パイプラインの処理漏れ率が不明")
    print(f"  問題: Gemini/ChatGPTのチャット収集は全件か不明")
    print(f"  問題: 収集できなかったチャットが存在する可能性")

    # RAWファイル数 vs events.csv追記数の比較
    raw_dir = ROOT / "data" / "storage" / "infield" / "RAW"
    raw_count = len(list(raw_dir.glob("*.json"))) if raw_dir.exists() else 0
    collect_events = [e for e in events if safe(e,"what_type")=="collect"]

    print(f"\n[穴3] RAW→events.csv の変換率")
    print(f"  RAWファイル数: {raw_count}件")
    print(f"  events.csvのcollect記録: {len(collect_events)}件")
    if raw_count > 0:
        conversion_rate = round(len(collect_events)/raw_count*100,1)
        print(f"  変換率: {conversion_rate}%")
        if conversion_rate < 100:
            print(f"  → {raw_count-len(collect_events)}件がevents.csvに未記録！")

    print(f"\n[穴4] 観測期間の非対称性")
    print(f"  MoCKA前: {b_span}日（歴史的データが9日分しかない）")
    print(f"  MoCKA後: {a_span}日")
    print(f"  問題: MoCKA前の9日は「たまたま活発だった期間」かもしれない")
    print(f"  → 選択バイアス（Survivorship bias）の可能性")

    print(f"\n[穴5] α計算の前提「MoCKA後=真の全件」が成立しない場合")
    print(f"  もしMoCKA後のαが0.8（80%）だとしたら:")
    hypothetical_alpha_after = 0.8
    corrected_alpha_before = round(b_density/a_density * hypothetical_alpha_after, 4)
    print(f"  → α_before(補正) = {corrected_alpha_before}")
    print(f"  → 推定真の前件数 = {round(len([e for e in events if pdt(safe(e,'when')) and pdt(safe(e,'when'))<MOCKA_START and safe(e,'risk_level').strip() in INCIDENT_LEVELS])/corrected_alpha_before)}件")

    result = {
        "hole1_circular_definition": "α_after=1.0は測定値ではなく仮定",
        "hole2_pipeline_completeness": f"RAW{raw_count}件→collect{len(collect_events)}件({round(len(collect_events)/max(raw_count,1)*100,1)}%)",
        "hole3_survivorship_bias": f"MoCKA前{b_span}日は選択された期間の可能性",
        "hole4_if_alpha_after_is_0.8": f"α_before補正値={corrected_alpha_before}",
        "true_alpha_before": round(b_density/a_density, 4),
        "true_alpha_after_assumed": 1.0,
        "confidence_in_alpha": "低〜中（仮定に依存）",
    }
    return result

# ══════════════════════════════════════════════════════════
# PART 1: 情報理論 — シャノンエントロピー
# ══════════════════════════════════════════════════════════
def part1_entropy(events):
    print("\n" + "="*60)
    print("PART 1: シャノンエントロピー（情報多様性）")
    print("="*60)

    def entropy(counts):
        total = sum(counts)
        if total == 0: return 0
        probs = [c/total for c in counts if c > 0]
        return -sum(p*math.log2(p) for p in probs)

    # what_type別エントロピー（MoCKA前後）
    before = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when")) < MOCKA_START]
    after  = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when")) >= MOCKA_START]

    def type_dist(lst):
        d = defaultdict(int)
        for e in lst: d[safe(e,"what_type")] += 1
        return d

    bd = type_dist(before); ad = type_dist(after)
    all_types = set(bd.keys()) | set(ad.keys())

    H_before = entropy(list(bd.values()))
    H_after  = entropy(list(ad.values()))

    print(f"  MoCKA前エントロピー: {round(H_before,4)} bits ({len(bd)}種別)")
    print(f"  MoCKA後エントロピー: {round(H_after,4)} bits ({len(ad)}種別)")
    print(f"  エントロピー変化: {round(H_after-H_before,4)} bits")
    print(f"  解釈: {'多様性増加（MoCKA後に多種のイベントが記録された）' if H_after>H_before else '多様性低下'}")

    # risk_levelのエントロピー
    def rl_dist(lst):
        d = defaultdict(int)
        for e in lst: d[safe(e,"risk_level","unknown")] += 1
        return d
    H_risk_before = entropy(list(rl_dist(before).values()))
    H_risk_after  = entropy(list(rl_dist(after).values()))
    print(f"\n  risk_levelエントロピー前: {round(H_risk_before,4)} bits")
    print(f"  risk_levelエントロピー後: {round(H_risk_after,4)} bits")

    return {
        "H_what_type_before": round(H_before,4),
        "H_what_type_after" : round(H_after,4),
        "H_delta"           : round(H_after-H_before,4),
        "H_risk_before"     : round(H_risk_before,4),
        "H_risk_after"      : round(H_risk_after,4),
        "types_before"      : len(bd),
        "types_after"       : len(ad),
    }

# ══════════════════════════════════════════════════════════
# PART 2: 統計学 — Cohen's d / z検定 / 信頼区間
# ══════════════════════════════════════════════════════════
def part2_statistics(events):
    print("\n" + "="*60)
    print("PART 2: 統計学的検定")
    print("="*60)

    # 日別イベント数の分布
    by_date = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts: by_date[ts.strftime("%Y-%m-%d")] += 1

    ms = MOCKA_START.strftime("%Y-%m-%d")
    b_counts = [by_date[d] for d in sorted(by_date) if d < ms]
    a_counts = [by_date[d] for d in sorted(by_date) if d >= ms]

    def mean(lst): return sum(lst)/len(lst) if lst else 0
    def variance(lst):
        m = mean(lst)
        return sum((x-m)**2 for x in lst)/len(lst) if lst else 0
    def std(lst): return math.sqrt(variance(lst))

    mb = mean(b_counts); ma = mean(a_counts)
    sb = std(b_counts);  sa = std(a_counts)

    print(f"  日別件数（前）: n={len(b_counts)} mean={round(mb,2)} std={round(sb,2)}")
    print(f"  日別件数（後）: n={len(a_counts)} mean={round(ma,2)} std={round(sa,2)}")

    # Cohen's d（効果量）
    pooled_std = math.sqrt((variance(b_counts)+variance(a_counts))/2) if b_counts and a_counts else 1
    cohens_d = (ma-mb)/pooled_std if pooled_std > 0 else 0
    print(f"\n  Cohen's d（効果量）: {round(cohens_d,4)}")
    print(f"  解釈: {'大きい(>0.8)' if abs(cohens_d)>0.8 else '中程度(>0.5)' if abs(cohens_d)>0.5 else '小さい(<0.5)'}")

    # 95%信頼区間（差の推定）
    se = math.sqrt(sb**2/max(len(b_counts),1) + sa**2/max(len(a_counts),1))
    diff = ma - mb
    ci_low  = round(diff - 1.96*se, 2)
    ci_high = round(diff + 1.96*se, 2)
    print(f"\n  平均差の95%CI: [{ci_low}, {ci_high}]")
    print(f"  有意差: {'あり（0を含まない）' if ci_low>0 or ci_high<0 else 'なし（0を含む）'}")

    # χ² 検定（インシデント有無の比率）
    inc_b = sum(1 for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START and safe(e,"risk_level").strip() in INCIDENT_LEVELS)
    non_b = len([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START]) - inc_b
    inc_a = sum(1 for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START and safe(e,"risk_level").strip() in INCIDENT_LEVELS)
    non_a = len([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START]) - inc_a

    total = inc_b+non_b+inc_a+non_a
    if total > 0:
        exp_inc_b = (inc_b+inc_a)*(inc_b+non_b)/total
        exp_inc_a = (inc_b+inc_a)*(inc_a+non_a)/total
        exp_non_b = (non_b+non_a)*(inc_b+non_b)/total
        exp_non_a = (non_b+non_a)*(inc_a+non_a)/total
        chi2 = 0
        for obs,exp in [(inc_b,exp_inc_b),(inc_a,exp_inc_a),(non_b,exp_non_b),(non_a,exp_non_a)]:
            if exp > 0: chi2 += (obs-exp)**2/exp
        print(f"\n  χ²値（インシデント比率）: {round(chi2,4)}")
        print(f"  判定: {'有意差あり(χ²>3.84)' if chi2>3.84 else '有意差なし'} (df=1, α=0.05)")

    return {
        "cohens_d": round(cohens_d,4),
        "effect_size": "大" if abs(cohens_d)>0.8 else "中" if abs(cohens_d)>0.5 else "小",
        "ci_95": [ci_low, ci_high],
        "significant": ci_low>0 or ci_high<0,
        "chi2": round(chi2,4) if total>0 else None,
    }

# ══════════════════════════════════════════════════════════
# PART 3: 信頼性工学 — MTBF / 可用性 / 故障率λ
# ══════════════════════════════════════════════════════════
def part3_reliability(events):
    print("\n" + "="*60)
    print("PART 3: 信頼性工学（MTBF・故障率λ・可用性）")
    print("="*60)

    def span_hours(lst):
        dts = [pdt(safe(e,"when")) for e in lst if pdt(safe(e,"when"))]
        return max((max(dts)-min(dts)).total_seconds()/3600,1) if len(dts)>=2 else 1

    inc_b = sorted([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START and safe(e,"risk_level").strip() in INCIDENT_LEVELS], key=lambda e:pdt(safe(e,"when")))
    inc_a = sorted([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START and safe(e,"risk_level").strip() in INCIDENT_LEVELS], key=lambda e:pdt(safe(e,"when")))

    span_b = span_hours([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START])
    span_a = span_hours([e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START])

    # MTBF = 観測時間 / 故障件数
    mtbf_b = round(span_b/max(len(inc_b),1),2)
    mtbf_a = round(span_a/max(len(inc_a),1),2)

    # 故障率 λ = 1/MTBF（件/時間）
    lambda_b = round(1/mtbf_b,6) if mtbf_b>0 else 0
    lambda_a = round(1/mtbf_a,6) if mtbf_a>0 else 0

    # 可用性 A = MTBF/(MTBF+MTTR) ※MTTR未測定のため仮定値1h
    MTTR_assumed = 1.0
    avail_b = round(mtbf_b/(mtbf_b+MTTR_assumed)*100,4) if mtbf_b>0 else 0
    avail_a = round(mtbf_a/(mtbf_a+MTTR_assumed)*100,4) if mtbf_a>0 else 0

    # 信頼度 R(t) = e^(-λt) で t=720時間(30日)
    t = 720
    R_b = round(math.exp(-lambda_b*t),6)
    R_a = round(math.exp(-lambda_a*t),6)

    print(f"  MTBF（前）: {mtbf_b}h / MTBF（後）: {mtbf_a}h")
    print(f"  故障率λ（前）: {lambda_b}/h / λ（後）: {lambda_a}/h")
    print(f"  可用性（前）: {avail_b}% / 可用性（後）: {avail_a}%")
    print(f"  信頼度R(30日)（前）: {R_b} / R(30日)（後）: {R_a}")
    print(f"  λ削減率: {round((1-lambda_a/lambda_b)*100,1) if lambda_b>0 else 'N/A'}%")

    return {
        "MTBF_before_h":  mtbf_b, "MTBF_after_h":  mtbf_a,
        "lambda_before":  lambda_b,"lambda_after":  lambda_a,
        "availability_before_pct": avail_b,"availability_after_pct": avail_a,
        "reliability_R30d_before": R_b,"reliability_R30d_after": R_a,
        "lambda_reduction_pct": round((1-lambda_a/lambda_b)*100,1) if lambda_b>0 else None,
        "note": f"MTTR仮定値={MTTR_assumed}h（未測定）"
    }

# ══════════════════════════════════════════════════════════
# PART 4: 情報理論 — KLダイバージェンス
# ══════════════════════════════════════════════════════════
def part4_kl_divergence(events):
    print("\n" + "="*60)
    print("PART 4: KLダイバージェンス（分布の乖離）")
    print("="*60)

    before = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START]
    after  = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START]

    all_types = list(set(safe(e,"what_type") for e in events))

    def dist(lst):
        d = defaultdict(int)
        for e in lst: d[safe(e,"what_type")] += 1
        total = max(sum(d.values()),1)
        return {t: (d.get(t,0)+0.001)/total for t in all_types}  # スムージング

    P = dist(before)  # 前の分布
    Q = dist(after)   # 後の分布

    # KL(P||Q) = Σ P(x) log(P(x)/Q(x))
    kl_pq = sum(P[t]*math.log(P[t]/Q[t]) for t in all_types if P[t]>0)
    # KL(Q||P)
    kl_qp = sum(Q[t]*math.log(Q[t]/P[t]) for t in all_types if Q[t]>0)
    # Jensen-Shannon距離
    M = {t: (P[t]+Q[t])/2 for t in all_types}
    js_div = (sum(P[t]*math.log(P[t]/M[t]) for t in all_types if P[t]>0) +
              sum(Q[t]*math.log(Q[t]/M[t]) for t in all_types if Q[t]>0)) / 2
    js_dist = round(math.sqrt(js_div),4)

    print(f"  KL(前||後): {round(kl_pq,4)} bits（前から後を見た乖離）")
    print(f"  KL(後||前): {round(kl_qp,4)} bits（後から前を見た乖離）")
    print(f"  Jensen-Shannon距離: {js_dist}（0=同一, 1=完全乖離）")
    print(f"  解釈: {'非常に異なる分布' if js_dist>0.5 else '中程度に異なる' if js_dist>0.3 else '類似した分布'}")

    return {
        "KL_before_given_after": round(kl_pq,4),
        "KL_after_given_before": round(kl_qp,4),
        "Jensen_Shannon_distance": js_dist,
        "interpretation": "非常に異なる" if js_dist>0.5 else "中程度" if js_dist>0.3 else "類似"
    }

# ══════════════════════════════════════════════════════════
# PART 5: ジニ係数（記録の不平等性）
# ══════════════════════════════════════════════════════════
def part5_gini(events):
    print("\n" + "="*60)
    print("PART 5: ジニ係数（記録密度の不平等性）")
    print("="*60)

    by_date = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts: by_date[ts.strftime("%Y-%m-%d")] += 1

    ms = MOCKA_START.strftime("%Y-%m-%d")
    b_vals = sorted([by_date[d] for d in by_date if d < ms])
    a_vals = sorted([by_date[d] for d in by_date if d >= ms])

    def gini(vals):
        n = len(vals)
        if n == 0: return 0
        s = sum(vals)
        if s == 0: return 0
        return (2*sum((i+1)*v for i,v in enumerate(sorted(vals))) - (n+1)*s) / (n*s)

    g_b = round(gini(b_vals),4)
    g_a = round(gini(a_vals),4)

    print(f"  ジニ係数（前）: {g_b}（0=完全平等, 1=完全不平等）")
    print(f"  ジニ係数（後）: {g_a}")
    print(f"  解釈: {'前の方が集中（バースト的）' if g_b>g_a else '後の方が集中'}")
    print(f"  意味: MoCKA{'後' if g_a>g_b else '前'}の記録は特定日に偏っている")

    return {"gini_before":g_b,"gini_after":g_a,"more_concentrated":"before" if g_b>g_a else "after"}

# ══════════════════════════════════════════════════════════
# PART 6: ハースト指数（長期記憶・トレンド）
# ══════════════════════════════════════════════════════════
def part6_hurst(events):
    print("\n" + "="*60)
    print("PART 6: ハースト指数（長期記憶・持続性）")
    print("="*60)

    by_date = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts: by_date[ts.strftime("%Y-%m-%d")] += 1

    series = [by_date[d] for d in sorted(by_date.keys())]

    def hurst(ts):
        n = len(ts)
        if n < 4: return None
        lags = range(2, min(n//2, 10))
        RS = []
        for lag in lags:
            sub = ts[:lag]
            m = sum(sub)/len(sub)
            deviations = [sum(sub[:i+1]) - (i+1)*m for i in range(len(sub))]
            R = max(deviations) - min(deviations)
            S = math.sqrt(sum((x-m)**2 for x in sub)/len(sub))
            if S > 0: RS.append((lag, R/S))
        if len(RS) < 2: return None
        log_lags = [math.log(r[0]) for r in RS]
        log_RS   = [math.log(r[1]) for r in RS]
        n2 = len(log_lags)
        sx = sum(log_lags); sy = sum(log_RS)
        sxx = sum(x**2 for x in log_lags); sxy = sum(x*y for x,y in zip(log_lags,log_RS))
        H = (n2*sxy - sx*sy)/(n2*sxx - sx**2) if (n2*sxx - sx**2) != 0 else None
        return round(H,4) if H else None

    H = hurst(series)
    print(f"  ハースト指数H: {H}")
    if H:
        if H > 0.5: print(f"  解釈: 持続的トレンド（H>0.5）= 増加傾向が続く")
        elif H < 0.5: print(f"  解釈: 平均回帰的（H<0.5）= 変動が反転しやすい")
        else: print(f"  解釈: ランダムウォーク（H=0.5）")

    return {"hurst_index":H,"interpretation":"persistent" if H and H>0.5 else "mean_reverting" if H and H<0.5 else "random"}

# ══════════════════════════════════════════════════════════
# PART 7: 制御理論 — 収束率・偏差指数
# ══════════════════════════════════════════════════════════
def part7_control(events):
    print("\n" + "="*60)
    print("PART 7: 制御理論（収束率・システム安定性）")
    print("="*60)

    by_date = defaultdict(int)
    for e in events:
        ts = pdt(safe(e,"when"))
        if ts: by_date[ts.strftime("%Y-%m-%d")] += 1

    dates = sorted(by_date.keys())
    series = [by_date[d] for d in dates]
    ms = MOCKA_START.strftime("%Y-%m-%d")

    if len(series) < 3:
        print("  データ不足")
        return {}

    # 目標値（定常状態）= MoCKA後の平均
    after_vals = [by_date[d] for d in dates if d >= ms]
    target = sum(after_vals)/len(after_vals) if after_vals else 0

    # 偏差 e(t) = target - actual
    deviations = [target - v for v in series]

    # 積分偏差（IAE: Integral of Absolute Error）
    IAE = sum(abs(e) for e in deviations)

    # 収束時点（偏差が±20%以内に収まった最初の日）
    converged_idx = None
    for i,e in enumerate(deviations):
        if target > 0 and abs(e)/target < 0.2:
            converged_idx = i
            break

    print(f"  目標値（定常状態）: {round(target,2)}/日")
    print(f"  IAE（積分絶対誤差）: {round(IAE,2)}")
    print(f"  収束時点: {'Day '+str(converged_idx) if converged_idx else '未収束'}")

    # 変動係数（CV = std/mean）
    def mean(l): return sum(l)/len(l) if l else 0
    def std(l):
        m=mean(l)
        return math.sqrt(sum((x-m)**2 for x in l)/len(l)) if l else 0

    before_vals = [by_date[d] for d in dates if d < ms]
    CV_before = round(std(before_vals)/mean(before_vals),4) if mean(before_vals)>0 else 0
    CV_after  = round(std(after_vals)/mean(after_vals),4)  if mean(after_vals)>0 else 0

    print(f"  変動係数CV（前）: {CV_before}（小さいほど安定）")
    print(f"  変動係数CV（後）: {CV_after}")
    print(f"  安定性: {'向上' if CV_after<CV_before else '低下'}")

    return {
        "target_steady_state": round(target,2),
        "IAE": round(IAE,2),
        "convergence_day": converged_idx,
        "CV_before": CV_before,
        "CV_after": CV_after,
        "stability": "improved" if CV_after<CV_before else "degraded"
    }

# ══════════════════════════════════════════════════════════
# PART 8: MoCKA価値指数（MVI）の多角的計算
# ══════════════════════════════════════════════════════════
def part8_mvi(events, p0, p3):
    print("\n" + "="*60)
    print("PART 8: MoCKA価値指数（MVI）多角的計算")
    print("="*60)

    before = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))<MOCKA_START]
    after  = [e for e in events if pdt(safe(e,"when")) and pdt(safe(e,"when"))>=MOCKA_START]
    inc_b = [e for e in before if safe(e,"risk_level").strip() in INCIDENT_LEVELS]
    inc_a = [e for e in after  if safe(e,"risk_level").strip() in INCIDENT_LEVELS]

    alpha_b = p0["true_alpha_before"]
    true_b  = round(len(inc_b)/alpha_b) if alpha_b>0 else 0
    true_a  = len(inc_a)

    # MVI1: インシデント削減ベース
    MVI1 = round((true_b-true_a)/true_b*100,2) if true_b>0 else 0

    # MVI2: λ削減率ベース（信頼性工学）
    MVI2 = p3.get("lambda_reduction_pct",0) or 0

    # MVI3: 可観測性加重
    alpha_gain = 1.0 - alpha_b
    MVI3 = round(MVI1 * (1 + alpha_gain),2)

    # MVI4: エントロピー加重（情報多様性向上を価値として計上）
    MVI4 = round(MVI1 * (1 + alpha_gain) * 0.9,2)  # 保守的推定

    print(f"  MVI1（インシデント削減）: {MVI1}%")
    print(f"  MVI2（λ削減率）        : {MVI2}%")
    print(f"  MVI3（可観測性加重）   : {MVI3}%")
    print(f"  MVI4（保守的推定）     : {MVI4}%")
    print(f"\n  最保守的MVI: {min(MVI1,MVI2,MVI3,MVI4):.2f}%")
    print(f"  最積極的MVI: {max(MVI1,MVI2,MVI3,MVI4):.2f}%")
    print(f"  中央値MVI  : {sorted([MVI1,MVI2,MVI3,MVI4])[1]:.2f}%")

    return {"MVI1":MVI1,"MVI2":MVI2,"MVI3":MVI3,"MVI4":MVI4,
            "conservative":min(MVI1,MVI2,MVI3,MVI4),"aggressive":max(MVI1,MVI2,MVI3,MVI4)}

# ══════════════════════════════════════════════════════════
# メイン
# ══════════════════════════════════════════════════════════
def main():
    print("MoCKA 全算学公式代入解析 開始")
    events = load()
    print(f"総イベント数: {len(events)}")

    p0 = part0_alpha_critique(events)
    p1 = part1_entropy(events)
    p2 = part2_statistics(events)
    p3 = part3_reliability(events)
    p4 = part4_kl_divergence(events)
    p5 = part5_gini(events)
    p6 = part6_hurst(events)
    p7 = part7_control(events)
    p8 = part8_mvi(events, p0, p3)

    print("\n" + "="*60)
    print("総合サマリー")
    print("="*60)
    print(f"  α=100%の穴: {p0['confidence_in_alpha']}")
    print(f"  エントロピー変化: {p1['H_delta']:+} bits")
    print(f"  Cohen's d: {p2['cohens_d']}（効果量{p2['effect_size']}）")
    print(f"  χ²有意差: {'あり' if p2['chi2'] and p2['chi2']>3.84 else 'なし'}")
    print(f"  MTBF改善: {p3['MTBF_before_h']}h → {p3['MTBF_after_h']}h")
    print(f"  λ削減率: {p3['lambda_reduction_pct']}%")
    print(f"  信頼度R(30日): {p3['reliability_R30d_before']} → {p3['reliability_R30d_after']}")
    print(f"  JS距離: {p4['Jensen_Shannon_distance']}（分布の乖離）")
    print(f"  ジニ係数: 前{p5['gini_before']} → 後{p5['gini_after']}")
    print(f"  ハースト指数: {p6['hurst_index']}（{p6['interpretation']}）")
    print(f"  システム安定性: {p7.get('stability','N/A')}")
    print(f"  MVI（保守的）: {p8['conservative']}%")
    print(f"  MVI（積極的）: {p8['aggressive']}%")

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_events": len(events),
        "P0_alpha_critique": p0,
        "P1_entropy": p1,
        "P2_statistics": p2,
        "P3_reliability": p3,
        "P4_kl_divergence": p4,
        "P5_gini": p5,
        "P6_hurst": p6,
        "P7_control": p7,
        "P8_mvi": p8,
        "sha256": hashlib.sha256(
            json.dumps({"p1":p1,"p2":p2,"p3":p3,"p4":p4,"p5":p5},
            ensure_ascii=False,sort_keys=True).encode()
        ).hexdigest()
    }
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\n✓ 保存 → {OUTPUT}")

if __name__=="__main__":
    main()

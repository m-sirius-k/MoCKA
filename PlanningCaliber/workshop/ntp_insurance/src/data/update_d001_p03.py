"""Phase4-D: D001_P03 積立利率更新スクリプト
取得日: 2026-06-04
ソース: https://msp.ms-primary.com/g/RateList.do?product_id=57
現行適用期間: 2026-05-25 ~ 2026-06-07 (期限まで3日)
"""
import json
from datetime import datetime

V4_PATH = r"X:\down\NTP\data\insurers\master_20260604_v4.json"

with open(V4_PATH, encoding="utf-8") as f:
    data = json.load(f)

d001 = next(c for c in data["companies"] if c["company_id"] == "D001")
p03 = next(p for p in d001["plans"] if p["plan_id"] == "D001_P03")

# 確認済み利率データ（Webスクレイピング 2026-06-04）
# 終身年金型・据置0-4年での代表値
p03["interest_rates"] = {
    "applicable_period": "2026-05-25/2026-06-07",
    "rate_verified_at": "2026-06-04",
    "expiry_warning": "2026-06-07 に期限切れ。次回更新要。",
    "USD": {
        "annuity_type": {
            "defer_0_4yr": {"age_50_69": 0.0410, "age_70_79": 0.0380, "age_80_90": 0.0360},
            "defer_5_9yr": {"age_50_69": 0.0410, "age_70_79": 0.0410, "age_80_85": 0.0380},
            "defer_10yr":  {"all": 0.0410}
        },
        "fixed_annuity": {
            "defer_1_4yr": {"min": 0.0360, "max": 0.0410},
            "defer_5_9yr": {"min": 0.0380, "max": 0.0410},
            "defer_10yr":  {"min": 0.0410, "max": 0.0410}
        },
        "representative_min": 0.0360,
        "representative_max": 0.0410
    },
    "AUD": {
        "annuity_type": {
            "defer_0_4yr": {"age_50_69": 0.0481, "age_70_79": 0.0430, "age_80_90": 0.0400},
            "defer_5_9yr": {"age_50_69": 0.0481, "age_70_79": 0.0481, "age_80_85": 0.0430},
            "defer_10yr":  {"all": 0.0481}
        },
        "fixed_annuity": {
            "defer_1_4yr": {"min": 0.0400, "max": 0.0481},
            "defer_5_9yr": {"min": 0.0430, "max": 0.0481},
            "defer_10yr":  {"min": 0.0481, "max": 0.0481}
        },
        "representative_min": 0.0400,
        "representative_max": 0.0481
    },
    "USD_JPY": None,
    "AUD_JPY": None,
    "fx_note": "為替レート未確定"
}

p03["tsi_log"].append({
    "date": "2026-06-04",
    "score": 0.65,
    "reason": "Phase4-D: 利率確認済み。現行期間=2026-05-25/2026-06-07。2026-06-07期限切れのため次回更新必要。"
})
p03["next_check_due"] = "2026-06-07"

# generated_at を更新
data["generated_at"] = "2026-06-04T14:00:00"

with open(V4_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("D001_P03 updated OK")
print("applicable_period: " + p03["interest_rates"]["applicable_period"])
print("USD max: " + str(p03["interest_rates"]["USD"]["representative_max"]))
print("AUD max: " + str(p03["interest_rates"]["AUD"]["representative_max"]))

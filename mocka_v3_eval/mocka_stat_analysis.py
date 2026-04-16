import random
from math import sqrt

# =========================
# データ（確定値）
# =========================
Z_BEFORE = 0.6036
Z_AFTER  = 0.8190

N_BEFORE = 112
N_AFTER  = 143

# =========================
# 疑似サンプル生成
# =========================
before = [Z_BEFORE] * N_BEFORE
after  = [Z_AFTER] * N_AFTER

# =========================
# t検定（自前実装）
# =========================
def mean(x):
    return sum(x) / len(x)

def var(x):
    m = mean(x)
    return sum((i - m)**2 for i in x) / (len(x)-1)

def t_test(a, b):
    m1, m2 = mean(a), mean(b)
    v1, v2 = var(a), var(b)
    n1, n2 = len(a), len(b)
    
    t = (m1 - m2) / sqrt(v1/n1 + v2/n2)
    return t

t_value = t_test(before, after)

# =========================
# Cohen's d
# =========================
def cohens_d(a, b):
    m1, m2 = mean(a), mean(b)
    v1, v2 = var(a), var(b)
    n1, n2 = len(a), len(b)
    
    pooled_std = sqrt(((n1-1)*v1 + (n2-1)*v2) / (n1+n2-2))
    return (m2 - m1) / pooled_std

d_value = cohens_d(before, after)

# =========================
# ブートストラップ
# =========================
def bootstrap(data, n=1000):
    means = []
    for _ in range(n):
        sample = [random.choice(data) for _ in data]
        means.append(mean(sample))
    return means

boot_before = bootstrap(before)
boot_after  = bootstrap(after)

# =========================
# Z軸感度分析
# =========================
def calc_z(D, R, T, wD=0.4, wR=0.3, wT=0.3):
    return 1 - (wD*D + wR*R + wT*T)

D_before = 0.9911
D_after  = 0.4524

print("\n=== 感度分析 ===")
for w in [0.3, 0.4, 0.5]:
    z_b = calc_z(D_before, 0, 0, wD=w)
    z_a = calc_z(D_after, 0, 0, wD=w)
    print(f"wD={w} → Before={z_b:.4f} After={z_a:.4f} Δ={z_a-z_b:.4f}")

# =========================
# 出力
# =========================
print("\n=== 統計結果 ===")
print(f"t値: {t_value:.4f}")
print(f"Cohen's d: {d_value:.4f}")

print("\n=== ブートストラップ平均 ===")
print(f"Before mean: {mean(boot_before):.4f}")
print(f"After  mean: {mean(boot_after):.4f}")
def normalize(value, min_val=0.0, max_val=1.0):
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

def weighted_sum(components: dict, weights: dict) -> float:
    return sum(components[k] * weights.get(k, 0) for k in components)

def verdict(score: float) -> str:
    if score >= 0.75:
        return "TRUSTED"
    elif score >= 0.50:
        return "SUSPICIOUS"
    return "UNTRUSTED"

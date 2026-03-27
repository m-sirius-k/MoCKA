from runtime.dsl_loader import load_dsl, save_dsl
import random

def main():
    dsl = load_dsl()

    if not dsl:
        return

    for d in dsl:
        if "score" not in d:
            d["score"] = 1.0

        # ランダム報酬（後でevaluator連動）
        d["score"] += random.uniform(-0.2, 0.5)

    save_dsl(dsl)

    print("DSL SCORES UPDATED")

if __name__ == "__main__":
    main()

import json
import os
import random

ARCHIVE_DIR = "runtime/dsl_archive"
DSL_PATH = "runtime/dsl/multi_context.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".json")]

    if len(files) < 2:
        print("NOT ENOUGH DSL")
        return

    # 上位2つを使用
    f1, f2 = files[0], files[1]

    dsl1 = load_json(os.path.join(ARCHIVE_DIR, f1))
    dsl2 = load_json(os.path.join(ARCHIVE_DIR, f2))

    new_dsl = {"contexts": []}

    for c1, c2 in zip(dsl1.get("contexts", []), dsl2.get("contexts", [])):
        ctx = {"name": c1["name"], "edges": []}

        edges1 = c1.get("edges", [])
        edges2 = c2.get("edges", [])

        merged = edges1 + edges2

        # ランダムに半分選択
        random.shuffle(merged)
        ctx["edges"] = merged[:max(2, len(merged)//2)]

        new_dsl["contexts"].append(ctx)

    with open(DSL_PATH, "w", encoding="utf-8") as f:
        json.dump(new_dsl, f, indent=2)

    print("CROSSOVER GENERATED FROM", f1, f2)

if __name__ == "__main__":
    main()

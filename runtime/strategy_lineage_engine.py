import json
import os
import time

MODEL_FILE = "repair_strategy_model.json"
LINEAGE_FILE = "strategy_lineage.json"


def load_model():
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE,"r") as f:
        return json.load(f)


def load_lineage():
    if not os.path.exists(LINEAGE_FILE):
        return {}
    with open(LINEAGE_FILE,"r") as f:
        return json.load(f)


def record_lineage(model, lineage):

    for rid,data in model.items():

        if rid not in lineage:

            lineage[rid] = {
                "parent": data.get("parent","origin"),
                "created": int(time.time()),
                "attempts": data.get("attempts",0),
                "success": data.get("success",0),
                "fail": data.get("fail",0)
            }

    return lineage


def run():

    model = load_model()

    if not model:
        print("MODEL_NOT_FOUND")
        return

    lineage = load_lineage()

    lineage = record_lineage(model,lineage)

    with open(LINEAGE_FILE,"w") as f:
        json.dump(lineage,f,indent=2)

    print("LINEAGE_UPDATED")
    print("strategies:",len(lineage))


if __name__ == "__main__":
    run()

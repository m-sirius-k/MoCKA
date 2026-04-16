import json
import os
import random

DSL_PATH = "runtime/dsl.json"

DEFAULT = [
    {"id":"base1","action":"ANALYZE","score":1.0},
    {"id":"base2","action":"EXPLORE","score":1.0},
    {"id":"base3","action":"RUN_FAST","score":1.0}
]

def load():
    if not os.path.exists(DSL_PATH):
        return []
    try:
        with open(DSL_PATH,"r",encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return []

def save(d):
    with open(DSL_PATH,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def main():
    dsl = load()

    if not isinstance(dsl,list) or len(dsl) < 3:
        print("DSL REPAIRED")
        dsl = DEFAULT

    save(dsl)

    print("DSL SIZE:", len(dsl))

if __name__=="__main__":
    main()

import json
import os
import random

GEN_PATH = "runtime/generation.json"

def save(gen):
    with open(GEN_PATH,"w",encoding="utf-8") as f:
        json.dump(gen,f,indent=2)

def main():
    # ★最低保証
    new_gen = set()

    while len(new_gen) < 3:
        new_gen.add(hex(random.randint(0,999999))[2:])

    wild = list(new_gen)[:2]

    result = {
        "generation": list(new_gen),
        "wild": wild
    }

    save(result)

    print("NEXT GENERATION (FORCED):", new_gen)
    print("WILD:", wild)

if __name__=="__main__":
    main()

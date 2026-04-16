import os
import json
import shutil

BASE_DIR = r"C:\Users\sirok\MoCKA"
BRANCH_DIR = os.path.join(BASE_DIR,"runtime","branches")

def load(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

print("=== MoCKA Branch Pruning ===")

scores = []

for b in os.listdir(BRANCH_DIR):

    ledger_path = os.path.join(BRANCH_DIR,b,"ledger.json")

    if not os.path.exists(ledger_path):
        continue

    ledger = load(ledger_path)

    failures = 0
    recoveries = 0

    for e in ledger:

        t = e["type"]

        if "failure" in t:
            failures += 1

        if "recovery" in t:
            recoveries += 1

    score = recoveries - failures

    scores.append((b,score))

scores.sort(key=lambda x:x[1],reverse=True)

print("")
print("branch ranking")
print("")

for b,s in scores:
    print(b,"score:",s)

print("")

KEEP = 5
print("keep top",KEEP,"branches")

keep_set = set([b for b,_ in scores[:KEEP]])

deleted = 0

for b,_ in scores[KEEP:]:

    path = os.path.join(BRANCH_DIR,b)

    shutil.rmtree(path)

    print("deleted:",b)

    deleted += 1

print("")
print("branches deleted:",deleted)

import json

LEDGER="runtime/main/ledger.json"
OUT="runtime/ledger_graph.dot"

with open(LEDGER,"r",encoding="utf-8") as f:
    d=json.load(f)

lines=[]
lines.append("digraph ledger {")
lines.append("rankdir=LR;")

for e in d:

    eid=e["event_id"]
    prev=e["prev_hash"][:8]
    h=e["event_hash"][:8]

    node=f"E{eid}"
    label=f"{eid}\\n{e['type']}"

    lines.append(f'{node} [label="{label}"];')

    if eid>0:
        prev_node=f"E{eid-1}"
        lines.append(f"{prev_node} -> {node};")

lines.append("}")

with open(OUT,"w",encoding="utf-8") as f:
    f.write("\n".join(lines))

print("LEDGER GRAPH GENERATED",OUT)

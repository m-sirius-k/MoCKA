from interface.router import MoCKARouter
from interface.diff_engine import analyze
from interface.ledger_writer import record
from interface.consensus_engine import decide
from interface.node_registry import register

NODE_NAME = "node_2"

prompt = "compare this system"

nodes = register(NODE_NAME)

r = MoCKARouter()
res = r.run(prompt, mode="multi")

analysis = analyze(res["results"])
decision = decide(res["results"], analysis)

record(prompt, res["results"], analysis)

print("NODE:", NODE_NAME)
print("KNOWN NODES:", nodes)
print("DECISION:", decision)

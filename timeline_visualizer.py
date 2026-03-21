import os

BASE_DIR = r"C:\Users\sirok\MoCKA"
BRANCH_DIR = os.path.join(BASE_DIR,"runtime","branches")

branches = os.listdir(BRANCH_DIR)

dot = []
dot.append("digraph mocka_time_tree {")
dot.append("rankdir=LR;")
dot.append("main [shape=box,label='main'];")

for b in branches:
    dot.append(f"main -> {b};")
    dot.append(f"{b} [shape=ellipse];")

dot.append("}")

dot_path = os.path.join(BASE_DIR,"runtime","branch_tree.dot")

with open(dot_path,"w") as f:
    f.write("\n".join(dot))

print("dot file created")
print(dot_path)

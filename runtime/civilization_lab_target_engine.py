import json
import os

ANALYSIS_FILE = "civilization_knowledge_analysis.json"
LAB_TARGET_FILE = "civilization_lab_target.json"

def load_analysis():
    if not os.path.exists(ANALYSIS_FILE):
        return None
    with open(ANALYSIS_FILE,"r") as f:
        return json.load(f)

def run():

    analysis = load_analysis()

    if not analysis:
        print("NO_ANALYSIS")
        return

    strategy = analysis.get("most_connected_strategy")

    result = {
        "priority_strategy":strategy,
        "reason":"knowledge_graph_centrality"
    }

    with open(LAB_TARGET_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("LAB_TARGET_SELECTED")
    print("strategy:",strategy)

if __name__ == "__main__":
    run()

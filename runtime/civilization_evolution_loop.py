import subprocess
import os

print("CIVILIZATION_EVOLUTION")

def run():

    if os.path.exists("error_capture_engine.py"):
        subprocess.call(["python","error_capture_engine.py"])

    if os.path.exists("incident_pipeline.py"):
        subprocess.call(["python","incident_pipeline.py"])

    if os.path.exists("repair_engine.py"):
        subprocess.call(["python","repair_engine.py"])

    if os.path.exists("verify_engine.py"):
        subprocess.call(["python","verify_engine.py"])

    if os.path.exists("knowledge_learning_engine.py"):
        subprocess.call(["python","knowledge_learning_engine.py"])

    if os.path.exists("adaptive_repair_selector.py"):
        subprocess.call(["python","adaptive_repair_selector.py"])

    if os.path.exists("civilization_consensus.py"):
        subprocess.call(["python","civilization_consensus.py"])

    if os.path.exists("civilization_history.py"):
        subprocess.call(["python","civilization_history.py"])

if __name__ == "__main__":
    run()

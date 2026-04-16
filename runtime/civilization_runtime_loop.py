import subprocess
import time

print("CIVILIZATION EVOLUTION LOOP START")

while True:

    print("STEP : civilization_evolution")
    subprocess.call(["python","civilization_evolution_loop.py"])

    print("STEP : analytics update")
    subprocess.call(["python","civilization_analytics_engine.py"])

    print("STEP : diagnostics")
    subprocess.call(["python","civilization_self_diagnostics_engine.py"])

    print("STEP : civilization goal")
    subprocess.call(["python","civilization_goal_engine.py"])

    print("STEP : civilization planning")
    subprocess.call(["python","civilization_planning_engine.py"])

    print("STEP : civilization progress")
    subprocess.call(["python","civilization_progress_engine.py"])

    print("STEP : civilization reflection")
    subprocess.call(["python","civilization_reflection_engine.py"])

    print("STEP : civilization history")
    subprocess.call(["python","civilization_history_archive_engine.py"])

    print("STEP : civilization prediction")
    subprocess.call(["python","civilization_prediction_engine.py"])

    print("STEP : governor decision")
    subprocess.call(["python","civilization_governor_v2.py"])

    print("STEP : governor action")
    subprocess.call(["python","governor_action_engine.py"])

    print("CYCLE COMPLETE")

    time.sleep(5)


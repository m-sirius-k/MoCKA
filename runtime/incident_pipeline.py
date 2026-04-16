import subprocess
import os

BASE_DIR = os.path.dirname(__file__)

def run(script):

    path = os.path.join(BASE_DIR, script)

    if not os.path.exists(path):
        print("MISSING:",script)
        return

    subprocess.run(["python",path])

def main():

    print("MOCKA INCIDENT PIPELINE START")

    run("incident_index_engine.py")
    run("incident_analyzer.py")
    run("incident_classifier.py")
    run("incident_timeline_builder.py")
    run("incident_anomaly_detector.py")
    run("incident_report_builder.py")

    print("MOCKA INCIDENT PIPELINE COMPLETE")

if __name__ == "__main__":
    main()

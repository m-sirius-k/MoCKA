import subprocess
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
LEDGER = os.path.join(BASE,"runtime","incident_ledger.json")

def commit_incident():

    try:

        subprocess.run(
            ["git","add",LEDGER],
            cwd=BASE,
            capture_output=True
        )

        subprocess.run(
            ["git","commit","-m","MoCKA incident update"],
            cwd=BASE,
            capture_output=True
        )

        subprocess.run(
            ["git","push"],
            cwd=BASE,
            capture_output=True
        )

        print("INCIDENT_GIT_RECORDED")

    except Exception as e:

        print("GIT_RECORD_FAILED",str(e))

if __name__ == "__main__":
    commit_incident()

import json
import os
import subprocess

RESULT_FILE="repair_execution_result.json"
VERIFY_FILE="repair_verification.json"

TARGET=r"C:\Users\sirok\MoCKA\civilization_evolution_loop.py"

def verify_runtime():

    try:

        result=subprocess.run(
            ["python",TARGET],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode==0:
            return "runtime_ok"
        else:
            return "runtime_error"

    except Exception as e:

        print(str(e))
        return "verification_failed"

def save_verification(status):

    data={
        "verification":status
    }

    with open(VERIFY_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():

    status=verify_runtime()

    save_verification(status)

    print("VERIFY_COMPLETED")

if __name__=="__main__":
    main()

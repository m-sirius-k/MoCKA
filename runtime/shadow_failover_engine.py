import json
import os
import subprocess

VERIFY_FILE="repair_verification.json"

def load_verification():

    if not os.path.exists(VERIFY_FILE):
        return None

    with open(VERIFY_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def start_shadow():

    print("PRIMARY_RUNTIME_FAILED")
    print("STARTING_SHADOW_RUNTIME")

    subprocess.Popen(["python","shadow_runtime.py"])

def main():

    v=load_verification()

    if not v:
        print("NO_VERIFICATION_DATA")
        return

    if v.get("verification")!="runtime_ok":
        start_shadow()
    else:
        print("PRIMARY_RUNTIME_OK")

if __name__=="__main__":
    main()

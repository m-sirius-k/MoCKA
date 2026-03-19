import json, os, sys, shutil
from runtime.security_ledger import log

POLICY_PATH = "mocka_governance/security_policy.json"

def load_policy():
    with open(POLICY_PATH,"r",encoding="utf-8") as f:
        return json.load(f)

def scan():
    policy = load_policy()
    violations = []

    for root, dirs, files in os.walk("."):
        for f in files:
            path = os.path.join(root,f)
            for d in policy["deny"]:
                if d in path:
                    violations.append(path)

    return violations

def auto_repair(v):
    for p in v:
        try:
            if os.path.isfile(p):
                os.remove(p)
                log("AUTO_DELETE:"+p)
        except:
            log("DELETE_FAIL:"+p)

def main():
    v = scan()
    if v:
        print("VIOLATION DETECTED")
        auto_repair(v)
        log("VIOLATION_FIXED")
        sys.exit(1)

    print("SECURITY OK")
    log("SECURITY_OK")

if __name__ == "__main__":
    main()

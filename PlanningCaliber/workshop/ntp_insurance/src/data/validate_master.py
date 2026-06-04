"""validate_master.py -- NTP master JSON validator"""
import json, sys

def validate(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    plans = []
    ids = []

    for company in data.get("companies", []):
        for p in company.get("plans", []):
            plans.append(p)
            pid = p.get("plan_id")
            if pid in ids:
                errors.append("dup plan_id: " + str(pid))
            ids.append(pid)

            if "tsi" not in p:
                errors.append("TSI missing: " + str(pid))

            if p.get("tsi", 1.0) == 0.0 and not p.get("discontinued"):
                errors.append("DEAD but discontinued=false: " + str(pid))

    declared = data.get("total_products", 0)
    actual = len(plans)
    if declared != actual:
        errors.append("total_products mismatch: declared=" + str(declared) + " actual=" + str(actual))

    if errors:
        print("NG validation failed:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    else:
        print("OK validation passed: " + str(actual) + " plans (version=" + str(data.get("version","?")) + ")")

if __name__ == "__main__":
    validate(sys.argv[1] if len(sys.argv) > 1 else "data/insurers/master_20260604_v4.json")

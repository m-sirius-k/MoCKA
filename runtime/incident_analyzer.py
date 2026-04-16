import json
import os

BASE_DIR = os.path.dirname(__file__)

INDEX_PATH = os.path.join(BASE_DIR,"incident_index.json")
REPORT_PATH = os.path.join(BASE_DIR,"incident_report.json")

def analyze():

    if not os.path.exists(INDEX_PATH):
        print("NO_INDEX")
        return

    with open(INDEX_PATH,"r",encoding="utf-8") as f:
        index = json.load(f)

    total_incidents = 0
    top_error = None
    top_count = 0

    for hid,data in index.items():

        count = data["count"]
        total_incidents += count

        if count > top_count:
            top_count = count
            top_error = {
                "incident_hash": hid,
                "title": data["title"],
                "count": count
            }

    report = {
        "total_incidents": total_incidents,
        "unique_incident_types": len(index),
        "most_frequent_incident": top_error
    }

    with open(REPORT_PATH,"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)

    print("INCIDENT_ANALYSIS_COMPLETE")

if __name__ == "__main__":
    analyze()

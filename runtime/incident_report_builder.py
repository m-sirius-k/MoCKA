import json
import os

BASE_DIR = os.path.dirname(__file__)

REPORT_PATH = os.path.join(BASE_DIR,"incident_report.json")
CLASS_PATH = os.path.join(BASE_DIR,"incident_classification.json")
TIMELINE_PATH = os.path.join(BASE_DIR,"incident_timeline.json")

SUMMARY_PATH = os.path.join(BASE_DIR,"incident_summary.txt")

def build_summary():

    if not os.path.exists(REPORT_PATH):
        print("NO_REPORT")
        return

    with open(REPORT_PATH,"r",encoding="utf-8") as f:
        report = json.load(f)

    with open(CLASS_PATH,"r",encoding="utf-8") as f:
        classes = json.load(f)

    with open(TIMELINE_PATH,"r",encoding="utf-8") as f:
        timeline = json.load(f)

    lines = []

    lines.append("MoCKA INCIDENT REPORT")
    lines.append("====================")
    lines.append("")

    lines.append("Total Incidents : " + str(report["total_incidents"]))
    lines.append("Unique Incident Types : " + str(report["unique_incident_types"]))
    lines.append("")

    lines.append("Most Frequent Incident")
    lines.append("---------------------")
    lines.append(report["most_frequent_incident"]["title"])
    lines.append("Count : " + str(report["most_frequent_incident"]["count"]))
    lines.append("")

    lines.append("Incident Classification")
    lines.append("----------------------")

    for k,v in classes.items():
        lines.append(k + " : " + str(v["count"]))

    lines.append("")
    lines.append("Timeline")
    lines.append("--------")

    for t,c in timeline.items():
        lines.append(t + " : " + str(c))

    with open(SUMMARY_PATH,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("INCIDENT_SUMMARY_CREATED")

if __name__ == "__main__":
    build_summary()

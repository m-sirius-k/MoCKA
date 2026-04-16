import json
import os

BASE_DIR = os.path.dirname(__file__)
REPORT_PATH = os.path.join(BASE_DIR,"incident_report.json")
ALERT_PATH = os.path.join(BASE_DIR,"incident_alert.json")

THRESHOLD = 50

def detect_trend():

    if not os.path.exists(REPORT_PATH):
        print("NO_REPORT")
        return

    with open(REPORT_PATH,"r",encoding="utf-8") as f:
        report = json.load(f)

    total = report.get("total_incidents",0)

    alert = {
        "alert": False,
        "reason": "",
        "total_incidents": total
    }

    if total >= THRESHOLD:
        alert["alert"] = True
        alert["reason"] = "Incident volume exceeds threshold"

    with open(ALERT_PATH,"w",encoding="utf-8") as f:
        json.dump(alert,f,indent=2)

    if alert["alert"]:
        print("INCIDENT_ALERT_TRIGGERED")
    else:
        print("SYSTEM_STABLE")

if __name__ == "__main__":
    detect_trend()

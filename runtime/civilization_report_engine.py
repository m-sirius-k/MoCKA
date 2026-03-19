import json
import os
from datetime import datetime

STATUS_FILE = "civilization_status.json"
PROGRESS_FILE = "civilization_progress.json"
THEORY_FILE = "civilization_theory.json"
PHILOSOPHY_FILE = "civilization_philosophy.json"

REPORT_FILE = "civilization_report.txt"


def load_json(path):

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    return None


def run():

    status = load_json(STATUS_FILE)
    progress = load_json(PROGRESS_FILE)
    theory = load_json(THEORY_FILE)
    philosophy = load_json(PHILOSOPHY_FILE)

    lines = []

    lines.append("MoCKA Civilization Report")
    lines.append("========================")
    lines.append("")
    lines.append("Generated : " + datetime.utcnow().isoformat())
    lines.append("")

    if status:
        s = status.get("civilization_status",{})
        lines.append("Mode : " + str(s.get("mode")))
        lines.append("Stability : " + str(s.get("stability")))
        lines.append("")

    if progress:
        lines.append("Progress : " + str(progress.get("progress")))
        lines.append("")

    if theory:
        lines.append("Dominant Strategy : " + str(theory.get("dominant_strategy")))
        lines.append("")

    if philosophy:
        lines.append("Philosophy : " + str(philosophy.get("principle")))
        lines.append("")

    with open(REPORT_FILE,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("CIVILIZATION_REPORT_CREATED")


if __name__ == "__main__":
    run()

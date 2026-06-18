import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
from datetime import datetime

SHUTDOWN_FILE = "civilization_shutdown_log.json"


def run():

    shutdown = {
        "civilization_shutdown":{
            "time":datetime.utcnow().isoformat(),
            "status":"stopped"
        }
    }

    with open(SHUTDOWN_FILE,"w",encoding="utf-8") as f:
        json.dump(shutdown,f,indent=2)

    print("CIVILIZATION_SHUTDOWN_COMPLETE")


if __name__ == "__main__":
    run()

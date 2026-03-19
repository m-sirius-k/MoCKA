import json
import os
import shutil
from datetime import datetime

IMPORT_DIR = "civilization_import"
IMPORT_LOG = "civilization_import_log.json"


def run():

    log = {
        "civilization_import":{
            "time":datetime.utcnow().isoformat(),
            "files":[]
        }
    }

    if not os.path.exists(IMPORT_DIR):

        log["civilization_import"]["status"] = "no_import_directory"

    else:

        for file in os.listdir(IMPORT_DIR):

            src = os.path.join(IMPORT_DIR,file)
            dst = file

            if os.path.isfile(src):

                try:

                    shutil.copy2(src,dst)

                    log["civilization_import"]["files"].append({
                        "file":file,
                        "imported":True
                    })

                except Exception as e:

                    log["civilization_import"]["files"].append({
                        "file":file,
                        "imported":False,
                        "error":str(e)
                    })

    with open(IMPORT_LOG,"w",encoding="utf-8") as f:
        json.dump(log,f,indent=2)

    print("CIVILIZATION_IMPORT_COMPLETE")


if __name__ == "__main__":
    run()

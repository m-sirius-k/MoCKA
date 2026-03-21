import os
import json
import requests
import time

REG = "runtime/node_registry.json"
HEALTH = "runtime/node_health.json"

def load_registry():

    if not os.path.exists(REG):
        return {}

    with open(REG,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save_health(data):

    with open(HEALTH,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

print("NODE HEALTH MONITOR START")

while True:

    reg = load_registry()

    health = {}

    for ip in reg:

        url = "http://" + ip + ":9100/snapshots"

        try:

            r = requests.get(url,timeout=3)

            snaps = r.json()

            health[ip] = {
                "status":"alive",
                "snapshot_count":len(snaps),
                "checked_at":int(time.time())
            }

            print("ALIVE",ip)

        except:

            health[ip] = {
                "status":"offline",
                "checked_at":int(time.time())
            }

            print("OFFLINE",ip)

    save_health(health)

    time.sleep(15)


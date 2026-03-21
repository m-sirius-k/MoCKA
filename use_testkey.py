import json
import time

with open("testkey.json","r",encoding="utf-8") as f:
    data = json.load(f)

# expiration check
now = int(time.time())
if now > data["issued_at"] + data["expires_in_days"]*86400:
    print("EXPIRED")
    exit()

# usage check
if data["uses"] >= data["max_uses"]:
    print("LIMIT REACHED")
    exit()

# increment usage
data["uses"] += 1

with open("testkey.json","w",encoding="utf-8") as f:
    json.dump(data,f,indent=2)

print("OK USE:", data["uses"])

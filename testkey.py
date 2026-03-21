import json
import hashlib
import time

# load token（BOM対応）
with open("token.json","r",encoding="utf-8-sig") as f:
    token_data = json.load(f)

payload = token_data["payload"]
signature = token_data["token"]

# derive test key
base = payload + ":" + signature
testkey = hashlib.sha256(base.encode()).hexdigest()

out = {
    "testkey": testkey,
    "issued_at": int(time.time()),
    "max_uses": 5000,
    "expires_in_days": 90,
    "uses": 0
}

with open("testkey.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2)

print("TESTKEY GENERATED")

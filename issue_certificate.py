import json
import hashlib
import time

with open("token.json","r",encoding="utf-8-sig") as f:
    token = json.load(f)

with open("testkey.json","r",encoding="utf-8") as f:
    testkey = json.load(f)

with open("ledger.json","r",encoding="utf-8") as f:
    ledger = json.load(f)

head_hash = ledger[-1]["hash"]

certificate = {
    "issued_at": int(time.time()),
    "token": token["token"],
    "testkey": testkey["testkey"],
    "ledger_head": head_hash,
    "caliber": testkey.get("caliber","UNKNOWN")
}

certificate["certificate_hash"] = hashlib.sha256(
    json.dumps(certificate, sort_keys=True).encode()
).hexdigest()

with open("certificate.json","w",encoding="utf-8") as f:
    json.dump(certificate,f,indent=2)

print("CERTIFICATE ISSUED")

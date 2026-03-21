import json
from nacl.signing import VerifyKey

# load public key
with open("public.key","rb") as f:
    vk = VerifyKey(f.read())

# load token
with open("token.json","r",encoding="utf-8-sig") as f:
    data = json.load(f)

# revocation load
try:
    with open("revocation.json","r",encoding="utf-8") as f:
        rev = json.load(f)
except:
    rev = {"revoked_tokens":[]}

if data["token"] in rev.get("revoked_tokens",[]):
    print("REVOKED TOKEN")
    exit()

payload = data["payload"].encode()
signature = bytes.fromhex(data["token"])

try:
    vk.verify(payload, signature)
    print("VALID TOKEN")
except:
    print("INVALID TOKEN")

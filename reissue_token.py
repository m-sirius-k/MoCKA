import hashlib
import platform
import uuid
import time
import json
from nacl.signing import SigningKey

# 秘密鍵読み込み
with open("private.key","rb") as f:
    sk = SigningKey(f.read())

# fingerprint生成
node = platform.node()
system = platform.system()
mac = uuid.getnode()
raw = f"{node}-{system}-{mac}"
fingerprint = hashlib.sha256(raw.encode()).hexdigest()

# payload
timestamp = str(int(time.time()))
nonce = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
payload = f"{fingerprint}:{timestamp}:{nonce}"

# 署名
signature = sk.sign(payload.encode()).signature.hex()

out = {
    "payload": payload,
    "token": signature
}

with open("token.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2)

print("TOKEN REISSUED (FINGERPRINT LOCKED)")

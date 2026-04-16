# Pseudocode only
import hashlib, base64

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            c=f.read(1024*1024)
            if not c: break
            h.update(c)
    return h.hexdigest()

def build_signed_bytes(env):
    text = (
        f"scheme_version=v2\n"
        f"event_id={env['event_id']}\n"
        f"chain_hash={env['chain_hash']}\n"
        f"timestamp_utc={env['timestamp_utc']}\n"
        f"payload_hash_sha256={env['payload_hash_sha256']}\n"
        f"key_id={env['key_id']}\n"
    )
    return text.encode('ascii')

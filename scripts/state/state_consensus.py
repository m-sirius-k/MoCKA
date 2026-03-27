import hashlib
import time

files = [
"runtime/shadow_1/state.json",
"runtime/shadow_2/state.json",
"runtime/shadow_3/state.json"
]

def hash_file(path):

    try:
        with open(path,"rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()
    except:
        return None

while True:

    hashes = [hash_file(f) for f in files]

    if None in hashes:
        print("STATE FILE MISSING",hashes)

    elif hashes.count(hashes[0]) == len(hashes):
        print("STATE CONSENSUS OK",hashes[0])

    else:
        print("STATE CONSENSUS ALERT",hashes)

    time.sleep(5)


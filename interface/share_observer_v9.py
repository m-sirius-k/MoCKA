import os, time, json, hashlib
from datetime import datetime

WATCH_DIR = r"C:\Users\sirok\planningcaliber\mocka-share\payloads"
LOCK_EXT = ".lock"
INTERVAL = 0.5

def get_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def is_locked(filepath):
    return os.path.exists(filepath + LOCK_EXT)

def acquire_lock(filepath):
    with open(filepath + LOCK_EXT, "w") as f:
        f.write(datetime.now().isoformat())

def release_lock(filepath):
    lock = filepath + LOCK_EXT
    if os.path.exists(lock):
        os.remove(lock)

def observe(callback):
    os.makedirs(WATCH_DIR, exist_ok=True)
    processed = set()
    print(f"[share_observer] 監視開始: {WATCH_DIR}")
    while True:
        for fname in os.listdir(WATCH_DIR):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(WATCH_DIR, fname)
            fhash = get_hash(fpath)
            if fhash in processed:
                continue
            if is_locked(fpath):
                print(f"[share_observer] LOCKED スキップ: {fname}")
                continue
            acquire_lock(fpath)
            try:
                with open(fpath, encoding="utf-8-sig") as f:
                    packet = json.load(f)
                print(f"[share_observer] 検知: {fname}")
                callback(fpath, packet)
                processed.add(fhash)
            except Exception as e:
                print(f"[share_observer] ERROR: {e}")
            finally:
                release_lock(fpath)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    def dummy_callback(fpath, packet):
        print(f"[share_observer] パケット受信: {json.dumps(packet, ensure_ascii=False)[:80]}")
    observe(dummy_callback)

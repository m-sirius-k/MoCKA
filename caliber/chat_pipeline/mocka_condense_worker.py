import argparse, csv, hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

OLLAMA  = Path(os.environ.get("LOCALAPPDATA","")) / "Programs" / "Ollama" / "ollama.exe"
ROOT    = Path("C:/Users/sirok/MoCKA")
RAW_DIR = ROOT / "data" / "storage" / "infield" / "RAW"
REDUCED = ROOT / "data" / "storage" / "infield" / "REDUCED"
DONE    = ROOT / "data" / "storage" / "infield" / "RAW_DONE"
EVENTS  = ROOT / "data" / "events.csv"
MODEL   = "gemma3:4b"
CHUNK   = 3000
UTC     = timezone.utc
P1 = "Extract up to 3 key design/structure points as bullet points from the following chat:\n\n"
P2 = "Extract up to 3 key risks/problems as bullet points from the following chat:\n\n"
P3A = "Step1:\n"
P3B = "\nStep2:\n"
P3C = "\nExtract any important insights not covered above. If none, say NO_RESIDUE.\nText:\n"

REDUCED.mkdir(parents=True, exist_ok=True)
DONE.mkdir(parents=True, exist_ok=True)

def ask(prompt):
    r = subprocess.run([str(OLLAMA),"run",MODEL,prompt],
        capture_output=True,text=True,encoding="utf-8",timeout=120)
    return r.stdout.strip()

def chunk_text(text, size=CHUNK):
    return [text[i:i+size] for i in range(0, len(text), size)]

def get_prev():
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig"))) if EVENTS.exists() else []
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"

def condense_file(fpath):
    fpath = Path(fpath)
    print("[CONDENSE] " + fpath.name)
    raw = json.load(open(fpath, encoding="utf-8"))
    text = raw.get("text", "")
    source = raw.get("source", "unknown")
    url = raw.get("url", "")
    if not text:
        print("[SKIP] no text"); return None
    chunks = chunk_text(text)
    print("[INFO] " + str(len(text)) + " chars / " + str(len(chunks)) + " chunks")
    all_s1 = []
    all_s2 = []
    for i, chunk in enumerate(chunks):
        print("[Step1-" + str(i+1) + "/" + str(len(chunks)) + "]")
        all_s1.append(ask(P1 + chunk))
        print("[Step2-" + str(i+1) + "/" + str(len(chunks)) + "]")
        all_s2.append(ask(P2 + chunk))
    merged_s1 = chr(10).join(all_s1)
    merged_s2 = chr(10).join(all_s2)
    print("[Step3] residue check...")
    s3 = ask(P3A + merged_s1[:2000] + P3B + merged_s2[:2000] + P3C + text[:1000])
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = "ERED_" + ts + "_" + source[:4].upper()
    h = hashlib.sha256((eid + ts + merged_s1[:100]).encode()).hexdigest()[:16]
    result = {"event_id":eid,"source":source,"url":url,"raw_file":fpath.name,
              "timestamp":ts,"original_chars":len(text),"chunks":len(chunks),
              "step1_structure":merged_s1,"step2_audit":merged_s2,"step3_residue":s3,
              "hash":h,"status":"REDUCED"}
    out = REDUCED / (ts + "_" + eid + ".json")
    json.dump(result, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[OK] saved: " + out.name)
    prev = get_prev()
    with open(EVENTS,"a",encoding="utf-8",newline="") as f:
        csv.writer(f).writerow([eid,ts,"condense_worker","condense","chat_condense",
            "mocka_condense_worker.py",fpath.name,"worker","internal",
            "in_operation","normal","A","infield/REDUCED",
            merged_s1[:100],prev,"condense_complete","REDUCED",
            "local","condense_pipeline","N/A","N/A",
            "hash="+h+" source="+source+" chunks="+str(len(chunks))+" chars="+str(len(text))])
    fpath.rename(DONE / fpath.name)
    print("[OK] moved to RAW_DONE")
    return out

def get_unprocessed():
    done_names = {f.name for f in DONE.glob("*.json")}
    reduced_raws = set()
    for r in REDUCED.glob("*.json"):
        try:
            d = json.load(open(r, encoding="utf-8"))
            reduced_raws.add(d.get("raw_file",""))
        except: pass
    return [f for f in sorted(RAW_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime)
            if f.name not in done_names and f.name not in reduced_raws]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--file")
    args = parser.parse_args()
    if args.file:
        condense_file(args.file); return
    if args.once:
        files = get_unprocessed()
        if not files: print("[INFO] no unprocessed files"); return
        for f in files: condense_file(f)
        print("[DONE] " + str(len(files)) + " files processed"); return
    print("[WORKER] watching... Ctrl+C to stop")
    while True:
        files = get_unprocessed()
        if files:
            for f in files: condense_file(f)
        else:
            print("[WORKER] waiting... " + datetime.now(UTC).strftime("%H:%M:%S"))
        time.sleep(60)

if __name__ == "__main__":
    main()
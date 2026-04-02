import argparse, csv, hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

OLLAMA     = Path(os.environ.get("LOCALAPPDATA","")) / "Programs" / "Ollama" / "ollama.exe"
ROOT       = Path("C:/Users/sirok/MoCKA")
RAW_DIR    = ROOT / "data" / "storage" / "infield" / "RAW"
REDUCED    = ROOT / "data" / "storage" / "infield" / "REDUCED"
RE_REDUCED = ROOT / "data" / "storage" / "infield" / "RE_REDUCED"
REDUCING   = ROOT / "data" / "storage" / "infield" / "REDUCING"
DONE       = ROOT / "data" / "storage" / "infield" / "RAW_DONE"
EVENTS     = ROOT / "data" / "events.csv"
MODEL      = "gemma3:4b"
CHUNK      = 3000
UTC        = timezone.utc
RESTORE_THRESHOLD = 0.80

# Pass1 プロンプト
P1  = "Extract up to 3 key design/structure points as bullet points from the following chat:\n\n"
P2  = "Extract up to 3 key risks/problems as bullet points from the following chat:\n\n"
P3A = "Step1:\n"
P3B = "\nStep2:\n"
P3C = "\nExtract any important insights not covered above. If none, say NO_RESIDUE.\nText:\n"

# Pass2 プロンプト
P4 = ("Given the following condensed summary, estimate what percentage of the original meaning "
      "can be restored from it. Reply with only a number 0-100.\nSummary:\n")
P5 = "From the following summary, extract ONLY the most critical single insight as one sentence:\n\n"

for d in [REDUCED, RE_REDUCED, REDUCING, DONE]:
    d.mkdir(parents=True, exist_ok=True)

def ask(prompt):
    r = subprocess.run([str(OLLAMA),"run",MODEL,prompt],
        capture_output=True,text=True,encoding="utf-8",timeout=120)
    return r.stdout.strip()

def chunk_text(text, size=CHUNK):
    return [text[i:i+size] for i in range(0, len(text), size)]

def get_prev():
    rows = list(csv.reader(open(EVENTS, encoding="utf-8-sig"))) if EVENTS.exists() else []
    return hashlib.sha256(",".join(rows[-1]).encode()).hexdigest()[:16] if rows else "GENESIS"

def parse_restore_rate(s):
    import re
    m = re.search(r"\d+", s)
    return int(m.group()) / 100.0 if m else 0.0

# ── Pass1: デッドエンド濃縮 ──────────────────────────────────
def pass1(fpath):
    fpath = Path(fpath)
    print("[PASS1] " + fpath.name)
    raw = json.load(open(fpath, encoding="utf-8"))
    text = raw.get("text", "")
    source = raw.get("source", "unknown")
    url = raw.get("url", "")
    if not text:
        print("[SKIP] no text"); return None, None
    chunks = chunk_text(text)
    print("[INFO] " + str(len(text)) + " chars / " + str(len(chunks)) + " chunks")
    all_s1, all_s2 = [], []
    for i, chunk in enumerate(chunks):
        print("[S1-" + str(i+1) + "/" + str(len(chunks)) + "]")
        all_s1.append(ask(P1 + chunk))
        print("[S2-" + str(i+1) + "/" + str(len(chunks)) + "]")
        all_s2.append(ask(P2 + chunk))
    merged_s1 = chr(10).join(all_s1)
    merged_s2 = chr(10).join(all_s2)
    print("[S3] residue check...")
    s3 = ask(P3A + merged_s1[:2000] + P3B + merged_s2[:2000] + P3C + text[:1000])
    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    eid = "ERED_" + ts + "_" + source[:4].upper()
    h   = hashlib.sha256((eid + ts + merged_s1[:100]).encode()).hexdigest()[:16]
    result = {
        "event_id": eid, "source": source, "url": url, "raw_file": fpath.name,
        "timestamp": ts, "original_chars": len(text), "chunks": len(chunks),
        "step1_structure": merged_s1, "step2_audit": merged_s2, "step3_residue": s3,
        "hash": h, "status": "REDUCED"
    }
    out = REDUCED / (ts + "_" + eid + ".json")
    json.dump(result, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[OK] REDUCED: " + out.name)
    prev = get_prev()
    with open(EVENTS,"a",encoding="utf-8",newline="") as f:
        csv.writer(f).writerow([eid,ts,"condense_worker","pass1","chat_condense",
            "mocka_condense_worker.py",fpath.name,"worker","internal",
            "in_operation","normal","A","infield/REDUCED",
            merged_s1[:100],prev,"pass1_complete","REDUCED",
            "local","condense_pipeline","N/A","N/A",
            "hash="+h+" source="+source+" chunks="+str(len(chunks))+" chars="+str(len(text))])
    fpath.rename(DONE / fpath.name)
    print("[OK] moved to RAW_DONE")
    return out, text

# ── Pass2: クロスフロー検証 ──────────────────────────────────
def pass2(reduced_path, original_text):
    reduced_path = Path(reduced_path)
    print("[PASS2] " + reduced_path.name)
    rd = json.load(open(reduced_path, encoding="utf-8"))
    summary = rd.get("step1_structure","") + chr(10) + rd.get("step2_audit","") + chr(10) + rd.get("step3_residue","")
    print("[P4] restore rate check...")
    rate_str = ask(P4 + summary[:3000])
    rate = parse_restore_rate(rate_str)
    print("[INFO] restore rate: " + str(int(rate*100)) + "%")
    print("[P5] core insight extraction...")
    core = ask(P5 + summary[:3000])
    ts  = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    src = rd.get("source","unknown")
    eid = "ERRD_" + ts + "_" + src[:4].upper()
    h   = hashlib.sha256((eid + ts + core[:100]).encode()).hexdigest()[:16]
    status = "RE_REDUCED" if rate >= RESTORE_THRESHOLD else "REDUCING"
    result = {
        "event_id": eid, "source": src, "url": rd.get("url",""),
        "reduced_file": reduced_path.name, "raw_file": rd.get("raw_file",""),
        "timestamp": ts, "restore_rate": rate, "threshold": RESTORE_THRESHOLD,
        "core_insight": core, "full_summary": summary,
        "hash": h, "status": status
    }
    dst_dir = RE_REDUCED if rate >= RESTORE_THRESHOLD else REDUCING
    out = dst_dir / (ts + "_" + eid + ".json")
    json.dump(result, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[OK] " + status + ": " + out.name)
    prev = get_prev()
    with open(EVENTS,"a",encoding="utf-8",newline="") as f:
        csv.writer(f).writerow([eid,ts,"condense_worker","pass2","chat_condense",
            "mocka_condense_worker.py",reduced_path.name,"worker","internal",
            "in_operation","normal","A","infield/"+status,
            core[:100],prev,"pass2_complete",status,
            "local","condense_pipeline","N/A","N/A",
            "hash="+h+" rate="+str(int(rate*100))+"pct source="+src])
    return out, status

# ── 統合処理 ─────────────────────────────────────────────────
def condense_file(fpath):
    reduced_path, original_text = pass1(fpath)
    if reduced_path is None:
        return
    pass2(reduced_path, original_text)

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
    parser.add_argument("--pass2only", help="REDUCEDファイルにPass2のみ実行")
    args = parser.parse_args()
    if args.pass2only:
        pass2(args.pass2only, ""); return
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
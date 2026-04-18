"""
mocka_pipeline.py
MoCKA Knowledge Pipeline v2.0
CSV -> 抽出 -> 濃縮 -> essence
API通信: なし (0円)
"""
import argparse, json, sys, subprocess
from pathlib import Path
from datetime import datetime

MOCKA_ROOT   = Path(r"C:\Users\sirok\MoCKA")
INTERFACE    = MOCKA_ROOT / "interface"
RAW_DIR      = MOCKA_ROOT / "data" / "storage" / "infield" / "RAW"
RAW_DONE_DIR = MOCKA_ROOT / "data" / "storage" / "infield" / "RAW_DONE"
EVENTS_CSV   = MOCKA_ROOT / "data" / "events.csv"
ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
PING_GEN     = MOCKA_ROOT / "interface" / "ping_generator.py"

sys.path.insert(0, str(INTERFACE))
sys.path.insert(0, str(MOCKA_ROOT))

def _load_modules():
    mods = {}
    try:
        from Sanitizer_Gate import SanitizerGate
        mods["gate"] = SanitizerGate(verbose=False)
    except Exception as e:
        print(f"[PIPELINE] WARNING Sanitizer_Gate: {e}")
    try:
        from language_detector import LanguageDetector
        mods["detector"] = LanguageDetector()
    except Exception as e:
        print(f"[PIPELINE] WARNING LanguageDetector: {e}")
    try:
        from essence_classifier import classify
        mods["classify"] = classify
    except Exception as e:
        print(f"[PIPELINE] WARNING essence_classifier: {e}")
    try:
        from essence_condenser import EssenceCondenser
        mods["condenser"] = EssenceCondenser(essence_path=ESSENCE_PATH)
    except Exception as e:
        print(f"[PIPELINE] WARNING EssenceCondenser: {e}")
    try:
        from incident_learner import IncidentLearner
        mods["learner"] = IncidentLearner()
    except Exception as e:
        print(f"[PIPELINE] WARNING IncidentLearner: {e}")
    return mods

def step_extract(text, mods):
    result = {"text": text, "danger_level": "INFO", "danger_score": 0, "danger_words": [], "axis": "OPERATION"}
    if "gate" in mods:
        raw_bytes, had_bom, valid = mods["gate"].sanitize_bytes(text.encode("utf-8"))
        if not valid:
            return {"status": "SANITIZE_FAILED"}
        text = raw_bytes.decode("utf-8", errors="replace")
        result["text"] = text
        if had_bom:
            print(f"  [抽出] BOM除去済み")
    if "detector" in mods:
        d = mods["detector"].analyze(text)
        result["danger_level"] = d.get("level", "INFO")
        result["danger_score"] = d.get("score", 0)
        result["danger_words"] = d.get("matched_words", [])
        if result["danger_level"] != "INFO":
            print(f"  [抽出] 危険度: {result['danger_level']} score={result['danger_score']:.0f}")
    if "classify" in mods:
        result["axis"] = mods["classify"](text)
        print(f"  [抽出] 分類: {result['axis']}")
    result["status"] = "OK"
    return result

def step_condense(extracted, mods):
    if extracted.get("status") != "OK":
        return {"status": "SKIP"}
    text  = extracted["text"]
    axis  = extracted["axis"]
    level = extracted["danger_level"]
    if "learner" in mods and level in ("DANGER", "CRITICAL"):
        lr = mods["learner"].learn(text)
        if lr.get("total_added", 0):
            print(f"  [濃縮] 自己学習: {lr['total_added']}件の新危険因子を追加")
    if "condenser" in mods:
        result = mods["condenser"].condense({axis: [text]})
        print(f"  [濃縮] essence更新: {result.get('updated_axes', [])}")
        return {"status": "OK", "condense": result}
    return {"status": "SKIP"}

def step_record(file_name, extracted, condense):
    try:
        import csv as _csv
        ts      = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        axis    = extracted.get("axis", "OPERATION")
        level   = extracted.get("danger_level", "INFO")
        score   = extracted.get("danger_score", 0)
        updated = condense.get("condense", {}).get("updated_axes", [])
        eid     = "EP_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        row = [eid, ts, "pipeline", "essence_update", "mocka_pipeline",
               file_name, f"axis={axis}", "pipeline", "internal",
               "in_operation", "normal", "A", "infield/essence",
               f"danger={level}({score:.0f}) essence={updated}",
               "N/A", "pipeline_complete", axis,
               "local", "pipeline", "N/A", "N/A",
               f"no_api|D_i=1|ΔE=0"]
        with open(EVENTS_CSV, "a", encoding="utf-8", newline="") as f:
            _csv.writer(f).writerow(row)
    except Exception as e:
        print(f"  [記録] WARNING: {e}")

def process_file(file_path, mods):
    print(f"\n[PIPELINE] {file_path.name}")
    try:
        raw = file_path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        data = json.loads(raw.decode("utf-8", errors="replace"))
        text = data.get("text", data.get("content", ""))
        if not text and "messages" in data:
            text = " ".join(m.get("content", m.get("text","")) for m in data["messages"] if isinstance(m, dict))
    except Exception as e:
        print(f"  JSON解析エラー: {e}")
        return {"status": "ERROR"}
    if not text or len(text.strip()) < 10:
        print(f"  テキスト空 -> スキップ")
        return {"status": "EMPTY"}
    extracted = step_extract(text, mods)
    if extracted.get("status") != "OK":
        return extracted
    condense = step_condense(extracted, mods)
    step_record(file_path.name, extracted, condense)
    RAW_DONE_DIR.mkdir(parents=True, exist_ok=True)
    dst = RAW_DONE_DIR / file_path.name
    if dst.exists():
        dst = RAW_DONE_DIR / (file_path.stem + f"_{datetime.now().strftime('%H%M%S')}" + file_path.suffix)
    file_path.rename(dst)
    print(f"  -> RAW_DONE/{dst.name}")
    return {"status": "OK", "axis": extracted.get("axis"), "level": extracted.get("danger_level")}

def run_ping():
    if PING_GEN.exists():
        r = subprocess.run(["python", str(PING_GEN)], capture_output=True, text=True)
        print(f"\n[PIPELINE] ping: {r.stdout.strip()}")

def main():
    parser = argparse.ArgumentParser(description="MoCKA Pipeline v2.0")
    parser.add_argument("--file",  help="単一ファイル処理")
    parser.add_argument("--text",  help="テキスト直接処理")
    parser.add_argument("--learn", action="store_true", help="学習のみ")
    parser.add_argument("--no-ping", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("MoCKA Knowledge Pipeline v2.0")
    print("CSV -> 抽出 -> 濃縮 -> essence | API:0円")
    print("=" * 50)

    mods = _load_modules()
    print(f"[PIPELINE] モジュール: {list(mods.keys())}\n")
    stats = {"ok": 0, "skip": 0, "error": 0}

    if args.learn:
        if "learner" in mods:
            r = mods["learner"].learn_from_events_csv(EVENTS_CSV)
            print(f"[PIPELINE] 学習完了: {r}")
        return

    if args.text:
        extracted = step_extract(args.text, mods)
        condense  = step_condense(extracted, mods)
        step_record("direct_input", extracted, condense)
        stats["ok"] += 1

    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"[PIPELINE] ERROR: {path}")
            sys.exit(1)
        r = process_file(path, mods)
        stats["ok" if r["status"] == "OK" else "error"] += 1

    else:
        files = sorted(RAW_DIR.glob("*.json"))
        if not files:
            print(f"[PIPELINE] RAWフォルダは空: {RAW_DIR}")
        else:
            print(f"[PIPELINE] 対象: {len(files)}件")
            for f in files:
                r = process_file(f, mods)
                s = r.get("status","error")
                stats["ok" if s=="OK" else ("skip" if s in ("EMPTY","SKIP") else "error")] += 1

    print(f"\n{'='*50}")
    print(f"[PIPELINE] 完了 OK:{stats['ok']} SKIP:{stats['skip']} ERR:{stats['error']}")
    print(f"{'='*50}")

    if not args.no_ping and stats["ok"] > 0:
        run_ping()

if __name__ == "__main__":
    main()

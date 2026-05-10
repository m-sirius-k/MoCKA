from pathlib import Path

app_py = Path(r"C:\Users\sirok\MoCKA\app.py")
txt = app_py.read_text(encoding="utf-8")

MARKER = "if __name__ == \"__main__\":"
if "guidelines" in txt:
    print("[SKIP] 既にパッチ適用済み")
    exit()

PATCH = '''
# ================================================================
# Guidelines Engine エンドポイント (2026-05-10)
# ================================================================
import importlib.util as _ilu
import threading as _threading

def _load_guidelines_engine():
    spec = _ilu.spec_from_file_location(
        "guidelines_engine",
        Path(ROOT_DIR) / "interface" / "guidelines_engine.py"
    )
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _run_guidelines_engine():
    try:
        mod = _load_guidelines_engine()
        mod.run(score_threshold=0.35, max_new=500)
        return True
    except Exception as e:
        print(f"[guidelines_engine] error: {e}")
        return False

@app.route("/guidelines/run", methods=["POST"])
def guidelines_run():
    ok = _run_guidelines_engine()
    gpath = Path(ROOT_DIR) / "data" / "guidelines.json"
    if gpath.exists():
        data = json.loads(gpath.read_text(encoding="utf-8"))
        return jsonify({
            "status": "ok" if ok else "error",
            "total": data["summary"]["total"],
            "by_category": data["summary"]["by_category"],
            "last_updated": data["summary"]["last_updated"],
        })
    return jsonify({"status": "ok" if ok else "error", "total": 0})

@app.route("/guidelines/status", methods=["GET"])
def guidelines_status():
    gpath = Path(ROOT_DIR) / "data" / "guidelines.json"
    if not gpath.exists():
        return jsonify({"total": 0, "by_category": {}, "top5": [], "last_updated": ""})
    data = json.loads(gpath.read_text(encoding="utf-8"))
    top5 = sorted(data["guidelines"], key=lambda g: g.get("score", 0), reverse=True)[:5]
    return jsonify({
        "total": data["summary"]["total"],
        "by_category": data["summary"]["by_category"],
        "last_updated": data["summary"].get("last_updated", ""),
        "top5": [{
            "category": g["category"],
            "score": g["score"],
            "directive": g["action_directive"],
        } for g in top5]
    })

@app.route("/guidelines/list", methods=["GET"])
def guidelines_list():
    cat   = request.args.get("category", "")
    limit = int(request.args.get("limit", 20))
    gpath = Path(ROOT_DIR) / "data" / "guidelines.json"
    if not gpath.exists():
        return jsonify({"items": [], "total": 0})
    data  = json.loads(gpath.read_text(encoding="utf-8"))
    items = data["guidelines"]
    if cat:
        items = [g for g in items if g.get("category") == cat]
    items = sorted(items, key=lambda g: g.get("score", 0), reverse=True)
    return jsonify({"items": items[:limit], "total": len(items)})

# guidelines定期実行（1時間ごと）
def _guidelines_loop():
    import time
    time.sleep(300)  # 起動5分後に初回実行
    while True:
        try:
            print("[guidelines] 定期実行開始")
            _run_guidelines_engine()
            print("[guidelines] 定期実行完了")
        except Exception as e:
            print(f"[guidelines] loop error: {e}")
        time.sleep(3600)  # 1時間ごと

_gt = _threading.Thread(target=_guidelines_loop, daemon=True)
_gt.start()

'''

# if __name__ の直前に挿入
idx = txt.rfind(MARKER)
patched = txt[:idx] + PATCH + txt[idx:]
app_py.write_text(patched, encoding="utf-8")
print(f"[OK] app.py パッチ適用完了 ({len(patched.splitlines())}行)")
print("追加エンドポイント:")
print("  POST /guidelines/run    — 行動指針生成")
print("  GET  /guidelines/status — 現状確認")
print("  GET  /guidelines/list   — 一覧")
print("  定期実行: 起動5分後→以降1時間ごと")

"""
essence_auto_updater.py v3
- events.dbのeventsテーブルから直接essenceを生成
- REDUCING->RE_REDUCED自動移動 (TODO_123)
- Caliberヘルスチェック統合 (断絶3)
"""
import re, sqlite3, threading, time, subprocess, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR   = Path(r"C:\Users\sirok\MoCKA")
DB_PATH    = ROOT_DIR / "data" / "mocka_events.db"
PING_GEN   = ROOT_DIR / "interface" / "ping_generator.py"
REDUCING   = ROOT_DIR / "data" / "storage" / "infield" / "REDUCING"
RE_REDUCED = ROOT_DIR / "data" / "storage" / "infield" / "RE_REDUCED"

INTERVAL_SEC      = 300
REDUCING_SEC      = 60
CALIBER_CHECK_SEC = 120

INCIDENT_KW  = ["エラー","失敗","インシデント","CRITICAL","DANGER","違反","捏造",
                 "なぜ","また同じ","クレーム","INTEGRITY","VIOLATION","バグ","問題","OVERDUE"]
PHILOSOPHY_KW= ["AIを信じるな","システムで縛れ","制度","文明","哲学","設計思想",
                 "信じる","縛る","原則","思想","理念","現状の把握",
                 "ここに至る経緯","失敗要因","成功のパターン"]
OPERATION_KW = ["完了","稼働","実装","確認","great","グレート","ヒント","success",
                 "hint","運用","手順","ルール","パイプライン","設定","修正済み"]

_caliber_alive = True


def _clean(text):
    if not text:
        return ""
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    text = re.sub(r"\x1b\[K", "", text)
    return text.lstrip("\ufeff").replace("\ufffd", "").strip()


def _score(text, kws):
    t = text.lower()
    return sum(1 for k in kws if k.lower() in t)


def check_caliber_health():
    global _caliber_alive
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:5679/health", timeout=5)
        _caliber_alive = True
    except:
        _caliber_alive = False
    print(f"[ESSENCE_AUTO] Caliber={'ALIVE' if _caliber_alive else 'DEAD'}")
    return _caliber_alive


def move_reducing_to_re_reduced():
    if not REDUCING.exists():
        return 0
    files = list(REDUCING.glob("*.json"))
    if not files:
        return 0
    moved = 0
    for f in files:
        try:
            dest = RE_REDUCED / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                moved += 1
        except Exception as e:
            print(f"[ESSENCE_AUTO] REDUCING移動失敗: {f.name} {e}")
    if moved > 0:
        print(f"[ESSENCE_AUTO] REDUCING->RE_REDUCED: {moved}件移動")
    return moved


def update_essence_from_events():
    con = sqlite3.connect(str(DB_PATH))
    rows = con.execute(
        "SELECT title, short_summary, free_note, when_ts FROM events ORDER BY rowid DESC LIMIT 500"
    ).fetchall()
    if not rows:
        con.close()
        return 0
    inc_texts, phi_texts, ops_texts = [], [], []
    for title, summary, note, when_ts in rows:
        text = _clean(" ".join(filter(None, [title, summary, note])))
        if not text:
            continue
        si = _score(text, INCIDENT_KW)
        sp = _score(text, PHILOSOPHY_KW)
        so = _score(text, OPERATION_KW)
        if si == 0 and sp == 0 and so == 0:
            continue
        entry = f"[{(when_ts or '?')[:10]}] {text[:150]}"
        if si >= sp and si >= so:
            inc_texts.append(entry)
        elif sp >= si and sp >= so:
            phi_texts.append(entry)
        else:
            ops_texts.append(entry)
    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    for axis, texts in [("INCIDENT", inc_texts),("PHILOSOPHY", phi_texts),("OPERATION", ops_texts)]:
        if texts:
            con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                        ("\n".join(texts[:5]), now, axis))
            print(f"[ESSENCE_AUTO] {axis}更新 ({len(texts)}件)")
            updated += 1
    con.commit()
    con.close()
    if updated > 0:
        try:
            subprocess.run([sys.executable, str(PING_GEN)], cwd=str(ROOT_DIR), timeout=30)
            print("[ESSENCE_AUTO] ping_generator完了")
        except Exception as e:
            print(f"[ESSENCE_AUTO] ping_generator error: {e}")
    return updated


def essence_auto_loop():
    time.sleep(15)
    last_essence = last_reducing = last_caliber = 0
    while True:
        now = time.time()
        try:
            if now - last_reducing >= REDUCING_SEC:
                move_reducing_to_re_reduced()
                last_reducing = now
            if now - last_caliber >= CALIBER_CHECK_SEC:
                check_caliber_health()
                last_caliber = now
            if now - last_essence >= INTERVAL_SEC:
                n = update_essence_from_events()
                if n == 0:
                    print("[ESSENCE_AUTO] essence更新対象なし")
                last_essence = now
        except Exception as e:
            print(f"[ESSENCE_AUTO] 例外: {e}")
        time.sleep(10)


def start_essence_auto_loop():
    t = threading.Thread(target=essence_auto_loop, daemon=True)
    t.start()
    print("[ESSENCE_AUTO] v3起動（essence=5分 / REDUCING=1分 / Caliber死活=2分）")
    return t


if __name__ == "__main__":
    moved = move_reducing_to_re_reduced()
    alive = check_caliber_health()
    n     = update_essence_from_events()
    print(f"[ESSENCE_AUTO] 完了: REDUCING={moved}件 Caliber={alive} essence={n}軸更新")

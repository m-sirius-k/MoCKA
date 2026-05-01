"""
essence_auto_updater.py v2
events.dbのeventsテーブルから直接essenceを生成する
RE_REDUCEDはCaliberのAI要約テキストなので不適切 → DBのeventsを直接使う
"""
import re
import sqlite3
import threading
import time
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR  = Path(r"C:\Users\sirok\MoCKA")
DB_PATH   = ROOT_DIR / "data" / "mocka_events.db"
PING_GEN  = ROOT_DIR / "interface" / "ping_generator.py"

INTERVAL_SEC = 300  # 5分ごと

INCIDENT_KW  = ['エラー','失敗','インシデント','CRITICAL','DANGER','違反','捏造',
                 'なぜ','また同じ','クレーム','INTEGRITY','VIOLATION','バグ','問題','OVERDUE']
PHILOSOPHY_KW= ['AIを信じるな','システムで縛れ','制度','文明','哲学','設計思想',
                 '信じる','縛る','原則','思想','理念','現状の把握',
                 'ここに至る経緯','失敗要因','成功のパターン']
OPERATION_KW = ['完了','稼働','実装','確認','great','グレート','ヒント','success',
                 'hint','運用','手順','ルール','パイプライン','設定','修正済み']


def _clean(text):
    if not text:
        return ''
    text = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', text)
    text = re.sub(r'\x1b\[K', '', text)
    text = text.lstrip('\ufeff').replace('\ufffd', '')
    return text.strip()


def _score(text, kws):
    t = text.lower()
    return sum(1 for k in kws if k.lower() in t)


def update_essence_from_events():
    con = sqlite3.connect(str(DB_PATH))
    rows = con.execute("""
        SELECT title, short_summary, free_note, when_ts
        FROM events
        ORDER BY rowid DESC
        LIMIT 500
    """).fetchall()

    if not rows:
        con.close()
        return 0

    inc_texts, phi_texts, ops_texts = [], [], []

    for title, summary, note, when_ts in rows:
        text = _clean(' '.join(filter(None, [title, summary, note])))
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

    for axis, texts in [('INCIDENT', inc_texts), ('PHILOSOPHY', phi_texts), ('OPERATION', ops_texts)]:
        if texts:
            content = '\n'.join(texts[:5])
            con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                        (content, now, axis))
            print(f"[ESSENCE_AUTO] {axis}更新 ({len(texts)}件から抽出)")
            updated += 1

    con.commit()
    con.close()

    if updated > 0:
        try:
            subprocess.run([sys.executable, str(PING_GEN)], cwd=str(ROOT_DIR), timeout=30)
            print("[ESSENCE_AUTO] ping_generator実行完了")
        except Exception as e:
            print(f"[ESSENCE_AUTO] ping_generator error: {e}")

    return updated


def essence_auto_loop():
    time.sleep(15)
    while True:
        try:
            n = update_essence_from_events()
            if n == 0:
                print("[ESSENCE_AUTO] 更新対象なし")
        except Exception as e:
            print(f"[ESSENCE_AUTO] 例外: {e}")
        time.sleep(INTERVAL_SEC)


def start_essence_auto_loop():
    t = threading.Thread(target=essence_auto_loop, daemon=True)
    t.start()
    print(f"[ESSENCE_AUTO] 自動更新ループ開始（{INTERVAL_SEC}秒間隔）")
    return t


if __name__ == "__main__":
    n = update_essence_from_events()
    print(f"[ESSENCE_AUTO] 完了: {n}軸更新")

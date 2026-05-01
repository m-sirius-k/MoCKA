"""
essence_auto_updater.py
RE_REDUCEDフォルダを監視してessenceテーブルを自動更新する
app.pyのauto_process_loopと同じ構造で動作する
"""
import os
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR     = Path(r"C:\Users\sirok\MoCKA")
RE_REDUCED   = ROOT_DIR / "data" / "storage" / "infield" / "RE_REDUCED"
ESSENCE_DONE = ROOT_DIR / "data" / "storage" / "infield" / "ESSENCE"
DB_PATH      = ROOT_DIR / "data" / "mocka_events.db"
PING_GEN     = ROOT_DIR / "interface" / "ping_generator.py"

# 分類キーワード
INCIDENT_KW  = ['エラー','失敗','インシデント','CRITICAL','DANGER','違反','捏造',
                 'なぜ','また同じ','クレーム','INTEGRITY','VIOLATION','exception',
                 'error','fault','broken','修正','バグ','問題']
PHILOSOPHY_KW= ['AIを信じるな','システムで縛れ','制度','文明','哲学','設計思想',
                 '信じる','縛る','原則','思想','概念','理念','価値観','なぜそうするか',
                 '現状の把握','ここに至る経緯','失敗要因','成功のパターン']
OPERATION_KW = ['完了','稼働','実装','確認','great','グレート','ヒント','success',
                 'hint','運用','手順','ルール','フロー','パイプライン','設定','config']

PROCESSED_LOG = ROOT_DIR / "data" / "essence_processed.json"
INTERVAL_SEC  = 300  # 5分ごと


def _load_processed():
    if PROCESSED_LOG.exists():
        try:
            return set(json.loads(PROCESSED_LOG.read_text(encoding='utf-8')))
        except:
            return set()
    return set()


def _save_processed(processed: set):
    PROCESSED_LOG.write_text(
        json.dumps(list(processed), ensure_ascii=False),
        encoding='utf-8'
    )


def _score(text, kws):
    return sum(1 for k in kws if k.lower() in text.lower())


def _read_file(path):
    for enc in ('utf-8', 'utf-8-sig', 'cp932'):
        try:
            return Path(path).read_text(encoding=enc, errors='ignore')
        except:
            continue
    return ''


def _extract_text(raw):
    """JSONファイルから有意なテキストを抽出"""
    try:
        d = json.loads(raw)
        # extractionフィールドを優先
        parts = []
        for key in ['extraction', 'title', 'short_summary', 'free_note',
                    'why_purpose', 'before_state', 'after_state', 'content']:
            v = d.get(key, '')
            if isinstance(v, str) and v.strip():
                parts.append(v)
        return ' '.join(parts) if parts else raw[:500]
    except:
        return raw[:500]


def update_essence_from_re_reduced():
    """RE_REDUCEDの未処理ファイルを読んでessenceテーブルを更新する"""
    processed = _load_processed()
    files = [f for f in RE_REDUCED.iterdir()
             if f.suffix == '.json' and f.name not in processed]

    if not files:
        return 0

    print(f"[ESSENCE_AUTO] {len(files)}件の未処理ファイルを検出")

    inc_texts, phi_texts, ops_texts = [], [], []

    for f in sorted(files)[-100:]:  # 最新100件まで
        raw = _read_file(f)
        if not raw.strip():
            processed.add(f.name)
            continue
        text = _extract_text(raw)
        si = _score(text, INCIDENT_KW)
        sp = _score(text, PHILOSOPHY_KW)
        so = _score(text, OPERATION_KW)

        if si == 0 and sp == 0 and so == 0:
            processed.add(f.name)
            continue

        if si >= sp and si >= so:
            inc_texts.append(text[:200])
        elif sp >= si and sp >= so:
            phi_texts.append(text[:200])
        else:
            ops_texts.append(text[:200])

        processed.add(f.name)

    _save_processed(processed)

    if not inc_texts and not phi_texts and not ops_texts:
        print("[ESSENCE_AUTO] 分類対象なし（スキップ）")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    con = sqlite3.connect(str(DB_PATH))

    updated = 0
    if inc_texts:
        content = '\n'.join(inc_texts[:5])
        con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                    (content, now, 'INCIDENT'))
        print(f"[ESSENCE_AUTO] INCIDENT更新 ({len(inc_texts)}件から抽出)")
        updated += 1
    if phi_texts:
        content = '\n'.join(phi_texts[:5])
        con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                    (content, now, 'PHILOSOPHY'))
        print(f"[ESSENCE_AUTO] PHILOSOPHY更新 ({len(phi_texts)}件から抽出)")
        updated += 1
    if ops_texts:
        content = '\n'.join(ops_texts[:5])
        con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                    (content, now, 'OPERATION'))
        print(f"[ESSENCE_AUTO] OPERATION更新 ({len(ops_texts)}件から抽出)")
        updated += 1

    con.commit()
    con.close()

    # ping_generatorを実行してping_latest.jsonを更新
    if updated > 0:
        import subprocess, sys
        try:
            subprocess.run(
                [sys.executable, str(PING_GEN)],
                cwd=str(ROOT_DIR),
                timeout=30
            )
            print("[ESSENCE_AUTO] ping_generator実行完了")
        except Exception as e:
            print(f"[ESSENCE_AUTO] ping_generator error: {e}")

    return updated


def essence_auto_loop():
    """定期実行ループ（app.pyのauto_process_loopと同構造）"""
    time.sleep(15)  # 起動時15秒待機
    while True:
        try:
            update_essence_from_re_reduced()
        except Exception as e:
            print(f"[ESSENCE_AUTO] 例外: {e}")
        time.sleep(INTERVAL_SEC)


def start_essence_auto_loop():
    """app.pyから呼ぶエントリーポイント"""
    t = threading.Thread(target=essence_auto_loop, daemon=True)
    t.start()
    print(f"[ESSENCE_AUTO] 自動更新ループ開始（{INTERVAL_SEC}秒間隔）")
    return t


if __name__ == "__main__":
    # 単体実行でも動作確認可能
    n = update_essence_from_re_reduced()
    print(f"[ESSENCE_AUTO] 更新完了: {n}軸更新")

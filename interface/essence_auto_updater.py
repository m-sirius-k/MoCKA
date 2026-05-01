"""
essence_auto_updater.py v4
- きむら博士の発言・思想・インシデントを特化抽出
- 蓄積型（上書きではなく重要発言を積み上げる）
- REDUCING->RE_REDUCED自動移動（1分間隔）
- ESSENCE_DONE自動アーカイブ
- Caliber死活監視（2分間隔）
- ping_generator定期強制実行（essence変化なくても10分毎）
"""
import re, sqlite3, threading, time, subprocess, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR    = Path(r"C:\Users\sirok\MoCKA")
DB_PATH     = ROOT_DIR / "data" / "mocka_events.db"
PING_GEN    = ROOT_DIR / "interface" / "ping_generator.py"
REDUCING    = ROOT_DIR / "data" / "storage" / "infield" / "REDUCING"
RE_REDUCED  = ROOT_DIR / "data" / "storage" / "infield" / "RE_REDUCED"
ESSENCE_DONE= ROOT_DIR / "data" / "storage" / "infield" / "ESSENCE_DONE"

INTERVAL_SEC       = 300   # essence更新: 5分
REDUCING_SEC       = 60    # REDUCING監視: 1分
CALIBER_CHECK_SEC  = 120   # Caliber死活: 2分
PING_FORCE_SEC     = 600   # ping強制実行: 10分（essence変化なくても）
ARCHIVE_SEC        = 3600  # RE_REDUCEDアーカイブ: 1時間
ESSENCE_MAX_LINES  = 8     # 各軸の最大保持行数（蓄積上限）

# きむら博士発言を優先的に抽出するキーワード
KIMURA_SIGNAL = [
    'いやいや', 'なぜ', 'どうして', 'また同じ', 'かっこ',
    'ヒント', 'グレート', 'そこで', 'ハインリッヒ', '組み替え',
    '現状の把握', 'ここに至る経緯', '失敗要因', '成功のパターン',
    '予想し得る危険', '勝ちパターン', '文脈', '分解', '制度',
    '文明', '設計思想', 'hint', 'great'
]

INCIDENT_KW   = ['エラー','失敗','インシデント','CRITICAL','DANGER','違反','捏造',
                  'バグ','問題','OVERDUE','INTEGRITY','VIOLATION','修正','断絶']
PHILOSOPHY_KW = ['AIを信じるな','システムで縛れ','制度','文明','哲学','設計思想',
                  '信じる','縛る','原則','思想','理念','現状の把握',
                  'ここに至る経緯','失敗要因','成功のパターン','組み替え','ハインリッヒ']
OPERATION_KW  = ['完了','稼働','実装','確認','great','グレート','ヒント','success',
                  'hint','運用','手順','ルール','パイプライン','設定','修正済み']

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


def _is_kimura_voice(text):
    """きむら博士の発言らしさを判定"""
    return _score(text, KIMURA_SIGNAL) >= 1


def check_caliber_health():
    global _caliber_alive
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:5679/health", timeout=5)
        _caliber_alive = True
    except:
        _caliber_alive = False
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


def archive_re_reduced():
    """RE_REDUCEDのファイルをESSENCE_DONEにアーカイブ"""
    ESSENCE_DONE.mkdir(parents=True, exist_ok=True)
    files = list(RE_REDUCED.glob("*.json"))
    if not files:
        return 0
    moved = 0
    for f in sorted(files)[:-10]:  # 最新10件はRE_REDUCEDに残す
        try:
            dest = ESSENCE_DONE / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                moved += 1
        except:
            pass
    if moved > 0:
        print(f"[ESSENCE_AUTO] RE_REDUCED->ESSENCE_DONE: {moved}件アーカイブ")
    return moved


def run_ping_generator():
    try:
        subprocess.run([sys.executable, str(PING_GEN)], cwd=str(ROOT_DIR), timeout=30)
        print("[ESSENCE_AUTO] ping_generator強制実行完了")
    except Exception as e:
        print(f"[ESSENCE_AUTO] ping_generator error: {e}")


def update_essence_from_events():
    """
    eventsテーブルから蓄積型essenceを生成。
    きむら博士の発言を優先し、重要行を積み上げる。
    """
    con = sqlite3.connect(str(DB_PATH))

    # 最新1000件から候補を取得
    rows = con.execute(
        "SELECT title, short_summary, free_note, who_actor, when_ts "
        "FROM events ORDER BY rowid DESC LIMIT 1000"
    ).fetchall()

    if not rows:
        con.close()
        return 0

    # 現在のessenceを取得（蓄積のベース）
    current = {}
    for axis, content, _ in con.execute("SELECT axis, content, updated_at FROM essence").fetchall():
        current[axis] = content or ""

    inc_new, phi_new, ops_new = [], [], []

    for title, summary, note, who, when_ts in rows:
        text = _clean(" ".join(filter(None, [title, summary, note])))
        if not text or len(text) < 10:
            continue

        # きむら博士発言は最優先
        is_kimura = _is_kimura_voice(text)
        si = _score(text, INCIDENT_KW)
        sp = _score(text, PHILOSOPHY_KW)
        so = _score(text, OPERATION_KW)

        if si == 0 and sp == 0 and so == 0 and not is_kimura:
            continue

        date = (when_ts or "?")[:10]
        entry = f"[{date}] {text[:180]}"

        # すでに同じ内容が現在のessenceに入っていればスキップ
        already_in = any(text[:50] in current.get(ax, "") for ax in ["INCIDENT","PHILOSOPHY","OPERATION"])
        if already_in:
            continue

        if sp >= si and sp >= so or (is_kimura and sp > 0):
            phi_new.append((is_kimura, entry))
        elif si >= sp and si >= so:
            inc_new.append((is_kimura, entry))
        else:
            ops_new.append((is_kimura, entry))

    # きむら博士発言を優先ソート
    for lst in [inc_new, phi_new, ops_new]:
        lst.sort(key=lambda x: x[0], reverse=True)

    now = datetime.now(timezone.utc).isoformat()
    updated = 0

    def merge_essence(axis, new_entries, current_content):
        """現在のessenceに新規行を追加し、上限行数を超えたら古い行を削除"""
        current_lines = [l for l in current_content.split("\n") if l.strip()]
        new_lines = [e for _, e in new_entries[:3]]  # 最大3件追加
        merged = new_lines + current_lines
        # 重複除去
        seen, deduped = set(), []
        for line in merged:
            key = line[:60]
            if key not in seen:
                seen.add(key)
                deduped.append(line)
        return "\n".join(deduped[:ESSENCE_MAX_LINES])

    for axis, new_entries, kw_name in [
        ("INCIDENT",   inc_new, "インシデント"),
        ("PHILOSOPHY", phi_new, "思想"),
        ("OPERATION",  ops_new, "運用")
    ]:
        if new_entries:
            merged = merge_essence(axis, new_entries, current.get(axis, ""))
            con.execute("UPDATE essence SET content=?, updated_at=? WHERE axis=?",
                        (merged, now, axis))
            kimura_count = sum(1 for k, _ in new_entries[:3] if k)
            print(f"[ESSENCE_AUTO] {axis}更新 (新規{len(new_entries[:3])}件 うちきむら博士発言{kimura_count}件)")
            updated += 1

    con.commit()
    con.close()
    return updated


def essence_auto_loop():
    time.sleep(15)
    last_essence = last_reducing = last_caliber = last_ping = last_archive = 0
    while True:
        now = time.time()
        try:
            if now - last_reducing >= REDUCING_SEC:
                move_reducing_to_re_reduced()
                last_reducing = now

            if now - last_caliber >= CALIBER_CHECK_SEC:
                alive = check_caliber_health()
                status = "ALIVE" if alive else "DEAD"
                print(f"[ESSENCE_AUTO] Caliber({status})")
                last_caliber = now

            if now - last_essence >= INTERVAL_SEC:
                n = update_essence_from_events()
                if n > 0:
                    run_ping_generator()
                    last_ping = now
                else:
                    print("[ESSENCE_AUTO] essence変化なし")
                last_essence = now

            # essenceが更新されなくても10分毎にping強制実行
            if now - last_ping >= PING_FORCE_SEC:
                run_ping_generator()
                last_ping = now

            if now - last_archive >= ARCHIVE_SEC:
                archive_re_reduced()
                last_archive = now

        except Exception as e:
            print(f"[ESSENCE_AUTO] 例外: {e}")
        time.sleep(10)


def start_essence_auto_loop():
    t = threading.Thread(target=essence_auto_loop, daemon=True)
    t.start()
    print("[ESSENCE_AUTO] v4起動（essence=5分/ping強制=10分/REDUCING=1分/Caliber=2分/アーカイブ=1時間）")
    return t


if __name__ == "__main__":
    moved   = move_reducing_to_re_reduced()
    archived= archive_re_reduced()
    alive   = check_caliber_health()
    n       = update_essence_from_events()
    if n > 0:
        run_ping_generator()
    print(f"[ESSENCE_AUTO] v4完了: REDUCING={moved}件 アーカイブ={archived}件 Caliber={alive} essence={n}軸更新")

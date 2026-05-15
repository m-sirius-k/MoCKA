import sqlite3
import csv
import sys as _sys
_sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent / 'interface'))
import db_helper
import shutil
import os
import json
import subprocess
import sys
import requests
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request

# --- Pattern Engine v2 ---
try:
    from interface.pattern_engine_v2 import PatternEngine as _PatternEngine
    _pattern_engine = _PatternEngine()
    print(f"[pattern_engine] OK - {len(_pattern_engine.registry.records)} keywords")
except Exception as _pe_err:
    _pattern_engine = None
    print(f"[pattern_engine] WARN: {_pe_err}")
_pattern_score_history = []
_PATTERN_HISTORY_MAX   = 100

def run_pattern_score(text):
    global _pattern_score_history
    if not _pattern_engine or not text:
        return
    try:
        r = _pattern_engine.analyze(text)
        r["timestamp"] = datetime.now().isoformat()
        r["preview"]   = text[:60]
        _pattern_score_history.append(r)
        if len(_pattern_score_history) > _PATTERN_HISTORY_MAX:
            _pattern_score_history = _pattern_score_history[-_PATTERN_HISTORY_MAX:]
        if r["verdict"] in ("CRITICAL","DANGER"):
            print(f"[pattern] {r['verdict']} R={r['R']} '{text[:40]}'")
    except Exception as e:
        print(f"[pattern_engine] error: {e}")

from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# ============================================================
# 文字化け撲滅 防御ミドルウェア (2026-04-29)
# ============================================================
import unicodedata

def _sanitize_utf8(text: str) -> str:
    """制御文字・BOM・代替文字を除去してUTF-8安全文字列を返す"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    # BOM除去
    text = text.lstrip("\ufeff")
    # Shift-JIS混入文字（U+FFFD 代替文字）を警告・除去
    if "\ufffd" in text:
        print(f"[ENCODING-GUARD] U+FFFD detected → stripped")
        text = text.replace("\ufffd", "")
    # 制御文字除去（タブ・改行は保持）
    text = "".join(c for c in text if unicodedata.category(c) != "Cc" or c in ("\t", "\n", "\r"))
    return text

def _sanitize_row(row: dict) -> dict:
    """イベント行の全フィールドをUTF-8安全化"""
    return {k: _sanitize_utf8(v) for k, v in row.items()}

# append_event をラップして文字化け防御
_orig_append_event = None  # 後でパッチ


# ===== 自動処理ループ（PILSキュー監視） =====
import threading
import time

PILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "storage", "outbox", "PILS")

def auto_process_loop():
    time.sleep(5)
    while True:
        try:
            files = [f for f in os.listdir(PILS_DIR) if f.endswith(".json")]
            if files:
                print("[AUTO] PILS queue: {} -> processing".format(len(files)))
                r = requests.post(
                    CALIBER_SERVER + "/process",
                    json={},
                    headers={"Content-Type": "application/json"},
                    timeout=1800
                )
                if r.status_code == 200:
                    result = r.json()
                    rate = result.get("restore_rate", "?")
                    print("[AUTO] 完了 restore_rate={}".format(rate))
                else:
                    print("[AUTO] エラー({}): {}".format(r.status_code, r.text[:80]))
            time.sleep(10)
        except Exception as e:
            print("[AUTO] 例外: {}".format(str(e)[:80]))
            time.sleep(30)

_auto_thread = threading.Thread(target=auto_process_loop, daemon=True)
_auto_thread.start()

# ===== Essence自動更新ループ（RE_REDUCED監視）=====
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        'essence_auto_updater',
        str(Path(__file__).parent / 'interface' / 'essence_auto_updater.py')
    )
    _eau = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_eau)
    _eau.start_essence_auto_loop()
except Exception as _eau_err:
    print(f"[ESSENCE_AUTO] 起動失敗: {_eau_err}")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
EVENTS_CSV = os.path.join(DATA_DIR, "events.csv")  # 廃止済み変数（互換保持のみ・書き込み禁止）
BASE_DIR = ROOT_DIR
RECORDS_DIR = os.path.join(BASE_DIR, "records")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OLD_DIR = os.path.join(BASE_DIR, "OLD_FILES")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
STORAGE = os.path.join(DATA_DIR, "storage", "infield")
OUTBOX  = os.path.join(DATA_DIR, "storage", "outbox", "PILS")
CALIBER_SERVER = "http://localhost:5679"
PATTERN_SCORE  = os.path.join(DATA_DIR, "latest_score.json")

FIELDNAMES = [
    "event_id", "when", "who_actor", "what_type",
    "where_component", "where_path", "why_purpose", "how_trigger",
    "channel_type", "lifecycle_phase", "risk_level",
    "category_ab", "target_class", "title", "short_summary",
    "before_state", "after_state", "change_type",
    "impact_scope", "impact_result", "related_event_id", "trace_id", "free_note",
]

_intent_queue = {}
_intent_lock = threading.Lock()

# ===== Pattern Hook =====
def run_pattern_score(text):
    try:
        import pattern_engine
        result = pattern_engine.score_text(text)
        print(f"[PATTERN] verdict={result['verdict']} s={result['success_score']} f={result['failure_score']}")
        with open(PATTERN_SCORE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[PATTERN] error: {e}")
        result = None

    # ===== Morphology Engine 接続 =====
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            'morphology_engine',
            os.path.join(ROOT_DIR, 'interface', 'morphology_engine.py')
        )
        _me = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_me)
        morph = _me.predict(text, threshold=0.3)
        if morph['prediction'] != 'SAFE':
            print(f"[MORPHO] {morph['prediction']} score={morph['danger_score']} tokens={morph['tokens'][:5]}")
            # DANGER以上はprevention_queueに自動追加
            if morph['danger_score'] >= 0.4:
                try:
                    pq_path = os.path.join(ROOT_DIR, 'data', 'prevention_queue.json')
                    pq = json.load(open(pq_path, encoding='utf-8')) if os.path.exists(pq_path) else []
                    import datetime
                    pq.append({
                        "id": f"MORPHO_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "MORPHO_DANGER",
                        "pattern": '|'.join(morph['tokens'][:5]),
                        "danger_score": morph['danger_score'],
                        "matched_l1": morph.get('matched_l1', []),
                        "proposal": [
                            f"【形態素解析】危険スコア{morph['danger_score']*100:.0f}%: {morph['interpretation']}",
                            f"【パターン】{[m['pattern'] for m in morph.get('matched_l1', [])[:3]]}",
                            "【対応】danger_patternsへの登録検討"
                        ],
                        "status": "pending",
                        "risk_level": "high" if morph['danger_score'] >= 0.6 else "normal"
                    })
                    json.dump(pq, open(pq_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
                except Exception as _pe:
                    print(f"[MORPHO] prevention_queue error: {_pe}")
        # 形態素スコアをファイルに保存
        morph_score_path = os.path.join(ROOT_DIR, 'data', 'morpho_score.json')
        json.dump(morph, open(morph_score_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    except Exception as me:
        print(f"[MORPHO] error: {me}")
        morph = None

    return result

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "master"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "summary"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "context"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "audit"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "structured"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "timeline"), exist_ok=True)
    os.makedirs(OLD_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "decisions"), exist_ok=True)

def ensure_events_csv():
    # CSV廃止済み（SQLite単一化 2026-04-29）。後方互換のため関数は残す。
    ensure_dirs()

def next_event_id():
    return db_helper.get_next_event_id()

def append_event(meta: dict):
    # CSV書き込み廃止 → SQLite(db_helper)のみ + 文字化け防御
    row = {key: "N/A" for key in FIELDNAMES}
    for k, v in meta.items():
        if k in row and v is not None:
            row[k] = _sanitize_utf8(str(v))
    if row["event_id"] == "N/A":
        row["event_id"] = next_event_id()
    if row["when"] == "N/A":
        row["when"] = datetime.now().isoformat(timespec="seconds")
    eid = row["event_id"]
    category = row.get("category_ab", "N/A")
    target = row.get("target_class", "N/A")
    master_path = os.path.join(RECORDS_DIR, "master", f"{eid}.json")
    master_obj = {
        "event_id": eid,
        "timestamp": row["when"],
        "what_type": row.get("what_type", "N/A"),
        "status": "recorded",
        "category": category,
        "target": target,
    }
    with open(master_path, "w", encoding="utf-8-sig") as f:
        json.dump(master_obj, f, ensure_ascii=False, indent=2)
    db_helper.write_event(row)

def load_history(limit=None):
    rows = db_helper.read_events(limit=int(limit) if limit else None)
    # 既存コードとの互換性: 全フィールドを文字列に正規化
    rows = [{k: (v if v is not None else "") for k, v in r.items()} for r in rows]
    return rows

def count_layer(layer):
    d = os.path.join(STORAGE, layer)
    if not os.path.exists(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith(".json")])

# =========================
# Flask Routes
# =========================




# ===== DECISION INTELLIGENCE: 判断理由ログ =====
@app.route('/decision/log/detail', methods=['GET'])
def decision_log_detail():
    """Decision LogにPrevention Queue情報を突合して詳細表示"""
    try:
        import sqlite3 as _sq, json as _json
        # prevention_queue読み込み
        pq_path = os.path.join(os.path.dirname(__file__), 'data', 'prevention_queue.json')
        pq_map = {}
        if os.path.exists(pq_path):
            with open(pq_path, encoding='utf-8') as f:
                pq_data = _json.load(f)
            for item in pq_data.get('queue', []):
                pq_map[item['id']] = item

        conn = _sq.connect(db_helper.DB_PATH)
        rows = conn.execute("""
            SELECT event_id, when_ts, title, free_note, risk_level, what_type
            FROM events
            WHERE what_type IN ('DECISION_APPROVED','DECISION_REJECTED','decision')
            ORDER BY when_ts DESC
            LIMIT 10
        """).fetchall()
        conn.close()

        # basis_event_ids用: component+what_typeでevents DB照合
        conn2 = _sq.connect(db_helper.DB_PATH)
        def _get_basis_events(component, what_type_pq):
            try:
                rs = conn2.execute(
                    """SELECT event_id FROM events
                       WHERE (title LIKE ? OR free_note LIKE ?)
                       AND what_type NOT IN ('DECISION_APPROVED','DECISION_REJECTED')
                       ORDER BY when_ts DESC LIMIT 3""",
                    (f'%{component}%', f'%{what_type_pq}%')
                ).fetchall()
                return [r[0] for r in rs]
            except:
                return []

        decisions = []
        for r in rows:
            event_id, when_ts, title, free_note, risk_level, what_type = r
            pq = pq_map.get(free_note, {})
            rc = pq.get('recurrence_count', 0)
            sev = (risk_level or pq.get('severity', 'normal')).upper()
            comp = pq.get('component', 'N/A')
            wt = pq.get('what_type', 'N/A')

            # 判断理由自動生成
            if rc >= 10:
                why = f'{comp}:{wt} が{rc}回再発 — 制度的介入が必要と判断'
            elif rc >= 3:
                why = f'{comp}:{wt} が{rc}回再発 — バリデーション追加を承認'
            else:
                why = f'{comp}:{wt} インシデント検知 — 予防措置を承認'

            # ESSENCE軸判定
            if sev in ('HIGH', 'CRITICAL') or rc >= 5:
                essence_axis = 'INCIDENT'
            elif rc >= 2:
                essence_axis = 'OPERATION'
            else:
                essence_axis = 'PHILOSOPHY'

            basis_ids = _get_basis_events(comp, wt)

            decisions.append({
                'event_id':         event_id,
                'when_ts':          when_ts,
                'verdict':          'APPROVED' if 'APPROVED' in (what_type or '') else 'REJECTED',
                'risk_level':       sev,
                'component':        comp,
                'what_type':        wt,
                'recurrence_count': rc,
                'candidates':       pq.get('candidates', []),
                'source':           pq.get('source', 'manual'),
                'pq_id':            free_note,
                'why_decided':      why,
                'essence_axis':     essence_axis,
                'basis_event_ids':  basis_ids,
            })
        conn2.close()

        return jsonify({'decisions': decisions, 'count': len(decisions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== TEMPORAL ANALYTICS: 7日トレンド =====
@app.route('/temporal/trend', methods=['GET'])
@app.route('/trend/weekly', methods=['GET'])
def temporal_trend():
    """直近7日のイベント推移・リスク分布・user_voice件数を返す"""
    try:
        from datetime import datetime, timedelta
        import sqlite3 as _sqlite3
        conn = _sqlite3.connect(db_helper.DB_PATH)
        days = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            total = conn.execute(
                "SELECT COUNT(*) FROM events WHERE when_ts LIKE ?", (f'{d}%',)
            ).fetchone()[0]
            danger = conn.execute(
                "SELECT COUNT(*) FROM events WHERE when_ts LIKE ? AND risk_level IN ('high','critical','danger')",
                (f'{d}%',)
            ).fetchone()[0]
            voice = conn.execute(
                "SELECT COUNT(*) FROM events WHERE when_ts LIKE ? AND what_type='user_voice'",
                (f'{d}%',)
            ).fetchone()[0]
            incident = conn.execute(
                "SELECT COUNT(*) FROM events WHERE when_ts LIKE ? AND what_type IN ('claim','mataka','incident')",
                (f'{d}%',)
            ).fetchone()[0]
            days.append({
                'date': d,
                'label': d[5:],   # MM-DD形式
                'total': total,
                'danger': danger,
                'voice': voice,
                'incident': incident,
                'l1': danger,     # Heinrich Layer1 = high/critical/danger
                'l3': voice,      # Heinrich Layer3 = user_voice（活動量）
            })
        conn.close()

        # トレンド矢印（直近3日 vs 前4日の平均比較）
        recent_avg = sum(d['total'] for d in days[-3:]) / 3
        prev_avg   = sum(d['total'] for d in days[:4]) / 4
        if recent_avg > prev_avg * 1.1:
            trend = '↑'
        elif recent_avg < prev_avg * 0.9:
            trend = '↓'
        else:
            trend = '→'

        return jsonify({'days': days, 'trend': trend, 'recent_avg': round(recent_avg, 1), 'prev_avg': round(prev_avg, 1)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== USER VOICE: きむら博士の発言を自動保存 =====
@app.route('/user_voice', methods=['POST'])
def user_voice():
    """content.js から送信される きむら博士の発言を events.db に保存する"""
    import re as _re
    try:
        data      = request.get_json(force=True)
        text      = data.get('text', '').strip()
        url       = data.get('url', '')
        timestamp = data.get('timestamp', '')

        if not text:
            return jsonify({'status': 'skip', 'reason': 'empty'}), 200

        # ===== サーバー側フィルター: きむら博士の発言のみ保存 =====
        def is_kimura_voice(t):
            # 3文字以下はスキップ
            if len(t) < 3:
                return False
            # システムログパターン（確実なノイズ）
            noise_patterns = [
                r'^\[PING',
                r'^\[MOCKA',
                r'^\[UTF-8',
                r'^Traceback',
                r'^File "[^"]+", line \d+',
                r'^SyntaxError:',
                r'^TypeError:',
                r'^ValueError:',
                r'^AttributeError:',
                r'^ImportError:',
                r'^OperationalError:',
                r'^Enumerating objects:',
                r'^Counting objects:',
                r'^Writing objects:',
                r'^remote:',
                r'^StatusCode\s+:',
                r'^StatusDescription\s+:',
                r'^RawContent\s+:',
                r'^Content\s+:',
                r'^Loading the font',
                r'^\[COMPLETION\]',
                r'^\[O11Y\]',
            ]
            for pat in noise_patterns:
                if _re.match(pat, t):
                    return False

            # 日本語を含む → きむら博士の発言として保存
            if _re.search(r'[ぁ-んァ-ン一-龥]', t):
                return True

            # 英数字のみ かつ 短い（40文字以下）→ コマンド・短い指示として保存
            if len(t) <= 40:
                return True

            # 英数字のみ かつ 長い → PowerShell出力の可能性 → スキップ
            return False

        if not is_kimura_voice(text):
            return jsonify({'status': 'skip', 'reason': 'noise_filtered'}), 200

        chat_id = 'unknown'
        m = _re.search(r'/chat/([a-zA-Z0-9_-]+)', url)
        if m:
            chat_id = m.group(1)[:16]

        event_id = next_event_id()
        when_ts  = timestamp or datetime.now().isoformat()

        append_event({
            'event_id':        event_id,
            'what_type':       'user_voice',
            'who_actor':       'kimura',
            'where_component': 'claude.ai',
            'where_path':      chat_id,
            'when':            when_ts,
            'why_purpose':     'voice_capture',
            'how_trigger':     'chrome_extension_v15',
            'title':           text[:200],
            'free_note':       text,
            'channel_type':    'chat',
        })


        # ===== matcher_v3 自動照合 =====
        try:
            import importlib.util
            from pathlib import Path
            _mpath = Path(r'C:\Users\sirok\MoCKA\interface\matcher_v3.py')
            _spec = importlib.util.spec_from_file_location("matcher_v3", _mpath)
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _result = _mod.match_v3(text, verbose=False)
            # ping_latest.jsonに結果を追記
            import json as _json
            _ping_path = Path(r'C:\Users\sirok\MoCKA\data\ping_latest.json')
            if _ping_path.exists():
                _ping = _json.loads(_ping_path.read_text(encoding='utf-8'))
            else:
                _ping = {}
            _ping['matcher_result'] = {
                'verdict':      _result['verdict'],
                'score':        _result['score'],
                'danger_rate':  _result['danger_rate'],
                'success_rate': _result['success_rate'],
                'text':         text[:80],
                'top_events':   _result['top_events'][:2],
                'updated_at':   when_ts,
            }
            _ping_path.write_text(_json.dumps(_ping, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as _e:
            import traceback
            print('[MOCKA matcher_v3 ERROR]', traceback.format_exc())
        # ===== matcher_v3 終了 =====

        return jsonify({'status': 'ok', 'event_id': event_id}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/")
def index():
    return send_from_directory(ROOT_DIR, "index.html")

@app.route("/get_history")
def get_history():
    rows = load_history()
    return jsonify(rows)

@app.route("/get_intent/<ai_name>")
def get_intent(ai_name):
    with _intent_lock:
        queue = _intent_queue.get(ai_name, [])
        if not queue:
            return '', 204
        payload = queue.pop(0)
        _intent_queue[ai_name] = queue
    print(f"[INTENT] {ai_name} -> payload dispatched")
    return jsonify({"payload": payload})

@app.route("/set_intent", methods=["POST"])
def set_intent():
    payload = request.get_json(force=True, silent=True) or {}
    ai_name = payload.get("ai_name", "")
    text    = payload.get("text", "")
    if not ai_name or not text:
        return jsonify({"status": "error", "message": "ai_name and text required"}), 400
    with _intent_lock:
        if ai_name not in _intent_queue:
            _intent_queue[ai_name] = []
        _intent_queue[ai_name].append(text)
    append_event({
        "what_type": "collaboration",
        "category_ab": "B",
        "target_class": ai_name,
        "title": f"協業依頼 -> {ai_name}",
        "short_summary": text[:100],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "local",
    })
    return jsonify({"status": "ok", "ai_name": ai_name})

@app.route("/collaborate", methods=["POST"])
def collaborate():
    payload = request.get_json(force=True, silent=True) or {}
    text    = payload.get("text", payload.get("prompt", ""))
    targets = payload.get("targets", ["ChatGPT", "Gemini", "Claude", "Perplexity", "Copilot", "Genspark"])
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    with _intent_lock:
        for ai_name in targets:
            if ai_name not in _intent_queue:
                _intent_queue[ai_name] = []
            _intent_queue[ai_name].append(text)
    try:
        subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", text, "collaborate"], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    except Exception as e:
        print(f"[COLLABORATE] orchestra error: {e}")
    append_event({
        "what_type": "collaboration",
        "category_ab": "B",
        "target_class": ",".join(targets),
        "title": f"協業一括投入: {text[:40]}",
        "short_summary": text[:200],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "multi_ai",
    })
    return jsonify({"status": "ok", "targets": targets})

@app.route("/caliber/status")
def caliber_status():
    layers = ["RAW", "REDUCED", "RE_REDUCED", "REDUCING", "CORE", "ESSENCE", "RAW_DONE"]
    counts = {layer: count_layer(layer) for layer in layers}
    outbox = len([f for f in os.listdir(OUTBOX) if f.endswith(".json")]) if os.path.exists(OUTBOX) else 0
    counts["outbox_PILS"] = outbox
    try:
        r = requests.get(CALIBER_SERVER + "/health", timeout=2)
        server = "online" if r.status_code == 200 else "error"
    except:
        server = "offline"
    return jsonify({"layers": counts, "caliber_server": server})

@app.route("/caliber/process", methods=["POST"])
def caliber_process():
    try:
        r = requests.post(CALIBER_SERVER + "/process", json={}, headers={"Content-Type": "application/json"}, timeout=1800)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/caliber/scan")
def caliber_scan():
    try:
        r = requests.get(CALIBER_SERVER + "/scan", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/orchestra", methods=["POST"])
def orchestra():
    payload = request.get_json(force=True, silent=True) or {}
    prompt = payload.get("prompt", "MoCKA Broadcast")
    mode = payload.get("mode", "orchestra")
    subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", prompt, mode], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    return jsonify({"status": "ok"})

@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(force=True, silent=True) or {}
    c = payload.get("c")
    o = payload.get("o")
    memo = payload.get("memo", "").strip()
    if c not in ("A", "B") or not o:
        return jsonify({"status": "error", "message": "invalid payload"}), 400
    if c == "A":
        what_type = "storage"
        title = f"保存取得 {o}"
        short_summary = "Storage mission dispatched"
    else:
        what_type = "broadcast"
        title = f"共有配信 {o}"
        short_summary = "Broadcast mission dispatched"
    meta = {
        "what_type": what_type,
        "category_ab": c,
        "target_class": o,
        "title": title,
        "short_summary": memo if memo else short_summary,
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "where_path": "mocka-extension/background.js",
        "why_purpose": "save/broadcast from command center",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "before_state": "N/A",
        "after_state": "N/A",
        "change_type": "N/A",
        "impact_scope": "local",
        "impact_result": "N/A",
        "related_event_id": "N/A",
        "trace_id": "N/A",
        "free_note": memo if memo else "N/A",
    }
    append_event(meta)
    if c == "A" and memo:
        try:
            _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
            subprocess.Popen([sys.executable, _pl, "--text", memo.strip(), "--no-ping"], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        except Exception as _e:
            print(f"[ASK] pipeline error: {_e}")
        # Pattern scoring
        threading.Thread(target=run_pattern_score, args=(memo,), daemon=True).start()
    return jsonify({"status": "ok"})


# ===== またか！/ クレーム！エンドポイント =====

# ===== 軸3: essence自動更新バッチ =====
def auto_update_essence_from_mataka():
    try:
        import re as _re3
        from pathlib import Path as _P3
        pdb = os.path.join(ROOT_DIR, 'data', 'morphology_patterns.db')
        if not os.path.exists(pdb): return
        pcon = sqlite3.connect(pdb)
        pcur = pcon.cursor()
        pcur.execute("SELECT ngram, count FROM patterns WHERE layer=1 ORDER BY count DESC LIMIT 5")
        top_patterns = pcur.fetchall()
        pcon.close()
        if not top_patterns: return
        essence_path = _P3(r'C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json')
        if not essence_path.exists(): return
        essence = json.load(open(essence_path, encoding='utf-8'))
        now = datetime.datetime.now().isoformat()
        lines = ['[AUTO_MATAKA_TOP5 ' + now[:10] + ']']
        for ng, cnt in top_patterns:
            lines.append('  ' + str(cnt) + 'kai: ' + ng)
        block = '\n'.join(lines)
        old = essence.get('INCIDENT','')
        old = _re3.sub(r'\[AUTO_MATAKA_TOP5[^\]]*\][^\[]*','',old).strip()
        essence['INCIDENT'] = old + '\n' + block
        essence['updated_at'] = now
        json.dump(essence, open(essence_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
        print('[ESSENCE] MATAKA Top5 自動更新完了')
    except Exception as e:
        print('[ESSENCE] error: ' + str(e))

def check_and_trigger_essence_update():
    try:
        db_path = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM events WHERE what_type='MATAKA'")
        count = cur.fetchone()[0]
        con.close()
        if count > 0 and count % 5 == 0:
            threading.Thread(target=auto_update_essence_from_mataka, daemon=True).start()
            print('[ESSENCE] MATAKA ' + str(count) + '件 -> essence自動更新トリガー')
    except Exception as e:
        print('[ESSENCE] trigger error: ' + str(e))

@app.route("/mataka", methods=["POST"])
def mataka():
    """再発クレーム — Essence_Direct_Parserで5W1H抽出→recurrence照合→prevention昇格"""
    import hashlib as _hs
    from datetime import datetime, timezone
    d = request.get_json(force=True, silent=True) or {}
    selected_text = d.get("selected_text", "")
    url           = d.get("url", "")
    who           = d.get("who", "unknown")
    ts            = datetime.now(timezone.utc)
    ts_str        = ts.strftime("%Y-%m-%dT%H:%M:%S")
    ts_f          = ts.strftime("%Y%m%d_%H%M%S")
    if not selected_text:
        return jsonify({"status": "empty"}), 400

    # Essence_Direct_Parserで5W1H抽出
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT_DIR, 'interface'))
        import os as _eos; _eos.environ['PYTHONIOENCODING']='utf-8'
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location('EDP', r'C:/Users/sirok/MoCKA/interface/Essence_Direct_Parser.py')
        _edp = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_edp)
        extract_5w1h = _edp.extract_5w1h
        w5h1 = extract_5w1h(selected_text, who=who, url=url, incident_type="MATAKA")
    except Exception as e:
        w5h1 = {
            "who": who, "what": selected_text[:80], "when": ts_str,
            "where": url[:80], "why": "再発パターン検知", "how": "またか！ボタン押下"
        }

    # recurrence_registry照合 — 同パターン何回目か
    recurrence_count = 1
    pattern_key = selected_text[:50].strip()
    try:
        import sqlite3
        db_path = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM events WHERE what_type='MATAKA' AND title LIKE ?",
            (f"%{pattern_key[:30]}%",)
        )
        recurrence_count = (cur.fetchone()[0] or 0) + 1
        con.close()
    except Exception:
        pass

    eid = f"MATAKA_{ts_f}_{who[:4].upper()}"
    h   = _hs.sha256(f"{eid}{ts_str}{selected_text[:50]}".encode()).hexdigest()[:16]

    # events.dbに構造化記録
    db_helper.write_event({
        "event_id": eid, "when": ts_str,
        "who_actor": w5h1.get("who", who),
        "what_type": "MATAKA",
        "where_component": w5h1.get("where", url[:80]),
        "where_path": "chrome_extension",
        "why_purpose": f"再発#{recurrence_count}: {w5h1.get('why','再発パターン')}",
        "how_trigger": "またか！ボタン",
        "channel_type": "external",
        "lifecycle_phase": "in_operation",
        "risk_level": "high" if recurrence_count >= 3 else "normal",
        "category_ab": "B",
        "target_class": "recurrence",
        "title": selected_text[:100],
        "short_summary": f"再発#{recurrence_count}",
        "before_state": "recurring_issue",
        "after_state": "recorded",
        "change_type": "incident",
        "impact_scope": "ai_behavior",
        "impact_result": f"recurrence_count={recurrence_count}",
        "related_event_id": "N/A", "trace_id": "N/A",
        "free_note": f"hash={h}|who={who}|pattern={pattern_key}",
    })

    # 3回以上でprevention_queue自動昇格
    if recurrence_count >= 3:
        try:
            pq_path = os.path.join(ROOT_DIR, 'data', 'prevention_queue.json')
            pq = json.load(open(pq_path, encoding='utf-8')) if os.path.exists(pq_path) else []
            pq.append({
                "id": eid,
                "timestamp": ts_str,
                "type": "MATAKA_AUTO",
                "pattern": pattern_key,
                "recurrence_count": recurrence_count,
                "who": who,
                "proposal": [
                    f"【制度改善案】「{pattern_key[:40]}」が{recurrence_count}回再発。danger_patternsに登録を検討",
                    f"【運用改善案】essenceのINCIDENT軸に「{who}の癖: {pattern_key[:40]}」を明記",
                    f"【設計改善案】該当パターンをCLAUDE_RULES.mdに禁止事項として追記"
                ],
                "status": "pending",
                "risk_level": "high"
            })
            json.dump(pq, open(pq_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MATAKA] prevention_queue error: {e}")

    # language_detector経由でDANGERシグナルも発火
    threading.Thread(target=run_pattern_score, args=(selected_text,), daemon=True).start()

    # 軸2: morphology自動更新
    try:
        import importlib.util as _ilu2, datetime as _dt2
        _spec2 = _ilu2.spec_from_file_location('morphology_engine2', os.path.join(ROOT_DIR,'interface','morphology_engine.py'))
        _me2 = _ilu2.module_from_spec(_spec2)
        _spec2.loader.exec_module(_me2)
        tokens = _me2.tokenize(selected_text)
        ngrams = _me2.generate_ngrams(tokens, n=3)
        if ngrams:
            pdb = os.path.join(ROOT_DIR, 'data', 'morphology_patterns.db')
            pcon = sqlite3.connect(pdb)
            pcur = pcon.cursor()
            now_str = _dt2.datetime.now().isoformat()
            added = 0
            for ng in ngrams:
                ng_str = '|'.join(ng)
                try:
                    pcur.execute("""INSERT INTO patterns(ngram,layer,event_id,source,count,last_seen) VALUES(?,1,?,?,1,?) ON CONFLICT(ngram,layer) DO UPDATE SET count=count+1,last_seen=?""", (ng_str,eid,'MATAKA',now_str,now_str))
                    added += 1
                except Exception: pass
            pcon.commit(); pcon.close()
            print('[MATAKA] morphology自動更新: ' + str(added) + 'パターン追加')
    except Exception as _me2e:
        print('[MATAKA] morphology更新エラー: ' + str(_me2e))

    # 軸4: フィードバックループ閉鎖
    threading.Thread(target=check_and_trigger_essence_update, daemon=True).start()

    return jsonify({
        "status": "ok",
        "event_id": eid,
        "recurrence_count": recurrence_count,
        "pattern": pattern_key,
        "w5h1": w5h1,
        "auto_escalated": recurrence_count >= 3
    })


@app.route("/claim", methods=["POST"])
def claim():
    """クレーム！— 新規インシデント即時記録"""
    import hashlib as _hs
    from datetime import datetime, timezone
    d = request.get_json(force=True, silent=True) or {}
    selected_text = d.get("selected_text", "")
    url           = d.get("url", "")
    who           = d.get("who", "unknown")
    ts            = datetime.now(timezone.utc)
    ts_str        = ts.strftime("%Y-%m-%dT%H:%M:%S")
    ts_f          = ts.strftime("%Y%m%d_%H%M%S")
    if not selected_text:
        return jsonify({"status": "empty"}), 400

    # Essence_Direct_Parserで5W1H抽出
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT_DIR, 'interface'))
        import os as _eos; _eos.environ['PYTHONIOENCODING']='utf-8'
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location('EDP', r'C:/Users/sirok/MoCKA/interface/Essence_Direct_Parser.py')
        _edp = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_edp)
        extract_5w1h = _edp.extract_5w1h
        w5h1 = extract_5w1h(selected_text, who=who, url=url, incident_type="CLAIM")
    except Exception as e:
        w5h1 = {
            "who": who, "what": selected_text[:80], "when": ts_str,
            "where": url[:80], "why": "クレーム", "how": "クレーム！ボタン押下"
        }

    eid = f"CLAIM_{ts_f}_{who[:4].upper()}"
    h   = _hs.sha256(f"{eid}{ts_str}{selected_text[:50]}".encode()).hexdigest()[:16]

    db_helper.write_event({
        "event_id": eid, "when": ts_str,
        "who_actor": w5h1.get("who", who),
        "what_type": "CLAIM",
        "where_component": w5h1.get("where", url[:80]),
        "where_path": "chrome_extension",
        "why_purpose": w5h1.get("why", "クレーム"),
        "how_trigger": "クレーム！ボタン",
        "channel_type": "external",
        "lifecycle_phase": "in_operation",
        "risk_level": "high",
        "category_ab": "B",
        "target_class": "incident",
        "title": selected_text[:100],
        "short_summary": w5h1.get("what", selected_text[:50]),
        "before_state": "issue_detected",
        "after_state": "recorded",
        "change_type": "incident",
        "impact_scope": "ai_behavior",
        "impact_result": "claim_recorded",
        "related_event_id": "N/A", "trace_id": "N/A",
        "free_note": f"hash={h}|who={who}",
    })

    # prevention_queueに即登録
    try:
        pq_path = os.path.join(ROOT_DIR, 'data', 'prevention_queue.json')
        pq = json.load(open(pq_path, encoding='utf-8')) if os.path.exists(pq_path) else []
        pq.append({
            "id": eid,
            "timestamp": ts_str,
            "type": "CLAIM",
            "pattern": selected_text[:50],
            "who": who,
            "proposal": [
                f"【即時対応】「{selected_text[:40]}」を確認・修正",
                f"【再発防止】同パターンをdanger_patternsに登録",
                f"【制度化】essenceのINCIDENT軸に記録し次回セッションから反映"
            ],
            "status": "pending",
            "risk_level": "high"
        })
        json.dump(pq, open(pq_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CLAIM] prevention_queue error: {e}")

    threading.Thread(target=run_pattern_score, args=(selected_text,), daemon=True).start()

    return jsonify({
        "status": "ok",
        "event_id": eid,
        "w5h1": w5h1
    })
@app.route("/collect", methods=["POST"])
def collect():
    import re as _re, csv as _csv, hashlib as _hs, json as _json
    from datetime import datetime, timezone
    from pathlib import Path as P
    d       = request.get_json()
    source  = d.get("source","unknown")
    text    = d.get("text","")
    url     = d.get("url","")
    mode    = d.get("mode","full")
    text    = _re.sub(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}","[EMAIL]",text)
    text    = _re.sub(r"sk-[A-Za-z0-9]{20,}","[APIKEY]",text)
    text    = _re.sub(r"(?i)password\s*[:=]\s*\S+","password=[MASKED]",text)
    if not text: return jsonify({"status":"empty"}),400
    INFIELD = P(r"C:/Users/sirok/MoCKA/data/storage/infield/RAW")
    INFIELD.mkdir(parents=True,exist_ok=True)
    ts      = datetime.now(timezone.utc)
    ts_str  = ts.strftime("%Y-%m-%dT%H:%M:%S")
    ts_f    = ts.strftime("%Y%m%d_%H%M%S")
    # prev_hash: CSV廃止 → SQLite最終イベントから取得
    last_rows = db_helper.read_events(limit=1)
    if last_rows:
        prev_str = f"{last_rows[-1].get('event_id','')}{last_rows[-1].get('when','')}"
        prev = _hs.sha256(prev_str.encode()).hexdigest()[:16]
    else:
        prev = "GENESIS"
    eid     = f"ECOL_{ts_f}_{source[:4].upper()}"
    h       = _hs.sha256(f"{eid}{ts_str}{text[:100]}{prev}".encode()).hexdigest()[:16]
    rec     = {"event_id":eid,"source":source,"layer":"RAW","url":url,"mode":mode,
               "text":text,"timestamp":ts_str,"hash":h,"prev_hash":prev,"status":"RAW"}
    fname = INFIELD/f"{ts_f}_{eid}.json"
    _json.dump(rec,open(fname,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    PILS = P(r"C:/Users/sirok/MoCKA/data/storage/outbox/PILS")
    PILS.mkdir(parents=True,exist_ok=True)
    shutil.copy2(fname, PILS/fname.name)
    # CSV書き込み廃止 → SQLite(db_helper)に記録
    db_helper.write_event({
        "event_id": eid, "when": ts_str, "who_actor": source,
        "what_type": "collect", "where_component": "chat_import",
        "where_path": "mocka_bridge_v2", "why_purpose": url[:80],
        "how_trigger": "extension", "channel_type": "external",
        "lifecycle_phase": "in_operation", "risk_level": "normal",
        "category_ab": "A", "target_class": "infield/RAW",
        "title": text[:100], "short_summary": prev,
        "before_state": "ingest_complete", "after_state": "RAW",
        "change_type": "local", "impact_scope": "chat_pipeline",
        "impact_result": "N/A", "related_event_id": "N/A", "trace_id": "N/A",
        "free_note": f"hash={h}|source={source}|mode={mode}",
    })
    try:
        _pl = os.path.join(ROOT_DIR, 'mocka_pipeline.py')
        subprocess.Popen([sys.executable, _pl, '--text', text[:500], '--no-ping'], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    except Exception as _e:
        print('[COLLECT] pipeline error: ' + str(_e))
    # Pattern scoring
    threading.Thread(target=run_pattern_score, args=(text[:500],), daemon=True).start()
    return jsonify({"status":"ok","event_id":eid,"hash":h})

# ===== Success Pattern API =====
SUCCESS_PATTERNS_FILE = os.path.join(DATA_DIR, "success_patterns.json")

def load_success_patterns():
    if not os.path.exists(SUCCESS_PATTERNS_FILE):
        return {"hint": [], "great": []}
    with open(SUCCESS_PATTERNS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_success_patterns(patterns):
    with open(SUCCESS_PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

@app.route("/success", methods=["POST"])
def success():
    payload = request.get_json(force=True, silent=True) or {}
    success_type = payload.get("type", "hint")
    text   = payload.get("text", "").strip()
    source = payload.get("source", "unknown")
    url    = payload.get("url", "")
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    patterns = load_success_patterns()
    entry = {"text": text, "source": source, "url": url, "timestamp": datetime.now().isoformat(timespec="seconds")}
    patterns.setdefault(success_type, []).append(entry)
    save_success_patterns(patterns)
    what_type = "success_hint" if success_type == "hint" else "success_great"
    label     = "[hint]" if success_type == "hint" else "[great]"
    append_event({
        "what_type": what_type,
        "category_ab": "A",
        "target_class": "infield",
        "title": f"{label} {text[:40]}",
        "short_summary": text[:200],
        "who_actor": "human_nsjsiro",
        "where_component": "chrome_extension",
        "where_path": "mocka-extension/background.js",
        "why_purpose": f"成功シグナル収集: {success_type}",
        "how_trigger": "context_menu_click",
        "channel_type": "browser_extension",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "impact_scope": "local",
        "free_note": f"source={source}|type={success_type}",
    })
    try:
        _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
        subprocess.Popen([sys.executable, _pl, "--text", f"{label} {text[:500]}", "--no-ping"], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    except Exception as e:
        print(f"[SUCCESS] pipeline error: {e}")
    # Pattern scoring
    threading.Thread(target=run_pattern_score, args=(text,), daemon=True).start()
    print(f"[SUCCESS] {what_type}: {text[:50]}")
    return jsonify({"status": "ok", "type": success_type, "stored": len(patterns.get(success_type, []))})

@app.route("/success/patterns")
def success_patterns():
    patterns = load_success_patterns()
    return jsonify({
        "hint_count":  len(patterns.get("hint", [])),
        "great_count": len(patterns.get("great", [])),
        "hints":  patterns.get("hint", [])[-10:],
        "greats": patterns.get("great", [])[-10:],
    })

@app.route("/pattern/score")
def pattern_score():
    if not os.path.exists(PATTERN_SCORE):
        return jsonify({"status": "NO_DATA"})
    try:
        with open(PATTERN_SCORE, encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/caliber/queue")
def caliber_queue():
    import json as _json
    from datetime import datetime
    layers = ["RAW","REDUCED","RE_REDUCED","REDUCING","CORE","ESSENCE","RAW_DONE"]
    counts = {layer: count_layer(layer) for layer in layers}
    outbox = os.path.join(DATA_DIR, "storage", "outbox", "PILS")
    pils_files = []
    if os.path.exists(outbox):
        for f in sorted(os.listdir(outbox)):
            if f.endswith(".json"):
                fpath = os.path.join(outbox, f)
                size = os.path.getsize(fpath)
                pils_files.append({"name": f, "size": size})
    re_reduced_dir = os.path.join(DATA_DIR, "storage", "infield", "RE_REDUCED")
    recent_results = []
    if os.path.exists(re_reduced_dir):
        files = sorted(os.listdir(re_reduced_dir), reverse=True)[:5]
        for f in files:
            try:
                d = _json.load(open(os.path.join(re_reduced_dir, f), encoding="utf-8-sig"))
                recent_results.append({"file": f, "source": d.get("source",""), "restore_rate": d.get("restore_rate", 0), "timestamp": d.get("timestamp",""), "status": d.get("status",""), "preview": d.get("extraction","")[:100]})
            except: pass
    try:
        r = __import__('requests').get("http://localhost:5679/health", timeout=2)
        server = "online"
    except:
        server = "offline"
    return __import__('flask').jsonify({"layers": counts, "caliber_server": server, "queue": pils_files, "recent_results": recent_results, "timestamp": datetime.now().strftime("%H:%M:%S")})

@app.route("/servers/status")
def servers_status():
    result = {}
    for name, port in [("caliber", 5679), ("mcp", 5002), ("runtime_b", 5003)]:
        try:
            r = requests.get(f"http://localhost:{port}/health", timeout=2)
            d = r.json()
            d["status"] = "online"
            result[name] = d
        except:
            result[name] = {"status": "offline", "port": port}
    return jsonify(result)


# ===== Morphology Engine Status =====
@app.route("/morpho/status")
def morpho_status():
    import glob
    try:
        morph_path = os.path.join(ROOT_DIR, 'data', 'morpho_score.json')
        morph = json.load(open(morph_path, encoding='utf-8')) if os.path.exists(morph_path) else {}
    except Exception:
        morph = {}
    try:
        import sqlite3
        db_path = os.path.join(ROOT_DIR, 'data', 'morphology_patterns.db')
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT layer, COUNT(*), SUM(count) FROM patterns GROUP BY layer")
        layers = {str(r[0]): {"unique": r[1], "total": r[2]} for r in cur.fetchall()}
        cur.execute("SELECT COUNT(*) FROM predictions")
        pred_count = cur.fetchone()[0]
        cur.execute("SELECT prediction, danger_score, text, created_at FROM predictions ORDER BY rowid DESC LIMIT 5")
        recent = [{"prediction": r[0], "score": r[1], "text": r[2][:50], "at": r[3]} for r in cur.fetchall()]
        con.close()
    except Exception as e:
        layers = {}
        pred_count = 0
        recent = []
    return jsonify({
        "latest": morph,
        "patterns": layers,
        "prediction_count": pred_count,
        "recent_predictions": recent
    })

# ===== Heinrich Status =====
@app.route("/heinrich/status")
def heinrich_status():
    cached = _cc_get('heinrich')
    if cached: return jsonify(cached)
    try:
        import importlib.util as _ilu_h
        _spec_h = _ilu_h.spec_from_file_location('heinrich_engine', os.path.join(ROOT_DIR,'interface','heinrich_engine.py'))
        _he = _ilu_h.module_from_spec(_spec_h)
        _spec_h.loader.exec_module(_he)
        report = _he.run()
        _cc_set('heinrich', report)
        return jsonify(report)
    except Exception as e:
        try:
            h_path = os.path.join(ROOT_DIR, 'data', 'heinrich_report.json')
            report = json.load(open(h_path, encoding='utf-8'))
            return jsonify(report)
        except Exception:
            return jsonify({"error": str(e)})


# ================================================================
# COMMAND CENTER v5.0 - 新規エンドポイント群
# ================================================================


# ── COMMAND CENTER キャッシュ ──
_cc_cache = {}
_CC_TTL = {
    'heinrich': 60,
    'trend':    300,
    'todo_risk': 60,
    'agent':    120,
}
def _cc_get(key):
    import time
    if key in _cc_cache:
        data, ts = _cc_cache[key]
        if time.time() - ts < _CC_TTL.get(key, 60):
            return data
    return None
def _cc_set(key, data):
    import time
    _cc_cache[key] = (data, time.time())

# --- Global Risk Meter ---
@app.route("/risk/global")
def risk_global():
    import sqlite3 as _sq, datetime as _dt
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); cur = con.cursor()
        # 直近24h のDANGER/CRITICAL/MATAKA件数
        since = (_dt.datetime.now() - _dt.timedelta(hours=24)).isoformat()
        cur.execute("SELECT COUNT(*) FROM events WHERE what_type IN ('MATAKA','CLAIM','CRITICAL','DANGER','ai_violation') AND when_ts >= ?", (since,))
        incidents_24h = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM events WHERE what_type='MATAKA'")
        mataka_total = cur.fetchone()[0] or 0
        con.close()
        # morpho score
        morph_path = os.path.join(ROOT_DIR, 'data', 'morpho_score.json')
        morph_score = 0.0
        if os.path.exists(morph_path):
            try: morph_score = json.load(open(morph_path,encoding='utf-8')).get('danger_score',0.0)
            except: pass
        # prevention queue
        pq_path = os.path.join(ROOT_DIR, 'data', 'prevention_queue.json')
        pq_pending = 0
        if os.path.exists(pq_path):
            try: pq_pending = len([x for x in json.load(open(pq_path,encoding='utf-8')) if x.get('status')=='pending'])
            except: pass
        # スコア計算 (0-100)
        score = min(100, int(
            incidents_24h * 15 +
            morph_score   * 40 +
            pq_pending    *  5 +
            (mataka_total // 5) * 3
        ))
        if   score >= 70: level = 'CRITICAL'
        elif score >= 40: level = 'DANGER'
        elif score >= 20: level = 'WARNING'
        else:             level = 'SAFE'
        # SYSTEM RECOMMENDATION
        rec = ''
        if pq_pending > 0:   rec = f'prevention_queueに{pq_pending}件の承認待ち案件があります。いいね！で承認してください。'
        elif incidents_24h > 0: rec = f'直近24hに{incidents_24h}件のインシデントが発生。essenceを確認してください。'
        elif mataka_total > 0:  rec = f'またか！が{mataka_total}件蓄積。morphologyパターンが強化されています。'
        else:                    rec = '現在は安全な状態です。通常運用を継続してください。'
        return jsonify({
            'score': score, 'level': level,
            'incidents_24h': incidents_24h,
            'mataka_total': mataka_total,
            'morph_score': morph_score,
            'pq_pending': pq_pending,
            'recommendation': rec,
            'timestamp': _dt.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'score':0,'level':'SAFE','error':str(e)})

# --- Temporal Analytics (7日トレンド) ---
@app.route("/trend/weekly")
def trend_weekly():
    cached = _cc_get('trend')
    if cached: return jsonify(cached)
    import sqlite3 as _sq, datetime as _dt
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); cur = con.cursor()
        days = []
        for i in range(6, -1, -1):
            d = _dt.datetime.now() - _dt.timedelta(days=i)
            ds = d.strftime('%Y-%m-%d')
            de = ds + 'T23:59:59'
            ds2 = ds + 'T00:00:00'
            cur.execute("SELECT COUNT(*) FROM events WHERE when_ts BETWEEN ? AND ?", (ds2, de))
            total = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM events WHERE what_type IN ('MATAKA','CLAIM','CRITICAL','ai_violation') AND when_ts BETWEEN ? AND ?", (ds2, de))
            l1 = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM events WHERE what_type IN ('DANGER','ERROR','INCIDENT') AND when_ts BETWEEN ? AND ?", (ds2, de))
            l2 = cur.fetchone()[0] or 0
            days.append({'date': ds, 'label': d.strftime('%m/%d'), 'total': total, 'l1': l1, 'l2': l2, 'l3': max(0, total-l1-l2)})
        con.close()
        # トレンド判定
        recent3 = sum(d['l1']+d['l2'] for d in days[-3:])
        prev3   = sum(d['l1']+d['l2'] for d in days[:3])
        trend = 'up' if recent3 > prev3 * 1.2 else 'down' if recent3 < prev3 * 0.8 else 'flat'
        result = {'days': days, 'trend': trend, 'recent3': recent3, 'prev3': prev3}
        _cc_set('trend', result)
        return jsonify(result)
    except Exception as e:
        return jsonify({'days':[],'trend':'flat','error':str(e)})

# --- Decision Log (判断理由) ---
@app.route("/decision/log")
def decision_log():
    import sqlite3 as _sq
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); con.row_factory = _sq.Row
        cur = con.cursor()
        cur.execute("SELECT event_id,when_ts,what_type,title,why_purpose,how_trigger,free_note FROM events WHERE what_type IN ('DECISION_APPROVED','DECISION_REJECTED','AUTO_GATE_APPROVED','AUDIT_COMPLETE') ORDER BY rowid DESC LIMIT 10")
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return jsonify({'decisions': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'decisions':[],'error':str(e)})

# --- TODO Risk Score ---
@app.route("/todo/risk")
def todo_risk():
    cached = _cc_get('todo_risk')
    if cached: return jsonify(cached)
    import importlib.util as _ilu, datetime as _dt
    try:
        todo_path = os.path.join(os.path.dirname(ROOT_DIR), 'MOCKA_TODO.json')
        if not os.path.exists(todo_path):
            todo_path = r'C:\Users\sirok\MOCKA_TODO.json'
        todos = json.load(open(todo_path, encoding='utf-8')).get('todos', [])
        # morphology engineでリスク評価
        _spec = _ilu.spec_from_file_location('me_risk', os.path.join(ROOT_DIR,'interface','morphology_engine.py'))
        _me = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_me)
        scored = []
        for t in todos:
            if t.get('status') == '完了': continue
            text = (t.get('title','') + ' ' + t.get('description','')).strip()
            try:
                r = _me.predict(text, threshold=0.2)
                risk = r['danger_score']
            except:
                risk = 0.0
            # 締切チェック
            overdue = False
            note = t.get('note','')
            if '5/14' in note or '5/21' in note:
                overdue = True
                risk = min(1.0, risk + 0.3)
            scored.append({
                'id': t.get('id',''),
                'title': t.get('title','')[:60],
                'priority': t.get('priority','中'),
                'risk_score': round(risk, 3),
                'risk_level': 'CRITICAL' if risk>=0.6 else 'HIGH' if risk>=0.4 else 'MEDIUM' if risk>=0.2 else 'LOW',
                'overdue': overdue,
                'status': t.get('status','')
            })
        scored.sort(key=lambda x: -x['risk_score'])
        return jsonify({'todos': scored[:10], 'top': scored[0] if scored else None})
    except Exception as e:
        return jsonify({'todos':[],'error':str(e)})

# --- Data Integrity Monitor ---
@app.route("/integrity/status")
def integrity_status():
    import sqlite3 as _sq, datetime as _dt
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        # 読み取りテスト
        con = _sq.connect(db); cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM events"); total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events WHERE event_id IS NULL OR when_ts IS NULL"); nulls = cur.fetchone()[0]
        cur.execute("SELECT MIN(when_ts), MAX(when_ts) FROM events"); span = cur.fetchone()
        con.close()
        health_pct = round((total-nulls)/total*100,1) if total>0 else 0
        # seal hash確認
        seal_path = os.path.join(ROOT_DIR, 'governance', 'anchor_record.json')
        last_seal = {}
        if os.path.exists(seal_path):
            try: last_seal = json.load(open(seal_path,encoding='utf-8'))
            except: pass
        # 締切超過TODOチェック
        overdue_todos = []
        try:
            todo_path = r'C:\Users\sirok\MOCKA_TODO.json'
            todos = json.load(open(todo_path,encoding='utf-8')).get('todos',[])
            for t in todos:
                if t.get('status') == '完了': continue
                note = t.get('note','')
                if '5/14' in note or '5/21' in note:
                    overdue_todos.append({'id':t['id'],'title':t.get('title','')[:50]})
        except: pass
        return jsonify({
            'total_events': total,
            'null_fields': nulls,
            'health_pct': health_pct,
            'oldest_event': span[0] if span else None,
            'newest_event': span[1] if span else None,
            'last_seal': last_seal,
            'overdue_todos': overdue_todos,
            'db_size_kb': round(os.path.getsize(db)/1024,1) if os.path.exists(db) else 0
        })
    except Exception as e:
        return jsonify({'error':str(e),'health_pct':0})

# --- Agent Allocation ---
@app.route("/agent/allocation")
def agent_allocation():
    cached = _cc_get('agent')
    if cached: return jsonify(cached)
    import sqlite3 as _sq, datetime as _dt
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); cur = con.cursor()
        since = (_dt.datetime.now() - _dt.timedelta(days=7)).isoformat()
        cur.execute("SELECT who_actor, COUNT(*) as cnt FROM events WHERE when_ts >= ? GROUP BY who_actor ORDER BY cnt DESC LIMIT 10", (since,))
        alloc = [{'agent': r[0] or 'unknown', 'count': r[1]} for r in cur.fetchall()]
        total = sum(a['count'] for a in alloc)
        for a in alloc:
            a['pct'] = round(a['count']/total*100,1) if total>0 else 0
        con.close()
        return jsonify({'allocation': alloc, 'total': total, 'period_days': 7})
    except Exception as e:
        return jsonify({'allocation':[],'error':str(e)})

# --- Seal History ---
@app.route("/seal/history")
def seal_history():
    try:
        seal_path = os.path.join(ROOT_DIR, 'governance', 'anchor_record.json')
        if os.path.exists(seal_path):
            data = json.load(open(seal_path, encoding='utf-8'))
            return jsonify({'history': data if isinstance(data,list) else [data], 'count': 1})
        return jsonify({'history':[],'count':0})
    except Exception as e:
        return jsonify({'history':[],'error':str(e)})

@app.route("/loop/status")
def loop_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH  = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    INJECT_FLAG   = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    PING_PATH     = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    RAW_DIR       = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW")
    RAW_DONE_DIR  = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW_DONE")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    essence_count = 0
    essence_axes  = {"INCIDENT": False, "PHILOSOPHY": False, "OPERATION": False}
    essence_updated = None
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8-sig"))
            for axis in essence_axes:
                if data.get(axis) and str(data[axis]).strip():
                    essence_axes[axis] = True
            essence_count = sum(essence_axes.values())
            dates = [data.get(f"{k}_updated") for k in essence_axes if data.get(f"{k}_updated")]
            if dates:
                essence_updated = max(dates)
        except: pass
    raw_count      = len(list(RAW_DIR.glob("*.json")))      if RAW_DIR.exists()      else 0
    raw_done_count = len(list(RAW_DONE_DIR.glob("*.json"))) if RAW_DONE_DIR.exists() else 0
    ping_data = {}
    ping_age  = None
    if PING_PATH.exists():
        try:
            text = PING_PATH.read_text(encoding="utf-8-sig")
            ping_data = json.loads(text)
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass
    # --- 8ステージ実データ収集 ---
    RECURRENCE_CSV = Path(r"C:\Users\sirok\MoCKA\data\recurrence_registry.csv")
    PREVENTION_JSON = Path(r"C:\Users\sirok\MoCKA\data\prevention_queue.json")
    LEDGER_JSON  = Path(r"C:\Users\sirok\MoCKA\runtime\main\ledger.json")

    # ② Record: events.db総件数（CSV廃止済み → SQLite参照）
    record_count = 0
    incident_count = 0
    decision_count = 0
    action_count = 0
    try:
        rows = db_helper.read_events(limit=None)
        record_count = len(rows)
        for r in rows:
            wt    = str(r.get("what_type","")).upper()
            rl    = str(r.get("risk_level","")).upper()
            title = str(r.get("title","")).upper()
            if rl in ["DANGER","CRITICAL"] or "INCIDENT" in wt or "INCIDENT" in title:
                incident_count += 1
            if "DECISION_APPROVED" in wt or "DECISION_APPROVED" in title:
                decision_count += 1
            if "AUTO_GATE_APPROVED" in wt or "AUTO_GATE" in title:
                action_count += 1
    except Exception as _e:
        print(f"[loop/status] db read error: {_e}")

    # ④ Recurrence件数（recurrence_registry.csv は継続利用）
    recurrence_count = 0
    if RECURRENCE_CSV.exists():
        try:
            import csv as _csv
            with open(RECURRENCE_CSV, encoding="utf-8", errors="replace") as f:
                recurrence_count = sum(1 for _ in _csv.DictReader(f))
        except: pass

    # ⑤ Prevention未承認件数
    prevention_pending = 0
    if PREVENTION_JSON.exists():
        try:
            pdata = json.loads(PREVENTION_JSON.read_text(encoding="utf-8-sig"))
            items = pdata if isinstance(pdata, list) else pdata.get("queue", [])
            prevention_pending = sum(1 for x in items if str(x.get("status","")).upper() not in ["APPROVED","REJECTED"])
        except: pass

    # ⑧ Audit: 最終seal時刻
    last_seal = None
    last_seal_hash = None
    if LEDGER_JSON.exists():
        try:
            ldata = json.loads(LEDGER_JSON.read_text(encoding="utf-8-sig"))
            if isinstance(ldata, list) and ldata:
                last_entry = ldata[-1]
                last_seal = str(last_entry.get("timestamp", ""))
                last_seal_hash = last_entry.get("event_hash", "")[:16]
            elif isinstance(ldata, dict):
                last_seal = ldata.get("last_updated") or ldata.get("timestamp")
                last_seal_hash = ldata.get("hash") or ldata.get("anchor_hash")
        except: pass

    civilization_loop = {
        "observe":    {"label": "Observe",    "count": raw_count,          "detail": "RAW未処理"},
        "record":     {"label": "Record",     "count": record_count,       "detail": "mocka_events.db総件数"},
        "incident":   {"label": "Incident",   "count": incident_count,     "detail": "DANGER/CRITICAL/INCIDENT"},
        "recurrence": {"label": "Recurrence", "count": recurrence_count,   "detail": "再発パターン"},
        "prevention": {"label": "Prevention", "count": prevention_pending,  "detail": "未承認Prevention案"},
        "decision":   {"label": "Decision",   "count": decision_count,     "detail": "承認済みDecision"},
        "action":     {"label": "Action",     "count": action_count,       "detail": "Auto Gate実行"},
        "audit":      {"label": "Audit",      "last_seal": last_seal,      "last_seal_hash": last_seal_hash},
    }

    return jsonify({"inject_mode": inject_mode, "essence_count": essence_count, "essence_axes": essence_axes,
                    "essence_updated": essence_updated, "raw_count": raw_count, "raw_done_count": raw_done_count,
                    "ping_latest": ping_data, "ping_age": ping_age,
                    "civilization_loop": civilization_loop})

@app.route("/loop/inject_toggle", methods=["POST"])
def inject_toggle():
    from pathlib import Path
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    current = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        current = v if v in ["ON","OFF"] else "ON"
    new_mode = "OFF" if current == "ON" else "ON"
    INJECT_FLAG.write_text(new_mode, encoding="utf-8-sig")
    return jsonify({"inject_mode": new_mode})

@app.route("/get_latest_dna")
def get_latest_dna():
    from pathlib import Path
    PING_PATH   = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    TODO_PATH   = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8-sig").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"
    if inject_mode == "OFF":
        return jsonify({"status": "OFF"}), 200
    if not PING_PATH.exists():
        return jsonify({"status": "NO_PING"}), 404
    todo_summary = []
    try:
        todo_data = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
        priority_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
        pending = [t for t in todo_data.get("todos", []) if t.get("status") == "未着手"]
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 9))
        todo_summary = [{"id": t.get("id"), "title": t.get("title"), "priority": t.get("priority")} for t in pending[:5]]
    except: todo_summary = []
    try:
        ping = json.loads(PING_PATH.read_text(encoding="utf-8-sig"))
        return jsonify({"status": "OK", "ping": ping, "todo_summary": todo_summary}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route("/gemini/briefing")
def gemini_briefing():
    from pathlib import Path
    TODO_PATH    = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    todos_pending = []
    try:
        todo_data = json.loads(TODO_PATH.read_text(encoding="utf-8-sig"))
        priority_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
        pending = [t for t in todo_data.get("todos", []) if t.get("status") == "未着手"]
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 9))
        todos_pending = [{"id": t.get("id"), "title": t.get("title"), "priority": t.get("priority")} for t in pending]
    except: pass
    essence = {}
    try:
        essence = json.loads(ESSENCE_PATH.read_text(encoding="utf-8-sig"))
    except: pass
    top = todos_pending[0] if todos_pending else {}
    header = f"[MoCKA SESSION START]\nPhase 2進行中\n未着手TODO: {len(todos_pending)}件\n最重要: {top.get('id','')} {top.get('title','')}"
    return jsonify({"status": "OK", "prompt_header": header, "todos_pending": todos_pending, "essence": essence}), 200

@app.route("/report", methods=["POST"])
def receive_report():
    from pathlib import Path
    REPORT_DIR = Path(r"C:\Users\sirok\MoCKA\data\reports")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        data = request.get_json(force=True)
        data["received_at"] = datetime.now().isoformat()
        fname = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        (REPORT_DIR / fname).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"status": "OK", "saved": fname}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/ngrok/status')
def ngrok_status():
    import requests as req
    try:
        r = req.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        d = r.json()
        t = d['tunnels'][0] if d.get('tunnels') else None
        return json.dumps({'status': 'online' if t else 'offline', 'public_url': t['public_url'] if t else '', 'addr': t['config']['addr'] if t else ''}), 200, {'Content-Type': 'application/json'}
    except:
        return json.dumps({'status': 'offline', 'public_url': '', 'addr': ''}), 200, {'Content-Type': 'application/json'}

@app.route("/pipeline/status")
def pipeline_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH  = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    PATTERNS_FILE = Path(r"C:\Users\sirok\MoCKA\interface\danger_patterns.json")
    LEARN_LOG     = Path(r"C:\Users\sirok\MoCKA\data\language_learn_log.json")
    PING_PATH     = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")
    WATCHDOG_LOG  = Path(r"C:\Users\sirok\MoCKA\data\watchdog_processed.json")
    result = {}
    input_info = {"chrome_extension":{"last":None},"watchdog":{"running":False},"pipeline":{"last":None}}
    if WATCHDOG_LOG.exists():
        try:
            wd = json.loads(WATCHDOG_LOG.read_text(encoding="utf-8"))
            input_info["watchdog"]["running"] = True
            input_info["watchdog"]["processed_count"] = len(wd)
        except: pass
    if PING_PATH.exists():
        try:
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            input_info["pipeline"]["last"] = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass
    result["input"] = input_info
    layers = {}
    base = Path(r"C:\Users\sirok\MoCKA\data\storage")
    for layer in ["RAW","REDUCED","RE_REDUCED","REDUCING","CORE","ESSENCE","RAW_DONE"]:
        d = base / "infield" / layer
        layers[layer] = len(list(d.glob("*.json"))) if d.exists() else 0
    pils = base / "outbox" / "PILS"
    layers["PILS"] = len(list(pils.glob("*.json"))) if pils.exists() else 0
    result["layers"] = layers
    danger_info = {"total":0,"tier1":0,"tier2":0,"tier3":0,"escalation":0,"silent_danger":0,"learned_today":0,"last_critical":None}
    if PATTERNS_FILE.exists():
        try:
            p = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
            for tier in ["tier1","tier2","tier3","escalation","silent_danger"]:
                n = len(p.get(tier,{}).get("patterns",[]))
                danger_info[tier] = n
                danger_info["total"] += n
        except: pass
    if LEARN_LOG.exists():
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            learned = 0; last_critical = None
            with open(LEARN_LOG, encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp","").startswith(today):
                            learned += entry.get("added_count", 0)
                        if entry.get("level") in ("CRITICAL","DANGER"):
                            last_critical = entry.get("incident_id")
                    except: pass
            danger_info["learned_today"] = learned
            danger_info["last_critical"] = last_critical
        except: pass
    result["danger"] = danger_info
    essence_detail = {}
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
            for axis in ["INCIDENT","PHILOSOPHY","OPERATION"]:
                text = data.get(axis,"")
                essence_detail[axis] = {"text":text[:120] if text else "","updated":data.get(f"{axis}_updated",""),"count":data.get(f"{axis}_source_count",0),"filled":bool(text and text.strip())}
        except: pass
    result["essence"] = essence_detail
    return jsonify(result)

@app.route("/essence/detail")
def essence_detail():
    from pathlib import Path
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    if not ESSENCE_PATH.exists():
        return jsonify({"status":"NOT_FOUND"})
    try:
        return jsonify({"status":"OK","data":json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))})
    except Exception as e:
        return jsonify({"status":"ERROR","message":str(e)})

@app.route("/danger/status")
def danger_status():
    from pathlib import Path
    PATTERNS_FILE = Path(r"C:\Users\sirok\MoCKA\interface\danger_patterns.json")
    if not PATTERNS_FILE.exists():
        return jsonify({"status":"NOT_FOUND"})
    try:
        p = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
        summary = {}
        for tier in ["tier1","tier2","tier3","escalation","silent_danger"]:
            patterns = p.get(tier,{}).get("patterns",[])
            summary[tier] = {"count":len(patterns),"samples":patterns[:3]}
        return jsonify({"status":"OK","summary":summary,"meta":p.get("_meta",{})})
    except Exception as e:
        return jsonify({"status":"ERROR","message":str(e)})

@app.route("/public/todo")
def public_todo():
    from pathlib import Path
    TODO_PATH = Path(r"C:\Users\sirok\MOCKA_TODO.json")
    if not TODO_PATH.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(TODO_PATH.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/overview")
def public_overview():
    from pathlib import Path
    OV_PATH = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")
    if not OV_PATH.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(OV_PATH.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/essence")
def public_essence():
    from pathlib import Path
    EP = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    if not EP.exists():
        return jsonify({"status": "NOT_FOUND"})
    try:
        return jsonify(json.loads(EP.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/events")
def public_events():
    n = int(request.args.get("n", 20))
    try:
        rows = db_helper.read_events(limit=None)
        clean = []
        for r in rows:
            row = {k: (v if v is not None else "") for k, v in r.items()}
            if row.get("_source") == "csv_migration" and not row.get("title") and not row.get("when_ts"):
                continue
            clean.append(row)
        return jsonify({"count": len(clean), "events": clean[-n:], "source": "sqlite"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})
@app.route("/public/write_event", methods=["POST"])
def public_write_event():
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title", "")
    description = payload.get("description", "")
    author = payload.get("author", "external_ai")
    tags = payload.get("tags", "")
    if not title or not description:
        return jsonify({"status": "error", "message": "title and description required"}), 400
    meta = {
        "what_type": "ai_event", "category_ab": "A", "target_class": "infield",
        "title": title, "short_summary": description[:200], "who_actor": author,
        "where_component": "public_api", "where_path": "/public/write_event",
        "why_purpose": tags, "how_trigger": "external_ai_call",
        "channel_type": "http_api", "lifecycle_phase": "in_operation",
        "risk_level": "normal", "before_state": "N/A", "after_state": "N/A",
        "change_type": "N/A", "impact_scope": "local", "impact_result": "N/A",
        "related_event_id": "N/A", "trace_id": "N/A", "free_note": description,
    }
    append_event(meta)
    return jsonify({"status": "ok", "event_id": next_event_id()})

@app.route("/public/pipeline", methods=["POST"])
def public_pipeline():
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text", "").strip()
    author = payload.get("author", "external_ai")
    if not text:
        return jsonify({"status": "error", "message": "text required"}), 400
    try:
        _pl = os.path.join(ROOT_DIR, "mocka_pipeline.py")
        subprocess.Popen([sys.executable, _pl, "--text", text[:1000], "--no-ping"], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        return jsonify({"status": "ok", "message": "pipeline started", "author": author})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/public/seal", methods=["POST"])
def public_seal():
    # CSV廃止済み → SQLiteのeventsテーブル全件ハッシュ
    import hashlib, json as _j
    try:
        rows = db_helper.read_events(limit=None)
        payload = _j.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
        h = hashlib.sha256(payload).hexdigest()
        return jsonify({"status": "ok", "sha256": h, "source": "sqlite",
                        "event_count": len(rows), "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/public/status")
def public_status():
    result = {
        "system": "MoCKA v3.0",
        "status": "online",
        "services": {
            "todo": "/public/todo", "overview": "/public/overview",
            "essence": "/public/essence", "events": "/public/events?n=20",
            "write_event": "/public/write_event (POST)", "pipeline": "/public/pipeline (POST)",
            "seal": "/public/seal (POST)", "pipeline_status": "/pipeline/status",
            "danger_status": "/danger/status", "essence_detail": "/essence/detail",
            "collaborate": "/collaborate (POST)", "set_intent": "/set_intent (POST)",
            "get_intent": "/get_intent/<ai_name> (GET)",
            "pattern_score": "/pattern/score (GET)",
        },
        "mcp": {"url": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp"},
        "ngrok": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev",
        "appointed_ai": ["Claude","Gemini","GPT","Copilot","Perplexity"],
    }
    return jsonify(result)

@app.route('/pattern/status')
def pattern_status():
    if _pattern_engine is None:
        return jsonify({"status": "unavailable"})
    reg     = _pattern_engine.registry
    recent  = _pattern_score_history[-20:]
    d_count = sum(1 for r in recent if r["verdict"] in ("DANGER","CRITICAL"))
    s_count = sum(1 for r in recent if r["verdict"] == "SUCCESS")
    return jsonify({
        "status":         "ok",
        "total_keywords": len(reg.records),
        "danger_kw":      len(reg.danger_keywords()),
        "success_kw":     len(reg.success_keywords()),
        "recent_count":   len(recent),
        "danger_count":   d_count,
        "success_count":  s_count,
        "last_verdict":   recent[-1]["verdict"] if recent else "NEUTRAL",
        "last_R":         recent[-1]["R"]       if recent else 0.0,
        "history":        recent[-10:],
    })
# ============================================================

# ============================================================
# 全自動LOOP: DANGER検知 → essence直結パイプ
# ============================================================
import threading as _lt, time as _lt2

def _auto_danger_to_essence(incident_text: str):
    """DANGER/CRITICAL検知時にessenceへ直接記録する"""
    try:
        from pathlib import Path as _P
        import json as _j
        essence_path = _P(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
        if not essence_path.exists():
            return
        data = _j.loads(essence_path.read_text(encoding="utf-8"))
        current = data.get("INCIDENT", "")
        data["INCIDENT"] = f"【自動記録】{incident_text[:60]} | {current[:60]}"
        data["INCIDENT_updated"] = datetime.now().isoformat()
        essence_path.write_text(_j.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # ping_generator自動実行
        import subprocess
        ping_gen = __import__("pathlib").Path(str(ROOT_DIR)) / "interface" / "ping_generator.py"
        if ping_gen.exists():
            subprocess.Popen(["python", str(ping_gen)], cwd=str(ROOT_DIR))
        print(f"[AUTO-PIPE] essence更新: {incident_text[:40]}")
    except Exception as e:
        print(f"[AUTO-PIPE] エラー: {e}")

# ============================================================
# 全自動LOOP: Audit（日次seal + 50件トリガー）
# ============================================================
_last_seal_date = [None]
_last_event_count = [0]
_seal_running = [False]


def _auto_approve_prevention():
    """NORMAL/CAUTIONのPrevention案を自動承認（3ヶ月レビュー方針）"""
    import uuid
    from datetime import datetime
    try:
        pq_data = _load_pqueue()
        pq = pq_data if isinstance(pq_data, list) else pq_data.get("queue", [])
        changed = False
        for item in pq:
            if item.get("status") != "pending":
                continue
            severity = item.get("severity", "NORMAL").upper()
            if severity in ("HIGH", "CRITICAL"):
                continue  # Human Gate
            item["status"] = "approved"
            item["approved_at"] = datetime.now().isoformat()
            item["approved_by"] = "AUTO_GATE"
            changed = True
            print(f"[AUTO_APPROVE] {item['id']} {item.get('recurrence_key','')} severity={severity}")
        if changed:
            save_data = {"queue": pq} if isinstance(pq_data, dict) else pq
            PREVENTION_QUEUE_PATH.write_text(
                json.dumps(save_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
    except Exception as e:
        print(f"[AUTO_APPROVE] error: {e}")


def auto_audit_loop():
    import subprocess, time
    _auto_approve_prevention()
    print("[AUTO-AUDIT] 日次自動sealループ開始")
    while True:
        try:
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            if now.hour == 0 and _last_seal_date[0] != today:
                seal_script = __import__("pathlib").Path(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
                if seal_script.exists():
                    subprocess.run(["python", str(seal_script), "AUTO_SEAL_" + today],
                                   cwd=str(ROOT_DIR), timeout=30)
                    print(f"[AUTO-AUDIT] 日次seal完了")
                _last_seal_date[0] = today
            # CSV廃止済み → SQLite件数でトリガー判定
            try:
                count = len(db_helper.read_events(limit=None))
            except Exception:
                count = _last_event_count[0]
            if count - _last_event_count[0] >= 50 and not _seal_running[0]:
                _seal_running[0] = True
                try:
                    seal_script = __import__("pathlib").Path(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
                    if seal_script.exists():
                        subprocess.run(["python", str(seal_script), "AUTO_SEAL_50EVT"],
                                       cwd=str(ROOT_DIR), timeout=30)
                        print(f"[AUTO-AUDIT] 50件seal完了")
                    _last_event_count[0] = count
                finally:
                    _seal_running[0] = False
        except Exception as e:
            print(f"[AUTO-AUDIT] ループ例外: {e}")
        _lt2.sleep(60)

_audit_thread = _lt.Thread(target=auto_audit_loop, daemon=True)
_audit_thread.start()


@app.route("/audit/status")
def audit_status():
    from pathlib import Path as _P
    seal_log = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    log = {}
    if seal_log.exists():
        try:
            log = __import__("json").loads(seal_log.read_text(encoding="utf-8"))
        except: pass
    return jsonify({"last_seal": log, "seal_log_exists": seal_log.exists()})

@app.route("/audit/seal", methods=["POST"])
def audit_seal_manual():
    import subprocess
    from pathlib import Path as _P
    seal_script = _P(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
    seal_log    = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    if seal_script.exists():
        result = subprocess.run(
            ["python", str(seal_script), "MANUAL_SEAL_" + datetime.now().strftime("%Y%m%d_%H%M%S")],
            cwd=str(ROOT_DIR), capture_output=True, text=True, timeout=30
        )
        log = {"sealed_at": datetime.now().isoformat(), "result": result.stdout[:200]}
        seal_log.write_text(__import__("json").dumps(log, ensure_ascii=False), encoding="utf-8")
        return jsonify({"status": "ok", "sealed_at": log["sealed_at"]})
    return jsonify({"status": "error", "message": "seal script not found"})


# ============================================================
# AUTO-CHAIN: append_event後のessence自動トリガー
# ============================================================
import threading as _chain_t

def _trigger_essence_chain(row):
    def _run():
        try:
            from pathlib import Path as _P
            import subprocess as _sp
            risk = row.get("risk_level","normal").lower()
            wtype = row.get("what_type","").lower()
            trigger_types = {"danger","critical","incident","claim","prevention"}
            if risk not in ("danger","critical") and wtype not in trigger_types:
                return
            ec = _P(ROOT_DIR) / "interface" / "essence_classifier.py"
            pg = _P(ROOT_DIR) / "interface" / "ping_generator.py"
            if ec.exists():
                _sp.run(["python", str(ec)], cwd=ROOT_DIR, timeout=30)
            if pg.exists():
                _sp.run(["python", str(pg)], cwd=ROOT_DIR, timeout=30)
            print("[AUTO-CHAIN] essence更新: " + row.get("event_id","?"))
        except Exception as e:
            print("[AUTO-CHAIN] エラー: " + str(e))
    _chain_t.Thread(target=_run, daemon=True).start()

# ============================================================

# PREVENTION QUEUE + DECISION
# ============================================================
from pathlib import Path as _pp
PREVENTION_QUEUE_PATH = _pp(ROOT_DIR) / "data" / "prevention_queue.json"

def _load_pqueue():
    if PREVENTION_QUEUE_PATH.exists():
        try:
            return json.loads(PREVENTION_QUEUE_PATH.read_text(encoding="utf-8"))
        except:
            pass
    return {"queue": []}

def _save_pqueue(data):
    PREVENTION_QUEUE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@app.route("/prevention/generate", methods=["POST"])
def prevention_generate():
    """recurrence_registryから未対応パターンをprevention_queueに自動生成"""
    import csv, uuid
    from datetime import datetime
    from collections import defaultdict

    rec_path = _pp(ROOT_DIR) / "data" / "recurrence_registry.csv"
    if not rec_path.exists():
        return jsonify({"error": "recurrence_registry.csv not found"}), 404

    rows = []
    try:
        with open(rec_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    groups = defaultdict(list)
    for row in rows:
        key = f"{row.get('component','unknown')}::{row.get('what_type','unknown')}"
        groups[key].append(row)

    pq_data = _load_pqueue()
    pq = pq_data if isinstance(pq_data, list) else pq_data.get("queue", [])
    existing_keys = {item.get("recurrence_key","") for item in pq}

    generated = 0
    for key, recs in groups.items():
        if key in existing_keys:
            continue
        count = max(int(r.get("recurrence_count", 1)) for r in recs)
        if count < 2:
            continue
        component, what_type = key.split("::", 1)
        severity = "HIGH" if count >= 5 else "CAUTION" if count >= 3 else "NORMAL"
        entry = {
            "id": f"PQ_{uuid.uuid4().hex[:8].upper()}",
            "recurrence_key": key,
            "component": component,
            "what_type": what_type,
            "recurrence_count": count,
            "severity": severity,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "candidates": [
                f"{component}の{what_type}処理に入力バリデーションを追加する",
                f"{component}の{what_type}処理をユニットテストでカバーする",
                f"{component}の{what_type}処理のログ出力を強化して早期検知できるようにする"
            ],
            "source": "recurrence_registry_auto"
        }
        pq.append(entry)
        generated += 1

    PREVENTION_QUEUE_PATH.write_text(
        json.dumps(pq, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return jsonify({
        "generated": generated,
        "total_pending": sum(1 for x in pq if x.get("status") == "PENDING"),
        "groups_analyzed": len(groups)
    })


@app.route("/prevention/queue")
def prevention_queue():
    data = _load_pqueue()
    pending = [q for q in data.get("queue", []) if q.get("status") == "pending"]
    return jsonify({"queue": data.get("queue", []), "pending_count": len(pending)})

@app.route("/decision/approve", methods=["POST"])
def decision_approve():
    payload = request.get_json(force=True, silent=True) or {}
    pid = payload.get("id", "")
    data = _load_pqueue()
    approved = None
    for item in data["queue"]:
        if item.get("id") == pid and item.get("status") == "pending":
            item["status"] = "approved"
            item["approved_at"] = datetime.now().isoformat()
            approved = item
            break
    if not approved:
        return jsonify({"status": "not_found"}), 404
    _save_pqueue(data)
    append_event({
        "what_type": "DECISION_APPROVED",
        "title": "[承認] " + approved.get("title", ""),
        "short_summary": approved.get("description", "")[:100],
        "risk_level": approved.get("risk_level", "normal"),
        "who_actor": "kimura_hakase",
        "free_note": pid,
    })
    def _upd():
        try:
            from pathlib import Path as _P
            import subprocess as _sp
            pg = _P(ROOT_DIR) / "interface" / "ping_generator.py"
            if pg.exists():
                _sp.run(["python", str(pg)], cwd=ROOT_DIR, timeout=30)
        except Exception as e:
            print("[ACTION] " + str(e))
    _chain_t.Thread(target=_upd, daemon=True).start()
    return jsonify({"status": "ok", "approved": pid})

@app.route("/decision/reject", methods=["POST"])
def decision_reject():
    payload = request.get_json(force=True, silent=True) or {}
    pid = payload.get("id", "")
    data = _load_pqueue()
    for item in data["queue"]:
        if item.get("id") == pid and item.get("status") == "pending":
            item["status"] = "rejected"
            item["rejected_at"] = datetime.now().isoformat()
            break
    _save_pqueue(data)
    append_event({
        "what_type": "DECISION_REJECTED",
        "title": "[却下] " + pid,
        "short_summary": "Human Gateで却下",
        "risk_level": "normal",
        "who_actor": "kimura_hakase",
        "free_note": pid,
    })
    return jsonify({"status": "ok", "rejected": pid})


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'port': 5000})


# ==============================
# NY抽出 → Essence自動反映エンドポイント
# ==============================
@app.route("/ny_extract", methods=["POST"])
def ny_extract():
    import threading
    data   = request.get_json(force=True)
    text   = data.get("text", "")
    source = data.get("source", "unknown")
    if not text:
        return jsonify({"status":"error","message":"no text"}), 400

    lines   = [l.strip() for l in text.split("\n") if len(l.strip()) > 15]
    results = {"great":[], "hint":[], "incident":[]}

    great_kw    = ["思想","哲学","格言","原則","本質","設計","制度","文明","再現","継承","座右","記録","証明"]
    incident_kw = ["失敗","エラー","おかしい","なぜ","動かない","限界","無駄","消費","暴走","誤","壊"]

    for line in lines:
        if any(kw in line for kw in incident_kw):
            what_type = "incident"
            results["incident"].append(line)
        elif any(kw in line for kw in great_kw):
            what_type = "success_great"
            results["great"].append(line)
        else:
            what_type = "success_hint"
            results["hint"].append(line)

        append_event({
            "who_actor": source, "what_type": what_type,
            "where_component": "ny_extract",
            "title": f"[NY/{what_type}] {line[:40]}",
            "short_summary": line, "risk_level": "normal",
            "channel_type": "chrome_extension",
            "lifecycle_phase": "in_operation",
            "free_note": f"ny_extract|source={source}"
        })

        if what_type in ["success_great","success_hint"]:
            try:
                sp_path = Path(BASE_DIR) / "data" / "success_patterns.json"
                sp = json.loads(sp_path.read_text(encoding="utf-8")) if sp_path.exists() else {"great":[],"hint":[]}
                key = "great" if what_type == "success_great" else "hint"
                if line not in sp.get(key,[]):
                    sp.setdefault(key,[]).append(line)
                    sp_path.write_text(json.dumps(sp,ensure_ascii=False,indent=2),encoding="utf-8")
            except: pass

    def run_essence():
        try:
            import subprocess, sys
            subprocess.run([sys.executable,"interface/essence_classifier.py"],cwd=BASE_DIR,timeout=30)
            subprocess.run([sys.executable,"interface/ping_generator.py"],cwd=BASE_DIR,timeout=30)
        except: pass
    threading.Thread(target=run_essence,daemon=True).start()

    return jsonify({
        "status":"ok",
        "great":len(results["great"]),
        "hint":len(results["hint"]),
        "incident":len(results["incident"]),
        "total":len(lines),
        "essence":"processing"
    })

# ── cross_audit エンドポイント ───────────────────────────────────────────────
try:
    from interface.cross_audit import (
        init_audit_db, create_task, submit_result,
        run_discrepancy_check, get_task_report, list_tasks as list_audit_tasks
    )
    init_audit_db()
    print("[app] cross_audit engine loaded")

    @app.route("/cross_audit/task", methods=["POST"])
    def cross_audit_task():
        data = request.json or {}
        task_text = data.get("task", "")
        agents = data.get("agents", None)
        if not task_text:
            return jsonify({"error": "task required"}), 400
        return jsonify(create_task(task_text, agents))

    @app.route("/cross_audit/submit", methods=["POST"])
    def cross_audit_submit():
        data = request.json or {}
        task_id  = data.get("task_id", "")
        agent    = data.get("agent", "")
        response = data.get("response", "")
        score    = float(data.get("score", 0.0))
        if not task_id or not agent:
            return jsonify({"error": "task_id and agent required"}), 400
        return jsonify(submit_result(task_id, agent, response, score))

    @app.route("/cross_audit/check/<task_id>")
    def cross_audit_check(task_id):
        discs = run_discrepancy_check(task_id)
        return jsonify({"task_id": task_id, "discrepancies": discs, "count": len(discs)})

    @app.route("/cross_audit/report/<task_id>")
    def cross_audit_report(task_id):
        return jsonify(get_task_report(task_id))

    @app.route("/cross_audit/list")
    def cross_audit_list():
        return jsonify(list_audit_tasks())

except Exception as _ce:
    print(f"[app] cross_audit load error: {_ce}")
# ─────────────────────────────────────────────────────────────────────────────




@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    import json as _json
    from pathlib import Path as _Path
    try:
        _TODO = _Path("C:/Users/sirok/MOCKA_TODO.json")
        with _TODO.open("r", encoding="utf-8-sig") as _f:
            _data = _json.load(_f)
        _count = len((_data.get("todos") or []) + (_data.get("completed") or []))
        return _json.dumps({"ok": True, "count": _count, "message": "local only"}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return _json.dumps({"ok": False, "error": str(e)}), 500, {"Content-Type": "application/json"}


# TODO_119: 締切超過TODO自動INCIDENT化 + Data Integrity Monitor
# ============================================================
import threading as _threading

def _auto_incident_overdue():
    import sqlite3 as _sq
    OVERDUE_KEYWORDS = ['5/14','5/21','4/30','5/1','5/2','5/3','5/4','5/5']
    try:
        todo_path = r'C:\Users\sirok\MOCKA_TODO.json'
        todos = json.load(open(todo_path, encoding='utf-8')).get('todos', [])
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db)
        cur = con.cursor()
        for t in todos:
            if t.get('status') == '完了':
                continue
            note = t.get('note', '') + t.get('description', '')
            is_overdue = any(kw in note for kw in OVERDUE_KEYWORDS)
            if not is_overdue:
                continue
            tid = t.get('id', '')
            cur.execute("SELECT COUNT(*) FROM events WHERE title LIKE ? AND what_type='OVERDUE_INCIDENT'", (f'%{tid}%',))
            if cur.fetchone()[0] > 0:
                continue
            eid = f"OVD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{tid}"
            cur.execute("""INSERT INTO events
                (event_id,when_ts,what_type,who_actor,title,why_purpose,how_trigger,free_note)
                VALUES (?,?,?,?,?,?,?,?)""",
                (eid, datetime.now().isoformat(), 'OVERDUE_INCIDENT', 'system',
                 f'[締切超過] {tid}: {t.get("title","")[:50]}',
                 '締切超過TODOの自動INCIDENT化',
                 'auto_incident_overdue()',
                 f'priority={t.get("priority","")} status={t.get("status","")}'))
            con.commit()
            print(f'[OVERDUE] INCIDENT化: {tid}')
        con.close()
    except Exception as e:
        print(f'[OVERDUE] error: {e}')

def _start_overdue_loop():
    _auto_incident_overdue()
    t = _threading.Timer(3600, _start_overdue_loop)
    t.daemon = True
    t.start()

_threading.Timer(10, _start_overdue_loop).start()

@app.route('/integrity/monitor')
def integrity_monitor():
    import sqlite3 as _sq
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM events"); total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events WHERE what_type='OVERDUE_INCIDENT'"); overdue_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM error_rows"); error_cnt = cur.fetchone()[0]
        db_size = os.path.getsize(db) // 1024
        con.close()
        return jsonify({'status':'ok','total_events':total,'overdue_incidents':overdue_cnt,'error_rows':error_cnt,'db_size_kb':db_size,'checked_at':datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'status':'error','error':str(e)})

@app.route('/operator/load')
def operator_load():
    import sqlite3 as _sq, datetime as _dt
    try:
        db = os.path.join(ROOT_DIR, 'data', 'mocka_events.db')
        con = _sq.connect(db); cur = con.cursor()
        since1h  = (_dt.datetime.now() - _dt.timedelta(hours=1)).isoformat()
        since24h = (_dt.datetime.now() - _dt.timedelta(hours=24)).isoformat()
        cur.execute("SELECT COUNT(*) FROM events WHERE when_ts >= ?", (since1h,))
        events_1h = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events WHERE when_ts >= ?", (since24h,))
        events_24h = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events WHERE what_type IN ('DANGER','CRITICAL','MATAKA') AND when_ts >= ?", (since24h,))
        alerts_24h = cur.fetchone()[0]
        alert_density = round(alerts_24h / 24, 2)
        cli = min(100, int(alert_density * 20 + events_1h * 0.3))
        con.close()
        reducing = 0
        try:
            cal = requests.get('http://localhost:5679/status', timeout=2).json()
            reducing = cal.get('REDUCING', 0)
        except: pass
        return jsonify({'events_1h':events_1h,'events_24h':events_24h,'alerts_24h':alerts_24h,'alert_density':alert_density,'cognitive_load_index':cli,'reducing_tasks':reducing,'status':'HEAVY' if cli>60 else 'MODERATE' if cli>30 else 'LIGHT'})
    except Exception as e:
        return jsonify({'error':str(e)})



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



# ============================================================
# TODO_118: Risk Engine — TODOリスクスコア + SYSTEM RECOMMENDATION
# ============================================================

def _calc_todo_risk_score(todo):
    """TODOのリスクスコアを算出 (0.0〜1.0)"""
    score = 0.0
    reasons = []

    priority = todo.get("priority", "中")
    category = todo.get("category", "")
    title = todo.get("title", "")
    desc = todo.get("description", "")
    text = title + " " + desc

    # 優先度スコア
    priority_map = {"最高": 0.40, "高": 0.30, "中": 0.15, "低": 0.05}
    p_score = priority_map.get(priority, 0.10)
    score += p_score
    if p_score >= 0.30:
        reasons.append(f"優先度={priority}")

    # カテゴリリスク
    high_risk_categories = ["core_engine", "architecture", "ガバナンス", "制度", "security"]
    for hrc in high_risk_categories:
        if hrc in category:
            score += 0.15
            reasons.append(f"高リスクカテゴリ={category}")
            break

    # キーワードリスク (危険シグナル)
    danger_keywords = [
        ("文字化け", 0.10), ("BOM", 0.10), ("断絶", 0.15), ("廃止", 0.10),
        ("移行", 0.08), ("修正", 0.05), ("バグ", 0.10), ("エラー", 0.08),
        ("未接続", 0.12), ("停止", 0.12), ("失敗", 0.10)
    ]
    for kw, ks in danger_keywords:
        if kw in text:
            score += ks
            reasons.append(f"キーワード={kw}")
            break  # 1件のみカウント

    # 再発リスク (recurrence_registry照合)
    try:
        import sqlite3
        db_path = os.path.join(ROOT_DIR, "data", "mocka_events.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # titleに関連するrecurrenceをチェック
        words = [w for w in title.split() if len(w) >= 3][:3]
        recur_count = 0
        for w in words:
            c.execute("SELECT COUNT(*) FROM events WHERE what_type='recurrence' AND title LIKE ?", (f"%{w}%",))
            recur_count += c.fetchone()[0]
        conn.close()
        if recur_count >= 3:
            score += 0.20
            reasons.append(f"再発{recur_count}回")
        elif recur_count >= 1:
            score += 0.10
            reasons.append(f"再発{recur_count}回")
    except Exception:
        pass

    score = min(score, 1.0)

    # リスクレベル判定
    if score >= 0.70:
        level = "CRITICAL"
    elif score >= 0.50:
        level = "HIGH"
    elif score >= 0.30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": round(score, 3),
        "level": level,
        "reasons": reasons[:3]  # 上位3理由
    }


@app.route("/risk/todos", methods=["GET"])
def risk_todos():
    """全未着手TODOにリスクスコアを付与して返す"""
    try:
        todo_path = os.path.join(os.path.dirname(__file__), "..", "MOCKA_TODO.json")
        if not os.path.exists(todo_path):
            todo_path = r"C:\Users\sirok\MOCKA_TODO.json"

        with open(todo_path, "r", encoding="utf-8") as f:
            todo_data = json.load(f)

        todos = todo_data.get("todos", [])
        active = [t for t in todos if t.get("status") not in ("完了", "closed")]

        scored = []
        for t in active:
            risk = _calc_todo_risk_score(t)
            scored.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "priority": t.get("priority", "中"),
                "category": t.get("category", ""),
                "status": t.get("status", "未着手"),
                "risk_score": risk["score"],
                "risk_level": risk["level"],
                "risk_reasons": risk["reasons"]
            })

        # スコア降順ソート
        scored.sort(key=lambda x: x["risk_score"], reverse=True)

        return jsonify({
            "status": "ok",
            "total": len(scored),
            "todos": scored
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/risk/recommendation", methods=["GET"])
def risk_recommendation():
    """SYSTEM RECOMMENDATION — 今やるべき1つを返す"""
    try:
        todo_path = os.path.join(os.path.dirname(__file__), "..", "MOCKA_TODO.json")
        if not os.path.exists(todo_path):
            todo_path = r"C:\Users\sirok\MOCKA_TODO.json"

        with open(todo_path, "r", encoding="utf-8") as f:
            todo_data = json.load(f)

        todos = todo_data.get("todos", [])
        active = [t for t in todos if t.get("status") not in ("完了", "closed")]

        if not active:
            return jsonify({
                "status": "ok",
                "recommendation": None,
                "message": "全TODOが完了しています"
            })

        # スコア計算して最高リスクを選出
        best = None
        best_score = -1
        for t in active:
            risk = _calc_todo_risk_score(t)
            if risk["score"] > best_score:
                best_score = risk["score"]
                best = {"todo": t, "risk": risk}

        # 推奨メッセージ生成
        t = best["todo"]
        r = best["risk"]
        level_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(r["level"], "⚪")
        message = f"{level_emoji} [{t['id']}] {t['title']}"
        reason_str = " / ".join(r["reasons"]) if r["reasons"] else "優先度・カテゴリ評価"

        return jsonify({
            "status": "ok",
            "recommendation": {
                "id": t.get("id"),
                "title": t.get("title"),
                "priority": t.get("priority"),
                "risk_score": r["score"],
                "risk_level": r["level"],
                "reasons": r["reasons"],
                "message": message,
                "reason_summary": reason_str
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 99999))
    src_filter = request.args.get('src', 'all')
    from datetime import datetime, timedelta
    sort_order = request.args.get('sort', 'desc')
    period = request.args.get('period', 'all')
    order = 'ASC' if sort_order == 'asc' else 'DESC'
    now = datetime.now()
    period_map = {
        'week': now - timedelta(days=7),
        'month': now - timedelta(days=30),
        '3month': now - timedelta(days=90),
        '6month': now - timedelta(days=180),
        'year': now - timedelta(days=365),
    }
    period_from = period_map.get(period)
    if period_from:
        period_clause = period_from.strftime('%Y-%m-%d')
    else:
        period_clause = ''
    if not q or len(q) < 2:
        return jsonify({'results': [], 'total': 0, 'query': q})
    try:
        conn = sqlite3.connect(db_helper.DB_PATH)
        conn.row_factory = sqlite3.Row
        results = []

        # AND/OR解析
        if ' OR ' in q.upper():
            keywords = [k.strip() for k in q.upper().replace(' OR ', '|').split('|')]
            mode = 'OR'
        else:
            keywords = [k.strip() for k in q.split()]
            mode = 'AND'

        def make_like_clause(fields, keywords, mode):
            clauses = []
            params = []
            for kw in keywords:
                sub = ' OR '.join([f"{f} LIKE ?" for f in fields])
                clauses.append(f"({sub})")
                params.extend([f"%{kw}%"] * len(fields))
            join = ' OR ' if mode == 'OR' else ' AND '
            return join.join(clauses), params

        # user_voice検索
        if src_filter in ('all', 'user_voice'):
            fields = ['text', 'session_title']
            clause, params = make_like_clause(fields, keywords, mode)
            pc = f"AND timestamp >= '{period_clause}'" if period_clause else ''
            rows = conn.execute(f"""
                SELECT 'user_voice' as src, id, timestamp as ts,
                       text as body, session_title as title
                FROM user_voice WHERE {clause} {pc}
                ORDER BY timestamp {order} LIMIT ?
            """, params + [limit]).fetchall()
            for r in rows:
                results.append({
                    'source': r['src'], 'id': str(r['id']),
                    'ts': r['ts'], 'title': r['title'] or '(no title)',
                    'body': (r['body'] or '')[:300]
                })

        # events検索（全主要フィールド）
        if src_filter in ('all', 'event'):
            fields = ['title','short_summary','free_note','why_purpose','how_trigger','before_state','after_state','who_actor']
            clause, params = make_like_clause(fields, keywords, mode)
            pc2 = f"AND event_id >= '{period_clause.replace('-','')}' " if period_clause else ''
            rows = conn.execute(f"""
                SELECT 'event' as src, event_id as id, when_ts as ts,
                       title, short_summary as body, what_type, risk_level, why_purpose
                FROM events WHERE {clause} {pc2}
                ORDER BY when_ts {order} LIMIT ?
            """, params + [limit]).fetchall()
            for r in rows:
                results.append({
                    'source': r['src'], 'id': str(r['id']),
                    'ts': r['ts'],
                    'title': r['title'] or r['what_type'] or '(event)',
                    'body': (r['body'] or r['why_purpose'] or '')[:300],
                    'risk': r['risk_level']
                })

        # claude_sessions検索
        if src_filter in ('all', 'session'):
            fields = ['args','result_summary','tool']
            clause, params = make_like_clause(fields, keywords, mode)
            pc3 = f"AND timestamp >= '{period_clause}'" if period_clause else ''
            rows = conn.execute(f"""
                SELECT 'session' as src, id, timestamp as ts,
                       tool as title, result_summary as body
                FROM claude_sessions WHERE {clause} {pc3}
                ORDER BY timestamp {order} LIMIT ?
            """, params + [limit]).fetchall()
            for r in rows:
                results.append({
                    'source': r['src'], 'id': str(r['id']),
                    'ts': r['ts'],
                    'title': f"[session] {r['title'] or ''}",
                    'body': (r['body'] or '')[:300]
                })

        # guidelines検索
        if src_filter in ('all', 'guideline'):
            fields = ['source_text','action_summary','edited_content']
            clause, params = make_like_clause(fields, keywords, mode)
            rows = conn.execute(f"""
                SELECT 'guideline' as src, id, reviewed_at as ts,
                       category as title, action_summary as body
                FROM guidelines_reviewed WHERE {clause}
                ORDER BY reviewed_at DESC LIMIT ?
            """, params + [limit]).fetchall()
            for r in rows:
                results.append({
                    'source': r['src'], 'id': str(r['id']),
                    'ts': r['ts'],
                    'title': f"[guideline] {r['title'] or ''}",
                    'body': (r['body'] or '')[:300]
                })

        conn.close()
        def normalize_ts(ts):
            if not ts: return ''
            ts = str(ts)
            if 'T' in ts: return ts[:19].replace('T',' ')
            if '_' in ts and len(ts) >= 15:
                d = ts[:8]
                t = ts[9:15]
                return d[:4]+'-'+d[4:6]+'-'+d[6:8]+' '+t[:2]+':'+t[2:4]+':'+t[4:6]
            return ts
        results.sort(key=lambda x: normalize_ts(x.get('ts','')), reverse=(sort_order=='desc'))
        return jsonify({'results': results[:limit], 'total': len(results), 'query': q, 'mode': mode})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ── SCAMPER Creative Engine エンドポイント ─────────────────────────────────
SCAMPER_ENGINE_PATH = os.path.join(ROOT_DIR, "PlanningCaliber", "workshop", "scamper_engine", "scamper_engine.py")
SCAMPER_TEMPLATES_PATH = os.path.join(ROOT_DIR, "PlanningCaliber", "workshop", "scamper_engine", "scamper_templates.json")

def _load_scamper_templates():
    if not os.path.exists(SCAMPER_TEMPLATES_PATH):
        return None
    with open(SCAMPER_TEMPLATES_PATH, encoding="utf-8") as f:
        return json.load(f)

def _run_scamper(event_row, templates, use_all=False):
    import re as _re
    scamper = templates["scamper"]
    rules   = templates["expansion_rules"]["trigger_mapping"]

    # 変数抽出
    title  = event_row.get("title", "") or ""
    who    = event_row.get("who_actor", "") or "Claude"
    what_t = event_row.get("what_type", "") or "INCIDENT"
    why    = event_row.get("why_purpose", "") or ""
    how    = event_row.get("how_trigger", "") or ""

    trigger = "INCIDENT"
    if what_t in ("CHANGE_DONE", "CHANGE_START", "FIX", "OPERATION"):
        trigger = "OPERATION"
    elif what_t in ("PHILOSOPHY", "DESIGN"):
        trigger = "PHILOSOPHY"

    short_what = title.replace("INCIDENT:", "").replace("CHANGE_DONE:", "").strip()
    if not short_what:
        short_what = what_t or "不明インシデント"
    short_what = short_what[:40]

    variables = {
        "trigger": trigger, "title": short_what, "what": short_what,
        "who": who, "why": why[:60] or "不明", "how": how[:60] or "不明",
        "n": 1, "operation": short_what,
        "philosophy": "AIを信じるな、システムで縛れ",
        "freq": "5分", "operation_a": "morphology_engine", "operation_b": "PHL-OS",
    }

    apply_ids = list({i for ids in rules.values() for i in ids}) if use_all else rules.get(trigger, rules["INCIDENT"])

    def fill(q, v):
        return _re.sub(r"\{(\w+)\}", lambda m: str(v.get(m.group(1), "{"+m.group(1)+"}")), q)

    expansions = []
    for vk, vd in scamper.items():
        for tmpl in vd["templates"]:
            if tmpl["id"] not in apply_ids:
                continue
            expansions.append({
                "scamper_id": tmpl["id"],
                "view": f"{vk}: {vd['label']}",
                "question": fill(tmpl["question"], variables),
                "output_type": tmpl["output_type"],
                "example_output": tmpl["example_output"],
            })

    return {
        "event_id":    event_row.get("event_id", ""),
        "event_title": title,
        "trigger":     trigger,
        "variables":   variables,
        "expansions":  expansions,
    }

@app.route("/scamper/run", methods=["POST"])
def scamper_run():
    """指定event_idをSCAMPER展開して返す"""
    try:
        data     = request.get_json() or {}
        event_id = data.get("event_id")
        use_all  = data.get("use_all", False)

        templates = _load_scamper_templates()
        if not templates:
            return jsonify({"error": "scamper_templates.json が見つかりません"}), 500

        conn = _sqlite3.connect(db_helper.DB_PATH)
        conn.row_factory = _sqlite3.Row
        if event_id:
            row = conn.execute("SELECT * FROM events WHERE event_id=? LIMIT 1", (event_id,)).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM events WHERE what_type IN ('INCIDENT','DANGER','CRITICAL','MATAKA','CLAIM') ORDER BY when_ts DESC LIMIT 1"
            ).fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "イベントが見つかりません"}), 404

        result = _run_scamper(dict(row), templates, use_all=use_all)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scamper/recent", methods=["GET"])
def scamper_recent():
    """直近インシデントN件をまとめてSCAMPER展開"""
    try:
        limit = int(request.args.get("limit", 3))
        templates = _load_scamper_templates()
        if not templates:
            return jsonify({"error": "scamper_templates.json が見つかりません"}), 500

        conn = _sqlite3.connect(db_helper.DB_PATH)
        conn.row_factory = _sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM events WHERE what_type IN ('INCIDENT','DANGER','CRITICAL','MATAKA','CLAIM') ORDER BY when_ts DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()

        results = [_run_scamper(dict(r), templates) for r in rows]
        return jsonify({"count": len(results), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scamper/status", methods=["GET"])
def scamper_status():
    """SCАMPERエンジンの状態確認"""
    try:
        templates_ok = os.path.exists(SCAMPER_TEMPLATES_PATH)
        engine_ok    = os.path.exists(SCAMPER_ENGINE_PATH)
        output_dir   = os.path.join(ROOT_DIR, "PlanningCaliber", "workshop", "scamper_engine", "scamper_outputs")
        output_count = len([f for f in os.listdir(output_dir) if f.endswith(".json")]) if os.path.exists(output_dir) else 0

        conn = _sqlite3.connect(db_helper.DB_PATH)
        incident_count = conn.execute(
            "SELECT COUNT(*) FROM events WHERE what_type IN ('INCIDENT','DANGER','CRITICAL','MATAKA','CLAIM')"
        ).fetchone()[0]
        conn.close()

        return jsonify({
            "templates_loaded": templates_ok,
            "engine_ready":     engine_ok,
            "output_files":     output_count,
            "incident_pool":    incident_count,
            "status":           "READY" if templates_ok else "ERROR"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("--- MoCKA STARTING ---")
    print(f"[STORAGE] SQLite単一化済み: CSV書き込み完全廃止")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    # ensure_events_csv() → CSV廃止済み。SQLiteはdb_helperが自動初期化。
    app.run(host="127.0.0.1", port=5000, debug=True)

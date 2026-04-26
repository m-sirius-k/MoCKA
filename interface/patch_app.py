"""
patch_app.py
app.py に pattern_engine_v2 統合を自動適用するスクリプト

実行: python interface/patch_app.py
  → app.py をバックアップし、統合コードを注入する

配置先: C:/Users/sirok/MoCKA/interface/patch_app.py
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.environ.get("MOCKA_ROOT", "C:/Users/sirok/MoCKA"))
APP_PY   = BASE_DIR / "app.py"
BACKUP   = BASE_DIR / f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

# ─── パッチ定義 ───────────────────────────────────────────────────────────────

PATCH_IMPORT = """
# --- Pattern Engine v2 (auto-patched) ---
try:
    from interface.pattern_engine_v2 import PatternEngine as _PatternEngine
    _pattern_engine = _PatternEngine()
    print(f"[pattern_engine] OK - {len(_pattern_engine.registry.records)} keywords")
except Exception as _pe_err:
    _pattern_engine = None
    print(f"[pattern_engine] WARN: {_pe_err}")
_pattern_score_history = []
_PATTERN_HISTORY_MAX   = 100
_PATTERN_BATCH_SIZE    = 20
"""

PATCH_HELPER = """
# --- Pattern Engine ヘルパー (auto-patched) ---
def _run_pattern_analysis(text: str, source: str = ""):
    global _pattern_score_history
    if not _pattern_engine or not text:
        return
    try:
        result = _pattern_engine.analyze(text)
        result["source"]    = source
        result["timestamp"] = datetime.now().isoformat()
        result["preview"]   = text[:60]
        _pattern_score_history.append(result)
        if len(_pattern_score_history) > _PATTERN_HISTORY_MAX:
            _pattern_score_history = _pattern_score_history[-_PATTERN_HISTORY_MAX:]
        if len(_pattern_score_history) % _PATTERN_BATCH_SIZE == 0:
            _d = sum(1 for r in _pattern_score_history[-_PATTERN_BATCH_SIZE:]
                     if r["verdict"] in ("DANGER","CRITICAL"))
            _s = sum(1 for r in _pattern_score_history[-_PATTERN_BATCH_SIZE:]
                     if r["verdict"] == "SUCCESS")
            print(f"[pattern_batch] DANGER={_d} SUCCESS={_s}")
        if result["verdict"] in ("CRITICAL","DANGER"):
            print(f"[pattern] {result['verdict']} R={result['R']} {source} '{text[:40]}'")
    except Exception as _e:
        print(f"[pattern_engine] error: {_e}")

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
"""

COLLECT_HOOK = """    # [pattern_engine]
    if _pattern_engine:
        _run_pattern_analysis(text if 'text' in locals() else str(data), source="/collect")
"""

ASK_HOOK = """    # [pattern_engine]
    if _pattern_engine:
        _q = (data.get("question","") + " " + data.get("text","")).strip()
        if _q: _run_pattern_analysis(_q, source="/ask")
"""

SUCCESS_HOOK = """    # [pattern_engine]
    if _pattern_engine:
        _t = text if 'text' in locals() else str(data)
        _pattern_engine.register_manual(_t, "SUCCESS", tier=1)
        _run_pattern_analysis(_t, source="/success")
"""

INDEX_PANEL = """
<!-- === Pattern Score Panel (auto-patched) === -->
<div id="pattern-panel" style="position:fixed;bottom:16px;right:16px;width:260px;background:#1a1a2e;color:#eee;border-radius:12px;padding:14px 16px;font-family:monospace;font-size:12px;box-shadow:0 4px 20px rgba(0,0,0,.4);z-index:9999;opacity:.95">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-weight:bold;font-size:13px">PATTERN ENGINE</span>
    <span id="pe-ts" style="color:#888;font-size:10px">--</span>
  </div>
  <div style="display:flex;gap:8px;margin-bottom:10px">
    <div style="flex:1;text-align:center;background:#0f3460;border-radius:8px;padding:8px">
      <div id="pe-verdict" style="font-size:18px;font-weight:bold;color:#00d4aa">--</div>
      <div style="color:#888;font-size:10px">verdict</div>
    </div>
    <div style="flex:1;text-align:center;background:#0f3460;border-radius:8px;padding:8px">
      <div id="pe-R" style="font-size:18px;font-weight:bold;color:#aaa">0.0</div>
      <div style="color:#888;font-size:10px">R軸</div>
    </div>
  </div>
  <div style="margin-bottom:5px"><span style="color:#888">DANGER </span><span id="pe-dbar" style="display:inline-block;height:6px;background:#ff6b6b;border-radius:3px;width:0;transition:width .4s;vertical-align:middle;margin:0 4px"></span><span id="pe-dn" style="color:#ff6b6b">0</span></div>
  <div style="margin-bottom:10px"><span style="color:#888">SUCCESS</span><span id="pe-sbar" style="display:inline-block;height:6px;background:#00d4aa;border-radius:3px;width:0;transition:width .4s;vertical-align:middle;margin:0 4px"></span><span id="pe-sn" style="color:#00d4aa">0</span></div>
  <div id="pe-prev" style="color:#aaa;font-size:10px;border-top:1px solid #333;padding-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">waiting...</div>
</div>
<script>
(function(){
  var C={CRITICAL:"#ff4444",DANGER:"#ff6b6b",WARNING:"#ffd166",SUCCESS:"#00d4aa",NEUTRAL:"#888"};
  function tick(){
    fetch('/pattern/status').then(r=>r.json()).then(d=>{
      if(d.status!=='ok')return;
      var v=d.last_verdict||'NEUTRAL';
      var el=document.getElementById('pe-verdict');
      el.textContent=v; el.style.color=C[v]||'#eee';
      var rEl=document.getElementById('pe-R');
      rEl.textContent=(d.last_R||0).toFixed(2);
      rEl.style.color=d.last_R>0.6?'#ff6b6b':'#aaa';
      var tot=Math.max(d.recent_count,1);
      document.getElementById('pe-dbar').style.width=Math.round(d.danger_count/tot*120)+'px';
      document.getElementById('pe-sbar').style.width=Math.round(d.success_count/tot*120)+'px';
      document.getElementById('pe-dn').textContent=d.danger_count;
      document.getElementById('pe-sn').textContent=d.success_count;
      var last=(d.history||[]).slice(-1)[0];
      if(last){
        document.getElementById('pe-prev').textContent=last.preview||'';
        document.getElementById('pe-ts').textContent=new Date(last.timestamp).toLocaleTimeString('ja-JP');
      }
    }).catch(function(){});
  }
  setInterval(tick,5000); tick();
})();
</script>
<!-- === /Pattern Score Panel === -->
"""

# ─── 適用処理 ─────────────────────────────────────────────────────────────────

def apply():
    if not APP_PY.exists():
        print(f"[ERROR] {APP_PY} が見つかりません")
        return False

    # バックアップ
    shutil.copy(APP_PY, BACKUP)
    print(f"[1] バックアップ: {BACKUP.name}")

    src = APP_PY.read_text(encoding="utf-8")

    # 二重適用チェック
    if "Pattern Engine v2 (auto-patched)" in src:
        print("[SKIP] 既にパッチ適用済みです")
        return True

    # PATCH 1: importブロックの末尾（from flask import の後）に追加
    # flask import 行を探して直後に挿入
    flask_match = re.search(r'^(from flask import .+)$', src, re.MULTILINE)
    if flask_match:
        insert_pos = flask_match.end()
        src = src[:insert_pos] + "\n" + PATCH_IMPORT + src[insert_pos:]
        print("[2] import パッチ適用")
    else:
        print("[WARN] from flask import が見つかりません。import パッチをスキップ")

    # PATCH 6: 最初の @app.route の直前にヘルパー関数を追加
    route_match = re.search(r'^@app\.route', src, re.MULTILINE)
    if route_match:
        insert_pos = route_match.start()
        src = src[:insert_pos] + PATCH_HELPER + "\n" + src[insert_pos:]
        print("[3] ヘルパー関数 + /pattern/status パッチ適用")
    else:
        print("[WARN] @app.route が見つかりません。ヘルパーパッチをスキップ")

    # PATCH 3: /collect エンドポイントの return 直前に追加
    collect_match = re.search(
        r'(@app\.route\([\'"]/collect[\'"].*?\ndef \w+.*?)(return\s+jsonify)',
        src, re.DOTALL
    )
    if collect_match:
        insert_pos = collect_match.start(2)
        src = src[:insert_pos] + COLLECT_HOOK + src[insert_pos:]
        print("[4] /collect パッチ適用")
    else:
        print("[WARN] /collect エンドポイントが見つかりません（手動で追加してください）")

    # PATCH 4: /ask エンドポイントの return 直前に追加
    ask_match = re.search(
        r'(@app\.route\([\'"]/ask[\'"].*?\ndef \w+.*?)(return\s+jsonify)',
        src, re.DOTALL
    )
    if ask_match:
        insert_pos = ask_match.start(2)
        src = src[:insert_pos] + ASK_HOOK + src[insert_pos:]
        print("[5] /ask パッチ適用")
    else:
        print("[WARN] /ask エンドポイントが見つかりません（手動で追加してください）")

    # PATCH 5: /success エンドポイントの return 直前に追加
    success_match = re.search(
        r'(@app\.route\([\'"]/success[\'"].*?\ndef \w+.*?)(return\s+jsonify)',
        src, re.DOTALL
    )
    if success_match:
        insert_pos = success_match.start(2)
        src = src[:insert_pos] + SUCCESS_HOOK + src[insert_pos:]
        print("[6] /success パッチ適用")
    else:
        print("[WARN] /success エンドポイントが見つかりません（手動で追加してください）")

    # 書き込み
    APP_PY.write_text(src, encoding="utf-8")
    print(f"[7] app.py 書き込み完了")

    # index.html パッチ
    index_html = BASE_DIR / "templates" / "index.html"
    if not index_html.exists():
        index_html = BASE_DIR / "index.html"

    if index_html.exists():
        html_src = index_html.read_text(encoding="utf-8")
        if "Pattern Score Panel" not in html_src:
            html_src = html_src.replace("</body>", INDEX_PANEL + "\n</body>")
            index_html.write_text(html_src, encoding="utf-8")
            print(f"[8] index.html パネル追加: {index_html}")
        else:
            print("[8] index.html パネル: 既存のためスキップ")
    else:
        print("[WARN] index.html が見つかりません")

    print("\n=== パッチ完了 ===")
    print("次: python app.py でサーバーを再起動してください")
    print("確認: curl http://localhost:5000/pattern/status")
    return True


if __name__ == "__main__":
    apply()

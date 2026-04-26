"""
patch_background.py
background.js に「ヒント！」「グレイト！」右クリックメニューを追加

実行: python interface/patch_background.py
配置先: C:/Users/sirok/MoCKA/interface/patch_background.py
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

BG_PATH = Path("C:/Users/sirok/MoCKA/mocka-extension/background.js")
BACKUP  = BG_PATH.parent / f"background_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"

# ─── 追加するメニュー定義 ────────────────────────────────────────────────────
MENU_ITEMS = """    chrome.contextMenus.create({ id:'mocka_hint',  title:'ヒント！（成功シグナル）', contexts:['selection','page'] });
    chrome.contextMenus.create({ id:'mocka_great', title:'グレイト！（強い成功シグナル）', contexts:['selection','page'] });"""

# ─── 追加するクリックハンドラ ─────────────────────────────────────────────────
CLICK_HANDLER = """
  // ── ヒント！/グレイト！ ──────────────────────────────────────────────────
  if (info.menuItemId === 'mocka_hint' || info.menuItemId === 'mocka_great') {
    const text    = info.selectionText || document.title || '';
    const outcome = info.menuItemId === 'mocka_great' ? 'success_great' : 'success_hint';
    const label   = info.menuItemId === 'mocka_great' ? 'グレイト！' : 'ヒント！';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/success', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text:       text,
          what_type:  outcome,
          source:     source,
          label:      label,
          timestamp:  new Date().toISOString()
        })
      });
      chrome.notifications.create({
        type: 'basic', iconUrl: 'icon.png',
        title: `MoCKA ${label}`,
        message: text.slice(0, 60)
      });
    } catch(e) { console.error('success signal error:', e); }
    return;
  }
"""

def apply():
    if not BG_PATH.exists():
        print(f"[ERROR] {BG_PATH} が見つかりません")
        return False

    shutil.copy(BG_PATH, BACKUP)
    print(f"[1] バックアップ: {BACKUP.name}")

    src = BG_PATH.read_text(encoding="utf-8")

    if "mocka_hint" in src:
        print("[SKIP] 既にパッチ適用済みです")
        return True

    # PATCH 1: mocka_collaborate の直後にメニュー2件追加
    target = "id:'mocka_collaborate'"
    pos = src.find(target)
    if pos == -1:
        print("[ERROR] mocka_collaborate が見つかりません")
        return False
    # その行の末尾（セミコロンの後）を探す
    line_end = src.find("\n", pos)
    src = src[:line_end+1] + MENU_ITEMS + "\n" + src[line_end+1:]
    print("[2] メニュー項目追加")

    # PATCH 2: onClicked ハンドラの先頭（最初の if文の直前）に追加
    # "if (info.menuItemId === 'mocka_share')" の直前
    target2 = "if (info.menuItemId === 'mocka_share')"
    pos2 = src.find(target2)
    if pos2 == -1:
        print("[ERROR] mocka_share ハンドラが見つかりません")
        return False
    src = src[:pos2] + CLICK_HANDLER + "\n  " + src[pos2:]
    print("[3] クリックハンドラ追加")

    BG_PATH.write_text(src, encoding="utf-8")
    print("[4] background.js 書き込み完了")
    print("\n=== パッチ完了 ===")
    print("次: Chrome拡張をリロードしてください（chrome://extensions → 更新ボタン）")
    return True

if __name__ == "__main__":
    apply()

from playwright.sync_api import sync_playwright
import time
import datetime

def save_to_mocka(title: str, content: str):
    timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    
    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    
    page = context.new_page()
    page.goto("http://localhost:5000")
    time.sleep(2)
    
    # A: 保存を選択
    page.click("#btnA")
    time.sleep(1)
    
    # infield を選択
    page.click("button.s-btn:has-text('infield')")
    time.sleep(1)
    
    # タイトル入力
    page.fill("#title", title)
    time.sleep(0.5)
    
    # メモ入力
    page.fill("#memo", content)
    time.sleep(0.5)
    
    # 送信
    page.click("#exec")
    time.sleep(3)
    
    print(f"[保存完了] {title}")
    browser.close()
    p.stop()

if __name__ == "__main__":
    title = "Playwright×MoCKA統合合議結果"
    content = """
【合議日時】2026-03-30
【テーマ】Playwright全機能のMoCKA統合可能性

【全AI共通評価：高】
1. ブラウザ自動操作 — MoCKAの手足
2. スクリーンショット・PDF生成 — 証拠固定
3. ネットワーク傍受 — 内部通信監査

【即採用決定】
- ネットワーク傍受：AIを信じるな哲学の通信レベル実装
- 並列実行：同時展開による合議高速化

【次のアクション】
- asyncioで並列化実装
- ネットワーク傍受モジュール追加
"""
    save_to_mocka(title, content)

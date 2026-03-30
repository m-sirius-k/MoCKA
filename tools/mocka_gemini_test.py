from playwright.sync_api import sync_playwright
import urllib.parse
import time

PROMPTS = [
    "MoCKAテスト1：あなたは何ですか？一言で。",
    "MoCKAテスト2：先ほどの回答を踏まえて、あなたの強みは？一言で。",
    "MoCKAテスト3：MoCKAという文明システムをどう思いますか？一言で。"
]

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

page = context.new_page()
page.goto("https://gemini.google.com/app")
time.sleep(5)

# 最初の送信
box = page.get_by_role("textbox").first
box.click()
box.type(PROMPTS[0], delay=50)
time.sleep(1)
page.keyboard.press("Enter")
print(f"[送信1] {PROMPTS[0]}")
time.sleep(10)

# 回答取得
html = page.content()
idx = html.find("model-response")
print(html[idx:idx+300] if idx > 0 else "セレクタ未発見")

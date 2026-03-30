from playwright.sync_api import sync_playwright
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
page.goto("https://copilot.microsoft.com/")
time.sleep(5)

for i, prompt in enumerate(PROMPTS, 1):
    box = page.locator("textarea").first
    box.click()
    box.type(prompt, delay=50)
    time.sleep(1)
    page.keyboard.press("Enter")
    print(f"[送信{i}] {prompt}")
    time.sleep(15)
    
    text = page.evaluate("() => document.body.innerText")
    idx = text.rfind("MoCKAテスト")
    snippet = text[idx:idx+300] if idx > 0 else text[:300]
    print(f"=== 回答{i} ===\n{snippet}\n")

print("完了")

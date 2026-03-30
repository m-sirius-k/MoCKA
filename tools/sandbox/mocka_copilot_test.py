from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

page = context.new_page()
page.goto("https://copilot.microsoft.com/")
time.sleep(5)

box = page.locator("textarea").first
box.click()
box.type("MoCKAテスト：あなたは何ですか？一言で。", delay=50)
time.sleep(1)
page.keyboard.press("Enter")
time.sleep(15)

# inner_textで全body取得
text = page.evaluate("() => document.body.innerText")
idx = text.find("MoCKA")
if idx > 0:
    print(text[idx:idx+500])
else:
    print("未発見")
    print(text[:500])

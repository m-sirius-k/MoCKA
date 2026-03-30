from playwright.sync_api import sync_playwright
import urllib.parse
import time

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

url = "https://www.perplexity.ai/search?q=" + urllib.parse.quote("MoCKAテスト1：あなたは何ですか？一言で。")
page = context.new_page()
page.goto(url)
time.sleep(10)

# 入力欄の種類を調査
print("textarea:", page.locator("textarea").count())
print("textbox:", page.get_by_role("textbox").count())
print("contenteditable:", page.locator('[contenteditable="true"]').count())

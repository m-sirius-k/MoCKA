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

# 最初のpromptで新タブ
url = "https://chatgpt.com/?q=" + urllib.parse.quote(PROMPTS[0])
page = context.new_page()
page.goto(url)
time.sleep(3)
page.keyboard.press("Enter")
print(f"[送信1] {PROMPTS[0]}")
time.sleep(20)

r1 = page.inner_text("[data-turn='assistant']")
print(f"=== 回答1 ===\n{r1}\n")

# 2回目以降は同じタブ
for i, prompt in enumerate(PROMPTS[1:], 2):
    page.click("#prompt-textarea")
    page.type("#prompt-textarea", prompt, delay=50)
    time.sleep(1)
    page.keyboard.press("Enter")
    print(f"[送信{i}] {prompt}")
    time.sleep(20)
    
    responses = page.query_selector_all("[data-turn='assistant']")
    print(f"=== 回答{i} ===\n{responses[-1].inner_text()}\n")

print("完了")

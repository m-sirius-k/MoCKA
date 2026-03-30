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
page.goto("https://gemini.google.com/app")
time.sleep(5)

box = page.get_by_role("textbox").first
box.click()
box.type(PROMPTS[0], delay=50)
time.sleep(1)
page.keyboard.press("Enter")
print(f"[送信1] {PROMPTS[0]}")
time.sleep(10)

r1 = page.inner_text("model-response")
print(f"=== 回答1 ===\n{r1[:200]}\n")

for i, prompt in enumerate(PROMPTS[1:], 2):
    box = page.get_by_role("textbox").first
    box.click()
    box.type(prompt, delay=50)
    time.sleep(1)
    page.keyboard.press("Enter")
    print(f"[送信{i}] {prompt}")
    time.sleep(10)
    
    responses = page.query_selector_all("model-response")
    print(f"=== 回答{i} ===\n{responses[-1].inner_text()[:200]}\n")

print("完了")

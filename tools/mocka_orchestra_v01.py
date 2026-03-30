from playwright.sync_api import sync_playwright
import urllib.parse
import time

PROMPT = "MoCKAという文明システムの最大の価値は何ですか？一言で。"

results = {}

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

# ChatGPT
print("[ChatGPT] 送信中...")
page1 = context.new_page()
page1.goto("https://chatgpt.com/?q=" + urllib.parse.quote(PROMPT))
time.sleep(3)
page1.keyboard.press("Enter")
time.sleep(20)
results["ChatGPT"] = page1.inner_text("[data-turn='assistant']")
print(f"[ChatGPT] {results['ChatGPT'][:100]}")

# Perplexity
print("[Perplexity] 送信中...")
page2 = context.new_page()
page2.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(PROMPT))
time.sleep(10)
results["Perplexity"] = page2.inner_text("[data-renderer='lm']")
print(f"[Perplexity] {results['Perplexity'][:100]}")

# Gemini
print("[Gemini] 送信中...")
page3 = context.new_page()
page3.goto("https://gemini.google.com/app")
time.sleep(5)
box3 = page3.get_by_role("textbox").first
box3.click()
box3.type(PROMPT, delay=50)
page3.keyboard.press("Enter")
time.sleep(15)
results["Gemini"] = page3.inner_text("model-response")
print(f"[Gemini] {results['Gemini'][:100]}")

# Copilot
print("[Copilot] 送信中...")
page4 = context.new_page()
page4.goto("https://copilot.microsoft.com/")
time.sleep(5)
box4 = page4.locator("textarea").first
box4.click()
box4.type(PROMPT, delay=50)
page4.keyboard.press("Enter")
time.sleep(15)
text4 = page4.evaluate("() => document.body.innerText")
idx = text4.find("Copilot の発言")
results["Copilot"] = text4[idx:idx+300] if idx > 0 else text4[:300]
print(f"[Copilot] {results['Copilot'][:100]}")

# 結果まとめ
print("\n=== 全AI回答 ===")
for ai, ans in results.items():
    print(f"\n【{ai}】\n{ans[:200]}")

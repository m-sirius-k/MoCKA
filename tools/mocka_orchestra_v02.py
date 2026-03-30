from playwright.sync_api import sync_playwright
import urllib.parse
import time

query = open(r"C:\Users\sirok\MoCKA\tools\orchestra_playwright_query.txt", encoding="utf-8").read()

results = {}

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

# ChatGPT
print("[ChatGPT] 送信中...")
page1 = context.new_page()
page1.goto("https://chatgpt.com/?q=" + urllib.parse.quote(query))
time.sleep(3)
page1.keyboard.press("Enter")
time.sleep(25)
results["ChatGPT"] = page1.inner_text("[data-turn='assistant']")
print(f"[ChatGPT] 完了")

# Perplexity
print("[Perplexity] 送信中...")
page2 = context.new_page()
page2.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(query))
time.sleep(15)
results["Perplexity"] = page2.inner_text("[data-renderer='lm']")
print(f"[Perplexity] 完了")

# Gemini
print("[Gemini] 送信中...")
page3 = context.new_page()
page3.goto("https://gemini.google.com/app")
time.sleep(5)
box3 = page3.get_by_role("textbox").first
box3.click()
box3.type(query, delay=20)
page3.keyboard.press("Enter")
time.sleep(25)
results["Gemini"] = page3.inner_text("model-response")
print(f"[Gemini] 完了")

# Copilot
print("[Copilot] 送信中...")
page4 = context.new_page()
page4.goto("https://copilot.microsoft.com/")
time.sleep(5)
box4 = page4.locator("textarea").first
box4.click()
box4.type(query, delay=20)
page4.keyboard.press("Enter")
time.sleep(25)
text4 = page4.evaluate("() => document.body.innerText")
idx = text4.find("Copilot の発言")
results["Copilot"] = text4[idx:idx+1000] if idx > 0 else text4[:1000]
print(f"[Copilot] 完了")

# 結果保存
with open(r"C:\Users\sirok\MoCKA\tools\orchestra_results.txt", "w", encoding="utf-8") as f:
    for ai, ans in results.items():
        f.write(f"【{ai}】\n{ans}\n\n{'='*50}\n\n")

print("\n全AI回答を orchestra_results.txt に保存しました")

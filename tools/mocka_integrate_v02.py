from playwright.sync_api import sync_playwright
import urllib.parse
import time

# 4AIから集めた回答
results = {
    "ChatGPT": "再現可能な信頼。",
    "Perplexity": "自律性。",
    "Gemini": "知識記録・AIガバナンスの基盤。",
    "Copilot": "人とAIが同じ歴史を共有し、未来を共同で決められる文明の核。"
}

# Claude用統合プロンプト
integrate_prompt = """以下は「MoCKAという文明システムの最大の価値は何ですか？」への各AIの回答です。

【ChatGPT】再現可能な信頼。
【Perplexity】自律性。
【Gemini】知識記録・AIガバナンスの基盤。
【Copilot】人とAIが同じ歴史を共有し、未来を共同で決められる文明の核。

これらを統合して、MoCKAの本質的価値を200字以内で分析してください。"""

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

# Claudeに統合分析させる
print("[Claude] 統合分析中...")
url = "https://claude.ai/new"
page = context.new_page()
page.goto(url)
time.sleep(5)

box = page.get_by_role("textbox").first
box.click()
box.type(integrate_prompt, delay=30)
time.sleep(1)
page.keyboard.press("Enter")
time.sleep(20)

# 回答取得
text = page.evaluate("() => document.body.innerText")
idx = text.find("MoCKA")
print("=== Claude統合分析 ===")
print(text[idx:idx+500] if idx > 0 else text[:500])

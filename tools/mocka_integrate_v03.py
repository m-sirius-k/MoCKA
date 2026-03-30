from playwright.sync_api import sync_playwright
import time

results = open(r"C:\Users\sirok\MoCKA\tools\orchestra_results.txt", encoding="utf-8").read()

integrate_prompt = """以下は「PlaywrightのMoCKAへの統合可能性」について各AIが回答した内容です。

""" + results[:3000] + """

これらを統合して以下を答えてください：
1. 各AIが共通して高く評価した機能は何か
2. MoCKAに今すぐ組み込むべき優先度TOP3
3. 長期的に最も文明的価値をもたらす機能はどれか

簡潔に構造化して答えてください。"""

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

print("[Claude] 統合分析中...")
page = context.new_page()
page.goto("https://claude.ai/new")
time.sleep(5)

box = page.get_by_role("textbox").first
box.click()
# fillで一括入力（タイムアウト回避）
box.fill(integrate_prompt)
time.sleep(2)
page.keyboard.press("Enter")
time.sleep(30)

text = page.evaluate("() => document.body.innerText")
idx = text.find("1.")
print("=== Claude統合分析 ===")
print(text[idx:idx+2000] if idx > 0 else text[500:2500])

from playwright.sync_api import sync_playwright
import urllib.parse
import time

query = open(r"C:\Users\sirok\MoCKA\tools\orchestra_playwright_query.txt", encoding="utf-8").read()

results = {}

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

def send_and_get(page, prompt, input_selector, submit_selector, response_selector, wait=20, use_fill=True):
    box = page.locator(input_selector).first if input_selector != "textbox" else page.get_by_role("textbox").first
    box.click()
    if use_fill:
        box.fill(prompt)
    else:
        box.type(prompt, delay=20)
    time.sleep(2)
    # 送信ボタンがあればクリック、なければEnter
    try:
        page.locator(submit_selector).click(timeout=3000)
    except:
        page.keyboard.press("Enter")
    time.sleep(wait)
    return page.inner_text(response_selector) if response_selector else page.evaluate("() => document.body.innerText")

# Claude用ページを先に開いて保持
print("[Claude] タブを準備中...")
claude_page = context.new_page()
claude_page.goto("https://claude.ai/new")
time.sleep(5)

# ChatGPT
print("[ChatGPT] 送信中...")
page1 = context.new_page()
page1.goto("https://chatgpt.com/?q=" + urllib.parse.quote(query))
time.sleep(3)
try:
    page1.locator("button[data-testid='send-button']").click(timeout=3000)
except:
    page1.keyboard.press("Enter")
time.sleep(25)
results["ChatGPT"] = page1.inner_text("[data-turn='assistant']")
print("[ChatGPT] 完了")

# Perplexity
print("[Perplexity] 送信中...")
page2 = context.new_page()
page2.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(query))
time.sleep(15)
results["Perplexity"] = page2.inner_text("[data-renderer='lm']")
print("[Perplexity] 完了")

# Gemini（fill+送信ボタン）
print("[Gemini] 送信中...")
page3 = context.new_page()
page3.goto("https://gemini.google.com/app")
time.sleep(5)
box3 = page3.get_by_role("textbox").first
box3.click()
box3.fill(query)
time.sleep(2)
try:
    page3.locator("button[aria-label='送信']").click(timeout=3000)
except:
    try:
        page3.locator("button[aria-label='Send message']").click(timeout=3000)
    except:
        page3.keyboard.press("Enter")
time.sleep(30)
try:
    results["Gemini"] = page3.inner_text("model-response")
except:
    results["Gemini"] = page3.evaluate("() => document.body.innerText")[2000:4000]
print("[Gemini] 完了")

# Copilot（fill+送信ボタン）
print("[Copilot] 送信中...")
page4 = context.new_page()
page4.goto("https://copilot.microsoft.com/")
time.sleep(5)
box4 = page4.locator("textarea").first
box4.click()
box4.fill(query)
time.sleep(2)
try:
    page4.locator("button[aria-label='送信']").click(timeout=3000)
except:
    try:
        page4.locator("button[type='submit']").click(timeout=3000)
    except:
        page4.keyboard.press("Enter")
time.sleep(25)
text4 = page4.evaluate("() => document.body.innerText")
idx = text4.find("Copilot の発言")
results["Copilot"] = text4[idx:idx+1000] if idx > 0 else text4[:1000]
print("[Copilot] 完了")

# 統合プロンプト作成
integrate_prompt = "以下は「PlaywrightのMoCKAへの統合可能性」への各AI回答です。統合分析してください：\n\n"
for ai, ans in results.items():
    integrate_prompt += f"【{ai}】\n{ans[:800]}\n\n"
integrate_prompt += "\n1. 共通して高く評価された機能\n2. 今すぐ組み込むべきTOP3\n3. 長期的に最も文明的価値をもたらす機能\n\n簡潔に答えてください。"

# 既に開いているClaudeに直接送信
print("[Claude] 統合分析中...")
box_c = claude_page.get_by_role("textbox").first
box_c.click()
box_c.fill(integrate_prompt)
time.sleep(2)
claude_page.keyboard.press("Enter")
time.sleep(30)

text_c = claude_page.evaluate("() => document.body.innerText")
idx = text_c.find("1.")
print("=== Claude統合分析 ===")
print(text_c[idx:idx+2000] if idx > 0 else text_c[500:2500])


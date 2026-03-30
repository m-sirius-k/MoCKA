import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time

PROMPT = "MoCKA並列テスト：あなたは何ですか？一言で。"

async def send_chatgpt(context, prompt):
    page = await context.new_page()
    await page.goto("https://chatgpt.com/?q=" + urllib.parse.quote(prompt))
    await asyncio.sleep(5)
    await page.keyboard.press("Enter")
    await asyncio.sleep(20)
    try:
        result = await page.inner_text("[data-turn='assistant']")
        return "ChatGPT", result
    except:
        return "ChatGPT", "取得失敗"

async def send_perplexity(context, prompt):
    page = await context.new_page()
    await page.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(prompt))
    await asyncio.sleep(12)
    try:
        result = await page.inner_text("[data-renderer='lm']")
        return "Perplexity", result
    except:
        return "Perplexity", "取得失敗"

async def send_gemini(context, prompt):
    page = await context.new_page()
    await page.goto("https://gemini.google.com/app")
    await asyncio.sleep(5)
    box = page.get_by_role("textbox").first
    await box.click()
    await box.fill(prompt)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(20)
    try:
        result = await page.inner_text("model-response")
        return "Gemini", result[:300]
    except:
        return "Gemini", "取得失敗"

async def send_copilot(context, prompt):
    page = await context.new_page()
    await page.goto("https://copilot.microsoft.com/")
    await asyncio.sleep(5)
    box = page.locator("textarea").first
    await box.click()
    await box.fill(prompt)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(20)
    try:
        text = await page.evaluate("() => document.body.innerText")
        idx = text.find("Copilot の発言")
        return "Copilot", text[idx:idx+200] if idx > 0 else text[:200]
    except:
        return "Copilot", "取得失敗"

async def main():
    start = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        # 全AI同時実行
        print("[並列送信開始]")
        tasks = [
            send_chatgpt(context, PROMPT),
            send_perplexity(context, PROMPT),
            send_gemini(context, PROMPT),
            send_copilot(context, PROMPT),
        ]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        print(f"\n=== 全AI回答（{elapsed:.1f}秒） ===")
        for ai, ans in results:
            print(f"\n【{ai}】\n{ans[:150]}")

asyncio.run(main())


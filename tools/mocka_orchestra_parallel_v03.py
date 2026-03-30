import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time

PROMPTS = [
    "MoCKA並列テスト1：あなたは何ですか？一言で。",
    "MoCKA並列テスト2：先ほどの回答を踏まえて強みは？一言で。",
    "MoCKA並列テスト3：MoCKAという文明をどう思いますか？一言で。"
]

async def run_chatgpt(context):
    page = await context.new_page()
    results = []
    await page.goto("https://chatgpt.com/?q=" + urllib.parse.quote(PROMPTS[0]))
    await asyncio.sleep(5)
    await page.keyboard.press("Enter")
    await asyncio.sleep(20)
    els = await page.query_selector_all("[data-turn='assistant']")
    results.append(await els[-1].inner_text() if els else "取得失敗")
    print(f"[ChatGPT] 回答1: {results[-1][:50]}")
    for i, prompt in enumerate(PROMPTS[1:], 2):
        await page.click("#prompt-textarea")
        await page.fill("#prompt-textarea", prompt)
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")
        await asyncio.sleep(20)
        els = await page.query_selector_all("[data-turn='assistant']")
        results.append(await els[-1].inner_text() if els else "取得失敗")
        print(f"[ChatGPT] 回答{i}: {results[-1][:50]}")
    return "ChatGPT", results

async def run_perplexity(context):
    page = await context.new_page()
    results = []
    await page.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(PROMPTS[0]))
    await asyncio.sleep(12)
    els = await page.query_selector_all("[data-renderer='lm']")
    results.append(await els[-1].inner_text() if els else "取得失敗")
    print(f"[Perplexity] 回答1: {results[-1][:50]}")
    for i, prompt in enumerate(PROMPTS[1:], 2):
        box = page.get_by_role("textbox").first
        await box.click()
        await box.fill(prompt)
        await page.keyboard.press("Enter")
        await asyncio.sleep(12)
        els = await page.query_selector_all("[data-renderer='lm']")
        results.append(await els[-1].inner_text() if els else "取得失敗")
        print(f"[Perplexity] 回答{i}: {results[-1][:50]}")
    return "Perplexity", results

async def run_gemini(context):
    page = await context.new_page()
    results = []
    await page.goto("https://gemini.google.com/app")
    await asyncio.sleep(5)
    for i, prompt in enumerate(PROMPTS, 1):
        box = page.get_by_role("textbox").first
        await box.click()
        await box.fill(prompt)
        await asyncio.sleep(2)
        await page.keyboard.press("Enter")
        await asyncio.sleep(20)
        els = await page.query_selector_all("model-response")
        results.append(await els[-1].inner_text() if els else "取得失敗")
        print(f"[Gemini] 回答{i}: {results[-1][:50]}")
    return "Gemini", results

async def run_copilot(context):
    page = await context.new_page()
    results = []
    await page.goto("https://copilot.microsoft.com/")
    await asyncio.sleep(5)
    for i, prompt in enumerate(PROMPTS, 1):
        box = page.locator("textarea").first
        await box.click()
        await box.fill(prompt)
        await asyncio.sleep(2)
        await page.keyboard.press("Enter")
        await asyncio.sleep(20)
        text = await page.evaluate("() => document.body.innerText")
        idx = text.rfind("Copilot の発言")
        results.append(text[idx:idx+200] if idx > 0 else "取得失敗")
        print(f"[Copilot] 回答{i}: {results[-1][:50]}")
    return "Copilot", results

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        tasks = [
            run_chatgpt(context),
            run_perplexity(context),
            run_gemini(context),
            run_copilot(context),
        ]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        print(f"\n=== 完了（{elapsed:.1f}秒） ===")
        for name, answers in results:
            print(f"\n【{name}】")
            for i, ans in enumerate(answers, 1):
                print(f"  回答{i}: {ans[:100]}")

asyncio.run(main())

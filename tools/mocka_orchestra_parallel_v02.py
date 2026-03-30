import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time

PROMPTS = [
    "MoCKA並列テスト1：あなたは何ですか？一言で。",
    "MoCKA並列テスト2：先ほどの回答を踏まえて強みは？一言で。",
    "MoCKA並列テスト3：MoCKAという文明をどう思いますか？一言で。"
]

async def run_ai(context, name, goto_func, send_func, get_func):
    page = await context.new_page()
    results = []
    
    # 最初のpromptで新タブ開く
    await goto_func(page, PROMPTS[0])
    await asyncio.sleep(3)
    await send_func(page, PROMPTS[0], first=True)
    await asyncio.sleep(20)
    r = await get_func(page, 0)
    results.append(r)
    print(f"[{name}] 回答1: {r[:50]}")
    
    # 2回目以降は同じタブ
    for i, prompt in enumerate(PROMPTS[1:], 2):
        await send_func(page, prompt, first=False)
        await asyncio.sleep(20)
        r = await get_func(page, i-1)
        results.append(r)
        print(f"[{name}] 回答{i}: {r[:50]}")
    
    return name, results

async def chatgpt_goto(page, prompt):
    await page.goto("https://chatgpt.com/?q=" + urllib.parse.quote(prompt))

async def chatgpt_send(page, prompt, first=False):
    if first:
        await asyncio.sleep(5)
        await page.keyboard.press("Enter")
    else:
        await page.click("#prompt-textarea")
        await page.fill("#prompt-textarea", prompt)
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")

async def chatgpt_get(page, idx):
    try:
        await asyncio.sleep(3)
        els = await page.query_selector_all("[data-turn='assistant']")
        return await els[-1].inner_text() if els else "取得失敗"
    except:
        return "取得失敗"

async def perplexity_goto(page, prompt):
    await page.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(prompt))

async def perplexity_send(page, prompt, first=False):
    if first:
        await asyncio.sleep(8)
    else:
        box = page.get_by_role("textbox").first
        await box.click()
        await box.fill(prompt)
        await page.keyboard.press("Enter")

async def perplexity_get(page, idx):
    try:
        els = await page.query_selector_all("[data-renderer='lm']")
        return await els[idx].inner_text() if els else "取得失敗"
    except:
        return "取得失敗"

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        tasks = [
            run_ai(context, "ChatGPT", chatgpt_goto, chatgpt_send, chatgpt_get),
            run_ai(context, "Perplexity", perplexity_goto, perplexity_send, perplexity_get),
        ]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        print(f"\n=== 完了（{elapsed:.1f}秒） ===")
        for name, answers in results:
            print(f"\n【{name}】")
            for i, ans in enumerate(answers, 1):
                print(f"  回答{i}: {ans[:100]}")

asyncio.run(main())



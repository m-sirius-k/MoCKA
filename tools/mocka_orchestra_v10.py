import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time

import sys
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "PlaywrightをMoCKA環境に組み込む場合、最も優先すべき機能を2つ、理由付きで提案してください。MoCKAの哲学「AIを信じるな、システムで縛れ」を踏まえて。"

def clean(ans):
    ans = ans.replace("ChatGPT:\n","").replace("ChatGPT:","")
    ans = ans.replace("Is this conversation helpful so far?","")
    ans = ans.replace("この性格は気に入りましたか？","")
    ans = ans.replace("Gemini の回答\n","").replace("Gemini の回答","")
    if "【知識記録" in ans: ans = ans.split("【知識記録")[0]
    if "作成AI：" in ans: ans = ans.split("作成AI：")[0]
    if "Copilot の発言" in ans:
        ans = ans.replace("Copilot の発言","").strip()
        lines = [l.strip() for l in ans.split("\n") if l.strip() and "MoCKA並列" not in l and "受理" not in l]
        ans = "\n".join(lines[:5]) if lines else ""
    return ans.strip()[:500]

async def run_chatgpt(context):
    page = await context.new_page()
    await page.goto("https://chatgpt.com/?q=" + urllib.parse.quote(PROMPT))
    await asyncio.sleep(5)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    els = await page.query_selector_all("[data-turn='assistant']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[ChatGPT] 完了")
    return "ChatGPT", result

async def run_perplexity(context):
    page = await context.new_page()
    await page.goto("https://www.perplexity.ai/search?q=" + urllib.parse.quote(PROMPT))
    await asyncio.sleep(15)
    els = await page.query_selector_all("[data-renderer='lm']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[Perplexity] 完了")
    return "Perplexity", result

async def run_gemini(context):
    page = await context.new_page()
    await page.goto("https://gemini.google.com/app")
    await asyncio.sleep(5)
    box = page.get_by_role("textbox").first
    await box.click()
    await box.fill(PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    els = await page.query_selector_all("model-response")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[Gemini] 完了")
    return "Gemini", result

async def run_copilot(context):
    page = await context.new_page()
    await page.goto("https://copilot.microsoft.com/")
    await asyncio.sleep(5)
    box = page.locator("textarea").first
    await box.click()
    await box.fill(PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    text = await page.evaluate("() => document.body.innerText")
    idx = text.rfind("Copilot の発言")
    result = text[idx:idx+800] if idx > 0 else text[:800]
    print(f"[Copilot] 完了")
    return "Copilot", result

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

        # Claude1のchat欄を先に確保
        print("[Claude] 既存タブ検索中...")
        claude_page = None
        for pg in context.pages:
            if "claude.ai" in pg.url:
                claude_page = pg
                print(f"[Claude] 発見: {pg.url[:60]}")
                break
        if not claude_page:
            claude_page = await context.new_page()
            await claude_page.goto("https://claude.ai/new")
            await asyncio.sleep(5)

        # 4AI並列実行
        tasks = [
            run_chatgpt(context),
            run_perplexity(context),
            run_gemini(context),
            run_copilot(context),
        ]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        # 回答をClaude1のchat欄に配置（Enterなし）
        prompt = f"以下は「{PROMPT[:50]}...」への各AI回答です。共通項・分布・別視点を分析し最適解を出してください。\n\n"
        for name, ans in results:
            prompt += f"【{name}】\n{clean(ans)}\n\n"

        await claude_page.bring_to_front()
        box = claude_page.get_by_role("textbox").first
        await box.click()
        await box.fill(prompt)
        print(f"\n[完了] {elapsed:.1f}秒 — Claude1のchat欄に配置済み。確認後にEnterを押してください。")

asyncio.run(main())

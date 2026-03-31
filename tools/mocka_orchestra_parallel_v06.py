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



async def integrate_claude(claude_page, all_results):
    await claude_page.bring_to_front()
    await asyncio.sleep(2)
    def clean(ans):
        ans = ans.replace("ChatGPT:\n","").replace("ChatGPT:","")
        ans = ans.replace("Is this conversation helpful so far?","")
        ans = ans.replace("この性格は気に入りましたか？","")
        ans = ans.replace("Gemini の回答\n","").replace("Gemini の回答","")
        if "【知識記録" in ans:
            ans = ans.split("【知識記録")[0]
        if "作成AI：" in ans:
            ans = ans.split("作成AI：")[0]
        if "Copilot の発言" in ans:
            ans = ans.replace("Copilot の発言","").strip()
            lines = [l.strip() for l in ans.split("\n") if l.strip() and "MoCKA並列テスト" not in l and "受理" not in l]
            ans = lines[0] if lines else ""
        lines = [l.strip() for l in ans.split("\n") if l.strip()]
        return lines[0][:100] if lines else "取得失敗"

    prompt = "以下は同じ3問への各AIの回答です。統合分析して本質を200字以内で。\n\n"
    for name, answers in all_results:
        prompt += f"【{name}】\n"
        for i, ans in enumerate(answers, 1):
            prompt += f"Q{i}: {clean(ans)}\n"
        prompt += "\n"
    # chat欄に貼り付けるだけ（Enterは押さない）
    box = claude_page.get_by_role("textbox").first
    await box.click()
    await box.fill(prompt)
    await claude_page.bring_to_front()
    print(f"\n=== Claude1のchat欄に回答を配置。確認後にEnterを押してください ===")

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

        # Claude1 = 現在開いているClaudeタブを取得
        print("[Claude] 既存タブ検索中...")
        claude_page = None
        for p in context.pages:
            if "claude.ai" in p.url:
                claude_page = p
                print(f"[Claude] 既存タブ発見: {p.url[:60]}")
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
        print(f"\n=== 全AI完了（{elapsed:.1f}秒） ===")
        for name, answers in results:
            print(f"\n【{name}】")
            for i, ans in enumerate(answers, 1):
                print(f"  回答{i}: {ans[:80]}")

        # Claude1に戻って統合分析
        print("\n[Claude] 統合分析中...")
        await integrate_claude(claude_page, results)

asyncio.run(main())











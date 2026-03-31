import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time
import sys

MODE = sys.argv[2] if len(sys.argv) > 2 else "orchestra"
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

async def get_or_create_page(context, domain, new_url):
    """既存タブを再利用、なければ新規作成"""
    for pg in context.pages:
        if domain in pg.url:
            print(f"[再利用] {domain}")
            return pg, False  # 既存タブ
    page = await context.new_page()
    await page.goto(new_url)
    return page, True  # 新規タブ

async def run_chatgpt(context):
    page, is_new = await get_or_create_page(context, "chatgpt.com", "https://chatgpt.com/")
    if is_new:
        await asyncio.sleep(5)
    # 入力欄にpromptを入力
    try:
        await page.click("#prompt-textarea", timeout=5000)
        await page.fill("#prompt-textarea", PROMPT)
    except:
        await page.keyboard.press("End")
        await asyncio.sleep(1)
        await page.fill("#prompt-textarea", PROMPT)
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    els = await page.query_selector_all("[data-turn='assistant']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[ChatGPT] 完了")
    return "ChatGPT", result

async def run_perplexity(context):
    page, is_new = await get_or_create_page(context, "perplexity.ai", "https://www.perplexity.ai/")
    # SPA対応: JS経由で強制遷移
    target = "https://www.perplexity.ai/search?q=" + urllib.parse.quote(PROMPT)
    await page.evaluate(f"window.location.href = '{target}'")
    await asyncio.sleep(15)
    els = await page.query_selector_all("[data-renderer='lm']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[Perplexity] 完了")
    return "Perplexity", result

async def run_gemini(context):
    page, is_new = await get_or_create_page(context, "gemini.google.com", "https://gemini.google.com/app")
    if is_new:
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
    page, is_new = await get_or_create_page(context, "copilot.microsoft.com", "https://copilot.microsoft.com/")
    if is_new:
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

        # orchestraモードのみClaudeタブを確保
        claude_page = None
        if MODE == "orchestra":
            print("[Claude] 既存タブ検索中...")
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

        if MODE == "orchestra" and claude_page:
            integrate_prompt = f"以下は「{PROMPT[:50]}...」への各AI回答です。共通項・分布・別視点を分析し最適解を出してください。\n\n"
            for name, ans in results:
                integrate_prompt += f"【{name}】\n{clean(ans)}\n\n"
            await claude_page.bring_to_front()
            box = claude_page.get_by_role("textbox").first
            await box.click()
            await box.fill(integrate_prompt)
            print(f"\n[完了] {elapsed:.1f}秒 — Claude1のchat欄に配置済み。確認後にEnterを押してください。")
        else:
            print(f"\n[共有完了] {elapsed:.1f}秒 — 各AIに送信しました")

asyncio.run(main())
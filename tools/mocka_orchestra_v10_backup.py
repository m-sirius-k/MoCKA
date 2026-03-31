import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time
import sys
import json
import os

MODE = sys.argv[2] if len(sys.argv) > 2 else "orchestra"
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "PlaywrightをMoCKA環境に組み込む場合、最も優先すべき機能を2つ、理由付きで提案してください。MoCKAの哲学「AIを信じるな、システムで縛れ」を踏まえて。"

CHAT_URLS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_urls.json")

def load_chat_urls():
    if os.path.exists(CHAT_URLS_FILE):
        with open(CHAT_URLS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_chat_url(ai_name, url):
    urls = load_chat_urls()
    urls[ai_name] = url
    with open(CHAT_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)

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

async def get_or_resume_page(context, ai_name, domain, new_url):
    """保存済みchat URLに戻る、なければ新規作成"""
    chat_urls = load_chat_urls()
    saved_url = chat_urls.get(ai_name)

    # 既存タブを探す
    for pg in context.pages:
        if domain in pg.url:
            print(f"[既存タブ] {ai_name}: {pg.url[:60]}")
            return pg, "existing"

    # 保存済みURLがあれば復元
    if saved_url:
        print(f"[復元] {ai_name}: {saved_url[:60]}")
        page = await context.new_page()
        await page.goto(saved_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        return page, "resumed"

    # 新規作成
    print(f"[新規] {ai_name}")
    page = await context.new_page()
    await page.goto(new_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(5)
    return page, "new"

async def run_chatgpt(context):
    page, status = await get_or_resume_page(context, "ChatGPT", "chatgpt.com", "https://chatgpt.com/")
    await page.click("#prompt-textarea", timeout=5000)
    await page.fill("#prompt-textarea", PROMPT)
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    # chat URLを保存
    save_chat_url("ChatGPT", page.url)
    els = await page.query_selector_all("[data-turn='assistant']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[ChatGPT] 完了 ({status})")
    return "ChatGPT", result

async def run_perplexity(context):
    chat_urls = load_chat_urls()
    saved_url = chat_urls.get("Perplexity")

    # 既存タブで保存済みURLのものを探す
    page = None
    for pg in context.pages:
        if "perplexity.ai" in pg.url and saved_url and saved_url in pg.url:
            page = pg
            print(f"[既存タブ] Perplexity: {pg.url[:60]}")
            break

    if not page:
        page = await context.new_page()
        if saved_url:
            print(f"[復元] Perplexity: {saved_url[:60]}")
            await page.goto(saved_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
        else:
            print(f"[新規] Perplexity")
            await page.goto("https://www.perplexity.ai/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

    # 入力欄にpromptを入力
    box = page.get_by_role("textbox").first
    await box.click()
    await box.fill(PROMPT)
    await page.keyboard.press("Enter")
    await asyncio.sleep(15)

    # chat URLを保存
    save_chat_url("Perplexity", page.url)
    els = await page.query_selector_all("[data-renderer='lm']")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[Perplexity] 完了")
    return "Perplexity", result

async def run_gemini(context):
    page, status = await get_or_resume_page(context, "Gemini", "gemini.google.com", "https://gemini.google.com/app")
    box = page.get_by_role("textbox").first
    await box.click()
    await box.fill(PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    save_chat_url("Gemini", page.url)
    els = await page.query_selector_all("model-response")
    result = await els[-1].inner_text() if els else "取得失敗"
    print(f"[Gemini] 完了 ({status})")
    return "Gemini", result

async def run_copilot(context):
    page, status = await get_or_resume_page(context, "Copilot", "copilot.microsoft.com", "https://copilot.microsoft.com/")
    box = page.locator("textarea").first
    await box.click()
    await box.fill(PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(25)
    save_chat_url("Copilot", page.url)
    text = await page.evaluate("() => document.body.innerText")
    idx = text.rfind("Copilot の発言")
    result = text[idx:idx+800] if idx > 0 else text[:800]
    print(f"[Copilot] 完了 ({status})")
    return "Copilot", result

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

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
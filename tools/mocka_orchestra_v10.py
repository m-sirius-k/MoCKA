import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import time
import sys
import json
import os

MODE = sys.argv[2] if len(sys.argv) > 2 else "orchestra"
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "PlaywrightをMoCKA環境に組み込む場合、最も優先すべき機能を2つ、理由付きで提案してください。MoCKAの哲学「AIを信じるな、システムで縛れ」を踏まえて。"

# TODO_419: Orchestra Context Bridge統合(DC_20260707_006承認)
_NO_CONTEXT = "--no-context" in sys.argv
try:
    from orchestra_context_bridge import inject_context as _inject_context
    ENRICHED_PROMPT = PROMPT if _NO_CONTEXT else _inject_context(PROMPT)
except ImportError:
    ENRICHED_PROMPT = PROMPT

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
    return ans.strip()[:2000]

async def wait_for_completion(get_text_func, ai_name, timeout=120, stable_sec=3, interval=2):
    """テキストが安定したら完了とみなす"""
    print(f"[{ai_name}] 回答待機中...")
    prev = ""
    stable_count = 0
    needed = stable_sec // interval
    elapsed = 0
    while elapsed < timeout:
        await asyncio.sleep(interval)
        elapsed += interval
        try:
            curr = await get_text_func()
        except:
            curr = prev
        if curr and curr == prev and len(curr) > 10:
            stable_count += 1
            if stable_count >= needed:
                print(f"[{ai_name}] 回答確定 ({elapsed}秒)")
                return curr
        else:
            stable_count = 0
        prev = curr
    print(f"[{ai_name}] タイムアウト ({timeout}秒)")
    return prev

async def preflight_check(page, ai_name, timeout=10):
    """TODO_166: ページが入力可能状態であることを検査する(preflight check)"""
    start = time.time()
    print(f"[{ai_name}] プリフライトチェック開始...")

    try:
        captcha_selectors = [
            'iframe[title="reCAPTCHA"]',
            'iframe[src*="recaptcha"]',
            'div.grecaptcha',
            'div[data-captcha]',
            'div.captcha',
            '[id*="captcha"]'
        ]
        for sel in captcha_selectors:
            if await page.query_selector(sel):
                elapsed = time.time() - start
                print(f"[{ai_name}] ⚠️ CAPTCHA検知 ({elapsed:.1f}秒)")
                return {"status": "BLOCKED_CAPTCHA", "description": "CAPTCHA detected", "wait_time": elapsed}

        dialog_keywords = ["login", "sign in", "sign up", "cookie", "accept", "agree"]
        for kw in dialog_keywords:
            elements = await page.query_selector_all(f'text="{kw}"')
            if elements:
                elapsed = time.time() - start
                print(f"[{ai_name}] ⚠️ Dialog検知: {kw} ({elapsed:.1f}秒)")
                return {"status": "BLOCKED_DIALOG", "description": f"Dialog detected: {kw}", "wait_time": elapsed}

        input_selectors = [
            "#prompt-textarea",
            "textarea[placeholder*='prompt']",
            "textarea[placeholder*='message']",
            "[data-testid='text-input']",
            "div[contenteditable='true']",
            "div.ProseMirror",
            "textarea"
        ]

        for sel in input_selectors:
            try:
                field = page.locator(sel).first
                await field.wait_for(state="visible", timeout=2000)
                await field.wait_for(state="enabled", timeout=1000)
                elapsed = time.time() - start
                print(f"[{ai_name}] ✓ 入力フィールド確認 ({elapsed:.1f}秒)")
                return {
                    "status": "READY",
                    "description": "Input field ready",
                    "input_field": field,
                    "wait_time": elapsed,
                    "selector": sel
                }
            except:
                continue

        elapsed = time.time() - start
        print(f"[{ai_name}] ⚠️ 入力フィールド未検出 ({elapsed:.1f}秒)")
        return {"status": "ERROR", "description": "Input field not found", "wait_time": elapsed}

    except Exception as e:
        elapsed = time.time() - start
        print(f"[{ai_name}] ❌ プリフライトエラー: {str(e)[:50]} ({elapsed:.1f}秒)")
        return {"status": "ERROR", "description": f"Preflight error: {str(e)[:50]}", "wait_time": elapsed}

async def get_or_resume_page(context, ai_name, domain, new_url):
    chat_urls = load_chat_urls()
    saved_url = chat_urls.get(ai_name)
    for pg in context.pages:
        if domain in pg.url:
            print(f"[既存タブ] {ai_name}: {pg.url[:60]}")
            return pg, "existing"
    if saved_url:
        print(f"[復元] {ai_name}: {saved_url[:60]}")
        page = await context.new_page()
        await page.goto(saved_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        return page, "resumed"
    print(f"[新規] {ai_name}")
    page = await context.new_page()
    await page.goto(new_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(5)
    return page, "new"

async def run_chatgpt(context):
    page, status = await get_or_resume_page(context, "ChatGPT", "chatgpt.com", "https://chatgpt.com/")

    pf = await preflight_check(page, "ChatGPT", timeout=10)
    if pf["status"] != "READY":
        print(f"[ChatGPT] ⚠️ ブロッカー検知: {pf['status']} — スキップ")
        return "ChatGPT", f"BLOCKED: {pf['status']}"

    chatgpt_box = pf["input_field"]
    await chatgpt_box.click()
    await chatgpt_box.fill(ENRICHED_PROMPT)
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)

    async def get_text():
        els = await page.query_selector_all("[data-turn='assistant']")
        return await els[-1].inner_text() if els else ""

    result = await wait_for_completion(get_text, "ChatGPT")
    save_chat_url("ChatGPT", page.url)
    print(f"[ChatGPT] 完了 ({status})")
    return "ChatGPT", result

async def run_perplexity(context):
    chat_urls = load_chat_urls()
    saved_url = chat_urls.get("Perplexity")
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

    if MODE == "orchestra":
        await page.goto("https://www.perplexity.ai/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

    pf = await preflight_check(page, "Perplexity", timeout=10)
    if pf["status"] != "READY":
        print(f"[Perplexity] ⚠️ ブロッカー検知: {pf['status']} — スキップ")
        return "Perplexity", f"BLOCKED: {pf['status']}"

    box = pf.get("input_field") or page.get_by_role("textbox").first
    await box.click()
    await box.fill(ENRICHED_PROMPT)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)

    async def get_text():
        els = await page.query_selector_all("[data-renderer='lm']")
        return await els[-1].inner_text() if els else ""

    result = await wait_for_completion(get_text, "Perplexity")
    save_chat_url("Perplexity", page.url)
    print(f"[Perplexity] 完了")
    return "Perplexity", result

async def run_gemini(context):
    page, status = await get_or_resume_page(context, "Gemini", "gemini.google.com", "https://gemini.google.com/app")
    if "/app" not in page.url or "app?" in page.url:
        print(f"[Gemini] チャット画面外検出 → /appに遷移")
        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)

    current_url = page.url
    print(f"[Gemini] URL確認: {current_url[:60]}")

    pf = await preflight_check(page, "Gemini", timeout=10)
    if pf["status"] != "READY":
        print(f"[Gemini] ⚠️ ブロッカー検知: {pf['status']} — スキップ")
        return "Gemini", f"BLOCKED: {pf['status']}"

    box = pf.get("input_field") or page.get_by_role("textbox").first
    await box.click()
    await box.fill(ENRICHED_PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)

    async def get_text():
        els = await page.query_selector_all("model-response")
        return await els[-1].inner_text() if els else ""

    result = await wait_for_completion(get_text, "Gemini")
    save_chat_url("Gemini", page.url)
    print(f"[Gemini] 完了 ({status})")
    return "Gemini", result

async def run_copilot(context):
    page, status = await get_or_resume_page(context, "Copilot", "copilot.microsoft.com", "https://copilot.microsoft.com/")

    pf = await preflight_check(page, "Copilot", timeout=10)
    if pf["status"] != "READY":
        print(f"[Copilot] ⚠️ ブロッカー検知: {pf['status']} — スキップ")
        return "Copilot", f"BLOCKED: {pf['status']}"

    box = pf.get("input_field")
    if not box:
        for selector in ["textarea", "#userInput", "[data-testid='composer-input']", "div[contenteditable='true']", "cib-text-input textarea", "div.input-area textarea"]:
            try:
                el = page.locator(selector).first
                await el.wait_for(state="visible", timeout=2000)
                box = el
                print(f"[Copilot] セレクター発見: {selector}")
                break
            except:
                continue

    if box is None:
        print("[Copilot] 入力欄が見つからない - スキップ")
        return "Copilot", ""

    await box.click()
    await box.fill(ENRICHED_PROMPT)
    await asyncio.sleep(2)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)

    async def get_text():
        text = await page.evaluate("() => document.body.innerText")
        idx = text.rfind("Copilot の発言")
        return text[idx:idx+2000] if idx > 0 else text[-2000:]

    result = await wait_for_completion(get_text, "Copilot")
    save_chat_url("Copilot", page.url)
    print(f"[Copilot] 完了 ({status})")
    return "Copilot", result

async def main():
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
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






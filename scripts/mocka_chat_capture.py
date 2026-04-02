"""
mocka_chat_capture.py
使い方:
  python scripts/mocka_chat_capture.py --url https://chatgpt.com/c/XXXX
  python scripts/mocka_chat_capture.py --url https://claude.ai/chat/XXXX
  python scripts/mocka_chat_capture.py --url https://gemini.google.com/app/XXXX

初回のみ:
  python scripts/mocka_chat_capture.py --login --source chatgpt
  → ブラウザが開くので手動ログイン → Enterで保存
"""
import asyncio, argparse, csv, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(r'C:\Users\sirok\MoCKA')
INFIELD = ROOT / 'data' / 'storage' / 'infield' / 'RAW'
EVENTS  = ROOT / 'data' / 'events.csv'
STATES  = ROOT / 'scripts' / 'sessions'
INFIELD.mkdir(parents=True, exist_ok=True)
STATES.mkdir(parents=True, exist_ok=True)
UTC = timezone.utc

# 各AIのメッセージセレクタ
SELECTORS = {
    'chatgpt':    '[data-message-author-role]',
    'claude':     '[data-testid*="message"], .font-claude-message, [class*="ConversationMessage"]',
    'gemini':     'message-content, model-response, user-query',
    'perplexity': '[class*="Message"], .message, [data-testid*="message"]',
    'copilot':    '[class*="message"], .cib-message-item',
    'default':    '[class*="message"], [class*="Message"], p',
}

def detect_source(url):
    if 'chatgpt.com' in url:       return 'chatgpt'
    if 'claude.ai' in url:         return 'claude'
    if 'gemini.google' in url:     return 'gemini'
    if 'perplexity.ai' in url:     return 'perplexity'
    if 'microsoft.com' in url:     return 'copilot'
    return 'unknown'

def mask(t):
    t = re.sub(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', '[EMAIL]', t)
    t = re.sub(r'sk-[A-Za-z0-9]{20,}', '[APIKEY]', t)
    t = re.sub(r'(?i)password\s*[:=]\s*\S+', 'password=[MASKED]', t)
    return t

def get_prev():
    rows = list(csv.reader(open(EVENTS, encoding='utf-8-sig'))) if EVENTS.exists() else []
    return hashlib.sha256(','.join(rows[-1]).encode()).hexdigest()[:16] if rows else 'GENESIS'

def save_to_mocka(messages, source, url):
    prev   = get_prev()
    ts     = datetime.now(UTC)
    ts_str = ts.strftime('%Y-%m-%dT%H:%M:%S')
    ts_f   = ts.strftime('%Y%m%d_%H%M%S')
    eid    = f'ECAP_{ts_f}_{source[:4].upper()}'
    text   = '\n\n'.join([f"[{m['role']}] {m['content']}" for m in messages])
    text   = mask(text)
    h      = hashlib.sha256(f'{eid}{ts_str}{text[:100]}{prev}'.encode()).hexdigest()[:16]
    rec    = {
        'event_id': eid, 'source': source, 'layer': 'RAW',
        'url': url, 'mode': 'playwright_capture',
        'message_count': len(messages),
        'messages': messages,
        'text_preview': text[:500],
        'timestamp': ts_str, 'hash': h, 'prev_hash': prev, 'status': 'RAW'
    }
    fname = INFIELD / f'{ts_f}_{eid}.json'
    json.dump(rec, open(fname, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    with open(EVENTS, 'a', encoding='utf-8', newline='') as f:
        csv.writer(f).writerow([
            eid, ts_str, source, 'playwright_capture', 'chat_import',
            'mocka_chat_capture.py', url[:80], 'cli', 'external',
            'in_operation', 'normal', 'A', 'infield/RAW',
            text[:100], prev, 'ingest_complete', 'RAW',
            'local', 'chat_pipeline', 'N/A', 'N/A',
            f'hash={h}|source={source}|msgs={len(messages)}'
        ])
    print(f'[OK] {eid} / {len(messages)}件 → infield/RAW/')
    print(f'[OK] ファイル: {fname.name}')
    return eid

async def login_and_save(source):
    from playwright.async_api import async_playwright
    urls = {
        'chatgpt':    'https://chatgpt.com',
        'claude':     'https://claude.ai',
        'gemini':     'https://gemini.google.com',
        'perplexity': 'https://perplexity.ai',
        'copilot':    'https://copilot.microsoft.com',
    }
    state_file = STATES / f'{source}_state.json'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page    = await context.new_page()
        await page.goto(urls.get(source, 'https://chatgpt.com'))
        print(f'[INFO] {source} にアクセスしました')
        print('[INFO] ブラウザで手動ログインしてください')
        print('[INFO] ログイン完了後 Enter を押してください')
        input()
        await context.storage_state(path=str(state_file))
        print(f'[OK] セッション保存: {state_file}')
        await browser.close()

async def capture(url, source):
    from playwright.async_api import async_playwright
    state_file = STATES / f'{source}_state.json'
    if not state_file.exists():
        print(f'[WARN] セッションファイルなし: {state_file}')
        print(f'[INFO] 先にログインしてください:')
        print(f'       python scripts/mocka_chat_capture.py --login --source {source}')
        sys.exit(1)

    sel = SELECTORS.get(source, SELECTORS['default'])
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(state_file))
        page    = await context.new_page()

        print(f'[INFO] ページ読み込み: {url}')
        await page.goto(url)
        await page.wait_for_timeout(4000)

        # 最上部へスクロールして全履歴ロード
        print('[INFO] スクロール開始（全履歴ロード）')
        last_height = None
        for _ in range(30):
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(1.5)
            height = await page.evaluate('document.body.scrollHeight')
            if height == last_height:
                break
            last_height = height
        print('[INFO] スクロール完了')
        await asyncio.sleep(2)

        # メッセージ抽出
        messages = await page.evaluate(f"""
        () => {{
            const nodes = document.querySelectorAll('{sel}');
            let results = [];
            nodes.forEach((node, i) => {{
                const role = node.getAttribute('data-message-author-role') || 
                             (i % 2 === 0 ? 'user' : 'assistant');
                const text = node.innerText.trim();
                if (text) results.push({{index: i, role: role, content: text}});
            }});
            return results;
        }}
        """)

        print(f'[INFO] 抽出件数: {len(messages)}')
        if not messages:
            # フォールバック: 全テキスト取得
            print('[INFO] セレクタ不一致 → 全テキストで取得')
            text = await page.evaluate('document.body.innerText')
            messages = [{'index': 0, 'role': 'full_page', 'content': text[:50000]}]

        await browser.close()

    eid = save_to_mocka(messages, source, url)
    return eid

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',    help='取得するchatのURL')
    parser.add_argument('--source', help='AI名 (chatgpt/claude/gemini/perplexity/copilot)')
    parser.add_argument('--login',  action='store_true', help='ログインセッション保存モード')
    args = parser.parse_args()

    if args.login:
        if not args.source:
            print('[ERR] --source が必要です')
            sys.exit(1)
        asyncio.run(login_and_save(args.source))
    elif args.url:
        source = args.source or detect_source(args.url)
        print(f'[INFO] source: {source}')
        asyncio.run(capture(args.url, source))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

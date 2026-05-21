#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestra One - Native Messaging Host
Chrome拡張からのリクエストを受け取り、Playwrightで各AIを自律操作する。

Usage: このスクリプトはChromeのNative Messagingプロトコルで起動される。
       直接実行する場合は --test フラグを使用。
"""

import sys
import json
import struct
import asyncio
import logging
from typing import Optional

logging.basicConfig(
    filename='orchestra_one.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    encoding='utf-8',
)

# ── AI ターゲット定義 ─────────────────────────────────────────────────────────

AI_TARGETS = {
    'ChatGPT': {
        'url': 'https://chatgpt.com',
        'input_selector': '#prompt-textarea, div[contenteditable="true"][data-id]',
        'response_selector': '[data-message-author-role="assistant"] .markdown',
        'stop_selector': 'button[aria-label="Stop streaming"]',
        'is_contenteditable': True,
    },
    'Gemini': {
        'url': 'https://gemini.google.com/app',
        'input_selector': '.ql-editor',
        'response_selector': 'model-response .response-container',
        'stop_selector': 'button[aria-label="Stop response"]',
        'is_contenteditable': True,
    },
    'Perplexity': {
        'url': 'https://www.perplexity.ai',
        'input_selector': 'textarea[placeholder]',
        'response_selector': '.prose',
        'stop_selector': 'button[aria-label="Stop"]',
        'is_contenteditable': False,
    },
    'Copilot': {
        'url': 'https://copilot.microsoft.com',
        'input_selector': 'textarea, #userInput',
        'response_selector': '.cib-chat-turn .ac-textBlock',
        'stop_selector': 'button[aria-label="Stop responding"]',
        'is_contenteditable': False,
    },
}

RESPONSE_TIMEOUT_MS = 90_000   # 最大90秒待機
STABLE_WAIT_MS = 2_000         # テキスト安定判定: 2秒変化なし

# ── Native Messaging プロトコル ───────────────────────────────────────────────

def read_message() -> Optional[dict]:
    """Chrome Native Messaging形式でメッセージを読み取る (4バイト長 + JSON)"""
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length or len(raw_length) < 4:
        return None
    length = struct.unpack('<I', raw_length)[0]
    if length == 0 or length > 1_048_576:  # 1MB上限
        return None
    data = sys.stdin.buffer.read(length)
    return json.loads(data.decode('utf-8'))


def send_message(msg: dict) -> None:
    """Chrome Native Messaging形式でメッセージを送信する"""
    encoded = json.dumps(msg, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


# ── Playwright オーケストレーション ──────────────────────────────────────────

async def inject_and_submit(page, config: dict, prompt: str) -> bool:
    """プロンプトを入力欄に注入してEnterで送信する"""
    # 複数セレクターを試す
    selectors = [s.strip() for s in config['input_selector'].split(',')]
    el = None
    for sel in selectors:
        try:
            await page.wait_for_selector(sel, timeout=10_000)
            el = page.locator(sel).first
            break
        except Exception:
            continue

    if not el:
        raise RuntimeError(f"Input element not found: {config['input_selector']}")

    await el.click()
    await el.fill('')  # clear first

    if config.get('is_contenteditable'):
        await el.evaluate(
            '(el, text) => { el.innerHTML = ""; document.execCommand("insertText", false, text); }',
            prompt
        )
    else:
        await el.fill(prompt)

    await page.keyboard.press('Enter')
    return True


async def wait_for_response(page, config: dict) -> str:
    """
    回答完了を待つ:
    1. stop_selector が出現するまで最大10秒待つ (生成開始確認)
    2. stop_selector が消えるまで待つ (生成完了)
    3. response_selector のテキストが2秒安定したら取得
    """
    # 生成開始を待つ (stop ボタン出現)
    try:
        await page.wait_for_selector(config['stop_selector'], timeout=10_000)
    except Exception:
        pass  # すでに完了しているか、検出できなかった場合はそのまま続行

    # 生成完了を待つ (stop ボタン消滅)
    try:
        await page.wait_for_selector(
            config['stop_selector'],
            state='hidden',
            timeout=RESPONSE_TIMEOUT_MS,
        )
    except Exception:
        logging.warning('Stop selector did not disappear within timeout.')

    # テキスト安定待機
    last_text = ''
    stable_count = 0
    for _ in range(60):  # 最大60秒
        await asyncio.sleep(1)
        selectors = [s.strip() for s in config['response_selector'].split(',')]
        text = ''
        for sel in selectors:
            try:
                els = page.locator(sel)
                count = await els.count()
                if count > 0:
                    text = await els.last.inner_text()
                    text = text.strip()
                    if text:
                        break
            except Exception:
                continue

        if text and text == last_text:
            stable_count += 1
            if stable_count >= 2:
                return text
        else:
            stable_count = 0
            last_text = text

    return last_text or 'ERROR: Response capture timed out'


async def run_orchestra(prompt: str) -> dict:
    """全AIにプロンプトを送り、回答を収集して返す"""
    from playwright.async_api import async_playwright

    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(
            locale='ja-JP',
            viewport={'width': 1280, 'height': 800},
        )

        for ai_name, config in AI_TARGETS.items():
            logging.info(f'Starting {ai_name}')
            try:
                page = await context.new_page()
                await page.goto(config['url'], wait_until='domcontentloaded', timeout=30_000)

                # ログイン済みセッションを使うためCookieはブラウザのデフォルト
                await inject_and_submit(page, config, prompt)
                response = await wait_for_response(page, config)
                results[ai_name] = response
                logging.info(f'{ai_name}: captured {len(response)} chars')
            except Exception as e:
                logging.error(f'{ai_name} error: {e}')
                results[ai_name] = f'ERROR: {str(e)}'
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

        await browser.close()

    return results


# ── エントリーポイント ────────────────────────────────────────────────────────

def main():
    if '--test' in sys.argv:
        # ローカルテスト用: 標準入力からJSONを読んで処理
        test_msg = {'type': 'RUN_ORCHESTRA', 'prompt': 'AIとは何ですか？簡潔に答えてください。'}
        logging.info('Test mode: running with sample prompt')
        results = asyncio.run(run_orchestra(test_msg['prompt']))
        send_message({'type': 'ORCHESTRA_RESULT', 'results': results})
        return

    # Native Messaging モード
    msg = read_message()
    if not msg:
        send_message({'type': 'ERROR', 'error': 'Failed to read message'})
        return

    if msg.get('type') == 'RUN_ORCHESTRA':
        try:
            results = asyncio.run(run_orchestra(msg['prompt']))
            send_message({'type': 'ORCHESTRA_RESULT', 'results': results})
        except Exception as e:
            logging.error(f'Fatal error: {e}')
            send_message({'type': 'ERROR', 'error': str(e)})
    elif msg.get('type') == 'PING':
        send_message({'type': 'PONG', 'ok': True})
    else:
        send_message({'type': 'ERROR', 'error': f'Unknown message type: {msg.get("type")}'})


if __name__ == '__main__':
    main()

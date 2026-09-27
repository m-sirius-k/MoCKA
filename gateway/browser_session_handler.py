# -*- coding: utf-8 -*-
"""
browser_session_handler.py - Shared browser session reuse (Orchestra pattern)

Purpose:
  Apply Orchestra's CDP session-reuse method to GPT/Gemini/Perplexity.

Pattern (from orchestra_one_host.py):
  1. Check if CHROME_CDP_ENDPOINT is set
  2. If yes: connect to existing Chrome via CDP (reuse logged-in session)
  3. If no: fall back to new browser (or API)

Design:
  - Minimal: only 50-70 lines
  - No inheritance, single function
  - Reused by adapters_gpt_socket.py, adapters_gemini_socket.py, adapters_perplexity_socket.py
"""

import os
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright


async def query_ai_web_ui(ai_name: str, ai_config: Dict[str, str],
                          prompt: str, max_response_chars: int = 5000) -> Dict[str, Any]:
    """
    Query AI via browser (Playwright) using existing logged-in session.

    Args:
        ai_name: 'ChatGPT', 'Gemini', or 'Perplexity'
        ai_config: {
            'url': 'https://...',
            'input_selector': 'CSS selector for input field',
            'response_selector': 'CSS selector for response',
            'stop_selector': 'CSS selector for stop button'
        }
        prompt: Text to send to AI
        max_response_chars: Max chars to capture

    Returns:
        {
            'status': 'ok' | 'error',
            'response': str (if ok),
            'method': 'cdp' | 'new_browser',
            'error': str (if error),
            'ai_name': ai_name
        }
    """

    async with async_playwright() as p:
        try:
            # STEP 1: Try CDP connection first (reuse existing session)
            cdp_endpoint = os.getenv('CHROME_CDP_ENDPOINT')
            method = None
            context = None
            page = None
            browser = None

            if cdp_endpoint:
                try:
                    browser = await p.chromium.connect_over_cdp(cdp_endpoint)
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                        pages = context.pages
                        page = pages[0] if pages else await context.new_page()
                        method = 'cdp'
                        # No log of credentials or session details
                except Exception as cdp_err:
                    pass  # Fall back to new browser

            # STEP 2: Fall back to new browser if CDP failed
            if method is None:
                browser = await p.chromium.launch(headless=False, slow_mo=50)
                context = await browser.new_context(
                    locale='ja-JP',
                    viewport={'width': 1280, 'height': 800}
                )
                page = await context.new_page()
                method = 'new_browser'

            # STEP 3: Navigate and query
            await page.goto(ai_config['url'], wait_until='domcontentloaded', timeout=30_000)

            # Try to find input field
            selectors = [s.strip() for s in ai_config['input_selector'].split(',')]
            input_el = None
            for sel in selectors:
                try:
                    await page.wait_for_selector(sel, timeout=5_000)
                    input_el = page.locator(sel).first
                    break
                except Exception:
                    continue

            if not input_el:
                return {
                    'status': 'error',
                    'error': f'Input field not found for {ai_name}',
                    'method': method,
                    'ai_name': ai_name,
                }

            # Input and submit
            await input_el.click()
            await input_el.fill('')

            is_contenteditable = ai_config.get('is_contenteditable', False)
            if is_contenteditable:
                await input_el.evaluate(
                    '(el, text) => { el.innerHTML = ""; document.execCommand("insertText", false, text); }',
                    prompt
                )
            else:
                await input_el.fill(prompt)

            await page.keyboard.press('Enter')

            # Wait for response
            try:
                await page.wait_for_selector(ai_config['stop_selector'], timeout=10_000)
            except Exception:
                pass

            try:
                await page.wait_for_selector(
                    ai_config['stop_selector'],
                    state='hidden',
                    timeout=90_000
                )
            except Exception:
                pass

            # Extract response
            response_text = ''
            for _ in range(60):
                await asyncio.sleep(1)
                response_sels = [s.strip() for s in ai_config['response_selector'].split(',')]
                for sel in response_sels:
                    try:
                        els = page.locator(sel)
                        count = await els.count()
                        if count > 0:
                            response_text = await els.last.inner_text()
                            if response_text:
                                break
                    except Exception:
                        continue
                if response_text:
                    break

            # Close page only if new browser, preserve if CDP
            if method == 'new_browser':
                try:
                    await page.close()
                except Exception:
                    pass

            return {
                'status': 'ok',
                'response': response_text[:max_response_chars] if response_text else '',
                'method': method,
                'ai_name': ai_name,
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': f'{ai_name} browser error: {str(e)}',
                'method': method if 'method' in locals() else 'unknown',
                'ai_name': ai_name,
            }

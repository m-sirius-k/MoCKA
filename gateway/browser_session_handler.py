# -*- coding: utf-8 -*-
"""
browser_session_handler.py - Shared browser session reuse (正規統合実装)

Purpose:
  BrowserSessionHandler is a boundary piece that supplies Orchestra's existing
  Browser/Context/Page to AI adapters.

Pattern (from orchestra_one_host.py):
  - Orchestra gets Browser/Context/Page at runtime
  - Pass them to BrowserSessionHandler via function parameters
  - BrowserSessionHandler supplies them to AI adapters
  - NO new browser launch, NO fallback, NO CDP endpoint guessing
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright


# Thread-local storage for Orchestra session handoff
import threading
_session_storage = threading.local()


def set_orchestra_session(browser=None, context=None, page=None):
    """Store Orchestra's browser/context/page for AI adapters to use."""
    _session_storage.browser = browser
    _session_storage.context = context
    _session_storage.page = page


def get_orchestra_session():
    """Retrieve Orchestra's browser/context/page."""
    return (
        getattr(_session_storage, 'browser', None),
        getattr(_session_storage, 'context', None),
        getattr(_session_storage, 'page', None),
    )


async def query_ai_web_ui(ai_name: str, ai_config: Dict[str, str],
                          prompt: str, max_response_chars: int = 5000,
                          page=None, context=None, browser=None) -> Dict[str, Any]:
    """
    Query AI via browser using existing logged-in session from Orchestra.

    Args:
        ai_name: 'ChatGPT', 'Gemini', or 'Perplexity'
        ai_config: Config with url, selectors, etc.
        prompt: Text to send to AI
        max_response_chars: Max chars to capture
        page: Existing Playwright page from Orchestra (optional)
        context: Existing Playwright context from Orchestra (optional)
        browser: Existing Playwright browser from Orchestra (optional)

    Returns:
        {
            'status': 'ok' | 'error',
            'response': str (if ok),
            'method': 'orchestra_session' | 'error',
            'error': str (if error),
            'ai_name': ai_name,
            'session_source': str (where page came from)
        }
    """

    try:
        # STEP 1: Get page from parameter or thread-local storage (from Orchestra)
        if page is None:
            browser, context, page = get_orchestra_session()

        if page is None:
            return {
                'status': 'error',
                'error': f'No existing page provided for {ai_name}. Cannot proceed without Orchestra session.',
                'method': 'error',
                'ai_name': ai_name,
            }

        session_source = 'orchestra_existing_session'
        method = 'orchestra_session'
        logging.info(f'[AI_SOCKET] {ai_name}: Received from Orchestra')
        logging.info(f'[AI_SOCKET] {ai_name}: page_id={id(page)}, browser_id={id(browser)}, context_id={id(context)}')
        logging.info(f'[AI_SOCKET] {ai_name}: new_browser=false, new_context=false, new_page=false')

        # STEP 2: Navigate and query using existing page
        try:
            logging.info(f'[AI_SOCKET] {ai_name}: Navigating to {ai_config["url"]}')
            await page.goto(ai_config['url'], wait_until='domcontentloaded', timeout=30_000)
            logging.info(f'[AI_SOCKET] {ai_name}: Navigation completed')

            # Try to find input field with fallback selectors
            selectors = [s.strip() for s in ai_config['input_selector'].split(',')]

            # Add generic fallback selectors for robustness
            fallback_selectors = [
                'textarea',
                '[contenteditable="true"]',
                'input[type="text"]',
                '[role="textbox"]',
                '[role="combobox"]',
            ]
            all_selectors = selectors + fallback_selectors

            input_el = None
            used_selector = None
            for sel in all_selectors:
                try:
                    # Don't wait for selector, just check if it exists
                    el = page.locator(sel).first
                    count = await el.count()
                    if count > 0:
                        input_el = el
                        used_selector = sel
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

            # Input and submit - use type() for CSP compatibility
            await input_el.click()
            await asyncio.sleep(0.5)

            # Use type() instead of evaluate() to avoid CSP violations (Gemini issue)
            # This works for textarea, input, and contenteditable elements
            await input_el.type(prompt, delay=10)  # Slow typing to simulate human input
            logging.info(f'[AI_SOCKET] {ai_name}: Prompt typed: {len(prompt)} chars')

            await asyncio.sleep(0.5)

            # Submit via Enter key (reliable method)
            await page.keyboard.press('Enter')
            logging.info(f'[AI_SOCKET] {ai_name}: Query submitted via Enter key')

            # Wait for response
            try:
                await page.wait_for_selector(
                    ai_config['stop_selector'],
                    state='hidden',
                    timeout=60_000,
                )
            except Exception:
                pass

            # Extract response
            response_text = ''
            captured_element_info = None
            for attempt in range(60):
                await asyncio.sleep(1)
                response_sels = [s.strip() for s in ai_config['response_selector'].split(',')]
                for sel in response_sels:
                    try:
                        els = page.locator(sel)
                        count = await els.count()
                        if count > 0:
                            response_text = await els.last.inner_text()
                            if response_text and len(response_text.strip()) > 0:
                                logging.info(f'[AI_SOCKET] {ai_name}: Response found at attempt {attempt+1}: {len(response_text)} chars')

                                # Capture detailed DOM info about the captured element
                                try:
                                    elem = els.last
                                    tag = await elem.evaluate('el => el.tagName')
                                    role = await elem.evaluate('el => el.getAttribute("role") || "none"')
                                    cls = await elem.evaluate('el => el.className || "no-class"')
                                    data_attrs = await elem.evaluate('el => Object.entries(el.dataset).map(([k,v]) => `${k}=${v}`).join("|")')
                                    parent_tag = await elem.evaluate('el => el.parentElement?.tagName || "none"')
                                    captured_element_info = {
                                        'tag': tag,
                                        'role': role,
                                        'class': cls,
                                        'data_attrs': data_attrs,
                                        'parent_tag': parent_tag,
                                    }
                                    logging.info(f'[DOM_INSPECT] Captured element: tag={tag}, role={role}, class={cls}, parent={parent_tag}')
                                    logging.info(f'[DOM_INSPECT] Data attrs: {data_attrs}')
                                except Exception as e:
                                    logging.debug(f'[DOM_INSPECT] Could not inspect element: {e}')

                                break
                    except Exception as e:
                        logging.debug(f'[AI_SOCKET] {ai_name}: Response selector error: {e}')
                        continue
                if response_text and len(response_text.strip()) > 0:
                    break

            # After response capture, inspect page structure
            if ai_name == 'ChatGPT' and response_text:
                try:
                    logging.info('[DOM_INSPECT] ===== ChatGPT Page Structure Analysis =====')

                    # Check for user message
                    user_msg_count = await page.locator('[data-message-author-role="user"]').count()
                    logging.info(f'[DOM_INSPECT] User messages found: {user_msg_count}')
                    if user_msg_count > 0:
                        user_text = await page.locator('[data-message-author-role="user"]').last.inner_text()
                        logging.info(f'[DOM_INSPECT] Latest user message: {repr(user_text[:100])}')

                    # Check for assistant message
                    asst_msg_count = await page.locator('[data-message-author-role="assistant"]').count()
                    logging.info(f'[DOM_INSPECT] Assistant messages found: {asst_msg_count}')
                    if asst_msg_count > 0:
                        asst_text = await page.locator('[data-message-author-role="assistant"]').last.inner_text()
                        logging.info(f'[DOM_INSPECT] Latest assistant message: {repr(asst_text[:100])}')

                    # Check for error notifications
                    error_count = await page.locator('[role="alert"], [class*="error"], [class*="Error"]').count()
                    logging.info(f'[DOM_INSPECT] Error/Alert elements found: {error_count}')
                    if error_count > 0:
                        try:
                            error_text = await page.locator('[role="alert"]').first.inner_text()
                            logging.info(f'[DOM_INSPECT] Error message: {repr(error_text)}')
                        except:
                            pass

                    # Check for login requirement
                    login_indicators = await page.locator('[class*="login"], [class*="sign"], [class*="auth"]').count()
                    logging.info(f'[DOM_INSPECT] Login/Auth indicators found: {login_indicators}')

                    # Check page title for clues
                    title = await page.title()
                    logging.info(f'[DOM_INSPECT] Page title: {repr(title)}')

                    logging.info('[DOM_INSPECT] ===== End Analysis =====')
                except Exception as e:
                    logging.error(f'[DOM_INSPECT] Failed to inspect: {e}')

            if not response_text or len(response_text.strip()) == 0:
                logging.warning(f'[AI_SOCKET] {ai_name}: No response captured after 60 attempts')
                # Try to get any text from page to diagnose
                try:
                    page_text = await page.inner_text('body')
                    if 'error' in page_text.lower() or 'went wrong' in page_text.lower():
                        logging.error(f'[AI_SOCKET] {ai_name}: Page contains error text')
                except Exception:
                    pass

            # Don't close page - it belongs to Orchestra session

            return {
                'status': 'ok',
                'response': response_text[:max_response_chars] if response_text else '',
                'method': method,
                'ai_name': ai_name,
                'session_source': session_source,
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': f'{ai_name} browser error: {str(e)}',
                'method': method,
                'ai_name': ai_name,
                'session_source': session_source,
            }

    except Exception as e:
        return {
            'status': 'error',
            'error': f'{ai_name} error: {str(e)}',
            'method': 'error',
            'ai_name': ai_name,
        }

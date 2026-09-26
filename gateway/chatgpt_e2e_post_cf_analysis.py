# -*- coding: utf-8 -*-
"""
ChatGPT E2E - Post-Cloudflare Analysis
Investigate actual ChatGPT page after CF bypass
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CHATGPT_URL = "https://chat.openai.com"

print("\n" + "="*70)
print("ChatGPT E2E - Post-Cloudflare Deep Analysis")
print("="*70)

results = {}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"\n[1] Navigate and wait for Cloudflare...")
        page.goto(CHATGPT_URL, wait_until="domcontentloaded")

        print(f"[2] Wait for Cloudflare challenge (40s)...")
        try:
            page.wait_for_url(lambda url: "cf_chl_rt_tk" not in url and "cloudflare" not in url.lower(), timeout=40000)
            print("  SUCCESS: Cloudflare passed")
        except:
            print("  Timeout: Waiting with extended timeout...")
            time.sleep(10)

        print(f"\n[3] Final URL: {page.url}")

        print(f"\n[4] Wait for content (10s)...")
        time.sleep(10)

        print(f"\n[5] Page title: {page.title()}")
        print(f"\n[6] Page body text (first 200 chars):")
        body = page.query_selector('body')
        if body:
            text = body.inner_text()[:200]
            print(f"     {repr(text)}")

        print(f"\n[7] Search for ALL input-like elements...")

        selectors = [
            'input',
            'textarea',
            'button',
            '[contenteditable]',
            '[role="textbox"]',
            '[role="button"]',
        ]

        for selector in selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"\n  {selector}: found {len(elements)} element(s)")
                for i, elem in enumerate(elements[:3]):  # First 3
                    try:
                        placeholder = elem.get_attribute('placeholder')
                        role = elem.get_attribute('role')
                        aria_label = elem.get_attribute('aria-label')
                        text = elem.inner_text()[:50]
                        print(f"    [{i}] placeholder={placeholder}, role={role}, aria-label={aria-label}, text={repr(text)}")
                    except:
                        pass

        print(f"\n[8] Check for auth indicators...")

        # Look for "Sign out" or logged-in indicators
        signin_btn = page.query_selector('button:has-text("Sign in"), button:has-text("Log in")')
        signout_btn = page.query_selector('button:has-text("Sign out"), button:has-text("Log out")')

        if signin_btn:
            print("  FOUND: Sign in button (user is logged OUT)")
            results["login_status"] = "LOGGED_OUT"
        elif signout_btn:
            print("  FOUND: Sign out button (user is logged IN)")
            results["login_status"] = "LOGGED_IN"
        else:
            print("  UNKNOWN: No sign in/out button visible")
            results["login_status"] = "UNKNOWN"

        print(f"\n[9] Check page readiness...")

        # Try to detect if page is fully loaded
        try:
            # Wait for any dynamic content
            page.wait_for_load_state('networkidle', timeout=5000)
            print("  Page reached network idle")
            results["page_ready"] = True
        except:
            print("  Page did not reach network idle (may still be loading)")
            results["page_ready"] = False

        print(f"\n[10] HTML structure analysis...")
        html = page.content()

        key_sections = [
            ("chat-history", "Chat message area"),
            ("input-area", "Input area"),
            ("message", "Message container"),
            ("textarea", "Text input"),
            ("chatbox", "Chat box"),
        ]

        for keyword, description in key_sections:
            if keyword.lower() in html.lower():
                print(f"  FOUND: {description} (keyword: {keyword})")

        print(f"\n[11] Attempt to interact with page...")

        # Try pressing Tab to see if there's a focusable element
        try:
            page.keyboard.press('Tab')
            focused_elem = page.evaluate("() => document.activeElement.tagName")
            print(f"  After Tab: focused element is {focused_elem}")
        except:
            pass

        print(f"\n[CLEANUP]")
        context.close()
        browser.close()

except Exception as e:
    results["error"] = str(e)
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "="*70)
    print("POST-CLOUDFLARE ANALYSIS SUMMARY")
    print("="*70)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("="*70)

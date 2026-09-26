# -*- coding: utf-8 -*-
"""
ChatGPT Browser E2E - Detailed Analysis
Investigate Cloudflare challenge and login requirements
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

TEST_INPUT = "MOCKA_BROWSER_E2E_TEST_20260923"
CHATGPT_URL = "https://chat.openai.com"
SESSION_ID = f"analysis_{int(time.time())}"

print("\n" + "="*70)
print("ChatGPT Browser E2E - Detailed Analysis")
print("="*70)

results = {}

try:
    print("\n[ANALYSIS] Starting browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Set verbose logging
        page.on("console", lambda msg: print(f"  [JS] {msg.text}"))
        page.on("response", lambda resp: print(f"  [HTTP] {resp.status} {resp.url[:80]}"))

        print(f"\n[STEP 1] Navigate to {CHATGPT_URL}")
        page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=30000)

        print(f"\n[STEP 2] Wait for page stabilization (5s)...")
        time.sleep(5)

        print(f"\n[STEP 3] Current state:")
        print(f"  URL: {page.url}")
        print(f"  Title: {page.title()}")

        print(f"\n[STEP 4] Check for Cloudflare challenge...")
        cf_challenge = page.query_selector('script:has-text("cf_clearance")')
        if cf_challenge:
            print("  FOUND: Cloudflare challenge script present")
            results["cloudflare_challenge"] = True
        else:
            print("  NOT FOUND: No Cloudflare challenge visible")

        print(f"\n[STEP 5] Check for auth/login elements...")

        # Multiple selectors for login indicators
        login_indicators = [
            ('input[type="email"]', 'Email input'),
            ('input[data-testid*="login"]', 'Login input'),
            ('button:has-text("Log in")', 'Login button'),
            ('button:has-text("Sign in")', 'Sign in button'),
            ('[data-testid*="auth"]', 'Auth element'),
            ('textarea[placeholder*="Message"]', 'Chat input (logged in)'),
            ('input[placeholder*="Message"]', 'Chat input (logged in)'),
        ]

        found_elements = {}
        for selector, label in login_indicators:
            elem = page.query_selector(selector)
            if elem:
                found_elements[label] = True
                print(f"  FOUND: {label}")
            else:
                found_elements[label] = False

        results["found_elements"] = found_elements

        print(f"\n[STEP 6] DOM content analysis...")

        # Get page content
        content = page.content()
        content_size = len(content)

        print(f"  Page content size: {content_size} bytes")

        # Check for key phrases
        phrases_to_check = [
            "chatgpt",
            "login",
            "auth",
            "message",
            "cf_challenge",
            "reCAPTCHA",
        ]

        for phrase in phrases_to_check:
            count = content.lower().count(phrase.lower())
            if count > 0:
                print(f"  Found '{phrase}': {count} occurrences")

        print(f"\n[STEP 7] Screenshot content (first 1000 chars of body)...")
        try:
            body = page.query_selector('body')
            if body:
                text = body.inner_text()[:1000]
                print(f"  Body text: {text}")
        except:
            pass

        print(f"\n[STEP 8] Playwright version check...")
        print(f"  Browser type: Chromium")
        print(f"  Context: headless CLI mode")

        print(f"\n[STEP 9] Attempt to wait for auth bypass (30s)...")

        # Try to wait for Cloudflare to clear
        try:
            page.wait_for_function(
                "() => !document.body.innerText.includes('cf_clearance')",
                timeout=30000
            )
            print("  SUCCESS: Cloudflare challenge cleared")
            results["cf_cleared"] = True
        except:
            print("  TIMEOUT: Cloudflare challenge still present after 30s")
            results["cf_cleared"] = False

        print(f"\n[STEP 10] Final URL check...")
        final_url = page.url
        print(f"  Final URL: {final_url}")

        if "cf_chl_rt_tk" in final_url or "cloudflare" in final_url.lower():
            print("  STATUS: Still on Cloudflare challenge")
            results["final_status"] = "BLOCKED_BY_CLOUDFLARE"
        elif "login" in final_url.lower() or "auth" in final_url.lower():
            print("  STATUS: On login/auth page")
            results["final_status"] = "ON_LOGIN_PAGE"
        elif "chat" in final_url.lower():
            print("  STATUS: On ChatGPT chat page")
            results["final_status"] = "ON_CHATGPT_PAGE"
        else:
            print("  STATUS: Unknown page")
            results["final_status"] = "UNKNOWN"

        print(f"\n[CLEANUP]")
        context.close()
        browser.close()
        print("  Browser closed")

except Exception as e:
    results["error"] = str(e)
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("\n" + "="*70)

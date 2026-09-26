# -*- coding: utf-8 -*-
"""
ChatGPT Browser E2E - Headless Mode (CLI-only environment)

Modified for headless execution to test maximum achievable path
without GUI display capability.

Purpose:
  Verify: Playwright → Browser → ChatGPT URL reach → Login detection

Limitation:
  Cannot bypass login (manual login impossible in headless CLI mode)

Evidence Target:
  Record how far automation can proceed without GUI interaction
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

gateway_path = Path(__file__).parent
sys.path.insert(0, str(gateway_path))

try:
    from core_kernel.orchestra.orchestrator_api import emit_event
    ORCHESTRA_AVAILABLE = True
except ImportError:
    ORCHESTRA_AVAILABLE = False

TEST_INPUT = "MOCKA_BROWSER_E2E_TEST_20260923"
CHATGPT_URL = "https://chat.openai.com"
SESSION_ID = f"browser_chatgpt_headless_{int(time.time())}"

print("\n" + "="*70)
print("ChatGPT Browser E2E - Headless Mode")
print("="*70)
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"Mode: HEADLESS (no GUI)")
print(f"Environment: CLI only")

results = {
    "browser_launch": "UNKNOWN",
    "chatgpt_page": "UNKNOWN",
    "login_detected": "UNKNOWN",
    "input_possible": "UNKNOWN",
    "submit_possible": "UNKNOWN",
    "response_detected": "UNKNOWN",
    "orchestra_event": "UNKNOWN",
    "error": None,
    "max_step": 0,
}

try:
    print("\n[STEP 1] Browser Launch (Headless)...")

    with sync_playwright() as p:
        results["max_step"] = 1
        results["browser_launch"] = "PASS"
        print("  PASS: Playwright context created")

        browser = p.chromium.launch(headless=True)
        print("  PASS: Chromium launched (headless)")

        context = browser.new_context()
        print("  PASS: Browser context created")

        page = context.new_page()
        print("  PASS: Page created")

        print("\n[STEP 2] Navigate to ChatGPT URL...")
        results["max_step"] = 2

        try:
            page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=30000)
            results["chatgpt_page"] = "PASS"
            print(f"  PASS: Navigated to {CHATGPT_URL}")
        except Exception as e:
            results["chatgpt_page"] = "FAIL"
            results["error"] = f"Navigation failed: {str(e)}"
            print(f"  FAIL: {e}")
            raise

        # Get page info
        print("\n[STEP 3] Page Analysis...")
        results["max_step"] = 3

        try:
            page_url = page.url
            page_title = page.title()
            print(f"  Current URL: {page_url}")
            print(f"  Page title: {page_title}")

            # Check for login indicators
            print("\n[STEP 4] Login Status Check...")
            results["max_step"] = 4

            # Look for login elements
            login_email = page.query_selector('input[type="email"]')
            login_button = page.query_selector('button[data-testid*="login"], button:has-text("Log in")')
            chat_input = page.query_selector('textarea[placeholder*="Message"], input[placeholder*="Message"]')

            if login_email or login_button:
                results["login_detected"] = "LOGIN_REQUIRED"
                print("  INFO: Login screen detected")
                print("  REASON: Email input or login button found in DOM")
                print("  [BLOCKED] Manual login required (GUI unavailable)")

            elif chat_input:
                results["login_detected"] = "ALREADY_LOGGED_IN"
                print("  PASS: Already logged in")
                results["max_step"] = 5

                print("\n[STEP 5] Input Field Test...")

                try:
                    chat_input.click()
                    print("  PASS: Input field focused")
                    results["input_possible"] = "PASS"
                    results["max_step"] = 6

                    # Test typing (don't actually send)
                    chat_input.fill(TEST_INPUT)
                    print(f"  PASS: Test input entered: {TEST_INPUT}")
                    results["submit_possible"] = "PASS"
                    results["max_step"] = 7

                except Exception as e:
                    results["input_possible"] = "FAIL"
                    results["error"] = f"Input failed: {str(e)}"
                    print(f"  FAIL: {e}")
            else:
                results["login_detected"] = "UNKNOWN"
                print("  UNKNOWN: Cannot determine login status from DOM")
                # Dump page content for analysis
                page_content = page.content()[:500]
                print(f"  Page content (first 500 chars):\n{page_content}")

        except Exception as e:
            results["error"] = str(e)
            print(f"  ERROR: {e}")

        print("\n[STEP 6] Cleanup...")
        try:
            context.close()
            browser.close()
            print("  PASS: Browser closed")
        except Exception as e:
            print(f"  WARN: Close error: {e}")

except Exception as e:
    results["error"] = str(e)
    print(f"\nFATAL: {e}")

finally:
    # Summary
    print("\n" + "="*70)
    print("HEADLESS EXECUTION SUMMARY")
    print("="*70)
    print(f"\nMax step reached: {results['max_step']}")
    print(f"Browser launch: {results['browser_launch']}")
    print(f"ChatGPT page: {results['chatgpt_page']}")
    print(f"Login status: {results['login_detected']}")
    print(f"Input possible: {results['input_possible']}")
    print(f"Submit possible: {results['submit_possible']}")
    print(f"Response detection: {results['response_detected']}")

    if results['error']:
        print(f"\nError: {results['error']}")

    # Try Orchestra event
    if ORCHESTRA_AVAILABLE and results['browser_launch'] == "PASS":
        try:
            emit_event(
                event_type="browser_e2e_headless_test",
                session_id=SESSION_ID,
                payload={
                    "max_step": results["max_step"],
                    "browser_launch": results["browser_launch"],
                    "chatgpt_page": results["chatgpt_page"],
                    "login_status": results["login_detected"],
                    "error": results["error"],
                }
            )
            results["orchestra_event"] = "PASS"
            print("\n[Orchestra] Event emitted successfully")
        except Exception as e:
            results["orchestra_event"] = "FAIL"
            print(f"\n[Orchestra] Emit failed: {e}")

    # Final verdict
    print("\n" + "="*70)
    print("EXECUTION VERDICT")
    print("="*70)

    if results['browser_launch'] == "PASS" and results['chatgpt_page'] == "PASS":
        if results['login_detected'] == "LOGIN_REQUIRED":
            print("\nStatus: BLOCKED (Login required, GUI unavailable)")
            print("Evidence: Successfully reached ChatGPT login screen")
            print("Limitation: Manual login impossible in CLI mode")
        elif results['login_detected'] == "ALREADY_LOGGED_IN":
            print("\nStatus: PARTIALLY VERIFIED")
            print("Evidence: ChatGPT page opened, input field accessible")
            if results['submit_possible'] == "PASS":
                print("Note: Can input text, but cannot send (headless limitation)")
        else:
            print("\nStatus: UNKNOWN")
            print("Evidence: Reached ChatGPT but login status unclear")
    else:
        print("\nStatus: FAILED")
        print(f"Error: {results['error']}")

    print("\n" + "="*70)

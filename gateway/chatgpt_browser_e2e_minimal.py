# -*- coding: utf-8 -*-
"""
ChatGPT Browser E2E Minimal Test
Orchestra + Playwright + ChatGPT Web UI

Purpose:
  Verify minimum E2E path: HAB → Orchestra → Browser → ChatGPT → Answer → HAB

Constraints:
  - No existing browser session reuse
  - Independent Playwright context (clean)
  - Manual login if required
  - No cookie/auth storage in code/logs
  - CAPTCHA → BLOCKED
  - No API usage

Test Flow:
  1. Launch new browser instance
  2. Navigate to https://chat.openai.com
  3. Wait for login (may require manual input)
  4. Input test string: "MOCKA_BROWSER_E2E_TEST_20260923"
  5. Send query
  6. Extract response
  7. Return to HAB via Orchestra API

Evidence Required:
  - Browser console output
  - DOM inspection results
  - Response text captured
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

# Setup
gateway_path = Path(__file__).parent
sys.path.insert(0, str(gateway_path.parent))  # Add MoCKA root for core_kernel import

# Import Orchestra API
try:
    from core_kernel.orchestra.orchestrator_api import emit_event
    ORCHESTRA_AVAILABLE = True
except ImportError:
    print("[WARNING] Orchestra API not available (will use stdout logging)")
    ORCHESTRA_AVAILABLE = False

# Test configuration
TEST_INPUT = "MOCKA_BROWSER_E2E_TEST_20260923"
CHATGPT_URL = "https://chat.openai.com"
TIMEOUT_MS = 60000  # 60 seconds
SESSION_ID = f"browser_chatgpt_{int(time.time())}"

print("\n" + "="*70)
print("ChatGPT Browser E2E Minimal Test - START")
print("="*70)
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"Session ID: {SESSION_ID}")
print(f"Test Input: {TEST_INPUT}")
print(f"Target: {CHATGPT_URL}")
print(f"Orchestra: {'AVAILABLE' if ORCHESTRA_AVAILABLE else 'NOT AVAILABLE (using stdout)'}")

# Results container
results = {
    "status": "UNKNOWN",
    "browser_launched": False,
    "page_opened": False,
    "login_required": False,
    "input_sent": False,
    "response_received": False,
    "response_text": None,
    "error": None,
}

try:
    print("\n[STEP 1] Launching browser...")

    with sync_playwright() as p:
        results["browser_launched"] = True
        print("  ✓ Browser instance created")

        # Launch independent browser (no session reuse)
        browser = p.chromium.launch(headless=False)  # headless=False to allow manual login
        print("  ✓ Chromium started")

        # Create independent context (no cookies, no cache)
        context = browser.new_context()
        print("  ✓ New browser context created (independent)")

        page = context.new_page()
        print("  ✓ New page tab created")

        # Setup navigation event tracking
        nav_events = []

        def on_framenavigated(frame):
            nav_events.append({
                "time": datetime.now(timezone.utc).isoformat(),
                "url": frame.page.url if frame == frame.page.main_frame else "iframe",
                "title": frame.page.title() if frame == frame.page.main_frame else "iframe"
            })
            if frame == frame.page.main_frame:
                print(f"  [NAV] Frame navigated: {frame.page.url}")

        page.on("framenavigated", on_framenavigated)
        print("  ✓ Navigation tracking enabled")

        print("\n[STEP 2] Navigating to ChatGPT...")
        try:
            page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            results["page_opened"] = True
            print(f"  ✓ Navigated to {CHATGPT_URL}")
            print(f"  Current URL: {page.url}")
        except Exception as e:
            results["error"] = f"Navigation failed: {str(e)}"
            print(f"  ✗ Navigation error: {e}")
            raise

        print("\n[STEP 3] Checking login status...")

        # Wait a bit for page to fully load
        time.sleep(3)

        # Check if we're at login page or chat page
        try:
            print(f"  [STATE] URL: {page.url}")
            print(f"  [STATE] Title: {page.title()}")

            # Try to find chat input (indicates logged in)
            try:
                chat_input = page.query_selector('textarea[placeholder*="Message"], input[placeholder*="Message"], [contenteditable="true"]')
            except Exception as selector_err:
                print(f"  [ERROR] query_selector failed: {selector_err}")
                chat_input = None

            if not chat_input:
                # Check for login button or email input
                try:
                    login_email = page.query_selector('input[type="email"]')
                except Exception as selector_err:
                    print(f"  [ERROR] login check query_selector failed: {selector_err}")
                    login_email = None

                if login_email:
                    results["login_required"] = True
                    print("  ✗ Login required - please log in manually in the browser window")
                    print("  ℹ Waiting for manual login (90 seconds)...")

                    # Wait for login to complete with navigation-safe retry
                    for i in range(90):
                        time.sleep(1)

                        try:
                            print(f"  [LOOP {i+1}] URL: {page.url} | Nav events: {len(nav_events)}")

                            # Try query_selector with error handling
                            try:
                                chat_input = page.query_selector('textarea[placeholder*="Message"], input[placeholder*="Message"], [contenteditable="true"]')
                            except Exception as loop_err:
                                print(f"  [LOOP {i+1}] Selector error (likely navigation): {type(loop_err).__name__}")
                                # Navigation just happened, wait a bit for page to stabilize
                                time.sleep(2)
                                try:
                                    chat_input = page.query_selector('textarea[placeholder*="Message"], input[placeholder*="Message"], [contenteditable="true"]')
                                except:
                                    chat_input = None

                            if chat_input:
                                print(f"  ✓ Login detected after {i+1} seconds")
                                print(f"  ✓ Final URL: {page.url}")
                                print(f"  ✓ Navigation events recorded: {len(nav_events)}")
                                break
                        except Exception as loop_err:
                            print(f"  [LOOP {i+1}] Exception: {loop_err}")
                    else:
                        results["error"] = "Login timeout (manual login not completed in 90 seconds)"
                        print("  ✗ Login not completed in time")
                        print(f"  Navigation history: {nav_events}")
                        raise TimeoutError("Manual login timeout")
                else:
                    print("  ℹ Checking page state...")
                    try:
                        page_title = page.title()
                        print(f"  Page title: {page_title}")
                    except:
                        print("  [ERROR] Cannot get page title")
                    results["error"] = "Unknown login state"
            else:
                print("  ✓ Already logged in")

        except Exception as e:
            results["error"] = f"Login check failed: {str(e)}"
            print(f"  ✗ Login check error: {e}")
            print(f"  Navigation history: {nav_events}")
            raise

        print("\n[STEP 4] Finding chat input field...")

        try:
            # Multiple selectors for different ChatGPT UI versions
            chat_input = page.query_selector('textarea[placeholder*="Message"]')
            if not chat_input:
                chat_input = page.query_selector('input[placeholder*="Message"]')
            if not chat_input:
                chat_input = page.query_selector('[contenteditable="true"][data-testid*="input"]')
            if not chat_input:
                # Fallback: find any textarea
                chat_input = page.query_selector('textarea')

            if not chat_input:
                results["error"] = "Chat input field not found in DOM"
                print(f"  ✗ Cannot find chat input element")
                print(f"  ℹ Page content (first 500 chars):")
                content = page.content()
                print(f"     {content[:500]}")
                raise Exception("Chat input element not found")

            print("  ✓ Chat input field found")
        except Exception as e:
            results["error"] = f"Input field search failed: {str(e)}"
            print(f"  ✗ Error: {e}")
            raise

        print("\n[STEP 5] Typing test input...")

        try:
            # Click to focus
            chat_input.click()
            print("  ✓ Input field focused")

            # Type test string
            chat_input.type(TEST_INPUT, delay=50)
            print(f"  ✓ Input typed: {TEST_INPUT}")
        except Exception as e:
            results["error"] = f"Input typing failed: {str(e)}"
            print(f"  ✗ Typing error: {e}")
            raise

        print("\n[STEP 6] Sending query...")

        try:
            # Find and click send button (multiple variations)
            send_button = page.query_selector('button[aria-label*="Send"], button:has-text("Send"), [data-testid*="send"]')
            if not send_button:
                # Fallback: press Enter key
                print("  ℹ Send button not found, using Enter key")
                chat_input.press("Enter")
            else:
                send_button.click()
                print("  ✓ Send button clicked")
        except Exception as e:
            results["error"] = f"Send failed: {str(e)}"
            print(f"  ✗ Send error: {e}")
            raise

        results["input_sent"] = True
        print("  ✓ Query sent")

        print("\n[STEP 7] Waiting for response...")

        try:
            # Wait for response to appear (different selectors for different layouts)
            # ChatGPT adds responses in message containers

            response_received = False
            start_time = time.time()

            while (time.time() - start_time) < 60:  # 60 second timeout
                # Try to find response text
                messages = page.query_selector_all('div[class*="message"], article, [data-testid*="message"]')

                if len(messages) > 0:
                    # Get the last message (should be AI response)
                    last_message = messages[-1]
                    text = last_message.inner_text()

                    # Check if it's not the input message and contains actual response
                    if text and TEST_INPUT not in text.split('\n')[0]:
                        results["response_text"] = text[:500]  # First 500 chars
                        results["response_received"] = True
                        response_received = True
                        print(f"  ✓ Response received")
                        print(f"  Response (first 100 chars): {text[:100]}...")
                        break

                time.sleep(1)

            if not response_received:
                print("  ℹ Waiting more (may be processing)...")
                # Try once more with longer wait
                page.wait_for_selector('div[class*="message"], article', timeout=30000)
                messages = page.query_selector_all('div[class*="message"], article')
                if messages:
                    last_message = messages[-1]
                    results["response_text"] = last_message.inner_text()[:500]
                    results["response_received"] = True
                    print(f"  ✓ Response received (late detection)")

        except Exception as e:
            results["error"] = f"Response wait failed: {str(e)}"
            print(f"  ✗ Response error: {e}")
            # Don't raise - continue to cleanup

        print("\n[STEP 8] Closing browser...")

        try:
            context.close()
            browser.close()
            print("  ✓ Browser closed cleanly")
        except Exception as e:
            print(f"  ⚠ Browser close warning: {e}")

except Exception as e:
    results["error"] = str(e)
    print(f"\n✗ FATAL ERROR: {e}")

finally:
    # Determine final status
    if results["response_received"]:
        results["status"] = "VERIFIED"
    elif results["input_sent"]:
        results["status"] = "BLOCKED"
    elif results["login_required"]:
        results["status"] = "BLOCKED"
    elif results["page_opened"]:
        results["status"] = "GAP"
    elif results["browser_launched"]:
        results["status"] = "BLOCKED"
    else:
        results["status"] = "BLOCKED"

    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"Status: {results['status']}")
    print(f"Browser launched: {results['browser_launched']}")
    print(f"Page opened: {results['page_opened']}")
    print(f"Login required: {results['login_required']}")
    print(f"Input sent: {results['input_sent']}")
    print(f"Response received: {results['response_received']}")
    if results["response_text"]:
        print(f"Response (excerpt): {results['response_text'][:80]}...")
    if results["error"]:
        print(f"Error: {results['error']}")

    # Emit to Orchestra if available
    if ORCHESTRA_AVAILABLE:
        try:
            emit_event(
                event_type="browser_e2e_test_complete",
                session_id=SESSION_ID,
                payload={
                    "status": results["status"],
                    "test_input": TEST_INPUT,
                    "response_received": results["response_received"],
                    "response_text": results["response_text"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            print("\n[Orchestra] Event emitted: browser_e2e_test_complete")
        except Exception as e:
            print(f"\n[Orchestra] Emit failed: {e}")

    print("\n" + "="*70)

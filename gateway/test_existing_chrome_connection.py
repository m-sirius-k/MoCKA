#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Connect to Existing Chrome Session via CDP

Purpose:
  Verify that Playwright can connect to an already-running Chrome instance
  with logged-in sessions (ChatGPT, Gemini, Perplexity).

Prerequisites:
  1. Chrome running with: chrome.exe --remote-debugging-port=9222
  2. ChatGPT tab logged in
  3. Gemini tab logged in
  4. Perplexity tab logged in

Execution:
  - Detect Chrome running on CDP port 9222
  - Connect via Playwright connect_over_cdp()
  - List existing pages/sessions
  - Verify login state
  - Optionally: Send prompt to ChatGPT
"""

import sys
import asyncio
import subprocess
from pathlib import Path

print("=" * 80)
print("EXISTING CHROME CONNECTION TEST")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Check if Chrome is running on CDP port
# ============================================================================
print("[STEP 1] Check Chrome DevTools Protocol (CDP) Availability")
print("-" * 80)

cdp_endpoint = "ws://localhost:9222"

try:
    import requests

    # Try to query Chrome's DevTools protocol endpoint
    response = requests.get("http://localhost:9222/json", timeout=5)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Chrome is running on CDP port 9222")
        print(f"  Browser version: {data[0].get('version', 'unknown')[:60]}")
        print(f"  WebSocket endpoint: {cdp_endpoint}")
        chrome_available = True
    else:
        print(f"✗ Chrome CDPport responded but with status: {response.status_code}")
        chrome_available = False

except requests.exceptions.ConnectionError:
    print(f"✗ Chrome NOT running on port 9222")
    print()
    print("  To enable CDP debugging, launch Chrome with:")
    print(f"  chrome.exe --remote-debugging-port=9222")
    print()
    chrome_available = False

except Exception as e:
    print(f"✗ Error checking CDP: {e}")
    chrome_available = False

print()

if not chrome_available:
    print("[STATUS] Chrome not available via CDP")
    print()
    print("To test existing Chrome connection:")
    print("  1. Launch Chrome with debugging enabled:")
    print("     chrome.exe --remote-debugging-port=9222")
    print()
    print("  2. Open and login to:")
    print("     - ChatGPT (https://chatgpt.com)")
    print("     - Gemini (https://gemini.google.com)")
    print("     - Perplexity (https://perplexity.ai)")
    print()
    print("  3. Then run this test again")
    print()
    sys.exit(1)

print()

# ============================================================================
# STEP 2: Connect to existing Chrome via CDP
# ============================================================================
print("[STEP 2] Connect to Existing Chrome via CDP")
print("-" * 80)

async def test_existing_chrome():
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            print("Connecting to existing Chrome instance...")
            print(f"  Endpoint: {cdp_endpoint}")

            try:
                # Connect to existing browser
                browser = await p.chromium.connect_over_cdp(cdp_endpoint)
                print("✓ Connected successfully!")

                # List existing contexts and pages
                print()
                print("Existing browser contexts and pages:")

                # Get all contexts
                contexts = browser.contexts
                print(f"  Total contexts: {len(contexts)}")

                # Get all pages from all contexts
                all_pages = []
                for ctx_idx, context in enumerate(contexts):
                    pages = context.pages
                    all_pages.extend(pages)
                    print(f"  Context {ctx_idx}: {len(pages)} page(s)")

                    for page_idx, page in enumerate(pages):
                        url = page.url
                        title = await page.title()
                        print(f"    Page {page_idx}: {title[:50]}")
                        print(f"      URL: {url[:70]}")

                print()

                # ============================================================
                # STEP 3: Identify logged-in pages
                # ============================================================
                print("[STEP 3] Identify Logged-in Sessions")
                print("-" * 80)

                chat_gpt_page = None
                gemini_page = None
                perplexity_page = None

                for page in all_pages:
                    url = page.url.lower()

                    if 'chatgpt.com' in url or 'chat.openai.com' in url:
                        chat_gpt_page = page
                        print("✓ ChatGPT page found")
                        print(f"  URL: {url[:70]}")

                    elif 'gemini.google.com' in url:
                        gemini_page = page
                        print("✓ Gemini page found")
                        print(f"  URL: {url[:70]}")

                    elif 'perplexity.ai' in url:
                        perplexity_page = page
                        print("✓ Perplexity page found")
                        print(f"  URL: {url[:70]}")

                print()

                # ============================================================
                # STEP 4: Verify login state
                # ============================================================
                if chat_gpt_page:
                    print("[STEP 4] Verify ChatGPT Login State")
                    print("-" * 80)

                    # Check if input element is visible (indicates logged-in state)
                    try:
                        input_element = chat_gpt_page.locator(
                            '#prompt-textarea, div[contenteditable="true"][data-id]'
                        )
                        is_visible = await input_element.is_visible(timeout=2000)

                        if is_visible:
                            print("✓ ChatGPT input element detected (logged-in)")
                        else:
                            print("⚠ ChatGPT input element not visible")

                    except Exception as e:
                        print(f"⚠ Could not verify login: {e}")

                    print()

                # ============================================================
                # STEP 5: Optional - Send a prompt to ChatGPT
                # ============================================================
                if chat_gpt_page:
                    print("[STEP 5] Send Prompt to ChatGPT (Optional)")
                    print("-" * 80)

                    try:
                        # Find and focus input element
                        input_element = chat_gpt_page.locator(
                            '#prompt-textarea, div[contenteditable="true"][data-id]'
                        )

                        # Check if it's visible
                        is_visible = await input_element.is_visible(timeout=2000)

                        if is_visible:
                            # Click and type prompt
                            await input_element.click()
                            await input_element.type("Test prompt from Orchestra via existing Chrome session")

                            print("✓ Prompt injected into ChatGPT input")
                            print()
                            print("  (Not sending - user must click Send manually)")
                            print("  This proves we can control the existing session!")

                        else:
                            print("⚠ ChatGPT input not visible - cannot inject prompt")

                    except Exception as e:
                        print(f"⚠ Could not inject prompt: {e}")

                    print()

                # ============================================================
                # Final Status
                # ============================================================
                print("=" * 80)
                print("[RESULT] Existing Chrome Connection Test")
                print("=" * 80)
                print()

                if chat_gpt_page or gemini_page or perplexity_page:
                    print("✅ VERIFIED: Can connect to existing Chrome sessions")
                    print()
                    print("Connected sessions:")
                    if chat_gpt_page:
                        print("  ✓ ChatGPT")
                    if gemini_page:
                        print("  ✓ Gemini")
                    if perplexity_page:
                        print("  ✓ Perplexity")
                    print()
                    print("This confirms Orchestra CAN use existing Chrome sessions!")
                    print()
                    print("Next: Modify orchestra_one_host.py to accept CDP endpoint")
                    print("      and use connect_over_cdp() instead of launch()")

                else:
                    print("⚠ No recognized AI pages found in existing Chrome")
                    print("  Make sure ChatGPT/Gemini/Perplexity tabs are open")

                await browser.close()

            except Exception as e:
                print(f"✗ Failed to connect: {e}")
                print()
                print("Troubleshooting:")
                print("  1. Verify Chrome is running with --remote-debugging-port=9222")
                print("  2. Check no other Chrome instance is using port 9222")
                print("  3. Firewall may be blocking localhost:9222")

    except ImportError:
        print("✗ Playwright not available")
        sys.exit(1)

try:
    asyncio.run(test_existing_chrome())
except KeyboardInterrupt:
    print("\n[Interrupted]")
    sys.exit(0)
except Exception as e:
    print(f"[Error] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

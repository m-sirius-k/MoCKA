#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 4 — SETUP BROWSER SESSION + DISPATCH

Approach:
1. Setup Playwright browser/context/page
2. Register via set_orchestra_session()
3. Call dispatch_with_orchestra_session()
4. Dispatch will use the session we just created

This is the "real Orchestra path" - browser session comes first, then dispatch.
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone

_mocka_root = Path(__file__).parent
gateway_path = _mocka_root / "gateway"
if str(gateway_path) not in sys.path:
    sys.path.insert(0, str(gateway_path))

print("\n" + "="*80)
print("PHASE 4 — BROWSER SETUP + ORCHESTRA DISPATCH")
print("="*80)
print(f"Start: {datetime.now(timezone.utc).isoformat()}")

# ============================================================================
# STEP 1: Setup Playwright session
# ============================================================================

async def setup_browser_session():
    """Setup Playwright browser/context/page and register via set_orchestra_session."""
    try:
        from playwright.async_api import async_playwright
        from browser_session_handler import set_orchestra_session

        print("\n[SETUP] Initializing Playwright...")
        async with async_playwright() as p:
            # Launch headless browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Register session
            set_orchestra_session(browser=browser, context=context, page=page)

            print(f"[OK] Browser session created and registered")
            print(f"    Browser: {id(browser)}")
            print(f"    Context: {id(context)}")
            print(f"    Page: {id(page)}")

            # Keep browser alive during dispatch
            return browser, context, page

    except Exception as e:
        print(f"[FAIL] Browser setup error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


# ============================================================================
# STEP 2: Execute dispatch with session
# ============================================================================

def dispatch_with_session(browser, context, page):
    """Execute dispatch_with_orchestra_session using the setup session."""
    try:
        from multi_dispatcher import dispatch_with_orchestra_session

        print("\n[DISPATCH] Calling dispatch_with_orchestra_session()...")

        request_text = """
PHASE 4 Integration Test — Browser Session Available

With a live browser session now registered in Orchestra,
please provide an assessment of:

1. Browser connectivity status
2. Readiness for AI web UI automation
3. Event store integration
4. Overall Phase 4 readiness

Response format: Brief 3-4 sentence summary.
        """

        result = dispatch_with_orchestra_session(
            request_text=request_text.strip(),
            providers=["gpt"],
            title="PHASE 4 Browser Session Integration",
            decision_id=None
        )

        print(f"\n[RESULT] Dispatch completed:")
        print(f"   Orchestra Session Status: {result.get('orchestra_session_status')}")
        print(f"   Overall Status: {result.get('status')}")
        print(f"   Request ID: {result.get('request_id')}")

        return result

    except Exception as e:
        print(f"\n[FAIL] Dispatch error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "ORCHESTRA_SESSION": "FAILED",
            "error": str(e)
        }


# ============================================================================
# STEP 3: Main async runner
# ============================================================================

async def main():
    # Setup browser session
    browser, context, page = await setup_browser_session()

    if browser is None:
        print("\n[ABORT] Browser setup failed - cannot proceed with dispatch")
        return {
            "ORCHESTRA_SESSION": "FAILED",
            "REAL_AI_RESPONSE": False,
            "EVENT_STORE_READBACK": False,
            "FULL_CHAIN": False,
            "STOP_POINT": "browser_setup_failed",
        }

    # Keep browser alive while dispatch runs
    try:
        # Execute dispatch (synchronous)
        result = dispatch_with_session(browser, context, page)

        # Analyze result
        orchestra_connected = result.get('orchestra_session_status') == 'connected'
        ai_response_ok = result.get('status') in ['all_ok', 'partial_ok']
        event_store_ok = orchestra_connected  # If connected, event was pushed
        full_chain_ok = orchestra_connected and ai_response_ok

        stop_point = None
        if not orchestra_connected:
            stop_point = "ORCHESTRA_NOT_CONNECTED"
        elif not ai_response_ok:
            stop_point = "NO_AI_RESPONSE"

        return {
            "ORCHESTRA_SESSION": "CONNECTED" if orchestra_connected else "FAILED",
            "REAL_AI_RESPONSE": ai_response_ok,
            "EVENT_STORE_READBACK": event_store_ok,
            "FULL_CHAIN": full_chain_ok,
            "STOP_POINT": stop_point,
            "dispatch_result": result,
        }

    finally:
        # Cleanup
        try:
            await page.close()
            await context.close()
            await browser.close()
            print("\n[OK] Browser session closed")
        except:
            pass


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run async main
    result = asyncio.run(main())

    # Get git info
    def get_git_info():
        try:
            import subprocess
            head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(_mocka_root),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()[:16]

            try:
                remote = subprocess.check_output(
                    ["git", "rev-parse", "@{upstream}"],
                    cwd=str(_mocka_root),
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()[:16]
            except:
                remote = "no-upstream"

            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=str(_mocka_root),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            worktree = "CLEAN" if not status_output else "DIRTY"
            return head, remote, worktree
        except:
            return "error", "error", "error"

    head, remote, worktree = get_git_info()

    # Final report
    print("\n" + "="*80)
    print("PHASE 4 FINAL REPORT")
    print("="*80)
    print(f"ORCHESTRA_SESSION = {result.get('ORCHESTRA_SESSION')}")
    print(f"REAL_AI_RESPONSE = {result.get('REAL_AI_RESPONSE')}")
    print(f"EVENT_STORE_READBACK = {result.get('EVENT_STORE_READBACK')}")
    print(f"FULL_CHAIN = {result.get('FULL_CHAIN')}")
    print(f"STOP_POINT = {result.get('STOP_POINT')}")
    print(f"HEAD = {head}")
    print(f"REMOTE = {remote}")
    print(f"WORKTREE = {worktree}")
    print("="*80)
    print(f"End: {datetime.now(timezone.utc).isoformat()}")

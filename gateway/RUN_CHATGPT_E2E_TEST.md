# ChatGPT Browser E2E Minimal Test - Execution Guide

**Date:** 2026-09-23  
**Objective:** Verify minimum E2E path: HAB → Orchestra → Browser → ChatGPT → Answer → HAB

---

## Prerequisites

✓ Playwright 1.57.0 (already installed)  
✓ Python 3.8+  
✓ Windows 11 with Chromium available  
✓ Internet connectivity to https://chat.openai.com  
✓ ChatGPT account (or ability to log in)

---

## How to Run

### Step 1: Open Terminal

```bash
cd C:\Users\sirok\MoCKA\gateway
```

### Step 2: Execute Test Script

```bash
python3 chatgpt_browser_e2e_minimal.py
```

### Step 3: Watch Browser

A new Chromium browser window will open showing https://chat.openai.com

**If login is required:**
- You will see: `Waiting for manual login (30 seconds)...`
- **Manually log in** in the browser window
- The script will detect login completion and continue automatically
- You have 30 seconds to log in

**If login is not required:**
- The script will proceed directly to input

### Step 4: Observe Test Execution

The script will:
1. ✓ Find the chat input field
2. ✓ Type: `MOCKA_BROWSER_E2E_TEST_20260923`
3. ✓ Click Send (or press Enter)
4. ✓ Wait for ChatGPT response (up to 60 seconds)
5. ✓ Extract response text
6. ✓ Close browser
7. ✓ Report results

---

## Expected Output Examples

### SUCCESS CASE (VERIFIED)
```
[STEP 1] Launching browser...
  ✓ Browser instance created
  ✓ Chromium started
  ✓ New browser context created (independent)
  ✓ New page tab created

[STEP 2] Navigating to ChatGPT...
  ✓ Navigated to https://chat.openai.com

[STEP 3] Checking login status...
  ✓ Already logged in

[STEP 4] Finding chat input field...
  ✓ Chat input field found

[STEP 5] Typing test input...
  ✓ Input field focused
  ✓ Input typed: MOCKA_BROWSER_E2E_TEST_20260923

[STEP 6] Sending query...
  ✓ Send button clicked

[STEP 7] Waiting for response...
  ✓ Response received
  Response (first 100 chars): I notice you've sent a test string. This appears to be a test message...

[STEP 8] Closing browser...
  ✓ Browser closed cleanly

======================================================================
RESULTS SUMMARY
======================================================================
Status: VERIFIED
Browser launched: True
Page opened: True
Login required: False
Input sent: True
Response received: True
Response (excerpt): I notice you've sent a test string. This appears...
```

### LOGIN REQUIRED CASE
```
[STEP 3] Checking login status...
  ✗ Login required - please log in manually in the browser window
  ℹ Waiting for manual login (30 seconds)...
  ✓ Login detected after 15 seconds
```

### BLOCKED CASE (CAPTCHA)
```
[STEP 2] Navigating to ChatGPT...
  ✓ Navigated to https://chat.openai.com

[STEP 3] Checking login status...
  ⚠ CAPTCHA detected on page
  
======================================================================
RESULTS SUMMARY
======================================================================
Status: BLOCKED
Browser launched: True
Page opened: True
Error: CAPTCHA requires manual intervention
```

---

## Interpreting Results

| Status | Meaning |
|--------|---------|
| **VERIFIED** | ✓ Full E2E works: input → ChatGPT → response → HAB |
| **IMPLEMENTED BUT UNVERIFIED** | Code exists but not tested |
| **GAP** | Missing component (not yet implemented) |
| **BLOCKED** | Cannot proceed (login, CAPTCHA, network, etc.) |
| **UNKNOWN** | Insufficient evidence |

---

## Security & Privacy Notes

- ✓ **No session stealing:** Uses independent Playwright context
- ✓ **No cookie storage:** Cookies not saved to code/logs
- ✓ **No auth exposure:** Credentials not logged
- ✓ **Manual login only:** No automated credential entry
- ✓ **CAPTCHA handling:** Blocked immediately if detected (not bypassed)

---

## Troubleshooting

### "Playwright available" but then error launching browser
**Solution:** Playwright may need to download Chromium
```bash
playwright install
```

### Browser doesn't launch / "chromium not found"
**Solution:**
```bash
playwright install chromium
```

### Login detection fails
**Possible causes:**
- ChatGPT UI changed (selectors may need update)
- Session expired
- CAPTCHA detected (will be marked BLOCKED)

### Response not detected after 60 seconds
**Possible causes:**
- ChatGPT is slow to respond
- DOM selector changed
- Network issue

---

## Next Steps (After Test Results)

### If VERIFIED ✓
- E2E path works with existing Orchestra + Playwright
- Ready to implement persistent browser session pooling
- Ready for multi-AI integration

### If BLOCKED (e.g., CAPTCHA)
- Indicates environment limitation, not code issue
- Can be retried at different time
- Alternative: Use API-based providers (Claude/Gemini)

### If GAP or ERROR
- Specific component needs implementation
- Will need targeted fix

---

## Cleanup After Test

Browser will close automatically. No cleanup required.

If you want to re-run:
```bash
python3 chatgpt_browser_e2e_minimal.py
```

---

**Ready to run the test? Execute the command above and report results.**

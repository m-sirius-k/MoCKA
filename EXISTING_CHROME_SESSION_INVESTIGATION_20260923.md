# 既存 Chrome セッション利用 - 調査報告
**Date:** 2026-09-23  
**Investigation:** Existing Chrome CDP Connection Feasibility  
**Status:** ✅ Technically Feasible (not yet implemented)

---

## Executive Summary

**既存Chrome セッション利用：実現可能**

Playwright は Chrome DevTools Protocol (CDP) 経由で **既に実行中の Chrome に接続** できます。ただし、現在の orchestra_one_host.py はこの機能を使用していません。

---

## Investigation Results

### 1. Playwright CDP Support
```
Status: ✅ AVAILABLE

Method: playwright.chromium.connect_over_cdp(endpoint)
Signature: browser = await chromium.connect_over_cdp('ws://localhost:9222')
Purpose: Connect to existing browser instance
Support Level: Full Playwright support
```

### 2. Current Orchestra Implementation
```
Status: ❌ NOT IMPLEMENTED

Current code: p.chromium.launch(headless=False, slow_mo=50)
Behavior: Launches NEW Chrome instance
Session reuse: NO (fresh start every time)
Login required: YES (must login to each site)
```

### 3. Existing Chrome Connection Capability
```
Status: ❌ NOT CURRENTLY USED

What's missing: CDP connection code in orchestra_one_host.py
What's needed: 20-50 lines of modification
Feasibility: CONFIRMED TECHNICAL FEASIBILITY
Blocking issues: NONE (pure implementation, no external blockers)
```

---

## Technical Architecture

### Current Flow (New Browser Launch)
```
orchestra_one_host.py
  ↓
p.chromium.launch()
  ↓
NEW Chrome instance starts
  ↓
Must login to ChatGPT/Gemini/Perplexity
  ↓
No CAPTCHA but slow (30+ seconds)
  ↓
Execute prompts
  ↓
Close browser
```

### Proposed Flow (Existing Chrome Session)
```
User: Launch Chrome with debugging
  $ chrome.exe --remote-debugging-port=9222
  ↓ (User manually opens ChatGPT/Gemini/Perplexity and logs in)

orchestra_one_host.py
  ↓
p.chromium.connect_over_cdp('ws://localhost:9222')
  ↓
Connect to EXISTING Chrome instance
  ↓
Access already-logged-in pages
  ↓
No login needed (session reuse)
  ↓
Fast execution (1-2 seconds)
  ↓
Execute prompts
  ↓
Return results (Chrome stays running for future use)
```

---

## Chrome DevTools Protocol (CDP) Details

### Prerequisites
```
1. Chrome must be launched with debugging port:
   chrome.exe --remote-debugging-port=9222

2. Pages must be opened and logged in:
   - https://chatgpt.com (logged in)
   - https://gemini.google.com (logged in)
   - https://perplexity.ai (logged in)

3. Playwright can then connect:
   ws://localhost:9222
```

### What CDP Enables
```
✓ Access to existing browser instance
✓ Reuse of cookies and auth tokens
✓ No need to re-login
✓ No CAPTCHA (using existing session)
✓ Fast execution (1-2 sec vs 30+ sec with login)
✓ Human can monitor/interact with Chrome simultaneously
✓ Single browser reused for multiple prompts
```

---

## Implementation Assessment

### Current Status
```
Code implementation: NOT DONE
- orchestra_one_host.py uses launch() only
- No CDP connection logic present
- No parameter for existing Chrome endpoint
```

### Required Changes
```
File: orchestra_one_host.py

1. Add parameter to run_orchestra():
   cdp_endpoint: Optional[str] = None

2. Add connection logic:
   if cdp_endpoint:
       browser = await p.chromium.connect_over_cdp(cdp_endpoint)
   else:
       browser = await p.chromium.launch(...)

3. Handle context/page enumeration:
   - List existing contexts
   - Find ChatGPT/Gemini/Perplexity pages
   - Reuse existing pages instead of creating new ones

Complexity: LOW (20-50 lines)
Risk: LOW (backward compatible - launch() still works)
Testing: MANUAL (requires Chrome running with --remote-debugging-port)
```

### Backward Compatibility
```
✓ If no CDP endpoint provided → launch() as before
✓ Existing behavior unchanged
✓ No breaking changes
✓ Optional feature
```

---

## Testing Plan

### Manual Test Procedure

**Step 1: Launch Chrome with debugging**
```bash
# Windows PowerShell
$chromePath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
& $chromePath --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

**Step 2: Login to AI services**
```
1. Open new Chrome tabs:
   - https://chatgpt.com (login)
   - https://gemini.google.com (login)
   - https://perplexity.ai (login)

2. Keep tabs open (don't close)
3. Chrome will remain running on port 9222
```

**Step 3: Run connection test**
```bash
cd C:\Users\sirok\MoCKA\gateway
python test_existing_chrome_connection.py
```

**Step 4: Verify results**
```
Expected output:
  ✓ Chrome is running on CDP port 9222
  ✓ Connected successfully!
  ✓ ChatGPT page found
  ✓ Gemini page found
  ✓ Perplexity page found
  ✓ ChatGPT input element detected (logged-in)

This confirms existing Chrome connection works!
```

---

## Benefits vs Challenges

### Benefits of Existing Chrome Connection
```
✅ Reuse logged-in sessions (no re-login)
✅ No CAPTCHA challenges (session tokens valid)
✅ Faster execution (1-2 sec vs 30+ sec)
✅ No rate limiting from login attempts
✅ Human can monitor Chrome simultaneously
✅ Single Chrome reused for multiple requests
✅ Cookies and preferences maintained
✅ Browser history preserved
```

### Challenges
```
❌ User must manually launch Chrome with --remote-debugging-port
❌ User must manually login to each AI service
❌ Chrome window must stay open (can't close)
❌ No longer "fire and forget" - requires active Chrome
❌ Playwright won't auto-detect; explicit endpoint needed
```

---

## Current Decision Points

### For Orchestra Implementation
```
Decision 1: Support CDP connection?
  Option A: Add CDP support (recommended)
  Option B: Keep launch() only
  Option C: Support both modes (recommended)

Decision 2: Make CDP primary or optional?
  Option A: CDP first, launch() fallback (recommended)
  Option B: Launch() first, CDP optional

Decision 3: How to pass CDP endpoint?
  Option A: Environment variable
  Option B: Command-line parameter
  Option C: Both
```

### Recommendation
```
✅ Add CDP support as OPTIONAL feature
✅ Support both launch() and connect_over_cdp()
✅ Pass endpoint via:
   - Environment variable: ORCHESTRA_CDP_ENDPOINT
   - Command-line parameter: --cdp-endpoint
✅ Default behavior unchanged (launch() if no CDP)
✅ Low risk, backward compatible
```

---

## Files Generated

### Test Scripts
1. `investigate_playwright_connect.py`
   - Confirms Playwright CDP support
   - Documents connect_over_cdp() method
   - Provides implementation guidance

2. `test_existing_chrome_connection.py`
   - Tests actual CDP connection
   - Enumerates existing pages
   - Verifies login state
   - Can inject prompts into existing sessions

### Documentation
- This report: `EXISTING_CHROME_SESSION_INVESTIGATION_20260923.md`

---

## Next Steps (if desired)

### To implement existing Chrome support:

1. **Modify orchestra_one_host.py**
   - Add CDP endpoint parameter
   - Add connect_over_cdp() logic
   - Keep launch() as fallback

2. **Update adapters_orchestra_socket.py**
   - Support CDP_ENDPOINT environment variable
   - Pass to orchestra_one_host.py

3. **Test end-to-end**
   - Launch Chrome with debugging
   - Login to AI services
   - Run OrchestraSocket E2E
   - Verify prompt execution with existing session

4. **Document for users**
   - How to launch Chrome with debugging
   - How to configure Orchestra for CDP
   - Benefits and limitations

---

## Conclusion

### Current State
```
✅ Playwright supports existing Chrome connection (CDP)
✅ Technical feasibility CONFIRMED
✅ Low implementation complexity
✅ Zero breaking changes

❌ Current orchestra_one_host.py does NOT use this
❌ Would require code modification to enable
❌ Not a blocker - optional enhancement
```

### Decision Required
```
Question: Should Orchestra be enhanced to support existing Chrome sessions?

Option A: YES → Modify orchestra_one_host.py to add CDP support
  Pro: Faster, no re-login, reusable session
  Con: User must manually run Chrome with debugging port

Option B: NO → Keep current launch() only
  Pro: No code changes, fully automated
  Con: Slower, must re-login, no session reuse, CAPTCHA risk

Recommendation: YES (Option A) - Low risk enhancement
```

---

## Investigation Status

```
Existing Chrome Detection:        INVESTIGATING
CDP Support in Playwright:         ✅ CONFIRMED
orchestra_one_host.py Integration: ❌ NOT IMPLEMENTED
Implementation Feasibility:        ✅ CONFIRMED
Testing Plan:                      ✅ DESIGNED
```

**Ready for implementation decision.**

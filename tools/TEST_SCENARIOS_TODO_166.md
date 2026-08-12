# TODO_166: Orchestra UI Blocker — Test Scenarios

## Preflight Check Test Matrix

### Scenario 1: Normal Case (READY)
**Input**: Page with visible, enabled input field
**Expected**: status="READY", input_field returned

```
Input Field Selector: #prompt-textarea → FOUND
→ wait_for(state="visible") → SUCCESS
→ wait_for(state="enabled") → SUCCESS
→ RETURN: {"status": "READY", "input_field": <element>, ...}
```

**Verification**: ✓ Input can be filled
**Regression**: ✓ Existing happy path unaffected


### Scenario 2: CAPTCHA Present
**Input**: Page with reCAPTCHA iframe
**Expected**: status="BLOCKED_CAPTCHA", do not attempt input

```
Selectors checked:
  - iframe[title="reCAPTCHA"] → FOUND
  → RETURN: {"status": "BLOCKED_CAPTCHA", "description": "CAPTCHA detected", ...}
```

**Verification**: ✓ No attempt to fill input
**User Impact**: ✓ Clear message that CAPTCHA is blocking
**Regression**: ✓ Other tabs continue


### Scenario 3: Cookie Dialog
**Input**: Page with cookie consent banner
**Expected**: status="BLOCKED_DIALOG", do not attempt input

```
Dialog Keywords checked: ["login", "sign in", "cookie", "accept"]
  - text="Cookie" → FOUND in page elements
  → RETURN: {"status": "BLOCKED_DIALOG", "description": "Dialog detected: cookie", ...}
```

**Verification**: ✓ Dialog not automatically dismissed
**User Impact**: ✓ Visible message: "Dialog detected: cookie"
**Regression**: ✓ Input field might exist but skip it


### Scenario 4: Login Required
**Input**: Page with login screen after session expiration
**Expected**: status="BLOCKED_DIALOG", skip attempt

```
Dialog Keywords checked:
  - text="Sign in" → FOUND
  → RETURN: {"status": "BLOCKED_DIALOG", "description": "Dialog detected: sign in", ...}
```

**Verification**: ✓ No blind fill attempt
**User Impact**: ✓ Clear feedback on login requirement
**Regression**: ✓ Other AIcontinue


### Scenario 5: Input Field Disabled
**Input**: Page where input field exists but is disabled
**Expected**: status="ERROR", graceful skip

```
Selectors checked:
  - textarea → FOUND in DOM
  → wait_for(state="enabled", timeout=1000) → TIMEOUT EXCEPTION
  → Try next selector...
  → All selectors exhausted
  → RETURN: {"status": "ERROR", "description": "Input field not found", ...}
```

**Verification**: ✓ Does not attempt to fill disabled field
**User Impact**: ✓ Error logged, orchestration continues
**Regression**: ✓ No exception thrown


### Scenario 6: Page Still Loading
**Input**: Page DOM loaded but interactive elements not yet ready
**Expected**: status="ERROR", timeout after 10 seconds

```
Preflight timeout=10 seconds:
  - CAPTCHA check → No (OK)
  - Dialog check → No (OK)
  - Input field wait_for(visible, timeout=2000) → No element yet
  - Input field wait_for(visible, timeout=2000) → No element yet
  - ... retries with different selectors
  - Elapsed time > 10 seconds
  → RETURN: {"status": "ERROR", wait_time=10.2, ...}
```

**Verification**: ✓ Does not hang indefinitely
**User Impact**: ✓ Orchestration moves forward after timeout
**Regression**: ✓ Other orchestrated AIs not blocked


### Scenario 7: Orchestration Result Report
**Input**: 5 concurrent preflight checks (ChatGPT, Perplexity, Copilot, Gemini, etc.)
**Expected**: Result breakdown with blocker status

```
Results:
  ✓ Claude: READY
  ✓ ChatGPT: READY
  ⚠️ Copilot: BLOCKED_CAPTCHA
  ✓ Perplexity: READY
  ⚠️ Genspark: BLOCKED_DIALOG (login)
  ✓ Gemini: READY

AI回答が得られたもののみ統合:
  【Claude】...
  【ChatGPT】...
  【Perplexity】...
  【Gemini】...

（Copilot, Genspark はスキップ、ユーザーに通知）
```

**Verification**: ✓ Partial results still useful
**User Impact**: ✓ Transparent about which AIs succeeded
**Regression**: ✓ Does not timeout waiting for all 5


## Regression Test Cases

### Regression 1: Normal Message Flow (No Blockers)
**Condition**: All 5 AIs are ready
**Expected**: Same timing as before (< 2 min for 5-way deliberation)

```
Before: ~90-120 seconds
After: ~90-120 seconds (preflight adds ~1-2 sec per AI)
Acceptable: < 140 seconds
```

### Regression 2: Message Input Not Duplicated
**Condition**: Input field found by preflight, used from preflight result
**Expected**: Only one fill() call per AI

```
Before: field = page.locator(sel).first; await field.fill(...)
After:  field = pf["input_field"]; await field.fill(...)
        (same element, used once)
```

### Regression 3: Existing Storage/Retrieval Unaffected
**Condition**: save_chat_url() and load_chat_urls() still called
**Expected**: Same session resumption behavior

```
Before: save_chat_url() called at end
After:  save_chat_url() still called at end (unchanged)
```

### Regression 4: Timeout Handling
**Condition**: wait_for_completion() still has 120s timeout
**Expected**: Same timeout behavior for "stuck AI"

```
Before: 120s timeout per AI if no response
After:  10s preflight timeout + 120s completion timeout = 130s max
Acceptable: Slight increase but still reasonable
```


## Test Execution Procedure

### Unit Tests (Mocked)
```bash
python3 tools/test_orchestra_preflight.py
# Tests:
#  1. Normal case (READY)
#  2. CAPTCHA detection
#  3. Dialog detection
#  4. Error handling
```

### Integration Tests (Real Playwright)
```bash
# Requires: playwright + browser drivers installed
# Test each AI individually:
python3 tools/mocka_orchestra_v10.py "test prompt" orchestra --test-preflight=ChatGPT
python3 tools/mocka_orchestra_v10.py "test prompt" orchestra --test-preflight=Copilot
python3 tools/mocka_orchestra_v10.py "test prompt" orchestra --test-preflight=Perplexity
# ... etc for each AI

# Verify: CAPTCHA page, Cookie banner page, etc.
```

### Manual Testing (Real Deliberation)
```bash
# Test 1: All AIs ready
1. Open all AI tabs (Claude, ChatGPT, Copilot, Perplexity, Gemini)
2. Navigate to chat screens
3. Use Chrome extension "MoCKAで協議" context menu
4. Verify: 5 responses received, combined in Claude

# Test 2: Copilot CAPTCHA block
1. Close Copilot tab and reopen (trigger CAPTCHA)
2. Use Chrome extension "MoCKAで協議"
3. Verify: "⚠️ Copilot BLOCKER DETECTED: CAPTCHA"
4. Verify: Other 4 AIs still respond

# Test 3: Perplexity Cookie dialog
1. Clear Perplexity cookies or access from private window
2. Use Chrome extension "MoCKAで協議"
3. Verify: "⚠️ Perplexity BLOCKER DETECTED: BLOCKED_DIALOG"
4. Verify: Combined response includes only 4 AIs (Copilot, Perplexity skipped)
```


## Success Criteria

✓ All preflight checks complete within 10 seconds per AI
✓ CAPTCHA/Dialog/Login blockers detected accurately
✓ Input field readiness verified before fill()
✓ Blocked AIs skipped without hanging
✓ Other AIs continue unaffected
✓ No regression in normal case (all ready)
✓ Error messages clear to user
✓ Orchestration completes in < 2 minutes (with blockers)


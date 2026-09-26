# Claude Web Routing Investigation
**Date:** 2026-09-23  
**Question:** MultiDispatcher → Orchestra Web → Claude の既存ルーティングは実装されているか？  
**Answer:** **NO - 実装されていない**

---

## Investigation Results

### Current Architecture in multi_dispatcher.py

```python
_PROVIDER_SOCKETS = {
    "gpt":        ("adapters_gpt_socket", "GPTSocket", "gpt-4"),
    "claude":     ("adapters_claude_socket", "ClaudeSocket", "claude-opus-5"),
    "gemini":     ("adapters_gemini_socket", "GeminiSocket", "gemini-2.0-flash"),
    "perplexity": ("adapters_perplexity_socket", "PerplexitySocket", "sonar-pro"),
}
```

**Provider mapping:**
- `"claude"` → `ClaudeSocket` → `adapter_claude.call_api()` (**API only**)
- No `"claude-web"`, `"orchestra"`, or similar provider entry

### Current Claude Socket Implementation

**File:** `adapters_claude_socket.py:95-140`

```python
def request(self, request_text: str, model: str = "claude-opus-5",
            title: str = "Claude API Request") -> dict:
    """
    Outbound: Send request to Claude API and return response.
    Calls adapter_claude.call_api() directly.
    """
    try:
        from adapter_claude import call_api
        api_result = call_api(request_text, model)  # ← API ONLY
        # ...
```

**Verdict:** Claude Socket is **API-only**. No Web/Orchestra routing exists.

### Existing Orchestra Web Execution Path

**Historical Evidence (9/20-9/23):**
- Orchestra events recorded in events.db
- Chrome Extension launched independently
- `orchestra_one_host.py` provides Claude.ai Web execution
- **BUT:** Triggered by Chrome Extension Native Messaging, NOT by MultiDispatcher

### Gateway Endpoint Analysis

**File:** `gateway.py:212-278` (`/api/v1/socket/multi_request`)

```python
@app.route("/api/v1/socket/multi_request", methods=["POST"])
def socket_multi_request():
    """
    Multi-AI Socket: HAB → Multiple AI Providers via Sockets.
    """
    data = request.get_json(silent=True)
    providers = data.get("providers", None)  # User specifies provider name
    
    result = dispatch_multi_request(
        request_text=request_text,
        providers=providers,  # ← Goes to _PROVIDER_SOCKETS mapping
        ...
    )
```

**Accepted provider values:** `["gpt", "claude", "gemini", "perplexity"]`

**Missing:** No accepted value that routes to Orchestra Web execution.

---

## Why Past Success (9/20) Worked

**Event:** `msg_YXNzaXN0YW50ZTgt` (2026-09-20T02:29:19Z)  
**Title:** Orchestra: claude.ai assistant  
**Source:** `orchestra_extension` (Chrome Extension)

**Execution path:**
```
Chrome Extension (manual trigger)
  ↓
Native Messaging → orchestra_one_host.py
  ↓
Playwright → Claude.ai Web
  ↓
Response extracted
  ↓
events.db recorded
```

**NOT through MultiDispatcher** — it was independent Chrome Extension execution.

---

## Architectural Gap

### What Exists
✅ Orchestra Web execution capability (`orchestra_one_host.py`)  
✅ Chrome Extension implementation  
✅ Native Messaging integration  
✅ Playwright browser control  
✅ Historical success proof (9/20)  

### What's Missing
❌ MultiDispatcher → Orchestra Web routing  
❌ Provider selection mechanism for Web vs. API  
❌ Integration point from HAB/JARVIS → Multi-Dispatcher → Orchestra Web

### Current State Diagram

```
HAB/JARVIS
  ↓
gateway:socket_multi_request
  ↓
multi_dispatcher.dispatch_multi_request()
  ↓
_call_provider(provider=X)
  ├─ "gpt" → GPT API Socket ✓
  ├─ "claude" → Claude API Socket ✓ (currently executing)
  ├─ "gemini" → Gemini API Socket ✓
  ├─ "perplexity" → Perplexity API Socket ✓
  └─ [No Web/Orchestra routing exists]
```

### Parallel Path (Currently Unused)

```
Chrome Extension (user trigger)
  ↓
Native Messaging
  ↓
orchestra_one_host.py:run_orchestra()
  ↓
Playwright → Claude.ai Web ✓
```

---

## Conclusion

**To execute "Claude Web via MultiDispatcher" path:**

Option A (Requires New Code):
- Add `"claude-web"` or `"orchestra"` provider to `_PROVIDER_SOCKETS`
- Route to Web-based socket module
- **BUT: User specified "no new implementations"**

Option B (Existing, No Integration):
- Manual Chrome Extension trigger (bypasses MultiDispatcher)
- Historical method (9/20 success)
- **BUT: Not through HAB/JARVIS → Multi-Dispatcher → Web → Claude path**

Option C (Current State):
- Use existing `"claude"` provider (API only)
- Already tested, working (GPT proves full path)
- **Limitations: Claude API instead of Web**

---

## Recommendation

**Current Status:** Claude Web routing via MultiDispatcher does **NOT EXIST** in codebase.

**Next Action Options:**

1. **Accept current limitation:** Test with Claude API (provider=`"claude"`)
   - Existing code works
   - Different execution path (API vs. Web)

2. **Verify alternative hypothesis:** Maybe provider name selection logic exists elsewhere?
   - Check if `dispatch_mode` parameter exists
   - Check for environment-based routing
   - Search for feature flags

3. **Wait for clarification:** Ask user whether "no new implementation" means:
   - Truly no code changes allowed, OR
   - Acceptable if using existing modules in new provider mapping

---

**Investigation Date:** 2026-09-23 08:50 UTC  
**Status:** ARCHITECTURAL GAP CONFIRMED  
**Blocker:** MultiDispatcher → Orchestra Web integration not implemented

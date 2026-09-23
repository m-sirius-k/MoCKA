# MoCKA HAB / JARVIS / T2 — User Guide

**Status:** User Documentation  
**Date:** 2026-09-22  
**Audience:** Developers, Researchers, AI System Operators

---

## Overview

MoCKA HAB (Human Authority Boundary) is the governance layer that sits between AI models and actual execution. This guide walks you through how to:

1. Submit an AI request to HAB
2. Approve or reject the request as a human operator
3. Watch JARVIS orchestrate and T2 execute
4. Retrieve results

---

## Architecture: AI Request → HAB → JARVIS → T2

```
Your Application / User
    |
    v
AI Model (GPT, Gemini, Claude, etc.)
    |
    v (mocka_record_event tool)
    |
HAB Common Core [PENDING state]
    |
    v (Human Operator approves/rejects)
    |
Authorization State [APPROVED/REJECTED]
    |
    v (if APPROVED)
    |
JARVIS Execution Orchestrator
    |
    v
T2 Runtime (actual execution)
    |
    v
Result Storage & Retrieval
    |
    v
Your Application / User (receives result)
```

---

## Step 1: Submit Request via AI Model

### Option A: Claude (Recommended)

Claude automatically includes the `mocka_record_event` tool. When you ask Claude to make a decision, save work, or perform an action, Claude calls this tool:

```python
# Claude's system prompt includes:
# "Call mocka_record_event tool when recording important decisions"

# Your interaction with Claude:
# User: "Please analyze this data and record your findings"
# 
# Claude will automatically call:
# {
#   "title": "Data analysis findings",
#   "description": "Analyzed Q4 metrics: revenue up 12%, costs down 5%",
#   "tags": ["analysis", "quarterly"]
# }
```

**What happens automatically:**
- Claude calls `mocka_record_event` tool
- `adapter_claude.py` receives the tool call
- HABBridge submits to HAB → generates `request_id`
- Claude receives `hab_request_id` in tool_result
- You see the `request_id` in Claude's response

### Option B: Direct API Call (Advanced)

If you're building a custom application, you can submit directly via event API:

```bash
curl -X POST http://localhost:5010/api/v1/event \
  -H "X-MoCKA-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Custom analysis",
    "description": "Processed 10000 records",
    "tags": ["custom", "batch"],
    "actor": {
      "vendor": "CustomApp",
      "model": "v1.0"
    }
  }'
```

This records an event but does NOT automatically generate a HAB request. To generate HAB request, use Option A (AI-based) or contact the HAB team for API submission.

---

## Step 2: Check HAB Status

Once submitted, your request enters PENDING state. Check its status:

### Check via CLI (Recommended)

```bash
# Check status of a specific request
python governance/human_gate_cli.py status REQ001

# Output:
# [status] request_id=REQ001 state=PENDING
```

### List All Pending Requests

```bash
python governance/human_gate_cli.py pending

# Output:
# [pending] PENDING状態のrequest_idはありません。
# (or lists pending request_ids with timestamps)
```

### Check via API

```python
from phi_os.human_gate import get_state

state = get_state("REQ001")
# Returns: "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED" | None
```

---

## Step 3: Human Authority Approves or Rejects

**Only a human operator at a terminal can approve/reject.**  
This is intentional — AI cannot auto-approve its own requests.

### Approve a Request

```bash
python governance/human_gate_cli.py approve REQ001

# Interactive prompt (TTY only):
# [approve] request_id=REQ001 現在の状態=PENDING
# この内容を、きむら博士本人が確認した上で承認しますか？ [yes/no]: yes
# [approve] request_id=REQ001 state=APPROVED event_id=HG20260922_...
```

**What happens when approved:**
1. State transitions to APPROVED
2. Authorization state is issued (authorization_id generated)
3. JARVIS engine detects APPROVED state
4. JARVIS calls `/runtime/approve` endpoint
5. T2 runtime begins execution

### Reject a Request

```bash
python governance/human_gate_cli.py reject REQ001

# Interactive prompt:
# request_id=REQ001(現在=PENDING)を却下しますか？ [yes/no]: yes
# [reject] request_id=REQ001 state=REJECTED event_id=HG20260922_...
```

Request is marked REJECTED. JARVIS will not proceed to execution.

---

## Step 4: JARVIS Orchestrates Execution

Once approved, JARVIS automatically:
1. Checks authorization state
2. Validates decision_id
3. Calls T2 runtime endpoint with authorization_id
4. Monitors execution status

**You don't need to do anything** — JARVIS handles this automatically.

To monitor JARVIS activity (if needed):

```bash
# Check JARVIS logs (if configured)
tail -f data/jarvis_execution.log
```

---

## Step 5: Retrieve Results

Once T2 execution completes, results are stored in MoCKA's event system.

### Option A: Check Last Event (API)

```bash
curl -H "X-MoCKA-Key: YOUR_API_KEY" \
  http://localhost:5010/api/v1/last_event
```

Response includes execution result + metadata:
```json
{
  "event_id": "EV20260922_...",
  "when": "2026-09-22T15:30:45.123Z",
  "who_actor": "Claude/opus-5",
  "what_type": "execution_result",
  "short_summary": "Tool execution completed: 5 records processed",
  "execution_id": "EX20260922_...",
  "execution_status": "success",
  "execution_result": { "records_processed": 5, "errors": 0 }
}
```

### Option B: Query HAB for Final State

```bash
python governance/human_gate_cli.py status REQ001

# Output after execution:
# [status] request_id=REQ001 state=APPROVED
# (HAB only tracks approval state, not execution result)
```

### Option C: Direct Database Query (Advanced)

```bash
sqlite3 data/mocka_events.db \
  "SELECT * FROM events WHERE execution_id='EX20260922_...' LIMIT 1"
```

---

## Complete Example: AI Analysis → HAB → Execution

### User's Interaction

```
User: "Please analyze this Q4 data and record the findings with 
       recommendations for Q1 planning."

Claude: [thinking and analyzing...]

[Calling tool: mocka_record_event]
{
  "title": "Q4 Financial Analysis & Q1 Recommendations",
  "description": "Analyzed Q4 metrics: Revenue increased 12% YoY, 
                  operating costs down 5%, profit margin 32%.
                  Recommended Q1 actions: Scale marketing spend to 
                  $500K, reduce overhead by 10%.",
  "tags": ["quarterly_analysis", "financial", "planning"]
}

[Tool result received]:
hab_request_id: REQ_20260922_abc123
hab_state: PENDING
event_id: EV_20260922_def456

Claude: "I've submitted the analysis to HAB for approval. 
         Your request ID is REQ_20260922_abc123. 
         The doctor needs to review and approve before execution."
```

### Operator's Actions

```bash
# Step 1: Check pending requests
$ python governance/human_gate_cli.py pending
[pending] 1件のPENDING:
  REQ_20260922_abc123  submitted_at=2026-09-22T15:20:00

# Step 2: Review and approve
$ python governance/human_gate_cli.py approve REQ_20260922_abc123
[approve] request_id=REQ_20260922_abc123 現在の状態=PENDING
この内容を、きむら博士本人が確認した上で承認しますか？ [yes/no]: yes
[approve] request_id=REQ_20260922_abc123 state=APPROVED event_id=HG20260922_xyz789

# Step 3: JARVIS automatically executes (you can check logs)
$ tail -f data/jarvis_execution.log
[JARVIS] Received APPROVED authorization for REQ_20260922_abc123
[JARVIS] Calling /runtime/approve with authorization_id=AUTH_...
[T2] Executing approved action...
[T2] Result recorded: execution_id=EX_20260922_ghi000

# Step 4: Retrieve result
$ curl -H "X-MoCKA-Key: KEY" http://localhost:5010/api/v1/last_event | jq
{
  "event_id": "EV_20260922_ghi000",
  "execution_status": "success",
  "execution_result": {
    "analysis_stored": true,
    "recommendations_queued": true
  }
}
```

---

## Environment Variables (Deployment)

For production deployment, configure these environment variables:

```bash
# Gateway Authentication
export MOCKA_API_KEYS="key1,key2,key3"
export MOCKA_HMAC_SECRET="your-secret-key"

# Endpoint Configuration (hostname:port)
export MOCKA_GATE_HOST="127.0.0.1"           # Default: 127.0.0.1
export MOCKA_GATE_PORT="5000"                # Default: 5000
export MOCKA_EXECUTION_RUNTIME_URL="http://..." # Default: http://127.0.0.1:8000
export MOCKA_RUNTIME_URL="http://..."        # Default: http://127.0.0.1:5000

# AI Integrations
export MOCKA_GATEWAY_URL="http://localhost:5010"
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Troubleshooting

### "Request ID not found" Error

**Cause:** Request was submitted but HAB submission failed silently.

**Solution:**
1. Check if HABBridge is available: `python -c "from gateway.hab_bridge import HABBridge; print('OK')"`
2. Check if `phi_os/human_gate.py` is accessible
3. Review error logs in `data/` directory

### "TTY required for approve/reject"

**Cause:** You ran the command in a pipe or automated script.

**Solution:**
```bash
# WRONG (non-TTY):
echo "yes" | python governance/human_gate_cli.py approve REQ001

# RIGHT (TTY):
python governance/human_gate_cli.py approve REQ001
# (then type 'yes' interactively)
```

### Execution Hangs After Approval

**Cause:** JARVIS/T2 endpoint is not reachable or misconfigured.

**Solution:**
1. Check endpoint URLs:
   ```bash
   # These should return HTTP 200 or 404, not connection refused
   curl -v http://127.0.0.1:5000/health
   curl -v http://127.0.0.1:8000/health
   ```
2. Check environment variables are set correctly
3. Review JARVIS logs in `data/jarvis_execution.log`

### Result Not Appearing in `/api/v1/last_event`

**Cause:** Result delivery pipeline delayed or event not flushed to database.

**Solution:**
1. Wait 5-10 seconds (event buffer batch interval)
2. Manually query database:
   ```bash
   sqlite3 data/mocka_events.db \
     "SELECT * FROM events ORDER BY rowid DESC LIMIT 5"
   ```
3. Check event_buffer status in logs

---

## Best Practices

✓ **DO:**
- Always use AI models (Claude preferred) to submit HAB requests
- Have humans review and explicitly approve important decisions
- Check request status before taking action
- Monitor execution results via API

❌ **DON'T:**
- Bypass HAB approval for critical operations
- Use non-TTY methods to approve (prevents accidental automation)
- Hard-code API keys in scripts (use environment variables)
- Assume execution succeeded — always check results

---

## Support & More Information

- Architecture details: See `docs/governance/control_map_v2.md`
- HAB specification: See `phi_os/human_gate.py` (code comments)
- JARVIS implementation: See `runtime/jarvis/core/engine.py`
- Questions: Contact the MoCKA team

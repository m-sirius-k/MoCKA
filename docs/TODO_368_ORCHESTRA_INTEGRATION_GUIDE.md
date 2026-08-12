# TODO_368: Orchestra → PHI-OS Event Gate Extension Integration Guide

## Status
Backend implementation: COMPLETE
Client integration: REQUIRES Orchestra extension modification

## Backend Endpoint
- Route: `/api/gate/event/extension`
- Method: POST
- Handler: `receive_event_extension()` in `phi_os/event_gate.py`
- Pattern: lightweight validation → idempotency → _write() convergence

## Integration Pattern (Orchestra background.js)

Current flow (existing):
```
User Action
    ↓
Orchestra background.js (saveMessage)
    ↓
IndexedDB storage
```

New flow (TODO_368):
```
User Action
    ↓
Orchestra background.js (saveMessage)
    ├→ IndexedDB storage (KEEP EXISTING)
    └→ /api/gate/event/extension (NEW)
        ↓
    PHI-OS Event Gate
        ↓
    validate_operational()
        ↓
    idempotency check
        ↓
    _write() → mocka_events.db
```

## Required Orchestra Modification

### Location
`Orchestra/background.js` - `saveMessage()` function

### Change Pattern
```javascript
// Existing code: preserve as-is
indexedDB operations...

// Add new code AFTER successful IndexedDB save
async function sendToMoCKAGate(event) {
  try {
    const response = await fetch('http://localhost:5000/api/gate/event/extension', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        who_actor: 'orchestra_extension',
        what_type: event.type || 'user_action',
        where_component: 'orchestra',
        why_purpose: 'user_initiated_storage',
        idempotency_key: event.id || generateUUID(),
        // Pass through other relevant fields from event
        ...event
      })
    });
    
    if (!response.ok) {
      console.warn('MoCKA gate write failed (non-blocking):', response.status);
    }
  } catch (err) {
    console.warn('MoCKA gate unreachable (non-blocking):', err.message);
  }
}

// In saveMessage() after IndexedDB commit:
await sendToMoCKAGate(eventData);
```

## Failure Handling (Non-blocking)
- If /api/gate/event/extension is unavailable: log warning, continue
- If network fails: log warning, continue
- If validation rejects: log rejection, but preserve local IndexedDB
- Existing Orchestra behavior must NOT be affected

## Validation Contract
Endpoint requires these fields (validated by `validate_operational`):
- `who_actor` (required)
- `what_type` (required)
- `where_component` (required)
- `why_purpose` (required)

## Idempotency
- Use `idempotency_key` if sending same event multiple times
- Prevents duplicate writes to mocka_events.db
- Duplicate submission returns HTTP 200 with status='duplicate'

## Testing
1. Send valid event → expect HTTP 201 + event_id
2. Send same event again with same idempotency_key → expect HTTP 200 + duplicate
3. Send without required field → expect HTTP 422 + validation error
4. Network unavailable → Orchestra continues working with local IndexedDB only

## Security Notes
- Browser sandbox constraint ensures Orchestra can only write via HTTP
- File-level DB permissions (Windows ACL) are separate defense layer
- No direct sqlite3 connection from Orchestra
- All writes converge to _write() single point

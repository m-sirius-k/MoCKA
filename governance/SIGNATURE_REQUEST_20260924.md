# Governance Event Signature Request v1.0

**Date**: 2026-09-24T01:22:03+00:00  
**Status**: PENDING SIGNATURE EXECUTION  
**Authority**: きむら博士 (Authorization Scope: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203)

## Executive Summary

This document formally requests Ed25519 signature execution for the canonical Production Governance Event. Signature execution is authorized by human gate approval but must be performed by authorized infrastructure (human operator or JARVIS/HAB signing service) using the protected root_key_v2.ed25519 private key.

**Critical Constraint**: Claude Code has NO access to private keys and WILL NOT directly execute signature operations. This document serves as a formal authorization handoff to authorized signing infrastructure.

---

## 1. Event Specification

**Event File**: `/home/user/MoCKA/governance/governance_event_production.json`

**Event Content** (unsigned, ready for signing):
```json
{
  "schema": "mocka.governance.event.v1",
  "event_type": "registry_update",
  "change_class": "major",
  "previous_registry_hash": "",
  "new_registry_hash": "119e97530d40d4e8cf0d319a46e8de78f85df74de31ceeeae8faccd06e63d84b",
  "approvers": [
    "kimura"
  ],
  "timestamp_utc": "2026-09-24T01:17:42.014098+00:00",
  "signature": "",
  "note": "Production governance event: registry commitment (signature pending)"
}
```

**Schema Validation**: PASS
- schema: mocka.governance.event.v1 ✓
- event_type: registry_update ✓
- change_class: major ✓
- All required fields present ✓
- approvers non-empty (major change requirement) ✓
- new_registry_hash matches current registry sha256 ✓

---

## 2. Authorization Evidence

**Decision Ledger Record**: `DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203`

**Authorization Details**:
```
decision_id: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203
decision_purpose: RUNTIME_AUTHORIZATION
runtime_scope: GOVERNANCE_EVENT_PRODUCTION
decision: approved
status: Active
approved_by: きむら博士
approved_at: 2026-09-24T01:22:03.582030+00:00

scope_target: canonical_production_governance_event_foundation

scope_includes:
  - governance_event_production.json generation ✓
  - registry_hash validation ✓
  - timestamp validation ✓
  - event schema validation ✓

scope_excludes:
  - signature_execution (THIS STEP REQUIRES SEPARATE AUTHORIZED EXECUTION)
  - production_activation
  - bootstrap_event_replacement
  - ai_self_authorization
```

**Authorization Scope Status**: GOVERNANCE_EVENT_PRODUCTION scope APPROVED
- Covers: event generation, validation ✓
- Does NOT cover: signature execution (delegated)
- Does NOT cover: production activation (separate gate)

---

## 3. Signature Execution Specification

**Canonical Signing Script**: `governance/sign_governance_event.py`

**Execution Requirements**:

1. **Private Key Location**: `governance/keys/root_key_v2.ed25519.private.pem`
   - Status: Protected (NOT accessible to Claude)
   - Owner: きむら博士 or authorized signing infrastructure only

2. **Public Key Verification Reference**: `governance/keys/root_key_v2.ed25519.public.b64u`
   - Value: `Fnyp7H0Lnzu0i3cGC4cEC0XnZIXBQGszIt_7FIXEyUY`
   - Status: Public, available for verification

3. **Signing Algorithm**: Ed25519

4. **Message to Sign**:
   - JSON representation with deterministic serialization
   - Format: `ensure_ascii=False, separators=(",", ":"), sort_keys=True`
   - Signature field set to empty string before signing
   - Encoding: UTF-8

5. **Signature Encoding**: Base64URL (rfc4648, no padding)

6. **Output Target**: Write signed event back to `governance/governance_event_production.json`

---

## 4. Authorized Signature Execution Instructions

**For Human Operator (きむら博士)**:

```bash
cd /home/user/MoCKA

# Step 1: Prepare environment
python3 --version  # Should be Python 3.12+ for cryptography compatibility

# Step 2: Load the canonical signing script
# Note: The script currently hardcodes governance_event.json
# For production_event signing, use the inline signing approach below

# Step 3: Execute Ed25519 signature
python3 << 'SIGN_SCRIPT'
import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parent
priv_path = ROOT / "governance" / "keys" / "root_key_v2.ed25519.private.pem"
event_path = ROOT / "governance" / "governance_event_production.json"

# Load private key
private_key = serialization.load_pem_private_key(
    priv_path.read_bytes(), 
    password=None
)

# Load event
event = json.loads(event_path.read_text(encoding="utf-8-sig"))
event_copy = dict(event)
event_copy["signature"] = ""

# Sign deterministically
msg = json.dumps(
    event_copy, 
    ensure_ascii=False, 
    separators=(",", ":"), 
    sort_keys=True
).encode("utf-8")
sig = private_key.sign(msg)

# Encode signature as base64url
def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")

event["signature"] = b64u(sig)

# Write signed event
event_path.write_text(
    json.dumps(event, ensure_ascii=False, indent=2), 
    encoding="utf-8"
)
print("OK: governance_event_production signed with root_key_v2")
SIGN_SCRIPT
```

**For Automated Signing Service (JARVIS/HAB)**:

```
REQUEST_TYPE: Ed25519_SIGNATURE
TARGET_FILE: governance/governance_event_production.json
KEY_ID: root_key_v2.ed25519
AUTHORIZATION_DECISION: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203
AUTHORIZATION_SCOPE: GOVERNANCE_EVENT_PRODUCTION
MESSAGE_FORMAT: deterministic_json (sort_keys=True, separators=(",", ":"))
SIGNATURE_ENCODING: base64url_no_padding
REQUIRE_VERIFICATION: true
```

---

## 5. Post-Signature Verification Checklist

After signature execution, the following verifications MUST be performed:

### 5.1 Signature Structure Verification

- [ ] Event file path correct: `/home/user/MoCKA/governance/governance_event_production.json`
- [ ] Signature field is non-empty string
- [ ] Signature field contains only base64url characters (alphanumeric, `-`, `_`, no `=` padding)
- [ ] Signature length approximately 86-88 characters (Ed25519 is 64 bytes = 86 chars base64url)

### 5.2 Event Integrity Verification

- [ ] All schema fields present and valid
- [ ] new_registry_hash unchanged: `119e97530d40d4e8cf0d319a46e8de78f85df74de31ceeeae8faccd06e63d84b`
- [ ] approvers unchanged: `["kimura"]`
- [ ] timestamp_utc unchanged: `2026-09-24T01:17:42.014098+00:00`
- [ ] JSON formatting valid (parseable)

### 5.3 Cryptographic Verification

```bash
cd /home/user/MoCKA
python3 << 'VERIFY_SCRIPT'
import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

def b64u_decode(s: str) -> bytes:
    s = s.strip()
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)

ROOT = Path(__file__).resolve().parent
pub_path = ROOT / "governance" / "keys" / "root_key_v2.ed25519.public.b64u"
event_path = ROOT / "governance" / "governance_event_production.json"

# Load public key
pub_raw = b64u_decode(pub_path.read_text(encoding="utf-8-sig"))
pub = ed25519.Ed25519PublicKey.from_public_bytes(pub_raw)

# Load and verify event
event = json.loads(event_path.read_text(encoding="utf-8-sig"))
sig_b = b64u_decode(event["signature"])

# Reconstruct message for verification
ev_copy = dict(event)
ev_copy["signature"] = ""
msg = json.dumps(
    ev_copy, 
    ensure_ascii=False, 
    separators=(",", ":"), 
    sort_keys=True
).encode("utf-8")

# Verify
try:
    pub.verify(sig_b, msg)
    print("PASS: Signature verification successful")
    print(f"signature_value: {event['signature']}")
    exit(0)
except Exception as e:
    print(f"FAIL: Signature verification failed: {e}")
    exit(1)
VERIFY_SCRIPT
```

---

## 6. Evidence Recording

After successful signature execution and verification, record evidence:

```bash
python3 << 'RECORD_SCRIPT'
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Read signed event
event = json.loads(
    (ROOT / "governance" / "governance_event_production.json").read_text(encoding="utf-8-sig")
)

# Record signature verification evidence (example structure)
evidence = {
    "timestamp_verified_utc": datetime.now(timezone.utc).isoformat(),
    "event_file": "governance/governance_event_production.json",
    "signature_algorithm": "Ed25519",
    "signature_value": event["signature"],
    "registry_hash_verified": event["new_registry_hash"],
    "authorization_decision": "DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203",
    "authorization_scope": "GOVERNANCE_EVENT_PRODUCTION",
    "verification_status": "PENDING_CRYPTOGRAPHIC_VERIFICATION"
}

print(json.dumps(evidence, indent=2))
print("\nNext Step: Execute cryptographic verification script above")
print("Then record CHANGE_DONE event with verification evidence")
RECORD_SCRIPT
```

---

## 7. Current State Summary

| Component | Status | Evidence |
|-----------|--------|----------|
| Event generated | ✓ DONE | `/governance/governance_event_production.json` created with current registry hash |
| Schema validated | ✓ DONE | All required fields present, approvers list non-empty |
| Registry hash verified | ✓ DONE | Matches current registry file sha256 |
| Human authorization | ✓ DONE | DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203 approved by きむら博士 |
| Signature execution | **PENDING** | Requires authorized infrastructure (private key access) |
| Cryptographic verification | **PENDING** | Awaits signature execution |
| Evidence recording | **PENDING** | Awaits verification completion |

---

## 8. Scope and Constraints

**This signature request authorizes**:
- Ed25519 signing of governance_event_production.json using root_key_v2.ed25519 private key
- Within authorization scope: GOVERNANCE_EVENT_PRODUCTION only

**This request does NOT authorize**:
- Production Activation (separate gate required)
- Bootstrap event.json replacement (separate decision required)
- AI self-authorization (explicitly forbidden)
- Modification of other governance files or registry

**Constraints (Non-negotiable)**:
- Private key MUST NOT be given to Claude
- Claude MUST NOT directly execute signature
- Signature must use existing root_key_v2.ed25519 key (no new keys)
- No bypass of authorization gates
- No modification of decision ledger by Claude

---

## 9. Next Steps (After Signature Execution)

1. Execute signature using authorized infrastructure (human or service)
2. Verify signature cryptographically
3. Record verification evidence
4. Await further instructions for Production Activation phase (separate authorization gate)

---

**Prepared by**: Claude Code (Haiku 4.5)  
**For Authorization by**: きむら博士  
**Execution Authorized by**: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203  
**Date Prepared**: 2026-09-24T01:22:03+00:00

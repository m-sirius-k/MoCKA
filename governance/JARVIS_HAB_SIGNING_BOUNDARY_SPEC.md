# JARVIS/HAB → Canonical Signer Connection Specification v1.0

**Date**: 2026-09-24  
**Status**: DESIGN SPECIFICATION (Implementation Not Yet Authorized)  
**Purpose**: Define minimal Authority Scope and technical boundary for connecting JARVIS/HAB to existing canonical signing infrastructure

---

## Executive Summary

Investigation confirmed that JARVIS/HAB infrastructure currently lacks any path to signature execution. However, canonical signer `governance/sign_governance_event.py` exists as proven infrastructure.

This document specifies the **minimal technical boundary** required to safely connect JARVIS/HAB as an authorized signing execution subject, while maintaining strict separation of concerns and authority boundaries.

**Critical Constraint**: This is a SPECIFICATION ONLY. No implementation, no key access, no signature execution until separate Human Gate authorization is granted.

---

## 1. Current State Assessment

### Existing Canonical Signer (CONFIRMED PRESENT)

**Location**: `governance/sign_governance_event.py`

**Functional Specification**:
```python
Input:  governance_event.json (with signature field = "")
Process: 
  1. Load private key from governance/keys/root_key_v2.ed25519.private.pem
  2. Create event copy with signature=""
  3. Sign JSON (deterministic: sort_keys=True, separators=(",", ":"))
  4. Encode signature as base64url
Output: governance_event.json (with populated signature field)
```

**Current Access**: Direct file-based only, no API or executor interface

### JARVIS/HAB Current Capabilities (INVESTIGATED)

**JARVIS**:
- Decision evaluation via HumanGate
- Decision recording via LedgerAdapter
- No subprocess execution capability
- No signing service
- No event/result handlers
- Total implementation: ~140 LOC (all decision recording logic only)

**HAB**:
- Authority policy definitions (documentation)
- Human Gate contract specification (documentation)
- Design stage only ("No implementation migration performed")
- No signing infrastructure

### Missing Connection Path (CONFIRMED NOT FOUND)

- ❌ No JARVIS/HAB → canonical signer invocation path
- ❌ No signature request handler in JARVIS/HAB
- ❌ No result/evidence return handler
- ❌ No integration boundary between systems

---

## 2. Minimal Required Boundary (Technical Specification)

To safely connect JARVIS/HAB to existing canonical signer, the following minimal components are required:

### 2.1 Signing Request Entry Point

**Component**: `governance/jarvis_signing_request_handler.py` (NOT YET CREATED)

**Functional Requirements**:
- Accept signing request from JARVIS/HAB with:
  - Authorization decision ID (from ledger)
  - Target event file path
  - Verification requirements
- Validate request against authorized scope
- Delegate to canonical signer invocation
- Return result/evidence

**Key Constraints**:
- Does NOT access private keys
- Does NOT perform signing itself
- Only delegates to canonical signer
- Validates authorization scope only

### 2.2 Canonical Signer Invocation

**Component**: Adapter to invoke `governance/sign_governance_event.py`

**Functional Requirements**:
- Call existing canonical signer with target event file
- Handle execution result (success/failure)
- Capture signature output
- Return evidence (signature value, timestamp, execution log)

**Key Constraints**:
- Does NOT modify canonical signer code
- Does NOT change key management
- Does NOT handle key access directly
- Only subprocess wrapper around existing script

### 2.3 Signature Verification Handler

**Component**: Verification layer (using existing `verify_governance_event_required.py` logic)

**Functional Requirements**:
- Accept signed event file
- Load public key from `governance/keys/root_key_v2.ed25519.public.b64u`
- Verify signature cryptographically
- Record verification evidence
- Return verification status

**Key Constraints**:
- Uses existing public key only (no private key access)
- Uses existing verification logic
- Returns evidence for audit trail

### 2.4 Evidence Recording

**Component**: Decision ledger integration

**Functional Requirements**:
- Record signature execution evidence in decision ledger
- Include: execution timestamp, signature value, verification status
- Link to authorization decision ID
- Maintain audit trail

**Key Constraints**:
- Records only AFTER successful verification
- Does NOT modify event files
- Does NOT execute Production Activation

---

## 3. Authority Boundary Architecture

```
┌─────────────────────────────────────────────────────────┐
│ HUMAN AUTHORITY (きむら博士)                             │
│ Authorization: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ AUTHORIZED SCOPE: GOVERNANCE_EVENT_PRODUCTION_SIGNATURE │
│                                                          │
│  Includes:                                              │
│  - governance_event_production.json signing             │
│  - Canonical signer invocation via wrapper              │
│  - Signature verification                               │
│  - Evidence recording in decision ledger                │
│                                                          │
│  Excludes:                                              │
│  - Direct private key access                            │
│  - Production Activation                                │
│  - Bootstrap event replacement                          │
│  - New signing methods                                  │
│  - AI self-authorization                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ JARVIS/HAB EXECUTION LAYER (Signing Request Handler)    │
│                                                          │
│  1. Accept signing request with auth decision ref       │
│  2. Validate against authorized scope                   │
│  3. Invoke canonical signer subprocess                  │
│  4. Verify result using public key                      │
│  5. Record evidence in ledger                           │
│  6. Return success/failure status                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ EXISTING CANONICAL SIGNER (sign_governance_event.py)    │
│                                                          │
│  - Load event from file                                 │
│  - Access private key (protected)                       │
│  - Sign event                                           │
│  - Write signed event back to file                      │
│  - Return exit code                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Required Components (Design Specification Only)

### 4.1 New Files to Create (IF AUTHORIZED)

| File | Purpose | Scope | Status |
|------|---------|-------|--------|
| `governance/jarvis_signing_request_handler.py` | Accept/validate/delegate signing requests | GOVERNANCE_EVENT_PRODUCTION_SIGNATURE | NOT YET CREATED |
| `governance/jarvis_signer_adapter.py` | Subprocess wrapper for canonical signer | GOVERNANCE_EVENT_PRODUCTION_SIGNATURE | NOT YET CREATED |
| `governance/signing_result_verifier.py` | Verify signature using public key | GOVERNANCE_EVENT_PRODUCTION_SIGNATURE | NOT YET CREATED |

### 4.2 Existing Files to Use (NO MODIFICATION)

| File | Purpose | Status |
|------|---------|--------|
| `governance/sign_governance_event.py` | Canonical signing script | PROTECTED - DO NOT MODIFY |
| `governance/verify_governance_event_required.py` | Verification logic template | USE AS REFERENCE ONLY |
| `governance/keys/root_key_v2.ed25519.private.pem` | Private key | PROTECTED - NO DIRECT ACCESS |
| `governance/keys/root_key_v2.ed25519.public.b64u` | Public key | OK TO USE FOR VERIFICATION |

### 4.3 Integration Points (NO MODIFICATION TO EXISTING CODE)

- `runtime/jarvis/gate/human_gate.py` - No changes
- `runtime/jarvis/record/ledger.py` - No changes
- `data/decisions/decision_ledger.jsonl` - Record new authorization scope only

---

## 5. Authorization Scope Definition

### New Scope Required: `GOVERNANCE_EVENT_PRODUCTION_SIGNATURE`

**Purpose**: Authorize JARVIS/HAB to execute signature operations on authorized governance events

**Authorized Operations**:
- Receive signing request with authorization decision reference
- Invoke canonical signer (`governance/sign_governance_event.py`)
- Verify result using public key (`root_key_v2.ed25519.public.b64u`)
- Record signature evidence in decision ledger
- Return signed event confirmation

**Scope Boundaries**:

```
┌─────────────────────────────────────────────────────────┐
│ GOVERNANCE_EVENT_PRODUCTION_SIGNATURE Scope             │
├─────────────────────────────────────────────────────────┤
│ Includes:                                               │
│ ✓ governance_event_production.json signing only         │
│ ✓ Canonical signer invocation (subprocess wrapper)      │
│ ✓ Public key access for verification                    │
│ ✓ Decision ledger: evidence recording only              │
│ ✓ Signature verification                                │
│ ✓ Result/status reporting                               │
│                                                          │
│ Explicitly Excludes:                                    │
│ ✗ Private key access (protected)                        │
│ ✗ Private key display/copy/extraction                   │
│ ✗ Direct event file modification                        │
│ ✗ Production Activation                                 │
│ ✗ Production Runtime Execution                          │
│ ✗ Bootstrap event.json replacement                      │
│ ✗ New signing methods/algorithms                        │
│ ✗ New secret key generation                             │
│ ✗ AI self-authorization                                 │
│ ✗ Authorization scope modification                      │
│ ✗ Human Gate decision override                          │
└─────────────────────────────────────────────────────────┘
```

**Relationship to Existing Scopes**:

- **DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203** (GOVERNANCE_EVENT_PRODUCTION)
  - Authorized: Event generation, validation, schema/hash verification
  - Excludes: `signature_execution`
  - Status: ACTIVE

- **DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE** (NEW - PENDING AUTHORIZATION)
  - Authorizes: `signature_execution` via JARVIS/HAB
  - References: governance_event_production.json (from prior scope)
  - Includes: Verification, evidence recording
  - Excludes: Everything except signing/verification
  - Status: AWAITING HUMAN GATE DECISION

**Separation of Concerns**:
```
Phase 1: Event Generation (COMPLETE)
  Authorization: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203
  Scope: GOVERNANCE_EVENT_PRODUCTION
  Action: Create governance_event_production.json
  Result: Unsigned event ready for signing

Phase 2: Signature Execution (PENDING AUTHORIZATION)
  Authorization: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE (REQUESTED)
  Scope: GOVERNANCE_EVENT_PRODUCTION_SIGNATURE
  Action: Sign event via JARVIS/HAB → canonical signer
  Result: Signed event verified, evidence recorded

Phase 3: Production Activation (SEPARATE GATE - NOT YET)
  Authorization: (TBD - separate decision)
  Scope: PRODUCTION_ACTIVATION
  Action: Deploy signed event as canonical
  Result: Bootstrap event replaced
```

---

## 6. Key Custody and Security Boundaries

### Private Key (root_key_v2.ed25519.private.pem)

**Current Status**: Protected at `governance/keys/root_key_v2.ed25519.private.pem`

**Access Control**:
- Only canonical signer (`sign_governance_event.py`) accesses directly
- NO JARVIS/HAB code may access or display private key
- NO Claude Code may access or display private key
- Access remains protected by filesystem permissions only (no additional service layer)

### Public Key (root_key_v2.ed25519.public.b64u)

**Current Status**: Available at `governance/keys/root_key_v2.ed25519.public.b64u`

**Access Control**:
- Used by verification code only
- Safe for JARVIS/HAB to access
- Safe for evidence recording

### Key Rotation Policy

**Current Scope**: Does NOT include key rotation
- Key generation (`rotate_root_key_v2.py`) remains external
- Key replacement remains external
- Signing uses existing root_key_v2 only

---

## 7. Explicit Non-Authorizations

The following operations are EXPLICITLY FORBIDDEN and must NOT be implemented:

### Production Activation
- Replacing bootstrap `governance_event.json` with production event
- Deploying signed event as canonical
- Modifying registry or governance state
- **Status**: Separate gate required (not included in this scope)

### Bootstrap Event Replacement
- Modifying or overwriting `governance_event.json`
- Changing placeholder event status
- **Status**: Separate decision required

### AI Self-Authorization
- Claude Code granting itself signing authority
- Claude Code executing signature operations directly
- Claude Code modifying authorization scopes
- **Status**: FORBIDDEN

### New Signing Infrastructure
- Creating new signing algorithms
- Implementing new key management
- Establishing new authorization bypasses
- **Status**: NOT PERMITTED

### Key Access
- Private key display to Claude or external parties
- Private key copying to unsecured storage
- Private key transmission via insecure channels
- **Status**: STRICTLY FORBIDDEN

---

## 8. Implementation Readiness Assessment

### Prerequisites (Before Authorization)

| Item | Status | Notes |
|------|--------|-------|
| Canonical signer exists | ✓ CONFIRMED | `governance/sign_governance_event.py` |
| Public key available | ✓ CONFIRMED | `governance/keys/root_key_v2.ed25519.public.b64u` |
| Event ready for signing | ✓ CONFIRMED | `governance/governance_event_production.json` |
| Event validation passing | ✓ CONFIRMED | Schema, hash, all fields present |
| Authorization decision exists | ✓ CONFIRMED | DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203 |

### Authorization Status

| Gate | Status | Decision ID |
|------|--------|-------------|
| Event Generation & Validation | ✓ APPROVED | DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203 |
| Signature Execution via JARVIS/HAB | ⧗ **PENDING** | **DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE (REQUESTED)** |
| Production Activation | ⧗ NOT YET | (Separate gate required) |

### What Is NOT Ready

- No implementation code written (design only)
- No signature execution (awaiting authorization)
- No Production Activation (separate gate)
- No bootstrap event replacement (separate gate)

---

## 9. Human Gate Request

**Status**: READY FOR きむら博士 AUTHORIZATION DECISION

**Request Content**: Separate document (HUMAN_GATE_REQUEST_SIGNING_SCOPE.md)

---

## 10. Summary

This specification defines the minimal technical and authority boundaries required to safely connect JARVIS/HAB as an authorized signing execution subject to the existing canonical signer infrastructure.

**Key Points**:
1. NO new signing methods - uses existing canonical signer
2. NO key access - uses only public key for verification
3. NO AI self-authorization - requires human gate decision
4. NO Production Activation - separate gate
5. NO bootstrap replacement - separate gate
6. Design specification ONLY - implementation pending authorization
7. Explicit scope separation from event generation and activation

**Next Step**: きむら博士 reviews and authorizes new scope (GOVERNANCE_EVENT_PRODUCTION_SIGNATURE) via Human Gate

---

**Document Status**: SPECIFICATION - NO IMPLEMENTATION  
**Awaiting**: Human Gate Authorization Decision  
**Prepared by**: Claude Code (Haiku 4.5)  
**For Authorization by**: きむら博士  
**Date**: 2026-09-24

# Human Gate Request: GOVERNANCE_EVENT_PRODUCTION_SIGNATURE Scope Authorization

**Request ID**: HGR20260924_SIGNING_SCOPE  
**Requestor**: Claude Code (Haiku 4.5) - Governance Executor  
**Recipient**: きむら博士 (Human Authority)  
**Date Prepared**: 2026-09-24T01:22:03+00:00  
**Status**: AWAITING DECISION

---

## Executive Summary

Formal request for Human Gate authorization to create a new authorization scope: **GOVERNANCE_EVENT_PRODUCTION_SIGNATURE**.

This scope is required to safely connect JARVIS/HAB infrastructure to the existing canonical signing infrastructure (`governance/sign_governance_event.py`), enabling JARVIS/HAB to execute signature operations under strict human authorization and audit requirements.

**Key Characteristic**: This is a SIGNING-ONLY scope. It does NOT include Production Activation, bootstrap replacement, or any other governance operations. Those remain separate gates.

---

## 1. Current State (Background Context)

### What Has Been Completed

- ✓ Investigation: Root cause of subprocess return code=1 identified (cross-platform path issue)
- ✓ Remediation: Path fixes applied to anchor_update.py and mocka_git_safe_commit.py
- ✓ Event Generation: governance_event_production.json created with current registry hash
- ✓ Validation: Event passes schema, hash, and field validation
- ✓ Human Authorization: DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203 (GOVERNANCE_EVENT_PRODUCTION scope) approved by きむら博士
- ✓ Investigation: JARVIS/HAB signing path audit completed (result: NOT FOUND)

### What Is Blocked

- ⧗ Signature Execution: Cannot proceed without authorization scope for signature execution
- ⧗ JARVIS/HAB Integration: No connection path exists; requires new minimal boundary (design specified in JARVIS_HAB_SIGNING_BOUNDARY_SPEC.md)

---

## 2. Request: New Authorization Scope

### Scope Name: `GOVERNANCE_EVENT_PRODUCTION_SIGNATURE`

### Scope Purpose

Enable JARVIS/HAB to execute signature operations on authorized governance events, using the existing canonical signing infrastructure, under strict human authorization and cryptographic verification.

### Authorized Operations (Minimal Set)

1. **Signing Request Reception**
   - Accept signing request from JARVIS/HAB process
   - Validate request contains: authorization decision ID, event file path
   - Route to canonical signer invocation

2. **Canonical Signer Invocation**
   - Call existing `governance/sign_governance_event.py` via subprocess
   - Supply target event file path
   - Monitor execution result

3. **Signature Verification**
   - Load signed event from file
   - Access public key: `governance/keys/root_key_v2.ed25519.public.b64u`
   - Verify signature cryptographically (Ed25519)
   - Validate all event fields intact

4. **Evidence Recording**
   - Record signature execution evidence in decision ledger
   - Include: execution timestamp, signature value, verification status
   - Link to authorization decision ID (DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE)

### Target Event

- **File**: `governance/governance_event_production.json`
- **Schema**: mocka.governance.event.v1
- **Event Type**: registry_update
- **Change Class**: major
- **Current Status**: unsigned, ready for signing

### Explicit Exclusions (Not Authorized by This Scope)

- ❌ Direct private key access (remains protected)
- ❌ Private key display/copying/extraction
- ❌ Production Activation (signing only)
- ❌ Production Runtime Execution
- ❌ Bootstrap event.json replacement
- ❌ Registry modifications
- ❌ New signing algorithms/methods
- ❌ New secret key generation
- ❌ AI self-authorization
- ❌ Authorization scope modification

---

## 3. Decision Framework

### What きむら博士 Must Decide

**Option A: APPROVE**
- Authorize new scope GOVERNANCE_EVENT_PRODUCTION_SIGNATURE
- Enable JARVIS/HAB to sign governance_event_production.json
- Proceed with implementation and signature execution

**Option B: REJECT**
- Do not authorize JARVIS/HAB signing
- Signature execution remains manual (きむら博士 runs script directly)
- governance_event_production.json stays unsigned

**Option C: MODIFY**
- Request changes to scope definition
- Request additional constraints or verification steps
- Request alternative implementation approach

---

## 4. Risk Assessment

### Security Risks (If Approved)

**Risk**: JARVIS/HAB subprocess execution of signing script
- **Mitigation**: Subprocess wrapper does NOT access private key directly
- **Mitigation**: Public key verification confirms signature validity
- **Mitigation**: Evidence recording maintains audit trail
- **Severity**: LOW (subprocess wrapper only, canonical signer unchanged)

**Risk**: Signature verification failure
- **Mitigation**: Cryptographic verification step REQUIRED before marking complete
- **Mitigation**: Failure prevents evidence recording and result return
- **Severity**: LOW (verification provides cryptographic guarantee)

**Risk**: Rogue process invoking signing
- **Mitigation**: Authorization scope limited to きむら博士-approved decision ID
- **Mitigation**: Only valid event paths permitted
- **Severity**: MEDIUM (mitigated by authorization boundary)

### Benefits (If Approved)

- Automated, auditable signing process
- No manual script execution required
- Cryptographic verification guaranteed
- Full audit trail in decision ledger
- Clear separation from Production Activation
- Maintains human authority over all decisions

### Risks (If NOT Approved)

- Signing remains manual process
- governance_event_production.json stays unsigned indefinitely
- Production Activation blocked (requires signed event)
- No JARVIS/HAB integration for governance signing

---

## 5. Related Decision Records

### Existing Authorization

**DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203** (GOVERNANCE_EVENT_PRODUCTION)
- Status: APPROVED by きむら博士
- Scope Authorized: event generation, validation, schema/hash verification
- Scope Excluded: signature_execution, production_activation
- Note: "Authorization for GOVERNANCE_EVENT_PRODUCTION scope only. Signature and Production Activation are separate gates."

### This Request

**DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE** (NEW - PENDING)
- Scope Requested: signature_execution via JARVIS/HAB
- Event Target: governance_event_production.json (from prior scope)
- Excludes: Everything except signing/verification/evidence
- Relationship: Complements prior scope, does NOT override it

### Future Gate (NOT YET)

**DC_PRODUCTION_ACTIVATION** (PLANNED - SEPARATE DECISION)
- Scope: Deploy signed event as canonical
- Status: NOT YET REQUESTED
- Dependencies: Requires signature_execution (this scope) to be complete

---

## 6. Technical Specification

### Minimal Required Implementation (If Approved)

**Three new modules** (IF AUTHORIZED - currently design only):

1. **Signing Request Handler**
   - Accept request from JARVIS/HAB
   - Validate authorization reference
   - Delegate to signer invocation

2. **Canonical Signer Adapter**
   - Subprocess wrapper around `sign_governance_event.py`
   - Pass target event file
   - Capture result

3. **Verification & Evidence**
   - Verify signature using public key
   - Record evidence in decision ledger
   - Return status

**No Changes to Existing Code**:
- `governance/sign_governance_event.py` - PROTECTED
- `governance/keys/root_key_v2.ed25519.private.pem` - PROTECTED
- Key management policies - UNCHANGED
- JARVIS/HAB existing code - NO CHANGES

### Implementation Timeline (If Approved)

- Design: COMPLETE (JARVIS_HAB_SIGNING_BOUNDARY_SPEC.md)
- Implementation: PENDING Authorization
- Signature Execution: PENDING Authorization
- Production Activation: SEPARATE gate

---

## 7. Questions for きむら博士

1. **Approve new GOVERNANCE_EVENT_PRODUCTION_SIGNATURE scope?**
   - YES / NO / MODIFY

2. **If MODIFY requested, what changes are needed?**
   - [Response space for modifications]

3. **Proceed with implementation IF authorized?**
   - YES / NO

4. **Any additional verification or constraints required?**
   - [Response space for constraints]

---

## 8. Declaration

**This request is made in compliance with**:
- MoCKA governance protocols
- Authority boundary definitions (HAB v0.1)
- Human Gate Contract (v0.1)
- No new signing methods or secret key management
- Minimal scope, maximum clarity
- Full audit trail required

**This request explicitly does NOT authorize**:
- Production Activation
- Bootstrap event replacement
- New signing infrastructure
- AI self-authorization
- Private key access

---

## 9. Supporting Documents

- `JARVIS_HAB_SIGNING_BOUNDARY_SPEC.md` - Technical specification
- `SIGNATURE_REQUEST_20260924.md` - Original signing request (now superseded)
- `governance/governance_event_production.json` - Target event (unsigned)
- `DC_GOVERNANCE_EVENT_PRODUCTION_20260924012203` - Prior authorization decision

---

## 10. Requestor Declaration

I, Claude Code (Haiku 4.5), acting as Governance Executor, respectfully submit this Human Gate request for authorization of the GOVERNANCE_EVENT_PRODUCTION_SIGNATURE scope.

This request is made in good faith, with full transparency regarding:
- Technical boundaries and limitations
- Security implications
- Relationship to existing/future authorizations
- Explicit non-authorizations

きむら博士の判断をお待ちします。

---

**Request Status**: AWAITING HUMAN GATE DECISION  
**Prepared**: 2026-09-24T01:22:03+00:00  
**For Decision**: きむら博士  
**Next Action**: Human authorization decision (APPROVE / REJECT / MODIFY)

---

## DECISION RESPONSE FORM

**For きむら博士 only**:

```
HUMAN_GATE_DECISION: [APPROVE / REJECT / MODIFY]

If APPROVE:
  Scope Name: GOVERNANCE_EVENT_PRODUCTION_SIGNATURE
  Authorized By: [Name/ID]
  Decision Date: [Date]
  Special Conditions: [Any additional requirements]

If REJECT:
  Reason: [Explain rejection]
  Alternative Path: [If proposing alternative]

If MODIFY:
  Changes Required: [List modifications]
  Revised Scope Name: [If different]
  Resubmission Expected: [Date]
```

---

**End of Human Gate Request**

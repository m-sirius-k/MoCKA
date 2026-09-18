# HG-M3 Phase 2: Change Impact Analysis
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** PREPARATION

## Impact Analysis by Layer

### Code Layer

**Current State:** No binding validation code exists

**Expected Change:** 
- Add 4 new Python modules (binding, validation, ledger, audit)
- ~2000-3000 LOC estimated

**Risk:** 
- Code quality (testing before authorization)
- Performance (must not slow MoCKA)

**Control:**
- Code review before authorization
- Unit tests required
- Performance benchmarks

### Data Layer

**Current State:** No ledger schema

**Expected Change:**
- Create Decision Ledger table
- Add Evidence Package structure
- Add Audit Memory schema

**Risk:**
- Storage overhead (estimate: 10-20MB for test data)
- Migration complexity (will add later)

**Control:**
- Schema validation before authorization
- Data migration plan required
- Backup before any production change

### Governance Layer

**Current State:** No binding-based decisions recorded

**Expected Change:**
- All Phase 2 decisions will use binding model
- Validation failures will escalate to Human Gate

**Risk:**
- Increased escalation workload
- New governance procedures needed

**Control:**
- Escalation procedure defined
- Human Gate notification mechanism
- No autonomous decisions allowed

### Audit Layer

**Current State:** Limited decision tracing

**Expected Change:**
- Full audit trail for every decision
- 5-year evidence retention requirements

**Risk:**
- Archive infrastructure required
- Compliance with retention policies

**Control:**
- Archival procedure defined
- Retention enforcement implemented
- Audit queries tested

### Security Layer

**Current State:** No cryptographic binding

**Expected Change:**
- Add SHA256 hashing for evidence
- Add HMAC for authority tokens
- Add signature verification

**Risk:**
- Key management required
- Cryptographic library dependencies

**Control:**
- Security review of crypto implementation
- Key storage procedures
- No keys committed to repository

## Risk Summary

| Layer | Risk Level | Mitigation | Approval |
|-------|-----------|-----------|----------|
| Code | MEDIUM | Review + Test | Required |
| Data | LOW | Validation | Required |
| Governance | MEDIUM | Procedure | Required |
| Audit | MEDIUM | Infrastructure | Required |
| Security | HIGH | Expert Review | **CRITICAL** |

**Critical Path:** Security review must complete before authorization

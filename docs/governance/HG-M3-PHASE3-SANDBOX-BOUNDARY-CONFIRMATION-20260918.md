# HG-M3 Phase 3: Sandbox Boundary Confirmation
**Date:** 2026-09-18 | **Authority:** Conditional Authorization (Option B) | **Status:** PREPARATION

---

## PURPOSE

Confirm that sandbox environment is isolated from production. This document verifies:
- Production environment is completely separated
- No data pathways from sandbox to production
- No code pathways from sandbox to production
- No credential leakage from sandbox to production
- Sandbox cannot accidentally affect production

---

## CONFIRMATION ITEM 1: Environment Isolation

### Confirmation 1.1: Database Separation
**Requirement:** Sandbox database completely separate from production

**Verification Method:**
```
Primary: sqlite3 :memory: OR separate sandbox.db file
Isolated: No shared tables with production
Access: Sandbox code NEVER references production database connection string
Whitelist: Only localhost connection allowed
```

**Confirmation Status:**
- [ ] Database file path confirmed: `/home/user/MoCKA/data/sandbox/sb_phase3.db`
- [ ] Connection string: `sqlite:///data/sandbox/sb_phase3.db`
- [ ] Production connection string NOT in sandbox code
- [ ] No environment variable cross-references

**Evidence:** Git commit will show no production connection strings in Phase 3 branch

---

### Confirmation 1.2: Schema Namespace Isolation
**Requirement:** Sandbox tables prefixed with `sb_` to prevent name collision

**Verification Method:**
```
Sandbox tables:
- sb_decisions (not decisions)
- sb_evidence (not evidence)
- sb_authority_references (not authority_references)
- sb_validation_records (not validation_records)
- sb_audit_references (not audit_references)
```

**Confirmation Status:**
- [ ] All sandbox tables use `sb_` prefix
- [ ] No unprefixed tables in sandbox database
- [ ] Production tables (no prefix) remain untouched
- [ ] SQL queries explicitly reference prefixed names

**Evidence:** Database schema inspection will show namespace separation

---

### Confirmation 1.3: Directory Structure Isolation
**Requirement:** Sandbox code and data in separate directory tree

**Verification Method:**
```
Project Structure:
/home/user/MoCKA/
├── (production code - UNCHANGED)
├── data/
│   ├── (production data - UNCHANGED)
│   └── sandbox/
│       ├── sb_phase3.db (NEW - sandbox database)
│       ├── test_results/ (NEW - test outputs only)
│       ├── validation/ (NEW - validation evidence)
│       └── failures/ (NEW - failure scenario results)
└── (production continues to run)
```

**Confirmation Status:**
- [ ] Sandbox data directory created: `/home/user/MoCKA/data/sandbox/`
- [ ] No production data in sandbox directory
- [ ] No sandbox data in production directories
- [ ] Directory permissions prevent cross-access

**Evidence:** File system audit will show isolation

---

## CONFIRMATION ITEM 2: Runtime Connection Isolation

### Confirmation 2.1: No Production API Access
**Requirement:** Sandbox code cannot call production APIs

**Verification Method:**
```
Configuration: Phase 3 code uses mock/local services ONLY
API Endpoints: All production endpoints hardcoded as PROHIBITED
Whitelist: Only localhost services allowed
Fallback: If production endpoint detected, immediate error/logging
```

**Confirmation Status:**
- [ ] API endpoint configuration reviewed
- [ ] No production API URLs in sandbox code
- [ ] Mock API servers available for testing
- [ ] Connection test confirms isolation (test connection blocked)

**Evidence:** Code review + connection logs will show mock APIs only

---

### Confirmation 2.2: No Credential Leakage
**Requirement:** Sandbox code contains NO production credentials

**Verification Method:**
```
Scan: grep for API keys, passwords, tokens in Phase 3 code
Result: ZERO production credentials found
Fallback: If any credential found, delete and report incident
Storage: All test credentials in .gitignore files (not committed)
```

**Confirmation Status:**
- [ ] Credential audit completed (0 production secrets found)
- [ ] All test credentials in temporary/ignored files
- [ ] .gitignore includes `**/sandbox/` (no secrets committed)
- [ ] No environment variables reference production secrets

**Evidence:** Git audit shows NO production credentials in Phase 3 commits

---

### Confirmation 2.3: Configuration Separation
**Requirement:** Sandbox uses separate configuration file

**Verification Method:**
```
Config Files:
Production: config.production.json (untouched)
Sandbox: config.sandbox.json (NEW - test-only settings)
Activation: Phase 3 code reads ONLY config.sandbox.json
Fallback: If production config detected in sandbox, immediate error
```

**Confirmation Status:**
- [ ] Sandbox config file created: `config.sandbox.json`
- [ ] Sandbox config uses only sandbox values
- [ ] Phase 3 code loads correct config file
- [ ] Config loading verified with test

**Evidence:** Config loading test will confirm separation

---

## CONFIRMATION ITEM 3: Data Scope Isolation

### Confirmation 3.1: Synthetic Data Only
**Requirement:** Sandbox contains ONLY synthetic test data, never production data

**Verification Method:**
```
Data Origin: All sandbox data generated by test fixtures
Quantity: Max 1,000 synthetic decision records for testing
Real Data: ZERO production rows in sandbox database
Purge Plan: Clear sandbox data after Phase 3 (if approved)
```

**Confirmation Status:**
- [ ] Test data generator created (`tests/fixtures/synthetic_data.py`)
- [ ] Synthetic data includes all 8 scenario types
- [ ] Production row count in sandbox: 0
- [ ] Data audit confirms synthetic origin

**Evidence:** Test data logs show fixture-generated data only

---

### Confirmation 3.2: No Production Queries
**Requirement:** Sandbox code never queries production tables

**Verification Method:**
```
Query Audit: All SQL queries reference `sb_*` tables only
Fallback: If unprefixed table reference detected, code won't compile
Schema Guard: Database schema validation rejects production names
```

**Confirmation Status:**
- [ ] SQL query audit completed (all queries use `sb_` prefix)
- [ ] No unprefixed table references found
- [ ] Query execution blocked if production table referenced
- [ ] Test query passes only on prefixed tables

**Evidence:** Query audit log shows 100% sandbox-only queries

---

## CONFIRMATION ITEM 4: Code Integration Isolation

### Confirmation 4.1: No Merge to Production Branch During Phase 3
**Requirement:** Phase 3 code stays on feature branch, never merges to main

**Verification Method:**
```
Branch Strategy: 
- Phase 3 work: claude/adoring-shannon-sj4shv (feature branch)
- Production: main branch (UNTOUCHED)
- Merge Protection: No pull requests to main during Phase 3
- Timeline: Merge decision only AFTER Human Gate re-authorization
```

**Confirmation Status:**
- [ ] Feature branch confirmed: `claude/adoring-shannon-sj4shv`
- [ ] Branch protection rules active (no direct pushes to main)
- [ ] Pull request to main forbidden until Phase 4 authorization
- [ ] Merge button disabled (GitHub branch protection)

**Evidence:** Git branch protection settings will show active rules

---

### Confirmation 4.2: No Production Deployment During Phase 3
**Requirement:** Sandbox code is NOT deployed to production systems

**Verification Method:**
```
Deployment: Sandbox builds to `/home/user/MoCKA/build/sandbox/` only
Production: Production builds from main branch to production server
Isolation: No deployment pipeline connects sandbox to production
Fallback: If sandbox code detected in production, immediate alert
```

**Confirmation Status:**
- [ ] Build process confirmed sandbox-only
- [ ] Production deployment uses main branch only
- [ ] No CI/CD pipeline connects Phase 3 branch to production
- [ ] Deployment validation confirms isolation

**Evidence:** Deployment logs show sandbox → sandbox only

---

### Confirmation 4.3: Testing Isolation
**Requirement:** Tests execute in sandbox containers only

**Verification Method:**
```
Test Execution:
- Unit Tests: Run against sb_phase3.db only
- Integration Tests: Use mock services only
- System Tests: Run in isolated Docker container (if applicable)
Database: No test modifies production database
Results: Test output stored in data/sandbox/test_results/ only
```

**Confirmation Status:**
- [ ] Test database confirmed as sandbox.db
- [ ] Mock API services configured for tests
- [ ] Test results stored in sandbox directory
- [ ] Test cleanup verified (no production changes)

**Evidence:** Test execution logs show sandbox-only operations

---

## CONFIRMATION ITEM 5: Monitoring and Detection

### Confirmation 5.1: Production Access Attempts Detection
**Requirement:** Any attempt to access production is logged and blocked

**Verification Method:**
```
Detection: Logging middleware tracks all connection attempts
Block: If production connection attempted, return error immediately
Alert: Production access attempt logged as CRITICAL incident
Response: Automatic notification to Human Gate
```

**Confirmation Status:**
- [ ] Logging middleware implemented
- [ ] Connection whitelist configured (localhost only)
- [ ] Test: Attempt to access production → blocked + logged
- [ ] Alert system configured (incident to events.db)

**Evidence:** Security logs will show all blocked production access attempts

---

### Confirmation 5.2: Data Leakage Detection
**Requirement:** Any data moving from sandbox to production is detected

**Verification Method:**
```
Audit: Database audit log tracks all writes
Source: Every write must originate from sandbox code
Destination: All writes must go to sb_* tables only
Fallback: If write to production table detected, transaction rolls back
```

**Confirmation Status:**
- [ ] Database audit logging enabled
- [ ] Write-to-production detection configured
- [ ] Test: Attempt write to production table → rolled back + logged
- [ ] Audit trail complete

**Evidence:** Audit logs show ZERO writes to production tables

---

### Confirmation 5.3: Credential Leak Detection
**Requirement:** Any leaked production credential is detected and reported

**Verification Method:**
```
Scanning: Automated credential detection on every commit
Webhook: Pre-commit hook scans for API keys/passwords
Result: Commits containing credentials are rejected
Report: Credential scan results in events.db incident
```

**Confirmation Status:**
- [ ] Pre-commit hook installed (git/hooks/pre-commit)
- [ ] Credential detection library configured (detect-secrets)
- [ ] Test: Attempt to commit credential → rejected
- [ ] Scan results stored in events.db

**Evidence:** Git hooks will prevent credential commits

---

## SANDBOX BOUNDARY CONFIRMATION CHECKLIST

### Database Layer
- [ ] Sandbox database isolated (separate file)
- [ ] Schemas use `sb_` prefix
- [ ] No production table access from sandbox code
- [ ] Connection string verified

### Environment Layer
- [ ] Configuration files separate (config.sandbox.json)
- [ ] No production credentials in sandbox code
- [ ] API endpoints point to mock services only
- [ ] Environment variables correctly set

### Code Layer
- [ ] Phase 3 code on feature branch only
- [ ] No merges to main branch during Phase 3
- [ ] Build artifacts sandbox-only
- [ ] Deployment disabled during Phase 3

### Data Layer
- [ ] Synthetic test data only (no production data)
- [ ] Data audit confirms fixture origin
- [ ] Purge plan prepared for post-Phase-3
- [ ] Data scope limited (max 1,000 records)

### Integration Layer
- [ ] Tests run in sandbox environment only
- [ ] Mock APIs configured
- [ ] Test results sandbox-only
- [ ] Production systems untouched

### Monitoring Layer
- [ ] Production access attempts detected and blocked
- [ ] Data leakage detection active
- [ ] Credential leak detection active
- [ ] Alerts configured to events.db

---

## CONFIRMATION FINAL STATUS

**Sandbox Boundary Integrity: READY FOR VERIFICATION**

All requirements for sandbox isolation are defined and verifiable. Implementation team can proceed with Phase 3 work within confirmed boundaries.

**Entry Condition:** All checkboxes above must be checked before implementation starts.

**Exit Condition:** All monitoring systems must show zero boundary violations during and after Phase 3.

---

**SANDBOX BOUNDARY DEFINITION COMPLETE**


# Decision Candidate 1: DI1 Evidence Conflict Priority Rule

**Candidate ID**: DI1_DC_01_20260820  
**Related**: DI1_DI2_UNKNOWN_LIST.md - Unknown 1.5  
**Status**: CANDIDATE (awaiting Human Gate decision)  
**Created**: 2026-08-20  
**For**: Human Gate (博士)

---

## The Decision

When approving an artifact, multiple evidence items may contradict each other. The system must have a rule to resolve contradictions.

**Examples of Contradiction**:
1. Code review says "Safe" but Security scan says "Vulnerability detected"
2. Design review approves design but Implementation contradicts design assumptions
3. Multiple security scans report different severity levels

**What This Decision Determines**: 
- How the approval validation system handles evidence contradictions
- Whether contradictions are automatically resolved or escalated for manual review
- Which evidence types take precedence in case of conflict

---

## Option 1: Escalate to Human Gate (Recommended)

### Description

When contradiction is detected, do not automatically approve. Instead, escalate to Human Gate for manual adjudication.

### Mechanism

```
Evidence Validation:
  ├─ Check for contradictions between evidence items
  ├─ If contradiction found:
  │   ├─ Log contradiction with both evidence items
  │   ├─ Create escalation request to Human Gate
  │   ├─ Wait for Human Gate decision
  │   └─ Issue approval or rejection based on decision
  └─ If no contradiction:
      └─ Issue approval (normal path)
```

### Implementation

- Error code: APPR_E003 (contradictory evidence detected)
- Recovery action: MANUAL_REVIEW_REQUIRED
- Timeline: Escalation notification sent immediately; decision timeline TBD

### Pros

- **Safety**: No automation of contradiction resolution; human judgment applied
- **Transparency**: Every contradiction is visible to Human Gate
- **Flexibility**: Human Gate can make case-by-case decisions
- **Governance**: Aligns with MoCKA principle of explicit human oversight

### Cons

- **Speed**: Contradictions delay approval (escalation + decision time)
- **Throughput**: Operations may queue up waiting for Human Gate decisions
- **Scalability**: If contradictions are frequent, Human Gate becomes bottleneck

### Recommendation

✓ **RECOMMENDED** - Maintains highest governance standard

---

## Option 2: SECURITY > DESIGN > CODE Precedence

### Description

Establish automatic precedence rule: Security findings always override other approvals.

### Mechanism

```
Evidence Validation:
  ├─ Collect all evidence items
  ├─ Assign priority to each:
  │   ├─ SECURITY: 1 (highest)
  │   ├─ DESIGN: 2
  │   ├─ CODE: 3 (lowest)
  ├─ Check highest priority evidence
  ├─ If SECURITY says "vulnerable":
  │   └─ REJECT approval (security takes precedence)
  └─ If SECURITY says "safe":
      └─ Check DESIGN (if no security evidence)
```

### Implementation

- Precedence rule stored in configuration
- Validation logic implements priority checking
- Contradictions resolved automatically (no Human Gate involvement)

### Pros

- **Speed**: Automatic resolution, no escalation needed
- **Clarity**: Simple, unambiguous rule
- **Security-first**: Security concerns always protected

### Cons

- **Inflexibility**: Rule might be inappropriate for some edge cases
- **Blind automation**: Might reject legitimate approvals if security tool has false positive
- **Override complexity**: If override is needed, requires separate exception mechanism

### Recommendation

❌ **NOT RECOMMENDED** - Too restrictive for governance

---

## Option 3: Most Recent Evidence Wins

### Description

Whichever evidence item was generated most recently (highest timestamp) takes precedence.

### Mechanism

```
Evidence Validation:
  ├─ Collect all evidence items with timestamps
  ├─ Find item with most recent timestamp
  ├─ Use that item's verdict (safe/vulnerable)
  └─ Issue approval or rejection based on most recent evidence
```

### Implementation

- Timestamp comparison logic
- Automatic selection of highest timestamp
- No Human Gate involvement

### Pros

- **Speed**: Fully automated, immediate resolution
- **Simple**: Easy to understand and implement
- **Responsive**: Latest information always used

### Cons

- **Unsafe**: Recent update might be mistaken or incomplete
- **Gaming**: Could be manipulated (re-run scan with false result)
- **Ignores older evidence**: Might reject stable approval based on single new scan

### Recommendation

❌ **NOT RECOMMENDED** - Too prone to errors

---

## Decision Matrix

| Aspect | Option 1: Escalate | Option 2: Security Priority | Option 3: Recent First |
|--------|---|---|---|
| **Safety** | ✓ High | ✓ High (security) | ✗ Low |
| **Speed** | ✗ Slow (escalation) | ✓ Fast (automatic) | ✓ Fast (automatic) |
| **Governance** | ✓ Explicit | ⚠ Semi-automatic | ✗ Fully automatic |
| **Human Control** | ✓ High | ⚠ Medium (rules defined) | ✗ None |
| **Flexibility** | ✓ Case-by-case | ✗ Rule-bound | ✗ Rule-bound |

---

## Related Design Elements

**In DI1_DESIGN_SPECIFICATION_DRAFT.md**:
- §3 (Data Handling Model) - Consistency Rule for evidence precedence
- §4 (Failure Conditions) - Failure Condition 3: Contradictory evidence handling
- §5 (Evidence Recording) - Evidence Registry indexing for contradiction detection

**In DI1_DI2_UNKNOWN_LIST.md**:
- Unknown 1.5: This decision

**In DI1_DI2_RISK_LIST.md**:
- Risk 2: Approval evidence contradictions not resolved

---

## Human Gate Decision Form

**Which option do you choose?**

- [ ] Option 1: Escalate to Human Gate (RECOMMENDED)
- [ ] Option 2: SECURITY > DESIGN > CODE precedence
- [ ] Option 3: Most recent evidence wins
- [ ] Other (please specify):

**If OTHER, please provide**:
- [ ] Precedence rule (if applicable)
- [ ] Implementation mechanism
- [ ] Rationale

**Additional Notes/Constraints**:

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Candidate | Claude (Phase 4 Review Prep) | Initial decision candidate |


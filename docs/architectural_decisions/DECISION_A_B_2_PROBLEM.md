# Architecture Decision: A+B/2 Problem Solution

## Context

Multiple AI agents (Claude, GPT, Gemini, Codex) propose solutions to reasoning tasks.
How do we: (1) prevent reasoning bias, (2) form consensus, (3) make binding decisions?

### The Problem

Naive averaging: `Decision = (A_proposal + B_proposal) / 2` is mathematically unsafe.
- Non-commutativity: logical AND/OR don't distribute like arithmetic
- Type mismatch: mixing boolean, categorical, numerical proposals fails
- Authority collapse: equal weighting ignores confidence/evidence quality

### JARVIS Requirement

Reasoning Layer (L4) must synthesize multi-AI input without:
- Blind averaging (unsafe)
- Arbitrary weighting (unmotivated)
- Single-AI veto (misses diversity benefit)

---

## Decision

Implement A+B/2 as **Weighted Attribute Synthesis** (NOT numeric averaging):

1. **Decompose** each proposal into attributes (rationale, risks, evidence)
2. **Weight** each attribute by evidence quality + consensus degree
3. **Synthesize** final decision via attribute voting (not averaging)
4. **Record** reasoning chain in Decision Ledger (transparent)
5. **Human Gate** reviews synthesized result (final authority)

### Definition: Weighted Attribute Synthesis

```
Multiple Proposals {A, B, C, ...}
        ↓
Decompose to Attributes:
  A = {attr_1: val_A1, attr_2: val_A2, ...}
  B = {attr_1: val_B1, attr_2: val_B2, ...}
  C = ...
        ↓
Evidence Quality Scoring (0-1):
  evidence_A = quality(rationale_A, test_coverage_A, uncertainty_A)
  evidence_B = quality(rationale_B, test_coverage_B, uncertainty_B)
        ↓
Attribute-level Consensus:
  For each attribute:
    - Extract AI opinions (votes)
    - Calculate consensus degree (0-1)
    - Assign weight = evidence_quality * consensus_degree
        ↓
Synthesis:
  For each attribute:
    IF consensus >= 0.8:
      → Use consensus value (high confidence)
    ELIF consensus >= 0.5:
      → Mark as "trade-off required" (route to Human Gate)
    ELSE:
      → Mark as "divergence flag" (note all proposals, needs review)
        ↓
Synthesized Decision
        ↓
Human Gate Review (final authority)
```

---

## Implementation Rules

### Rule 1: Attribute Decomposition

Every proposal must express as attribute vector:

```json
{
  "proposal_id": "claude_20260813_001",
  "proposer": "Claude-haiku-4-5",
  "timestamp": "2026-08-13T13:00:00Z",
  "attributes": {
    "recommended_action": "integrate",
    "risk_assessment": "low",
    "implementation_cost_days": 2.5,
    "confidence_score": 0.87,
    "rationale_summary": "Breaking change affects secondary component only...",
    "evidence": {
      "tests_passed": 12,
      "edge_cases_examined": 5,
      "uncertainty_factors": ["timing conflict", "test coverage gap"]
    }
  }
}
```

### Rule 2: Evidence Quality Scoring

```
evidence_quality = (
  test_coverage_ratio * 0.4 +
  rationale_coherence * 0.3 +
  (1 - uncertainty_normalized) * 0.3
)
```

Where:
- `test_coverage_ratio`: 0-1, higher is better
- `rationale_coherence`: semantic consistency check (0-1)
- `uncertainty_normalized`: [0,1], 0=certain, 1=total uncertainty

### Rule 3: Consensus Calculation

```
attribute_consensus = (
  COUNT(proposals_agreeing) / COUNT(all_proposals)
  * (1 - std_deviation(attribute_values))
)
```

High consensus: >0.8 (strong agreement + low variance)
Medium consensus: 0.5-0.8 (agreement but some variance)
Low consensus: <0.5 (significant divergence)

### Rule 4: Synthesis Decision Tree

```
For each attribute:

if consensus_score >= 0.8:
  → Use consensus value
  → Confidence: HIGH
  
elif consensus_score >= 0.5:
  → Use weighted average of proposals
  → Flag as "trade-off required"
  → Route to Human Gate
  → Confidence: MEDIUM
  
else:  # consensus_score < 0.5
  → Record ALL proposals
  → Flag as "divergence, needs human judgment"
  → Route to Human Gate with full evidence
  → Confidence: LOW (multiple valid paths)
```

### Rule 5: Recording in Decision Ledger

Every A+B/2 synthesis MUST record:

```jsonl
{
  "decision_id": "DC_20260813_XYZ",
  "decision_type": "synthesis",
  "title": "Impact Analysis Recommendation - Tech Dependency Update",
  "timestamp": "2026-08-13T13:15:00Z",
  "inputs": {
    "proposals": [
      {
        "proposer": "Claude",
        "evidence_quality": 0.87,
        "recommendation": "test_more"
      },
      {
        "proposer": "GPT",
        "evidence_quality": 0.82,
        "recommendation": "integrate"
      }
    ]
  },
  "synthesis_process": {
    "decomposed_attributes": ["action", "risk", "cost", "confidence"],
    "attribute_consensus_scores": {
      "action": 0.45,
      "risk": 0.78,
      "cost": 0.82,
      "confidence": 0.65
    },
    "high_confidence_attributes": ["risk", "cost"],
    "needs_human_review": ["action", "confidence"]
  },
  "synthesized_result": {
    "recommended_action": "test_more_with_risk_monitoring",
    "cost_estimate": 2.6,
    "risk_level": "medium",
    "confidence": 0.73
  },
  "human_gate_routing": "HG-review-required",
  "rationale": "Strong consensus on risk and cost. Action divergence (test_more vs integrate) routed to Human Gate."
}
```

---

## Implementation Artifacts

### 1. Reasoning Rule Codification

**File:** `governance/a_b_2_synthesis_rules.json`

```json
{
  "version": "1.0",
  "rules": {
    "consensus_threshold_high": 0.80,
    "consensus_threshold_medium": 0.50,
    "evidence_quality_weights": {
      "test_coverage": 0.40,
      "rationale_coherence": 0.30,
      "uncertainty": 0.30
    },
    "synthesis_method": "weighted_attribute_voting",
    "human_gate_triggers": [
      "consensus_score < 0.80",
      "confidence_score < 0.75",
      "risk_assessment_divergence"
    ]
  }
}
```

### 2. Reasoning Principle (Human-Facing)

**File:** `docs/reasoning_principles/A_B_2_PRINCIPLE.md`

This is a REASONING PRINCIPLE, not a code-embedded algorithm.

AI agents should internalize:
1. Always decompose proposals into attributes
2. Score evidence for each proposal
3. Calculate consensus per attribute (not per proposal)
4. Flag low-consensus attributes for human review
5. Record synthesis reasoning in Decision Ledger
6. NEVER auto-decide when consensus < 0.75

### 3. Human Gate Integration

**Update to:** `governance_pipeline.py`

```python
class HumanGateRules:
    def check_synthesis_decision(self, decision: dict):
        """A+B/2 synthesis decision validation"""
        
        if decision.get('type') == 'synthesis':
            consensus_scores = decision.get('synthesis_process', {}).get('attribute_consensus_scores', {})
            
            # Auto-approve only if ALL attributes high consensus
            if all(score >= 0.80 for score in consensus_scores.values()):
                return {'action': 'auto_approve', 'confidence': 0.95}
            
            # Otherwise: route to Human Gate
            return {
                'action': 'human_review_required',
                'rationale': f'Low consensus on {count_low_consensus(consensus_scores)} attributes',
                'divergence_flags': extract_divergence_flags(decision)
            }
```

---

## Decision Record

**Decision ID:** DC_A_B_2_PROBLEM_SOLUTION

**Adopted:** 2026-08-13

**Authority:** JARVIS Architecture Consolidation Period - Priority 3

**Rationale:**
- Weighted Attribute Synthesis is mathematically safe (no invalid type mixing)
- Consensus-driven (respects multi-AI diversity)
- Transparent (full reasoning chain recorded)
- Human-centered (low-confidence decisions escalated)
- Operationalizable (rules + Decision Ledger recording)

**Alternatives Considered:**
1. ~~Naive averaging~~ - Mathematically unsafe, type mismatch
2. ~~Veto authority~~ - Single AI dominates, loses diversity benefit
3. ~~Ranking + selection~~ - Arbitrary weighting, not transparent
4. **Weighted Attribute Synthesis** ✓ Adopted

**Success Criteria:**
- [ ] Synthesis rules codified in `a_b_2_synthesis_rules.json`
- [ ] 3+ multi-AI reasoning chains successfully synthesized
- [ ] All syntheses recorded in Decision Ledger
- [ ] Human Gate properly routes low-consensus decisions
- [ ] Z-axis (Governance Stability) stable during multi-AI reasoning

---

## Integration with JARVIS

### Reasoning Layer (L4) Enhancement

```
Multiple AI Agents (Claude, GPT, Gemini, Codex)
        ↓
Proposal Generation (with evidence)
        ↓
A+B/2 Weighted Attribute Synthesis
        ↓
Consensus Scoring per Attribute
        ↓
IF high_consensus_all_attributes:
  → Synthesized Decision
ELSE:
  → Flag for Human Gate
        ↓
Human Gate (final authority)
        ↓
Event Gate (recording)
        ↓
P-DERS (immutable ledger)
```

### Connection to Governance Layer (L3)

A+B/2 synthesis provides **evidence-weighted reasoning** to Human Gate.
Human Gate makes final **authority decision**.
Outcome recorded in Decision Ledger as institutional knowledge.

---

## References

- JARVIS Architecture Mapping v1.0: Reasoning Layer (L4)
- MoCKA Theory Implementation Audit: A+B/2 Problem (0% → Principle Stage)
- TODO_453: Priority 3 implementation
- Decision Ledger schema: TODO_361

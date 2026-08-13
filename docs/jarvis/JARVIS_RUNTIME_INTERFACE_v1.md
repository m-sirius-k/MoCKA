# JARVIS Runtime Interface v1.0

Unified integration point for MoCKA → JARVIS architecture.

---

## Overview

JARVIS is not a new monolith. It's the **coherent integration layer** over existing MoCKA components.

```
MoCKA Components (operational, proven)
  ├─ p-DERS (event store)
  ├─ PHL (essence pipeline)
  ├─ DNA Packet (pattern injection)
  ├─ Fluid Coordinate (state model)
  ├─ Decision Ledger (governance records)
  ├─ Integrity Classification (anomaly detection)
  ├─ Human Gate (authority boundary)
  ├─ Event Gate (execution safety)
  ├─ BEE v2.0 (evidence validation)
  └─ Connector Framework (AI capability registry)
        ↓
   JARVIS Runtime Interface
   (orchestration + coordination)
        ↓
   5-Layer JARVIS Architecture
   (Perception, Memory, Governance, Reasoning, Execution Safety)
```

---

## JARVIS Runtime Interface Specification

### 1. Interface Definition

**File:** `runtime/jarvis_runtime_interface.py`

```python
class JARVISRuntime:
    """
    Unified JARVIS interface orchestrating MoCKA components.
    
    Responsibilities:
    - Component lifecycle management
    - Signal flow routing
    - State consistency
    - Error handling
    """
    
    def __init__(self):
        # Layer 1: Perception
        self.perception = PerceptionLayer(
            health_check=HealthCheck(),
            tech_watcher=TechWatcher(),
            tic_sandbox=TechLabSandbox(),
            impact_analyzer=ImpactAnalyzer(),
            context_vector=ContextVectorExtractor(),
        )
        
        # Layer 2: Memory
        self.memory = MemoryLayer(
            event_store=EventStore(db_path=DB_PATH),
            essence_pipeline=EssencePipeline(),
            dna_injector=DNAPacketInjector(),
            living_context=LivingContext(),
        )
        
        # Layer 3: Governance
        self.governance = GovernanceLayer(
            human_gate=HumanGate(),
            event_gate=EventGate(),
            decision_ledger=DecisionLedger(),
            integrity_classifier=IntegrityClassifier(),
            constitution=MoCKAConstitution(),
        )
        
        # Layer 4: Reasoning
        self.reasoning = ReasoningLayer(
            ai_connectors=ConnectorFramework(),
            evidence_validator=BEE(),
            trust_scorer=TrustScoreVector(),
            a_b_2_synthesizer=WeightedAttributeSynthesis(),
        )
        
        # Layer 5: Execution Safety
        self.execution_safety = ExecutionSafetyLayer(
            p_ders=PersistentDistributedEventRecord(),
            veto_authority=VetoAuthority(),
            runtime_verifier=RuntimeVerifier(),
        )
        
        self._state = SystemState()
        self._logger = EventLogger()
```

### 2. Signal Flow Routing

**Core lifecycle**: Observation → Record → Decide → Act → Audit

```python
class JARVISRuntime:
    
    def cycle_observe(self) -> ObservationState:
        """Layer 1: Perception - Acquire current state"""
        
        # Parallel observation from all L1 sensors
        health = self.perception.health_check.sample()
        tech_changes = self.perception.tech_watcher.detect_changes()
        context = self.perception.context_vector.extract_at(now())
        
        state = ObservationState(
            timestamp=now(),
            health=health,
            tech_changes=tech_changes,
            context_influences=context.S_vector,
            xyz_coordinate=(X, Y, Z),
        )
        
        self._state.update(state)
        return state
    
    def cycle_record(self, observation: ObservationState) -> Event:
        """Layer 2: Memory - Persist and integrate"""
        
        # Write to p-DERS
        event = self.memory.event_store.write(
            title=observation.summary,
            description=observation.details,
            timestamp=observation.timestamp,
        )
        
        # Inject patterns
        self.memory.dna_injector.inject_patterns(event)
        
        # Update essence
        self.memory.essence_pipeline.update(observation)
        
        self._logger.record('cycle:record', event_id=event.id)
        return event
    
    def cycle_decide(self, observation: ObservationState) -> Decision:
        """Layer 3-4: Governance + Reasoning - Form decision"""
        
        # L4: AI Reasoning (multi-agent synthesis)
        proposals = []
        for ai in self.reasoning.ai_connectors.active_agents():
            proposal = ai.analyze(observation, context=self._state)
            proposals.append(proposal)
        
        # L4: A+B/2 Synthesis
        synthesized = self.reasoning.a_b_2_synthesizer.synthesize(proposals)
        
        # L3: Evidence Validation
        evidence = self.reasoning.evidence_validator.validate(synthesized)
        
        # L3: Human Gate Review
        decision = self.governance.human_gate.review(
            proposal=synthesized,
            evidence=evidence,
            context=self._state,
        )
        
        # Record in Decision Ledger
        self.governance.decision_ledger.write(decision)
        
        self._logger.record('cycle:decide', decision_id=decision.id)
        return decision
    
    def cycle_act(self, decision: Decision) -> ExecutionResult:
        """Layer 5: Execution Safety - Implement with guardrails"""
        
        # L5: Runtime Verification (pre-execution check)
        verified = self.execution_safety.runtime_verifier.verify(decision)
        if not verified.is_safe:
            return ExecutionResult(
                status='blocked',
                reason=verified.reason,
            )
        
        # L5: Event Gate (veto authority)
        approved = self.execution_safety.veto_authority.can_proceed(decision)
        if not approved:
            return ExecutionResult(
                status='vetoed',
                reason='Event Gate veto',
            )
        
        # Execute action
        result = self._execute_action(decision)
        
        # L5: Immediate recording (immutable history)
        self.execution_safety.p_ders.write_execution_record(result)
        
        self._logger.record('cycle:act', result_id=result.id)
        return result
    
    def cycle_audit(self, decision: Decision, result: ExecutionResult):
        """Post-action audit + institutional learning"""
        
        # Integrity check
        integrity = self.governance.integrity_classifier.check(
            decision=decision,
            result=result,
        )
        
        # Record anomalies
        if integrity.has_anomaly:
            self.governance.integrity_classifier.record_anomaly(integrity)
        
        # Institutional reflection (BEE)
        self.reasoning.evidence_validator.reflect(
            outcome=result,
            expected=decision,
        )
        
        # Update coordinate trajectory
        new_xyz = self._calculate_new_coordinate(decision, result)
        self.perception.context_vector.record_state(new_xyz)
        
        self._logger.record('cycle:audit', integrity_id=integrity.id)
```

### 3. State Consistency Management

```python
class SystemState:
    """Current institutional + technical state"""
    
    def __init__(self):
        self.xyz_coordinate: Tuple[float, float, float]  # (X, Y, Z)
        self.s_influences: SituationalInfluenceSet       # (H, P, B, T, TC, SD, OC)
        self.timestamp: str
        self.health_status: HealthStatus
        self.tech_context: TechContext
        self.governance_status: GovernanceStatus
        self.recent_decisions: List[Decision]
        self.anomalies_flagged: List[IntegrityIssue]
    
    def consistency_check(self) -> ValidationResult:
        """Verify state across layers"""
        
        # Layer 1: Perception consistency
        perceived_z = self.health_status.calculate_z()
        assert abs(perceived_z - self.xyz_coordinate.Z) < 0.05
        
        # Layer 2: Memory consistency
        event_count = self.event_store.count()
        ledger_count = self.decision_ledger.count()
        assert event_count >= ledger_count  # More events than decisions
        
        # Layer 3: Governance consistency
        assert self.governance_status.has_authority  # Human Gate always active
        
        # Layer 4-5: Reasoning + Execution consistency
        pending_decisions = self.reasoning.pending_proposals()
        assert len(pending_decisions) < 10  # Backpressure limit
        
        return ValidationResult(is_consistent=True)
```

### 4. Error Handling & Graceful Degradation

```python
class JARVISRuntime:
    
    def run_cycle_with_resilience(self, max_retries=3):
        """Single cycle with recovery"""
        
        for attempt in range(max_retries):
            try:
                # Normal cycle
                obs = self.cycle_observe()
                evt = self.cycle_record(obs)
                dec = self.cycle_decide(obs)
                res = self.cycle_act(dec)
                self.cycle_audit(dec, res)
                
                return res
                
            except IntegrityViolation as e:
                # Institutional safety breach
                self._logger.error(f"Integrity violation: {e}")
                self.governance.human_gate.escalate(e)
                raise  # Do not retry
                
            except TechWatcherAlert as e:
                # External technology change
                self._logger.warning(f"Tech alert: {e}")
                # Route to sandbox, don't block main cycle
                self.perception.tic_sandbox.create_experiment(e)
                
            except HumanGateVeto as e:
                # Decision rejected
                self._logger.info(f"HG veto: {e}")
                return ExecutionResult(status='vetoed', reason=str(e))
                
            except Exception as e:
                if attempt < max_retries - 1:
                    self._logger.warning(f"Attempt {attempt+1} failed: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self._logger.error(f"Final attempt failed: {e}")
                    # Shadow movement (degraded mode)
                    return self._shadow_movement_fallback(obs)
```

### 5. Observability & Introspection

```python
class JARVISRuntime:
    
    def get_runtime_status(self) -> RuntimeStatus:
        """Complete system health snapshot"""
        
        return RuntimeStatus(
            timestamp=now(),
            state=self._state,
            layer_status={
                'perception': self.perception.health(),
                'memory': self.memory.health(),
                'governance': self.governance.health(),
                'reasoning': self.reasoning.health(),
                'execution_safety': self.execution_safety.health(),
            },
            xyz_coordinate=self._state.xyz_coordinate,
            s_influences=self._state.s_influences,
            pending_decisions=self.reasoning.pending_count(),
            integrity_issues=self.governance.integrity_classifier.open_issues(),
            recent_events=self.memory.event_store.recent(n=10),
            system_health_score=self._compute_health_score(),
        )
    
    def get_decision_audit_trail(self, decision_id: str) -> DecisionAuditTrail:
        """Full reasoning chain for a decision"""
        
        decision = self.governance.decision_ledger.get(decision_id)
        return DecisionAuditTrail(
            decision=decision,
            observations_that_led_to_it=...,
            ai_proposals_considered=...,
            evidence_validation_results=...,
            human_gate_review=...,
            event_gate_verification=...,
            execution_result=...,
            post_action_audit=...,
        )
```

---

## Integration Checklist

- [ ] **Perception Layer (L1)**: All 4 sensors operational (health, tech_watch, context, sandbox)
- [ ] **Memory Layer (L2)**: Event store + essence pipeline + DNA injection
- [ ] **Governance Layer (L3)**: Human Gate + Event Gate + Decision Ledger + Integrity
- [ ] **Reasoning Layer (L4)**: AI Connectors + BEE + A+B/2 Synthesis
- [ ] **Execution Safety (L5)**: p-DERS + veto authority + runtime verification
- [ ] **State Consistency**: xyz + S vectors + anomaly flags synchronized
- [ ] **Observability**: Full audit trails + health snapshots available
- [ ] **Error Handling**: Graceful degradation + shadow movement fallback
- [ ] **Human Gate Authority**: Veto power confirmed, override-proof
- [ ] **Decision Ledger Recording**: 100% decision capture in JSONL

---

## Operational Modes

### Normal Mode

```
Continuous cycle: Observe → Record → Decide → Act → Audit
Interval: 30 seconds (tunable)
Human Gate: Review > 0.75 confidence decisions
Decision Ledger: All decisions recorded
```

### Degraded Mode (Shadow Movement)

```
Conditions: Major component failure OR Human Gate override
Changes:
  - Observation: Reduce sampling frequency
  - Recording: Local-only (no external sync)
  - Deciding: Simplified rules (no AI synthesis)
  - Acting: Maintenance mode (no institutional changes)
  - Auditing: Local-only

Fallback: 75% functional capability maintained
```

### Human Gate Override

```
Condition: Human (Dr. Kimura) invokes override
Effect:
  - All AI reasoning suspended
  - Direct authority through Event Gate
  - Full recording maintained (transparency)
  - Z-axis may drop (governance stability impact)
  - Log: "Human override, decision: ..."
```

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Observation latency | < 1s | Acceptable |
| Record-to-Ledger latency | < 2s | Acceptable |
| Decision synthesis time | 3-10s | Acceptable |
| Human Gate review time | 10s-1min | HG paced |
| Event Gate veto latency | < 0.5s | Critical |
| p-DERS append latency | < 0.1s | Append-only |
| Cycle throughput | 2-3 cycles/min | Sustainable |

---

## References

- JARVIS Architecture Mapping v1.0: 5-layer structure
- MoCKA Theory Implementation Audit: Component status matrix
- MOCKA_OVERVIEW.json: Current component paths
- Decision Ledger schema: TODO_361
- Integrity Classification: TODO_350

# NIST Requirement Catalog v1.0

**Source document:** *NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure — Community of Interest Discussion Draft*, Jul 7, 2026. Authors: Raymond Sheh and Martin Stanley (aiciprof@nist.gov), NIST ITL. Status printed on every page of the source: **"NOT OFFICIAL GUIDANCE, FOR DISCUSSION ONLY"** — a work-in-progress draft circulated to a Community of Interest ahead of the formal comment period.

**Source file used for this extraction:** `X:\down\DiscussionDraft_NIST_AIRMF_TACIP_20260707.pdf` (16 pages, provided directly by the requester in-session). Full text extracted via `pdftotext -layout` and read in its entirety (3,622 lines / 4 read passes, no section skipped). This supersedes the earlier finding that only the 2026-04-07 Concept Note was obtainable; that finding is preserved for the record in `MOCKA_EVIDENCE_MATRIX_v1.0.md`.

**Provenance chain (why this document is treated as canonical for this audit):** (1) provided directly by the requester within this session — highest priority per explicit instruction; (2) not found elsewhere in local repositories; (3) not found in general public web search at the time of the earlier search pass (see Evidence Matrix). Readers relying on this catalog should independently confirm they hold the same draft, since the source explicitly states it is a fluid work-in-progress ("Please expect rough text, incomplete sections... as we trial options and rapidly integrate ongoing feedback").

---

## 0. Extraction Method and ID Scheme

This catalog does **not** invent a new ID scheme. The source document itself assigns unique identifiers to **Practices** (1–12, with 13+ reserved/TBD) and **Tasks** (`<Practice>.<Task>`, e.g. `3.2`), and enumerates **Implementations** (`<Practice>.<Task>.<Implementation>`, e.g. `3.2.3`) as illustrative (non-exhaustive) examples. This catalog reuses those IDs verbatim rather than assigning arbitrary new ones, so that any claim here can be checked directly against the source PDF by page/ID.

- **Practice** = governance-level objective, audience: CI Asset Owners / C-Suite / Strategic Managers. This is the level the source calls "requirement" in the practical sense — each Practice is the unit with a stated "unique identifier."
- **Task** = discrete, assignable, independently-executable step under a Practice, audience: Technical Managers / Compliance Officers / Operations Leads. **Tasks are the operative unit used for the Mapping table in Task 2 of this audit** (53 Tasks total across Practices 1–12).
- **Implementation** = illustrative example of how to fulfill a Task, audience: Engineering/Field/Vendor personnel. The source is explicit that Implementations are *not exhaustive and not a checklist*; a large fraction are placeholder stubs marked **`(TBD — suggestions welcome)`** in the source itself — this catalog preserves that TBD marking rather than inventing content to fill it.
- Practices 13, 14, 15, etc. are explicitly reserved as **`(TBD)`** in the source — the document invites the Community of Interest to propose additional Practices. No content exists yet for these; they are listed here only because their absence is itself part of the source document's current state.

**Category classification.** The user-specified category taxonomy (Govern / Map / Measure / Manage / Human Oversight / Risk / Transparency / Validation / Monitoring / Supply Chain / Incident / Lifecycle / Critical Infrastructure / Operational Guidance) is **not** a taxonomy the source document itself uses to label Practices. The source's own primary structural mapping is to the four AI RMF 1.0 core functions (**Govern, Map, Measure, Manage**), cited per-Task under "Primary AI RMF Mappings." Categories beyond those four (Human Oversight, Risk, Transparency, Validation, Monitoring, Supply Chain, Incident, Lifecycle, Critical Infrastructure, Operational Guidance) are applied in this catalog as an **editorial cross-reference layer added by this audit**, judged from each Practice/Task's actual content and stated AI RMF subcategory citations. This is flagged explicitly so the classification is not mistaken for something NIST itself asserts.

**Scope decision on Implementations:** given ~140 Implementation-level entries across the 12 Practices, many of which are one-line TBD stubs with no extractable content, this catalog lists Implementation titles/one-line content under each Task rather than reproducing full implementation text. Every Implementation that has real (non-TBD) content is named; TBD stubs are marked as such rather than omitted, so the catalog reflects the source's actual completeness state.

---

## 1. Reference Tables (verbatim from source)

### Table 1 — The 16 Critical Infrastructure Sectors (CISA / PPD-21)
Chemical · Commercial Facilities · Communications · Critical Manufacturing · Dams · Defense Industrial Base · Emergency Services · Energy · Financial Services · Food and Agriculture · Transportation Systems · Information Technology · Healthcare and Public Health · Nuclear Reactors, Materials, and Waste · Government Services and Facilities · Water and Wastewater Systems

### Table 2 — Trustworthy AI Characteristics as re-interpreted for Critical Infrastructure
| Characteristic | Source description |
|---|---|
| **Safe** | Supports the functional safety of CI systems, reducing risk to human life, property, or the environment from AI-driven actions. |
| **Secure** | Addresses the heightened adversarial interest in CI systems by protecting the integrity of AI-enabled processes. |
| **Resilient** | Decoupled from cyber-defense to target systemic, operational, and physical robustness; enhances service continuity by facilitating AI system robustness and graceful degradation. |
| **Explainable & Interpretable / Accountable & Transparent** | Supports situational awareness and regulatory oversight, facilitates post-event investigation via true forensic telemetry (not statistical reconstructions), promotes community trust. |
| **Privacy Enhanced** | Reduces risk of unauthorized exposure or inadvertent ingestion of sensitive CI telemetry, proprietary facility data, and personal information. |
| **Fair** | Promotes equitable service delivery by identifying/mitigating biases in AI-mediated allocation or performance, including uneven detection/performance across equipment types, populations, or operating conditions. |
| **Accurate, Valid, Reliable, & Bias Managed** | Supports operational dependability by aligning engineering and statistical performance with mission requirements across long CI system lifecycles. |

### Scope note (verbatim intent)
"AI systems can vary in unpredictable ways... performance or efficiency gains must not introduce unmitigated brittleness or run the risk of degrading essential operational skillsets." The profile explicitly **deconflicts** with the still-drafting NIST Cyber AI Profile (IR 8596) — cybersecurity control-level specifics are deferred to that document; this profile addresses *operational and consequence-containment* practice. All "Primary Cyber AI Profile Mappings" fields in the source are blank/TBD pending IR 8596 publication.

---

## 2. Requirement Catalog by Practice

Legend for **Category** column: G=Govern, M=Map, Ms=Measure, Mg=Manage, HO=Human Oversight, R=Risk, T=Transparency, V=Validation, Mo=Monitoring, SC=Supply Chain, I=Incident, L=Lifecycle, CI=Critical Infrastructure (cross-cutting on all 12; noted only where the CI-specificity is the dominant point), OG=Operational Guidance.

---

### Practice 1 — Establish requirements for success
**Category:** G, M, Ms, OG
Define performance, safety, and security benchmarks so AI-driven systems align with organizational mission and operational resilience. Primary AI RMF Mappings (Task 1.1): Govern 1.1, Govern 1.2.

| Task | Content | AI RMF mapping | Implementations (source titles; TBD = stub) |
|---|---|---|---|
| 1.1 Identify current requirements | Catalog functional/safety/performance requirements the AI system supports or augments; grounds AI objectives in mission-critical benchmarks. | Govern 1.1, 1.2 | 1.1.1 Operational baseline review; 1.1.2 Structured requirements mapping |
| 1.2 Create quantitative baselines for existing systems, normal and challenging conditions | Establish quantitative performance baselines for current legacy/manual processes as a comparative metric. | TBD | 1.2.1 Establish manual/legacy process performance & safety baselines (TBD); 1.2.2 Develop high-fidelity operational baselines incl. edge-case stress performance (TBD) |
| 1.3 Implement evaluation and test plans, including TEVV, across the AI lifecycle | Develop/execute a systematic TEVV program assessing AI performance at each lifecycle stage against requirements and baselines; the anchor task for TEVV across the whole profile. | Map 2.3, Measure 2.5, Measure 2.6 | 1.3.1 Define TEVV scope & requirements per AI system; 1.3.2 Categorization of Testing Environments (production-path testing prohibitions vs. permitted maintenance-window testing); 1.3.3 Evaluate AI system behavior against requirements/baselines; 1.3.4 Generate and maintain audit-ready TEVV evidence |
| 1.4 Establish Domain Knowledge and Linguistic Alignment Requirements | Identify/document domain-specific knowledge, terminology, and community context required for the AI system to perform accurately and safely. | TBD | 1.4.1 Maintenance & Operations; 1.4.2 Administrative & Support; 1.4.3 Infrastructure Optimization; 1.4.4 Requirements for AI-Generated Code, Configurations, Procedures, and Other Logic |

---

### Practice 2 — Define AI Robustness, Resilience, and Quality of Service expectations
**Category:** Ms, Mg, R, OG
Establish safeguards maintaining essential service delivery and functional safety when AI performance deviates from expected levels, regardless of cause; layered approach to reduce cascading failure likelihood.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 2.1 Establish AI usage thresholds and rate control mechanisms | Define technical constraints on volume/frequency/scope of AI-driven actions, communications, resource usage. | TBD | 2.1.1 Implement baseline rate limiting; 2.1.2 Process-informed dynamic guardrails; 2.1.3 Anomaly-driven detection and throttling |
| 2.2 Establish requirements for redundancy in AI-driven functions | Integrate independent, non-AI backup systems/parallel processing paths for critical AI-dependent functions. | TBD | 2.2.1 Maintain fully functional backup systems with documented fail-over procedures; 2.2.2 Deploy "watchdog" controllers on independent, deterministic architectures |
| 2.3 Establish protocols for and regularly perform systematic, achievable TEVV | Rigorous testing focused on anomalous/edge-case conditions, extending Task 1.3 to specialized boundary/stress conditions. | TBD | 2.3.1 Baseline AI system performance ("validated standard" dataset); 2.3.2 Targeted failure mode mapping (incl. MITRE ATLAS); 2.3.3 Use Digital Twins to test anomalous-condition behavior; 2.3.4 Recurrent Risk Evaluations ("Time-to-Divergence" cadence-setting) |
| 2.4 Perform Linguistic and Domain-Context Robustness Testing | Integrate domain-specific linguistic/contextual validation into TEVV to prevent hallucination/misprioritization failure modes. | TBD | 2.4.1 Benchmarking on application-specific terminology; 2.4.2 Localization and Community Validation; 2.4.3 Technical Accuracy and "Plausible Hallucination" Audits |
| 2.5 Verify and Ensure Policy Robustness Against Component, Hardware, and Data Schema Variance | Ensure learning systems (e.g. RL) do not learn to rely on undocumented/out-of-spec behavior of target systems. | TBD | 2.5.1 Train Across the Full Operating Range; 2.5.2 Multi-Vendor Testing |

---

### Practice 3 — Define risks, policies, and oversight for automated AI and agentic behavior
**Category:** G, R, HO, Mg
Establish well-defined, deterministic, actionable boundaries, policies, and oversight for high-risk actions that may disrupt safety-critical (cyber-)physical processes.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 3.1 Identify risk tradeoffs | Document possible high-risk AI actions/outcomes and maintain documentation as system/task/environment change; includes adversarial manipulation of AI outputs. | Govern 1.1, 1.2, 1.4, 2.1, 2.3, 3.2, 4.1; Map 1.1, 1.5, 2.1, 2.2, 5.1 | 3.1.1 Identify AI system decision points and potential outcomes of errors (incl. MITRE ATLAS); 3.1.2 Evaluate misclassification tradeoffs; 3.1.3 Define acceptable risk thresholds and control responses (SSVC-style consequence-driven framing, not raw CVSS/confidence scores); 3.1.4 Artifact-driven impact analysis |
| 3.2 Implement independent guardrails ("safety wrappers") for AI outputs | Enclose AI systems within hard-coded, deterministic guardrails independent of AI logic; block unsafe commands regardless of source, including from an authenticated but erroneous source. | Map 1.1, 2.2 | 3.2.1 Identify AI output intercept points; 3.2.2 Define deterministic operational constraints; 3.2.3 Specify fail-safe states and fallback behavior; 3.2.4 Define further logging and communication actions; 3.2.5 Artifact verification (independent, ideally non-AI/deterministic means) |
| 3.3 Establish Failure Notification Requirements | Define when an AI system should "fail loudly" (overt exception) vs. attempt autonomous recovery; balance against alarm-flood risk. | NIST AI RMF 1.0 Measure 1.1, 1.2, 2.4, 2.5, 2.6 | 3.3.1 Context-Specific Failure Modes; 3.3.2 Establish Maximum Drift Thresholds ("distribution fuse"/"distribution circuit breaker") |
| 3.4 Monitor for anomalous AI behavior | Define policies/procedures for detecting acute/undesired/unexpected AI behavior via continuous real-time monitoring, complementing scheduled batch evaluations (2.3.4). | Map 1.1, 2.2; MAP 3.2 | 3.4.1 Define observability requirements; 3.4.2 Establish operational baselines and deviation thresholds; 3.4.3 Monitor validation control integrity; 3.4.4 Define runtime anomaly escalation procedures |
| 3.5 Define and control risks to adjacent and related systems | Define/control risk to intentionally interdependent systems (cascading failure) and unrelated-but-adjacent systems (splash damage/blast radius); extend HVA assessment to supply chain. | TBD | 3.5.1 Map direct functional and algorithmic dependencies; 3.5.2 Identify indirect shared infrastructure and collateral damage exposure (physical/network/logical substrate commonality); 3.5.3 Impact compartmentalization (sandboxing); 3.5.4 Define and implement resource limiting |
| 3.6 Mitigate automation complacency and skills degradation | Continuous readiness/training protocols countering creeping dependence on AI, preserving manual-override proficiency. | TBD | 3.6.1 Baseline Human Competency Retention; 3.6.2 Scheduled "Manual Control" Drills; 3.6.3 Cognitive Engagement Monitoring (counter automation bias) |
| 3.7 Govern and mitigate risks from unauthorized, transient, and "Shadow AI" systems | Organizational policies, procurement gates, contractor onboarding to detect/restrict unvetted AI systems and localized open-source models. | Govern 1.1, Govern 4.1, Map 1.1 | 3.7.1 AI Attestation (third-party contractor disclosure); 3.7.2 AI Use Detection (traffic to known public AI API endpoints) |

---

### Practice 4 — Define procedures for emergency avoidance override, recovery, and situation awareness
**Category:** HO, Mg, I, OG
Establish/maintain documented procedures allowing operators to intervene in, suspend, or override unreliable/unexpected/harmful AI actions.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 4.1 Establish "break glass" intervention procedures | Procedures for authorized personnel to safely override AI-driven actions in an emergency ("break glass" analogy); disabling AI can itself leave the system unsafe. | Govern 1.4, 2.1, 3.2, 4.1, 4.3; Map 1.1, 2.2, 3.2, 3.5 | 4.1.1 Ensure AI systems can be reliably overridden; 4.1.2 Establish tiered intervention procedures, training, and authorization (incl. "emergency mode" for external responders); 4.1.3 Regularly practice and evaluate intervention processes (tabletop exercises, correlated-degradation scenarios) |
| 4.2 Ensure that personnel are able to gain and maintain situational awareness | Role-appropriate mechanisms for rapid, actionable situational awareness of AI system state/task/decisions/anomalies. | Measure 1.2, 3.1 | 4.2.1 Develop situational awareness processes/procedures per personnel group; 4.2.2 Regularly evaluate situational awareness mechanisms |
| 4.3 Establish independent ("out-of-band") communication, monitoring, alerting, and control capabilities | Ensure personnel needing to intervene have access to information independent of the AI system's own functionality (analog-gauge analogy). | Measure 3.1; Manage 4.1, 4.2, 4.3 | 4.3.1 Inventory channels for situational awareness/control affected by the AI system; 4.3.2 Implement AI-independent channels |
| 4.4 Attention Governance and Alert/Alarm Flood Mitigation | Treat human attention as a finite resource; AI-driven notification volume can exceed triage capacity. | Measure 1.2, 3.1 | 4.4.1 Recognizing novel AI-driven alert floods in unfamiliar domains; 4.4.2 Adapting legacy alarm management for AI's non-deterministic failure modes; 4.4.3 Managing correlated multi-system attention surges; 4.4.4 Applying consolidation and low-cognitive-load design techniques |
| 4.5 Define operational regimes for human-on-the-loop and human-out-of-the-loop operation | Identify contexts where real-time HITL is infeasible due to tight time constants (<10–15s); formally define where oversight becomes nominal/superficial. | Govern 3.2; Map 1.1 | 4.5.1 Define engineering time-constant thresholds; 4.5.2 Mandate deterministic boundary constraints for automated regimes |

---

### Practice 5 — Implement identity and access management (IdAM) for AI agents, systems, and tools
**Category:** G, R, SC(adjacent)
Establish IdAM controls for AI agents/tools appropriate to role, auditability, risk, and oversight across the lifecycle.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 5.1 Require identities and authentication for AI entities | Inventory AI entities and define authentication uniquely identifying each, including ephemeral ones, at a granularity enabling isolated revocation. | TBD | 5.1.1 Audit for and replace shared credentials/service accounts/secrets/API keys (Non-Human Identities); 5.1.2 Establish unique identities for AI service accounts/agents (TBD); 5.1.3 Implement cryptographically verifiable identities and automated mutual authentication (TBD) |
| 5.2 Determine and enforce specific access requirements | Define specific systems/data/tools each AI entity is authorized to access; technically enforced and auditable. | TBD | 5.2.1 Map and document AI agent access to operational/data assets (TBD); 5.2.2 Implement dynamic, context-aware access control policies (TBD); 5.2.3 Determine appropriate agent/asset/permission granularity (TBD) |
| 5.3 Enforce principles of least agency and least privilege for AI entities | "Least agency" (minimize capability to initiate independent action) distinct from "least privilege" (restrict what's allowed if attempted). | TBD | 5.3.1 Determine practical minimum necessary permissions per task (TBD); 5.3.2 Deploy automated "Least Agency" policy enforcement and session-based execution limits (TBD) |
| 5.4 Implement continuous security monitoring for AI entity actions | Continuously monitor AI entity actions against access boundaries to detect out-of-scope actions, unauthorized access, privilege escalation. | TBD | 5.4.1 Establish logging/periodic review of AI agent authentication and access events (TBD); 5.4.2 Deploy real-time behavioral anomaly detection within the SOC (TBD) |

---

### Practice 6 — Integrate visibility of the external supply chain of AI into vendor and 3rd party risk management
**Category:** SC, G, R
Enforce pre-acquisition/procurement-phase governance over external vendor dependencies (contrast with Practice 7's post-acquisition internal scope).

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 6.1 Develop policies for AI supply chain requirements | Define minimum trustworthiness/visibility requirements for AI-related vendors/assets, scaled by criticality. | Govern 1.6, 6.1, 6.2; Map 1.5, 4.1, 4.2, 5.1 | 6.1.1 Add AI disclosure to existing procurement policies (model-update frequency, training-data provenance, safety-behavior change disclosure; contractual suspension rights for updates); 6.1.2 Require machine-readable AIBOM for mission-critical applications (compensating controls if unavailable); 6.1.3 Domain-Specific Terminology and Contextual Attestation; 6.1.4 Manufacturer Accountability and AI Resilient-by-Design Mandates |
| 6.2 Align AI and existing CI asset lifecycle management | Integrate externally sourced AI components into existing asset lifecycle/change-control processes. | Map 4.1, 4.2 | 6.2.1 Register externally sourced AI components in asset management systems (TBD); 6.2.2 Track vendor updates/third-party changes through change management (TBD); 6.2.3 Manage end-of-life transitions for externally sourced AI components (TBD) |
| 6.3 Identify and control dataflows across the AI supply chain | Define/maintain visibility over dataflows between AI systems and external vendors/platforms/services. | Manage 1.1, 1.4, 3.1, 3.2 | 6.3.1 Catalog data egress points and third-party processing destinations (TBD); 6.3.2 Implement egress monitoring and isolated, access-restricted enclaves (TBD) |

---

### Practice 7 — Manage internal AI supply chain and data provenance
**Category:** SC, L, T
Post-acquisition operational oversight for AI assets under direct organizational control (fine-tuning, RAG repositories, safety-wrapper version control, local provenance).

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 7.1 Maintain an Internal Registry of AI Deployments | Catalog internal instances/versions/use-cases across departments, including legacy pre-authorization systems. | TBD | 7.1.1 Create/maintain a "Master AI Asset List"; 7.1.2 Maintain a data inventory of organizational data sources used in AI systems (source, role, classification, lineage, quality, ownership, security controls, hosting); 7.1.3 Integrate automated internal AIBOM management and regular network scanning |
| 7.2 Validate data provenance for model inputs | Document source/cleaning/permitted-use/authorization of internal datasets used to fine-tune or prompt models. | TBD | 7.2.1 Implement data quality monitoring/certification; 7.2.2 Verify data provenance via cryptographic hashing and data lineage tools |
| 7.3 Manage Version Control and Logging for Internal AI Safety Mechanisms | Rigorous configuration management/logging for internal "wrappers," system prompts, and safety filters. | TBD | 7.3.1 Maintain a registry uniquely identifying model/prompt-template/safety-logic versions with change log; 7.3.2 Automate Policy-as-Code; 7.3.3 Implement Logical Policy Locks for Adaptive Models (freeze weights/hyperparameters/boundary logic during active operation) |
| 7.4 Define Authorization and Access Controls for AI Modifications | Strict identity-based access controls for individuals authorized to modify internal AI models/systems/mechanisms/datasets/configurations. | TBD | 7.4.1 Define/implement approval and logging requirements for updates/changes; 7.4.2 Implement regular "integrity checks" for systems interfacing with external AI services |
| 7.5 Conduct Impact Assessments and Risk Management for AI System and Model Updates | Structured risk/performance assessment before deploying internal updates (prompts, config, data, wrappers); mitigating controls if risk increases. | TBD | 7.5.1 Perform pre-update validation and re-calibration; 7.5.2 Perform automated "champion-challenger" and drift assessment (shadow mode); 7.5.3 Integrate Privacy Impact Assessments into update cycles; 7.5.4 Audit Interoperability for Hardware or Data Substrate Substitution |
| 7.6 Establish processes for internal AI component deprecation and decommissioning | Secure, structured protocols for sunsetting internally developed AI agents/systems/tools/models/datasets. | TBD | 7.6.1 Internal Dependency Mapping (Orphan System Prevention); 7.6.2 Secure Archiving and Destruction of Model and Other AI Artifacts ("zombie model" prevention); 7.6.3 Legacy Logic Vulnerability Management ("Extended Isolation Protocol") |

---

### Practice 8 — Incorporate AI-aware incident analysis and response procedures
**Category:** I, T, Mg
Protocols for responding to and investigating AI-related failures given probabilistic/non-deterministic behavior.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 8.1 Identify scenarios requiring deterministic root cause analysis and incident reconstruction | Define applications/thresholds/triggers mandating comprehensive deterministic reconstruction of an AI-driven failure. | TBD | 8.1.1 Evaluate AI applications for required root-cause-analysis rigor; 8.1.2 Identify AI systems that may not satisfy root cause analysis requirements (LLMs w/ non-deterministic sampling, ephemeral-context agentic systems; explicit warning that SHAP/LIME post-hoc explainability is **not** forensic proof); 8.1.3 Update incident response policies/playbooks; 8.1.4 Conduct incident reconstruction drills (digital twins/high-fidelity simulators); 8.1.5 Multi-agent cascade reconstruction capabilities |
| 8.2 Identify additional controls required where deterministic root cause analysis is not possible | Formal risk-based protocols/alternative verification standards where non-determinism prevents precise root-cause identification. | TBD | 8.2.1 Identify applications where root-cause-analysis requirements may be relaxed with compensating controls; 8.2.2 Identify opaque systems and appropriate safety margins |
| 8.3 Designate roles for AI incident governance | Formulate a cross-functional AI Incident Response Team (AIRT: legal, technical, risk management, communications). | TBD | 8.3.1 Identify internal incident management points of contact per AI system; 8.3.2 Form a permanent AI incident governance team (CISO, technical, legal, ops) |
| 8.4 Define external reporting and regulatory disclosure protocols following AI incidents | Formal procedures/relationships with external regulators and the public following an AI-related anomaly. | TBD | 8.4.1 Integrate AI-specific triggers into existing incident disclosure/reporting protocols (TBD); 8.4.2 Establish automated notification and detailed impact disclosure for sector-specific authorities (TBD) |
| 8.5 Pre-arrange specialized resources for investigating and recovering from AI incidents | Pre-identified/pre-arranged access to specialized personnel/budget (third-party AI forensic auditors, specialized legal counsel); market noted as "currently nascent." | TBD | 8.5.1 Identify third-party AI forensic and legal experts for contingency access (TBD); 8.5.2 Establish formal retainer-style relationships with specialized AI incident responders/auditors (TBD) |

---

### Practice 9 — Provide calibrated, needs-based AI risk management training
**Category:** G, HO, OG
Systematic AI risk management training program tailored to operational roles and decision-making responsibilities.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 9.1 Perform role-based AI risk competency mapping | Identify AI-related knowledge/skills required for different roles, executive to front-line. | TBD | 9.1.1 Identify required AI literacy/risk-awareness levels for existing roles (TBD); 9.1.2 Develop AI risk competency matrix and personalized learning paths (TBD) |
| 9.2 Deliver specialized training on human-AI interaction and automation bias | Skills to recognize/mitigate "automation bias" — the tendency to over-trust automated outputs. | NIST AI RMF 1.0 Govern 4.2, Map 3.4, Manage 2.3, 2.4 | 9.2.1 Include role-specific "AI failure modes" training in standard annual technical/cybersecurity training; 9.2.2 Implement realistic incident simulation training (digital twins) |
| 9.3 Establish audit-ready systems for verifying workforce readiness | Formal mechanisms to assess/document AI risk training effectiveness through structured assessments, tabletop simulations, periodic drills. | TBD | 9.3.1 Maintain logs of completed AI training and proficiency assessment scores (TBD); 9.3.2 Implement periodic "readiness drills" and validated skills certifications for critical roles (TBD) |

---

### Practice 10 — Implement multi-tiered AI system logging and audit capabilities
**Category:** T, Mo, V
Systematic capture/preservation of operational telemetry across the AI lifecycle so decision-making logic remains transparent and verifiable.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 10.1 Define decision-level logging and metadata retention policies | Specify AI systems/applications for which inputs/outputs/prompts/version metadata are captured for deterministic reconstructability. | TBD | 10.1.1 Identify AI systems that may take/influence mission-critical actions; 10.1.2 Immutable Runtime Telemetry and Artifact Tracking (explicitly: post-hoc SHAP/LIME approximations are **not** a substitute for true decision-level logs); 10.1.3 Forensic Integrity and Privacy-Preserving Log Partitioning; 10.1.4 Asynchronous Token Logging for Constrained Edges |
| 10.2 Establish data integrity and tamper-evidence controls for AI telemetry and logging | Access controls/security protocols ensuring immutability/reliability of captured AI logs ("digital chain of custody"). | TBD | 10.2.1 Ensure logs are stored in an immutable manner (bandwidth/retention safeguards) |
| 10.3 Implement systematic audit review and performance trend analysis | Formal procedures for periodic review of AI logs to identify drift, emerging bias, performance anomalies. | TBD | 10.3.1 Conduct periodic manual reviews of AI logs for performance issues/drift (TBD); 10.3.2 Implement automated trend analysis and dashboarding for continuous audit oversight (TBD) |

---

### Practice 11 — Maintain AI-aware mission continuity and disaster recovery planning
**Category:** L, Mg, CI, OG
Strategic framework for immediate-term alternative operating modes and longer-term recovery/restoration following significant AI failure.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 11.1 Identify and prioritize AI-dependent essential functions | Catalog infrastructure services relying on AI components, ranked by impact on mission continuity/public safety. | TBD | 11.1.1 Rank operational processes by impact of AI failure/unavailability (TBD); 11.1.2 Conduct comprehensive AI dependency mapping across sector-critical functions (TBD) |
| 11.2 Define manual and alternative operating procedures for long-term mission continuity | "Manual Mode" instructions for running essential functions for extended periods without AI support, tailored to system timeline (24/7 vs. non-realtime). | TBD | 11.2.1 Document basic manual fallback procedures for AI-dependent control points (TBD); 11.2.2 Develop a validated "Safe Operating Mode" independent of AI infrastructure (TBD) |
| 11.3 Pre-allocate operational resources for alternative service delivery | Ensure availability/maintenance of physical tools, trained standby personnel, budgetary reserves for fail-over to non-AI backups. | TBD | 11.3.1 Identify standby personnel and physical tools required for manual operations (TBD); 11.3.2 Maintain Isolated Standby Infrastructure and Allocated Reserves (TBD) |
| 11.4 Establish system integrity re-validation and re-commissioning protocols | Mandatory technical benchmarks/safety tests before transitioning from manual mode back to automated operations. | TBD | 11.4.1 Define a checklist for validating system safety before re-engaging AI control (TBD); 11.4.2 Implement "Shadow Mode" validation and mandatory safety-interlock checks for AI re-commissioning (TBD) |
| 11.5 Execute periodic mission continuity simulations and stress tests | Regular "fail-to-manual" exercises verifying alternative operating procedures are effective under stress. | TBD | 11.5.1 Conduct annual "fail-to-manual" tabletop exercises (TBD); 11.5.2 Execute high-fidelity simulation drills involving total AI infrastructure loss and recovery (incl. ambiguous-cause scenarios) |

---

### Practice 12 — Validate AI-Generated Operational Logic and Artifacts
**Category:** V, T, R
Rigorous validation/verification protocols for AI-generated artifacts (code, configurations, procedures) that direct or influence CI operations.

| Task | Content | AI RMF mapping | Implementations |
|---|---|---|---|
| 12.1 Establish Governance and Accountability for AI-Generated Execution Artifacts | Policy framework/responsibility structures for creation, classification, and authorization of AI-generated logic; every artifact gets a risk tier and human owner. | TBD | 12.1.1 Artifact Risk Classification ("Direct-Execution Logic" vs. "Human-Mediated Logic"); 12.1.2 Provenance and Traceability (link artifact to model version/prompt/inference context — not post-hoc explanation tools); 12.1.3 Authorization of Machine-Authored Logic (who may "promote" draft→production) |
| 12.2 Implement Multi-Layered Validation of Machine-Authored Logic | Hybrid verification: deterministic automated testing + expert human scrutiny against formal specs and tacit domain knowledge. | TBD | 12.2.1 Deterministic and Rule-Based Guardrails (non-AI static analyzers/schema validators); 12.2.2 SME Review of Procedures ("red-team" review for plausible hallucinations); 12.2.3 Validation against Tacit and Formal Requirements |
| 12.3 Manage Operational Continuity and Resilience for Generated Artifacts | Safeguards protecting availability/safety throughout the lifecycle of AI-generated logic: isolated testing, version control, "known-good" rollback availability. | TBD | 12.3.1 Isolated Execution Testing (Sandboxing); 12.3.2 Version Control and Rollback Procedures; 12.3.3 Monitoring for Latent Failures |

---

### Practices 13, 14, 15, etc. — Reserved / Not Yet Written
The source states verbatim: *"13, 14, 15, etc.: (TBD)"* with a reviewer note inviting proposals for additional Practices not naturally fitting under 1–12. **No content exists for this catalog to extract.** This is recorded as a fact about the source's current completeness, not a gap in this extraction.

---

## 3. Document-Level (non-Practice) Content Relevant to a Compliance Audit

These are structural/process statements in the source that are not themselves Practices/Tasks but shape how any compliance mapping should be read:

1. **Explicitly not a checklist.** "This document is not intended to be exhaustive and should not be treated as a rigid compliance checklist." Any FULL/PARTIAL/NONE scoring in Task 2 of this audit must be read against this framing — the source itself disclaims binary compliance semantics.
2. **Governance-incomplete by design.** "It is intentionally not 'governance-complete' and stops where sector-agnostic guidance ends," explicitly inviting sector-specific extension.
3. **Deconfliction with Cyber AI Profile (IR 8596).** All "Primary Cyber AI Profile Mappings" fields are blank/TBD across the entire document pending that profile's publication. Any gap analysis must not penalize an audited system for cybersecurity-control-level items the source itself has not yet populated.
4. **Draft status affects every downstream claim.** The source is dated Jul 7, 2026, labeled Community of Interest Discussion Draft, with an open comment period through roughly mid-August 2026 (per public NIST program page, not this PDF itself — see Evidence Matrix). Requirements text is described by the authors as having "uneven emphasis, and layout inconsistencies," with many Implementations placeholder TBDs. A "Requirement Catalog" built from this source is therefore a catalog of a **moving target**, not a stable regulatory baseline.
5. **AI-assisted authorship disclosure.** The source document itself discloses: "This document was created with the assistance of Google Gemini (versions 3.0 and 3.5) and Anthropic Claude (Sonnet 5)... All content has been reviewed and verified by the authors." Noted for completeness/transparency, not as a compliance point.
6. **Appendix "Ideas and References Already in Progress"** lists cross-cutting themes and Practice-specific extensions NIST is already considering but has not yet incorporated (e.g., "Autonomy isn't one-dimensional" cross-cutting Practices 3–4; "Specification gaming" under Practice 2; "Chaining of agentic failures" under Practice 3; "Near-miss reporting" under Practice 8; explicit stakeholder-engagement task under Practice 9; "AI-assisted coding tech debt" under Practice 12). These are **not requirements** — they are the source's own internal roadmap notes — but are relevant context for Task 3 (Gap Analysis) since a gap against a not-yet-written idea is not a compliance gap against MoCKA.
7. **Sector-specific reference lists** (Oil & Gas, Electric/Bulk Power, Water/Wastewater, Healthcare, Emergency Services, cross-sector process-safety standards) and a **Standards Bodies/Consortia tracking list** (AIBOM/SBOM efforts, agentic security initiatives, cross-industry consortia, international frameworks) appear in the appendix as candidate references, not requirements.

---

## 4. Summary Counts

- **Practices with content:** 12 (Practices 13+ reserved, no content)
- **Tasks:** 53 (P1:4, P2:5, P3:7, P4:5, P5:4, P6:3, P7:6, P8:5, P9:3, P10:3, P11:5, P12:3 — sums to 53; an earlier internal draft of this count stated 54 in error and was corrected during the Task7/8 fairness/consistency audit pass)
- **Implementations named in source:** ~140, of which a substantial fraction (concentrated in Practices 5, 6.2, 6.3, 8.4, 8.5, 9.1, 9.3, 10.3, 11.1–11.4) are explicit **`(TBD — suggestions welcome)`** stubs with no operative content yet.
- **Tasks with a populated "Primary AI RMF Mappings" field:** roughly half; the remainder are marked `>(TBD - suggestions welcome)` in the source itself.
- **"Primary Cyber AI Profile Mappings" fields populated:** 0 (all blank/TBD, pending IR 8596).

This catalog is the input to `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md` (Task 2), which maps MoCKA's institutional components against each of the 53 Tasks above.

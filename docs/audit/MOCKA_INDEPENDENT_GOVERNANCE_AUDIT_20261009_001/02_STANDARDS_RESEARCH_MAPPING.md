# Deliverable 2: Standards and Research Mapping

Audit ID: MOCKA_INDEPENDENT_GOVERNANCE_AUDIT_20261009_001
Access date for all web items: 2026-10-09 (session date).

## A. Access status (read first)

- Primary-source fetch attempts were made on 2026-10-09 and failed:
  - csrc.nist.gov, www.rfc-editor.org, www.w3.org: HTTP 403 from the session egress proxy (policy denial, recorded in the proxy status). Not bypassed.
  - opentelemetry.io, nvlpubs.nist.gov, genai.owasp.org, www.iso.org: DNS resolution failure via WebFetch.
- Consequence: no source below is PRIMARY_SOURCE_VERIFIED. Entries are based on WebSearch snippets. Where several snippets agree, the label is SECONDARY_SOURCE_CORROBORATED. Where the claim has not been confirmed, the label is NOT_VERIFIED.
- Exact section and control identifiers are NOT given unless the search snippet stated them. Where a section number is needed, it is marked NOT_VERIFIED. No section numbers were invented.

## B. Source register

Columns: ID, title, issuer, version/date, URL (as surfaced in search), type (N = normative, I = informative, E = empirical, P = proposal), label.

| ID | Title | Issuer | Version / date | URL surfaced | Type | Label |
|---|---|---|---|---|---|---|
| S01 | Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1 | NIST | 1.0, 26 Jan 2023 | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf (primary not fetched) | I (voluntary framework) | SECONDARY_SOURCE_CORROBORATED |
| S02 | NIST AI RMF Playbook (companion) | NIST | NOT_VERIFIED date | NOT_VERIFIED | I | NOT_VERIFIED (mentioned in secondary sources only) |
| S03 | Generative AI Profile, NIST AI 600-1 | NIST | 26 Jul 2024 | NOT_VERIFIED URL | I | SECONDARY_SOURCE_CORROBORATED (date only). Note: one source says it was commissioned under EO 14110, which was rescinded January 2025. Status NOT_VERIFIED. |
| S04 | Zero Trust Architecture, NIST SP 800-207 | NIST | Revision and date NOT_VERIFIED (SP 800-207, commonly cited as 2020) | https://csrc.nist.gov/pubs/sp/800/207/final (blocked 403) | N/I (architecture guidance) | SECONDARY_SOURCE_CORROBORATED for the PDP/PEP split. Date NOT_VERIFIED. |
| S05 | Guide to Computer Security Log Management, NIST SP 800-92 | NIST (Kent, Souppaya per the PDF; some records list Scarfone and Souppaya) | Sep 2006 | DOI https://doi.org/10.6028/NIST.SP.800-92 (surfaced in search) | I | SECONDARY_SOURCE_CORROBORATED. Current revision status NOT_VERIFIED. Author attribution conflict preserved. |
| S06 | Certificate Transparency Version 2.0, RFC 9162 | IETF (Laurie, Messeri, Stradling) | Experimental, Dec 2021; obsoletes RFC 6962 | https://www.rfc-editor.org/rfc/rfc9162.html (blocked 403); datatracker also surfaced | I/E (Experimental) | SECONDARY_SOURCE_CORROBORATED. Datatracker reports last update 2025-12-04 per search snippet; errata status NOT_VERIFIED. |
| S07 | PROV-DM: The PROV Data Model | W3C (editors Luc Moreau, Paolo Missier) | Recommendation, 30 Apr 2013 | https://www.w3.org/TR/prov-dm/ (blocked 403) | N (W3C Recommendation) | SECONDARY_SOURCE_CORROBORATED. PROV-CONSTRAINTS (companion Recommendation) surfaced, not read. |
| S08 | Context propagation (traceparent, parent ID) | OpenTelemetry project | Current docs; version NOT_VERIFIED | https://opentelemetry.io/docs/concepts/context-propagation/ (DNS fail) | I | SECONDARY_SOURCE_CORROBORATED. W3C Trace Context recommendation is the normative reference; not fetched. |
| S09 | OWASP Top 10 for LLM Applications (LLM06 Excessive Agency) | OWASP GenAI Security Project | 2025 edition per secondary; 2026 reordering reported by one source | https://genai.owasp.org/llm-top-10/ (DNS fail) | I (practitioner guidance) | SECONDARY_SOURCE_CORROBORATED for 2025 LLM06. 2026 reordering NOT_VERIFIED. |
| S10 | OWASP Top 10 for Agentic Applications (ASI01-ASI10) | OWASP GenAI Security Project | Published Dec 2025 (per genai.owasp.org post URL) | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | I | SECONDARY_SOURCE_CORROBORATED. ASI03 identity and privilege abuse is the closest match to least privilege. Full ASI entry text NOT_VERIFIED. |
| S11 | ISO/IEC 42001:2023, AI management system | ISO and IEC | Dec 2023 | https://www.iso.org/standard/42001 (DNS fail); webstore.iec.ch/publication/90574 surfaced | N (certifiable management system standard) | SECONDARY_SOURCE_CORROBORATED for title, year, scope. Clause and control counts NOT_VERIFIED. EU AI Act relation NOT_VERIFIED. |
| S12 | MITRE ATT&CK; defensive controls frameworks; OpenTelemetry specification beyond concepts; W3C Trace Context; ISO/IEC 27001 and 27037; NIST SP 800-53 AU family; NIST SP 800-162 (ABAC); NIST SP 800-63 (identity); event sourcing and idempotency literature | various | NOT_VERIFIED | NOT_VERIFIED | mixed | NOT_VERIFIED. Not searched in this session. Listed as leads for the next research pass. |

Not applicable or not established as applicable: the list above is candidate material, not a claim that each framework applies. No source here establishes that MoCKA conforms to, or is certified against, any standard.

## C. Standard-to-MoCKA applicability matrix

Columns: principle or design need; source(s) that address it; what the source guarantees (as far as the snippet supports); what it does not guarantee; MoCKA applicability; evidence needed in MoCKA.

| Need | Source | Guarantees (supported) | Does not guarantee | MoCKA applicability | Evidence needed in MoCKA |
|---|---|---|---|---|---|
| Govern AI risk across lifecycle | S01 | A structured, voluntary vocabulary: GOVERN cross-cutting, MAP, MEASURE, MANAGE | Any specific control, any runtime behavior, any compliance | Vocabulary for mapping the audit; not a control set | Mapping of each MoCKA control to a function; no certification claim |
| Decision separated from enforcement | S04 | PDP (policy engine and administrator) decides; PEP in path enforces; PEP waits for decision | That PEP actually sits in every path; that the decision source is authentic or fresh | Directly relevant to Human Gate vs EventGate vs runtime | Proof that all execution paths pass the PEP (bypass test); decision record references |
| Append-only tamper-evidence | S06 | Merkle inclusion and consistency proofs let auditors verify that a later log extends an earlier one; detects misbehavior | Prevents misissuance; guarantees the logged item is correct or authorized | Applicable concept for event store anchors and exports; not an implementation spec | Anchors recorded outside the store; verification of an export against an anchor |
| Provenance model | S07 | Entities, activities, agents, and derivations as a vocabulary | That the provenance records are complete or true | Map evidence, decision, authorization, action, outcome | Actual provenance records with identifiers; completeness check |
| Causal context propagation | S08 | Trace and parent identifiers propagated across services via traceparent | That every hop is instrumented; that absent spans mean absent work | Event correlation IDs in MoCKA | Propagated IDs present in records; missing propagation detected as gap, not absence |
| Log management practice | S05 | Planning and operating log infrastructure, centralization, retention policy (per summary) | Current requirements, integrity mechanisms specific to AI governance | General baseline for event retention and log integrity | Retention policy and log integrity checks in MoCKA; current revision NOT_VERIFIED |
| Agentic excessive agency and privilege | S09, S10 | Names the risk classes (excessive functionality, permissions, autonomy; ASI03 identity and privilege abuse) | Specific technical controls; MoCKA-specific compliance | Threat taxonomy for AI components and orchestration | Per-component authority inventory; tests that show no component grants itself authority |
| AI management system | S11 | Requirements for establishing, maintaining, and improving an AIMS; Annex SL structure | That any particular control works; certification outcome | Organizational wrapper; not a runtime control | Management review records; not claimed as conformance |

## D. Claim-to-evidence matrix (external claims used in this package)

| Claim | Evidence label | Basis | Conflict or gap | Resolving evidence |
|---|---|---|---|---|
| NIST AI RMF is voluntary, four functions | SECONDARY_SOURCE_CORROBORATED | Several secondary guides, consistent | Primary not read | Fetch S01 PDF |
| PDP/PEP split in NIST SP 800-207 | SECONDARY_SOURCE_CORROBORATED | Several secondary guides | Vendor pages tie roles to products; NIST text not read | Fetch S04 |
| Certificate Transparency v2 uses Merkle proofs and detects rather than prevents misissuance | SECONDARY_SOURCE_CORROBORATED | Snippet quoting RFC 9162 summary | Primary blocked | Fetch S06 |
| PROV-DM Recommendation 30 Apr 2013 | SECONDARY_SOURCE_CORROBORATED | Search result referencing W3C URLs, including an earlier Proposed Recommendation (12 Mar 2013) | Primary blocked | Fetch S07 |
| traceparent carries 128-bit trace ID and 64-bit parent ID | SECONDARY_SOURCE_CORROBORATED | Secondary guides | Primary not read | Fetch S08 and W3C Trace Context |
| LLM06 Excessive Agency in 2025 LLM Top 10 | SECONDARY_SOURCE_CORROBORATED | Secondary guides | 2026 reordering conflicting | Fetch S09 |
| Agentic Top 10 split of excessive agency across ASI entries | SECONDARY_SOURCE_CORROBORATED | Secondary guides citing the agentic list | Entry text not read | Fetch S10 |
| ISO/IEC 42001:2023 published Dec 2023 | SECONDARY_SOURCE_CORROBORATED | Multiple vendor and store listings | Clause counts conflict across sources (secondary says 7 clauses and 38 controls; not verified) | Obtain official text via ISO or IEC |
| EU AI Act and ISO 42001 presumption of conformity | NOT_VERIFIED | One secondary source | Legal claim; do not use | EU official text |

Conflicts preserved:
- Excessive agency: 2025 LLM06 versus a reported 2026 reordering (moved to #3). Not resolved.
- SP 800-92 authorship: Kent and Souppaya versus Scarfone and Souppaya in some records. Not resolved.
- ISO 42001 counts: one secondary source states 7 clauses and 38 controls across nine areas. Not verified against the standard.

## E. Where no authoritative source was found

- No primary standard was found in this session that defines "REQUEST_ACCEPTED", "GATE_DECISION_RECORDED", "EVENT_PERSISTED", "EVENT_READ_BACK_VERIFIED", or "OUTCOME_VERIFIED" as terms. These are MoCKA-specific states. Their definitions are design choices, not standard terms. Stated as ANALYTICAL_INFERENCE.
- No authoritative source was found for "quarantine" semantics in admission gates as a general standard. Treated as design choice.
- No authoritative source found yet for event-store idempotency records in a standards body. Practitioner patterns only (ANALYTICAL_INFERENCE; NOT_VERIFIED as standards).
- No source was found that establishes that a configuration flag or policy declaration constitutes runtime causal efficacy. Brief section 2.3 is a design requirement, not a standard result.

## F. Limits of this mapping

- Built from search snippets; no primary text has been read in this session.
- Section and control identifiers are omitted where not verified. Add them after primary fetch.
- No compliance, certification, or conformance claim is made.

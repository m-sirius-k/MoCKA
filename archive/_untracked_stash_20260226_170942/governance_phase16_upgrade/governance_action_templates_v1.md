\# NOTE: Governance Action Templates v1 (Phase14.6 linkage)

\# NOTE: These templates are used when FAIL(STRUCTURAL) -> GOVERNANCE\_ACTION\_REQUIRED.

\# NOTE: Record a governance event describing the decision and remediation.



\# Governance Action Templates v1



\## ERR-STRUCT-001 GENESIS\_DUPLICATE

Decision: Select canonical GENESIS, quarantine the others.

Actions:

1\. Identify all GENESIS candidates (event\_id list).

2\. Choose canonical GENESIS by rule (earliest timestamp\_utc).

3\. Register non-canonical as QUARANTINE in branch\_registry.

4\. Emit governance decision event with justification.

5\. Re-run struct\_verify\_v1.py.



\## ERR-STRUCT-002 TIP\_UNREACHABLE

Decision: Repair chain reachability or move TIP to last reachable event.

Actions:

1\. Detect first broken prev\_hash link.

2\. If data corruption: quarantine the broken segment.

3\. Set TIP to last reachable event\_id.

4\. Emit governance decision event.

5\. Re-run struct\_verify\_v1.py.



\## ERR-STRUCT-003 BRANCH\_CLASSIFICATION\_INVALID

Decision: Enforce non-NULL classification.

Actions:

1\. List rows with NULL classification.

2\. Assign classification by governance decision (NORMAL/QUARANTINE/etc).

3\. Add NOT NULL constraint if absent.

4\. Emit governance decision event.

5\. Re-run struct\_verify\_v1.py.



\## ERR-STRUCT-004 QUARANTINE\_CONFLICT

Decision: Ensure quarantine branches are never selected as TIP.

Actions:

1\. Confirm quarantine branches exist.

2\. Enforce TIP selection excludes quarantine.

3\. Emit governance decision event.

4\. Re-run struct\_verify\_v1.py.


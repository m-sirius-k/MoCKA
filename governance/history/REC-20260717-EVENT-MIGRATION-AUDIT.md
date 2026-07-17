\# REC-20260717 EVENT MIGRATION AUDIT



\## Target



Artifact:

mocka\_events.db



Path:

data/mocka\_events.db



SHA-256:

52c24abee57f123a99af611068de4396b44eb83e37ac8ac1e7ebec92e14b89ec



Event Count:

16483



\## Finding



Detected:

22 records with data\_integrity=corrupted\_migration



Classification:

Historical CSV migration boundary failure



Cause:

CSV column shift / parse error



\## Impact Verification



Verified\_by contamination:

0



Decision Ledger reference:

Not detected



Anchor record reference:

Not detected



Governance JSON reference:

Not detected



\## Disposition



Status:

Contained historical anomaly



Action:

Retain records with integrity\_note.

Do not promote to verified event state.

Do not delete historical evidence.



\## Verification



Audit date:

2026-07-17


# MoCKA Global Rule Pack v1.0

## PURPOSE
This file is a mandatory system-level rule definition for all MoCKA-related execution environments.

---

## RULE 1: SINGLE ROOT
All MoCKA modules MUST be placed under:

C:\Users\sirok\MoCKA\

No exceptions.

---

## RULE 2: NO TEMP STRUCTURES
Forbidden:
- mocka_v0.1
- tmp
- draft
- test
- *_copy

---

## RULE 3: NO DOUBLE NESTING
Forbidden:
- mcp/mcp
- relay/relay
- event/event

---

## RULE 4: DESIGN ≠ DEPLOYMENT
Design is conceptual only. Deployment requires validation.

---

## RULE 5: STOP CONDITION
If root is unclear:
STOP execution immediately and request confirmation.

---

## RULE 6: GLOBAL CONSISTENCY
All AI systems (ChatGPT / Claude / Copilot) MUST behave identically under these rules.

END OF SPEC

# Port Contract Verification Report

Date: 2026-07-13

## Decision

DC_20260713_001 の実プロセス再検証。

## Verified Architecture

| Port | PID | Parent PID | Service |
|---|---:|---:|---|
| 5000 | 16652 | 16044 | MoCKA Core/API |
| 8750 | 16912 | 16468 | SEO-OS Command Center |

## Process Verification

5000:
- Process: python -X utf8 app.py
- Parent: MoCKA-APP tab
- Endpoint verification:
  - /health/status -> 200
  - /api/ise/status -> 200

8750:
- Process: python -X utf8 app.py
- Working directory:
  PlanningCaliber/workshop/seo-os/command_center
- Parent: MoCKA-SEO-OS tab
- Endpoint verification:
  - /api/capabilities -> 200
  - /api/jobs -> 200

## Conclusion

8750 is not a MoCKA Core API endpoint.

8750 is the SEO-OS Command Center interface.

5000 remains the official MoCKA Core/API port.

No code modification required.

## Prevention Rule

Before API troubleshooting:
1. Identify port ownership.
2. Verify process path.
3. Confirm service contract.
4. Modify only after architecture verification.

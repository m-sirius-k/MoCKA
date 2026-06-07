# Orchestra Changelog

## v1.1.0 — 2026-06-06

### New Features
- **30-day Free Trial** — New users can activate a full Pro trial with one click via Google sign-in. No credit card required.
  - Trial tracks usage via privacy-preserving SHA-256 hash of Google account ID (sub)
  - Stored in Cloudflare Workers KV with 31-day auto-expiry
  - Trial banner appears in popup for Free users (hidden for Pro/One license holders)
  - Days-remaining counter shown during active trial
  - Expired trial prompts upgrade with direct link to Settings

### Technical Changes
- `manifest.json`: version bumped to 1.1.0
- Added `identity` and `identity.email` permissions for Google OAuth2
- Added `oauth2` section with client ID for `chrome.identity.getAuthToken`
- New `extension/trial.js`: `TrialManager` module (startTrial, getStatus, check, checkProLicense)
- `backend/worker.js`: Added `POST /api/trial/start` and `GET /api/trial/status` endpoints (existing Stripe webhook and HMAC logic unchanged)
- `popup.html` / `popup.js`: Trial banner UI with `#trial-banner` element and `initTrialBanner()` handler

### Constraints Preserved
- Existing HMAC-SHA256 offline license validation is unchanged
- Stripe webhook handler is unchanged
- All existing Pro/One license holders: zero impact
- `trial:` KV prefix is isolated from existing `issued:` and `serial` records

---

## v1.0.1

- Bug fixes and stability improvements

## v1.0.0

- Initial release: conversation capture, local IndexedDB storage, CSV/JSON export
- AI Share (Pro): send to 5 AIs simultaneously
- AI Collab (One): fully autonomous multi-AI orchestration

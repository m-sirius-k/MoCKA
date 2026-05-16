# mini MoCKA Series

> AI cognitive extension tools for claude.ai — built on a shared private foundation.

**planningcaliber/workshop/mini-mocka-series/**

---

## Products

| Product | Status | TODO | Description |
|---|---|---|---|
| Core SDK | 🟡 Phase 0 | TODO_146 | Shared private foundation |
| Orchestra | ✅ Dev complete | TODO_140/141 | Parallel AI deliberation |
| Relay | 🟡 Phase 2 | TODO_147 | Auto conversation handoff |
| Vault | ⬜ Phase 3 | TODO_148 | Save + context injection |
| Logbook | ⬜ Phase 4 | TODO_149 | Decision + TODO extraction |
| Prism | ⬜ Phase 5 | TODO_150 | Mode-switching thought deepener |

---

## Directory Structure

```
mini-mocka-series/
├── core-sdk/               # Private shared foundation (never shipped alone)
│   └── src/
│       ├── storage/        store.js · session.js · export.js
│       ├── dom/            watcher.js · extractor.js
│       ├── summary/        generator.js · injector.js
│       ├── settings/       prefs.js
│       ├── bridge/         inter-product.js
│       └── index.js
├── orchestra/              # Phase 1 — Chrome Web Store ready
├── relay/                  # Phase 2 — in development
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   └── popup/
├── vault/                  # Phase 3
├── logbook/                # Phase 4
├── prism/                  # Phase 5
└── docs/
    ├── CORE_SDK_SPEC.md
    └── ROADMAP.md
```

---

## Core SDK — Reuse from Orchestra

| Module | Source | Action |
|---|---|---|
| session.js | Orchestra storage | ✅ Migrated & generalised |
| export.js | Orchestra CSV/JSON | ✅ Migrated & cleaned |
| watcher.js | Orchestra content.js | ⚠️ Fresh rewrite (selectors as reference only) |
| injector.js | — | ✅ New implementation |
| generator.js | — | ✅ New implementation (no API key) |

---

## Design Principles

- **English-first.** Japanese localisation planned post-launch.
- **No MoCKA core dependencies.** No ledger, essence, or MCP in mini series.
- **No API keys required** for Core SDK operations.
- **Reverse-flow R&D.** User feedback from mini products flows into MoCKA research.
- **Attack surface reduction.** Mini products expose no MoCKA internals.

---

## Development Commands

```bash
# Load unpacked extension in Chrome
# Chrome → chrome://extensions → Developer mode → Load unpacked → select product folder

# For Relay (during development)
cd relay && open chrome://extensions
```

---

*mini MoCKA Series v1.0 — 2026-05-16*  
*nsjp_kimura / m-sirius-k*

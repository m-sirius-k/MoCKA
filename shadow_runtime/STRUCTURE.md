========================
Shadow Runtime Structure
========================

Directory Layout

shadow_runtime/
│
├── README.md
├── STRUCTURE.md
├── .gitignore
│
├── governance/
│   └── (runtime-only governance notes)
│
├── specs/
│   └── (optional deterministic specs)
│
└── outbox/
    └── (generated outputs, logs, volatile artifacts)

Notes

This layer may contain runnable prototypes and data artifacts.
No coupling to MoCKA core execution and CI is allowed.

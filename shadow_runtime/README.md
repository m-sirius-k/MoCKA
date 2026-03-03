========================
Shadow Runtime Layer
========================

Purpose

This layer contains experimental, runnable, or data-oriented artifacts related to Shadow concepts.
It preserves evolutionary room without contaminating shadow_pj (the purely descriptive layer).

Rules

- Must not modify MoCKA core.
- Must not inject runtime hooks into MoCKA.
- Must not alter CI pipelines.
- Must not contain operational secrets.
- Generated outputs and volatile artifacts belong in shadow_runtime/outbox/.

Boundary

shadow_pj remains byte-stable and non-executable.
shadow_runtime may evolve but must stay uncoupled from MoCKA core execution paths and CI.

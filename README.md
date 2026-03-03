MoCKA v4 - Verifiable Governance Architecture

Architecture Diagram:
docs/mocka_architecture.svg

MoCKA is a deterministic, cryptographically verifiable governance architecture for AI-assisted systems.
It replaces hidden state with sealed, explicit artifacts.

Core Principles
- No Hidden State
- Deterministic Artifacts (UTF-8 no BOM, LF enforced)
- Signed Commits and Tags (Ed25519)
- Explicit Layer Separation
- Reproducibility by Policy

Layer Model
- governance: cryptographic responsibility model
- shadow_pj: immutable descriptive layer
- shadow_runtime: evolution-safe sandbox

Japanese
MoCKA v4 wa, AI shien system no tame no kettei-ronteki de ango-gakuteki ni kensho kanou na tochi architecture desu.
Kakureta joutai o haishi shi, fuin kanou na meishiteki seikabutsu e okikaemasu.

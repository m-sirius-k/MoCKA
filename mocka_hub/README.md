# MoCKA Hub

Institution Gateway Hub for MoCKA.

> Not AI-to-AI. AI-to-Institution.

## Architecture

```
ChatGPT / Claude / Gemini / NotebookLM
         |
   [AI Adapter]        <- AI ごとの差異を吸収
         |
[Institution Gateway]  <- 制度境界。入力検証・権限確認・出力整形
         |
   MoCKA Core          <- Single Source of Truth (SQLite)
```

## Components

- `gateway/` — Institution Gateway Hub (IGH)
- `adapters/` — AI ごとの Adapter
- `manifests/` — AI Agent Manifest (JSON)

## Visibility Levels

| Level | Content | Destination |
|-------|---------|-------------|
| A (public) | Architecture / Agent Roles / Papers / Products / FAQ | GitHub Pages / Public |
| B (internal) | Living Context / Decision summary / Event stats | Notion only |
| C (restricted) | SQLite / Decision detail / MCP config / API keys | Never published |

## Principles

1. AI agents never access MoCKA Core directly
2. All input passes through Gateway validation
3. All output passes through visibility policy check
4. Human Gate approval required for all Decisions
5. Single Source of Truth: MoCKA Core (SQLite)

## Status

- Design: 2026-07-22 (Claude R02 + GPT R01)
- Implementation: Pending (くろこ S02)
- Human Gate: きむら博士

---

*MoCKA Hub — Browse an Institution Like You Browse a Repository.*

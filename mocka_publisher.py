"""
MoCKA Publisher
================
Author : Claude (R02) + GPT (R01) 合同設計
Date   : 2026-07-22
Purpose: MoCKA Core -> 複数形式への一方向配信

Output:
  docs/
  ├── index.html          Public トップ
  ├── architecture.html   MoCKA 設計思想
  ├── ai/
  │   ├── index.html      AI Agent 入口
  │   ├── claude.html     Claude 向け
  │   ├── claude.json     Claude Manifest
  │   ├── chatgpt.html    GPT 向け
  │   ├── chatgpt.json    GPT Manifest
  │   ├── gemini.html     Gemini 向け
  │   ├── gemini.json     Gemini Manifest
  │   └── notebooklm.md  NotebookLM 向け Markdown
  └── assets/
      └── style.css

USAGE:
  python mocka_publisher.py
  python mocka_publisher.py --output docs/
  python mocka_publisher.py --target json
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

MOCKA_DB_PATH = Path(os.environ.get(
    "MOCKA_DB_PATH",
    r"C:\Users\sirok\MoCKA\data\mocka_events.db"
))

DECISION_TYPES = ("DECISION_APPROVED", "phl_decision", "DECISION_REJECTED")

AGENT_MANIFESTS = {
    "claude": {
        "agent": "Claude",
        "role": "R02",
        "authority": ["Documentation", "Audit", "Paper Lead"],
        "read": ["All"],
        "write": [],
        "entry_notion": "https://app.notion.com/p/3a43be67ea2f81789ddfee0c4a7e5cf9",
        "mcp_startup": [
            "mocka_get_overview",
            "mocka_get_todo",
            "mocka_get_essence",
            "mocka_get_guidelines"
        ],
        "restrictions": [
            "Do not write to MoCKA Core without Human Gate approval",
            "Do not merge branches to main directly",
            "Record all changes via mocka_write_event"
        ],
        "version": "1.0"
    },
    "chatgpt": {
        "agent": "ChatGPT (GPT)",
        "role": "R01",
        "authority": ["Design Audit", "Institution Review", "Paper Sub"],
        "read": ["Architecture", "Governance", "Public Decisions", "Evidence"],
        "write": [],
        "entry_public": "/ai/chatgpt.html",
        "restrictions": [
            "Audit only — no implementation",
            "All decisions require Human Gate approval",
            "Do not override R02 documentation"
        ],
        "version": "1.0"
    },
    "gemini": {
        "agent": "Gemini",
        "role": "Adversarial Reviewer",
        "authority": ["Challenge claims", "Identify weaknesses"],
        "read": ["Architecture", "Evidence", "Research"],
        "write": [],
        "entry_public": "/ai/gemini.html",
        "restrictions": [
            "Review only — no implementation",
            "Flag logical inconsistencies",
            "Cannot approve Decisions"
        ],
        "version": "1.0"
    },
    "notebooklm": {
        "agent": "NotebookLM",
        "role": "Literature Analyst",
        "authority": ["Literature search", "Citation analysis"],
        "read": ["Research", "Evidence", "Papers"],
        "write": [],
        "format": "markdown",
        "version": "1.0"
    }
}

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       color: #24292f; background: #fff; line-height: 1.6; }
.header { background: #0d1117; color: #e6edf3; padding: 16px 32px;
          display: flex; align-items: center; gap: 16px; }
.header h1 { font-size: 18px; font-weight: 600; }
.header .badge { background: #238636; color: #fff; padding: 2px 8px;
                 border-radius: 12px; font-size: 12px; }
.nav { background: #f6f8fa; border-bottom: 1px solid #d0d7de;
       padding: 8px 32px; display: flex; gap: 24px; }
.nav a { color: #24292f; text-decoration: none; font-size: 14px; }
.nav a:hover { color: #0969da; }
.container { max-width: 1200px; margin: 0 auto; padding: 32px; }
.status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
               gap: 16px; margin: 24px 0; }
.stat-card { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px;
             padding: 16px; text-align: center; }
.stat-card .value { font-size: 28px; font-weight: 700; color: #0969da; }
.stat-card .label { font-size: 12px; color: #57606a; margin-top: 4px; }
.section { margin: 32px 0; }
.section h2 { font-size: 20px; font-weight: 600; border-bottom: 1px solid #d0d7de;
              padding-bottom: 8px; margin-bottom: 16px; }
.agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
              gap: 16px; }
.agent-card { border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; }
.agent-card h3 { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.agent-card .role { background: #ddf4ff; color: #0550ae; padding: 2px 8px;
                    border-radius: 4px; font-size: 12px; display: inline-block; }
.agent-card a { display: block; margin-top: 8px; color: #0969da; font-size: 13px; }
.tree { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px;
        padding: 16px; font-family: monospace; font-size: 13px; line-height: 1.8; }
.footer { background: #f6f8fa; border-top: 1px solid #d0d7de; padding: 16px 32px;
          font-size: 12px; color: #57606a; text-align: center; margin-top: 48px; }
.health-green { color: #238636; font-weight: 600; }
table { width: 100%; border-collapse: collapse; margin: 16px 0; }
th, td { border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; font-size: 14px; }
th { background: #f6f8fa; font-weight: 600; }
"""


def get_stats(db_path: Path) -> dict:
    if not db_path.exists():
        return {"total_events": "N/A", "total_decisions": "N/A",
                "open_incidents": 0, "last_sync": "N/A"}
    conn = sqlite3.connect(db_path)
    ph_d = ",".join("?" * len(DECISION_TYPES))
    ph_i = "?,?,?"
    stats = {
        "total_events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "total_decisions": conn.execute(
            f"SELECT COUNT(*) FROM events WHERE what_type IN ({ph_d})",
            list(DECISION_TYPES)).fetchone()[0],
        "open_incidents": conn.execute(
            f"SELECT COUNT(*) FROM events WHERE what_type IN ({ph_i})",
            ["INCIDENT", "incident", "OVERDUE_INCIDENT"]).fetchone()[0],
        "seal_count": conn.execute(
            "SELECT COUNT(*) FROM events WHERE what_type IN (?,?)",
            ["AUTO_SEAL_PENDING", "SEAL_READY"]).fetchone()[0],
    }
    conn.close()
    stats["last_sync"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return stats


def build_index(stats: dict) -> str:
    health = "Normal" if stats["open_incidents"] == 0 else "Warning"
    health_class = "health-green" if health == "Normal" else ""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<title>MoCKA Explorer</title>
<style>{CSS}</style></head>
<body>
<div class="header">
  <h1>MoCKA Explorer</h1>
  <span class="badge">Phase 4</span>
  <span style="font-size:13px;color:#7d8590;margin-left:auto">
    Browse an Institution Like You Browse a Repository.
  </span>
</div>
<nav class="nav">
  <a href="index.html">Home</a>
  <a href="architecture.html">Architecture</a>
  <a href="ai/index.html">AI Agents</a>
  <a href="https://github.com/m-sirius-k/MoCKA">GitHub</a>
</nav>
<div class="container">
  <p style="color:#57606a;margin-bottom:24px">
    MoCKA (Model of Cybernetic Knowledge Architecture) —
    AI governance framework by Masahito Kimura.
    <strong>AIを信じるな、システムで縛れ。</strong>
  </p>

  <div class="section">
    <h2>Project Status</h2>
    <div class="status-grid">
      <div class="stat-card">
        <div class="value">{stats['total_events']:,}</div>
        <div class="label">Total Events</div>
      </div>
      <div class="stat-card">
        <div class="value">{stats['total_decisions']}</div>
        <div class="label">Decisions</div>
      </div>
      <div class="stat-card">
        <div class="value {health_class}">{health}</div>
        <div class="label">Health</div>
      </div>
      <div class="stat-card">
        <div class="value">{stats['open_incidents']}</div>
        <div class="label">Open Incidents</div>
      </div>
    </div>
    <p style="font-size:12px;color:#57606a">Last sync: {stats['last_sync']}</p>
  </div>

  <div class="section">
    <h2>AI Agent Entry Points</h2>
    <div class="agent-grid">
      <div class="agent-card">
        <h3>Claude</h3>
        <span class="role">R02 — Documentation</span>
        <a href="ai/claude.html">Entry →</a>
        <a href="ai/claude.json">manifest.json</a>
      </div>
      <div class="agent-card">
        <h3>ChatGPT</h3>
        <span class="role">R01 — Audit</span>
        <a href="ai/chatgpt.html">Entry →</a>
        <a href="ai/chatgpt.json">manifest.json</a>
      </div>
      <div class="agent-card">
        <h3>Gemini</h3>
        <span class="role">Adversarial Reviewer</span>
        <a href="ai/gemini.html">Entry →</a>
        <a href="ai/gemini.json">manifest.json</a>
      </div>
      <div class="agent-card">
        <h3>NotebookLM</h3>
        <span class="role">Literature Analyst</span>
        <a href="ai/notebooklm.md">context.md</a>
        <a href="ai/notebooklm.json">manifest.json</a>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Repository Browser</h2>
    <div class="tree">
MoCKA Explorer
├── Institution
│   ├── Decision Ledger    ({stats['total_decisions']} decisions)
│   ├── Event Store        ({stats['total_events']:,} events)
│   ├── Evidence
│   └── Incidents          ({stats['open_incidents']} open)
├── Projects
│   ├── MoCKA Core
│   ├── mini-MoCKA Series
│   │   ├── Orchestra
│   │   ├── Relay
│   │   └── PHI-OS
│   └── Research (AAAI 2027)
└── Developer
    ├── API Reference (MCP 23 tools)
    ├── GitHub: m-sirius-k/MoCKA
    └── Sync: mocka_notion_sync.py
    </div>
  </div>

  <div class="section">
    <h2>Rules</h2>
    <ol style="padding-left:20px;font-size:14px;line-height:2">
      <li>This site is Read Only — MoCKA Core is the Single Source of Truth</li>
      <li>All Decisions require Human Gate approval (きむら博士)</li>
      <li>Local sessions must run MoCKA MCP startup protocol</li>
      <li>Record changes via mocka_write_event only</li>
      <li>Never write to Notion directly — sync from MoCKA Core only</li>
    </ol>
  </div>
</div>
<div class="footer">
  MoCKA Explorer — Built by Claude (R02) &amp; GPT (R01) — 2026-07-22 —
  Human Gate: きむら博士 —
  <a href="https://github.com/m-sirius-k/MoCKA">GitHub</a>
</div>
</body></html>"""


def build_agent_html(key: str, m: dict) -> str:
    read_list = "".join(f"<li>{r}</li>" for r in m.get("read", []))
    restrict_list = "".join(f"<li>{r}</li>" for r in m.get("restrictions", []))
    startup = ""
    if m.get("mcp_startup"):
        startup = "<h3 style='margin-top:16px'>MCP Startup Protocol</h3><ol style='padding-left:20px;font-size:14px;line-height:2'>" + \
                  "".join(f"<li><code>{s}</code></li>" for s in m["mcp_startup"]) + "</ol>"
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MoCKA — {m['agent']}</title>
<style>{CSS}code{{background:#f6f8fa;padding:2px 6px;border-radius:4px;font-size:13px}}</style>
</head><body>
<div class="header">
  <h1>MoCKA Explorer — {m['agent']}</h1>
  <span class="badge">{m['role']}</span>
</div>
<nav class="nav">
  <a href="../index.html">Home</a>
  <a href="index.html">AI Agents</a>
  <a href="{key}.json">manifest.json</a>
</nav>
<div class="container">
  <div class="section">
    <h2>Agent Profile</h2>
    <table>
      <tr><th>Agent</th><td>{m['agent']}</td></tr>
      <tr><th>Role</th><td>{m['role']}</td></tr>
      <tr><th>Authority</th><td>{', '.join(m.get('authority', []))}</td></tr>
      <tr><th>Write Access</th><td>{'None' if not m.get('write') else ', '.join(m['write'])}</td></tr>
    </table>
  </div>
  <div class="section">
    <h2>Read Access</h2>
    <ul style="padding-left:20px;font-size:14px;line-height:2">{read_list}</ul>
  </div>
  {startup}
  <div class="section">
    <h2>Restrictions</h2>
    <ul style="padding-left:20px;font-size:14px;line-height:2;color:#cf222e">{restrict_list}</ul>
  </div>
  <div class="section">
    <h2>MoCKA Overview</h2>
    <p style="font-size:14px">
      MoCKA (Model of Cybernetic Knowledge Architecture) is an AI governance framework
      designed by Masahito Kimura. Philosophy: <strong>Do not trust AI — constrain it with systems.</strong>
    </p>
    <p style="font-size:14px;margin-top:8px">
      Single Source of Truth: SQLite database on local MoCKA server.<br>
      Human Gate: きむら博士 — all final approvals.<br>
      Current Phase: 4 (Commercial) | AAAI 2027 paper submitted.
    </p>
  </div>
</div>
<div class="footer">MoCKA Explorer — {m['agent']} Entry — 2026-07-22</div>
</body></html>"""


def build_notebooklm_md(stats: dict) -> str:
    return f"""# MoCKA Context — NotebookLM

## What is MoCKA

MoCKA (Model of Cybernetic Knowledge Architecture) is an AI governance framework
designed by Masahito Kimura. Philosophy: Do not trust AI, constrain it with systems.

## Current Status

- Phase: 4 (Commercial)
- Total Events: {stats['total_events']:,}
- Decisions: {stats['total_decisions']} (Human Gate approved)
- Open Incidents: {stats['open_incidents']}
- AAAI 2027 paper: Submitted 2026-07-19
- Formal Core: S_DTS = (E, P, V)

## Agent Roles

| Role | Agent | Responsibility |
|------|-------|---------------|
| R01 | GPT | Audit / Design Review |
| R02 | Claude | Documentation / Paper Lead |
| S02 | Claude Code (くろこ) | Implementation |
| Human Gate | きむら博士 | Final approval |

## Key Decisions (Recent)

- DC_20260719_021: Paper work complete (final hash: 1c5cb9be...)
- DC_20260719_005: Formal Core S_DTS=(E,P,V) confirmed
- DC_20260719_004: Paper Lead transferred GPT -> Claude

## Products

- Orchestra: Chrome extension for multi-AI orchestration (Live)
- Relay: Session handoff management
- PHI-OS: Shared infrastructure layer

## Architecture

```
MoCKA Core (SQLite)
      |
      v
MoCKA Publisher
      |
      +-- Notion (Internal Explorer)
      +-- HTML  (Public Docs)
      +-- JSON  (AI Manifests)
      +-- Markdown (NotebookLM / GitHub)
```

## Rules

1. Read Only — MoCKA Core is Single Source of Truth
2. All Decisions require Human Gate approval
3. Never write to Notion directly

*Generated by MoCKA Publisher — {stats['last_sync']}*
"""


def build_ai_index() -> str:
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MoCKA — AI Agent Index</title>
<style>{CSS}</style></head><body>
<div class="header"><h1>MoCKA Explorer — AI Agent Index</h1></div>
<nav class="nav">
  <a href="../index.html">Home</a>
</nav>
<div class="container">
  <div class="section">
    <h2>AI Agent Entry Points</h2>
    <p style="font-size:14px;color:#57606a;margin-bottom:16px">
      Each AI agent has a dedicated entry point with role, authority, and restrictions.
    </p>
    <table>
      <tr><th>Agent</th><th>Role</th><th>HTML</th><th>JSON Manifest</th></tr>
      <tr><td>Claude</td><td>R02 — Documentation</td>
          <td><a href="claude.html">claude.html</a></td>
          <td><a href="claude.json">claude.json</a></td></tr>
      <tr><td>ChatGPT</td><td>R01 — Audit</td>
          <td><a href="chatgpt.html">chatgpt.html</a></td>
          <td><a href="chatgpt.json">chatgpt.json</a></td></tr>
      <tr><td>Gemini</td><td>Adversarial Reviewer</td>
          <td><a href="gemini.html">gemini.html</a></td>
          <td><a href="gemini.json">gemini.json</a></td></tr>
      <tr><td>NotebookLM</td><td>Literature Analyst</td>
          <td><a href="notebooklm.md">notebooklm.md</a></td>
          <td><a href="notebooklm.json">notebooklm.json</a></td></tr>
    </table>
  </div>
</div>
<div class="footer">MoCKA Explorer — 2026-07-22</div>
</body></html>"""


def publish(output_dir: Path, db_path: Path):
    stats = get_stats(db_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    ai_dir = output_dir / "ai"
    ai_dir.mkdir(exist_ok=True)

    # index.html
    (output_dir / "index.html").write_text(build_index(stats), encoding="utf-8")
    print("[PUB] docs/index.html")

    # AI index
    (ai_dir / "index.html").write_text(build_ai_index(), encoding="utf-8")
    print("[PUB] docs/ai/index.html")

    # Agent HTML + JSON
    for key, m in AGENT_MANIFESTS.items():
        if key == "notebooklm":
            (ai_dir / "notebooklm.md").write_text(
                build_notebooklm_md(stats), encoding="utf-8")
            print("[PUB] docs/ai/notebooklm.md")
        else:
            (ai_dir / f"{key}.html").write_text(
                build_agent_html(key, m), encoding="utf-8")
            print(f"[PUB] docs/ai/{key}.html")
        (ai_dir / f"{key}.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[PUB] docs/ai/{key}.json")

    print(f"\n[PUB] Done. {len(list(output_dir.rglob('*')))} files in {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="MoCKA Publisher")
    parser.add_argument("--output", default="docs", help="Output directory")
    parser.add_argument("--db-path", default=str(MOCKA_DB_PATH))
    args = parser.parse_args()
    publish(Path(args.output), Path(args.db_path))


if __name__ == "__main__":
    main()

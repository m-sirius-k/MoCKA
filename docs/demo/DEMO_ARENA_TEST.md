# MoCKA Demo Arena

## Verification Demonstration Environment

> Experimental space for observing the MoCKA verification system.

MoCKA Demo Arena is the **demonstration environment of the MoCKA ecosystem**.  
It provides a concrete, inspectable view of verification flows, research workflow, and institutional memory outputs.

MoCKA Demo Arena は **MoCKA エコシステムのデモ実験環境** です。  
検証フロー、研究ワークフロー、制度的記憶の出力を実際に観測できる場所です。

---

## Scope

This page focuses on demonstrable behaviors.  
It is designed to be readable as a standalone test page.

このページは「実際に見える動作」に絞って構成します。  
単体で読めるテストページとして設計しています。

---

## Ecosystem Architecture

```mermaid
flowchart LR
  A[MoCKA Core] --> B[Knowledge Gate]
  A --> C[Civilization Layer]
  A --> D[Transparency Layer]
  A --> E[External Brain]
  A --> F[Core Private]
  B --> G[Institutional Memory]
  D --> H[Audit Evidence]
  E --> I[External Knowledge]
  C --> J[Governance Philosophy]
Research Workflow
Verification Architecture
Repository Structure
MoCKA
├ docs
├ tools
├ experiments
├ canon
└ artifacts
Quick Verification Demo
cd C:\Users\sirok\mocka-ecosystem
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1
Quick Verification Demo (日本語)
cd C:\Users\sirok\mocka-ecosystem
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1
Demo Observation Checklist

 Verify that all Mermaid diagrams render without errors.

 Confirm repository structure block keeps alignment.

 Run the verification command and observe output artifacts.

 Confirm links are navigable from this page.

Observation Points

Verification surface (what is checked)

System integrity checks

Research process checks

Documentation checks

Audit and evidence checks

Artifact surface (what is produced)

JSON artifacts

Logs

Trace notes

Related Repositories
LayerRepository
MoCKA CoreMoCKA

Knowledge GateMoCKA-KNOWLEDGE-GATE

Transparencymocka-transparency

External Brainmocka-external-brain

Civilizationmocka-civilization

Core Privatemocka-core-private
Notes

If a Mermaid block fails to render, confirm that the block is closed with a terminating ``` on its own line.
Avoid placing any text immediately after the closing fence.

Mermaid が表示されない場合、ブロック終端の ``` が単独行になっているか確認してください。
終端直後に文字列を続けて書かないでください。

System Status

Research Infrastructure: operational
Verification System: active
Experiment Framework: running

MoCKA Demo Arena demonstrates the self-verifying architecture of the ecosystem.

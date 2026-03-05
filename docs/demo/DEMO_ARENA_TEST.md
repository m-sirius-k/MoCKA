 # MoCKA Demo Arena

 A live demonstration surface for the MoCKA ecosystem.
 This page exposes the verification structure, research workflow, and institutional memory flow in a form that can be inspected directly.

 ---

 ## Verification Demonstration Environment

 MoCKA Demo Arena is the demonstration environment of the MoCKA ecosystem.
 It exposes how experiments, verification procedures, and institutional memory interact in a verifiable research system.

 MoCKA Demo Arena は MoCKA エコシステムの検証デモ環境です。
 実験、検証プロセス、制度的記憶の流れを可視化し、研究基盤として観測できる形で公開しています。

 ---

 ## What This Page Demonstrates

 This page demonstrates four essential aspects of the MoCKA ecosystem.

 - Ecosystem architecture
 - Research workflow
 - Verification architecture
 - Repository organization

 These elements together illustrate how MoCKA maintains reproducible and verifiable research infrastructure.

 ---

 ## Ecosystem Architecture

 The MoCKA ecosystem is composed of several interconnected layers.
 Each layer contributes a specific responsibility to the system.

 ```mermaid
 flowchart LR

   A[MoCKA Core]

   A --> B[Knowledge Gate]
   A --> C[Civilization Layer]
   A --> D[Transparency Layer]
   A --> E[External Brain]
   A --> F[Core Private]

   B --> G[Institutional Memory]
   D --> H[Audit Evidence]
   E --> I[External Knowledge]
   C --> J[Governance Philosophy]

 ```

 Layer overview

 - MoCKA Core
   Execution engine for research verification.

 - Knowledge Gate
   Institutional memory layer storing reasoning artifacts and research outcomes.

 - Civilization Layer
   Governance philosophy and long-term structural design of the ecosystem.

 - Transparency Layer
   Public audit trail and verification outputs.

 - External Brain
   External knowledge synchronization and extended research context.

 - Core Private
   Internal secure execution environment.

 ---

 ## Research Workflow

 The research workflow represents the lifecycle of a MoCKA experiment.
 Each experiment produces verifiable artifacts and institutional knowledge.

 ```mermaid
 flowchart LR

   A[Experiment]

   A --> B[Experiment Registry]
   B --> C[Research Gate Verification]
   C --> D[Artifact Generation]
   D --> E[Knowledge Gate Archival]
   E --> F[Institutional Memory]

 ```

 Workflow description

 1. Experiment
    A hypothesis or research action is executed.

 2. Experiment Registry
    The experiment is registered for reproducibility.

 3. Research Gate Verification
    Verification procedures confirm experiment validity.

 4. Artifact Generation
    Structured artifacts such as JSON outputs and logs are produced.

 5. Knowledge Gate Archival
    Artifacts are archived into the institutional memory layer.

 6. Institutional Memory
    Results become part of the long-term research knowledge base.

 ---

 ## Verification Architecture

 MoCKA verification combines several categories of checks.
 Together they guarantee the integrity of research operations.

 ```mermaid
 flowchart TD

   A[System Integrity Verification]
   B[Research Process Verification]
   C[Documentation Verification]
   D[Audit and Evidence Verification]

   A --> R[Research Run]
   B --> R
   C --> R
   D --> R

   R --> E[Emit Artifacts]
   E --> F[Traceable Evidence]

 ```

 Verification categories

 - System Integrity Verification
   Repository structure, execution environment, and integrity checks.

 - Research Process Verification
   Experiment registration and research workflow validation.

 - Documentation Verification
   README and documentation consistency checks.

 - Audit and Evidence Verification
   Artifact generation and traceable evidence production.

 ---

 ## Repository Structure

 ```text
 MoCKA
 ├ docs
 │   └ demo
 │
 ├ tools
 │
 ├ experiments
 │
 ├ canon
 │
 └ artifacts
 ```

 ---

 ## Quick Verification Demo

 ```text
 cd C:\Users\sirok\mocka-ecosystem
 powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1
 ```

 ---

 ## Demo Observation Checklist

 - Mermaid diagrams render without errors
 - Repository structure formatting remains aligned
 - Verification command produces artifact outputs
 - Navigation links remain functional

 ---

 ## Artifact Outputs

 - JSON artifacts
 - Execution logs
 - Trace notes

 ---

 ## Related Repositories

 | Layer | Repository |
 |------|-----------|
 | MoCKA Core | MoCKA |
 | Knowledge Gate | MoCKA-KNOWLEDGE-GATE |
 | Transparency | mocka-transparency |
 | External Brain | mocka-external-brain |
 | Civilization | mocka-civilization |
 | Core Private | mocka-core-private |

 ---

 ## System Status

 - Research Infrastructure : operational
 - Verification System : active
 - Experiment Framework : running

 ---

 MoCKA Demo Arena demonstrates the self-verifying architecture of the ecosystem.

 ============================================================
 日本語版
 ============================================================

 # MoCKA Demo Arena

 MoCKA エコシステムの構造と検証フローを観測できるデモページです。
 このページでは研究実行・検証・制度的記憶の流れを可視化しています。

 ---

 ## 検証デモ環境

 MoCKA Demo Arena は MoCKA の検証実行環境を説明するデモページです。
 実験、検証、記録という研究プロセスがどのように連携しているかを示します。

 ---

 ## エコシステム構造

 ```mermaid
 flowchart LR

   A[MoCKA Core]

   A --> B[Knowledge Gate]
   A --> C[Civilization Layer]
   A --> D[Transparency Layer]
   A --> E[External Brain]
   A --> F[Core Private]

   B --> G[Institutional Memory]
   D --> H[Audit Evidence]
   E --> I[External Knowledge]
   C --> J[Governance Philosophy]

 ```

 ---

 ## 研究ワークフロー

 ```mermaid
 flowchart LR

   A[実験]

   A --> B[実験レジストリ]
   B --> C[研究ゲート検証]
   C --> D[成果物生成]
   D --> E[Knowledge Gate 保存]
   E --> F[制度的記憶]

 ```

 ---

 ## 検証アーキテクチャ

 ```mermaid
 flowchart TD

   A[システム整合性検証]
   B[研究プロセス検証]
   C[ドキュメント検証]
   D[監査証跡検証]

   A --> R[研究実行]
   B --> R
   C --> R
   D --> R

   R --> E[成果物生成]
   E --> F[検証可能証跡]

 ```

 ---

 ## システム状態

 - 研究インフラ : 稼働中
 - 検証システム : 稼働中
 - 実験フレームワーク : 稼働中

 MoCKA Demo Arena は自己検証型研究アーキテクチャのデモです。
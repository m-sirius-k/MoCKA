 # MoCKA Demo Arena

 A demonstration environment for the MoCKA Insight System.
 This page reveals how MoCKA organizes AI research, verification, and institutional memory into a reproducible system.

 MoCKA Demo Arena は、MoCKA Insight System の実行・検証・記録の流れを観測できるデモページです。

 ------------------------------------------------------------

 ## What is MoCKA

 MoCKA is a verifiable AI research system designed to transform how knowledge is produced, validated, and preserved.

 Traditional AI systems generate answers.
 MoCKA builds a continuously improving knowledge system.

 Instead of producing isolated results, MoCKA treats every experiment as part of a verifiable research process.

 The system integrates several capabilities normally separated in conventional AI systems.

 - AI orchestration
 - verification pipelines
 - institutional memory
 - governance architecture

 Together these components form the **MoCKA Insight System**.

 ------------------------------------------------------------

 ## Architecture Overview

 The MoCKA Insight System is built around two complementary layers.

 Movement
 The trusted core of the system responsible for verification, governance, and institutional memory.

 Exterior
 The evolving research surface where experiments and AI orchestration expand continuously.

  Click the architecture preview below to explore the full architecture.

 [![MoCKA Insight Architecture](docs/images/mocka_insight_architecture_preview.png)](docs/architecture/mocka_insight_architecture.md)

 ------------------------------------------------------------

 ## The MoCKA Knowledge Cycle

 Most AI workflows follow a simple pattern.

 AI → Result

 A result appears, but the reasoning behind it may not be verifiable, reproducible, or preserved.

 MoCKA introduces a fundamentally different structure.

 AI → Verification → Record → Institutional Memory

 This structure forms a continuous knowledge cycle.

 ```mermaid
 flowchart LR

   A[AI Execution]

   A --> V[Verification]
   V --> R[Record Artifacts]
   R --> M[Institutional Memory]
   M --> K[Verified Knowledge Base]

   K --> A

 ```

 AI generates hypotheses or answers.
 Verification confirms their validity.
 Recording preserves artifacts and reasoning traces.
 Institutional memory accumulates verified knowledge.

 Over time this produces a growing body of reliable knowledge.

 ------------------------------------------------------------

 ## Recoverable Knowledge

 A critical property of MoCKA is that every step is recorded.

 Every experiment produces traceable artifacts.

 - logs
 - JSON outputs
 - verification traces

 ```mermaid
 flowchart TD

   A[Experiment Execution]

   A --> B[Logs]
   A --> C[JSON Artifacts]
   A --> D[Verification Traces]

   B --> E[Recorded Evidence]
   C --> E
   D --> E

   E --> F[Institutional Memory]

 ```

 Because these artifacts are preserved, knowledge is not fragile.

 If an error occurs, the system can return to a previously verified state.

 ```mermaid
 flowchart LR

   A[Current State]
   A --> B[Problem Detected]
   B --> C[Rollback]
   C --> D[Last Verified Record]
   D --> E[Stable Knowledge Base]

 ```

 MoCKA does not only generate answers.

 It builds **recoverable facts**.

 ------------------------------------------------------------

 ## Core Concepts

 MoCKA is designed around four structural pillars.

 1 Verifiable AI execution
 2 Institutional memory
 3 Research orchestration
 4 Transparent verification

 These elements allow research processes to remain inspectable and reproducible.

 ------------------------------------------------------------

 ## Insight Architecture

 ```mermaid
 flowchart LR

   A[MoCKA Movement]

   B[Verification Engine]
   C[Governance Logic]
   D[Institutional Memory]

   E[MoCKA Exterior]

   F[Experiments]
   G[AI Orchestration]
   H[Research Expansion]

   A --> B
   A --> C
   A --> D

   E --> F
   E --> G
   E --> H

   F --> B
   G --> B

 ```

 Movement ensures reliability.
 Exterior enables continuous evolution.

 Most components of the Exterior are still expanding.

 ------------------------------------------------------------

 ## Research Workflow

 ```mermaid
 flowchart LR

   A[Experiment]

   A --> B[Experiment Registry]
   B --> C[Research Gate Verification]
   C --> D[Artifact Generation]
   D --> E[Knowledge Gate Archival]
   E --> F[Institutional Memory]

 ```

 ------------------------------------------------------------

 ## Verification Architecture

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

 ------------------------------------------------------------

 ## Repository Structure

 ```mermaid
 flowchart TB

   A[MoCKA Repository]

   A --> B[docs]
   B --> B1[demo]

   A --> C[tools]
   A --> D[experiments]
   A --> E[canon]
   A --> F[artifacts]

 ```

 ------------------------------------------------------------

 ## 日本語版

 MoCKA Demo Arena は MoCKA Insight System のデモページです。

 このページでは

 - システム構造
 - 研究ワークフロー
 - 検証アーキテクチャ
 - 知識循環構造

 を図とともに説明しています。

 MoCKA の最も重要な特徴は

 **AI → 検証 → 記録 → 制度的記憶**

 という知識循環です。

 AI の結果は検証され、
 記録され、
 制度的記憶として蓄積されます。

 検索すればするほど

 正しい知識が増え
 回答精度が向上します。

 さらにすべての処理が記録されるため、

 **誤りがあっても過去の正しい状態へ戻ることができます。**

 ------------------------------------------------------------

 MoCKA Demo Arena demonstrates the self-verifying architecture of the MoCKA Insight System.

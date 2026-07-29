# PHI Module Interface Contract v0.1

**Status:** DESIGN(契約定義案。実装・Decision Ledger登録はまだ行わない)
**位置づけ:** PHI-OS Operational Integration Phase, **I-01**。各Module間の契約を定義する。統合手順(独立性維持→Interface定義→Simulation→限定統合→Verification)のうち、本文書は「Interface定義」段階に相当する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 0. 対象構造

```
PHI-OS Core

 +-- MoCKA
 +-- Memory
 +-- Orchestra
 +-- Relay
 +-- Sequence Controller
```

各Moduleについて、Input / Output / Authority Boundary / Error Handling / Evidence Requirementを定義する。

---

## 1. MoCKA Interface Contract

| 項目 | 内容 |
|---|---|
| Input | Sequence Controllerからの Event候補・Decision候補 |
| Output | Verification結果、Gate通過/却下判定、Audit記録 |
| Authority Boundary | Event Authority/Knowledge Authority/Gate Authority/Version Authority/Verification Authority/Institution Authority(`PHI_OS_CONSTITUTION_v1.md`第3章)を保持。他Moduleはこれらを代行できない |
| Error Handling | 検証失敗時はEvent/Decisionを却下し理由を返す。サイレント失敗は禁止(既存インシデント知見、`TODO_390`等と整合) |
| Evidence Requirement | すべての入力は一次資料参照(Evidence)を伴わなければならない |

**境界(重要): MoCKAを侵食しない。** 他ModuleがGate相当の判断(検証・監査)を独自実装し、MoCKAを迂回することを禁止する。`DC_20260728_003`が定めた「PHI-OS CoreからMoCKA本体`phi_os/`パッケージへの直接import禁止」は本契約でも継続適用される。

---

## 2. Memory Interface Contract

| 項目 | 内容 |
|---|---|
| Input | Event/Decision/Semantic/Procedural Memoryの書込要求 |
| Output | Context Reconstruction結果、Retrieval結果 |
| Authority Boundary | 保存・再構成のみを担当し、判断は行わない(`PHI_MEMORY_ARCHITECTURE_v1.0.md`§1) |
| Error Handling | 未署名・破損の疑いがあるデータも`EVENT_DATA_LIFECYCLE_v1.md`の方針に従い削除せず保持し、異常として記録する |
| Evidence Requirement | Retrieval結果には出典(`event_id`/`decision_id`)を必ず添付する |

**境界(重要): Memoryを単なるDBにしない。** Memoryは常に分類(Event/Decision/Semantic/Procedural)・検証(署名確認)・Access Control(Phase I-03で別途定義)を経て提供される。生のSELECT文でDBを直接参照する経路は、本契約が定義するMemory Interfaceの対象外とする。

---

## 3. Orchestra Interface Contract

| 項目 | 内容 |
|---|---|
| Input | Sequence Controllerからのモデル選択要求(Model Selection) |
| Output | 選択されたモデル/能力の実行結果 |
| Authority Boundary | 「どのモデル・能力を使うか」の調整のみを担当。誰が最終決定権を持つか(Authority)には関与しない |
| Error Handling | モデル選択失敗時はSequence Controllerへエラーを返し、勝手に代替実行しない |
| Evidence Requirement | 選択理由(能力表・信頼レベル等)を記録する |

**境界(重要): OrchestraをAuthority Layerにしない。** Orchestraが「どの判断を採用するか」を決定する権限を持つことは許されない。これはPHI-Con(Constitution)・MoCKA(Gate)が担う領域であり、Orchestraはモデル選択・協調制御に限定される。

---

## 4. Relay Interface Contract

| 項目 | 内容 |
|---|---|
| Input | 外部システムの状態変化通知 |
| Output | 状態同期結果 |
| Authority Boundary | 状態同期のみを担当。同期した情報の真偽・信頼性判断は行わない |
| Error Handling | 同期失敗時は静かに失敗せず、Sequence Controllerへ通知する |
| Evidence Requirement | 同期元・同期時刻を記録する |

**境界(重要): RelayをTrust Layerにしない。** Relayが同期した外部状態を無条件に信頼できる事実として扱ってはならない。信頼性の判断はMoCKA(Verification Authority)またはMemory(Evidence Chain確認)側の責務であり、Relay自身が「これは正しい」と判定することは許されない。

---

## 5. Sequence Controller Interface Contract

| 項目 | 内容 |
|---|---|
| Input | Observation/User Intent/External Event |
| Output | Action Request/Decision Candidate/Audit Event |
| Authority Boundary | 判断候補生成・Module呼出・Gate要求のみを担当(`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`§5)。最終判断・Authority変更・Evidenceなし実行は行わない |
| Error Handling | いずれかのModuleがエラーを返した場合、実行を停止しHuman Gateへ差し戻す |
| Evidence Requirement | すべてのAction RequestはVerification/Planning段階のEvidenceを伴う |

**境界(重要、最上位): Sequence ControllerをDecision Makerにしない。** Sequence Controllerが単独で「実行してよい」と最終確定することは禁止される。この境界は本契約全体の前提であり、他の4契約(MoCKA/Memory/Orchestra/Relay)はいずれも、この境界が破られないよう相互に設計されている。

---

## 6. Cross-Module原則

- いずれのModuleも、他Moduleの既存Authorityを代行・侵食してはならない
- Authority Flow(PHI-Con/PHI-Core間の統治関係)は`DC_20260729_009`によりPending Resolutionのまま維持されている。本契約はこの未確定状態を前提とし、いずれのModule契約もAuthority Flowの確定を要求しない
- 5つの契約はいずれも「独立運用可能」という既存資産の価値を壊さない。本契約は各Moduleの独立性を前提とした**境界の明文化**であり、統合実装そのものではない

---

## 7. 本契約で決めないこと

- 各Moduleの内部実装詳細
- Simulation設計(Phase I-05)
- Sequence Controller State Model(Phase I-02)
- Memory Access Control Policy(Phase I-03)
- Human Gate Integration Model(Phase I-04)

---

## Knowledge Lineage

**Document:** PHI_MODULE_INTERFACE_CONTRACT_v0.1.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** きむら博士よりPHI-OS Operational Integration Phase I-01として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md
- docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md
- PHI_OS_CONSTITUTION_v1.md
- DC_20260728_003、DC_20260729_009
**Derived From:** PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0、PHI_MEMORY_ARCHITECTURE_v1.0
**Supersedes:** なし
**Reason For Creation:** Module間の契約(Input/Output/Authority Boundary/Error Handling/Evidence Requirement)を明文化し、統合作業(Interface定義→Simulation→限定統合→Verification)の第一段階を完了するため。
**Affected Components:** MoCKA、Memory、Orchestra、Relay、Sequence Controller(`phios/core/*`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。5Module分の契約(Input/Output/Authority Boundary/Error Handling/Evidence Requirement)、境界明記、Cross-Module原則、本契約で決めないことを記載。実装・Decision Ledger登録は無し。

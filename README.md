# MoCKA

MoCKA is a deterministic governance and verifiable orchestration architecture for AI operations.
It treats memory, decisions, and evidence as first-class artifacts and preserves them as reproducible, cryptographically-verifiable records.

This repository is part of the MoCKA Ecosystem and represents the execution and orchestration layer.

## Architecture Overview

MoCKA is designed around a strict separation between canonical local state (infield) and publishable/replicable state (outfield).
The architecture below shows the ecosystem-level components and how MoCKA connects to verification, transparency, and external brain layers.

![MoCKA Architecture Overview](docs/architecture/mocka_architecture_overview.png)

## Security Model

MoCKA assumes that AI outputs may be incorrect, incomplete, or adversarially influenced.
Security is achieved by making state transitions explicit and verifiable.

Threats considered:

- Silent state drift (implicit changes without an auditable trace)
- Tampered artifacts (modified files without detection)
- Non-deterministic execution (unreproducible decisions)
- Loss of provenance (missing origin and decision context)

Controls:

- Canonicalization: LF-first normalization and strict repository hygiene
- Cryptographic integrity: SHA-256 chaining for deterministic evidence trails
- Authenticity: Ed25519 signatures for governance-grade commitments
- Time anchoring: RFC3161 timestamping for externally verifiable time proofs (where applicable)
- Multi-observer structure: separation of roles and redundancy in verification

## Repository Responsibility

MoCKA (this repository) focuses on:

- Orchestrating deterministic phases and producing structured artifacts
- Generating evidence packs suitable for review and reproduction
- Providing a stable execution surface for the ecosystem layers

## Verification and Transparency

MoCKA is designed to work with ecosystem repositories:

- Transparency layer: public-facing proofs and logs
- Knowledge gate: institutional memory and trace preservation
- Civilization layer: governance definitions and doctrine

## How to Navigate

- docs/architecture/ : ecosystem overview diagrams and references
- infield/ : canonical local evidence and governance artifacts (when applicable)
- outfield/ : publishable outputs and transparency-ready exports (when applicable)

---

# MoCKA（日本語）

MoCKA は、AI運用を「決定可能」で「検証可能」にするための統治・オーケストレーション設計です。
記憶、判断、根拠を一次成果物として扱い、再現可能かつ暗号学的に検証できる記録として保存します。

本リポジトリは MoCKA Ecosystem の一部であり、実行およびオーケストレーション層を担当します。

## Architecture Overview（全体図）

MoCKA は、正本のローカル状態（infield）と、公開・複製可能な状態（outfield）を厳密に分離します。
下図はエコシステム全体の構成と、MoCKA が検証・透明性・外部脳レイヤへ接続する関係を示します。

![MoCKA Architecture Overview](docs/architecture/mocka_architecture_overview.png)

## Security Model（脅威と対策）

MoCKA は、AI出力が誤り・欠落・誘導を含み得ることを前提にします。
安全性は「状態遷移を明示し、検証できる形で残す」ことで成立させます。

想定する脅威：

- 監査痕跡のない状態変化（サイレントなドリフト）
- 成果物の改ざん（検知不能な編集）
- 非決定的な実行（再現不能な判断）
- 来歴の喪失（生成元や判断理由が失われる）

対策：

- 正本化：LF 正規化とリポジトリ衛生の厳格化
- 完全性：SHA-256 連鎖による証拠トレイル
- 真正性：Ed25519 署名による統治級コミット
- 時刻固定：RFC3161 タイムスタンプ（適用可能な場合）
- 多重観測：役割分離と冗長な検証構造

## 本リポジトリの責務

MoCKA（本リポジトリ）は次を担当します。

- 決定可能なフェーズ実行と構造化成果物の生成
- 再現とレビューに耐える証拠パックの出力
- エコシステム各層が依存できる安定した実行面の提供

## 検証と透明性の接続

MoCKA は、次のエコシステム repo と連携します。

- transparency：公開検証（proof/log）
- knowledge-gate：制度的記憶（trace保存）
- civilization：統治定義（思想と規範）

## ナビゲーション

- docs/architecture/ : 全体図と参照
- infield/ : 正本・根拠・統治（適用時）
- outfield/ : 公開可能な出力（適用時）

# MoCKA Runtime

Model of Cybernetic Knowledge Architecture

## Architecture

![MoCKA Overview](docs/images/mocka_overview.svg)

### Governance Layer

Defines how decisions are made and controlled.

- execution_order_engine
- dispatcher
- meta_audit_engine
- preventive_rule_engine

## What is MoCKA

MoCKA is not a conventional AI system.

It is a deterministic and verifiable architecture that models how a knowledge-generating civilization operates.

Instead of relying on hidden internal state, MoCKA transforms all processes into:

- Structured records
- Append-only logs
- Auditable decisions
- Reproducible outcomes

This enables knowledge to become traceable, reliable, and continuously improvable.

## Why it matters

Most AI systems cannot explain how they reached a result.

MoCKA changes this.

Every action is:

- Recorded
- Verified
- Audited
- Learned from

This creates a system where:

- Failure is prevented before it occurs
- Decisions are accountable
- Improvements are cumulative

## Civilization Loop

MoCKA operates as a closed-loop system:

Observation → Record → Incident → Recurrence → Prevention → Decision → Action → Audit → Learning

This loop transforms isolated execution into a self-regulating structure.

## Architecture

### Governance Layer

Defines how decisions are made and controlled.

- execution_order_engine
- dispatcher
- meta_audit_engine
- preventive_rule_engine

### Record Layer

Ensures all events are structured and reusable.

- csv_record_engine
- recurrence_engine
- improvement_loop

### Core Runtime

Drives the entire civilization loop.

- main_loop

## Quick Start

Run the system:

```bash
python -m runtime.main_loop
```

If correctly configured, the system will begin executing a preventive knowledge cycle.

## Verification

MoCKA is designed to be verifiable.

```bash
python verify_chain.py
python rebuild_state.py
```

These ensure integrity and reproducibility of the system state.

## Version

v1.0.0  
Initial complete release of the MoCKA civilization architecture

## Concept

MoCKA does not aim to generate answers.

It builds a structure where knowledge becomes trustworthy over time.

This is not just an AI system.

It is a civilization model.

---

## 日本語版

### 概要

MoCKAは従来のAIではない。

これは、知識がどのように生成され、検証され、安定していくかを再現する  
文明構造アーキテクチャである。

内部状態に依存せず、すべてを以下へ変換する。

- 構造化記録
- 追記型ログ
- 監査可能な判断
- 再現可能な結果

これにより、知識は「検証可能で信頼できるもの」となる。

### なぜ重要か

従来のAIは、結果は出せるが過程は説明できない。

MoCKAは違う。

すべての行動は：

- 記録され
- 検証され
- 監査され
- 学習される

その結果：

- 問題は発生前に抑止され
- 判断は追跡可能となり
- 改善は蓄積され続ける
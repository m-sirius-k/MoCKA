========================
Asset Management pj
========================

ENGLISH VERSION
------------------------

Purpose

This is an experimental Shadow-only project.
It strengthens the Shadow institution without impacting the MoCKA core system.

Core Concept

Shadow is not backup.
Shadow is bypass circulation.

If Primary integrity fails,
Shadow maintains degraded but continuous operation (75% mode).

Design Principles

- No interference with MoCKA core
- Deterministic switching
- Full observability (Signal + Ledger)
- Controlled repair proposal model (Repair_ID)
- Fail-safe defaults to Shadow

Visual Registry

Location:
shadow_pj/visual

Index:
shadow_pj/visual/VAR_INDEX.json

Beginner Reading Order

1. VAR-001 Shadow Bypass Architecture
2. VAR-003 75% Operational Mode
3. VAR-004 Integrity Trigger Flow
4. VAR-005 Repair Proposal Flow
5. VAR-002 Signal and Ledger Flow
6. VAR-006 Bypass Switching Architecture


==================================================
日本語版
==================================================

目的

本プロジェクトは Shadow 制度を高めるための実験領域である。
MoCKA本体への影響は一切与えない。

基本思想

Shadowはバックアップではない。
Shadowは代替循環である。

Primaryの整合性が損なわれた場合でも、
業務を止めず、75%縮退運転を維持する。

設計原則

・MoCKA本体非干渉
・決定的切替
・SignalとLedgerによる完全観測
・修復は提案制（Repair_ID）
・曖昧な場合はShadowへフェイルセーフ

可視資産

shadow_pj/visual 配下に
全構造図とフローを保存する。

読み方

1. VAR-001 で構造を理解
2. VAR-003 で守る範囲を理解
3. VAR-004 で切替条件を理解
4. VAR-005 で修復制度を理解
5. VAR-002 で記録構造を理解
6. VAR-006 で経路制御を理解

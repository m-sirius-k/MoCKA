# MoCKA Research Entry

--------------------------------
ENGLISH VERSION
--------------------------------

## Overview

MoCKA is a verifiable AI architecture designed to demonstrate structural transparency, reproducible reasoning, and ecosystem-level validation.

Unlike conventional repositories that only host source code, MoCKA exposes verification mechanisms that validate the structure of the system itself.

The goal is to make system architecture observable, reproducible, and evaluable by external engineers.

---

## Core Idea

MoCKA treats system design as a research subject.

The repository is structured so that architecture, documentation, and operational integrity are continuously verified through automated experiments.

Key principles:

Structure must be testable  
Documentation must be verifiable  
System integrity must be reproducible

---

## Ecosystem Structure

The MoCKA ecosystem consists of several repositories that represent different layers of the system architecture.

MoCKA  
Core orchestration and verification infrastructure.

MoCKA-KNOWLEDGE-GATE  
Institutional memory layer preserving reasoning traces and hypothesis evolution.

mocka-civilization  
Conceptual and architectural civilization layer.

mocka-transparency  
Public observability and structural audit layer.

mocka-external-brain  
External reasoning storage and knowledge continuity.

mocka-core-private  
Private operational layer.

---

## Verification System

MoCKA includes built-in verification mechanisms that continuously validate ecosystem integrity.

### Doctor

The Doctor system performs ecosystem integrity checks.

Examples:

repository presence verification  
broken link detection  
documentation scanning  
artifact generation

Artifacts are generated in:

MoCKA/artifacts/doctor_runs

Each artifact is hashed and logged to maintain integrity.

---

### Research Gate

The Research Gate is a structured experiment runner that validates system properties.

Experiment registry:

MoCKA/tools/research_experiments.json

Execution script:

MoCKA/tools/mocka_research_run.ps1

Example execution:

cd C:\Users\sirok\mocka-ecosystem  
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

The system executes multiple structural experiments validating ecosystem integrity.

---

## Canonical Research Map

Research topics and validation targets are documented in the canonical research map.

Canonical location

_canon/docs/RESEARCH_MAP.md

Mirror

MoCKA/canon/RESEARCH_MAP.md

This map acts as the reference registry of research experiments.

---

## Research Ledger

Research results may be recorded in an append-only ledger.

Location

MoCKA/research_ledger

This ledger records experiment results, artifact hashes, and chained verification records.

The ledger ensures that research activity can be externally audited.

---

## Reproducibility

External engineers can reproduce the verification process by executing the Research Gate runner.

cd C:\Users\sirok\mocka-ecosystem  
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

Successful execution confirms ecosystem structural integrity.

---

## Documentation

System design documents and architectural references are located in the following directories.

docs  
canon  
tools

These documents explain both conceptual design and operational verification procedures.

---

## Purpose

MoCKA explores a simple question.

Can an AI architecture make its own structural integrity observable and verifiable?

This repository is an experiment toward that goal.



--------------------------------
日本語版
--------------------------------

## 概要

MoCKA は、構造の透明性・推論の再現性・エコシステムレベルの検証を実現するために設計された「検証可能AIアーキテクチャ」です。

一般的なリポジトリはソースコードのみを公開しますが、MoCKA はシステム構造そのものを検証する仕組みを公開しています。

目的は、外部エンジニアがシステム構造を観測・再現・評価できる状態を作ることです。

---

## 基本思想

MoCKA はシステム設計そのものを研究対象として扱います。

このリポジトリは

構造  
文書  
運用状態

が自動実験によって継続的に検証されるよう設計されています。

基本原則

構造はテスト可能であること  
文書は検証可能であること  
システムは再現可能であること

---

## エコシステム構造

MoCKA エコシステムは複数のリポジトリで構成され、それぞれが異なる構造レイヤーを担います。

MoCKA  
コアオーケストレーションと検証インフラ

MoCKA-KNOWLEDGE-GATE  
推論履歴と仮説進化を保存する制度的記憶レイヤー

mocka-civilization  
文明構造と概念アーキテクチャ

mocka-transparency  
公開観測と構造監査レイヤー

mocka-external-brain  
外部推論保存レイヤー

mocka-core-private  
内部運用レイヤー

---

## 検証システム

MoCKA にはエコシステムの整合性を検証する仕組みが組み込まれています。

### Doctor

Doctor システムはエコシステムの整合性チェックを実行します。

例

リポジトリ存在確認  
リンク破損検出  
文書スキャン  
アーティファクト生成

生成されたアーティファクトは

MoCKA/artifacts/doctor_runs

に保存され、ハッシュで保護されます。

---

### Research Gate

Research Gate は構造検証実験を実行するランナーです。

実験定義

MoCKA/tools/research_experiments.json

実行スクリプト

MoCKA/tools/mocka_research_run.ps1

実行例

cd C:\Users\sirok\mocka-ecosystem  
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

複数の構造検証実験が実行されます。

---

## Canonical Research Map

研究テーマと検証対象は Research Map に記録されています。

正本

_canon/docs/RESEARCH_MAP.md

ミラー

MoCKA/canon/RESEARCH_MAP.md

これは研究実験の参照レジストリです。

---

## Research Ledger

研究結果は追記型の台帳に保存できます。

保存場所

MoCKA/research_ledger

実験結果・アーティファクトハッシュ・チェーン記録が保存されます。

これにより研究履歴の監査が可能になります。

---

## 再現性

外部エンジニアは Research Gate を実行することで検証プロセスを再現できます。

cd C:\Users\sirok\mocka-ecosystem  
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

正常終了すればエコシステムの整合性が確認されます。

---

## ドキュメント

設計文書とアーキテクチャ資料は以下に配置されています。

docs  
canon  
tools

これらの文書には概念設計と運用検証の両方が記録されています。

---

## 目的

MoCKA は次の問いを探求しています。

AIアーキテクチャは、自身の構造整合性を観測可能かつ検証可能な形で公開できるのか。

このリポジトリは、その問いに対する実験です。


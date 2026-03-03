# MoCKA v4
Trust & Identity Layer — 2-of-3 Multi-Signature Responsibility Model

---

## Overview

MoCKA v4 introduces a threshold-based responsibility layer (2-of-3 multi-signature model) designed for verifiable AI governance and decision accountability.

This release demonstrates:

- Threshold authorization (2-of-3)
- Append-only key registry with revocation enforcement
- Canonical JSON determinism
- Independent verification scripts
- Explicit PASS / FAIL policy tests

Release artifact:
verify_pack_v4_sample.zip

SHA256:
d5995d34e3cb651dbd00ba9d5acae52aaafbc67cdf27ba502de7893830221fea

Verify (Windows):
certutil -hashfile verify_pack_v4_sample.zip SHA256

Run:
python verify_all_v4.py

Expected:
1 PASS
4 FAIL (by design)

---

## Why It Matters

MoCKA v4 prevents:

- Single-actor authority abuse
- Silent key substitution
- Undetected revocation bypass
- Canonical tampering

It converts responsibility from policy text into cryptographic structure.

---

## 日本語概要

MoCKA v4 は、
2-of-3 マルチシグ方式による責任分散レイヤーを実装した
検証可能なAIガバナンス構造です。

主な特徴：

- 閾値署名（2-of-3）
- 追記専用キー台帳と失効管理
- Canonical JSON による決定論的整合性
- 独立検証スクリプト
- PASS / FAIL を明示した制度テスト

これは単なる署名実装ではなく、
責任を暗号構造へ変換する設計です。

---

## Verification

Download the release:
https://github.com/nsjpkimura-del/MoCKA/releases/tag/v4-sample-1.0

Compute hash and run verification script.

---

## Status

v4-sample-1.0 — Public Release  
Reproducible  
Threshold Verified  
Revocation Enforced


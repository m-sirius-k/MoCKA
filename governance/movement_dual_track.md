MoCKA Movement Dual-Track Governance (Primary / Shadow)
1. Scope

This document defines the Dual-Track governance model of MoCKA Movement.

It governs two structurally distinct tracks:

Movement Primary (public, frozen, externally verifiable)

Movement Shadow (private, resilience, diagnostic-only)

This document is normative.

2. Definitions

Primary

The only publicly published Movement track.
The external reference standard.
The sole public source of truth.

Shadow

A private resilience track activated when Primary integrity is compromised.
Shadow exists only to preserve verifiability and investigative continuity.
Shadow is diagnostic-only.

Caliber

A private experimentation domain (Infield/Outfield, orchestration, integrations).
Caliber may evolve rapidly but must not weaken Primary governance.

3. Core Principles

P1. One Public Truth
Primary is the sole public source of truth.

P2. No Invisible State
Movement must not rely on hidden state or unverifiable claims.

P3. No Exceptions
Verification, revocation, and multi-signature requirements must never be bypassed.

P4. Shadow Is Not a Backdoor
Shadow must never function as an alternative authority or shortcut.

4. Primary Track Requirements

4.1 Public Verifiability
Primary artifacts must be externally verifiable using only published materials.

4.2 Multi-Signature Enforcement
The 2-of-3 responsibility layer is mandatory.

4.3 Append-Only Registry
Primary registries are append-only.
History rewriting is forbidden.

4.4 Revocation Enforcement
Revoked artifacts must fail verification by design.

4.5 Determinism
Canonical JSON determinism is mandatory.

4.6 Change Cadence
Primary must not be frequently modified.
Release cadence policy is semiannual.

Emergency changes are allowed only to fix verifier defects or critical security flaws and must follow full publication discipline.

5. Shadow Track Requirements

5.1 Purpose Limitation
Shadow is permitted only for:

Root-cause investigation

Impact boundary identification

Minimal evidence recovery

Diagnostic reporting

5.2 Diagnostic-Only Constraint
Shadow must be read-only with respect to Primary artifacts.

Shadow must not:

Modify Primary history

Relax revocation

Relax multi-signature

Create alternative truth

Generate substitute approvals

5.3 No Pass-Through
Shadow must not be used to make verification succeed.

5.4 Deactivation
Shadow is an emergency instrument.
After Primary integrity is restored, Shadow operations should cease.

6. Caliber Relationship

Caliber may evolve rapidly.
Caliber must not weaken Primary or Shadow principles.

Promotion path:
Caliber → abstraction → hardening → Primary release cycle.

Direct injection into Primary is forbidden.

7. Shadow-to-Primary Flow Control

Shadow findings do not automatically become Primary truth.

Shadow outputs may include:

Diagnostic reports

Minimal evidence packages

Reproducible reproduction steps

These may inform future Primary releases but are not authoritative.

8. Compliance

Any artifact claiming Movement compliance must align with this document.

Violations constitute governance breaches.

9. Versioning

This document follows the same governance discipline as Primary.

MoCKA Movement 二重トラック統治文書（Primary / Shadow）
1. 適用範囲

本書は MoCKA Movement における二重トラック統治モデルを定義する。

対象は以下の二層である。

Movement Primary（公開・凍結・外部検証可能）

Movement Shadow（非公開・レジリエンス・診断専用）

本書は規範文書である。

2. 用語定義

Primary

唯一の公開 Movement トラック。
外部検証の基準。
公開された真実の唯一の源。

Shadow

Primary の整合性が損なわれた場合に起動される非公開レジリエンス層。
検証可能性と調査継続性を維持するための補助層。
診断専用である。

Caliber

私的実験領域（Infield / Outfield / 自動化 / 統合）。
高速進化は許容されるが、Primary の統治を弱体化させてはならない。

3. 基本原則

原則1　公開真実は一つ
Primary のみが公開真実である。

原則2　不可視状態を許容しない
検証不能な内部状態に依存してはならない。

原則3　例外を制度化しない
検証、失効、マルチ署名は回避されてはならない。

原則4　Shadow は裏口ではない
Shadow は代替権威にならない。

4. Primary 要件

4.1 外部検証可能性
公開物のみで検証可能であること。

4.2 2-of-3 マルチ署名強制
責任層を必須とする。

4.3 追記専用レジストリ
履歴改竄は禁止。

4.4 失効強制
失効した成果物は必ず検証失敗となる。

4.5 決定性
Canonical JSON 決定性を維持する。

4.6 改定周期
頻繁な変更を行わない。
原則として半年単位の改定。

緊急修正は検証器欠陥または重大セキュリティ問題に限定する。

5. Shadow 要件

5.1 目的限定

原因特定

影響範囲特定

最小証跡回収

診断報告

5.2 診断専用制約
Shadow は Primary に対して読み取り専用である。

以下は禁止する。

Primary 履歴変更

失効緩和

署名要件緩和

代替真実生成

代替承認生成

5.3 通過目的禁止
検証を通すために使用してはならない。

5.4 復旧後停止
Primary 復旧後は Shadow を停止する。

6. Caliber との関係

Caliber は高速進化可能である。
ただし Primary および Shadow の原則を弱体化させてはならない。

昇格経路は
Caliber → 抽象化 → 強化 → Primary 改定サイクル

直接注入は禁止。

7. Shadow 逆流制御

Shadow の発見は自動的に Primary 真実にならない。

Shadow の出力は以下に限定される。

診断報告

証跡パッケージ

再現手順

これらは将来の改定判断材料であり、真実そのものではない。

8. 遵守

Movement 準拠を名乗る成果物は本書と整合していなければならない。

違反は統治違反とみなす。

9. 版管理

本書の改定は Primary と同等の統治規律に従う。
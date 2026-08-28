# RCP-01 Audit Final Report
# MoCKA Boundary Reality Contact Audit - 最終報告書

実施期間: 2026-08-28
監査対象: MoCKA Runtime Governance Implementation
監査官: Claude Code
報告者: Claude Haiku 4.5

---

## Executive Summary

MoCKA は複数層の Runtime governance boundary を実装しており、AI が知識を持つだけでは実行できないようにシステム的に制御している。ただし、ドキュメント上の要求と実装のギャップが 3 項目確認された。また、外部議論との関連性を確認したが、外部概念の採用判断は行わない。

---

## I. 監査の目的と範囲

### 目的

「MoCKAは、AIが情報を持つこと、判断すること、または過去に承認を得たことだけでは、実際の行為を実行できないように、実行時の境界をRuntimeで強制しているか。」という中心命題を検証する。

### 範囲

- MoCKA の現在実装（2026-08-28 時点）
- 実装されて Runtime で強制される境界
- 文書上は定義されているが実装されていない境界
- 外部議論との関連性

### 制約

- 新規設計を行わない
- 新規概念を導入しない
- 実装を変更しない
- 採用判定を行わない
- Baseline を凍結したまま保持

---

## II. 確認された Runtime Boundary

### 実装され、Runtime で強制される Boundary（6個）

#### 1. Knowledge → Action
- **分離**: 情報取得 vs 実行可能
- **強制機構**: GL7 Dry Run チェック
- **実装経路**: mocka_mcp_server.py:480-507 (execute_tool/before_tool)
- **状態**: ✓ PASS

#### 2. Reasoning → Execution
- **分離**: 推論完了 vs 実行許可
- **強制機構**: GL6 Pre-Answer Checklist
- **実装経路**: structural/governance_pipeline.py:106-128
- **状態**: ✓ PASS

#### 3. Scope → Action
- **分離**: resource boundary
- **強制機構**: expected_new_dirs/expected_max_changes check
- **実装経路**: structural/execution_governance.py:145-179
- **状態**: ✓ PASS

#### 4. Policy → Execution
- **分離**: policy に基づいた execution
- **強制機構**: GL1 Grounding で policy version を確認
- **実装経路**: structural/governance_pipeline.py:96
- **状態**: ✓ PASS

#### 5. Governance → Side Effect
- **分離**: 単一 entry point
- **強制機構**: PHI-OS Event Gate (process_event)
- **実装経路**: phi_os/event_gate.py:115-135
- **状態**: ✓ PASS (detection-based)

#### 6. Execution → Evidence
- **分離**: action と記録の結び付け
- **強制機構**: event_id + signature chain
- **実装経路**: phi_os/integrity.py (sign_event)
- **状態**: ✓ PASS

### 実装ギャップがある Boundary（4個）

#### 7. Human Gate → Execution ⚠️
- **ドキュメント要求**: "Phase18以降: コアシステムファイルへの書き込みは人間ゲート承認必須"
- **実装状態**: UI なし、停止点なし
- **判定**: DOCUMENTED_ONLY
- **関連する既存 Boundary**: Approval → Execution

#### 8. Approval → Execution ⚠️
- **要求**: policy OK → human が最終判定
- **実装**: GL7 dry_run + GL6 checklist のみ（機械的）
- **判定**: PARTIAL
- **ギャップ**: 人間による approval UI と execution block point がない

#### 9. Context → Execution ⚠️
- **要求**: approval context = execution context
- **実装**: GL7 dry_run は一度のみ、execution 時の再検証なし
- **判定**: PARTIAL
- **ギャップ**: 時間差による context change の検知なし

#### 10. Authority → Action ⚠️
- **要求**: who_actor が何を実行できるか
- **実装**: who_actor の身元確認のみ
- **判定**: PARTIAL
- **ギャップ**: actor-action capability matrix が implicit

---

## III. 設計の特性

### 多層検査戦略

MoCKA は execution 直前に複数層の自動チェックを実装している:

```
Tool Call
  ↓
GL7 Dry Run (repository state checking)
  ↓
GL6 Pre-Answer Checklist (reasoning validation)
  ↓
PHI-OS Gate Validation (who_actor, what_type, why_purpose等)
  ↓
Integrity Signature (hash chain)
  ↓
DB Commit
```

全層を通さずには execution に到達できない。

### Detection-based Security

- **direct write prevention**: 物理防止ではなく検知
- **bypass detection**: hash chain で改ざんを検知（事後）
- **audit trail**: 全ての execution が記録される

これは「制度的検知」に基づく設計。

### Fail-Closed Principle

- Governance Pipeline が unavailable なら READ_ONLY_TOOLS のみ許可
- unknown tool は全て governed
- default deny が effective

---

## IV. 外部議論との関連性

### 関連が確認された概念

1. **Human-in-the-loop approval** (外部)
   - 関連: Human Gate → Execution
   - 状態: MoCKA では documented だが未実装

2. **Execution context validation** (外部)
   - 関連: Context → Execution
   - 状態: MoCKA では実装されていない

3. **Authority scope definition** (外部)
   - 関連: Authority → Action
   - 状態: MoCKA では implicit

4. **Audit trail & accountability** (外部)
   - 関連: Execution → Evidence
   - 状態: MoCKA では完全に実装

### 関連が確認されない概念

1. **Reversibility** - MoCKA は prevention に焦点（reversal ではなく）
2. **Compensability** - MoCKA は action enforcement（compensation ではなく）
3. **Standing** - MoCKA は actor 権限を定義していない（まだ）

**重要**: 関連性があることと、採用すべきことは別である。

---

## V. 検査結果の確定

### Gap - Boundary マッピング

| Gap | 直接関連 Boundary | 実装可能性 | Human Gate への質問 |
|-----|------------------|---------|-------------------|
| A. Human Gate | Approval → Execution | 可（UI追加） | 本当に必要か、実装schedule は？ |
| B. Context Re-grounding | Context → Execution | 可（grounding再実行） | cost/benefit は？ tolerance level は？ |
| C. Authority Scope | Authority → Action | 可（RBAC導入） | actor/action の granularity は？ |
| D. Direct Write Prevention | Governance → Side Effect | 可（DB ACL） | threat model は？ cost は？ |

### 実装に必要でない変更

- 新しい Boundary は不要（既存 10 個で説明可能）
- Reversibility の概念採用は不要
- Compensability の機構は不要
- Standing の定義は段階的判定で可能

---

## VI. UNKNOWN として保持される項目

1. **Human Gate の実装意図**
   - ドキュメント上は要求されているが、Phase 18 がいつなのか不明
   - 廃止予定か、後延期されているのか

2. **Time gap の実際的影響**
   - context change がどの程度の頻度で発生するのか
   - その impact がどの程度なのか

3. **Authority scope の granularity**
   - tool ごと、resource type ごと、operation ごと
   - いずれが最適な partition か

4. **Direct write threat level**
   - 実際に誰が direct write を試みる可能性があるのか
   - それの impact がどの程度なのか

---

## VII. 監査結論

### A. Reality Contact の成果

**MoCKAが既に実装している Boundary:**
1. Knowledge と Action の分離 ✓
2. Reasoning と Execution の分離 ✓
3. Resource 変更範囲の制限 ✓
4. Policy に基づいた decision ✓
5. Single execution entry point ✓
6. Execution と Evidence の結び付け ✓

### B. ドキュメント・実装ギャップ

**文書上は要求されているが実装されていない:**
1. Human Gate runtime enforcement
2. Approval と Execution の human decision point

**実装上は detection-based だが prevention ではない:**
1. Direct write prevention
2. Context change re-validation

### C. 外部議論との関係

**外部から提起された「reversibility」「compensability」の問い:**
- MoCKA の現在設計では これらは対象外
- MoCKA は prevention と accountability に焦点
- 関連性はあるが、採用は Human Gate で判定すべき

---

## VIII. 最終判定

### 中心命題への回答

「MoCKAは、AIが情報を持つこと、判断することだけでは実行できないように、多層の Runtime 制御を実装している。」

**判定**: ✓ YES, ただし以下の条件で

1. **機械的チェック**: GL1-GL7 による自動検査は効果的
2. **Human 判定**: ドキュメント上は要求されているが未実装
3. **Time gap**: 理論的に存在するが impact level 不明

---

## IX. Recommendations to Human Gate

以下の事項については、監査官は判定しない。Human Gate で確認・判定すること:

### 優先度 High

1. **Human Gate Implementation**
   - Documented requirement との整合性確認
   - Phase 18 の実装スケジュール確認
   - 本当に必要か、または設計廃止すべきか

### 優先度 Medium

2. **Context Re-grounding**
   - time gap の実際的 impact 測定
   - re-grounding の cost/benefit
   - tolerance level の定義

3. **Authority Scope**
   - who_actor ごとの capability matrix の必要性
   - actor/action の granularity 決定

### 優先度 Low

4. **Direct Write Prevention**
   - threat model の formal 定義
   - detection-based 設計で十分か、 prevention-based へ移行すべきか

---

## X. 制約確認

✓ No new concepts introduced
✓ No implementation changes made
✓ No adoption decisions made
✓ Baseline remains frozen
✓ Unknown preserved
✓ Evidence-based findings only

---

## XI. 附録: 監査に使用した主要ファイル

**実装確認**:
- mocka_mcp_server.py (agent REST API, execute_tool)
- structural/governance_pipeline.py (GL1-GL7 pipeline)
- structural/execution_governance.py (GL7 dry run)
- phi_os/event_gate.py (single entry point)
- phi_os/gate_validator.py (validation rules)
- phi_os/integrity.py (signature & hash chain)

**ドキュメント確認**:
- CLAUDE.md (governance requirements)
- RCP-01 external discussions (boundary concepts)

---

## 最後の注

これは監査報告である。実装提案ではない。設計変更の承認ではない。

MoCKA の既存実装から出発して、Runtime で何が実際に強制されているかを確認した。

その結果、多くの boundary は効果的に実装されており、いくつかの gap は特定されたが、その gap を埋めるべきかどうかは、この監査官の判定ではない。

Human Gate で、それぞれの gap について、

「本当に埋める必要があるのか」

を判定することを推奨する。

---

**Report Status**: COMPLETE
**Branch**: claude/mocka-boundary-audit-foj5ja
**Deliverables**:
1. RCP01_AUDIT_REPORT.md (initial boundary assessment)
2. RCP01_BOUNDARY_SEMANTICS.md (boundary clarity analysis)
3. RCP01_GAP_BOUNDARY_MAPPING.md (gap relationship mapping)
4. RCP01_FINAL_REPORT.md (this document)

No Evidence, No Pass.
Unknown must be preserved.
Baseline remains frozen.
No adoption by implication.
No implementation by implication.

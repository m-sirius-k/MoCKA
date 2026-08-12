# Human Gate 最終判断パッケージ

**作成日**: 2026-08-12
**調査者**: Claude (くろこ)
**ステータス**: Read-Only 調査完了 → Human Gate Hold
**実行モード**: 実装禁止・調査禁止・以下の7項目のみ Human Gate判断材料として提出

---

## 現在の制度状態（維持）

```
TODO_451 Phase 3: BLOCKED / HUMAN GATE HOLD
  ステータス: NOT STARTED / WAITING（先行タスク TIC Phase 2設計範囲確定）
  実装開始: 禁止
  DB変更: 禁止
  Event Store変更: 禁止
  Decision Ledger変更: 禁止
  TODO状態変更: 禁止
  seal/freeze: 禁止
  
責務境界: 部分確定（未確定事項あり）
Phase 3 Unblock判定: 保留（以下7項目の Human Gate決定待ち）
```

---

## 責務マトリックス基準（新規分類）

### 4軸定義

| 軸 | 定義 |
|----|------|
| **Owner** | 責務を制度的に所有する者・最終責任を負う者 |
| **Verifier** | 独立して検証する者・検証結果を報告する者 |
| **Veto Authority** | 不成立時に拒否できる者・動作を停止する権限を持つ者 |
| **Evidence Recorder** | 結果を証拠として記録する者・Audit trail に記載する者 |

---

## Human Gate へ提示する7項目の判断事項

---

### 【判断1】MCP 再検証の実行義務性

**問題背景**: DC_001「optional」vs DC_002「各層必須」

**分解質問**:

#### 1-A. Execution Obligation（実行必須性）
```
質問: MCP による actor_id 再検証を実装することは
     Phase 3 実装スコープに「含める」のか「含めない」のか？

現状: DC_001は「optional」と記載
     DC_002は「各層で必須」と記載
     
Human Gate判断: □ 含める（必須実装）
             □ 含めない（オプション）
             
理由: [ Human Gate記述 ]
```

#### 1-B. Veto Authority（MCP の拒否権）
```
質問: MCP での actor_id verification に失敗した場合、
     MCP自身が「Event を拒否する」権限を持つべきか？

現状: DC_002は「independently verify」と記載するが、
     拒否権の有無は明記されていない
     
Human Gate判断: □ MCP が拒否権を持つ（Defense in Depth完全）
             □ MCP は検証のみで拒否権なし（Gateway のみ拒否）
             □ MCP 拒否は選択的（設定可能）
             
理由: [ Human Gate記述 ]
```

#### 1-C. Responsibility Ownership（MCP の責務所有）
```
質問: Authorization 責務そのものについて、
     Gateway だけが「Owner」なのか、
     MCP も shared owner なのか？

現状: DC_001では「Gateway (一次防御)」「MCP (再検証層)」と記載
     責務所有の主・副が不明確
     
Human Gate判断: □ Gateway 単独 Owner（MCP は助言者）
             □ Gateway 主 Owner + MCP 副 Owner
             □ Gateway と MCP が共同 Owner（equal）
             
理由: [ Human Gate記述 ]
```

---

### 【判断2】Event Store の Integrity 責務の分解

**問題背景**: DC_001「最終層」vs 実装の曖昧性

#### 2-A. Integrity 検証責務
```
質問: Event Store が「Integrity を検証する」とは、
     具体的に何を検証するのか？

候補:
  - actor_id の正当性確認
  - Event record の改ざん検知
  - Audit log の完全性確認
  - Authorization scope の照合
  
現状: DC_001では「integrity validation」と総称されている
     
Human Gate判断: [ Event Store が検証する具体的項目リスト ]

理由: [ Human Gate記述 ]
```

#### 2-B. Event 最終拒否権
```
質問: Event Store での Integrity check に失敗した場合、
     Event Store は query を「拒否」できるか？

現状: DC_001では「最終層」と記載されるが、
     実際の拒否権がどこまで及ぶか不明確
     
Human Gate判断: □ Event Store が query を拒否可能（veto権あり）
             □ Event Store は log のみで拒否権なし
             □ Event Store 拒否は選択的（設定可能）
             
理由: [ Human Gate記述 ]
```

#### 2-C. Authorization 判断責務
```
質問: Event Store の Integrity check は、
     Authorization judgment そのものなのか、
     それとも Authorization の「確認」に過ぎないのか？

現状: Authorization owner が Gateway と記載されているが、
     Event Store での actor_id scope check は Authorization
     
Human Gate判断: □ Event Store は Authorization owner（Gateway と shared）
             □ Event Store は Authorization 検証のみ（Owner ではない）
             
理由: [ Human Gate記述 ]
```

#### 2-D. Evidence Recorder 責務
```
質問: Event Store が「audit log に actor_id を記録する」
     というのは、
     「検証結果を記録する」のか「すべてのアクセスを記録」するのか？

現状: DC_002では「audit log に actor_id を記録」と記載
     何を記録するかは曖昧
     
Human Gate判断: □ すべての query attempt を記録（許可・拒否含む）
             □ 拒否された query のみ記録
             □ 許可された query のみ記録
             
理由: [ Human Gate記述 ]
```

---

### 【判断3】Gateway の Authorization Owner としての範囲

**問題背景**: Gateway が「一次防御」であることは確定したが、スコープ不明

```
質問: Gateway が Authorization owner として保証する範囲は何か？
     また、保証しない範囲は何か？

現在のGateway責務（DC_001より）:
  - HTTP認証（X-MoCKA-Key検証）
  - actor_id establish
  - enforce_observe() 実装
  - 拒否権（unauthorized access ブロック）
  
以下について Human Gate決定:

A. 保証する範囲:
  □ X-MoCKA-Key holder が実在する actor であることを保証
  □ X-MoCKA-Key が authorized actor に属することを保証
  □ observe権限が真正であることを保証
  □ 上記3点のうち、以下のみ: [ 番号指定 ]
  
B. 保証しない範囲:
  □ MCP 内部での再検証
  □ Event Store での最終確認
  □ actor_id の downstream misuse detection
  □ その他: [ 指定 ]

理由: [ Human Gate記述 ]
```

---

### 【判断4】User / API key holder の責務

**問題背景**: User 責務が未定義

```
質問: X-MoCKA-Key を保有し使用する User（クライアント）の
     責務範囲は何か？
     
現状: User責務が明記されていない

Human Gate判断:

A. User が保証する事項:
  □ API key の秘密保持（Transport Security）
  □ request の semantic correctness
  □ Authorization権限の自己確認
  □ appeal・dispute 権限
  □ その他: [ 項目追加 ]

B. User が保証しない事項:
  □ Gateway での認証正確性
  □ Event Store での integrity
  □ MoCKA内部の Authorization実装
  □ その他: [ 項目追加 ]

C. User support の範囲:
  □ API key reset・revoke
  □ Authorization appeal（拒否された access の再検討）
  □ Audit log 閲覧権
  □ 上記のうち: [ 項目指定 ]

理由: [ Human Gate記述 ]
```

---

### 【判断5】Human Gate の最終権限構造

**問題背景**: Human Gate が「最終判断」することは確定したが、override 権限が不明

```
質問: Human Gate（Human Authority）が下した decision に対し、
     上位の override authority を設けるのか設けないのか？

現状: Authorization → Visibility → Projection → Human Gate decision
     という層構造は確定。
     ただし、Human Gate decision 後の hierarchy が不明確。

Human Gate判断:

A. Human Gate decision の最終性:
  □ Human Gate decision は最終的（override authority なし）
  □ Human Gate decision は appeal可能（上位 review あり）
  □ 特定の条件下でのみ override 可能: [ 条件指定 ]

B. Appeal・Override 権限の所有:
  □ User が Human Gate decision に appeal できるか
  □ きむら博士が override できるか
  □ 別の制度層が review するか
  □ その他: [ 権限構造記述 ]

C. Decision Ledger の immutability:
  □ override 時に新規 decision を追加（overridden decision は残す）
  □ override 時に prior decision を削除
  □ override は禁止（一度の decision は覆さない）

理由: [ Human Gate記述 ]
```

---

### 【判断6】H2-3 の5層モデルと3層モデルの正式対応

**問題背景**: H2-3 定義が「進行中」で、5層と3層の対応が未精査

```
質問: H2-3 「5層構造案」（進行中）と
     Phase 4 決定の「3層モデル」（確定）の
     正式な対応関係は何か？

現状: 
  - Control/Sovereign/Data 3層は Phase 4実装モデルとして確定
  - 5層構造案は精査中（未確定）
  - 対応関係が明確でない

Human Gate判断:

A. 正式対応（もしあれば）:
  5層構造案 → 3層モデル対応マッピング
  
  Layer 1: __________ → Control / Sovereign / Data [ 選択 ]
  Layer 2: __________ → Control / Sovereign / Data [ 選択 ]
  Layer 3: __________ → Control / Sovereign / Data [ 選択 ]
  Layer 4: __________ → Control / Sovereign / Data [ 選択 ]
  Layer 5: __________ → Control / Sovereign / Data [ 選択 ]

B. 対応がない場合:
  □ 5層と3層は異なる分類体系
  □ Phase 3は3層ベースで実装
  □ 5層との統合は Phase 5以降

理由: [ Human Gate記述 ]
```

---

### 【判断7】TODO_451 Phase 3 Unblock 条件の制度的確定

**問題背景**: Phase 3開始の条件が不明確

```
質問: TODO_451 Phase 3 をUnblock する条件は何か？
     
現状: TIC Phase 2設計範囲確定（2026-06-15）は完了しているが、
      H2-3 責務確定に未確定事項がある。
      
以下を Human Gate で判断すること:

A. 必須先行条件（現在の状態):
  ✓ TIC Phase 2設計範囲確定（完了）
  ? H2-3責務確定（部分確定）
  ? 上記【判断1～6】の Human Gate 決定（保留中）

B. Unblock の threshold（何が確定したら開始するのか）:
  
  □ 上記【判断1～6】がすべて決定されれば自動 Unblock
  □ 上記のうち、以下のみ決定されれば Unblock: [ 判断番号指定 ]
  □ 別途条件あり: [ 条件記述 ]

C. 注記（DC_006との分離）:
  DC_20260812_006（ORCHESTRA Terminal Event再定義）は
  TODO_451 Phase 3 Unblock条件から明確に分離される。
  ORCHESTRA修正のみを理由として Phase 3開始してはならない。

理由: [ Human Gate記述 ]
```

---

## 参考: DC_20260812 Decisions の状態

| ID | Title | Phase 3 Relevance | Status |
|----|-------|-------------------|--------|
| DC_001 | H2-3 Event-level Enforcement Owner | **RELEVANT** | 矛盾あり（optional vs 必須） |
| DC_002 | Trusted actor_id Boundary | **RELEVANT** | MCP拒否権不明 |
| DC_003 | H2-3 Event-level Enforcement Owner (重複) | **RELEVANT** | DC_001と重複 |
| DC_004 | Trusted actor_id Boundary (重複) | **RELEVANT** | DC_002と重複 |
| DC_005 | Authorization/Visibility/Projection 責任分離 | **RELEVANT** | 完全確定（依存性明確） |
| DC_006 | ORCHESTRA Terminal Event Redefinition | **NOT RELEVANT** | Phase 3と無関係 |

---

## 調査の制約

- **実行モード**: Read-Only（ファイル読取・Decision照会のみ）
- **許容スコープ**: 責務分類・整合性検証
- **禁止スコープ**: 実装提案・code design・state変更
- **次ステップ**: Human Gate判断（AI側での実装開始禁止）

---

## 成果物の位置付け

このドキュメントは、以下の目的で Human Gate へ提出される：

1. **責務境界の未確定事項を明示化** - 不確定なまま Phase 3実装を開始しないため
2. **判断事項を明確に分解** - 意思決定の粒度を統一するため
3. **Decision Ledger への記録準備** - Human Gate判断後、新規Decisionを ledgerに記載するため

**状態**: Human Gate Hold（制度的完全性確定まで実装禁止）

---

**調査者署名**: Claude (くろこ)
**調査完了日**: 2026-08-12
**次工程**: Human Gate 最終判断

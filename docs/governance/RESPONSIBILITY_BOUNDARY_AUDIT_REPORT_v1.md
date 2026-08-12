# TODO_451 Phase 2 責務境界確定調査 - 最終監査報告

**作成日**: 2026-08-12
**調査者**: Claude (くろこ)
**実行モード**: Read-Only（コード変更禁止・Decision Ledger書込禁止）
**監査原則**: R01 - 制度責務確定優先（実装可能性ではなく責務・権限・保証範囲が確定したことをPhase 3 Unblockの根拠とする）

---

## 1. TODO_451 Phase 2 停止条件 - 正確な説明

### 現在ステータス
- **ステータス値**: 未着手
- **ステータス分類**: 「保留」（待機中 / 2026-06-15以降に再開予定）
- **参照イベント**: E20260601_061（TIC Phase 2設計範囲確定）

### 停止条件の本質
```
技術的停止 ≠ 制度的停止

停止理由: TIC Phase 2（連鎖障害解析）の設計範囲確定が
         2026-06-15に完了するまで、実装着手保留
         
特性: 先行タスク依存型の保留（技術スコープ未確定）
```

### 設計範囲確定内容（E20260601_061より）
- Technical Dependency: Stripe → Webhook → Worker → License → Orchestra
- Business Dependency: 同上
- 範囲確定: 2026-06-15完了（Agent確認）

---

## 2. H2-3 Event-level Enforcement - 責務所有者確定

### H2-3の定義（進行中）
```
タイトル: HAB/PlanningCaliber/Caliber/Runtime 5層構造案の精査
ステータス: 進行中（E20260622_017030043d9b2にて3層モデル確定）
参考: Control/Sovereign/Data 3層が Phase 4実装モデル
```

### Event-level Enforcement の責務分解

#### 2-1. Authorization（アクセス制御） - Gateway主導

| 項目 | 実装 | 責務所有 | 拒否権 |
|------|------|---------|--------|
| HTTP認証 | X-MoCKA-Key検証 | Gateway | YES |
| actor_id確立 | header extract | Gateway | YES |
| 権限判定 | enforce_observe() | Gateway | YES |
| 実装要件 | Phase 3実装必須 | Gateway | 主責務 |

**Gateway責務の定義**:
> Gateway は外部クライアントからの untrusted request を受け入れる最初の信頼境界として機能する。X-MoCKA-Key から actor_id を確定し、permissions.check_observe() を実行してアクセス拒否を判定する。この段階での拒否判定が「最初の拒否権」であり、Gateway を通らない request は MoCKA システム内部に進入しない。

**Defense in Depth における Gateway の位置**:
- 層別責務: 第1層（最初の防御）
- 責務の本質: 信頼境界確立
- 再検証可能性: 下流での再検証を前提とする（Gateway単独では不十分）

---

#### 2-2. actor_id Verification（信頼性確認） - 多層検証

##### DC_001 vs DC_002 の矛盾検出

| Document | MCP Secondary Check | 各層独立検証 |
|----------|-------------------|-----------|
| DC_001 | optional | 記載なし |
| DC_002 | - | 各層で必須 |
| **整合性** | **矛盾あり** | **整合性不明** |

**問題の詳細**:

DC_001より:
```
- MCP (再検証層): tool caller verification + secondary permission check (optional)
```

DC_002より:
```
Decision: actor_id must be independently verified at each layer.
...
Each layer performs independent verification - 
no layer trusts previous layer's actor_id extraction.
```

**矛盾の構造**:
- DC_001が「optional」と記載 → MCP実装は選択肢か
- DC_002が「各層必須」と記載 → MCP実装は必須か
- **制度的に一義的ではない状態**

**この矛盾の影響**:
```
IF MCP verification is optional:
  - Defense in Depth原則が部分的に実装（不完全）
  - Gateway単独障害で全体が動作する状態
  - Phase 5-2 Unified Event Entry との整合性が不明確

IF MCP verification is mandatory:
  - DC_001の記述が不正確（"optional"は削除すべき）
  - MCP実装スコープが拡大（Phase 3にて要確認）
```

**Human Gateへの最終判断事項**: 
→ MCP での actor_id verification が「必須」か「オプション」かを制度上明確にすること（責務確定に必須）

---

#### 2-3. Visibility（フィールド可視性） - Gateway実装完了？

| 項目 | 実装 | 責務所有 | 検証可能性 |
|------|------|---------|-----------|
| Sensitive field filtering | φ-OS event_gate | Gateway | YES |
| actor-scoped access | Event Store層 | Store | YES |
| 実装状態 | Single Entry Point稼働中 | φ-OS | 確認済み |

**Visibility責務の定義**:
> Authorization（「誰が」）が確定した後、Visibility層は「どのフィールドが見える」を制御する。Sensitive metadata の自動フィルタリング、actor-scoped access の強制を行う。

**重要**: DC_005より
```
Authorization determines WHO can access events (access control gate).
Visibility determines WHICH FIELDS are exposed to the authorized actor 
(field filtering and sensitive metadata sanitization).
Projection determines PRESENTATION FORMAT...
```

これは制度的な**依存性**を示す:
- Authorization なし → Visibility 判定不可（無意味）
- Visibility なし → Projection は機能しない（フィルタリング前のデータを返す）

---

#### 2-4. Event Integrity Validation - 最終層

| 項目 | 実装 | 責務所有 | 最終拒否権 |
|------|------|---------|----------|
| Audit logging | Event Store | Store | YES（記録層） |
| Integrity check | IC_STATUS層 | IC/Anomaly | YES（検証層） |
| Scope confirm | Event Store query | Store | 不明確* |

*Scope confirm の拒否権が実装されているか未確認（Read-Only制約で検証不可）

---

### 2-5. Decision admissibility（意思決定正当性） - Human Gate層

| 項目 | 実装 | 責務所有 |
|------|------|---------|
| Decision Policy validation | human_gate.py | Human Gate |
| Decision Ledger write | mocka_decision_write | Human Gate |
| Ratification authority | きむら博士 | Human Authority |

**重要な分離**:
```
Authorization (WHOが見られるか) = MoCKA Gate層
↓
Decision admissibility (その判断が正当か) = Human Gate層
```

Human Gate は Gateway/MCP/Event Store の意思決定を「事後検証」する最終層であり、これらの「正当性」を判定する権限を持つ。

---

## 3. Gateway / User / Hybrid 責務分類

### 3-1. Gateway責務の境界

```
実装位置: gateway/auth.py (推定)
主責務:
  - HTTP request の受け入れ・終点化
  - X-MoCKA-Key からの actor_id establish
  - Authorization first gate (enforce_observe()実行)
  - Unauthorized requestの最初の拒否
  
保証すること:
  - actor_id が確実に確定されている
  - Authorization判定が実行された
  - Unauthorized requestは下流に進入しない
  
保証しないこと:
  - MCP内部の再検証（Gateway責務外）
  - Event Store層の整合性（別層責務）
  - Human Authority の判断（人間層）
  - Future: 外部AI接続時の権限分離（設計待ち）

信頼境界の位置: HTTP request の最初の受け入れ点
```

### 3-2. User責務の位置付け

```
ユーザーが行うこと:
  - X-MoCKA-Key を保管・使用
  - request を Gateway に送信
  
ユーザーが保証する範囲:
  - API key の秘密保持（Transport Security）
  - request の正当性（semantic correctness）
  
ユーザーが保証しないこと:
  - システム内部の Authorization
  - Event Integrity の確認（MoCKA側責務）
  - Decision Ledger の正当性（Human Gate側責務）

信頼境界の位置: X-MoCKA-Key の所有・使用権限
```

### 3-3. Hybrid（多層防御）の構造

```
Hybrid Defense in Depth:
  - Gateway: 第1防御 (HTTP level Authorization)
  - MCP: 第2防御 (MCP tool level actor_id verification - optional?)
  - Event Store: 第3防御 (Event scope integrity check)
  - Human Gate: 第4防御 (Decision policy validation)

重要な原則:
  「責務共有」≠「多層防御」
  
  各層は独立した拒否権を持つ。
  下流層が上流層を「信頼」することは許されない。
  各層は自層の責務について完全に独立した検証を行う。
```

---

## 4. 各層の「保証すること／保証しないこと」マトリックス

### 4-1. Gateway層

| 保証する | 保証しない |
|---------|----------|
| actor_id が確実に確定されている | MCP内部の実装正確性 |
| Authorization check が実行された | Visibility filtering の完全性 |
| Unauthorized request は進入しない | Event Store層での再検証の実施 |
| X-MoCKA-Key認証が成功した | Human Authority（Human Gateが別途判定） |
| actor_id が真正である | 下流での attack detection |

### 4-2. MCP層

| 保証する | 保証しない |
|---------|----------|
| tool call metadata から actor_id を re-extract | Gateway actor_id を信頼 |
| 内部consistency check を実行（optional?） | 最終Authorization判定（Gateway責務） |
| tool invocation context を確認（optional?） | Visibility filtering（別層） |
| | Human Gate decision（別層） |

**問題**: optional と marked された項目が保証を「しない」となるため、Defense in Depth が機能しない

### 4-3. Event Store層

| 保証する | 保証しない |
|---------|----------|
| Event query の actor_id match を検証 | Authorization check の実施（Gateway責務） |
| audit log に actor_id を記録 | Visibility filtering policy の正確性 |
| Integrity validation を実行 | Human decision の正当性 |
| Immutable event history を保持 | actor_id extraction（他層責務） |

### 4-4. Human Gate層

| 保証する | 保証しない |
|---------|----------|
| Decision Policy を検証 | Technical implementation details |
| Ratification の正当性 | Runtime event processing |
| Decision Ledger の integrity | Authorization execution |
| 意思決定の論理的整合性 | actual enforcement point |

---

## 5. DC_20260812_001～006 整合性評価

### 5-1. Decision一覧

| ID | Title | Status | Impact |
|----|-------|--------|--------|
| DC_001 | H2-3 Event-level Enforcement Owner - Gateway-led | Active | Phase 3実装スコープ確定 |
| DC_002 | Trusted actor_id Boundary - Defense in Depth | Active | **矛盾あり** |
| DC_003 | H2-3 Event-level Enforcement Owner (重複) | Active | 同上内容再記 |
| DC_004 | Trusted actor_id Boundary (重複) | Active | DC_002と同内容 |
| DC_005 | Authorization/Visibility/Projection 責任分離 | Active | 依存性確認・完全 |
| DC_006 | TODO_368 ORCHESTRA Terminal Event Redefinition | Active | **TODO_451と無関係** |

### 5-2. 検出された矛盾・重複・欠落

#### 矛盾1: MCP verification スコープ

```
DC_001: "MCP (再検証層): secondary permission check (optional)"
DC_002: "actor_id must be independently verified at each layer"

結論: optional と必須が同一Decision内で混在
影響: Defense in Depth の範囲が制度的に不明確
```

#### 重複1: DC_003 = DC_001の再記

```
DC_001と DC_003は同じ内容（Gateway-led Authorization）
重複の理由: 不明（別スコープの再確認か、意図的な強化か？）
```

#### 重複2: DC_004 = DC_002の再記

```
DC_002と DC_004は同じ内容（Defense in Depth actor_id verification）
重複の理由: 不明（確認強化か、制度化強化か？）
```

#### 欠落1: User / Human Authority の責務

```
DC_001～005 の記載内容:
  - Gateway責務: 明記
  - MCP責務: 記載あり（optional）
  - Event Store責務: 記載あり（検証）
  
欠落:
  - User が保証する範囲
  - Human Authority（きむら博士）が保証する範囲
  - Human Gate decision に対する appeal/override 権限
```

#### 欠落2: MCP optional の理由

```
DC_001で「optional」と記載されているが、その理由が記されていない。
  - 技術的に実装困難なのか？
  - 設計上の選択なのか？
  - Phase 3後に検討するのか？

この不明確さが、Phase 3実装スコープの曖昧さにつながる。
```

#### 無関係: DC_006

```
DC_006: TODO_368 ORCHESTRA Terminal Event Redefinition
関連性: TODO_451 Phase 2 停止条件とは無関係
理由: 
  - DC_006は「Event contract の Terminal Event timing」を定義
  - TODO_451 Phase 2の停止理由は「設計範囲確定待ち」（TIC Phase 2関連）
  
つまり、DC_006は「実装タイミングの修正」であり、「停止条件解除」ではない。
```

### 5-3. 整合性総合評価

| 観点 | 評価 | 根拠 |
|------|------|------|
| Authorization層 | 確定 | Gateway主導が明記・拒否権確定 |
| actor_id検証 | **不確定** | optional/必須が混在 |
| Visibility層 | 確定 | Authorization→Visibility→Projectionの依存性が明記 |
| Projection層 | 確定 | Authorization不成立時は実行不可が明記 |
| Gateway/User境界 | 部分的確定 | Gateway側は明確だが、User/Human Authority側が不明確 |
| 多層防御全体 | 部分的実装 | optional項目により完全性が不明確 |

---

## 6. Phase 3 Unblock条件 - 制度的閉鎖性の確認

### 6-1. 現在の停止原因（再掲）

```
Primary: TIC Phase 2 設計範囲確定（2026-06-15）を待機中
Secondary: H2-3 5層/3層構造の対応関係が未精査
Tertiary: MCP verification scope の制度的曖昧性
```

### 6-2. Unblock に必要な条件

#### 条件A: TIC Phase 2設計確定の実施
```
状態: 確認済み（E20260601_061 / 2026-06-15完了）
Phase 3への影響: UNBLOCK可能
```

#### 条件B: H2-3 責務確定（本調査の成果）
```
状態: 進行中
確定した事項:
  - Gateway Authorization主導
  - Authorization→Visibility→Projection依存性確定
  
未確定事項:
  - MCP verification の「optional」が制度的に許容されるか
  - 下流での「再検証不可」が実装上可能か
  
Phase 3への影響: **条件付きUNBLOCK**
  「optional」の定義をHuman Gate決定により明確にすれば UNBLOCK可能
```

#### 条件C: 責務の制度的閉鎖性

```
確定状況:

✓ Authorization owner: Gateway（拒否権あり・実装必須）
✓ Visibility owner: Gateway/Event Store（フィルタリング実装）
✓ Projection owner: downstream（削減実装）
✓ Event Integrity owner: Event Store（記録・検証）
✓ Decision admissibility owner: Human Gate（Policy validation）

?? User responsibility boundary: 定義されていない
?? Human Authority override 権限: 定義されていない
?? MCP拒否権: optional のため保証されない

Phase 3への影響: **条件付きUNBLOCK**
  User / Human Authority の責務を明文化すれば完全UNBLOCK可能
```

### 6-3. Phase 3 Unblock の可否判定

```
技術実装可能性: YES
  - Gateway authorization 実装可能
  - Visibility filtering 実装可能
  - Event Store logging 実装可能

制度責務明確性: PARTIAL
  - Gateway/MCP/Event Store の層別責務は明記
  - MCP optional について「なぜoptionalなのか」の理由が記載されていない
  - User / Human Authority の責務範囲が不明確

制度的完全性の評価:
  「実装が可能」≠「責務が確定している」

判定: **条件付きUNBLOCK**（以下の3点の明確化後）
```

---

## 7. Human Gate へ残す最終判断事項

### 7-1. 必須判断1: MCP verification の位置付け

```
問題: DC_001でoptional、DC_002で必須と矛盾

Human Gateへの質問:
  「MCP での actor_id 再検証は、Defense in Depth を完成させるために
    『必須』なのか『オプション』なのか？」

根拠:
  - optional ならば、Gateway単独障害時に下流での検証ができない
  - 必須ならば、DC_001の「optional」記載は削除すべき
  - いずれにせよ、現状は制度的に曖昧

結論: この判断をせずに Phase 3実装スコープは確定できない
```

### 7-2. 必須判断2: User責務の明文化

```
問題: User が何を保証し何を保証しないかが定義されていない

Human Gateへの質問:
  「User（X-MoCKA-Key holder）の責務範囲は何か？
    特に、authorization failure時の liability境界は？」

根拠:
  - Gateway がactor_id を確定しても、その actor_id が「本当にそのuser」か？
  - User が API key を漏洩させた場合の責任追跡
  - Human Authority（きむら博士）による override 時の User notification

結論: User責務が不明確では、ユーザーサポート/サポート契約が設計できない
```

### 7-3. 必須判断3: Human Authority override 権限

```
問題: Human Gate decision が出た後の override 権限が不明確

Human Gateへの質問:
  「Human Gate（Human Authority）が下した『承認』『却下』『保留』decision に対し、
    上位authority（きむら博士本人など）の override 権限は存在するか？」

根拠:
  - Decision Ledger Bypass インシデント（TODO_361）の再発防止
  - Authority hierarchy の明文化（User → MoCKA System → Human Gate → ?)
  - Appeal/Review機構の必要性

結論: Authority hierarchy が不明確では、governance recursion（制度が制度を監視する仕組み）が実装できない
```

### 7-4. 確認判断1: DC_006 と TODO_451 の関係

```
質問: 「DC_006 (ORCHESTRA Terminal Event Redefinition) が、
       TODO_451 Phase 2 停止条件解除の『十分条件』なのか？」

現状分析:
  - DC_006は「Event contract の timing」修正
  - TODO_451停止は「TIC Phase 2設計範囲確定待ち」（別の理由）
  
結論: DC_006は TODO_451と独立した修正であり、
      停止条件解除の十分条件ではない（DC_006単独では Phase 2 停止は解けない）
```

### 7-5. 確認判断2: H2-3と制度の整合性

```
質問: 「H2-3 (5層構造案 vs 3層モデル) の対応関係が未精査だが、
       Phase 3実装に支障はないか？」

現状分析:
  - 3層モデル（Control/Sovereign/Data）は Phase 4で確定済み
  - 5層構造案との対応関係は「進行中」
  - 対応関係の未精査は「設計の完全性」に影響

結論: Phase 3は 3層モデル（確定済み）ベースで実装可能だが、
      完全な制度確立には 5層との整合性確認が必須
```

---

## まとめ: 実装可能性 vs 制度完全性

### 実装可能性: ✓ YES
```
Gateway Authorization → Visibility filtering → Event logging の直列実装は
技術的に可能。Phase 3 code changes は明記されている（DC_001より）。
```

### 制度責務確定度: ⚠ PARTIAL (70%)
```
確定した事項:
  - Authorization layer: Gateway主導（明確）
  - Visibility layer: filtering実装（明確）
  - Event Integrity: logging＆validation（明確）
  - Layer dependency: Authorization→Visibility→Projection（明確）
  
未確定事項:
  - MCP verification: optional か必須か（曖昧）
  - User responsibility: 定義なし（欠落）
  - Human Authority override: 定義なし（欠落）
  - H2-3 full definition: 進行中（未完了）
```

### Phase 3 Unblock 判定

```
R01監査基準: 「実装可能性ではなく、責務・権限・保証範囲・証拠境界が
            確定したことを Phase 3 Unblockの根拠とする」

判定: **CONDITIONAL UNBLOCK**

条件:
  1. MCP verification scope を Human Gate decision で明確化
  2. User responsibility boundary を明文化
  3. Human Authority override 権限を定義
  
これら3条件が Human Gate で明示決定されれば、
Phase 3実装スコープは完全に確定する。
```

---

## 参考資料

### 取得した公式Decision
- DC_20260812_001: H2-3 Event-level Enforcement Owner - Gateway-led Defense in Depth
- DC_20260812_002: Trusted actor_id Boundary - Defense in Depth
- DC_20260812_003: H2-3 Event-level Enforcement Owner (重複記載)
- DC_20260812_004: Trusted actor_id Boundary (重複記載)
- DC_20260812_005: Authorization/Visibility/Projection - Responsibility Separation
- DC_20260812_006: TODO_368 Decision 6: ORCHESTRA Terminal Event Sequence Redefinition

### 参照イベント・文書
- E20260601_061: TIC Phase 2 設計範囲確定
- E20260622_017030043d9b2: Control/Sovereign/Data 3層モデル確定
- TODO_451: [くろこ/repo] 検証履歴のcommit/seal/push
- TODO_368: ORCHESTRA Event Contract validation

### 監査実行スコープ
- 対象: TODO_451 Phase 2、H2-3 Event-level Enforcement
- モード: Read-Only（ファイル読取・Decision照会のみ）
- 実行時間: 2026-08-12
- 調査者権限: くろこ（制度監査権）

---

**調査終了 / Human Gate 判断待機中**

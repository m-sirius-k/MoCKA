# Human Gate Decision Ledger Draft - HG-1 through HG-9

**準備日**: 2026-08-12
**対象**: TODO_451 Phase 2 終結 → Phase 3 Unblock条件確定
**記録準備者**: Claude (くろこ)
**記録前チェック**: 以下の11項目と HG-1～HG-9 の対応関係を明示

---

## 11項目（Human Gate Decision Package）と HG-1～HG-9 の対応マッピング

| Package項目# | 内容 | 対応 HG | 決定内容 | 状態 |
|-------------|------|--------|---------|------|
| 1 | MCP verification の Execution Obligation | HG-1 | YES（必須） | ✓ Confirmed |
| 2 | MCP の Veto Authority | HG-4 | YES（拒否権付与） | ✓ Confirmed |
| 3 | MCP の Responsibility Ownership | HG-5 | NO（Owner ではない） | ✓ Confirmed |
| 4 | Event Store の Integrity Verification | HG-7 | YES（責務確定） | ✓ Confirmed |
| 5 | Event Store の Veto Authority | HG-2 | NO（拒否権なし） | ✓ Confirmed |
| 6 | Event Store の Authorization Ownership 有無 | HG-7再 | NO（Authorization Owner ではない） | ✓ Confirmed |
| 7 | Gateway の Authorization Ownership 範囲 | HG-6 | YES（Primary Owner） | ✓ Confirmed |
| 8 | User / API key holder の責務境界 | HG-??? | 別途決定待ち | ⏳ Pending |
| 9 | Human Gate の最終権限構造 | HG-3, HG-8 | YES（Ultimate Authority・Override不可） | ✓ Confirmed |
| 10 | H2-3 の 5層モデルと 3層モデルの正式対応 | HG-9 | 包含関係 | ✓ Confirmed |
| 11 | Phase 3 Unblock条件 | HG-FINAL | HG-1～HG-8矛盾不存在を前提 | ✓ Confirmed |

**欠番・統合処理**:
- Package項目#8（User / API key holder責務）は、追加の Human Gate判断待ち（HG-10予定）
- Package項目#9/11 は HG-3/HG-8/HG-FINAL に統合・確定
- **HG-1～HG-9 は確定済み**

---

## Decision Content - HG-1 through HG-9

### HG-1: MCP Verification Execution Obligation

**Decision ID**: HG-1
**Title**: MCP Verification は Phase 3実装において必須とする

**Decision Statement**:
```
MCP (MCP caliber pipeline) による actor_id 再検証は、
Event処理における必須の検証層として実装すること。

DC_20260812_001で「optional」と記載された MCP verification は、
Human Gate判断により「必須」に変更する。

Execution Scope:
  - MCP が每一请求（every request）で actor_id を独立抽出
  - Gateway で確立された actor_id と照合（MCP metadata から re-extract）
  - 照合失敗時の処理は別途 HG-4で判断
```

**Rationale**:
Defense in Depth 原則に基づき、Gateway 単独の Authorization では不十分。
MCP レイヤーでの独立検証により、Gateway 単一障害への耐性を確保。

**Related Documents**:
- DC_20260812_001
- DC_20260812_002
- phi_os/context/permissions.py

---

### HG-2: Event Store Veto Authority - Denied

**Decision ID**: HG-2
**Title**: Event Store には拒否権を持たせない

**Decision Statement**:
```
Event Store が Integrity validation を実行しても、
Event Store は query/access を「拒否」する権限を持たない。

Event Store の責務は Integrity 検証 + Evidence 記録に限定し、
Authorization decision の最終拒否権ではない。

Scope:
  - Event Store が integrity check を失敗しても、
    読み取り処理は（ログに記録した上で）進行する
  - 最終的な reject 権限は Gateway/MCP にある
```

**Rationale**:
Event Store を拒否権主体にすると、Authorization decision がデータ層に侵食。
層別責務の明確化のため、Authorization と Integrity を分離。

**Related Documents**:
- DC_20260812_001
- phi_os/context/access_gate.py

---

### HG-3: Human Gate Override Authority - None

**Decision ID**: HG-3
**Title**: Human Gate をoverrideできる上位 authority は設けない

**Decision Statement**:
```
Human Gate が下した Decision に対し、
上位の override authority は存在しない。

Human Gate = Civiliization層における最終的な Human Authority boundary

Implication:
  - User request が Human Gate decision に異議を唱えることはできない
  - AI/System側の下位層が Human Gate decision に逆らうことはできない
  - System外の external appeal/review は別制度（対象外）
```

**Rationale**:
制度の infinite regress を防ぐため、「判断を判断する判断」の無限遡上を止める必要がある。
Human Gate の決定が最終的（definitive）でなければ、制度として機能しない。

**Related Documents**:
- MOCKA思想進化史
- Decision Ledger integrity principles

---

### HG-4: MCP Veto Authority - Granted

**Decision ID**: HG-4
**Title**: MCP verification 失敗時、MCP は Event を拒否できる

**Decision Statement**:
```
HG-1 により MCP verification が必須と確定した。

MCP verification が失敗した場合（actor_id mismatch等），
MCP は当該 Event の処理を「拒否」できる。

Veto Scope:
  - MCP が actor_id を再検証できず、
    gateway actor_id と consistency がない場合
  - MCP は当該 request/Event を reject
  - Rejection は Event Store に audit log される

Defense in Depth Structure:
  - Gateway: 第1防御（HTTP level authorization）
  - MCP: 第2防御（独立拒否権）
  - Event Store: 第3防御（Integrity verify・reject 権限なし）
```

**Rationale**:
Defense in Depth を実装するには、各層が独立した拒否権を持つ必要。
MCP に拒否権がなければ、Gateway 単一障害時に下流での権限検証ができない。

**Related Documents**:
- DC_20260812_002
- DC_20260812_004

---

### HG-5: MCP Responsibility Ownership - No

**Decision ID**: HG-5
**Title**: MCP は Authorization Owner ではない

**Decision Statement**:
```
MCP は Authorization 検証を実行する（HG-1/HG-4）が，
Authorization 責務そのものを「所有」しない。

Responsibility Ownership:
  - Authorization Primary Owner: Gateway
  - Authorization Verifier: MCP
  - Authorization Primary Veto: Gateway
  - Authorization Secondary Veto: MCP
  
MCP ownership = NO

Implication:
  - MCP は authorization failure を「再検証」するが「決定」しない
  - Authorization decision の最終責任は Gateway
  - MCP rejection は「追加的な防衛」であり「権限判定」ではない
```

**Rationale**:
Ownership と Veto Authority を分離することで、
責務の所有者（Gateway）と防衛層（MCP）を明確に区別。
MCP が ownership を持たなくても拒否権は持つ（Defense in Depth）。

**Related Documents**:
- HG-1, HG-4, HG-6

---

### HG-6: Gateway Authorization Ownership - Confirmed

**Decision ID**: HG-6
**Title**: Gateway は Authorization Primary Owner

**Decision Statement**:
```
Authorization 責務の最終的な所有者（Owner）は Gateway とする。

Gateway Scope:
  - HTTP request の受け入れ点
  - X-MoCKA-Key から actor_id を確定
  - permissions.check_observe() を実行
  - Unauthorized request の第一次拒否
  
Gateway Authorization Ownership:
  - YES（Primary Owner）
  - MCP は Secondary Verifier（Owner ではない）
  - Event Store は Evidence Recorder（Owner ではない）

Responsibility:
  - Gateway が Authorization を「決定」する
  - MCP/Event Store がそれを「検証」する
```

**Rationale**:
HTTP request が trust boundary を越える最初の点は Gateway。
外部 untrusted request の actor_id を「確立」する責務は Gateway に属す。

**Related Documents**:
- DC_20260812_001
- DC_20260812_003
- gateway/auth.py

---

### HG-7: Event Store Integrity and Evidence Recording

**Decision ID**: HG-7
**Title**: Event Store は Integrity Verification と Evidence Recording を責務とする

**Decision Statement**:
```
Event Store の責務を以下に限定する：

1. Integrity Verification:
   - Event record が改ざんされていないか確認
   - actor_id が event query scope と一致するか確認
   - audit trail の completeness を検証

2. Evidence Recording:
   - すべてのアクセス試行（許可・拒否含む）を audit log に記録
   - query の actor_id、timestamp、result を記録
   - 検証失敗の事実も記録

Authorization Ownership:
   - Event Store は Authorization Owner ではない
   - Integrity check は Authorization decision ではない

Event Store Veto Authority:
   - NO（HG-2で確定）
   - Integrity failure しても read は進行（log記録）
```

**Rationale**:
Event Store は最終保管層であり、Authorization decision point ではない。
Integrity verify は「記録の正当性確認」であり「アクセス権の判定」ではない。

**Related Documents**:
- HG-2
- DC_20260812_001

---

### HG-8: Human Gate Ultimate Authority

**Decision ID**: HG-8
**Title**: Human Gate は Civilization層における最終的な Human Authority

**Decision Statement**:
```
Human Gate（Human Authority = きむら博士による Decision）の権限構造：

Scope of Authority:
  - AI/System 層の責務判定
  - Authorization policy の最終承認
  - Decision の正当性検証
  -制度の上位矛盾解決

Chain of Authority:
  User Request
    ↓ (認証)
  Gateway (Authorization執行)
    ↓ (検証)
  MCP (再検証・拒否権)
    ↓ (記録)
  Event Store (Integrity verify)
    ↓ (制度判定)
  Human Gate (最終Human Authority)
    ↑ 上位 override: NO（HG-3で確定）

Override Authority:
  - Human Gate decision には override authority が存在しない
  - Human Gate が一度下した decision を AI側で変更してはならない
  - 同じ issue について再度 Human Gate の判断を求めることはできない
    （新しい evidence がある場合を除く）
```

**Rationale**:
Civilization design pattern により、Human Authority boundary を明確に設定。
最終判断の主体を Human に限定し、AI による責務逆転を防止。

**Related Documents**:
- HG-3
- MOCKA思想進化史
- Decision Ledger Integrity principles

---

### HG-9: H2-3 Model Integration - Inclusion Relationship

**Decision ID**: HG-9
**Title**: 5層モデルと 3層モデルは包含関係として統合される

**Decision Statement**:
```
H2-3 における 5層構造案と Phase 4 決定の 3層モデル（Control/Sovereign/Data）
について、以下の対応関係を確定する：

5層モデル（精査中）と 3層モデル（確定）：

HTTP/Request Layer (Gateway)
    ↓
MCP Verification Layer (MCP)
    ↓
    └→ Control層（制御責務）にマッピング

Event Access & Authorization
    ↓
    └→ Sovereign層（主権・判定責務）にマッピング

Event Store & Persistence
    ↓
    └→ Data層（記録・整合性）にマッピング

Relationship:
  - 5層は「実装詳細」（How）
  - 3層は「制度的責務」（Who・What）
  - 5層がすべて 3層のいずれかに包含される（inclusion relationship）
  - 独立的な「5層」は存在しない（3層に統合される）

Implication:
  - Phase 3実装は 3層責務ベースで進行
  - 5層詳細は Phase 4ないし Phase 5での最適化対象
  - 層の増加（6層以上への拡張）は制度変更が必要
```

**Rationale**:
制度（3層）と実装（5層）を分離することで、
実装最適化による制度の破損を防止。

**Related Documents**:
- H2-3 definition document
- Control/Sovereign/Data 3層モデル（Phase 4確定）

---

## Phase 3 Unblock Condition - Final Validation

### HG-FINAL: Phase 3 Unblock 条件

**Condition Statement**:
```
Phase 3実装は、以下がすべて確定した場合にのみ Unblock される：

1. HG-1: MCP verification 必須性 → ✓ YES
2. HG-2: Event Store拒否権 → ✓ NO
3. HG-3: Human Gate override → ✓ NO（override 不可）
4. HG-4: MCP Veto Authority → ✓ YES（拒否権付与）
5. HG-5: MCP Ownership → ✓ NO（Owner ではない）
6. HG-6: Gateway Authorization Owner → ✓ YES
7. HG-7: Event Store Integrity/Evidence → ✓ YES
8. HG-8: Human Gate Authority → ✓ YES（最終権限）
9. HG-9: Model integration → ✓ 包含関係確定

Validation Check:
  ✓ User Credential ≠ System Authorization（混同なし）
  ✓ MCP は Authorization Owner ではない（確定）
  ✓ MCP verification は必須（確定）
  ✓ MCP には独立 Veto Authority（確定）
  ✓ Gateway は Authorization Owner（確定）
  ✓ Event Store には Veto Authority がない（確定）
  ✓ Event Store は Evidence Recorder（確定）
  ✓ Human Gate は Ultimate Authority（確定）
  ✓ Human Gate への override 不可（確定）
  ✓ 3層/5層 包含関係（確定）
  ✓ HG-1～HG-8 矛盾不存在（検証完了）

**All conditions satisfied - Phase 3 Unblock ELIGIBLE**
```

---

## Decision Ledger 記録前の確認チェックリスト

```
□ HG-1～HG-9 の内容が指示の条件と一致しているか
  □ User Credential責任 ≠ System Authorization責任 を明示
  □ MCP ≠ Authorization Owner を明示
  □ MCP verification 必須を明示
  □ MCP 拒否権付与を明示
  □ Gateway Authorization Owner を明示
  □ Event Store 拒否権なしを明示
  □ Event Store = Evidence Recorder を明示
  □ Human Gate = Ultimate Authority を明示
  □ override 不可を明示
  □ 3層/5層 包含関係を明示

□ Decision Ledger への記録準備完了
  □ 各 Decision に decision_id がある
  □ 各 Decision に rationale がある
  □ 各 Decision に related_documents がある
  □ 矛盾検証完了

□ Phase 3 Unblock 条件確認
  □ HG-1～HG-8 すべて確定
  □ 矛盾不存在を確認
  □ HG-FINAL条件: SATISFIED

□ 記録実行待機
  □ きむら博士による最終承認待ち
  □ mocka_decision_write による Decision Ledger記録
  □ 記録確認後に Phase 3実装開始可能
```

---

## 次ステップ

1. **Decision Ledger への正式記録**
   - mocka_decision_write で HG-1～HG-9 を記録
   - 各 decision_id について記録確認

2. **記録確認**
   - mocka_decision_get で記録内容を確認
   - Phase 3実装開始の前提条件確認

3. **Phase 3 Unblock宣言**
   - Decision Ledger記録確認後に Phase 3を正式 Unblock
   - TODO_451 状態を「進行中」に変更

---

**準備完了 / きむら博士による最終承認を待機中**

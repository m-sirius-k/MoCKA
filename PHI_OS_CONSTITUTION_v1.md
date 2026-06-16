# PHI_OS_CONSTITUTION_v1.md
## PHI-OS 制度憲法 — MoCKA Institutional Authority 正式定義

**文書番号:** PHI-OS-CONST-001  
**作成日:** 2026-06-16  
**フェーズ:** MoCKA Phase 4 — 制度実装  
**状態:** RATIFIED v1  
**発効条件:** Gate Authority承認後に効力を持つ  

---

## 前文

本憲法は、MoCKAにおける唯一の制度執行機関としてPHI-OSを正式に定義し、  
全制度参加者（Human、AI、MCP、CLI、Script、Runtime、External System）が  
従うべき原則・権限・制度接続経路・禁止事項・Complianceを固定するものである。

本憲法はMoCKA制度体系の最上位文書であり、いかなる実装・運用文書もこれに反してはならない。

---

## 第1章 基本理念

### 1.1 PHI-OSの役割

PHI-OS（Persistent History Intelligence OS）は、MoCKA全体の  
**唯一の制度執行機関（Institutional Authority）** である。

PHI-OSは以下の機能を担う。

- 全Artifactの制度意味（Meaning）の最終裁定
- Gate定義・Gate通過基準の設定と維持
- Event生成条件の制度的保証
- Institution間の権限境界の維持
- 制度違反の検知・記録・修復命令の発行

### 1.2 制度の目的

MoCKA制度は以下の目的のために存在する。

1. **信頼性の保証** — すべての判断・行動が記録可能かつ検証可能であること
2. **変化の制度化** — 事故・インシデントが文明進化の資産となること
3. **権限の明確化** — 誰が何を決定できるかが常に制度上明確であること
4. **再現性の担保** — 任意の時点の制度状態が再現可能であること
5. **沈黙の禁止** — 記録なき作業はMoCKAとして存在しない

### 1.3 創造OSとしての位置付け

PHI-OSは単なるシステムソフトウェアではない。  
PHI-OSは、MoCKAが「AIではなく文明モデル」として機能するための  
**制度カーネル**であり、知識の記録・検証・証明を継続的に実行する  
永続型知性の基盤（Persistent Intelligence Foundation）である。

PHI-OSは以下の三要素を実現する制度OSである。

| 要素 | 内容 |
|---|---|
| Structure（構造） | Gate・Institution・Bindingによる制度的拘束 |
| Record（記録） | Eventによる不変・追記専用の事実台帳 |
| Verification（検証） | Complianceによる制度整合性の継続的確認 |

---

## 第2章 制度原則

本章に定める7原則は、MoCKA制度の根本規則であり変更不可とする。  
変更を要する場合はGate Authorityの完全承認と新版Constitutionの発行を必要とする。

### 原則1: Eventは唯一の事実である

- Event Ledgerはappend-onlyであり、いかなる主体も既存Eventを変更・削除できない
- DBの内容・Derived Viewの表示はEventから派生した参照情報であり、それ自体は制度上の事実ではない
- 制度上の事実の確認は常にEvent Ledgerを参照することで行う

### 原則2: PHI-OSのみが制度を定義できる

- MeaningDefinition、Gate定義、Institution定義、Binding規則の制定はPHI-OSの専権事項である
- いかなる制度参加者もPHI-OSの承認なしに制度を新設・変更・廃止できない
- PHI-OS自身の変更もGate Authorityの承認を要する（自己適用原則）

### 原則3: Gateのみが制度変更を承認できる

- 制度変更とは、Meaning・Institution・Gate・Bindingの新設・変更・廃止を指す
- 制度変更はいずれかのGate（主にDocument Gate）を通過し、Eventとして記録されなければならない
- Gateを通過しない制度変更はShadow状態とみなし制度的効力を持たない

### 原則4: DBは保存媒体であり真実ではない

- データベース（SQLite等）はEventの物理的格納媒体であり、制度上の権威は持たない
- DBへの直接書き込みによるEvent生成は制度違反である
- DBの参照は許可するが、DBの内容を制度的事実として扱ってはならない

### 原則5: Derived Viewは派生情報である

- COMMAND CENTER・Dashboard・API応答等のDerived ViewはEventから算出された表示であり、  
  制度上の権威はEventに帰属する
- Derived Viewの表示内容に誤りがある場合、Derived Viewを修正するのではなく  
  Eventの制度的正確性を検証する
- Derived Viewを直接編集する行為は制度違反である

### 原則6: Meaningが制度上の意味を決定する

- すべてのArtifactはMeaning Authority（MEANING_AUTHORITY_v1.md）に基づく  
  単一の主Meaningを持たなければならない
- Meaningが未定義のArtifactは制度未登録（UNCLASSIFIED）であり、  
  いかなるInstitution・Gateにも制度接続できない
- Meaningの変更はMeaning変更プロトコルに従い、変更記録が必須である

### 原則7: Institutionが責任主体となる

- すべてのArtifactは単一の主Institutionに帰属する
- Institutionはそのに帰属するArtifactの制度的健全性に責任を持つ
- Institution未所属のArtifactはOrphan状態であり、制度的操作の対象となれない

---

## 第3章 Authority体系

### 3.1 Authority定義

AuthorityはPHI-OS制度内で特定の制度行為を実行する権限の単位である。  
各Authorityは重複して行使できない（Authority一意性原則）。

| Authority | 定義 | 保持主体 | 責務 |
|---|---|---|---|
| **Event Authority** | Eventの生成・記録を承認する権限 | PHI-OS / Event Gate | Event IDの採番、Event Ledgerへの書き込み承認 |
| **Knowledge Authority** | 知識Artifactの登録・参照・廃止を管理する権限 | PHI-OS / Knowledge Gate | Knowledge登録条件の判定、Knowledge Ledger維持 |
| **Gate Authority** | Gateの新設・廃止・基準変更を承認する権限 | PHI-OS（最上位） | Constitution改定の最終承認、全Gate定義の管理 |
| **Version Authority** | ArtifactのVersionおよびLifecycleを管理する権限 | PHI-OS / Release Gate | Version確定、Seal発行、Deprecation承認 |
| **Verification Authority** | 制度整合性・Compliance・監査を実行する権限 | PHI-OS / Compliance Runtime | Audit実行、違反検知、修復命令発行 |
| **Institution Authority** | Institutionの設立・変更・廃止を承認する権限 | PHI-OS（専権） | Institution定義、Institution間境界の確定 |

### 3.2 Authority一意性原則

- 同一の制度行為に対して複数のAuthorityが重複して行使されてはならない
- Authority間の競合が発生した場合、Gate Authorityが最終裁定を行う
- Authorityの委譲は記録を伴う場合にのみ有効であり、暗黙の委譲は認めない

### 3.3 Authority継承規則

```
Gate Authority（最上位）
  ├─ Institution Authority（制度機関の管理）
  ├─ Event Authority（事実記録の管理）
  ├─ Knowledge Authority（知識資産の管理）
  ├─ Version Authority（版・配布の管理）
  └─ Verification Authority（制度整合性の管理）
```

上位Authorityは下位Authorityの権限行使を停止・審査できる。  
下位Authorityは上位Authorityの決定を覆すことができない。

---

## 第4章 Binding原則

### 4.1 制度接続の唯一正規経路

すべてのArtifactは以下の経路によってのみ制度に接続される。

```
Artifact
   ↓ Meaning付与（PHI-OS承認）
Meaning
   ↓ Institution帰属確定
Institution
   ↓ Gate通過（Gate Authority検証）
Gate
   ↓ Event生成（Event Authority記録）
Event
```

この経路を迂回した制度接続は、Binding状態にかかわらず制度的効力を持たない。

### 4.2 Binding状態の定義

| 状態 | 定義 | 制度的扱い |
|---|---|---|
| CONNECTED | 正規経路を完全に通過した状態 | 制度的操作の対象 |
| PARTIAL | 経路の一部が未完了の状態 | 制限付き操作可。完全接続が必要 |
| SHADOW | 経路外に存在するが無害と判断された状態 | 監視対象。制度操作不可 |
| ORPHAN | Institution未帰属の状態 | 制度操作不可。即時修復対象 |
| DEPRECATED | 廃止決定済みの状態 | 参照のみ可。後継実装の確認が必要 |
| UNKNOWN | Meaningが特定できない状態 | 制度操作不可。Audit最優先 |

### 4.3 Binding変更プロトコル

- Bindingの変更はDocument Gateを通過し、変更Eventが記録されなければならない
- CONNECTED → DEPRECATEDの遷移は後継実装の確認と承認を要する
- いかなる主体もPHI-OS承認なしにCONNECTEDを宣言できない

---

## 第5章 禁止事項

以下は制度違反（Constitutional Violation）であり、発覚次第即時にIncident Eventが生成される。

### 5.1 Event関連禁止事項

| 禁止行為 | 理由 |
|---|---|
| DB直接更新によるEvent生成 | Event Authorityを迂回するため |
| Event IDの手動入力・改竄 | Event一意性を破壊するため |
| Event Ledgerの変更・削除 | append-only原則違反 |
| Gate迂回によるEvent生成 | Gate Authorityを無効化するため |

### 5.2 Artifact関連禁止事項

| 禁止行為 | 理由 |
|---|---|
| Meaning未定義Artifactの制度登録 | 原則6違反 |
| Institution未所属ArtifactのGate通過 | 原則7違反 |
| Bindingを持たないArtifactの制度的操作 | 制度接続なき操作は事実の汚染 |

### 5.3 Gate関連禁止事項

| 禁止行為 | 理由 |
|---|---|
| Gate迂回による制度変更 | 原則3違反 |
| Gate定義のPHI-OS承認なしの変更 | 原則2違反 |
| 複数GateへのAuthority重複付与 | Authority一意性違反 |

### 5.4 View関連禁止事項

| 禁止行為 | 理由 |
|---|---|
| Derived Viewの直接編集 | 原則5違反（Eventを通じない事実改竄） |
| DBコンテンツを制度的事実として引用 | 原則4違反 |

### 5.5 Authority関連禁止事項

| 禁止行為 | 理由 |
|---|---|
| 記録なきAuthority委譲 | Authority追跡不能 |
| PHI-OS承認なしの制度新設 | 原則2違反 |
| Authority重複行使 | Authority一意性違反 |

---

## 第6章 Compliance

### 6.1 制度違反の定義

制度違反（Constitutional Violation）とは、本憲法第2章の7原則または第5章の禁止事項に反する行為である。  
違反は行為の意図にかかわらず、制度上の結果により判断する。

### 6.2 違反の分類

| 分類 | 定義 | 例 |
|---|---|---|
| **Critical Violation** | 制度の根幹を破壊する即時対処必須の違反 | Event Ledger改竄、Gate権威複数化 |
| **High Violation** | 主要制度機能に障害をきたす違反 | Institution未定義Artifactの本番稼働 |
| **Medium Violation** | 制度的曖昧性を生む違反 | Meaning未確定のまま長期放置 |
| **Low Violation** | 制度整合性の微細な欠陥 | Naming Convention不準拠 |

### 6.3 監査

- Verification Authorityはいつでも全Artifactの制度監査を実行できる
- 監査はBINDING_REGISTRYおよびBINDING_GAP_REPORTを基礎資料とする
- 定期監査の周期はGate Authorityが定める
- インシデント発生時は即時特別監査を実施する

### 6.4 修復

- 違反が検知された場合、Verification Authorityは修復命令（Remediation Order）を発行する
- 修復はIMPLEMENTATION_PRIORITYに従い優先度順に実施する
- 修復完了はEvent Gateを通じたEvent記録により確認する
- 修復なき違反が継続する場合、当該ArtifactのBinding状態をSHADOWに降格する

### 6.5 記録方法

- すべての違反・監査・修復はEvent Ledgerに記録する
- 記録フォーマットは `INCIDENT: {違反種別} — {対象Artifact} — {対処状態}` とする
- 違反記録は永続的であり削除できない（append-only）
- 重大違反（Critical/High）は docs/incidents/ へのドキュメント記録も必須とする

---

## 付記

本文書はMoCKA Phase 4 制度設計フェーズの成果物として策定された。  
BINDING_REGISTRY_v1.md、MEANING_AUTHORITY_v1.md、INSTITUTION_BINDING_MAP_v1.md、  
BINDING_GAP_REPORT_v1.md、IMPLEMENTATION_PRIORITY_v1.mdを基礎資料とする。

関連文書:
- INSTITUTION_PROTOCOL_v1.md — 制度参加者共通運用規約
- GATE_ARCHITECTURE_v1.md — Gate統一設計
- MEANING_AUTHORITY_v1.md — Meaning正典定義
- BINDING_REGISTRY_v1.md — Artifact制度登録台帳

*文書バージョン: v1.0*  
*最終更新: 2026-06-16*  
*次回見直し: Gate Authority承認後またはPhase 5移行時*  

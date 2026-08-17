# MoCKA Public Evolutionary Snapshot Reconstruction v1.0

**調査日:** 2026-08-17  
**調査方法:** 公開リポジトリ、Git commit history、公開ドキュメントのみを使用  
**分類:** OBSERVED / DOCUMENTED / HISTORICAL / INFERRED / UNKNOWN を明確に分離

---

## 1. 調査範囲

### 1.1 調査対象メディア

- GitHub リポジトリ: `m-sirius-k/MoCKA` (https://github.com/m-sirius-k/MoCKA)
- 公開ドキュメント: README.md, ARCHITECTURE.md, CONSTITUTION.md, 各種設計文書 (*.md)
- Git commit履歴: 全ブランチの commit log
- ディレクトリ構造: 物理ファイルシステム上の構成

### 1.2 調査対象外（内部限定情報）

以下は公開リポジトリに存在しないため調査対象外:
- MOCKA_OVERVIEW.json の内部状態管理
- mocka_mcp_server.py の完全な動作実装
- Decision Ledger の詳細記録
- 内部システムの「shadow_Movement」運用状況
- 過去のインシデント記録の詳細

---

## 2. 公開情報から見えるMoCKAの創造過程

### 2.1 コア思想の成熟（DOCUMENTED）

**初期仮説 (README.mdより)**

```
MoCKA is not a system. It is a civilization model.
Every action is recorded. Every decision is verified. Every failure becomes an asset.
```

**宣言:** MoCKAは「ログシステム」「フレームワーク」「ラッパー」ではなく、
**決定論的ガバナンスアーキテクチャ**（deterministic governance architecture）
として設計されている。

**根本哲学（README.md より）:**

| 従来のAI | MoCKA |
|---|---|
| 答えを生成 | 信頼できる知識を構築 |
| 文脈を忘れる | 制度的記憶を保持 |
| ブラックボックス決定 | 完全に監査可能な決定チェーン |
| 静かに失敗 | すべての異常を検出・記録 |
| 毎回ゼロからスタート | 蓄積・進化し続ける |

**観察:** この思想は公開ドキュメントの複数層（README, CONSTITUTION, PHI_OS_CONSTITUTION_v1）
で一貫して反復されており、単一のSnapshot的な設計ではなく、**段階的に精緻化されている**
ことが示唆される。

### 2.2 全体構図の形成（DOCUMENTED + HISTORICAL）

**Civilization Loop（README.md より）**

```
Observation → Record → Incident → Recurrence → Prevention → Decision → Action → Audit
     ↑                                                                          ↓
     └──────────────────── Learning : infield ◄─────────────────────────────────┘
```

**観察:** この ループは以下の特性を示す:
- **閉ループ設計**: 学習が feedback として戻る
- **Append-only 記録**: 線形時間軸での履歴管理
- **自己修復能力**: Auditが Prevention へ入力される構造

**Dual-Path Architecture（README.md より）**

- `mocka_Movement`: 主統治ループ（通常運用）
- `shadow_Movement`: 独立検証経路（フォールバック）

**インフィールド / アウトフィールド分離（README.md より）**

```
mocka_Receptor (単一入口)
      ↓         ↓
infield    outfield
(記憶)     (公開)
```

**観察:** このニ層分離は、「内部状態の維持」と「外部への証明」を意図的に分離する
設計思想であり、**独立したコンポーネント化**を可能にする構造である。

---

## 3. コンポーネントの独立進化

### 3.1 公開ディレクトリ構造から見える独立性（OBSERVED）

**core_kernel/ 配下の独立モジュール:**

```
core_kernel/
├── orchestra/           ← Orchestration エンジン
├── orchestra_core/      ← Orchestration 実装（重複or派生）
├── relay_core/          ← Relay コンポーネント
├── memory_core/         ← Memory コンポーネント
├── phios_integration/   ← PHI-OS 統合層
├── prism/               ← Prism コンポーネント
├── governance/          ← ガバナンス層
├── core_store/          ← コアストレージ
└── event_contracts/     ← イベント仕様
```

**観察:**

1. **Orchestra / Relay / Memory**: core_kernel 内で**独立したディレクトリ**として存在
2. **重複実装の痕跡**: `orchestra/` と `orchestra_core/` の存在（BINDING_GAP_REPORT_v1.md で確認）
3. **統合層の存在**: `phios_integration/` という名称から、PHI-OSが**後付けの統合機構**
   として追加されたことが示唆される

### 3.2 独立エントリーポイント（DOCUMENTED）

**README.md より:**
```bash
mocka-check        # Ledger + governance check
mocka-loop         # Single civilization loop cycle
mocka-seal         # Seal decision into ledger
```

**観察:** 各コマンドが**個別の概念的操作**として公開されており、
Orchestra/Relay/Memoryが**独立的に呼び出し可能**な設計を示唆する。

### 3.3 独立テスト（DOCUMENTED）

**MEMORY_LAYER.md より:**
```bash
python memory/memory_integration_test.py
python memory/memory_retrieval_test.py
python memory/memory_consistency_test.py
```

**観察:** Memory Layer は**独立した3つのテスト**を持つ。
これは、Memory が MoCKA の他の層から**独立して検証可能**
な設計であることを示唆する。

### 3.4 独立ドキュメント（DOCUMENTED）

公開リポジトリには以下の独立設計文書が存在:

- `MEMORY_LAYER.md`: Memory の設計・API・データフロー
- `DECISION_LAYER.md`: Decision エンジンの独立設計
- `SEMANTIC_LAYER.md`: Semantic 解析の独立仕様
- `PHI_OS_CONSTITUTION_v1.md`: PHI-OS の制度定義（**他から独立したドキュメント**）

**観察:** 各コンポーネントが**独立したアーキテクチャドキュメント**を
持つこと自体が、コンポーネント的な発展段階を示している。

### 3.5 Independent Product Potential（OBSERVED + INFERRED）

| コンポーネント | 単独性指標 | 根拠 |
|---|---|---|
| **Orchestra** | HIGH | 独立dir + 重複実装 = 長期開発 → 独立製品化検討 |
| **Relay** | HIGH | core_kernel/relay_core/ の独立dir |
| **Memory** | MEDIUM-HIGH | 独立テスト3種 + 他層への依存分離設計 |
| **PHI-OS** | MEDIUM | phios_integration/ = 後付け統合 → 独立性保有 |
| **Prism** | UNKNOWN | prism/ dir は存在するが公開doc不足 |

**重要な観察:**

- Orchestra / Relay は `core_kernel/` **直下**の独立ディレクトリ
- Memory / PHI-OS は**独立した設計仕様**を持つ
- これらは「コンポーネント化」段階ではなく、「**独立製品化の可能性を保持**」
  している段階であると解釈できる

---

## 4. PING / HOOK / Boundary / Bindingの公開証拠

### 4.1 PING（接続確認信号）（DOCUMENTED）

**観察対象:** `mocka_Movement` と `shadow_Movement` の並列実行

- README.md で明示的に定義
- Dual-path architecture として記述
- shadow_Movement = 独立検証経路

**推測（INFERRED）:** PING は各コンポーネント間の「健全性確認」
メカニズムとして機能していると推測されるが、具体実装は公開されていない。

### 4.2 HOOK（イベント注入）（DOCUMENTED）

**観察:** Civilization Loop の構造

```
Observation → Record → Incident → Recurrence → Prevention → Decision → Action → Audit
```

**観察:** 各ステップの間に**ファンクション実行の余地**（hook point）がある設計

**根拠:** README.md で「Incident」「Recurrence」「Prevention」が明示的に区分されており、
これらは**独立した処理ステップ**として実装可能な構造を示している。

### 4.3 Boundary（層間境界）（DOCUMENTED）

**BINDING_REGISTRY_v1.md より:**

| Institution | Gate | Role |
|---|---|---|
| MoCKA (core) | Module Gate | Core システム層 |
| Orchestra | Experiment Gate | コンポーネント層 |
| Relay | Experiment Gate | コンポーネント層 |
| Memory | Knowledge Gate | コンポーネント層 |
| PHI-OS | Event Gate | 制度執行層 |

**観察:** 各コンポーネントが**異なるGate**に割り当てられている
= **独立した承認経路**を持つ設計

### 4.4 Binding（接続状態）（DOCUMENTED）

**BINDING_REGISTRY_v1.md + BINDING_GAP_REPORT_v1.md より:**

| コンポーネント | Binding状態 | 意味 |
|---|---|---|
| orchestra/ | PARTIAL | 完全には接続されていない |
| orchestra_core/ | PARTIAL | 派生or代替実装 |
| relay_core/ | CONNECTED | 完全に接続済み |
| memory_core/ | CONNECTED | 完全に接続済み |
| phios_integration/ | CONNECTED | 統合層として接続済み |

**Gap統計（BINDING_GAP_REPORT_v1.md より）:**

- SHADOW: 11件（制度上の存在が未確認）
- ORPHAN: 15件（制度接続なし・孤立）
- DEPRECATED: 2件（廃止状態）
- VERSION CONFLICT: 6件（重複or分岐）
- INSTITUTION未所属: 4件
- Gate未登録: 7件
- **合計: 45件のGap**

**解釈（INFERRED）:** 45件のGapは、「**Binding が完全ではない**」ことを示す。
これは、「完成したシステム」ではなく「**進化型・後付けBinding可能な構造**」
であることの証拠。

---

## 5. Independent Product Potential（詳細検証）

### 5.1 Orchestra

**単独製品性の指標:**

| 要素 | 状態 | 根拠 |
|---|---|---|
| 単独ディレクトリ | YES | core_kernel/orchestra/ + orchestra_core/ |
| 独立エントリーポイント | PARTIAL | README に mocka-seal/mocka-loop などは記載されるが、Orchestra専用 CLI 記載なし |
| 独立テスト | UNKNOWN | 公開doc に記載なし |
| 独立ドキュメント | UNKNOWN | Orchestra専用の設計doc 公開なし |
| MoCKA への依存度 | HIGH | core_kernel/ 内に存在 = MoCKA core への強い依存 |
| 切り離し可能性 | MEDIUM | `phios_integration/` があるため、PHI-OS さえ独立させれば分離可能 |

**結論（INFERRED）:**
Orchestra は **独立製品への潜在性を保有** しているが、
現在のところ MoCKA core への依存が深い。
「単独製品として販売可能」というレベルではなく、
「**独立コンポーネント化の余地を残した設計**」段階。

### 5.2 Relay

**単独製品性の指標:**

| 要素 | 状態 | 根拠 |
|---|---|---|
| 単独ディレクトリ | YES | core_kernel/relay_core/ |
| 独立エントリーポイント | UNKNOWN | 公開doc に記載なし |
| 独立テスト | UNKNOWN | 公開doc に記載なし |
| 独立ドキュメント | UNKNOWN | Relay 専用doc 公開なし |
| MoCKA への依存度 | MEDIUM-HIGH | core_kernel/ 内だが、Event Gate を通じた独立性がある |
| 切り離し可能性 | MEDIUM-HIGH | Event Gate の仕様が明確であれば分離可能 |

**結論（INFERRED）:**
Relay は **Orchestra よりも独立性が高い** と推測される。
理由: BINDING_REGISTRY で CONNECTED 評価、且つ Event Gate という
明確な境界を持つため。

### 5.3 Memory

**単独製品性の指標:**

| 要素 | 状態 | 根拠 |
|---|---|---|
| 単独ディレクトリ | YES | core_kernel/memory_core/ + memory/ |
| 独立エントリーポイント | YES | memory_pipeline.py という単一window口 |
| 独立テスト | YES | 3種のテスト（integration, retrieval, consistency） |
| 独立ドキュメント | YES | MEMORY_LAYER.md (100行超) |
| MoCKA への依存度 | MEDIUM | 4層記憶の概念定義、Semantic/Decision との連携あり |
| 切り離し可能性 | HIGH | data/memory_store.json という独立ストレージ |

**結論（INFERRED）:**
Memory は **最も独立製品化に近い状態** にあると推測される。
理由: 独立ドキュメント・独立テスト・明確な API インタフェース・
独立ストレージを備えているため。

### 5.4 PHI-OS

**単独製品性の指標:**

| 要素 | 状態 | 根拠 |
|---|---|---|
| 単独ディレクトリ | YES | phi_os/ + phios_integration/ |
| 独立エントリーポイント | YES | Event Gate という制度層インタフェース |
| 独立テスト | UNKNOWN | 公開doc に記載なし |
| 独立ドキュメント | YES | PHI_OS_CONSTITUTION_v1.md |
| MoCKA への依存度 | PARADOX | 「MoCKA の制度執行機関」 = MoCKA に依存しているようにみえるが、実は「**制度カーネルの提供側**」 |
| 切り離し可能性 | UNKNOWN | 概念的には独立しているが、event_gate.py の実装形態により左右される |

**結論（INFERRED）:**
PHI-OS は **設計思想としては完全に独立**している。
PHI_OS_CONSTITUTION_v1.md で「唯一の制度執行機関」と定義され、
その上、「MoCKA がない場合でも成立する」ほどの抽象度で設計されている。

ただし、「単独製品として存在」するには、
Event Gate / Knowledge Gate などの **Gate 実装** を独立させる必要がある。

---

## 6. Gap / Deferred Binding（公開記録）

### 6.1 明示的なGap（DOCUMENTED）

**BINDING_GAP_REPORT_v1.md が示すGap:**

#### SHADOW（11件）
- governance/_chaos_tmp/ — Incident記録が制度登録なし
- mocka-extension/（重複存在）— どちらが正規か不明
- archive/_untracked_stash_* — 命名が「stash」だが制度意図不明
- backup/ — 目的・タイミングが制度上未定義
- OLD_FILES/ — 命名から推測だが公式扱いなし

**解釈:** これらは「制度上の意図が不明確な領域」。
つまり、「**まだBinding が完成していない領域**」を示す。

#### ORPHAN（15件）
- immutable/ — Immutableデータ保護を示唆するが制度登録なし
- ops/ — MoCKA/ops/ との関係不明
- shared/ — 複数システム共有か不明

**解釈:** 「**独立した独立プロジェクトが、MoCKA本体と未接続**」
の状態。逆に言えば、各々が**独立している可能性**を示唆。

#### DEPRECATED（2件）
- mocka_3/ vs mocka3/ — バージョン分岐、正規化未完了
- archive/ledger_old/ — ledger旧版

**解釈:** バージョン遷移の途上。
「**Phase移行**」の実装証跡。

#### VERSION CONFLICT（6件）
- orchestra/ vs orchestra_core/ — 同一機能の2実装並立
- phi_os/ vs knowledge-gate/ vs mocka-knowledge-gate/ — 3箇所に分散
- mocka-extension/（2箇所） — 重複存在

**解釈:** 「**長期開発による派生・分岐**」の証拠。
特に Orchestra の重複実装は、「**長期間にわたる進化**」
の痕跡。

### 6.2 Deferred Binding（推測される構造）（INFERRED）

**パターン1: 後付けBiding**

Example: phios_integration/

```
Timeline (推測):

Phase A: core_kernel/orchestra/, relay_core/, memory_core/ が先に独立開発
         ↓
Phase B: 「制度層が必要」という認識
         ↓
Phase C: phi_os/ が新規追加
         ↓
Phase D: phios_integration/ で既存Componentとの接続レイヤーを追加
```

**観察:** これは「**後付けBinding**」の典型的パターン。
つまり、各コンポーネントが**先に独立して存在**し、
後から統合レイヤーで binding されている。

**パターン2: Version Conflict の放置**

Example: orchestra/ vs orchestra_core/

```
推測Timeline:

v1時代: orchestra/ が実装される
         ↓
v2時代: 「改良が必要」との判断 → orchestra_core/ が平行開発
         ↓
現在: どちらを「正規」とするかが制度上未確定
         ↓
→ Binding が「PARTIAL」のまま
```

**観察:** このパターンは「**段階的な改良**」を示唆。
つまり、「破壊的な置換ではなく、平行運用による進化」。

### 6.3 未着手Binding（推測）（INFERRED）

**公開ドキュメントに記載がないため推測できない。**

ただし、BINDING_GAP_REPORT_v1.md の「修復提案」欄に以下の記載がある:

```
Orchestra: Version統合。orchestra/ を主実装、orchestra_core/ をARCHIVEまたはレガシーAdapterとして明示
Relay: Relay Institution所属を正式に登録
Memory: Knowledge Gate登録
PHI-OS: Gate権威をphi_os/ に一元化
```

**観察:** これらが「**推奨される次のBinding**」。
つまり、現在「PARTIAL」な状態から「CONNECTED」へ移行することが
次の段階である。

---

## 7. 時系列追跡

### 7.1 Git Commit Log より（DOCUMENTED）

**最新Phase:**
```
430fd7e 2026-08-11 Phase8-3: remove unintended record artifact
e60216c 2026-08-11 Phase8-3: align ExecutionOrchestrator with HAB contract
```

**直近の活動:**
```
2026-08-11 以降: 「auto sync」による自動同期が約60回
```

**解釈:**

- Phase8-3 が最新フェーズ（2026-08-11）
- その後の「auto sync」は**機械的な同期操作**（意図的な設計変更ではない）

### 7.2 Phase の推定進化（INFERRED）

公開ドキュメントには Phase 1〜8 の明示がされているが、
各Phaseの具体的な日付・内容は公開リポジトリに完全には記載されていない。

**推測可能な段階:**

| Phase | 推定内容 | 根拠 |
|---|---|---|
| Phase 1-3 | 基本制度構築 | Constitution 存在 |
| Phase 4 | コンポーネント化 | BINDING_REGISTRY v1 (2026-06-16) |
| Phase 5-2 | Event Integrity Framework | EVENT_INTEGRITY_v1.md 記載 |
| Phase 2-1 ~ 2-3 | Semantic / Decision / Memory Layers | README に「Phase 2-1」「Phase 2-2」「Phase 2-3」 記載 |
| Phase 3-1 ~ 3-2 | Self-Audit / Feedback Loops | README に記載 |
| Phase 4-1 | Self-Learning Kernel | README に記載 |
| Phase 8-3 | 最新（2026-08-11） | Git commit より |

**重要な観察:**

README.md を見ると、Phase番号が **時系列順ではなく、層ごとに並行して**
記載されている。これは、MoCKA が「**異なる層が同時進行で開発される**」
構造を持つことを示唆。

---

## 8. 「完成」の意味の変遷

### 8.1 Code Complete（実装完了）

**根拠:** README.md に以下が記載

- Semantic Layer: 実装完了
- Decision Layer: 実装完了
- Memory Layer: 実装完了
- Self-Audit Layer: 実装完了
- Feedback Loop: 実装完了
- Self-Learning Kernel: 実装完了

**観察:** ここでいう「完成」は「**実装が存在する**」という意味。
デプロイ・本運用ではなく、コード存在。

### 8.2 Test Complete（検証完了）

**根拠:** README.md に以下の test commands 記載

```bash
python memory/memory_integration_test.py
python memory/memory_retrieval_test.py
python memory/memory_consistency_test.py
```

**観察:** 各層が「**テスト可能な状態**」にある。
ただし、「全テストがPASS」という状態は公開ドキュメントでは明記されていない。

### 8.3 Design Complete（設計確定）

**根拠:** 独立した設計ドキュメントの存在

- MEMORY_LAYER.md
- DECISION_LAYER.md
- SEMANTIC_LAYER.md
- GATE_ARCHITECTURE_v1.md
- PHI_OS_CONSTITUTION_v1.md

**観察:** 「設計がドキュメント化され、公開されている」 = 「設計が確定状態」。

### 8.4 Component Complete（コンポーネント化完了）

**根拠:** core_kernel/ 内の独立ディレクトリ構造

```
core_kernel/orchestra/
core_kernel/relay_core/
core_kernel/memory_core/
core_kernel/phios_integration/
```

**観察:** 各機能が「**独立したコンポーネント**」として物理的に分離されている。

### 8.5 Binding Complete（接続完了）

**根拠:** BINDING_REGISTRY_v1.md で CONNECTED/PARTIAL/SHADOW/ORPHAN を区分

**実態:** 多くが「PARTIAL」であり、完全な binding はまだ。

**観察:** 「Binding Complete」ではなく「**Binding In Progress**」段階。

### 8.6 Runtime Complete（実行可能状態）

**根拠:** README.md の「Quick Start」コマンド

```bash
mocka-check        # Run and PASS
mocka-loop         # Run and complete 1 cycle
mocka-seal         # Seal and commit
```

**観察:** 「実行可能 = 実際に動く」という最小条件は満たされている。

### 8.7 Institutionalized（制度化完成）

**根拠:** PHI_OS_CONSTITUTION_v1.md の「RATIFIED v1」標記

**観察:** 制度として「正式に発効」している。

---

## 9. Snapshot としての 2026-08-17

### 9.1 現在地

| 層 | 状態 | Binding |
|---|---|---|
| 基本制度（Constitution） | ✓ COMPLETE | CONNECTED |
| Core Loop（mocka_Movement + shadow_Movement） | ✓ COMPLETE | CONNECTED |
| Governance Layer (GL1-7) | ✓ COMPLETE | CONNECTED |
| Semantic Layer | ✓ IMPLEMENTED | PARTIAL |
| Decision Layer | ✓ IMPLEMENTED | PARTIAL |
| Memory Layer | ✓ IMPLEMENTED | CONNECTED |
| Self-Audit Layer | ✓ IMPLEMENTED | PARTIAL |
| Feedback Loop | ✓ IMPLEMENTED | PARTIAL |
| Self-Learning Kernel | ✓ IMPLEMENTED | PARTIAL |
| Event Integrity Framework | ✓ IMPLEMENTED | CONNECTED |
| Orchestra | ✓ PARTIAL | PARTIAL |
| Relay | ✓ IMPLEMENTED | CONNECTED |
| PHI-OS | ✓ CONSTITUTION DEFINED | CONNECTED |

### 9.2 Gap の現存

- **制度未接続**: 45項目（BINDING_GAP_REPORT_v1.md）
- **Version Conflict**: 6項目（主に Orchestra の重複）
- **ORPHAN**: 15項目（孤立プロジェクト）
- **未登録**: 7項目（Gate未登録）

### 9.3 進行中の作業

**Git log より:**
- 最新: Phase8-3 (2026-08-11)
- 形式: ExecutionOrchestrator の HAB contract への alignment

---

## 10. 公開情報からは判断不能な領域

### 10.1 実装の詳細動作

以下について、公開ドキュメントに**具体的な実装は記載されていない**:

- shadow_Movement の実際の動作メカニズム
- Caliber の実測値スコアリング実装
- Drift detection の具体的アルゴリズム
- Memory Retriever の類似度計算ロジック

**判定:** UNKNOWN

### 10.2 運用状況・実績数値

以下について、公開ドキュメントに**数値記録がない**:

- 実際に処理されたイベント数
- Governance check の PASS/FAIL 率
- Shadow Movement の実際の稼働比率（「75%」という数字は公開説明だが、実測値ではない）
- Component ごとの Error rate

**判定:** UNKNOWN

### 10.3 内部インシデント履歴

BINDING_GAP_REPORT が「修復提案」を記載しているが、
「**なぜこのGapが発生したのか**」という根因は公開ドキュメントに記載されていない。

例:
- orchestra/ vs orchestra_core/ が並立している経緯
- Binding が PARTIAL のままである理由

**判定:** INFERRED only（推測不可）

### 10.4 将来計画

README に記載される次のPhase（9以上）について、
具体的な期限・実装計画は**公開リポジトリに記載されていない**。

**判定:** UNKNOWN

---

## 11. 仮説の検証結果

### **中心仮説A:**

> MoCKAは、最初から全機能を完成させて一つに結合するのではなく、
> 全体構図を形成しながら独立した構成要素を育て、
> 後からBindingする余地を残す進化型設計である。

**検証結果:** ✓ **STRONGLY SUPPORTED**

**根拠:**

1. **全体構図**: Civilization Loop, mocka_Movement + shadow_Movement が
   "最初から"（README.md で冒頭に記載）定義されている

2. **独立構成要素**: core_kernel/ 内に orchestra/, relay_core/, memory_core/
   が物理的に独立したディレクトリとして存在（現時点で実装完了）

3. **後付けBinding**: phios_integration/ の存在が、後付けBiding の
   実装例を示す

4. **Binding の余地**: BINDING_REGISTRY + BINDING_GAP で 45項目の
   未完成Bindingが記録されている

5. **Version Conflict の放置**: orchestra/ vs orchestra_core/ など、
   複数実装の並存は「段階的な進化」を示す

**結論:** 公開情報から、MoCKAが「**段階的コンポーネント化 → 後付けBinding**」
の設計戦略を採用していることが明らかに示されている。

---

### **中心仮説B:**

> Orchestra / Relay / Memory / PHI-OS は
> MoCKAの内部部品であるだけではなく、
> それぞれ単独製品として成立できる可能性を保持している。

**検証結果:** ✓ **PARTIALLY SUPPORTED（段階的）**

**根拠:**

| コンポーネント | 根拠 | 結論 |
|---|---|---|
| **Orchestra** | 独立dir + 重複実装 + 長期開発痕跡 | Independent Product Potential: MEDIUM |
| **Relay** | 独立dir + CONNECTED binding + Event Gate | Independent Product Potential: MEDIUM-HIGH |
| **Memory** | 独立dir + 独立doc + 独立test 3種 + 独立storage | Independent Product Potential: HIGH |
| **PHI-OS** | PHI_OS_CONSTITUTION_v1.md で独立定義 + Event Gate 仕様 | Independent Product Potential: MEDIUM (概念的には HIGH) |

**限定:**

- 「単独製品として販売できる」というレベルではなく、
  「**独立コンポーネント化の道筋が明確にある**」というレベル

- 各コンポーネントは現在のところ `core_kernel/` 内に存在し、
  完全な独立化（独立リポジトリ化等）はまだ進行していない

- Memory は最も独立製品化に近い状態（独立doc + 独立API）

**結論:** 仮説Bは「段階的には支持される」。ただし、
「**現在は独立製品ではなく、独立製品化の潜在性を保有**」
というレベルにとどまる。

---

## 12. 最終構造図（公開情報から見えるMoCKAの現在の姿）

```
┌─────────────────────────────────────────────────────────────────┐
│              MoCKA: Civilization Model v2026-08-17              │
└─────────────────────────────────────────────────────────────────┘

┌─ Foundation Layer ─────────────────────────────────────────────┐
│                                                                 │
│  mocka_Receptor (Single Entry Point)                           │
│         ↓                          ↓                            │
│  ┌─ infield          ┌─ outfield                              │
│  │ (internal         │ (external                              │
│  │  memory)          │  proof)                                │
│  └─                  └─                                       │
│         ↓                          ↓                            │
│  Civilization Loop                 Public Ledger               │
│  (mocka_Movement +                                             │
│   shadow_Movement)                                             │
└─────────────────────────────────────────────────────────────────┘

┌─ Governance Layer (GL1-7) ─────────────────────────────────────┐
│                                                                 │
│  GL1: Repository Grounding                                     │
│  GL2: Working Memory                                           │
│  GL3: Thinking Mode                                            │
│  GL4: Knowledge Mass                                           │
│  GL5: Consensus                                                │
│  GL6: Reasoning Governance                                     │
│  GL7: Execution Governance (Dry Run + Default Deny)           │
└─────────────────────────────────────────────────────────────────┘

┌─ Processing Layers (並行開発) ────────────────────────────────┐
│                                                                 │
│  ┌─ Semantic Layer (Phase 2-1)  ──────────┐                  │
│  │ Intent Classification                   │ PARTIAL Binding  │
│  └─────────────────────────────────────────┘                  │
│  ┌─ Decision Layer (Phase 2-2)   ──────────┐                  │
│  │ Action Selection / Risk Scoring          │ PARTIAL Binding  │
│  └─────────────────────────────────────────┘                  │
│  ┌─ Memory Layer (Phase 2-3)     ──────────┐                  │
│  │ Episodic / Semantic / Procedural / Skill │ CONNECTED        │
│  └─────────────────────────────────────────┘                  │
│  ┌─ Self-Audit Layer (Phase 3-1)  ────────┐                  │
│  │ Evaluation & Improvement Suggestions    │ PARTIAL Binding  │
│  └─────────────────────────────────────────┘                  │
│  ┌─ Feedback Loop (Phase 3-2)    ──────────┐                  │
│  │ Weight Adjustment & Adaptive Decision   │ PARTIAL Binding  │
│  └─────────────────────────────────────────┘                  │
│  ┌─ Self-Learning Kernel (Phase 4-1) ────┐                  │
│  │ Weight State Management & Rollback     │ PARTIAL Binding  │
│  └─────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘

┌─ Component Layer (core_kernel/) ────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Orchestra    │  │ Relay        │  │ Memory       │        │
│  │ core/        │  │ core/        │  │ core/        │        │
│  │ PARTIAL      │  │ CONNECTED    │  │ CONNECTED    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ PHI-OS       │  │ Prism        │  │ [Others]     │        │
│  │ integration/ │  │ core/        │  │              │        │
│  │ CONNECTED    │  │ UNKNOWN      │  │ PARTIAL      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘

┌─ Institutional Layer (PHI-OS) ────────────────────────────────┐
│                                                                 │
│  ┌─ Event Gate        (Who can write events?)                 │
│  ├─ Knowledge Gate    (What can be learned?)                  │
│  ├─ Module Gate       (What modules exist?)                   │
│  ├─ Document Gate     (What is documented?)                   │
│  ├─ Release Gate      (What can be released?)                 │
│  └─ Experiment Gate   (What can be tested?)                   │
│                                                                 │
│  ┌─ Binding Registry (45 Gaps / PARTIAL status)              │
│  └─ Gap Report (Version Conflict × 6 / SHADOW × 11)          │
└─────────────────────────────────────────────────────────────────┘

Legend:
 CONNECTED: 制度的に完全に接続
 PARTIAL:   部分的に接続
 SHADOW:    制度上の意図が不明確
 ORPHAN:    制度接続なし・孤立
```

---

## 結論

### **MoCKA の現在地（2026-08-17）**

1. **設計思想**: 「AIではなく文明モデル」というコア思想は
   すべての公開ドキュメントで一貫している

2. **進化戦略**: 全体構図を先に形成し、後付けBiding を前提とした
   段階的コンポーネント化戦略を採用している

3. **実装状況**: 多くのコンポーネント（Semantic, Decision, Memory,
   Self-Audit, Feedback, Learning）は「実装完了」だが、
   「Binding」「Integration」は「PARTIAL」のまま

4. **独立性**: Orchestra/Relay/Memory/PHI-OS は単独コンポーネント化
   の基盤を持つが、現在は「内部部品」として MoCKA に統合されている

5. **未完成性**: 45項目のGapが公式に記録されており、
   MoCKA自体が「完成したシステム」ではなく
   「継続進化するシステム」として設計されている

6. **制度化**: PHI-OS Constitution により、制度的な枠組みは
   すでに確定状ている

### **仮説の検証**

**仮説A（進化型設計）**: ✓ CONFIRMED
- 公開情報から、段階的コンポーネント化 → 後付けBinding の
  設計戦略が明確に示されている

**仮説B（独立製品の可能性）**: ✓ PARTIALLY CONFIRMED
- 各コンポーネント（特にMemory）は独立製品化の潜在性を保有
- ただし、現在は「潜在性」段階であり、「単独製品」ではない
- Binding Architecture の完成により、独立化が可能になる見通し

### **限定と注釈**

- 本ドキュメントは**公開リポジトリとドキュメント のみ**から再構成
- 内部システム（Decision Ledger, essence_auto_updater, MCP server等）
  の実装詳細は公開情報の範囲外
- Phase移行の具体的な日付・契機は推測ベース
- Gap修復の具体的な実装計画は公開情報に記載されていない

---

**文書作成日:** 2026-08-17  
**調査範囲:** 公開 GitHub リポジトリ・ドキュメント・Git history のみ  
**著者:** MoCKA Evolutionary Analysis (Public Information Only)

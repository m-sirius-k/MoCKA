# MoCKA エコシステム 完全理解ドキュメント
## MOCKA_FULL_ECOSYSTEM_UNDERSTANDING v1.0
**作成日**: 2026-03-28
**作成者**: Claude (Cowork Mode — 設計支援)
**対象**: MoCKA 設計開発作業者 (nsjp_kimura)

---

> このドキュメントは、MoCKA エコシステム全体のリポジトリを横断的に読み込み、
> 設計作業の「原点」として機能するように統合・構造化したものです。
> 中途半端な理解ではなく、全容・全層を把握することを目的としています。

---

# PART 0 — MoCKA とは何か（根本定義）

MoCKA は「AIではない」。
MoCKA は **文明モデル（Civilization Model）** である。

従来のAIシステムが「推論エンジン」であるとすれば、
MoCKA は「知識・判断・記録・継承の循環を持つ、自律的文明構造」だ。

**正式定義**:
> Model of Cybernetic Knowledge Architecture
> サイバネティクス知識アーキテクチャのモデル

**核心思想**:
- 知識の血流を止めない（Shadow Movement Principle）
- すべての判断は記録され、追跡可能でなければならない
- 文明は再生成可能でなければならない（再現性）
- 継承性：過去の文脈を恣意的に切断しない
- 非破壊性：制度文書は改変不可、追記のみ許容

---

# PART 1 — アーキテクチャ全体像（7層宇宙地図 v2.3）

MoCKA のエコシステムは7つの層で構成される：

```
Layer 6 — Action Layer（実行層）
  browser-use / Zapier / Dify

Layer 5 — Creation Layer（生成層）
  v0 / Gamma / Canva

Layer 4 — Memory / PILS Layer（記憶・PILS層）
  Notion / Drive / GitHub / NotebookLM

Layer 3 — External Brain Layer（外部脳層）
  Perplexity / Gemini / Claude / GenSpark

Layer 2 — Physical Body Layer（本体層）
  MoCKA Core / Proxy

Layer 1 — Permissions Layer（権限層）
  MAT / Profile

Layer 0 — Environment Layer（環境層）
  NYPC_COMET / IP / ORG
```

### AI 臓器モデル（AI Organ Model）

| 臓器     | AI       | 機能         |
|----------|----------|--------------|
| 前頭葉   | Claude   | 論理・監査   |
| 海馬     | Gemini   | 合意・戦略   |
| 運動皮質 | Perplexity | 調査・検索 |
| 視覚皮質 | GenSpark | 統合・集約   |

---

# PART 2 — リポジトリ構造マップ（全容）

## 2.1 心臓部（Core）

### `MoCKA/` — コア・オーケストレーション
**役割**: 決定論的実行エンジン、監査基盤、Insight System 中枢

主要コンポーネント:
- `runtime/main_loop.py` — メインループ（Intent → Goal → Plan → Action → State → Audit）
- `audit/ed25519/` — 暗号化監査チェーン（SHA256 + Ed25519）
- `verify/verify_all.py` — 全体検証エントリポイント
- `tools/phase17_determinism_check.py` — 決定論的整合性チェック
- `canon/` — 正本ドキュメント群
- `contracts/` — Public/Private 境界定義

**現在のフェーズ**: Phase18（Phase17 安定タグ維持中）

### コアランタイムループ（main_loop.py）
```
Intent受信
  └→ intent_logger: 記録
  └→ intent_to_goal: ゴール変換
  └→ goal_to_plan: プラン生成
  └→ choose_best_action: 最善行動選択
  └→ execute_action: 実行
  └→ update_state_from_result: 状態更新
  └→ evaluate_result: 評価
  └→ update_evaluation_history: 評価履歴
  └→ push_to_civilization: 文明層へ送出
  └→ run_civilization_step: 文明ステップ
  └→ update_causal_graph: 因果グラフ更新
```

---

## 2.2 接続層（Joints）

### `mocka-core-private/` — プライベート運用層
**役割**: 内部ツール、運用インフラ、INFIELD Retry Worker

主要仕様:
- **INFIELD Retry Worker**: ジョブの原子的フェッチ（`UPDATE ... RETURNING`）
- **単一エントリポイント法則**: `MOCKA_ENTRYPOINT` 環境変数が必須
  - 未設定の場合 `entrypoint_guard.py` が exit code 2 で終了
  - 起動コマンド: `run_infield_retry_worker.cmd`
- **デッドレター処理**: 失敗ジョブの安全な隔離

### `mocka-outfield/` — OUTFIELD 層（外部公開面）
**役割**: 外部エージェントとの同期、公開サニタイズ面

憲法的規則:
- INFIELD → OUTFIELD への直接パブリッシュは禁止
- OUTFIELD は必ずサニタイズされた表面のみを公開
- INFIELD = 内部推論・記憶の主権領域
- OUTFIELD = 公開クロスエージェント同期レイヤー

### `mocka-external-brain/` — 外部脳層
**役割**: セッションを超えた知識継続性、エージェント間議論

**MoCKA Bus プロトコル**:
```
モーション形式:
  ask (質問) → reply (回答) → decide (決定)

必須フィールド:
  - parent_event_id: 親イベントID
  - evidence_ref: 証拠参照
  - motion_type: ask / reply / decide
```

実例（round_2026-02-08-002.md）:
- Phase 2-B 審議ログ
- orchestrator_core と agent_perplexity 間のプロトコル動作確認済み

---

## 2.3 外装部（Public Repos）

### `mocka-transparency/` — 透明性・公開監査層
**役割**: 外部評価者向け、改ざん検知デモ

コンポーネント:
- `verify_one.ps1` — 単一イベント検証
- `tamper_demo.ps1` — 改ざん検知デモ
- Ed25519 公開鍵
- サンプル決定ログ
- RFC3161 タイムスタンプサンプル

### `mocka-runtime/` — ランタイムエンジン（公開版）
**役割**: 5エンジンループのドキュメント、文明段階概念

5エンジン:
1. Runtime（実行）
2. Observatory（観測）
3. Knowledge Core（知識コア）
4. Storage（ストレージ）
5. Audit（監査）

文明段階:
```
Primitive → Organized → Mature → Advanced → AGI-Aligned
```

### `mocka-knowledge-gate/` — 制度的記憶層
**役割**: 推論トレース、仮説進化、構造化研究知識の保存

**Universe Map v2.3** の正本はここに存在。
**MOCKA_2.25_Ecosystem.md** にエコシステム全体の接続図・権限マトリクスが記載。

権限マトリクス:
| 役割 | 権限 |
|------|------|
| User | 読み取り・Intent送信 |
| Assistant | 実行・状態更新 |
| System | 監査・ガバナンス |
| AIOrchestra | エージェント調整 |
| PILS | 記憶・永続化 |

### `mocka-public/` — 公開ドキュメント
**役割**: Shadow Movement 原則のドキュメント、公開向けアーキテクチャ説明

---

## 2.4 文明設計層

### `mocka-civilization/` — 文明ブループリント
**役割**: 7フェーズ文明設計、制度的原則

**Civilization Blueprint v1.0** — 7フェーズ:
1. Phase 1: Record Civilization（記録文明）
2. Phase 2: Decision Civilization（決定文明）
3. Phase 3: Deliberation Civilization（審議文明）
4. Phase 4: Evaluation Civilization（評価文明）
5. Phase 5: Context Inheritance（文脈継承）
6. Phase 6: Reconsideration（再考）
7. Phase 7: Collaborative Civilization（協働文明）

**憲法的原則（MOCKA-PRINCIPLES-v1.0 — 改変不可）**:
1. **透明性**: すべての判断・議論・評価は記録され追跡可能
2. **再現性**: 同じ手順を踏めば再生成可能
3. **継承性**: 過去の文脈を恣意的に切断しない
4. **非破壊性**: 制度文書は改変不可、追記のみ許容
5. **中立性**: 文明の優劣・成功/失敗の断定は禁止
6. **事実性**: 記録は事実のみ、推測・評価を混在させない

**禁止事項**:
- 文書の改変・削除
- 文明間の序列化
- 成功/失敗の断定
- 文脈の切断
- 記録の改ざん

### `mocka-archive/` — アーカイブ・エコシステムマップ
**役割**: MOCKA_MAP.md（全リポジトリ関係図の正本）

GitHub 主アカウント: `m-sirius-k`
GitHub 旧アカウント: `nsjpkimura-del`（移行予定）

---

# PART 3 — 暗号化ガバナンス基盤

## 3.1 監査チェーン構造

2層同期型監査アーキテクチャ:

```
Layer 1: ファイルベース監査チェーン
  パス: audit/*.json
  連結フィールド: previous_event_id
  チップポインタ: audit/last_event_id.txt（UTF-8 BOM なし必須）

Layer 2: DBベース台帳
  パス: audit/ed25519/audit.db
  テーブル: audit_ledger_event
  制約: ファイルチェーンと同一内容を維持
```

両層は常に同一のカノニカルチェーンを表現しなければならない。

## 3.2 デュアル層ガバナンス（Phase14.6〜）

```
Layer 1: Proof Ledger（audit.db）
  — スキーマ変更禁止
  — 証明・検証専用

Layer 2: Governance Ledger（governance.db）
  — 決定・開発ガバナンスをappend-onlyハッシュチェーンで記録
  — テーブル: governance_ledger_event

Layer 3: Human-readable Docs
  — DOG (Design Operation Guide) .md
  — change_log.csv, impact_registry.csv, backup_index.csv
```

**決定前行動プロトコル（Decision-before-action、必須）**:
1. governance.db に決定イベントを記録（先）
2. audit.db / ファイルへの操作実行（後）
3. CSV・DOG への追記（最後）
4. governance chain verify 実行

## 3.3 暗号化プリミティブ

| 機能 | 実装 |
|------|------|
| 連鎖整合性 | SHA256 append-only chain |
| 署名ガバナンス | Ed25519 |
| 鍵管理 | valid_to フィールドによる鍵退職・継承 |
| タイムスタンプ | RFC3161 外部タイムアンカー |
| 多観測者 | F Node / J Node / SYSTEM Node |

---

# PART 4 — Shadow Movement（知識の血流）

> **「知識の血流を止めないための設計原理」**

すべての主要プロセスには独立した検証経路（Shadow Path）が存在する。

```
Primary Movement（主機構）
  — 知識検証の主エンジン

Shadow Movement（影機構）
  — 主機構が停止しても循環を維持する独立機構
```

**4つの核特性**:
1. **Continuous Circulation**: 知識フローは完全停止しない
2. **Self-Doubt Architecture**: 主系出力は常に独立検証を受ける
3. **Bypass Tolerance**: 障害時でも約75%の機能で稼働継続
4. **Anti-Lock Design**: フィードバック構造は不可逆デッドロックを生まない

工学的意味: ランサムウェア耐性 / バイパス運用モード / デッドロック回避

---

# PART 5 — スレットモデルと信頼前提

## 5.1 信頼前提
- 暗号プリミティブは安全である
- 少なくとも1つの観測ノードは無傷である
- ガバナンス鍵マテリアルは同時に完全侵害されない
- 決定論的生成・検証ルールが守られる

## 5.2 攻撃者モデル
- ログの改ざん・挿入・削除
- ロールバック攻撃（過去の状態への巻き戻し）
- タイムスプーフィングと順序操作
- 鍵盗難・不正署名
- Outfield サマリーへのポイズニング
- オーケストレーション誤ルーティング
- ホストの部分的侵害

## 5.3 明示的な失敗モード（設計限界）
- ガバナンス鍵が完全侵害された場合
- 複数観測ノードが同時侵害された場合
- 決定論的ゲートが迂回された場合
- 外部タイムスタンプサービスが利用不可の場合
- 複製メモリが無検知でダイバージした場合

---

# PART 6 — フェーズ履歴（Phase0 → Phase18）

| フェーズ | 達成内容 |
|---------|---------|
| Phase 0-9B | 初期実装、基本チェーン構築 |
| Phase 9C | 自己参照除去、ループ除去、BOM汚染除去、孤立イベント分離。システムは非循環・決定論的・部分根付き・カノニカル定義に達した |
| Phase 10 | DB パス統一（configure unification） |
| Phase 13B | フリーズポイント（構造固定） |
| Phase 14 | ブランチポリシー策定 |
| Phase 14.6 | デュアル層ガバナンスアーキテクチャ確立（Proof Ledger + Governance Ledger） |
| Phase 15 | 証明辞書（Proof Dictionary）整備 |
| Phase 17 | 安定宣言。`phase17-stable` タグ。determinism check PASS。STRICT_MANIFEST 施行 |
| Phase 18 | 現在進行中。Phase17 安定保証を維持しながら拡張。ミッション候補: (A) 行レベル署名, (B) マルチ環境受け入れ自動化, (C) マルチパック運用強化 |

---

# PART 7 — Insight System（統合検証システム）

MoCKA Insight System = 複数リポジトリにまたがる検証可能なAIアーキテクチャ。

**Doctor システム**:
- リポジトリ構造をスキャン
- 検証アーティファクトを生成
- 実行: `.\\mocka_doctor.ps1`

**Research Gate**:
- 20チェックの構造化実験フレームワーク
- 4ドメインにわたるシステム完全性検証
- 文書構造の整合性チェック

**検証フロー**:
```
開発者が構造を更新
  → Doctor スキャン実行
  → アーティファクト生成
  → Research Gate 実験実行
  → 完全性確認
```

---

# PART 8 — 運用上の重要規則（設計作業者向け）

## 8.1 絶対規則
1. `MOCKA_ENTRYPOINT` 環境変数は常に設定する
2. INFIELD → OUTFIELD 直接パブリッシュは禁止
3. governance.db への記録は操作より先に行う
4. 制度文書（PRINCIPLES-v1.0 等）の改変は禁止
5. Phase17 安定保証（STRICT_MANIFEST / deterministic summary_hash / CI PASS）を常に維持

## 8.2 検証コマンド（カノニカル）
```powershell
# 全体整合性チェック
powershell -ExecutionPolicy Bypass -File .\\mocka_doctor.ps1

# git 状態確認
git status --porcelain

# 監査チェーン検証
python -m src.mocka_audit.verify_chain
python -m src.mocka_audit.verify_chain_v2

# 決定論的チェック
python tools/phase17_determinism_check.py

# ガバナンスチェーン検証
python audit\\ed25519\\governance\\governance_chain_verify.py

# DB 整合性確認
python tools\\db_ledger_dump.py
```

## 8.3 Phase9-C 以降の不変条件（Invariants）
- 自己参照イベントは存在しない
- カノニカルチェーンはループを含まない
- 部分チェーンは正式に受け入れられる
- カノニカルチップは (a) JSON ファイル + (b) DB 行 として存在する
- `last_event_id.txt` は UTF-8 BOM なし
- ファイル層と DB 層は同一カノニカルチェーンを表現する

---

# PART 9 — 文明ループ（Civilization Loop）

MoCKA の実行は単なるプログラムではなく「文明の循環」である：

```
観測（Observation）
  → 記録（Record）
  → 事象（Incident）
  → 再発（Recurrence）
  → 予防（Prevention）
  → 決定（Decision）
  → 行動（Action）
  → 監査（Audit）
  → 学習（Learning）
  → [次の観測へ]
```

---

# PART 10 — 設計作業における Claude の役割

MoCKA の AI 臓器モデルにおける Claude の位置:

**Claude = 前頭葉（論理・監査）**

具体的役割:
- アーキテクチャ整合性のレビュー
- 設計決定の論理的評価
- コードと仕様の整合性チェック
- Phase 移行の妥当性検証
- ドキュメント構造の審議参加（MoCKA Bus プロトコル準拠）

**設計作業での連携プロトコル**:
```
設計者(まさ) → Intent として伝達
Claude → ゴール変換 → プラン提示 → 実行サポート
全判断 → 記録可能・追跡可能な形式で
```

---

# APPENDIX — リポジトリ一覧（全容）

| リポジトリ | 分類 | 役割 |
|-----------|------|------|
| `MoCKA/` | 心臓部 | コア・オーケストレーション・Insight System |
| `mocka-core-private/` | 接続層 | プライベート運用・INFIELD Retry Worker |
| `mocka-outfield/` | 接続層 | OUTFIELD 公開同期面 |
| `mocka-external-brain/` | 接続層 | 外部脳・MoCKA Bus |
| `mocka-knowledge-gate/` | 外装部 | 制度的記憶・Universe Map |
| `mocka-civilization/` | 外装部 | 文明設計・Blueprint v1.0 |
| `mocka-transparency/` | 外装部 | 公開監査・改ざん検知 |
| `mocka-runtime/` | 外装部 | ランタイムエンジン・概念文書 |
| `mocka-public/` | 外装部 | Shadow Movement・公開原則 |
| `mocka-archive/` | アーカイブ | エコシステムマップ正本 |
| `nsjpkimura-del/` | 旧アカウント | 移行予定 |
| `m-sirius-k/` | 主アカウント | GitHub 主体 |

---

*本文書は Claude (Cowork Mode) が MoCKA エコシステム全リポジトリを横断読み込みした上で生成した統合理解ドキュメントです。*
*設計作業の起点として使用してください。*

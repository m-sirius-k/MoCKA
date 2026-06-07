# PR-OS / SEO-OS マスター計画書 v1.0
**MoCKA Knowledge Distribution Layer — 設計・構築指示書**
作成日: 2026-06-06 | ステータス: Draft | 承認者: きむら博士

---

## 0. 定義と位置づけ

| 層 | 名称 | 役割 |
|----|------|------|
| 上位 | MoCKA Core | 知識の生成・蓄積・ガバナンス |
| 中位 | **PR-OS** | 知識の品質保証・原本確定・配信管理 |
| 下位 | Output Adapters | 各媒体への変換・投稿・公開 |

MoCKAが「知識を生むOS」、PR-OSが「知識を社会へ循環させるOS」。
生成と配信は分離する。責務の混濁を防ぐため。

---

## 1. 基本原則

```
人間の言葉（断片・メモ・既存文書・日々の積み重ね）
        ↓
    [AI Gate] — Caliber内処理
    校正・整合性チェック・最適化・品質確定
        ↓
        原本 (Confirmed Knowledge Source)
        インデックスIDで管理
        ↓
    [PR-OS Command Center]
    スケジュール・変換指示・公開管理
        ↓
    [Output Adapters]
    WordPress / X / Instagram / Facebook / GitHub Pages / Newsletter
```

---

## 2. システム全体構成

### 2.1 レイヤー定義

```
Layer 0: Input
  - 手書きメモ・チャット断片
  - 既存HTML/TXT/MD
  - Git更新情報
  - 開発日誌・研究記録

Layer 1: AI Gate (Caliber内)
  - 校正エンジン
  - 整合性チェック（MoCKA蓄積知識と照合）
  - 最適化・補完
  - 原本確定 → KS_NNN発番

Layer 2: Knowledge Store
  - 原本アーカイブ（インデックス管理）
  - バージョン履歴
  - タグ・カテゴリ・関連リンク
  - 公開ステータス管理

Layer 3: PR-OS Command Center
  - 全媒体の公開状況ダッシュボード
  - スケジュール管理
  - 変換ジョブ管理
  - ヘルスチェック（TSI準拠）
  - Google Analytics連携

Layer 4: Output Adapters
  - OA-001: WordPress
  - OA-002: X (Twitter)
  - OA-003: Instagram
  - OA-004: Facebook
  - OA-005: GitHub Pages
  - OA-006: Newsletter
  - OA-NNN: 拡張可能
```

---

## 3. 原本管理仕様（Knowledge Store）

### 3.1 インデックス体系

```
KS_NNN
例: KS_001, KS_002 ...
```

### 3.2 原本レコード構造

```json
{
  "id": "KS_001",
  "title": "タイトル",
  "created_at": "2026-06-06T10:00:00Z",
  "confirmed_at": "2026-06-06T10:15:00Z",
  "status": "confirmed",
  "tags": ["tag1", "tag2"],
  "category": "development",
  "source_type": "manual_input",
  "ai_gate_log": {
    "score": 0.95,
    "corrections": 3,
    "integrity_pass": true
  },
  "publish_status": {
    "wordpress": "published",
    "x": "scheduled",
    "instagram": "pending",
    "github_pages": "not_set"
  },
  "files": {
    "original": "draft/KS_NNN_raw.txt",
    "confirmed": "confirmed/KS_NNN.md",
    "wordpress": "confirmed/KS_NNN_wp.html",
    "x_post": "confirmed/KS_NNN_x.txt"
  }
}
```

---

## 4. AI Gate 仕様（Caliber内処理）

### 4.1 処理フロー

```
入力受付
  ↓
前処理（文字コード統一・改行正規化）
  ↓
校正エンジン（誤字脱字・表記統一）
  ↓
整合性チェック（MoCKA蓄積知識と矛盾検出）
  ↓
最適化（構造化・見出し・要約自動生成）
  ↓
スコアリング（品質スコア 0.0〜1.0）
  ↓
確定判定（スコア閾値 0.8以上 → 自動確定）
  ↓
KS_NNN発番 → Knowledge Storeへ格納
```

### 4.2 品質スコア基準

| スコア | 判定 | 処理 |
|--------|------|------|
| 0.9〜1.0 | 優良 | 自動確定 |
| 0.8〜0.9 | 良好 | 自動確定（ログ記録） |
| 0.6〜0.8 | 要確認 | きむら博士へ通知 → 手動承認 |
| 0.6未満 | 要修正 | ドラフト差し戻し |

---

## 5. Command Center 仕様

### 5.1 機能一覧

| 機能 | 説明 |
|------|------|
| Knowledge Board | 全KSの一覧・ステータス表示 |
| Publish Manager | 媒体別公開状況・予約管理 |
| Adapter Health | 各OAの接続状態・エラー監視 |
| GA Dashboard | Google Analytics主要指標 |
| TSI Monitor | 出先変更管理・ヘルスチェック |
| AI Gate Queue | 校正待ち・処理中・完了一覧 |
| Alert Panel | エラー・警告・通知 |

---

## 6. Output Adapter 仕様（共通インターフェース）

```python
class OutputAdapter:
    def convert(self, ks_record) -> str:
        """原本を媒体別フォーマットに変換"""
        pass

    def publish(self, converted_content) -> dict:
        """変換済みコンテンツを投稿"""
        pass

    def schedule(self, ks_id, publish_at) -> dict:
        """予約投稿登録"""
        pass

    def health_check(self) -> dict:
        """接続・状態確認"""
        pass

    def get_analytics(self) -> dict:
        """投稿後パフォーマンス取得"""
        pass
```

---

## 7. MoCKAとの統合ポイント

| MoCKA側 | 接続 | PR-OS側 |
|---------|------|---------|
| mocka_write_event | → | AI Gate受付ログ |
| mocka_add_todo | → | 公開スケジュール登録 |
| MoCKA Caliber | → | 品質スコア・整合性DB |
| mocka_events.db | ← | 公開後フィードバック記録 |
| Command Center | ← | PR-OS Command Center |

---

## 8. 実装フェーズ計画

### Phase 1 — 骨格（MVP）
- [ ] フォルダ構造作成 ← **完了 2026-06-06**
- [ ] KSインデックス設計・実装
- [ ] AI Gate（基本校正）実装
- [ ] WordPress Adapter実装
- [ ] Command Center（基本UI）作成

### Phase 2 — 拡張配信
- [ ] X (Twitter) Adapter
- [ ] Instagram Adapter
- [ ] 予約投稿スケジューラー

### Phase 3 — 分析・最適化
- [ ] Google Analytics連携
- [ ] TSIヘルスモニター
- [ ] AI Rewriter（反応ベース改善提案）

### Phase 4 — 完全統合
- [ ] GitHub Pages Adapter
- [ ] Newsletter Adapter
- [ ] MoCKA Command Centerとの統合

---

## 9. 命名規則

| 項目 | 規則 | 例 |
|------|------|-----|
| 知識ソース | KS_NNN | KS_001 |
| 原本ファイル | KS_NNN.md | KS_001.md |
| 変換ファイル | KS_NNN_{adapter}.{ext} | KS_001_wp.html |
| 公開ログ | PUB_NNN_{adapter}_{date} | PUB_001_wp_20260606 |
| エラーログ | ERR_{adapter}_{timestamp} | ERR_wp_20260606T1000 |

---

*本文書はMoCKA PlanningCaliber管理下。変更はCHANGE_START/CHANGE_DONEイベントで記録すること。*

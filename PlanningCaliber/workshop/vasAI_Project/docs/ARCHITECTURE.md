# vasAI Architecture

## 概要

**vasAI** は企業向けAI統治基盤（AI Activity Recording & Governance Platform）。
MoCKAの設計思想を圧縮・軽量化し、企業が即座に導入できる形にした。

## 3層の棲み分け

```
MoCKA  → 研究機関・軍需・大規模組織
vasAI  → 企業向け標準仕様（本システム）
PHI-OS → 個人向け民生運用核
```

## 2心臓アーキテクチャ

```
┌─────────────────────────────────────────┐
│  MoCKAMovement（第1の心臓）             │
│  8ステージ: OBS→REC→INC→REC2→         │
│            PRE→DEC→ACT→AUD             │
├─────────────────────────────────────────┤
│  ShadowMovement（第2の心臓）            │
│  ミラーリング / 縮退運用（75%保証）     │
│  5ステージ: INC→REC2→PRE→DEC→ACT      │
└─────────────────────────────────────────┘
```

## コンポーネント

| コンポーネント | 役割 |
|---|---|
| `core/event_store.py` | append-only SQLite、SHA-256ハッシュチェーン |
| `core/artifact_schema.py` | 共通Artifactスキーマ |
| `core/audit_chain.py` | HMAC-SHA256署名連鎖 |
| `core/governance.py` | Auto-Gate + Human Gate |
| `movement/mocka_movement.py` | 第1の心臓 |
| `movement/shadow_movement.py` | 第2の心臓 |
| `caliber/base_caliber.py` | 企業拡張インターフェース |
| `api/app.py` | REST API（port 6000） |
| `dashboard/index.html` | COMMAND CENTER UI |
| `sdk/vasai/client.py` | 企業向けSDK |

## 情報フロー

```
社内イントラ
  → caliber.receive_from_intranet()
  → caliber.classify_event()
  → vasAI core (event_store)
  → shadow_movement.mirror()
  → governance.process()
  → vasAI core → 監査ログ
  → caliber.format_for_intranet()
  → 社内イントラ（結果注入）
```

## 設計哲学

- **AIを信じるな、システムで縛れ**
- **記録なき作業は存在しない**
- append-only: 過去の改ざんは構造上不可能
- HMAC署名連鎖: 外部からの改ざんを検知
- 2心臓: 単一障害点なし

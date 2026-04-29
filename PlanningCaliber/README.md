# planningcaliber

MoCKAのcaliber開発・実験・設計管理スペース。

## ディレクトリ構成

```
planningcaliber/
├── workshop/           # 作業スペース（実験・プロトタイプ）
│   ├── phl_os/         # PHL-OS caliber設計資料
│   └── needle_eye_project/  # Needle Eye実験（完了）
├── candidates/         # caliber候補（設計中・評価待ち）
├── specs/              # 仕様書（確定済みcaliberの設計書）
└── Experiment_v2.0/    # 実験v2.0データ（アーカイブ）
    ├── data_raw/
    ├── essence_out/
    ├── logs/
    └── refining_engine/
```

## 運用ルール

- `workshop/` — 試作・実験中のcaliberはここで開発する
- `candidates/` — workshopで実証済み・本体統合を検討中のものを移動
- `specs/` — 本体統合済みcaliberの設計書・仕様書を配置
- `Experiment_v2.0/` — 過去実験データ。読み取り専用アーカイブ

## 現在稼働中のcaliber（本体統合済み）

| caliber | ポート | 状態 |
|---------|--------|------|
| mocka_caliber_server.py | 5679 | ✅ 稼働中 |
| PHL-OS v2 | 5679/phl/* | ✅ 稼働中 |
| pattern_engine_v2 | 5679/pattern/* | ✅ 稼働中 |

## workshop/phl_os/

PHL-OS（Persistent History Layer Operating System）の設計資料。

- v1: モジュール選択・記録（完了）
- v2: モジュール実行接続・system_prefix付与（完了 2026-04-29）
- v3: 予定（重み付きスコアリング・COMMAND CENTER連携）

## 更新履歴

- 2026-04-29: ディレクトリ構造整備（TODO_005完了）
- 2026-04-04: 初期構造作成

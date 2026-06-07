# PR-OS — Knowledge Distribution Layer

MoCKAが「知識を生むOS」、PR-OSが「知識を社会へ循環させるOS」。

## 構成

| フォルダ | 役割 |
|----------|------|
| `ai_gate/` | 校正・品質保証エンジン（Caliber内処理） |
| `command_center/` | 全媒体の公開状況ダッシュボード |
| `knowledge_store/` | 原本アーカイブ（KS_NNN管理） |
| `adapters/` | Output Adapters（WordPress/X/Instagram等） |
| `scheduler/` | 予約配信キュー管理 |
| `analytics/` | Google Analytics連携 |
| `logs/` | 公開・エラーログ |

## 設計書

→ [PROS-DESIGN.md](PROS-DESIGN.md)

## フェーズ

- **Phase 1 (MVP):** 原本管理 + WordPress出力
- **Phase 2:** SNS系Adapter追加
- **Phase 3:** 分析・最適化
- **Phase 4:** MoCKA完全統合

---
*管理: MoCKA PlanningCaliber | 変更はCHANGE_START/CHANGE_DONEイベントで記録*

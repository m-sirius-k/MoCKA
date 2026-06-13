# Governance Layer v1.1 — Baseline

MoCKA 3.0 における公式品質基準（Baseline）。
GL1〜GL7（Governance Layer 1-7）の監査・Dogfooding・異常系検証が
完了し、品質保証基盤として固定された状態を指す。

## Baseline識別情報

| 項目 | 値 |
|---|---|
| Version | Governance Layer v1.1 |
| Commit | `e35724b97b7abcdc68ce5df5574537581faf0dfb` |
| Event | `E20260613_067` |
| 監査報告書 | [structural/GL_AUDIT_REPORT.md](structural/GL_AUDIT_REPORT.md) |
| 総合判定 | PASS |

## 保証範囲

- GL1 Repository Grounding
- GL2 Working Memory
- GL3 Thinking Mode（単語境界キーワード判定）
- GL4 Knowledge Mass
- GL5 Consensus
- GL6 Reasoning Governance（Pre-Answer ChecklistがDecision.allowedに反映）
- GL7 Execution Governance（READ_ONLY_TOOLS以外はDefault Deny / Dry Run対象）
- Fail Closed（governance未初期化・例外時に書き込み系toolを拒否）

## Baseline以降のルール

Baseline (`e35724b97b7abcdc68ce5df5574537581faf0dfb`) 以降の全変更は、
以下を一括実行する Regression Test の通過を必須条件とする。

```
python structural/governance_regression.py
```

このコマンドが `Overall PASS` を返さない変更はBaselineへマージしない。

詳細な品質ゲートの定義は [QUALITY_GATE.md](QUALITY_GATE.md) を参照。

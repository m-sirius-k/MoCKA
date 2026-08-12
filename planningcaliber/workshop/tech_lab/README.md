# TIC Layer 2: tech_lab Sandbox

本体MoCKAに触れない隔離実験場。

## 目的

新しい技術・ライブラリ・実装パターンを試験する環境。本体汚染ゼロの原則に基づき、実験完了後の記録を必須とする。

## ディレクトリ構成

```
tech_lab/
├── README.md（このファイル・sandbox規約）
├── experiments/（個別実験フォルダ）
│   ├── claude_agent_view/
│   ├── mcp_v2_schema/
│   └── _template/（実験テンプレート・新規実験の基礎）
└── results/（評価結果集約 evaluation_log.jsonl）
```

## 厳守ルール

### 本体接続禁止

- MoCKA本体のファイル・フォルダ・データベースへの読み書き禁止
- 本体スクリプト（app.py・health_check.py・impact_analyzer.py等）への import/実行禁止
- 本体依存モジュール（structural/・gateway/・phi_os/直接参照）の使用禁止
- 本体イベント記録への直接書き込み禁止

### 実験テンプレート

各実験は `experiments/_template/` を基に作成する。以下情報を必須記載:

- **対象技術名**: 実験対象（ライブラリ名・実装パターン名等）
- **発見日**: YYYY-MM-DD 形式
- **発見源**: どこで見つけたか（GitHub Issue / PR / ブログ記事 / 実装中の気付き等）
- **仮説**: MoCKAのどこに影響するか（Relay / Orchestra / PHI-OS / Caliber / COMMAND CENTER）
- **実験手順**: 再現可能な step-by-step
- **結果**: 有効 / 無効 / 危険
- **MoCKAへの影響範囲**: 上記仮説の検証結果
- **推奨**: 採用 / 保留 / 却下 + その理由

### 実験完了後の義務

実験フォルダが完成した時点で、以下を実施**必須**:

1. `experiments/[実験名]/RESULT.md` を作成（結果サマリー）
2. `results/evaluation_log.jsonl` に実験結果を1行 JSON形式で追記
   ```
   {"experiment": "claude_agent_view", "result": "有効", "timestamp": "2026-08-12T...", "reason": "..."}
   ```
3. `mocka_write_event()`でイベント記録（type: SANDBOX_RESULT）
   - タイトル例: `SANDBOX_RESULT: claude_agent_view — 有効（Caliber影響範囲限定）`
   - description に実験テンプレート全内容を含める

記録なき実験は MoCKA記録層では存在しない扱いとする。

## Phase移行條件

- TIC Layer 2完全稼働: tech_lab フォルダ構造確立 + 実験テンプレート定着 + evaluation_log.jsonl に3件以上のSANDBOX_RESULT記録
- Layer 3移行前に: 本ディレクトリ本体汚染0件をverify_all.pyで確認

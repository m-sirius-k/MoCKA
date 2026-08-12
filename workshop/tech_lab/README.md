# tech_lab - MoCKA隔離実験場

## 目的

本体MoCKAに接続せず、新しい技術・提案の検証を行う隔離実験環境。

## 厳守ルール

**本体接続禁止**
- MoCKA本体のファイル変更一切禁止
- MoCKA本体のDB接続禁止
- MoCKA本体の関数呼び出し禁止
- 本体との統合は必ずEvent記録 + Human Gate判定を経て別途実施

**実験後の記録義務**
- 全ての実験はREADME入力後に`mocka_write_event(SANDBOX_RESULT)`を実行
- 結果はresults/evaluation_log.jsonl へ追記

## フォルダ構造

```
tech_lab/
├── README.md (this file)
├── experiments/
│   ├── _template/ (実験テンプレート)
│   ├── claude_agent_view/
│   ├── mcp_v2_schema/
│   └── (other experiments)
└── results/
    └── evaluation_log.jsonl
```

## 実験テンプレート

新しい実験を開始する場合、`experiments/_template/` をコピーして実験フォルダを作成。

### 実験フォルダ内容

各実験フォルダには以下を含める：

```
experiment_name/
├── README.md (実験定義・結果記録)
├── code/ (実装・テスト)
├── data/ (テストデータ)
└── results/ (出力結果)
```

### README.md テンプレート

実験フォルダの README.md には以下を記入：

```markdown
# 実験: {技術名}

## 基本情報

- 対象技術: {技術名}
- 発見日: {YYYY-MM-DD}
- 発見源: {どこで見つけたか}
- 実験開始日: {YYYY-MM-DD}

## 仮説

MoCKAのどこに影響するか：
- (Relay影響)
- (Orchestra影響)
- (PHI-OS影響)
- (Caliber影響)
- (COMMAND CENTER影響)

## 実験手順

1. (Step 1)
2. (Step 2)
3. (...)

## 結果

### 判定: [有効 / 無効 / 危険]

詳細:
- (What worked)
- (What didn't)
- (Risks identified)

## MoCKAへの影響範囲

影響を受ける可能性のあるコンポーネント:
- [ ] Relay
- [ ] Orchestra
- [ ] PHI-OS
- [ ] Caliber
- [ ] COMMAND CENTER

## 推奨判定

- [ ] 採用 (理由: {explanation})
- [ ] 保留 (理由: {explanation})
- [ ] 却下 (理由: {explanation})

## 次ステップ

- Event: `mocka_write_event(SANDBOX_RESULT, ...)`
- 本体統合: Human Gate判定を待つ
```

## 結果記録

実験完了後、以下の形式で`results/evaluation_log.jsonl`に追記：

```json
{
  "experiment_name": "example_tech",
  "date": "2026-08-12",
  "result": "有効",
  "verdict": "採用",
  "affected_components": ["Relay", "Orchestra"],
  "event_id": "E20260812_xxxxx",
  "notes": "本体統合ready"
}
```

## MoCKA本体との区別

**tech_lab内の作業:**
- 自由度あり（試験的、破壊的なコード可）
- 結果は評価のためだけ
- 本体影響ゼロ

**本体への統合:**
- Human Gateの判定必須
- 採用決定後に別途TODO生成
- すべての統合はEvent記録

---

**最終ルール: 「まず試す、本体は守る」**


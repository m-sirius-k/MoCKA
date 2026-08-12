# 実験テンプレート

このファイルをコピーして新しい実験を開始してください。

---

# 実験: {技術名}

## 基本情報

- **対象技術:** {技術名/提案名}
- **発見日:** {YYYY-MM-DD}
- **発見源:** {どこで見つけたか (e.g. GitHub issue, paper, internal discussion)}
- **実験開始日:** {YYYY-MM-DD}
- **実験者:** {実験を実施する人/AI}

## 仮説

MoCKAのどこに影響するか、どのような改善が期待できるか：

### 影響範囲想定

- [ ] **Relay** - (説明)
- [ ] **Orchestra** - (説明)
- [ ] **PHI-OS** - (説明)
- [ ] **Caliber** - (説明)
- [ ] **COMMAND CENTER** - (説明)

### 期待効果

- (具体的な効果1)
- (具体的な効果2)

## 実験手順

### Prerequisites

- (必要な環境設定)
- (必要なツール)
- (依存関係)

### Step 1: (ステップ名)

(手順詳細)

### Step 2: (ステップ名)

(手順詳細)

### Step 3: (ステップ名)

(手順詳細)

## 結果

### 最終判定: [ ] 有効 / [ ] 無効 / [ ] 危険

#### 有効 - この技術は機能し、MoCKAの改善に寄与する
#### 無効 - この技術は期待通り動作しなかった
#### 危険 - この技術は予期しないリスクを持つ

### 詳細結果

**うまくいったこと:**
- (実験結果1)
- (実験結果2)

**うまくいかなかったこと:**
- (失敗1)
- (失敗2)

**発見されたリスク:**
- (リスク1)
- (リスク2)

## MoCKAへの影響範囲

影響を受ける可能性のあるコンポーネント（複数選択可）:

- [ ] **Relay** - (どのように影響するか)
- [ ] **Orchestra** - (どのように影響するか)
- [ ] **PHI-OS** - (どのように影響するか)
- [ ] **Caliber** - (どのように影響するか)
- [ ] **COMMAND CENTER** - (どのように影響するか)

### 維持コスト試算

5年後もこの技術をメンテナンスできるか：
- (メンテナンス難度)
- (依存深度)
- (代替可能性)

### MoCKA思想との整合性

PHL/SPP思想と矛盾しないか：
- (整合性評価)

## 推奨判定

### [ ] 採用

**理由:**
- (採用すべき理由)
- (ROI)
- (維持可能性)

**次ステップ:**
- MoCKA本体への統合TODO自動生成
- Human Gate最終判定後に実施

---

### [ ] 保留

**理由:**
- (なぜ今は採用できないか)
- (解決すべき課題)

**再評価予定:**
- 60日後に再評価キューへ

---

### [ ] 却下

**理由:**
- (採用できない理由)
- (代替手段の存在)
- (維持負荷の懸念)

**永久記録:**
- 却下理由がEvents.dbに永久記録される
- 同様の提案の再検討時に参照される

## 実験ファイル

### コード

`code/` フォルダに実装コードを格納：

- `code/main.py` - メイン実装
- `code/test.py` - テスト
- `code/README.md` - 実装説明

### データ

`data/` フォルダにテストデータを格納：

- `data/input_sample.json` - 入力例
- `data/expected_output.json` - 期待出力

### 結果

`results/` フォルダに出力結果を格納：

- `results/output.json` - 実験出力
- `results/metrics.txt` - 性能指標

## 終了時の手続き

実験完了後、以下を実行：

### 1. 結果をREADMEに記入（このファイル）

### 2. Event記録を実行

```python
mocka_write_event(
    title="SANDBOX_RESULT: {技術名}",
    description="実験完了\n推奨判定: {採用/保留/却下}\n詳細: results/evaluation_log.jsonl参照",
    tags="sandbox_result,TODO_205",
    why_purpose="TIC Layer 2 evaluation"
)
```

### 3. evaluation_log.jsonlに追記

`results/evaluation_log.jsonl` へJSON行を追記：

```json
{
  "experiment_name": "{技術名}",
  "date": "{YYYY-MM-DD}",
  "result": "{有効/無効/危険}",
  "verdict": "{採用/保留/却下}",
  "affected_components": ["Relay", "Orchestra"],
  "event_id": "E{date}_{id}",
  "notes": "{推奨理由}"
}
```

---

**重要: 本体接続禁止を再確認してから実験開始**


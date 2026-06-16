# workshop 標準テンプレート仕様 v1.0

**制定日**: 2026-06-17  
**適用**: workshop/ 内すべての新規プロジェクト  
**イベントID**: E20260617_017

---

## 目的

すべての実験を同じ構造で管理し、比較可能にする。  
構造のばらつきをゼロにすることで、Caliberの評価精度を上げる。

---

## ディレクトリ標準

```
workshop/<project_name>/
├── core/           実験ロジック本体
├── experiment/     試行・検証コード
├── logs/           実行履歴（必須）
├── output/         成果物（HTML / JSON / MD）
├── config/         設定ファイル
├── tests/          テストコード
└── DESIGN.md       設計文書（必須）
```

---

## 各ディレクトリの責務

### core/
- 実験の本質ロジックのみ配置
- 外部依存を最小化
- 他実験から参照可能な形で設計

### experiment/
- 仮説検証コード・試行スクリプト
- 失敗実験も含めて保存（削除禁止）
- ファイル名に日時を含める（例: `exp_20260617_v1.py`）

### logs/
- すべての実行結果を記録（省略禁止）
- 形式: JSONL（1行1レコード）
- `run_YYYYMMDD_HHMMSS.jsonl` 形式推奨

### output/
- Caliber提出用成果物
- HTML / JSON / Markdown のいずれか
- 生成物のみ（ソースコードは置かない）

### config/
- 設定値・パラメータ
- 機密情報は `.env` に分離（configには置かない）

### tests/
- 再現性スコア（R）の根拠となるテスト
- テストなし → R スコアは最大 0.5

---

## DESIGN.md 必須記述項目

```markdown
# {プロジェクト名} 設計文書

**作成日**: YYYY-MM-DD
**ステータス**: workshop / candidates / specs

## 目的
（何のために存在するか）

## 仮説
（このプロジェクトが証明しようとしていること）

## 検証方法
（どう確かめるか）

## 成功条件
（何を達成したら「成功」か）

## 失敗条件
（何が起きたら「失敗」か）

## 依存関係
（他モジュール・外部サービスへの依存一覧）

## Caliber評価記録
（評価日・スコア・判定を記録する）
```

---

## 禁止事項

| 禁止 | 理由 |
|---|---|
| workshop外への直接出力 | 未評価成果物の本体汚染リスク |
| logsなし実験 | 再現性スコアが取得不能になる |
| DESIGNなしプロジェクト着手 | 目的不明実験は Caliber受理拒否 |
| experiment/ の失敗データ削除 | 失敗耐性評価に必要 |

---

## 新規プロジェクト起動手順

```powershell
# 1. ディレクトリ作成
$name = "project_name"
$base = "C:\Users\sirok\MoCKA\PlanningCaliber\workshop\$name"
@("core","experiment","logs","output","config","tests") | ForEach-Object {
    New-Item -ItemType Directory -Path "$base\$_" -Force
}

# 2. DESIGN.md 生成（workshop_template/DESIGN.md をコピー）
Copy-Item "C:\Users\sirok\MoCKA\PlanningCaliber\workshop_template\DESIGN.md" "$base\DESIGN.md"

# 3. MoCKAイベント記録
# mocka_write_event(title="WORKSHOP_START: {name}", tags="workshop_start")
```

---

## Caliber提出チェックリスト

```
□ DESIGN.md が存在し、必須項目が全て記載されている
□ logs/ に実行記録が1件以上ある
□ tests/ にテストが存在する（なければ R スコア上限 0.5）
□ output/ に成果物が存在する
□ 禁止事項に違反していない
□ mocka_write_event(WORKSHOP_DONE) が記録されている
```

---

*workshop 標準テンプレート仕様 v1.0 / 2026-06-17*

# vasAI L4.9 Reproduction Log

## 再現記録

| # | 環境 | OS | Python | 実行日時 | 結果 | ハッシュ |
|---|------|-----|--------|---------|------|---------|
| 1 | 開発機（PC-A） | Windows 11 | 3.12.x | 2026-05-31 | 未実施 | - |
| 2 | 第三者（PC-B） | - | - | - | 未実施 | - |
| 3 | 審査環境（PC-C） | - | - | - | 未実施 | - |

## 再現手順

```bash
# ① リポジトリをクローン
git clone https://github.com/m-sirius-k/vasAI.git
cd vasAI

# ② 依存パッケージをインストール
pip install -r requirements.txt

# ③ 再現スクリプトを実行
python reproduce_l48.py

# 期待される出力:
# vasAI L4.9 Proof of Reproducibility: VERIFIED
# Reproduction Hash: sha256:xxxxxxxx
# Result: 18/18 PASS
```

## Docker で再現する場合（Python不要）

```bash
docker compose run reproduce

# 期待される出力:
# vasAI L4.9 Proof of Reproducibility: VERIFIED
# Reproduction Hash: sha256:xxxxxxxx
```

## ハッシュ検証

`REPRODUCE_RESULT.md` に記載された `sha256:xxxx` ハッシュは、
全18シナリオの合否結果から生成されます。
同じコード・同じ環境で実行した場合、同じハッシュが生成されます。

## L4.9 判定

条件①〜⑪ 全達成時点で L4.9 VERIFIED を宣言する。

| 条件 | 内容 | 状態 |
|------|------|------|
| ① | reproduce_l48.py 完成 | 達成 |
| ② | README.md に再現手順記載 | 達成 |
| ③ | 18/18 PASS（S-16/S-17追加） | 達成 |
| ④ | GitHub Actions ubuntu/macos/windows PASS | 未実施（CI実行待ち） |
| ⑤ | SCENARIO-16 故意破壊試験 PASS | 達成 |
| ⑥ | SCENARIO-17 失敗DNA試験 PASS | 達成 |
| ⑦ | REPRODUCE_RESULT.md にSHA-256記載 | 達成 |
| ⑧ | Docker化（docker compose run reproduce） | 達成 |
| ⑨ | 別PC再現記録を REPRODUCTION_LOG.md に記載 | 第三者再現待ち |
| ⑩ | L5ベースライン収集開始（baseline_collector.py） | 達成 |
| ⑪ | 失敗DNA JSONスキーマ公式化（failure_dna_schema.json） | 達成 |

# tools/audit/ — 監査ツール

MoCKA の制度状態を読み取り、確認するためのツール群。

- 配置日: 2026-07-31(commit `3baf5dbe3` で正式管理下へ移設)
- 作成時期: 2026-07-17
- 種別: **監査ツール**。本番運用コードではない

---

## 1. このディレクトリの目的

MoCKA が記録した制度データ(Decision Ledger / Event Store)に対して、
**"誰が承認したのか""状態はどう分布しているのか"を外側から確認する**ためのツールを置く。

いずれも読み取りのみを行い、MoCKA の状態を変更しない。
パイプラインからは呼ばれず、人間が必要なときに手で実行する。

これらは 2026-07-17 に Decision Ledger の identity(承認主体)分布を調査する過程で
作られたものであり、その調査自体が MoCKA の監査可能性を示す証跡でもある。

---

## 2. 各スクリプトの役割

| スクリプト | 役割 | 対象データ |
|-----------|------|-----------|
| `check_approved.py` | `approved_by` の値を集計する。承認主体ごとの件数分布を出す | Decision Ledger |
| `check_status_boundary.py` | `approved_by` のキーワード(PENDING / Claude / Human Gate)と `status` のクロス集計。承認主体と決定状態の境界を見る | Decision Ledger |
| `classify_identity.py` | `approved_by` を6分類へ正規化して集計する。PENDING / VERIFICATION_ACTOR / EXECUTION_PROXY / HUMAN_GATE / HUMAN_AUTHORITY / OTHER | Decision Ledger |
| `inspect_identity.py` | `approved_by` に Claude / PENDING / 代理 / くろこ / R01 を含む Decision を一覧表示する | Decision Ledger |
| `inspect_other.py` | 既知の identity パターンのいずれにも該当しない `approved_by` を持つ Decision を抽出する。分類漏れの検出用 | Decision Ledger |
| `list_hg.py` | `approved_by` に Human Gate を含む Decision の ID と承認者を一覧表示する | Decision Ledger |
| `inspect_duplicate.py` | 特定 Decision (`DC_20260712_008` / `DC_20260712_010`) の全文を出力する。**調査対象IDがコード内に固定されている** | Decision Ledger |
| `check_tables.py` | Event Store のテーブル名一覧を出力する | Event Store |

`inspect_duplicate.py` は特定の重複調査のために書かれた一回限りのツールである。
対象IDが固定されているため汎用ではないが、当時の調査手順を再現できる証跡として残している。

---

## 3. 実行条件

| 項目 | 内容 |
|------|------|
| 実行場所 | **リポジトリルート**(`C:\Users\sirok\MoCKA`)。相対パスを使うため他の場所からは動かない |
| 依存 | Python 標準ライブラリのみ(`json` / `collections` / `sqlite3`)。外部パッケージ不要 |
| 認証 | 不要。ネットワークアクセスなし |
| 前提データ | `data/decisions/decision_ledger.jsonl` および `data/mocka_events.db` が存在すること |

実行例:

```bash
python tools/audit/check_approved.py
```

---

## 4. 対象となる MoCKA 状態

| データ | パス | 内容 |
|--------|------|------|
| Decision Ledger | `data/decisions/decision_ledger.jsonl` | 裁定記録(append-only)。7ツールが参照する |
| Event Store | `data/mocka_events.db` | イベント記録。`check_tables.py` が参照する |

いずれも `.gitignore` により非公開領域にある。
したがって本ツールはリポジトリを clone しただけでは実行できず、
MoCKA の実データを持つ環境でのみ意味を持つ。

---

## 5. 生成される証跡

**ファイルを生成しない。** 出力はすべて標準出力である。

証跡として残す場合は、実行結果を Event Ledger へ記録するか、
調査文書(`docs/audits/` 等)へ引用する運用とする。
ツール自身は記録装置を持たない。

---

## 6. 本番運用コードとの境界

| 観点 | 本ディレクトリ | 本番運用コード |
|------|---------------|---------------|
| 呼び出し元 | 人間の手動実行のみ | パイプライン / MCP / 常駐プロセス |
| 参照関係 | **他モジュールから import されていない**(実測確認済み) | 相互に依存する |
| 状態変更 | 行わない(読み取りのみ) | 行う |
| 実行の必然性 | 調査時のみ | 定常的に動く |
| 壊れた場合の影響 | 調査ができないだけ | 制度記録に影響する |

**本ディレクトリのスクリプトを本番経路へ組み込まないこと。**
組み込むと、監査する側とされる側の分離が失われる。

### 6.1 実装上の注意

- `check_tables.py` は `sqlite3.connect()` を読み書きモードで開く(SELECT のみ実行するが
  ハンドル自体は読み書き)。厳密な読み取り専用が必要な場合は `mode=ro` の URI 接続を用いること
- 各スクリプトは Decision Ledger の全行を素直に `json.loads` する。
  1行でも壊れていれば例外で停止する。破損検知としては機能するが、
  部分的な集計はできない

# Evidence Synchronization Strategy v0.1

Status: 設計提案（Human Gate確認前。まだ制度として固定しない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md、OPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.md、
REPOSITORY_DIVERGENCE_REPORT_v0.1.md

本文書は、Cloud・Local・MCPの3環境間で、どの文書をどの経路で同期すれば監査が再開できるかを設計する。
Option C監査の再開そのもの（Task 1〜4の実施）は本文書の範囲外。

---

## 1. 同期対象文書一覧

個別ファイル名の列挙はOPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.mdに既に存在するため、本文書では
重複させず参照する。本文書が定義するのは、今後同種の状況が発生した際に（何を同期対象と判定するか）の
基準である。

同期対象と判定する条件（いずれか一つでも満たせば対象）:

1. Decision Ledgerのrelated_documentsフィールドに列挙されているファイルパスで、Cloud checkout（git
   管理下）に存在しないもの。
2. Event LedgerのCHANGE_DONEイベントのtitleまたはafter_stateに新規作成・変更の対象として明記されて
   いるファイルパスで、Cloud checkoutに存在しないもの。
3. 会話内で、既存の設計・実装の前提として参照されたファイル・コンポーネントで、Cloud checkout内に
   実体が確認できないもの。

---

## 2. 同期単位

### 2.1 選択肢

- **文書単位**: 個々のファイル内容をそのまま貼り付け・添付する。
- **コミット単位**: Local環境でgit commitされたものを、実際のgit push/pull経由でCloud checkoutへ
  反映する。

### 2.2 比較

```
観点                  | 文書単位            | コミット単位
----------------------|----------------------|----------------------
反映の速さ              | 速い(即時貼付可)      | 遅い(commit->push手順必要)
来歴の検証可能性         | 弱い(誰がいつ書いたか| 強い(commit hash・author・
                       | の記録が残らない)     | timestamp・署名が残る)
既存のMoCKA git規律との  | 整合しない(TODO_364の| 整合する(mocka_git_safe_commit
整合                   | 共有ヘルパー経由の原則| 経由の原則をそのまま適用できる)
                       | から外れる)          |
差分追跡                | 不可(貼付前後の差分が| 可(git diffで機械的に確認できる)
                       | 記録されない)         |
Cloud checkout側の状態  | 変わらない(git管理外  | 変わる(git履歴に反映される)
                       | のローカル編集扱い)   |
```

### 2.3 推奨

**コミット単位を第一選択とする。** 理由: MoCKAは（記録なき作業はMoCKAとして存在しない）（三原則の
Record）を掲げており、既にmocka_git_safe_commit（TODO_364）という共有ヘルパー経由でのgit操作を制度化
している。文書単位の貼り付けは、この規律の外側に一時的な例外を作ることになる。

ただし、Local環境からの実際のcommit/push作業がすぐに行えない緊急時（例: Human Gate裁定を急ぐ必要が
あり、監査の一部だけでも先に進めたい場合）に限り、文書単位の貼り付けを暫定的な代替経路として認める。
この場合、貼り付けられた内容は（来歴未検証（Unverified Provenance））として扱い、後日必ず正式なcommit
に置き換えることを条件とする。

---

## 3. 同期完了判定

以下の条件をすべて満たした時点で、当該文書の同期は完了したとみなす。

1. Cloud checkout（またはそれに準ずる、監査を行うセッションから読み取り可能な場所）に、対象ファイルの
   実体が存在すること。
2. コミット単位の場合: commit hashが記録され、対応するEvent LedgerのCHANGE_DONE記録（event_id・
   作成日時）と時系列上矛盾しないこと（例: commitのタイムスタンプがCHANGE_DONEのwhen_tsより著しく
   後にならない）。
3. 文書単位（暫定貼り付け）の場合: （来歴未検証）の注記を本文冒頭に残すこと。
4. UTF-8検証（BOM無し・CP932汚染防止規約の禁止装飾記号無し）に合格していること。

---

## 4. 同期失敗時の対応

- 同期を試みても対象ファイルが読み取り不能な状態が続く場合、DC_20260730_009の枠組みに従い（未検証
  文脈（Unverified Context））として隔離し、当該ファイルを前提とするTaskの実施は見送る。
- 無制限な再試行は行わない。1回の同期試行が失敗した場合、原因（環境側の問題か、対象ファイルが実際には
  存在しないのかの切り分け）を記録した上で、次の判断（再試行/別経路の検討/Human Gateへの報告）を
  きむら博士に委ねる。
- 同期失敗が繰り返し発生する場合（本セッションで既に2回発生したcross-session contamination事故と
  同型のパターン）は、個別対応ではなくIntegrity Classification（state: Unknown, type: Evidence
  Missing相当）として記録し、recurrence_registryでの追跡対象とすることを検討する。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task1-4切替後の追加指示に基づき作成。 |

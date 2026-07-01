# REGISTRY_CHARTER_v1.0

KN-001: Registry Series 憲章

Artifact Type: Governance Document
Completion Evidence: .md 必須
Evidence Location: docs/governance/REGISTRY_CHARTER_v1.0.md
Verification Status: Pending（きむら博士承認待ち）

---

## 1. Registry の目的

Registry とは「何が存在するか」を一元的に管理する台帳である。

MoCKA において知識・制度・成果物が増殖するにつれ、「それが存在する」という事実そのものを
把握するコストが増大する。Registry はこの問題に対処するため、MoCKA 内に存在する全対象を
単一の参照可能な台帳に登録・管理する仕組みである。

Registry の役割は以下の一文で表される：

> 「存在する」ことを、問い合わせ可能な状態で保持する。

---

## 2. Registry の責務

Registry が管理対象とする登録カテゴリの大枠を以下に示す。

| カテゴリ | 説明 |
|---|---|
| CATEGORY | MoCKA 内の分類体系（カテゴリ・シリーズ等） |
| DOCUMENT | ガバナンス文書・ポリシー文書・仕様書等 |
| EVENT | イベント記録（mocka_write_event により記録されるもの） |
| DECISION | 決定事項・裁定結果 |
| POLICY | 運用ポリシー・制度ルール |
| SPEC | 仕様（スキーマ・プロトコル・インタフェース定義等） |
| TEST | テスト・検証結果の記録 |
| WORKFLOW | 手順・プロセス・承認ゲートの定義 |
| HEALTH | ヘルスチェック・状態監視に関する記録 |
| KNOWLEDGE | 知識アセット全般（上記に分類されないもの） |

フィールド定義・スキーマ設計はこの文書の範囲外である（KN-004 で扱う）。

---

## 3. KN カテゴリ内での位置付け

Registry Series は、KN（Knowledge Navigation）カテゴリの下に置かれた最初のシリーズである。

KN_SERIES_LEDGER（2026-07-01 宣言）に従い、KN カテゴリの構成は以下の通りである：

```
KN (Knowledge Navigation)
 +-- Registry Series  （今回開始）
 +-- Atlas Series     （将来）
 +-- （その他 Navigation 系 Series・将来）
```

KN カテゴリは「知識をナビゲートする」ための仕組みを管理する。
Registry Series はその中で「存在を知る」機能を担う最初のシリーズとして位置づけられる。

---

## 4. Atlas との責務分離

KN カテゴリ内の 2 つのシリーズは、以下の役割分担で成立する：

- Registry = 「何が存在するか」を知る（What）
- Atlas = 「どう繋がっているか」を知る（How）

Registry は存在の台帳であり、Atlas は関係の地図である。
Registry が「A が存在する」と記録し、Atlas が「A は B と連携する」と記録する。
この分離により、存在管理と関係管理が独立して進化できる。

Atlas Series は将来シリーズとして予告のみとし、現時点での設計・着手は行わない。

---

## 5. シリーズ構成の予告

Registry Series の構成を以下に予告する。着手は各前段階の承認後にのみ許可される。

| 番号 | タイトル | 内容（予告） |
|---|---|---|
| KN-001 | Registry Charter | Registry の目的・責務・位置付け・分離・ゲート条件（本文書） |
| KN-002 | Category Registry | MoCKA 内のカテゴリ体系を Registry として整理する |
| KN-003 | Registry Record Specification | Registry レコードの構造を定義する |
| KN-004 | Registry Schema | KN-003 の仕様を JSON Schema として形式化する |
| KN-005 | Registry Validation Rules | Registry の検証ルール・整合性条件を定義する |
| KN-006 | Registry Lifecycle | レコードの状態遷移（Draft → Review → Approved → Deprecated → Archived）を定義する |
| KN-007 | Registry Implementation Plan | KN-002〜KN-006 に基づく実装計画を策定する |

KN-002 以降の個別 TODO 起票は、前段階の承認完了後に行う（現時点では起票しない）。

---

## 6. 次段階へのゲート条件

KN-002（Category Registry）へ進むために、本文書（KN-001）において以下が確定している
必要がある：

1. Registry の目的が 1 文で明確に定義されていること（セクション 1 参照）
2. Registry の管理対象カテゴリの大枠が列挙されていること（セクション 2 参照）
3. KN カテゴリ内における Registry Series の位置付けが KN_SERIES_LEDGER と整合していること（セクション 3 参照）
4. Atlas との責務分離が「What / How」の軸で明文化されていること（セクション 4 参照）
5. KN-002〜KN-007 のシリーズ構成が予告として記載されていること（セクション 5 参照）
6. きむら博士による承認が得られていること

上記 6 条件がすべて満たされた後に、KN-002 の着手を許可する。

---

## 改訂履歴

- v1.0（2026-07-01）: KN-001 として新規作成。Registry Series 憲章。くろこ起草、きむら博士承認待ち。

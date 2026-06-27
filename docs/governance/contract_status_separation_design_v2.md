# contract_status分離設計 v2（TODO_385設計案・17件全件対応）

Status: DESIGN_PROPOSAL（本文書は設計案の提示のみ。コード変更・データ変更は未実施）
Date: 2026-06-28
作成: Claude-sonnet-4-6
前版: `docs/governance/contract_status_separation_design_v1.md`（13件版。本v2作成後も削除せず残置）
関連: TODO_384(調査・正規化), TODO_385(本設計), .claude/CLAUDE.md「TODO管理スキーマ」節
裁定: きむら博士裁定(2026-06-28) — 対象範囲を13件から17件全件へ拡大

## v1からの変更点

| 項目 | v1 | v2 |
|---|---|---|
| 対象件数 | 13件（category="設計成果物"/"基準仕様"のみ） | 17件全件（Architecture Contract系9語彙を使う全TODO） |
| 除外していた4件 | 対象外として提案 | きむら博士裁定により対象に含める |
| 件数差分の検証 | — | 1.1節で原因を特定（後述） |
| Architecture_Contract_Critical 3件の特殊性 | 未検討 | 1.4節で「変更不可」原則との抵触を検討（提案として提示） |
| GL7-VALIDATION-MISSING-BUGの扱い | 「対象外」として除外説明のみ | 1.5節・2章表内で「不具合管理上の調査済み」である旨を明記し対象に含める |
| 2章移行マッピング表 | 13件 | 17件 |

v1で示した1.スキーマ定義案（フィールド名/型/デフォルト値3案）・3.mocka_mcp_server.py変更案・
4.移行リスクの骨格は変更しない。本v2は「対象範囲」と「移行マッピング表」を拡張する文書である。

## 0. 本文書のスコープ

これは設計案の提示であり、実行ではない。

- 実施しないこと: MOCKA_TODO.jsonへの書き込み変更 / mocka_mcp_server.pyのコード変更 /
  17件のstatus値の実移行
- 実施すること: 件数差分の原因特定 / スキーマ定義案(v1から継承) / 17件の移行マッピング表 /
  コード変更案(v1から継承、差分形式) / Architecture_Contract_Critical 3件の特殊性検討 /
  GL7-VALIDATION-MISSING-BUGの扱い明確化 / リスク整理

実行は本文書の内容について別途Human Gate(きむら博士)承認後、別TODOとして着手する。

## 1. 件数差分の特定（3.1対応・最優先）

### 1.1 再検索結果

MOCKA_TODO.json正本（`C:/Users/sirok/MOCKA_TODO.json`）に対し、todos配列・completed配列の
両方からAchitecture Contract系9語彙
（DECISION_RECORDED/DONE_LOCKED/ALTERNATE_IMPLEMENTED/SPEC_OBSOLETE/SUPERSEDED/CLOSED/
確定/Phase3停止中(設計待ち)/調査済み）でstatus値を全文検索した。

結果: **17件**がヒットした。completed配列側にはヒットなし（全件todos配列内）。
ヒットしたIDは以下（Claude Chat側が提示した17件リストと完全一致、一次データで確認済み）。

```
TODO_HAB_GPT_CONNECTION_SPEC_V1            DONE_LOCKED              Architecture_Contract_Critical
TODO_PHASE5_6_GOVERNANCE_AUTHORITY_V1      DONE_LOCKED              Architecture_Contract_Critical
TODO_ARCHITECTURE_MAP_MCP_V1               DONE_LOCKED              Architecture_Contract_Critical
EXEC-LAYER-STD-V1                          ALTERNATE_IMPLEMENTED    設計成果物
HAB-CONTRACT-LAYER-V1                      SPEC_OBSOLETE            設計成果物
CONTRACT-INTEGRATION-TEST-SPEC-V1          CLOSED                   設計成果物
UNIFIED-EXEC-PHASE-PLAN-V1                 SPEC_OBSOLETE            設計成果物
REALITY-ALIGNMENT-HAB-GL7-V1               ALTERNATE_IMPLEMENTED    設計成果物
GL7-VALIDATION-MISSING-BUG                 調査済み                  不具合
GL7-MINIMAL-IMPL-SPEC                      ALTERNATE_IMPLEMENTED    設計成果物
GL7-MIGRATION-POLICY-V1                    CLOSED                   設計成果物
PHI-OS-GATE-BASELINE-V1                    SUPERSEDED               基準仕様
MOCKA-TWO-LAYER-OS-BASELINE-V1             確定                     基準仕様
GL7-KERNEL-SPEC-DOC-V1                     CLOSED                   基準仕様
CONTROL-MAP-V1-DECISION                    SUPERSEDED               基準仕様
CONTROL-MAP-V2-DECISION                    DECISION_RECORDED        基準仕様
PHI-OS-HUMAN-GATE-STATE-MODEL-V1           Phase3停止中(設計待ち)     基準仕様
```

### 1.2 16件→17件の差分の原因（特定済み）

検索範囲の漏れや正本とMCP経由データの差異ではない。**v1報告書の集計記述の誤り**が原因である。

v1作成時、9語彙の全文検索自体は今回と同じ範囲（todos配列全体）に対して実行しており、
実際にヒットしたのは今回と同じ17件だった。しかしv1の報告書（本文1.4節「対象13件の確定根拠」）
では、このうち`GL7-VALIDATION-MISSING-BUG`を「参考・除外1件」として別枠で記述し、
本文中の生の合計を「16件」（=17件 − GL7-VALIDATION-MISSING-BUGの1件）と記載してしまった。
つまり検索結果自体は最初から17件で一致していたが、報告時の足し算でGL7-VALIDATION-MISSING-BUG
を合計に含め忘れたことが直接の原因である。データ自体の齟齬ではなく、Claudeの集計記述ミス。

### 1.3 結論

正本に対する9語彙検索のヒット数は**17件**で一次データ上確定する。v1の「16件」表記は誤りであり、
本v2でこれを訂正する。きむら博士裁定により、この17件全件を二軸化（contract_status付与）の
対象とする。

### 1.4 Architecture_Contract_Critical 3件の特殊性に関する検討（3.3対応・提案）

対象3件: `TODO_HAB_GPT_CONNECTION_SPEC_V1` / `TODO_PHASE5_6_GOVERNANCE_AUTHORITY_V1` /
`TODO_ARCHITECTURE_MAP_MCP_V1`。いずれもnoteに「本契約は変更するとPhase4全体が構造的に
壊れる種類の仕様であるため、『変更不可TODO』として扱う」「変更が必要になった場合はPhase5
以降の『解釈固定の更新権』議論を経てv2.0として再定義する以外の変更経路は想定しない」と
明記されている（一次データ確認済み）。

**検討（提案・断定しない）**: contract_statusフィールドの新規付与は、この「変更不可」原則に
抵触しないと考える。理由は以下の通り。

- 「変更不可」原則が対象とするのは、契約の**内容**（HAB↔GPT間の構造接続規約・Phase5/6の
  ガバナンス定義そのもの）であり、本設計が変更するのは契約に紐づく**メタデータ管理方式**
  （status欄の意味づけ・contract_status欄の新設）である。契約本文の文言・構造・invariant
  には一切変更を加えない。
- 既存のstatus値`DONE_LOCKED`自体は変更しない（contract_statusへ同値をそのままコピーする
  だけであり、書き換えではなく複製）。status欄を5値スキーマに合わせて`完了`へ読み替える
  操作も、契約が「完了し凍結された」という事実認識を変えるものではない。
- TODO_384裁定（2026-06-27）で、この種のメタデータ正規化作業自体がCHANGE_START/DONE記録を
  必須とする運用ルールとして既に確立されている。これは「構造変更」と「記録を伴う運用上の
  整理」を区別する既存の枠組みであり、本作業は後者に該当する。

**代替案（抵触の可能性を重く見る場合）**: 上記の判断に同意できない場合、この3件のみ
移行を見送り、Phase5以降の「解釈固定の更新権」議論（TODO_PHASE5_6_GOVERNANCE_AUTHORITY_V1
で定義されたL4=Human Gate=きむら博士の構造更新権）を経て、v2.0契約として再定義する際に
合わせてcontract_status付与を行う案もある。

最終判断はきむら博士が行うこと。本文書はメタデータ変更で抵触しないとの立場を提案するに
留め、断定しない。

### 1.5 GL7-VALIDATION-MISSING-BUGの扱いに関する明確化（3.4対応）

`GL7-VALIDATION-MISSING-BUG`（`category="不具合"`）のstatus値`調査済み`は、Architecture
Contract系9語彙の1つと文字列として一致するが、意味としては設計成果物・基準仕様の
「契約ライフサイクル状態」ではなく、**不具合管理フローにおける進捗状態**（バグの原因調査が
完了した、修正自体は未完了）を表している。

2章の移行マッピング表ではこの1件について、他16件と同じ表内に含めつつ、注記列で
「不具合管理上の調査済み（契約ライフサイクルではない）」である旨を明示する。

## 2. 既存status/contract_statusフィールドのスキーマ定義案（v1から継承）

v1の1章「contract_statusフィールドのスキーマ定義案」をそのまま継承する。要点のみ再掲する。

- フィールド名: `contract_status`（提案）。型: 文字列、9値のenum。
- 適用対象: 本v2では17件全件（範囲拡大に伴い、適用対象の判定基準を「category=設計成果物/
  基準仕様」から「**status値が9語彙のいずれかに該当する全TODO**」へ変更する。これにより
  Architecture_Contract_Critical・不具合カテゴリも機械的に対象に含まれ、1.4/1.5の追加検討
  だけで済む）。
- 未付与時のデフォルト値: v1同様、案A（フィールド省略・キー自体を持たない）を推奨。
- 既存`status`フィールドとの関係: 両方を持つTODOについて、`status`は通常5値へ読み替える。
  一般原則はv1の表をそのまま適用する。

## 3. 17件全件の移行マッピング表

| TODO ID | category | 現status値 | 移行後status(5値・提案) | 移行後contract_status(9語彙) | 注記 |
|---|---|---|---|---|---|
| TODO_HAB_GPT_CONNECTION_SPEC_V1 | Architecture_Contract_Critical | DONE_LOCKED | 完了 | DONE_LOCKED | 1.4節「変更不可」原則の検討対象。メタデータ変更のみで本文は不変との立場(提案) |
| TODO_PHASE5_6_GOVERNANCE_AUTHORITY_V1 | Architecture_Contract_Critical | DONE_LOCKED | 完了 | DONE_LOCKED | 同上 |
| TODO_ARCHITECTURE_MAP_MCP_V1 | Architecture_Contract_Critical | DONE_LOCKED | 完了 | DONE_LOCKED | 同上 |
| EXEC-LAYER-STD-V1 | 設計成果物 | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED | — |
| HAB-CONTRACT-LAYER-V1 | 設計成果物 | SPEC_OBSOLETE | 廃止 | SPEC_OBSOLETE | — |
| CONTRACT-INTEGRATION-TEST-SPEC-V1 | 設計成果物 | CLOSED | 完了 | CLOSED | — |
| UNIFIED-EXEC-PHASE-PLAN-V1 | 設計成果物 | SPEC_OBSOLETE | 廃止 | SPEC_OBSOLETE | — |
| REALITY-ALIGNMENT-HAB-GL7-V1 | 設計成果物 | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED | — |
| GL7-VALIDATION-MISSING-BUG | 不具合 | 調査済み | 進行中 | （対象外・付与しない） | 1.5節参照。不具合管理上の調査済みであり契約ライフサイクルではないため、contract_statusは付与しない(空欄/キー省略)のが妥当。statusは「原因調査済み・修正未完了」を表すため5値では「進行中」が近い |
| GL7-MINIMAL-IMPL-SPEC | 設計成果物 | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED | — |
| GL7-MIGRATION-POLICY-V1 | 設計成果物 | CLOSED | 完了 | CLOSED | — |
| PHI-OS-GATE-BASELINE-V1 | 基準仕様 | SUPERSEDED | 廃止 | SUPERSEDED | — |
| MOCKA-TWO-LAYER-OS-BASELINE-V1 | 基準仕様 | 確定 | 完了 | 確定 | — |
| GL7-KERNEL-SPEC-DOC-V1 | 基準仕様 | CLOSED | 完了 | CLOSED | — |
| CONTROL-MAP-V1-DECISION | 基準仕様 | SUPERSEDED | 廃止 | SUPERSEDED | — |
| CONTROL-MAP-V2-DECISION | 基準仕様 | DECISION_RECORDED | 完了 | DECISION_RECORDED | — |
| PHI-OS-HUMAN-GATE-STATE-MODEL-V1 | 基準仕様 | Phase3停止中(設計待ち) | 進行中 | Phase3停止中(設計待ち) | 指示書内の例示(Phase3停止中→進行中)に従ったが、note内に「意図的停止」とあり「保留」も妥当。実行時に再確認推奨 |

**GL7-VALIDATION-MISSING-BUGについての重要な注記**: 本TODOは指示書3.4の指摘通り性質が
異なるため、`contract_status`フィールド自体を付与しないことを提案する（1.5節参照）。
9語彙のいずれにも当たらない別軸（不具合管理用の進捗ラベル）が必要であれば、それは本設計の
スコープ外であり、別途検討が必要。

## 4. mocka_mcp_server.py変更案（差分形式・未適用、v1から継承）

v1の3章をそのまま継承する（`TODO_STATUS_ENUM`/`CONTRACT_STATUS_ENUM`分割案、
`mocka_add_todo`/`mocka_update_todo`への`contract_status`パラメータ追加案）。
対象件数が17件に拡大したことによるコード変更案自体への影響はない
（enum定義の値集合・関数シグネチャは変わらない。影響するのはMOCKA_TODO.json側の
データ件数のみ）。

## 5. 移行実行時のリスク・注意点（v1から拡張）

v1の4章の内容（CHANGE_START/DONE記録義務、note/reference_event整合性確認事項、
スコープ境界）をそのまま継承する。17件への拡大に伴う追加事項を以下に示す。

- Architecture_Contract_Critical 3件は「変更不可TODO」として運用上は别格扱いされてきた
  経緯があるため、実際の移行作業時にきむら博士の最終承認を個別に得ること（1.4節の検討は
  あくまで提案であり、本文書の結論ではない）。
- GL7-VALIDATION-MISSING-BUGはcontract_status欄を付与しない方針(3章注記)とする場合、
  移行スクリプト・手動修正のいずれであっても「他16件は付与・本件のみ付与しない」という
  分岐処理が必要になる。一括処理スクリプトを書く場合はこの分岐を明示的にテストすること。
- 件数差分の原因（1.2節）はデータの不整合ではなくClaude側の報告ミスだったため、データ
  自体の再検証は不要。ただし今後同種の集計作業を行う際は、除外候補を「別枠」で記述する際に
  本体の合計から漏れないよう、合計値は常に「除外前の生ヒット数」を先に確定してから
  除外理由を付記する手順に変更することを推奨する（再発防止）。

# AUTO_SEAL M1 Implementation Proposal v1.0

- Document ID: GOV-PROP-ASM1-001
- Status: Proposed (drafting authorized; implementation NOT yet approved)
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Approval owner: きむら博士
- Parent decision: DC_20260713_003 (AUTO_SEAL Boundary Design v1.0, Model B Approved)
- Proposal decision: DC_20260713_004
- Design ref: docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md (Migration Plan M1)

本書は M1 の実装「提案」である。コードは含まず、実装は本書承認後の別工程とする。
本書作成時点で コード変更・Migration実行・本番データ変更は一切行っていない。

---

## 1. Purpose / Scope

DC_20260713_003 で採用確定した Model B の Auth Model を成立させる最初の一歩(M1)として、
seal監査レコードに Auth拡張フィールドを「後方互換で追加定義」し、それを書ける/読める/
検証できる最小モジュールを新規追加する。

M1のScopeは以下に限定する。

- IN: Auth拡張スキーマの定義、その write/read/verify を行う新規モジュール、その単体テスト。
- OUT(M1では行わない): 既存 seal経路(SealGovernanceGate/anchor_update.py/app.py)への接続、
  本番 decision_ledger.jsonl への書込、seal授権の強制、pending_ref の実在接続。

## 2. Minimal Working Path (最小実働経路)

M1が「動いた」と言える最小単位を次の1経路に限定する。

1. 新規モジュール `seal_auth_record` の write関数が、Auth拡張8フィールドを持つ
   seal監査レコードを1件、sandbox/一時ファイル(呼び出し側指定パス)へ追記する。
2. read関数が同レコードを読み戻す。
3. verify関数が必須条件(特に approved_by=human、必須フィールド充足)を判定する。
4. 従来スキーマの行(Auth拡張フィールドなし)と新スキーマの行が同一ファイルに混在しても、
   両方 parse できる(後方互換)。

この4ステップが sandbox 上で通ることを M1 の完了条件とする。本番 ledger への書込・
既存経路からの呼び出しは M1 に含めない(M2)。

## 3. Auth 拡張スキーマ (後方互換の追加フィールド)

既存 Decision Unit フィールド(decision_id/artifact_hash/seal_hash 等)は変更しない。
以下を追加フィールドとして定義する(既存行に無くても有効=optional parse)。

| フィールド | 型 | 必須 | 意味 |
|---|---|---|---|
| seal_request_id | str(一意) | 必須 | Seal要求単位の識別(execution_idとは別) |
| requester | str | 必須 | 要求主体(human識別子 or system:auto_audit_loop) |
| decision_id | str | 必須 | 根拠となる事前承認Decision(既存フィールド流用) |
| approved_by | str | 必須(human) | 人間の承認者。system値は不可 |
| approval_timestamp | ISO8601 | 必須 | 人間が承認した時刻 |
| artifact_hash | str | seal後必須 | 固定対象commit(既存フィールド流用) |
| seal_hash | str | seal後必須 | sealed_summary_hash(既存フィールド流用) |
| pending_ref | str | AUTO由来なら必須 | 対応 AUTO_SEAL_PENDING event_id(形式のみ、実在検証はM3) |

## 4. 変更対象ファイル 事前列挙

### 4.1 新規追加(M1実装時に作成するファイル。本書時点では未作成)

1. governance/seal_auth_record.py
   - Auth拡張レコードの write/read/verify を提供する薄いモジュール。
   - 既存の seal/hash/commit ロジックは呼ばない(記録層のみ)。
2. tests/test_seal_auth_record.py
   - 第6章デバッグ計画の単体テスト(tmp/sandbox で完結)。

(スキーマ定義は本書 第3章 に内包する。別途スキーマ専用文書が必要と判断される場合のみ
 docs/governance/AUTO_SEAL_AUTH_SCHEMA_v1.0.md を追加候補とする。)

### 4.2 変更しないファイル(M1で触らないことを明示)

- governance/seal_governance_gate.py (接続は M2、M1では無変更)
- scripts/ledger/anchor_update.py (frozen、無変更)
- app.py / API / port (無変更)
- data/decisions/decision_ledger.jsonl 本番 (M1では書込まない。既存行・スキーマ無変更)
- events.db 仕様 (無変更)

## 5. 非侵襲設計

- M1モジュールは呼び出し側指定の sandbox/一時パスに対してのみ書込む(前例:
  governance/seal_governance_wrapper.py の sandbox_root 限定方式に倣う)。
- 本番 decision_ledger.jsonl への書込・既存経路からの呼出は M1 では発生しない。
- したがって M1 実装は本番 seal/anchor/台帳へ影響を与えない(GREEN維持)。

## 6. 実装後デバッグ計画

M1実装後に実施する検証(すべて tmp/sandbox、本番無影響)。

| ID | テスト | 期待 |
|---|---|---|
| T1 | 後方互換: 旧行(拡張なし)+新行(拡張あり)混在を読む | 両方 parse 成功、旧行は欠落フィールドをoptional扱い |
| T2 | approved_by 検証: system/空/非human | verify 不合格(Seal不可判定) |
| T3 | approved_by=human | verify 合格 |
| T4 | 必須フィールド欠落(seal_request_id/requester/decision_id/approval_timestamp) | 各欠落で verify 不合格 |
| T5 | seal_request_id 一意性: 重複ID | 重複検知 |
| T6 | pending_ref: AUTO由来レコードで pending_ref 欠落 | 形式検証で不合格(実在検証はM3) |
| T7 | append-only/JSON整合: 書込後のファイル | 有効JSONL、既存行バイト不変 |

- 実行手段: pytest tests/test_seal_auth_record.py + 手動1件 write->read->verify。
- ロールバック: M1は新規ファイル追加のみのため、当該ファイル削除で完全復旧。本番データ
  変更が無いため戻し作業は不要。
- 記録: 実装時は CHANGE_START/CHANGE_DONE と本番/外部ハーネス別の CHANGE_DONE補完
  (GOV-PROC-EHCR-001)を遵守する。

## 7. Non Goals

- M2(既存 Gate から新モジュールへの接続)/M3(pending_ref 実在接続)/M4(直接実行境界の構造化)は
  行わない。
- 本番 decision_ledger.jsonl への書込・スキーマ改変は M1 では行わない。
- 既存コード(SealGovernanceGate/anchor_update.py/app.py)の変更は行わない。
- seal授権の強制(approved_by=human でない場合に実 seal を止める強制)は M1 では実装しない
  (verify 判定関数の提供のみ。強制の接続は M2)。
- 本書自体はコードを含まない(実装は本書承認後)。

## 8. 承認条件 (実装着手の条件)

1. 本書(GOV-PROP-ASM1-001)を きむら博士が承認する。
2. 第4.1章の新規追加ファイル(2件)と非侵襲方針(sandbox限定・本番無書込)を承認する。
3. M1完了後、M2(既存 Gate 接続)は更に別の Proposal と承認を要する。

## 9. History

- 2026-07-13: 初版(v1.0)。DC_20260713_003(Model B Approved)の M1 として起草。
  博士の起草許可条件(コード変更禁止/Migration実行禁止/最小実働経路/実装後デバッグ計画/
  変更対象ファイル事前列挙)を全て反映。実装は本書承認後の別工程(DC_20260713_004)。

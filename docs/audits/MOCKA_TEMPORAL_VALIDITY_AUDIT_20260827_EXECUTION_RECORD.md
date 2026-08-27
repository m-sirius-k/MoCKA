# MOCKA TEMPORAL VALIDITY AUDIT - EXECUTION RECORD (試験記録)

Date: 2026-08-27
Author: Claude-opus-5 (kuroko)
Related: `docs/audits/MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md`
Related commit: `56f760c5a` (監査報告書の追加)

---

## 0. 本文書の位置づけ (最重要)

**Status: PENDING_BACKFILL**

本文書は events.db への正規記録の**代替ではない**。
`mocka_write_event` が GL7 により恒久的に阻止されている状態 (3章) のため、
CHANGE_START / CHANGE_DONE および実行証跡を**一時的に**保全するものである。

MCP サーバー復旧後、本文書の内容を events.db へ遡及記録することを前提とする。
遡及記録が完了した時点で、本文書 status を BACKFILLED へ更新すること。

きむら博士より md 形式での試験記録保存の明示的許可を得て作成した
(CLAUDE.md の MCP Tool Registry Drift 対応方針における、
別経路への恒久的代替書込の禁止に対する、判断者による個別の裁定)。

| 項目 | 状態 |
|---|---|
| events.db への CHANGE_START 記録 | **未達** (GL7_EXECUTION_BLOCKED) |
| events.db への CHANGE_DONE 記録 | **未達** (同上) |
| Integrity Classification 登録 | **未達** (mocka_integrity_write も同経路で阻止) |
| Decision Ledger 登録 | 不要 (本監査は裁定を伴わない現状評価のみ) |
| 本 md による一時保全 | 完了 (本文書) |
| git commit / push | 完了 (`56f760c5a` および本文書のcommit) |

---

## 1. CHANGE_START (events.db へ記録できなかった内容、全文)

以下は `mocka_write_event` へ実際に送出し、拒否された内容である。

```
author: Claude-opus-5
tags:   change_start,audit,temporal_validity,read_only
title:  CHANGE_START: MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md 作成着手

why_purpose:
Temporal Validity Enforcement の実装境界 (どこまで実装済みで、どこから先が
未実装・未接続・未検証か) を Canonical Evidence によって一本の線として確定するため。
問題解決ではなく実装地図の作成が目的。

how_trigger:
きむら博士からの MOCKA TEMPORAL VALIDITY IMPLEMENTATION BOUNDARY AUDIT 指示書

description:
対象: docs/audits/MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md (新規)

変更理由: T0 (Decision/Authorization 成立時点) と Tn (Consequence/Tool Execution 時点)
の間の状態変化を、MoCKA が実行前に検知し必要なら実行を阻止できる状態まで
Level 0-8 のどこまで実装されているかを確定する。

変更内容: 監査報告書1ファイルの新規作成のみ。実装変更・修正・リファクタリング・
テスト追加・新規設計は指示により全て禁止。既存コードには一切触れない (read-only 調査)。

調査対象 (Canonical source):
  structural/governance_pipeline.py, structural/execution_governance.py,
  governance/write_path/restore/schema.py, governance/write_path/runtime/validator.py,
  governance/write_path/restore/materializer.py,
  app.py (/get_restore_packet, /get_restore_packet_v1),
  tools/mocka-bridge/extension/content.js, phi_os/human_gate.py,
  phi_os/runtime/authority_manager.py, phi_os/context/permissions.py,
  phi_os/context/control_gate.py, mocka_mcp_server.py, interface/health_check.py,
  structural/bee.py, structural/beta_engine.py, governance/verify_revoke_event.py,
  docs/experimental/meta/o0_v2_temporal_annotation_layer_v1.md,
  docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md

環境境界: 本セッションは Linux コンテナ上の git clone であり、正本の実行環境
(Windows, C:\Users\sirok\MoCKA) ではない。稼働中サーバー (5000/5679) への到達不可。
PlanningCaliber/workshop/ 配下は .gitignore 除外のため本 clone に不在。
これらは UNVERIFIED として報告書に明記する。
```

---

## 2. CHANGE_DONE (events.db へ記録できなかった内容、全文)

```
author: Claude-opus-5
tags:   change_done,audit,temporal_validity,read_only
title:  CHANGE_DONE: MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md 作成完了

description:
結果: docs/audits/MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md
作成完了 (806行、35,695文字)。commit 56f760c5a。
branch claude/temporal-validity-audit-k7d4f8 へ push 済。

UTF-8: OK (BOM無し / cp932汚染無し / 禁止装飾記号無し / 制御文字無し)
検証方法は本文書 4.8 に記載。

判定結果:
  L0 Problem Recognition        YES
  L1 Design Specification       PARTIAL
  L2 Mechanism Implementation   YES (Authority Continuity 軸) / PARTIAL (Time 軸)
  L3 Execution Path Integration PARTIAL
  L4 Pre-Execution Revalidation PARTIAL
  L5 Change Detection           PARTIAL
  L6 Execution Blocking         PARTIAL
  L7 Reproducible Validation    ABSENT
  L8 Operational Verification   ABSENT

CURRENT IMPLEMENTATION BOUNDARY (単一直線では表現不能、2軸x2経路):
  Authority Continuity 軸 x Context Injection 経路   -> LEVEL 6 到達、LEVEL 7 未確立
  Authority Continuity 軸 x MCP Tool Execution 経路  -> LEVEL 3 未確立
  Time 軸                 x 全経路                   -> LEVEL 2 未確立

主要所見:
1. MoCKA の Freshness は時間ではなく Governance Anchor 一致で定義されている
   (governance/write_path/restore/schema.py:95-100)。実測により generated_at が
   26年前でも anchor 一致なら is_fresh=True であることを確定。時間経過は判定入力から
   構造的に排除されており、これは実装漏れではなく明示的な設計判断である。
2. 前回監査の "実行経路 未接続" は部分的に不正確。enforcement point は Python 側ではなく
   Chrome 拡張 (tools/mocka-bridge/extension/content.js:269-292) にあり、
   Mode C 縮退という形で Blocking まで到達している。委譲は DC_20260723_007 で承認済。
3. check_freshness_against_current_anchor() / ExecutionGate / AuthorityManager は
   いずれも実行経路からの呼び出し元がゼロ。
4. STALE 用 fixture (fixtures.py:38-42) は存在するが、それを使うテストファイルが
   リポジトリ全体に存在しない。
5. anchor は 2026-07-07 から 51日間不変であり、検知機構は本番で一度も発火していない。

実装変更・修正・リファクタリング・テスト追加・新規設計: いずれも未実施 (指示通り)。
既存コードへの変更: ゼロ (git show --stat で新規1ファイルのみを確認済)。
```

---

## 3. INCIDENT 候補: Runtime Divergence (events.db / Integrity Classification へ未登録)

以下は `mocka_integrity_write` で
`state=Failure` / `type=Runtime Divergence` として登録すべき内容である。
同経路が阻止されているため未登録。

### 3.1 事象

`mocka_write_event` の呼び出しが2回連続で同一内容により拒否された。

```
1回目 / 2回目とも完全に同一 (決定論的、一時的要因ではない):

{"error": "GL7_EXECUTION_BLOCKED",
 "reason": "GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                       'encoding_mismatch:di_terminology_inventory_20260820.txt',
                       'encoding_mismatch:s05_decision_extract.txt']",
 "thinking_mode": "audit"}
```

### 3.2 detection_method (再現可能な検出手順)

1. 任意の書込系 MCP tool (`mocka_write_event` 等) を呼ぶ
2. 応答に `encoding_mismatch:<path>` を含む `GL7_EXECUTION_BLOCKED` が返ることを確認
3. 現行 HEAD の `structural/execution_governance.py` の `ABORT_CONDITIONS` を確認し、
   `encoding_mismatch` が**含まれていない**ことを確認
4. `git show HEAD~1:structural/execution_governance.py | grep -n encoding_mismatch` により、
   削除前のコードにのみ `aborts.append(f"encoding_mismatch:{path}")` (189行) が
   存在することを確認

### 3.3 確定した分岐

| 項目 | 値 |
|---|---|
| 削除 commit | `da4d4db` GL7-UNENFORCED-CONDITIONS-BUG: Remove unimplemented safety conditions |
| 削除日時 | 2026-08-12 |
| 実行時点 | 2026-08-27 |
| 乖離期間 | 15日間 |
| 検知手段 | 存在しない (本監査が偶発的に発見) |

現行 HEAD `structural/execution_governance.py:51-56`:

```python
ABORT_CONDITIONS = [
    "new_directory_detected",
    "unexpected_file_count",
    "deletion_outside_scope",
    "grounding_not_completed",
]
```

`HEAD~1` `structural/execution_governance.py:189`:

```python
aborts.append(f"encoding_mismatch:{path}")
```

runtime が返却した `encoding_mismatch:data/n8n/database.sqlite` は
後者の書式と完全に一致し、前者のコードには生成箇所が存在しない。

**結論: localhost:5002 で稼働中の MCP サーバーは commit `da4d4db` より前の
`structural/execution_governance.py` を実行している。**

### 3.4 impact_scope

削除前の実装は `BINARY_EXTENSIONS` に `.sqlite-shm` / `.sqlite-wal` / `.db` を含むが
`.sqlite` を含まない。このため `data/n8n/database.sqlite` は UTF-8 デコードを試行され
必ず `UnicodeDecodeError` となる。

当該ファイルが working tree に dirty として存在する限り、
`READ_ONLY_TOOLS` 以外の**全ての MCP tool が恒久的に阻止される**。

本監査時点で実行不能なもの:

```
mocka_write_event / mocka_decision_write / mocka_integrity_write /
mocka_update_todo / mocka_add_todo / mocka_seal / mocka_registry_add
```

### 3.5 本監査における位置づけ

この事象は、本監査が対象としている T0/Tn 問題そのものの実例である。

```
T0   = 2026-08-12  commit da4d4db で ABORT_CONDITIONS が変更された時点
Tn   = 2026-08-27  MCP tool が実行された時点
差分 = 実行中プロセスは T0 以前のコードを保持したまま
検知 = ゼロ
```

MoCKA には、稼働中プロセスが読み込んだコードと Canonical source の一致を
Tn 時点で検証する機構が存在しない。
CLAUDE.md が `mocka_mcp_server.py` 変更後の必須手順として更新を要求する
hash store (`data/tic/mcp_schema_hash.json`) は本 clone に**存在しない**ことも確認した。

### 3.6 実施しなかったこと (明示)

- 別経路 (events.db 直書き等) への恒久的な代替書込: **実施していない**
- 状態解消のためのコード変更: **実施していない** (read-only 監査であり、
  かつ Core System File 変更は Human Gate 承認事項であるため)
- working tree 操作 (dirty ファイルの削除・コミット等): **実施していない**
- 3回目以降の同一 tool 再試行: **実施していない**
  (CLAUDE.md の Drift 対応方針: 再試行は1回のみ、以降そのセッション内では抑制)

---

## 4. 試験記録 (本監査で実施した read-only 検証の全実行証跡)

以下は全て副作用のない読み取り専用実行である。
リポジトリ内のファイル・DB・稼働サービスに対する変更は一切行っていない。

### 4.1 Freshness Contract の実挙動確認 (Canonical source 直接実行)

対象: `governance/write_path/restore/schema.py` の `is_fresh()` / `validate()`
入力: `governance/write_path/restore/fixtures.py` の3 fixture +
      `governance/anchor_record.json` の実 anchor 値

```
current_anchor = 37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5

EXAMPLE_RESTORE_PACKET_V1:             validate_errors=[]  is_fresh=True
EXAMPLE_RESTORE_PACKET_V1_SUPERSEDING: validate_errors=[]  is_fresh=True
EXAMPLE_RESTORE_PACKET_V1_STALE:       validate_errors=[]  is_fresh=False

generated_at を 2000-01-01T00:00:00Z に差し替え、anchor は一致のまま
  -> is_fresh = True
```

判定: **PASS (仕様どおりに動作)**。かつ、
時間経過が判定入力から構造的に排除されていることを実測により確定。

備考: 本実行が `EXAMPLE_RESTORE_PACKET_V1_STALE` fixture が使用された
初めての記録である可能性が高い (4.6 参照)。監査目的の read-only 実行であり、
テストファイルの追加は行っていない。

### 4.2 Governance Anchor と materialized packet の突合

```
governance/anchor_record.json
  anchor_type         = manual_external_post
  sealed_summary_hash = 37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5
  sealed_at_utc       = 2026-07-07T11:03:41Z

governance/write_path/restore/materialized/
  RP_DCWP001_001.json  seq=1  generated_at=2026-07-22T23:39:22Z  -> FRESH
  RP_DCWP001_002.json  seq=2  generated_at=2026-07-22T23:39:46Z  -> FRESH
  RP_DCWP001_003.json  seq=3  generated_at=2026-07-23T00:11:43Z  -> FRESH
```

判定: anchor は 2026-07-07 から本監査時点 (2026-08-27) まで **51日間不変**。
materialized packet 3件は全て FRESH。
**実装された唯一の変化検知機構 (anchor 不一致) は本番データで一度も STALE を出力していない。**

### 4.3 Legacy restore packet の経過時間

```
PlanningCaliber/fp/restore_packet.json
  keys         = [$schema, version, generated_at, session_context, immutable, restore_5points]
  generated_at = 2026-05-28T09:02:46.225Z
  経過          = 約91日 (本監査時点)
```

判定: TODO_439 で "約8週間" として認識された staleness は、
新経路 (`/get_restore_packet_v1`) の追加によって迂回されただけであり、
旧経路 (`app.py:1661 /get_restore_packet`) 上では**解消されていない**。
当該ルートには freshness gate が存在せず、`generated_at_age_sec` の算出のみ
(`app.py:1681-1686`)。

### 4.4 beta_registry の T0 三点セット実データ集計

```
structural/beta_registry.json  (7エントリ、うち _meta 1件)
  expires_at フィールド保有: 6件
  expires_at が非 null:      0件
  approved_at が非 null:     4件
```

判定: 承認時刻 (T0) は実際に記録されているが、失効時刻は一度も設定されたことがない。
`expires_at` を**読む**コードはリポジトリ全体に存在しない
(書込側は `structural/bee.py:297,334` / `structural/beta_engine.py:261` の3箇所、
いずれも `None` 固定)。

### 4.5 失効機構の実在確認

```
governance/revoke_event.json  -> ls: cannot access: No such file or directory
```

判定: `governance/verify_revoke_event.py` は `verify_all.py:18` から呼ばれるが、
対象ファイルが不在のため常に `INFO: revoke_event.json not present` を出力し exit 0。
すなわち鍵失効検証は恒常的に no-op である。

### 4.6 呼び出し元ゼロの確認 (リポジトリ全文検索)

| 対象 | 検索結果 |
|---|---|
| `check_freshness_against_current_anchor` | 定義行 (`validator.py:72`) 以外の出現なし |
| `is_fresh` | 定義 (`schema.py:95`) と上記からの呼出 (`validator.py:75`) のみ |
| `EXAMPLE_RESTORE_PACKET_V1_STALE` | 定義 (`fixtures.py:38`) のみ。使用箇所なし |
| `ExecutionGate` | `phi_os/context/execution_context.py` 自モジュール外からの参照なし |
| `InstitutionRuntime` (AuthorityManager 保持) | `production_observation.py` と `phi_os/tests/` のみ |
| `human_gate.expire()` | `phi_os/tests/test_human_gate.py:52,89` のみ |
| `write_path` (tests/ 配下) | `tests/` 10エントリ・`phi_os/tests/` 15ファイルともに参照ゼロ |
| `*.test.js` / `*spec.js` | リポジトリ全体に存在しない |

### 4.7 /mcp エンドポイントの認可検証の不在確認

```
mocka_mcp_server.py:1126-1151  mcp_endpoint()   -> Authorization ヘッダ検証なし
mocka_mcp_server.py:146-150    @app.before_request -> リクエストログ出力のみ
mocka_mcp_server.py:1399       access_token 発行  -> 検証コードがリポジトリ内に存在しない
```

判定: 時間ベース失効が機能している唯一の資格情報 (OAuth authorization code、300秒、
`:1362` / `:1382`) は、交換して得た access_token が実行経路で一度も提示・検証されないため、
Tn における実行可否に影響を与えない。認可 (T0) と実行 (Tn) が経路として接続されていない。

### 4.8 成果物の UTF-8 / CP932 汚染防止規約 検証

対象: `docs/audits/MOCKA_TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md`

`mocka_check_utf8` は MCP サーバーが Windows 正本ホスト上で動作しており、
本セッションのファイルが Linux コンテナ側にあるため到達できなかった
(`File not found: C:\Users\sirok\MoCKA\docs\audits\...`)。
代替として同等の検証をローカルで実施した。

```
BOM:                        False
utf-8 decode:               OK  (35,695 文字)
禁止装飾記号:               NONE
  (初回検査で全角引用符2種を検出 -> Edit ツールにて ASCII 引用符へ全置換)
  (併せて非ASCIIダッシュを ASCII ハイフンへ全置換)
制御文字:                   NONE
残存する非ASCII約物:        § 、 。 ・  (いずれも通常の日本語約物および節記号、規約適合)
.gitignore:                 NOT IGNORED (docs/audits/ は除外対象外)
```

判定: **PASS**

### 4.9 commit 内容の実含有確認 (TODO_390 インシデント準拠)

```
git show --stat 56f760c5a
  docs/audits/...TEMPORAL_VALIDITY_IMPLEMENTATION_BOUNDARY_AUDIT_20260827.md | 806 +++++
  1 file changed, 806 insertions(+)

git push -u origin claude/temporal-validity-audit-k7d4f8
  * [new branch]  claude/temporal-validity-audit-k7d4f8 -> claude/temporal-validity-audit-k7d4f8
```

判定: 意図したファイルが実際に commit へ含まれていることを確認。既存コードへの変更ゼロ。

---

## 5. 復旧後に実施すべきこと (提案のみ、本セッションでは未実施)

以下はきむら博士の判断を仰ぐ項目であり、本監査では一切実行していない。

1. 稼働中 MCP サーバーの再起動 (現行 HEAD のコードをロードさせる)
2. 再起動後、`mocka_write_event` の疎通確認
3. 本文書 1章 / 2章の内容を events.db へ遡及記録
4. 本文書 3章を `mocka_integrity_write` で
   `state=Failure` / `type=Runtime Divergence` として登録
5. 登録後、`mocka_read_event` / `mocka_integrity_get` で読み戻し確認
   (CLAUDE.md: 実行証跡の定義 - 書込操作の成立条件)
6. 本文書 status を PENDING_BACKFILL から BACKFILLED へ更新
7. `data/tic/mcp_schema_hash.json` の不在について、
   CLAUDE.md の必須手順が実運用で機能しているかを別途確認

上記 1 は稼働中サービスへの操作であり、
3-6 は書込系操作であるため、いずれも判断者の明示的な指示を待つ。

---

以上

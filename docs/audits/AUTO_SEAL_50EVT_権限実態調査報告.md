# AUTO_SEAL_50EVT 権限実態調査報告

作成日: 2026-07-08
作成者: Claude (くろこ)
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-1 成果物
調査範囲: 調査のみ。Gate/Policy/AUTO_SEAL実コードへの変更は行っていない。
一次データ: app.py / watchdog_mocka.py / governance/mocka_git_safe_commit.py の現行コード、
git log 全履歴（コミットメッセージに AUTO_SEAL_50EVT を含む全5962件）、
data/integrity/integrity_classification.jsonl、MOCKA_TODO.json(TODO_371/426/427)、essence.json/guidelines.json。

---

## 0. 調査結論サマリー（最重要・先出し）

**IC_20260707_006は初回ではない。同型のCore System File Human Gateバイパスが、
検出されずに少なくとも2件、それより前に発生していたことをgit log上で確認した。**

- `0f7f9b89c941215658170a895e01cb7c623a6925`（2026-07-07 06:10:19、gateway/auth.py, gateway/gateway.py）
- `b66af6c63ad8289f3f54c837618947e37463cf5b`（2026-07-05 13:11:42、gateway/adapter_gpt.py, gateway/context_builder.py, structural/event_recency.py, structural/governance_pipeline.py）

いずれもintegrity_classification.jsonl / decision_ledger.jsonl / MOCKA_TODO*.json のいずれにも
記録がなく、事後に発見・分類された形跡がない（4章のObservation Record参照）。
**本指示書v2 3章「未知インシデント兆候発見時の取扱い」に基づき、本件のIC起票要否は
くろこが判断せず、きむら博士のHuman Gate判断に委ねる。**

---

## 1. 権限比較表（設計 vs 実装）

判定基準: 「権限があったか」ではなく「存在しないはずの権限経路が存在したか」を確認する。
差異欄は「-」（一致）または「調査」（未確認・要検証）のいずれかで埋め、憶測で断定しない。

| 項目 | 設計（あるべき姿） | 実装（現行コード、2026-07-08時点） | 実装（過去、2026-06-30〜2026-07-08） | 差異 |
|---|---|---|---|---|
| Event生成（AUTO_SEAL_PENDING記録） | ○（50件到達/日次でPENDINGイベントのみ記録） | ○（app.py:2107, watchdog_mocka.py:95 get_buffer().push） | ○（同様に記録は行っていた） | - |
| Seal実行（anchor_update.py直接起動） | ×（人間の明示指示によるhuman_gate_override_event_id経由のみ） | ×（commit 1707fcc38/3bc80842e以降、subprocess呼出は完全に除去済み。app.py 2052-2137行・watchdog_mocka.py 82-122行で確認） | **○（TODO_371是正=commit 1707fcc38、TODO_427是正=commit 3bc80842eより前は、50EVT分岐・日次分岐ともHuman Gate未経由でanchor_update.pyをsubprocess直接実行していた）** | 調査対象そのもの。2026-07-08是正で解消。ただし「解消済み」は最新app.pyプロセス再起動（PID 18468/10904、[[project_mocka_daily_autoseal_residual_risk]]参照）で実機確認済み。watchdog_mocka.pyはコード修正済みだが実プロセスとして現在稼働していない（dormant）ため、runtime反映の実証はしていない。 |
| Human Gate bypass（Core System Fileがgit commitに混入） | ×（is_core_system_file()除外により無条件で禁止） | ×（mocka_git_safe_commit.py 111-128行のpost-condition verification追加、commit 1707fcc38により2026-07-08是正済み） | **調査で確認: ○（実際に発生していた）。除外ロジック自体は2026-06-25/06-30から存在していたにもかかわらず、restore returncode未検証という実装バグ（TODO_426）により実効性がなかった。少なくとも3件のAUTO_SEAL_50EVTコミットがCore System Fileを含んで成立した（f1f0b6932/0f7f9b89c/b66af6c63、2章参照）。** | 「設計上は×だが実装上は存在してしまっていた経路」の実例。本調査の核心的発見。 |
| Ledger write（events.dbへの5W1H記録） | ○ | ○ | ○ | - |
| Policy override（Decision Policy評価のバイパス） | × | ×（該当コード上、risk_level/category_abはハードコード値であり、Decision Policyエンジン自体を呼び出す分岐が存在しない。Policy評価を経由しない代わりに「評価をバイパスする」機構も存在しない、という意味で×） | 調査（過去バージョンのコード差分は未精査） | - （ただし過去差分は未精査のため厳密には「調査」寄り） |
| MANUAL_SEALエンドポイント（/audit/seal） | ○（SealGovernanceGate経由でGL7評価を必須化、Phase C-2是正） | ○（app.py 2150-2159行、Phase C-2是正済みと確認） | 調査（Phase C-2是正前の状態は本調査では未精査） | - |
| _auto_approve_prevention()（NORMAL/CAUTION severityの自動承認） | 調査（本項目は本来のAUTO_SEAL_50EVT権限モデルの範囲外だが、同一ループ内(auto_audit_loop起動時に呼ばれる)にあり、approved_by="AUTO_GATE"という自己承認名義が使われている点は権限モデル上のグレーゾーンとして記録する） | app.py 2023-2049行に現存。severity=HIGH/CRITICALはHuman Gateへ回すが、NORMAL/CAUTIONは無条件でAUTO_GATE名義の自己承認が今も有効 | 同左（無変更） | 調査。TODO_428（パック2、実装監査止まり）の対象として別途扱われており、本調査ではAUTO_SEAL_50EVTの権限モデルとは別の制度設計問題として扱う（[[project_mocka_daily_autoseal_residual_risk]]のC分類と対応）。TASK-7横断マップで扱う。 |

---

## 2. 過去バイパス事例 年表（git log一次データに基づく）

### 2.1 調査方法

`git log --all --grep="AUTO_SEAL_50EVT" --name-only` で該当する全5962コミットのファイル一覧を取得し、
`governance/mocka_git_safe_commit.py` の `is_core_system_file()` 判定ロジック
（CORE_SYSTEM_DIRS = phi_os/, interface/, structural/, gateway/ の直下.pyファイル、
CORE_SYSTEM_FILES_EXTRA = app.py, index.html, scripts/ledger/anchor_update.py,
PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py）と機械的に突き合わせた。

Core System File保護ロジックが実装として初めて存在したのは commit `90a39ef27`
（2026-06-25 19:47:02、anchor_update.py/sync_watch.py個別実装）、
統合ヘルパー `governance/mocka_git_safe_commit.py` としての一本化は commit `fda5e37ec`
（2026-06-30 13:19:35）。gateway/ はこの統合ヘルパー作成時点から既にCORE_SYSTEM_DIRSに
含まれていたことをgit blameで確認済み。よって2026-06-30 13:19:35以降にCore System Fileが
AUTO_SEAL_50EVTコミットへ混入した事例は、すべて「保護ロジックが存在していたにもかかわらず
実効しなかった」事例として扱える。

### 2.2 該当事例一覧（2026-06-30以降、Core System Fileを含んだAUTO_SEAL_50EVTコミット）

| # | commit | 日時 | 含まれたCore System File | 検出・記録状況 |
|---|---|---|---|---|
| 1 | `0f7f9b89c941215658170a895e01cb7c623a6925` | 2026-07-05 13:11:42 | gateway/adapter_gpt.py, gateway/context_builder.py, structural/event_recency.py, structural/governance_pipeline.py | **未検出。integrity_classification.jsonl / decision_ledger.jsonl / MOCKA_TODO*.jsonのいずれにも本commitへの言及なし（grep確認済み）。4章のObservation Record参照。** |
| 2 | `b66af6c63ad8289f3f54c837618947e37463cf5b` | 2026-07-07 06:10:19 | gateway/auth.py, gateway/gateway.py | **未検出。同上。IC_20260707_006（同日20:03:40発生）のおよそ14時間前。** |
| 3 | `f1f0b6932c8f1995f133b7801477214cdcd1b7b0` | 2026-07-07 20:03:40 | app.py | **検出済み・IC_20260707_006として記録・DC_20260708_001でclose。** |
| 4 | `1707fcc382f3687c0825f69339a21a9c80111740` | 2026-07-08 07:16:42 | app.py | 是正パッチ自体のcommit。`human_gate_override_event_id`付き正規承認（TODO_426是正）であり、バイパス事例ではない。 |

備考: `6187be393`（2026-06-26、TODO_368/370/347-c統合コミット）および`90a39ef27`
（2026-06-25、除外ロジック新規追加コミット）もCore System Fileを含むが、いずれも
コミットメッセージ本文にAUTO_SEAL_50EVTへの言及があっただけの人間承認済み手動commitであり、
ボット自動生成コミット（コミットメッセージが厳密に"AUTO_SEAL_50EVT"のみ）ではないため、
上表から除外した。

### 2.3 保護ロジック成立前（2026-06-30より前）の扱いについて

2026-06-30より前は、Core System File除外ロジックが存在しない、または個別実装
（anchor_update.py/sync_watch.py側、2026-06-25〜）のみで統合前だったため、この期間の
AUTO_SEAL_50EVTコミットがapp.py等を含んでいたとしても、それは「保護されるべきという
設計判断自体がまだ制度化されていなかった期間の挙動」であり、「保護があったのにすり抜けた」
事例とは性質が異なる。ただし件数としては非常に多い（5962件中、2026-06-30以前かつ
Core System Fileを含むコミットは308件確認、うち大半はTODO_347/362是正前の「Gitに丸ごと
保存する保険機構」という当初設計どおりの挙動と推測される。この period のリスク評価は
本調査の主眼ではないため、詳細な個別精査は行っていない — 推測を含む記述である点に注意）。

---

## 3. AUTO_SEAL_50EVTの設計意図（一次データからの確認）

TODO_371のdescription（2026-06-26、きむら博士発言）より：

> AUTO_SEAL_50EVT/sync_watch.pyは、きむら博士自身が意図的に設計したもの。理由は
> 「MoCKAの最重要記録（会話・変更・イベントログ）が正しく記録されていない不安が
> あったため、Gitに丸ごと保存させることで漏れなく全てを残す保険機構」として組んだ。

この設計意図自体は「通常ファイルを丸ごとGitに保存する」ことであり、「Core System File
（app.py/phi_os等）をHuman Gate未経由でcommitする」ことまでは意図されていなかった、
というのがTODO_347/362是正（2026-06-25）以降の制度上の解釈である。2章で確認した3件は、
この「意図されていなかった経路」が実際に発生した実例である。

---

## 4. Observation Record（指示書v2 3章準拠。IC起票・原因分類はここでは行わない）

**指示書v2 3章の規定に基づき、以下は「発見」の記録に留める。既存IC番号への結合、
原因の断定的分類、IC起票要否の判断はいずれも行わない。これらはHuman Gate（きむら博士）
の判断事項である。**

- 発見日時: 2026-07-08（本調査中）
- 発見箇所: git log全AUTO_SEAL_50EVTコミット履歴（5962件）のうち、Core System File
  保護ロジック成立後（2026-06-30 13:19:35以降）の2件
  - `0f7f9b89c941215658170a895e01cb7c623a6925`（2026-07-05 13:11:42）
  - `b66af6c63ad8289f3f54c837618947e37463cf5b`（2026-07-07 06:10:19）
- 観測内容: いずれもコミットメッセージが厳密に"AUTO_SEAL_50EVT"のみ（ボット自動生成の
  特徴と一致）であり、gateway/・structural/配下のCore System File（.py）を、
  human_gate_override_event_id等の承認記録なしにcommitへ含めている。
  ファイル構成上、いずれも大量の自動生成ログ・イベントJSON（events_latest.json等）と
  混在しており、IC_20260707_006（f1f0b6932）と同一の「巻き込まれ混入」パターンに
  見える（推測。ソースコード上の混入経路（restore returncode未検証バグ、TODO_426）が
  同一かどうかは、当時のmocka_git_safe_commit.pyのバージョン差分を追わないと
  確定できないため、ここでは「推測」に留める）。
- 関連の疑いがある既存IC番号（参考記載のみ、結合はしない）: IC_20260707_006
- 未確認事項: (1)これら2件のcommitに含まれた変更内容自体が意図した（承認済みの）
  変更だったか、AUTO_SEAL自体が生成した意図しない変更だったかは未調査。
  (2)この2件以外にも、2026-06-30以前の期間（308件、2.3節）に同型の見落としが
  ないかは未精査。(3)このObservation自体をどう扱うか（IC起票/既存ICへの追記/
  経過観察のみ等）はHuman Gate判断待ち。

---

## 5. 推測・未確認の明示（総括）

- 「推測」と明示した箇所: 2.3節（2026-06-30以前の308件の性質）、4章の混入経路同一性。
- 未確認のまま残した箇所: watchdog_mocka.pyの是正コードは実プロセスとして現在稼働
  していないため、runtime反映の実証はできていない（コード上の是正は確認済み）。
  Decision Policy override（1章表内）は過去差分を精査していないため「調査」寄り。
- 本報告は指示書のIMMUTABLE制約に従い、調査結果に基づくGate/Policy/AUTO_SEALの
  実コード変更は一切行っていない。

---

## 6. 次工程への申し送り

- 4章のObservation Recordについて、IC起票要否のHuman Gate判断をきむら博士に仰ぐこと。
- TASK-7（横断マッピング）にて、本報告の「過去バイパス事例が複数・未検出のまま
  存在していた」という事実を、Autonomy Ladder（TASK-4）の確定不可原則・
  Exit Condition（TASK-5）のAI自己申告排除原則の裏付け根拠として明示的に接続すること。

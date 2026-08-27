# MOCKA TEMPORAL VALIDITY IMPLEMENTATION BOUNDARY AUDIT

Date: 2026-08-27
Auditor: Claude-opus-5 (kuroko)
Scope: READ-ONLY. 実装変更・修正・リファクタリング・テスト追加・新規設計はいずれも実施していない。
Audit Type: Implementation Boundary Measurement (not problem solving)

---

## 0. 監査の目的と前提

### 0.1 中心問題

T0 = Decision / Authorization 成立時点
Tn = Consequence / Tool Execution 時点

T0とTnの間で Evidence / Authority / Permission / Governance Anchor 等が変化した場合、
MoCKAが実行前にそれを検知し、必要なら実行を阻止できる状態まで実装されているか。

本監査は"どこまで実装されているか"と"どこから先が未実装・未接続・未検証なのか"を
Canonical Evidence によって確定することのみを目的とする。

### 0.2 監査環境の境界 (重要)

本監査は Linux コンテナ上の git clone に対して実施した。以下は本監査で到達できなかった。

| 到達不能な対象 | 理由 | 本報告書での扱い |
|---|---|---|
| 稼働中の app.py (port 5000) | 正本実行環境 (Windows, C:\Users\sirok\MoCKA) 外 | UNVERIFIED |
| 稼働中の caliber (port 5679) | 同上 | UNVERIFIED |
| PlanningCaliber/workshop/ 配下の全コード | .gitignore:65 により本cloneに不在 (別リポジトリ mocka-workshop-private 管理) | UNVERIFIED |
| Chrome拡張の実機実行 | 拡張をロードする手段が本環境に無い | UNVERIFIED |
| data/decisions/decision_ledger.jsonl | 本cloneに不在。MCP経由 (mocka_decision_get) でのみ参照可 | MCP経由で個別取得したもののみ Canonical 扱い |

ただし MCP サーバー (port 5002) へは到達可能であった。後述 6章の Runtime Divergence
所見は、この経路を通じた実測に基づく。

### 0.3 判定値の定義

YES / PARTIAL / ABSENT / UNVERIFIED / NOT APPLICABLE の5値のみを使用する。
推測による PASS は与えていない。grep 結果のみで runtime execution を断定していない。

### 0.4 本監査で厳守した区別

DEFINED != CALLED != REACHABLE != EXECUTED != ENFORCED != VALIDATED != OPERATIONALLY VERIFIED

各機構について"定義が存在すること"を"安全境界が実現されていること"として扱っていない。

---

## 1. 最重要の構造的発見 (先に述べる)

### 1.1 MoCKAの Freshness は"時間"ではなく"権威継続性"で定義されている

`governance/write_path/restore/schema.py:10-15` (WP-05, Phase4-03確定):

```
Freshness Contract(WP-05, Phase4-03確定):
    Primary Freshness Condition は時間経過ではなく Authority一致。
        packet.governance_anchor_hash == current governance sealed_summary_hash
    不一致の場合は STALE_CONTEXT として扱う。
```

`governance/write_path/restore/schema.py:95-100`:

```python
def is_fresh(packet: dict, current_governance_anchor_hash: str) -> bool:
    """
    Freshness Verification API相当の判定ロジック(WP-05)。
    Authority一致のみを基準とし、generated_atの経過時間は判定に用いない。
    """
    return packet.get("governance_anchor_hash") == current_governance_anchor_hash
```

本監査で当該 Canonical source を実際に実行し、以下を実測した (read-only、副作用なし)。

```
current_anchor = 37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5
EXAMPLE_RESTORE_PACKET_V1:            validate_errors=[] is_fresh=True
EXAMPLE_RESTORE_PACKET_V1_SUPERSEDING: validate_errors=[] is_fresh=True
EXAMPLE_RESTORE_PACKET_V1_STALE:       validate_errors=[] is_fresh=False

generated_at を 2000-01-01T00:00:00Z に差し替え、anchor は一致のまま -> is_fresh = True
```

**結論: generated_at が26年前であっても、Governance Anchor が一致していれば FRESH と判定される。**
時間経過は判定入力から構造的に排除されている。これは実装漏れではなく明示的な設計判断である。

したがって本監査の評価は、以下の2軸に分離しなければ意味を持たない。

- **軸A: Authority Continuity 軸** (governance anchor 一致) - 実装が進んでいる
- **軸B: Time / Staleness 軸** (経過時間による失効) - 意図的に判定入力から除外されている

### 1.2 唯一の明示的な時間層仕様は"時間をトリガにしない"ことを規定している

`docs/experimental/meta/o0_v2_temporal_annotation_layer_v1.md` (2026-06-24)
Status: EXPERIMENTAL / META / NON-CANONICAL

```
### 2.2 絶対制約(最重要)
- Δtはトリガではない
- Δtは"補助メタデータ"のみであり、SNAP発火条件には含めない
- Δtの増大それ自体はA6・O0-v1のいずれにも影響を与えない
```

MoCKA において"時間層"を正面から定義した唯一の文書が、時間を注釈 (annotation) と
位置づけ、enforcement 入力になることを禁じている。しかもこの文書自体が NON-CANONICAL で
あり、正式 governance ではない。

この教義は実装にも一貫して現れている。`app.py:1681-1686` (`/get_restore_packet`) は
`generated_at_age_sec` を算出して応答に付加するが、この値に基づく判定・拒否は一切行わない。
時間は測られ、露出され、しかし決して作用しない。

---

## 2. 評価階層別の判定

### LEVEL 0 - Problem Recognition: **YES**

Temporal Validity 問題は複数の一次記録で明示的に認識されている。

| Evidence | 場所 | 内容 |
|---|---|---|
| Memory Freshness Contract | `docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md` §3 | `Stored Evidence -> Time Passage -> Validity Unknown`。時間経過したMemoryは自動的にVerified扱いへ戻さない。具体的な鮮度閾値は本文書では確定させないと明記 |
| Gap-003 | `docs/audits/PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md` §4 | Freshness Threshold未確定を Pending Resolution として表形式で登録済 |
| SIM-002 | `docs/audits/PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md` §2 | UNKNOWN経路Simulationで"時間経過のみでのVerified化禁止"を確認 (ただし机上トレース) |
| TODO_439 実害記録 | `governance/write_path/restore/schema.py:4-8` | Legacy restore_packet.json が2026-05-28生成のまま約8週間、無警告で新規セッションへ注入され続けた |
| IC_20260724_004 | MOCKA_TODO_ACTIVE.json (ESSENCE Materialization Pipeline Staleness Investigation) | ping_generator.py / essence_auto_updater.py の常駐化未実装・鮮度リスク。materialization freshness indicator 追加が検討候補として記録され、実装は現時点で禁止と明記 |

Gap: 認識は明確だが、認識された Gap (特に Gap-003 の閾値) は本監査時点まで未解消のまま。

---

### LEVEL 1 - Design Specification: **PARTIAL**

| 対象 | Status | Evidence |
|---|---|---|
| Freshness (Authority一致基準) | YES | `governance/write_path/restore/schema.py:10-15` WP-05 Phase4-03確定 |
| Reader側縮退挙動 (Mode C) | YES | 同 :14-15。immutable層のみ許可、dynamic contextは拒否 (HG-WP-04, R01推奨) |
| Supersede Resolution | YES | 同 :17-20。単純timestamp最大ではなく Governance Seal一致 + sequence最大 + supersedes chain有効 の複合条件 (HG-WP-05, Phase6/8確定) |
| Decision-to-Execution Boundary | PARTIAL | `structural/execution_governance.py:13-16` に Execution Pipeline 固定順序 (Task -> Grounding -> Policy確認 -> Conflict検出 -> Dry Run -> Approval -> Execute -> Verify) が定義。ただし Approval と Execute の間の再検証は規定されていない |
| Freshness 閾値 (時間) | ABSENT | Gap-003 として未確定。`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md` §5 で"本Policyで決めないこと"に明記 |
| Authority Freshness | ABSENT | Authority に時間概念を持たせる仕様が存在しない (2.2 参照) |
| Present-State Revalidation | PARTIAL | Consumer側責務として `/get_restore_packet_v1` docstring に規定 (DC_20260723_007準拠)。Producer側での再検証義務は規定されていない |

Gap: Authority一致軸は仕様化済み。時間軸は"決めないこと"として明示的に棚上げされている。

---

### LEVEL 2 - Mechanism Implementation: **YES (軸A) / PARTIAL (軸B)**

#### 2.1 実装済み機構 (Authority Continuity 軸)

| # | 機構 | file:line | function/class | 定義内容 | 意図された目的 |
|---|---|---|---|---|---|
| M1 | Freshness判定 | `governance/write_path/restore/schema.py:95-100` | `is_fresh()` | anchor hash 一致比較 | WP-05 Freshness Verification API相当 |
| M2 | 現行anchorとの突合 | `governance/write_path/runtime/validator.py:72-75` | `check_freshness_against_current_anchor()` | Tn時点の anchor_record.json を再読込して M1 を呼ぶ | draft packet の現在時点妥当性確認 |
| M3 | Supersede chain解決 | `governance/write_path/restore/materializer.py:41-64` | `_resolve_supersede_chain()` | anchor一致 + sequence最大 + chain有効 | HG-WP-05 最新判定 |
| M4 | Reader側 Fresh/Stale判定 | `tools/mocka-bridge/extension/content.js:269` | `injectDNA()` 内 | `d1.packet.governance_anchor_hash === d1.current_governance_anchor_hash` | Mode C 縮退注入の分岐 |
| M5 | Anchor値の同時配信 | `app.py:1688-1719` | `get_restore_packet_v1()` | packet と current_governance_anchor_hash を同時返却 | Consumer が判定するための材料供給 |

#### 2.2 実装済み機構 (Time 軸) - 限定的

| # | 機構 | file:line | 内容 | 評価 |
|---|---|---|---|---|
| M6 | OAuth authorization code 失効 | `mocka_mcp_server.py:1362`, `:1382` | `"expires_at": time.time() + 300` / `if stored["expires_at"] < time.time(): -> invalid_grant` | MoCKA内で唯一、実行経路上で機能している時間ベース失効。ただし transport 層 |
| M7 | Human Gate EXPIRED状態 | `phi_os/human_gate.py:23,30,38,171-172` | STATES に EXPIRED、`expire()` は PENDING からのみ遷移可 | 状態機械としては存在。時間駆動の発火機構は無し (2.4参照) |
| M8 | 運用鮮度監視 | `interface/health_check.py:119,146,329-362,447-460` | canary CI `stale_days=7` 超過でFAIL / Relay ping `stale_seconds=300` 超過でFAIL | 実装され機能する時間ベース判定。ただし対象は liveness であり authorization ではない |
| M9 | Grounding TTLキャッシュ | `structural/governance_pipeline.py:60,84-89` | `GROUNDING_REFRESH_SECONDS = 60` | 時間による再取得。ただし"鮮度保証"ではなく"負荷軽減"目的 |
| M10 | Legacy packet 経過秒算出 | `app.py:1681-1686` | `generated_at_age_sec` を算出し応答に付加 | 測定のみ。判定・拒否には一切用いられない |

#### 2.3 失効 (Revocation) 機構

| # | 機構 | file:line | 状態 |
|---|---|---|---|
| M11 | 鍵失効イベント署名検証 | `governance/verify_revoke_event.py:10-30` | 実装済。ただし `governance/revoke_event.json` は**存在しない** (本監査で確認)。結果として常に `INFO: revoke_event.json not present` を出力し exit 0 |
| M12 | 鍵失効チェック | `verify/manifest_resolver.py:96-102` | `revoked_at_utc is not None -> raise ValueError("key revoked")`。実装済 |
| M13 | Authority委譲の失効 | `phi_os/runtime/authority_manager.py:144-147` | `revoke_delegation()` 実装済。ただし `self._store` は in-memory (`__init__` で `dict(_CANONICAL_AUTHORITY)` を毎回複製)。永続化なし |
| M14 | Token失効リスト | `verify_token.py:17-19` | `revoked_tokens` 参照。スタンドアロン検証スクリプト |

#### 2.4 定義のみで値が入らない機構 (schema-only)

`structural/bee.py:297`, `structural/bee.py:334`, `structural/beta_engine.py:261`:

```python
"approved_by":   None,
"approved_at":   None,
"expires_at":    None,
```

β (証拠で成長する仮説構造体) レコードは T0 三点セット (承認者・承認時刻・失効時刻) の
フィールドを持つ。本監査で実データを集計した結果:

```
structural/beta_registry.json (7エントリ、うち _meta 1件)
  expires_at フィールド保有: 6件
  expires_at が非null:       0件
  approved_at が非null:      4件
```

承認時刻 (T0) は実際に記録されているが、失効時刻は一度も設定されたことがなく、
`expires_at` を**読む**コードはリポジトリ全体に存在しない (grep 確認済)。

#### 2.5 構造的に不在の機構 (ABSENT)

| 対象 | Evidence | 内容 |
|---|---|---|
| Authority の時間表現 | `phi_os/runtime/runtime_types.py:84-88` | `Authority` dataclass のフィールドは `authority_type` / `holder` / `delegated_to` / `delegation_event_id` の4つのみ。issued_at / expires_at / valid_until のいずれも存在しない |
| Permission の時間表現 | `phi_os/context/permissions.py:21-38` | `check_observe` / `check_write` / `check_control` はいずれも引数に時刻を取らない純粋関数。`check_control` は `actor_id == "HAB"` の恒真比較。失効しうる状態が構造的に存在しない |
| Decision の有効期限 | `mocka_mcp_server.py` mocka_decision_write | 記録されるのは `approved_at` のみ。`status` は Active/Superseded/Withdrawn の3値だが、時間による自動遷移は存在しない |

---

### LEVEL 3 - Execution Path Integration: **PARTIAL**

#### 3.1 追跡した実行経路

```
[MCP Tool 経路]
HTTP POST /mcp                          mocka_mcp_server.py:1126  mcp_endpoint()
  -> method == "tools/call"                                :1143
  -> execute_tool(name, args)                              :479
  -> _governance.before_tool(name, args)                   :492
     -> GovernancePipeline.before_tool()   structural/governance_pipeline.py:91
        -> _refresh_grounding()                                  :96  (60秒TTL)
        -> ThinkingModeEngine.detect_mode()                      :98
        -> ReasoningGovernanceEngine.enforce_pre_answer_checklist():106
        -> if tool_name not in READ_ONLY_TOOLS:                  :109  (Default Deny)
             ExecutionGovernanceEngine.pre_execution_check()     :115
               -> dry_run()  structural/execution_governance.py:102
                    -> git status --porcelain -z                     :108   [Tn現在値を再取得]
                    -> check_abort_conditions()                      :145
  -> if not decision.allowed: return GL7_EXECUTION_BLOCKED  :493-498
  -> (許可された場合のみ) 各tool本体を実行                    :509以降

[Context Injection 経路]
Chrome Extension injectDNA()   tools/mocka-bridge/extension/content.js:256
  -> fetch /get_restore_packet_v1                                :266
     -> app.py:1688 get_restore_packet_v1()
        -> anchor_record.json の sealed_summary_hash をTn時点で再読込  :1697
        -> materialized/RP_*.json のうち sequence最大を選択            :1712
        -> packet と current_governance_anchor_hash を返却            :1713-1717
  -> const fresh = (packet.governance_anchor_hash === current...)  :269  [Tn比較]
  -> fresh  -> 全層注入                                            :270-278
  -> !fresh -> LIMITED TRUST 縮退注入 (immutable層のみ)             :279-292
  -> (v1が非OK/例外の場合) fetch /get_restore_packet               :303  [Legacy、freshness gate無し]
  -> (それも失敗の場合) fetch /get_latest_dna                       :317  [v2]
```

#### 3.2 機構別 DEFINED / CALLED / REACHABLE / EXECUTED 判定

| 機構 | DEFINED | CALLED | REACHABLE | EXECUTED | 根拠 |
|---|---|---|---|---|---|
| M1 `is_fresh()` | YES | YES (M2からのみ) | NO | NO | 呼び出し元は M2 一箇所のみ。M2 自身に呼び出し元が無い |
| M2 `check_freshness_against_current_anchor()` | YES | **NO (呼び出し元ゼロ)** | NO | NO | リポジトリ全文検索の結果、定義行以外に出現しない |
| M3 `_resolve_supersede_chain()` | YES | YES (materialize内) | UNVERIFIED | UNVERIFIED | materialize() の呼び出し元がリポジトリ内に無い (app.py:1690等は文字列一致のみで実呼出ではない) |
| M4 content.js freshness比較 | YES | YES | YES | **UNVERIFIED** | 拡張実機実行が未検証。E記録に Not verified: Live Chrome Extension runtime execution と明記済 |
| M5 `/get_restore_packet_v1` | YES | YES | YES | YES (隔離port5098でHTTP実証済、E記録) | ただし本番稼働の実測は本環境から不可 |
| M6 OAuth code失効 | YES | YES | YES | UNVERIFIED | 経路上に存在。ただし発行された access_token は後段で検証されない (3.3参照) |
| M7 `human_gate.expire()` | YES | **tests のみ** | NO | NO | `phi_os/tests/test_human_gate.py:52,89` 以外に呼び出し元なし |
| M8 health_check 鮮度監視 | YES | YES | YES | UNVERIFIED | 稼働確認は本環境から不可 |
| M13 `revoke_delegation()` | YES | **NO** | NO | NO | `AuthorityManager` を保持する `InstitutionRuntime` の参照元は `production_observation.py` と tests のみ。MCP/app 実行経路に接続なし |
| ExecutionGate (5チェック) | YES (`phi_os/context/execution_context.py:49-`) | **NO (呼び出し元ゼロ)** | NO | NO | 全文検索で自モジュール外からの参照なし |
| GL7 dry_run / abort | YES | YES | YES | **YES (本監査で実測)** | 6章参照 |

#### 3.3 認可と実行経路の断絶 (重大)

`mocka_mcp_server.py` は OAuth 2.0 (authorize / token / PKCE) を実装し、
authorization code に 300秒の失効を課している (M6)。しかし:

- `/mcp` エンドポイント (`:1126-1151`) に Authorization ヘッダの検証が存在しない
- `@app.before_request` (`:146-150`) はリクエストログ出力のみ
- 発行された `access_token` (`:1399`) を検証するコードがリポジトリ内に存在しない

**すなわち、時間ベース失効が機能している唯一の資格情報 (authorization code) は、
それを交換して得た access_token が実行経路で一度も提示・検証されないため、
Tn における実行可否に影響を与えない。** 認可 (T0) と実行 (Tn) が経路として接続されていない。

#### 3.4 Producer 側が判定を放棄していることの一次証拠

`app.py:1689-1691` (`/get_restore_packet_v1` docstring):

```
現在のGovernance Seal値(anchor_record.jsonのsealed_summary_hash)を返す。
Fresh/Staleの判定自体はConsumer側(Reader)の責務とする(DC_20260723_007準拠)。
```

DC_20260723_007 (MCP経由で本監査中に取得、status=Active、approved_by=きむら博士(Human Gate、2026-07-23)):

```
decision=Phase 8-4 scope updated。... Actual runtime path discovered:
content.jsはmocka_mcp_server.py(port5002、MCP)を一切使わず、
app.py(port5000、COMMAND CENTER)の/get_restore_packetルートへ直接fetchしている
impact=Phase8-4の実装対象は(1)app.py (2)content.js の2ファイルへ絞られ、
mocka_mcp_server.pyの変更は別Decision対象として保留される。
```

判定責務が Consumer (Chrome拡張の JavaScript) に委譲されたことは制度的に承認済みである。
これは逸脱ではない。ただし帰結として、**Temporal Validity の enforcement point が
governed runtime の外側 (拡張機能) に置かれ、サーバーは STALE な packet の payload 全体を
無条件に配信する**構造になっている。別の Consumer、または fallback 経路を通る Consumer には
enforcement が及ばない。

Gap: 軸A の機構群のうち、実行経路に接続されているのは M4/M5 (Context Injection 経路) のみ。
M1/M2/M13/ExecutionGate は接続ゼロ。MCP Tool 実行経路 (execute_tool) には
Temporal Validity 機構が一切接続されていない。

---

### LEVEL 4 - Pre-Execution Revalidation: **PARTIAL**

Tn 現在値の再検証が行われているか、対象別に判定する。

| 再検証対象 | Status | Evidence | 備考 |
|---|---|---|---|
| filesystem / repository 物理状態 | **YES** | `structural/execution_governance.py:108` が tool 呼び出しの都度 `git status --porcelain -z` を実行 | T0 の判定結果を再利用していない。真の Present-State Revalidation |
| governance anchor validity | **PARTIAL** | `app.py:1697` が要求の都度 anchor_record.json を再読込。`content.js:269` が Tn 比較を実施 | Producer は判定せず材料供給のみ。判定は Consumer 側 |
| grounding (branch/構造) | PARTIAL | `structural/governance_pipeline.py:86` の 60秒 TTL キャッシュ | 最大60秒前の値が再利用されうる。Tn 値の保証ではない |
| evidence freshness (時間) | **ABSENT** | 1.1 の実測 (generated_at=2000年でも FRESH) | 構造的に判定入力から除外 |
| authority freshness | **ABSENT** | 2.5。Authority に時間フィールドなし | 再検証すべき状態が存在しない |
| permission validity | **ABSENT** | `phi_os/context/permissions.py` は静的な純粋関数 | 同上 |
| decision validity | **ABSENT** | Consequence 実行直前に decision_ledger の status (Superseded/Withdrawn) を照合する経路が存在しない。`grep Superseded --include=*.py` の結果、消費側は `governance/write_path/transition/schema.py` の enum 定義と restore 系の supersedes chain のみ | Decision が Withdrawn になっても、それに基づく実行は阻止されない |

Gap: 物理状態の再検証は確立している。制度状態 (authority / permission / decision / evidence) の
実行直前再検証は、anchor 一致を除いて存在しない。

---

### LEVEL 5 - Change Detection: **PARTIAL**

| 変化の種類 | 検知可能か | 実行経路から到達可能か | Evidence |
|---|---|---|---|
| Governance anchor changed | **YES** | YES (Context Injection 経路のみ) | M1/M4/M5 |
| Relevant state changed (filesystem) | **YES** | YES | GL7 dry_run。6章で実測 |
| Evidence expired (時間経過) | **ABSENT** | N/A | 1.1 の実測により構造的に検知不能 |
| Authority revoked | **ABSENT** | NO | M13 は in-memory かつ実行経路未接続。`revoke_event.json` は不在 (M11) |
| Permission changed | **ABSENT** | NO | 2.5 |
| Decision superseded / withdrawn | **ABSENT** | NO | LEVEL 4 表参照 |

#### 5.1 検知機構が一度も発火していないことの実測

本監査で実データを照合した結果:

```
governance/anchor_record.json
  sealed_summary_hash = 37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5
  sealed_at_utc       = 2026-07-07T11:03:41Z

governance/write_path/restore/materialized/
  RP_DCWP001_001.json  seq=1  generated_at=2026-07-22T23:39:22Z  -> FRESH
  RP_DCWP001_002.json  seq=2  generated_at=2026-07-22T23:39:46Z  -> FRESH
  RP_DCWP001_003.json  seq=3  generated_at=2026-07-23T00:11:43Z  -> FRESH
```

Governance anchor は 2026-07-07 から本監査時点 (2026-08-27) まで51日間変化していない。
materialized packet 3件は全て FRESH と判定される。

**すなわち、実装された唯一の変化検知機構 (anchor 不一致) は、本番データにおいて
一度も STALE を出力したことがない。** 検知経路が実際に発火した記録は存在しない。

#### 5.2 対照: 時間軸では実害が発生していた

`governance/write_path/restore/schema.py:4-8`:

```
Legacyは immutable / restore_5points / session_context / generated_at の
4フィールドのみで、生成コード自体が存在しなかった。
その結果、2026-05-28生成のまま約8週間、無警告で新規セッションへ注入され続けた(TODO_439)。
```

本監査で `PlanningCaliber/fp/restore_packet.json` の `generated_at` を確認:

```
generated_at = 2026-05-28T09:02:46.225Z   (本監査時点で約91日経過)
```

TODO_439 発見時点から更に日数が経過している。当該ファイルは
`app.py:1661` の `/get_restore_packet` から現在も配信可能な状態にあり、
このルートには freshness gate が存在しない (`generated_at_age_sec` の算出のみ、
`app.py:1681-1686`)。すなわち **TODO_439 で認識された staleness そのものは
新経路の追加によって迂回されただけで、旧経路上では解消されていない。**

さらに `content.js` の fallback 構造 (`:296-313`) により、
`/get_restore_packet_v1` が非OK応答または例外を返した場合、
freshness gate を持たない Legacy 経路へ自動的に縮退する。

---

### LEVEL 6 - Execution Blocking: **PARTIAL**

Detection -> Decision -> Blocking -> No Consequence の因果経路を対象別に判定する。

| Blocking Point | Status | Evidence | 因果経路の完全性 |
|---|---|---|---|
| GL7_EXECUTION_BLOCKED | **YES** | `mocka_mcp_server.py:493-498`。abort 検出時に tool 本体へ到達せず JSON エラーを返す | Detection (git status) -> Decision (check_abort_conditions) -> Blocking (early return) -> No Consequence。**6章で実測により確認** |
| GL_FAIL_CLOSED | YES | `mocka_mcp_server.py:481-486`, `:500-508`。Governance Pipeline 初期化失敗時・例外時も READ_ONLY_TOOLS 以外を停止 | Fail Closed 設計として完結 |
| Mode C 縮退注入 | **PARTIAL** | `content.js:279-292`。STALE 検出時に restore_5points / session_context を注入せず、immutable層のみ注入 | 完全阻止ではなく縮退。ただしこれは WP-05 の設計どおり (Mode C)。dynamic context という Consequence は確実に発生しない |
| control_action | YES (ただし判定ではない) | `phi_os/context/control_gate.py:60-73`。`before_control_action()` は常に `{"result":"REJECT","reason":"H2_3_PENDING"}` 固定、`control_action()` は常に例外 | 恒久無効化スタブ。条件分岐・policy評価を一切含まない設計 (H2-3未確定のため) |
| 時間経過を根拠とする Blocking | **ABSENT** | 該当なし | M6 (OAuth) のみが唯一の時間ベース拒否だが、3.3 のとおり実行可否に影響しない |
| Authority/Permission 失効を根拠とする Blocking | **ABSENT** | 該当なし | 検知機構自体が不在 (LEVEL 5) |

警告・ログのみの箇所を Blocking と認定していない。該当例として `app.py:1681-1686` の
`generated_at_age_sec` (測定のみ) を除外した。

Gap: 物理ゲート (GL7) の Blocking は完全に機能している。
Authority Continuity 軸の Blocking は Consumer 側で縮退として実装されている。
時間軸の Blocking は存在しない。

---

### LEVEL 7 - Reproducible Validation: **ABSENT**

| Case | シナリオ | Status | Evidence |
|---|---|---|---|
| **A** | T0 valid / Tn valid -> execution permitted | **PARTIAL (テスト無し)** | events.db 記録に"隔離port5098でHTTP経由の動作を実証。packet_id=RP_DCWP001_002, sequence=2, Fresh=True"とあり一度は実証済。ただし**再現可能なテストファイルは存在しない**。同記録に Not verified: Live Chrome Extension runtime execution / Browser DOM injection と明記 |
| **B** | T0 valid / Tn authority revoked -> execution blocked | **ABSENT** | 検知機構自体が実行経路に無い (LEVEL 3/5)。テストも無し |
| **C** | T0 valid / Tn permission changed -> execution blocked | **ABSENT** | 同上 |
| **D** | T0 evidence valid / Tn evidence stale -> blocked or explicitly governed | **ABSENT** | 1.1 のとおり構造的に判定不能。テストも無し |
| **E** | governance anchor changed before execution -> expected behavior verified | **ABSENT** | 後述 7.1 |

#### 7.1 Case E: fixture は存在するがテストが存在しない

`governance/write_path/restore/fixtures.py:38-42`:

```python
# Freshness Contract不一致確認用(governance_anchor_hashが異なる = STALE_CONTEXT)
EXAMPLE_RESTORE_PACKET_V1_STALE = {
    **EXAMPLE_RESTORE_PACKET_V1,
    "packet_id": "RP_20260722_stale",
    "governance_anchor_hash": "0" * 64,
}
```

STALE を再現するための fixture は用意されている。しかし本監査で確認した結果:

- `tests/` 配下 (10エントリ) に `write_path` を参照するファイルは**ゼロ**
- `phi_os/tests/` 配下 (15ファイル) にも**ゼロ**
- `pytest.ini` にも write_path に関する設定なし
- `EXAMPLE_RESTORE_PACKET_V1_STALE` を使用するコードはリポジトリ全体に**存在しない**

本監査が実行した 1.1 の検証が、この fixture が使用された初めての記録となる可能性が高い
(監査目的の read-only 実行であり、テスト追加は行っていない)。

#### 7.2 Consumer 側 (実際の enforcement point) にテスト基盤が無い

`tools/mocka-bridge/extension/` 配下の構成:

```
background.js  background.js.bak  config.js  content.js  icon.png
icons  manifest.json  mataka_patch.js  mocka_perplexity.js
style.css  turn_counter_patch.js
```

`*.test.js` / `*spec.js` は本リポジトリ全体に存在しない。
Fresh/Stale 判定という MoCKA の Temporal Validity enforcement が実際に行われている唯一の箇所
(`content.js:269`) に対する自動検証は皆無である。E記録上の検証も
"node --check で構文OK、フォールバック構造をコードレビューで確認"に留まる。

#### 7.3 UNVERIFIED として保存する項目

events.db の記録によれば `PlanningCaliber/workshop/phi-os/phios/context_assembly/` に
`freshness.py` と `tests/test_context_builder_stale.py` が存在し、7テスト PASS とある
(閾値300秒は暫定値と明記)。しかし `.gitignore:65` により workshop 配下は本clone に不在であり、
Canonical source を確認できない。**UNVERIFIED** として保存する。
これが実在する場合、MoCKA エコシステム内で唯一の時間ベース鮮度判定の再現テストとなるが、
対象は MoCKA 本体ではなく PHI-OS 製品側の Context Assembly Layer である。

同記録に併記された `PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md` の SIM-001/SIM-002 は
"実装が存在しないため全てのSimulationは机上トレースであることを明記"とあり、
再現可能テストには該当しない。

---

### LEVEL 8 - Operational Verification: **ABSENT**

単発テストと運用監視を混同しないため、両者を分離して判定する。

| 監視対象 | Status | Evidence |
|---|---|---|
| Canary CI の実行鮮度 | YES | `interface/health_check.py:146,329-362`。`stale_days=7` 超過で FAIL |
| Relay 拡張の生存 | YES | 同 `:119,447-460`。`stale_seconds=300` 超過で FAIL |
| Governance anchor の drift | **ABSENT** | health_check.py に anchor / seal を参照する処理は存在しない (grep 確認済) |
| Restore packet の freshness | **ABSENT** | 継続監視する仕組みが存在しない |
| Authority / Permission の失効 | **ABSENT** | 監視対象となる状態自体が存在しない |
| Legacy restore_packet の staleness | **ABSENT** | 91日経過した packet が無警告で配信可能な状態 (5.2) |

health_check.py が持つのは**実行系の liveness 監視**であり、
**authorization の temporal validity 監視**ではない。両者は次元が異なる。
この区別自体は MoCKA 内で既に確立している (events.db 記録:
"audit_trigger=正しさの監査、CI heartbeat=実行系の生存確認、次元の異なる役割として明確に区別")。

決定的な事実として、5.1 のとおり **anchor 不一致が一度も発生していないため、
Temporal Validity の enforcement 経路が運用下で作動した実績が存在しない。**
機構は実装され、経路に接続され (Consumer側)、しかし運用上一度も検証されていない。

---

## 3. 総括表

| Level | Capability | Status | Evidence | File/Line | Gap |
|---|---|---|---|---|---|
| 0 | Problem Recognition | **YES** | Memory Freshness Contract / Gap-003 / TODO_439 / IC_20260724_004 | `docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`:61-77 / `PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md`§4 / `governance/write_path/restore/schema.py`:4-8 | 認識された Gap-003 (鮮度閾値) が未解消のまま |
| 1 | Design Specification | **PARTIAL** | WP-05 Freshness Contract / Mode C / HG-WP-05 | `governance/write_path/restore/schema.py`:10-20 | 時間軸の仕様が明示的に棚上げ (決めないことに列挙)。唯一の時間層仕様 O0-v2 は Δt をトリガにしないことを規定、かつ NON-CANONICAL |
| 2 | Mechanism Implementation | **YES (軸A) / PARTIAL (軸B)** | is_fresh / supersede chain / OAuth expiry / health_check staleness | `.../restore/schema.py`:95-100 / `.../restore/materializer.py`:41-64 / `mocka_mcp_server.py`:1362,1382 / `interface/health_check.py`:329-362 | Authority に時間フィールド不在。expires_at は全レコードで null かつ read 側コード不在 |
| 3 | Execution Path Integration | **PARTIAL** | GL7 は完全接続。freshness は Consumer 側のみ接続 | `mocka_mcp_server.py`:492 / `app.py`:1688-1719 / `content.js`:266-292 | `check_freshness_against_current_anchor()` 呼び出し元ゼロ。ExecutionGate 呼び出し元ゼロ。AuthorityManager 実行経路未接続。access_token が実行経路で未検証 |
| 4 | Pre-Execution Revalidation | **PARTIAL** | git status 都度実行 / anchor 都度再読込 | `structural/execution_governance.py`:108 / `app.py`:1697 | evidence/authority/permission/decision の実行直前再検証は全て ABSENT。grounding は 60秒 TTL |
| 5 | Change Detection | **PARTIAL** | anchor 不一致検知 / filesystem 変化検知 | `.../restore/schema.py`:100 / `content.js`:269 | 時間経過・authority revoked・permission changed・decision superseded は検知不能。anchor は51日間不変で一度も発火せず |
| 6 | Execution Blocking | **PARTIAL** | GL7_EXECUTION_BLOCKED (実測済) / Mode C 縮退 | `mocka_mcp_server.py`:493-498 / `content.js`:279-292 | 時間経過・authority 失効を根拠とする Blocking は存在しない。Blocking 位置が governed runtime 外 (Chrome拡張) |
| 7 | Reproducible Validation | **ABSENT** | Case A のみ一度の手動実証記録あり | `fixtures.py`:38-42 (STALE fixture は存在するがテスト不在) | Case B/C/D/E のテストは皆無。write_path を参照するテストファイルがゼロ。拡張側に JS テスト基盤なし |
| 8 | Operational Verification | **ABSENT** | health_check の staleness 監視は liveness 対象 | `interface/health_check.py`:146,329-362,447-460 | anchor drift / packet freshness / authority freshness の継続監視は不在。enforcement 経路の運用下作動実績ゼロ |

---

## 4. CURRENT IMPLEMENTATION BOUNDARY

単一の直線では表現できないため、2軸 x 2経路で確定する。

```
軸A (Authority Continuity / governance anchor 一致)
  Context Injection 経路 (app.py -> content.js):
      IMPLEMENTED THROUGH LEVEL 6.
      LEVEL 7 NOT ESTABLISHED.
  MCP Tool Execution 経路 (execute_tool):
      IMPLEMENTED THROUGH LEVEL 2.
      LEVEL 3 NOT ESTABLISHED.

軸B (Time / Staleness)
  全経路:
      IMPLEMENTED THROUGH LEVEL 1 (PARTIAL, かつ明示的に棚上げ).
      LEVEL 2 NOT ESTABLISHED (認可・証拠の時間失効機構として).
      注: OAuth code 失効 (M6) と health_check 鮮度監視 (M8) は
          実装済だが、いずれも authorization の temporal validity を
          対象としていないため本軸の Level 2 とは認定しない。

物理ゲート (GL7 / filesystem present-state)
  MCP Tool Execution 経路:
      IMPLEMENTED THROUGH LEVEL 6.
      LEVEL 7 PARTIAL (structural/gl_integration_test.py, dogfood_run.py が存在).
      LEVEL 8 NOT ESTABLISHED.
```

一行での要約が必要な場合:

```
TEMPORAL VALIDITY IS IMPLEMENTED THROUGH LEVEL 6 ON THE AUTHORITY-CONTINUITY AXIS
FOR THE CONTEXT-INJECTION CONSEQUENCE ONLY, WITH LEVEL 7 NOT ESTABLISHED;
ON THE TIME AXIS AND FOR THE TOOL-EXECUTION CONSEQUENCE, LEVEL 3 IS NOT ESTABLISHED.
```

前回監査の"設計 YES / 機構実装 PARTIAL / 実行経路 未接続 / 運用検証 ABSENT"との差分:

- 実行経路は**未接続ではない**。Context Injection 経路については Level 3-6 まで接続され、
  Mode C 縮退という形で Blocking まで到達している (`content.js:269-292`)。
  前回監査が"未接続"と判定したのは、enforcement point が Python 側ではなく
  Chrome拡張の JavaScript 側にあるためと推定される。
- ただし MCP Tool Execution 経路については前回判定どおり未接続である。
- 運用検証 ABSENT は追認される。加えて、**検知機構が運用下で一度も発火していない**
  ことを実データで確定した (5.1)。

---

## 5. 全機構の5分類

### 5.1 Confirmed implemented (定義され、呼ばれ、到達可能で、実行が確認された)

| 機構 | file:line | 確認方法 |
|---|---|---|
| GL7 Dry Run / abort 判定 | `structural/execution_governance.py`:102-179 | 本監査中に実際に `GL7_EXECUTION_BLOCKED` を受領 (6章) |
| GL7 の execute_tool への接続 | `mocka_mcp_server.py`:492-498 | 同上 |
| Default Deny (READ_ONLY_TOOLS 以外は全て GL7 対象) | `structural/governance_pipeline.py`:31-50,109 | 同上。書込系tool が実際に阻止された |
| `is_fresh()` の判定ロジック | `governance/write_path/restore/schema.py`:95-100 | 本監査で Canonical source を実行し fixtures 3件で挙動確認 |
| Restore Packet v1 schema validation | 同 :66-92 | 同上 (validate_errors=[] を確認) |

### 5.2 Implemented but disconnected (実装済だが実行経路から呼ばれていない)

| 機構 | file:line | 呼び出し元 |
|---|---|---|
| `check_freshness_against_current_anchor()` | `governance/write_path/runtime/validator.py`:72-75 | **ゼロ** |
| `ExecutionGate.run()` (Architecture/Ownership/Incident/Permission 検査) | `phi_os/context/execution_context.py`:49-252 | **ゼロ** (自モジュール外からの参照なし) |
| `AuthorityManager.revoke_delegation()` / `delegate()` / `assert_unique()` | `phi_os/runtime/authority_manager.py`:90-147 | `InstitutionRuntime` 経由のみ。同 Runtime の参照元は `production_observation.py` と tests のみ |
| `human_gate.expire()` (EXPIRED 遷移) | `phi_os/human_gate.py`:171-172 | **tests のみ** (`test_human_gate.py`:52,89) |
| `verify_revoke_event.py` (鍵失効署名検証) | `governance/verify_revoke_event.py`:1-30 | `verify_all.py`:18 から呼ばれるが、`governance/revoke_event.json` が不在のため常に no-op |
| `manifest_resolver` の revoked_at_utc チェック | `verify/manifest_resolver.py`:96-102 | `verify_all.py`:29 の条件付きステップ (`verify.manifest_resolver.py` の存在時のみ)。オフライン検証であり実行前ゲートではない |
| β の `expires_at` フィールド | `structural/bee.py`:297,334 / `beta_engine.py`:261 | 書き込み側のみ (常に None)。**読み出し側コードは存在しない** |
| `materializer.materialize()` | `governance/write_path/restore/materializer.py`:67-105 | リポジトリ内に呼び出し元なし (手動実行と推定) |

### 5.3 Reachable but unverified (実行経路上にあるが実行が確認されていない)

| 機構 | file:line | 未検証の理由 |
|---|---|---|
| `content.js` Fresh/Stale 判定と Mode C 縮退 | `tools/mocka-bridge/extension/content.js`:266-292 | Chrome 拡張の実機実行が未検証 (E記録に Not verified と明記)。本環境でも拡張ロード不可 |
| `/get_restore_packet_v1` の本番稼働 | `app.py`:1688-1719 | 隔離port5098での HTTP 実証は記録あり。本番 port5000 での稼働実測は本環境から不可 |
| OAuth authorization code 失効 (300秒) | `mocka_mcp_server.py`:1362,1382 | 経路上に存在。ただし後段の access_token 検証が無いため実行可否に影響しない (3.3) |
| health_check の stale_days / stale_seconds 判定 | `interface/health_check.py`:329-362,447-460 | 稼働確認が本環境から不可 |
| `_resolve_supersede_chain()` | `governance/write_path/restore/materializer.py`:41-64 | materialize() 自体の呼び出し実績が不明 |

### 5.4 Missing (存在しない)

| 対象 | 根拠 |
|---|---|
| Authority の有効期限表現 (issued_at / expires_at / valid_until) | `phi_os/runtime/runtime_types.py`:84-88 の Authority dataclass に該当フィールドなし |
| Permission の時間依存判定 | `phi_os/context/permissions.py`:21-38 は時刻を引数に取らない純粋関数 |
| Decision の失効・有効期限 | mocka_decision_write のスキーマに expires_at 相当なし。status の時間駆動遷移なし |
| Consequence 実行直前の decision status (Superseded/Withdrawn) 照合 | 該当コードなし |
| `governance/revoke_event.json` | ファイル自体が不在 (本監査で確認) |
| APPROVED 状態からの EXPIRED 遷移 | `phi_os/human_gate.py`:30。`"expire": {"PENDING"}` のみ。承認済リクエストは時間で失効しない |
| Freshness 閾値 (時間) の数値定義 | Gap-003 として Pending Resolution |
| Case B/C/D/E の再現テスト | tests/ phi_os/tests/ ともにゼロ |
| Chrome 拡張の JS テスト基盤 | `*.test.js` / `*spec.js` がリポジトリ全体に不在 |
| anchor drift / packet freshness の継続監視 | health_check.py に該当処理なし |
| `/mcp` エンドポイントの Authorization 検証 | `mocka_mcp_server.py`:1126-1151 および `@app.before_request`:146-150 に該当処理なし |

### 5.5 Unknown / Unverified (本環境から確定できなかった)

| 対象 | 理由 |
|---|---|
| `PlanningCaliber/workshop/phi-os/phios/context_assembly/freshness.py` と test_context_builder_stale.py (7テストPASSとの記録あり) | `.gitignore`:65 により本clone に不在 |
| 本番稼働中の app.py / caliber の実挙動 | 正本実行環境外 |
| Chrome 拡張の実機での Fresh/Stale 分岐動作 | 拡張ロード手段なし |
| decision_ledger.jsonl 全件の内容 | 本clone に不在。MCP経由で個別取得した DC_20260723_007 のみ Canonical 扱い |
| MCP サーバー稼働ホストの working tree 状態 | 6章の abort メッセージから3ファイルが dirty であることのみ判明 |

---

## 6. 監査中に実測した Runtime Divergence (T0 コード vs Tn 実行コード)

本監査は read-only 調査として設計されたが、監査プロトコル (CLAUDE.md) に従い
CHANGE_START を記録しようとした際、以下が発生した。

### 6.1 事象

`mocka_write_event` の呼び出しが2回連続で同一内容により拒否された。

```
{"error": "GL7_EXECUTION_BLOCKED",
 "reason": "GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                       'encoding_mismatch:di_terminology_inventory_20260820.txt',
                       'encoding_mismatch:s05_decision_extract.txt']",
 "thinking_mode": "audit"}
```

再試行1回を実施し、完全に同一の応答を得た (決定論的、一時的要因ではない)。

### 6.2 Canonical Evidence による分岐の特定

`encoding_mismatch` は本リポジトリの HEAD (`da4d4db`, 2026-08-12) において
**削除済み**である。

```
commit da4d4db "GL7-UNENFORCED-CONDITIONS-BUG: Remove unimplemented safety conditions"
  - Remove encoding_mismatch from ABORT_CONDITIONS
      - Never implemented in check_abort_conditions()
      - Marked obsolete in GL7最小カーネル仕様v1
  - Remove BINARY_EXTENSIONS definition
```

現行 HEAD の `structural/execution_governance.py:51-56`:

```python
ABORT_CONDITIONS = [
    "new_directory_detected",
    "unexpected_file_count",
    "deletion_outside_scope",
    "grounding_not_completed",
]
```

`encoding_mismatch` は存在しない。一方、`HEAD~1` (削除前) の
`structural/execution_governance.py:189` には以下が存在する。

```python
aborts.append(f"encoding_mismatch:{path}")
```

実行時に返された文字列 `encoding_mismatch:data/n8n/database.sqlite` は、
この `f"encoding_mismatch:{path}"` の書式と完全に一致する。
削除後のコードにこの文字列を生成しうる箇所は存在しない。

**結論: localhost:5002 で稼働中の MCP サーバーは、commit `da4d4db` (2026-08-12) より前の
`structural/execution_governance.py` を実行している。commit から本監査時点 (2026-08-27) まで
15日間、コミット済みの正本と実行中のコードが乖離したまま検知されていない。**

### 6.3 本監査における位置づけ

この事象は、本監査が対象としている T0/Tn 問題そのものの実例である。

```
T0 = 2026-08-12  commit da4d4db で ABORT_CONDITIONS が変更された時点
Tn = 2026-08-27  MCP tool が実行された時点
差分 = 実行中プロセスは T0 以前のコードを保持したまま
検知 = ゼロ (本監査が偶発的に発見するまで)
```

MoCKA には、稼働中プロセスが読み込んだコードと Canonical source の一致を
Tn 時点で検証する機構が存在しない。`data/tic/mcp_schema_hash.json` (CLAUDE.md が
`mocka_mcp_server.py` 変更後の必須手順として更新を要求する hash store) は
**本clone に存在しない** ことも併せて確認した。

### 6.4 派生する運用影響 (事実の記録のみ)

削除前の実装は `BINARY_EXTENSIONS` に `.sqlite-shm` / `.sqlite-wal` / `.db` を含むが
`.sqlite` を含まない。このため `data/n8n/database.sqlite` は UTF-8 デコードを試行され、
必ず `UnicodeDecodeError` となる。当該ファイルが working tree に dirty として存在する限り、
`READ_ONLY_TOOLS` 以外の全ての MCP tool が恒久的に阻止される。

本監査時点で `mocka_write_event` / `mocka_decision_write` / `mocka_integrity_write` /
`mocka_update_todo` / `mocka_add_todo` / `mocka_seal` / `mocka_registry_add` は
いずれも実行不能である。

### 6.5 本監査における記録義務の未達 (明示)

上記により、CLAUDE.md が要求する CHANGE_START / CHANGE_DONE の
`mocka_write_event` による記録が実施できていない。

CLAUDE.md の MCP Tool Registry Drift 対応方針に従い、
別経路 (events.db 直書き等) への代替書き込みによるワークアラウンドは**実施していない**。
また、この状態を解消するためのコード変更・working tree 操作も**実施していない**
(本監査は read-only であり、かつ Core System File 変更は Human Gate 承認事項であるため)。

本報告書の存在自体を記録の代替とみなさず、
きむら博士の判断により、MCP サーバー再起動後に遡及記録を行うことを推奨する。

---

## 7. 監査の限界

以下は本報告書が主張していないことである。

1. 本報告書は Chrome 拡張の実機動作を検証していない。`content.js:269` の Fresh/Stale 判定が
   実際のブラウザ上で期待どおり分岐することは **UNVERIFIED** である。
   Level 6 の PARTIAL 判定はコード上の因果経路の存在に基づくものであり、
   実行証跡に基づくものではない。
2. 本報告書は稼働中サーバーの挙動を、6章で記録した一点を除いて観測していない。
3. `PlanningCaliber/workshop/` 配下は一切検証できていない。同配下に本監査の結論を
   変更しうる実装が存在する可能性を排除できない。
4. 本報告書は Temporal Validity が実装されるべきか否かについて何も述べていない。
   1.1 で示したとおり、時間を判定入力から除外することは MoCKA の明示的な設計判断であり、
   本監査はそれを欠陥として扱っていない。測定したのは実装境界の位置のみである。

---

## 8. 参照した Canonical Evidence 一覧 (優先順位順)

### 優先度1: 実行可能な Canonical source (本監査で実際に実行)

- `governance/write_path/restore/schema.py` (`is_fresh` / `validate`)
- `governance/write_path/restore/fixtures.py` (3 fixtures)
- `governance/anchor_record.json`
- `governance/write_path/restore/materialized/RP_DCWP001_{001,002,003}.json`
- `structural/beta_registry.json`
- `PlanningCaliber/fp/restore_packet.json`
- localhost:5002 `mocka_write_event` (2回、いずれも GL7_EXECUTION_BLOCKED)
- localhost:5002 `mocka_decision_get(DC_20260723_007)`

### 優先度2: 実コード

- `structural/execution_governance.py` (HEAD および HEAD~1)
- `structural/governance_pipeline.py`
- `structural/event_recency.py`
- `mocka_mcp_server.py`
- `app.py` (`/get_restore_packet`, `/get_restore_packet_v1`)
- `tools/mocka-bridge/extension/content.js`
- `phi_os/human_gate.py`
- `phi_os/runtime/authority_manager.py`, `runtime_types.py`
- `phi_os/context/permissions.py`, `control_gate.py`, `access_gate.py`, `execution_context.py`
- `governance/write_path/runtime/validator.py`
- `governance/write_path/restore/materializer.py`
- `governance/human_gate_continuity.py`
- `governance/verify_revoke_event.py`, `sign_revoke_event.py`, `verify_approval_flow.py`
- `verify/manifest_resolver.py`, `verify_all.py`
- `interface/health_check.py`
- `structural/bee.py`, `structural/beta_engine.py`

### 優先度3: 実行経路

- 3.1 に記載した2経路のトレース

### 優先度4: テスト

- `phi_os/tests/test_human_gate.py` (expire の唯一の呼び出し元)
- `tests/` 配下10エントリ (write_path 参照ゼロを確認)

### 優先度5: 永続監査記録

- decision: DC_20260723_007 (MCP経由取得)
- events.db: Phase8-1 / 8-2 / 8-4 の CHANGE_DONE 記録、
  PHI_MEMORY_ACCESS_CONTROL_POLICY / PHI_RUNTIME_SIMULATION_SCOPE /
  PHI_RUNTIME_BINDING_ARCHITECTURE 作成記録、
  PHIOS_CONTEXT_ASSEMBLY 実装記録
- `MOCKA_TODO_ACTIVE.json` (IC_20260724_004 関連エントリ)
- `MOCKA_OVERVIEW.json` current_view (seal_status)

### 優先度6: 設計文書

- `docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`
- `docs/audits/PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md`
- `docs/audits/PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md`
- `docs/experimental/meta/o0_v2_temporal_annotation_layer_v1.md` (NON-CANONICAL)

### 優先度7: 説明・コメント

- 各モジュールの docstring (本文中に引用したもの)

---

以上

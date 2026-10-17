# MoCKA MASTER MAP (v0.1)

作成日: 2026-10-10 / 方法: 静的確認(一覧・ヘッダ読取・grep参照)と読取専用のDB件数取得
対象: MoCKAリポジトリ `C:/Users/sirok/MoCKA`

本書は'何がどこにあり、何を読み、何を使い、何を次に実装すべきか'を人間とAIが同じ地図から判断するための入口である。
状態語彙(PRESENT / CONNECTED / USED / ENFORCED / VERIFIED / UNKNOWN / NOT_VERIFIED)の定義は [SCHEMA.md](SCHEMA.md) を参照する。
資産の一覧は [ASSET_INDEX.json](ASSET_INDEX.json)(A001-A074)、関係は [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md)、機能は [CAPABILITY_MAP.md](CAPABILITY_MAP.md)、作業は [WORK_MAP.md](WORK_MAP.md)、記憶は [MEMORY_INDEX.md](MEMORY_INDEX.md)、未確認事項は [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) にある。

所在・階層の入口は [LOCATION_GUIDE.md](LOCATION_GUIDE.md) である。ファイル単位の所在は [FILE_LOCATION_INDEX.csv](FILE_LOCATION_INDEX.csv)、ディレクトリ単位は [DIRECTORY_INDEX.csv](DIRECTORY_INDEX.csv) を参照する。

注意: 本書の'USED''ENFORCED''VERIFIED'は、本作業で実行証拠を取得した場合にのみ使う。大半は `NOT_VERIFIED` である。存在することは利用可能であることを意味しない。

---

## 1. 目的・原則・制度上の境界

| 項目 | 内容 | 出典 |
|---|---|---|
| 定義 | Model of Cybernetic Knowledge Architecture。AIではなく、知識の記録・検証・証明を制度として行うモデル | [data/MOCKA_OVERVIEW.json](../data/MOCKA_OVERVIEW.json) (what_is_mocka) |
| 起源 | RECORD / VERIFY / INHERIT (記録・検証・継承)。AIは信用せず制度で縛る | [docs/MOCKA_ORIGIN.md](../docs/MOCKA_ORIGIN.md) |
| 憲法的原則 | イベント台帳は追記専用。判断は5W1H。Infieldは内部記憶、Outfieldは協働面。イベント履歴が唯一の正本 | 同上 (constitution 項目) |
| 三要素 | Structure(システムで縛る) / Record(記録なき作業は存在しない) / Verification(検証) | [AGENTS.md](../AGENTS.md), [.claude/CLAUDE.md](../.claude/CLAUDE.md) |
| 命名 | 正規名称は FIXED (mocka_receptor, mocka_Movement 等) | [docs/NAMING_CONVENTION.md](../docs/NAMING_CONVENTION.md) |
| 符号化 | 全テキストは UTF-8 正規形。未指定 encoding 禁止。文字化け検知時は HALT | [CONSTITUTION.md](../CONSTITUTION.md) (実体はエンコーディング規約) |
| 制度上の境界 | 認可権限は Human Gate (HG) に帰属。Evidence は Authority ではない。UNKNOWN は FALSE ではない。権限を持たない記録は実行を許可しない | [AI_BOOT_HUB.md](../AI_BOOT_HUB.md), [docs/governance/](../docs/governance/) 配下の各規約 |

本台帳の作成は HG の設計選択、実装認可、テスト実行認可を含まない。

---

## 2. 主要システムと責任範囲

| システム | 責任 | 主な所在 |
|---|---|---|
| Event Ledger | 唯一のイベント台帳(SQLite, 追記専用と宣言) | `data/mocka_events.db` [A032] |
| MCP Server | AI(Claude等)向け内部標準I/F。読書・TODO・Decision・Integrity・Seal | [mocka_mcp_server.py](../mocka_mcp_server.py) (port 5002) [A019] |
| COMMAND CENTER | 管理UI兼HTTP API | [app.py](../app.py) (port 5000) [A020] |
| Gateway | AI Connector 層(GPT/Gemini/Copilot)。context/todo/essence/event | [gateway/](../gateway/) (port 5010, 内部用) [A021-A024] |
| PHI-OS | Event Gate(イベント単一入口), Human Gate(承認状態機械), Integrity(署名・ハッシュチェーン), HAB | [phi_os/](../phi_os/) [A029-A031] |
| Human Gate (HG) | 人間の承認・却下・期限切れ・昇格要求 | [phi_os/human_gate.py](../phi_os/human_gate.py) [A030] |
| Memory | MoCKA 3.0 記憶層。4分類(episodic/semantic/procedural/skill)と保存ポリシー。別系統の memory_core と feedback を含む | [memory/](../memory/) [A025-A026], [core_kernel/memory_core](../core_kernel/memory_core) [A055], [feedback/](../feedback) [A056] |
| Relay | 状態を持つ中継カーネル(プロセス内state、DB永続化なし)とReplay | [relay/](../relay/) [A027-A028] |
| Orchestra | (a) ブラウザ自動化の多AI実行スクリプト、(b) イベント駆動の実行エンジン core_kernel。二つは別物 | [tools/mocka_orchestra_v10.py](../tools/mocka_orchestra_v10.py) [A042], [core_kernel/orchestra/](../core_kernel/orchestra/) [A043] |
| RCL Governance Runtime | 判断・認可の実行経路と Memory 証拠の統合(本番経路での使用は未検証) | [core_kernel/governance/runtime/rcl/](../core_kernel/governance/runtime/rcl/) [A044] |
| Ledger (JSON) | 別系統の主要台帳として宣言された JSON 台帳 | [runtime/main/ledger.json](../runtime/main/ledger.json) [A051] |
| Decision Ledger | 裁定の記録(mocka_decision_write 経由) | [data/decisions/](../data/decisions/) [A047] |
| TODO | 作業台帳 | [data/MOCKA_TODO_ACTIVE.json](../data/MOCKA_TODO_ACTIVE.json) [A035] |
| Essence | AI向け制度哲学・行動指針 | [interface/lever_essence.json](../interface/lever_essence.json) (Claude用) [A039], [data/lever_essence.json](../data/lever_essence.json) (Gateway用) [A040] |
| Caliber | 要約・重要文抽出のローカルパイプライン | [caliber/chat_pipeline/mocka_caliber_server.py](../caliber/chat_pipeline/mocka_caliber_server.py) (port 5679) [A050] |
| Bridge | Chrome拡張の連携(MoCKA Bridge) | [tools/mocka-bridge/](../tools/mocka-bridge/) [A049] |
| HAB / JARVIS | 人間権限境界の設計文書(HAB)。JARVIS は監査資料のみ確認、実装体は未特定 | [phi_os/hab/](../phi_os/hab/) [A014 近傍], [docs/audits/JARVIS_CAPABILITY_INVENTORY.md](../docs/audits/JARVIS_CAPABILITY_INVENTORY.md) [A015] |

---

## 3. 所在と関係(要約)

- 全体の正本は、イベント台帳 `data/mocka_events.db` と、外部の `C:/Users/sirok/MOCKA_OVERVIEW.json` (リポジトリ外、primary と宣言) に分かれる。
- MCP(5002)・COMMAND CENTER(5000)・Gateway(5010)・Caliber(5679) は、いずれも台帳を読書する。書込の経路は MCP と Event Gate に集中して見える(静的確認)。
- Event Gate は全イベントの単一入口と宣言されるが、すべての書込がこの経路を通ることの証明は未実施。
- Human Gate は phi_os/human_gate.py の状態機械と、events.db の human_gate_events(2,195行)として存在する。実行を止める強制(ENFORCED)は未検証。
- Memory は3系統に分かれて存在する: memory/ (MoCKA 3.0 本体, A025)、core_kernel/memory_core (A055)、feedback/ (強化提案, A056)。memory 層を参照する .py は31件あり、大半は core_kernel/governance/runtime/rcl と feedback/ 配下である。gateway・mocka_mcp_server・app.py からの参照は見つからない。3系統の関係は未確認。
- Relay は relay/ が Python 実装、PlanningCaliber/workshop/Relay_Project/extension/ が拡張機能の正本として宣言されている。役割が異なる。

関係の詳細は [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md)。

---

## 4. 主要入口・API・イベント経路・データ保存先

| 入口 | 種別 | 保存先・読取元 | 状態 |
|---|---|---|---|
| mocka_mcp_server.py /mcp (port 5002) | MCP HTTP (公開 23 tools、分岐 25) | data/mocka_events.db, data/MOCKA_TODO_ACTIVE.json, data/decisions/ | CONNECTED (static) / USED 未検証 |
| app.py (port 5000) | Flask 40+ ルート | 各種 (orchestra, collaborate, integrity/status 等) | CONNECTED (static) |
| gateway/gateway.py (port 5010) | Flask /api/v1/* 8 ルート | context: events.db 読取。event(POST): HMAC検証 | CONNECTED (static) |
| gateway/context_builder.py | 関数 build(mode) | events.db 読取、TODO、Essence | CONNECTED (static) |
| phi_os/event_gate.py | Blueprint: receive_event, batch 等 | events.db 書込 (_write) | CONNECTED (static) |
| phi_os/human_gate.py | http_submit / approve / reject / status / pending | events.db human_gate_events | CONNECTED (static), 強制 未検証 |
| tools/mocka_auto_record.py | Claude Code PostToolUse フック | MCP 経由で CHANGE_DONE | CONNECTED (static), 発火 未検証 |
| relay/mcp_bridge.py | Relay の MCP ブリッジ | (未確認) | NOT_VERIFIED |
| tools/mocka_orchestra_v10.py | CLI (Playwright) | 外部 AI サービス画面 | 外部送信を伴うため未実行 |
| data/mocka_events.db | SQLite | 24,753 events 他 (読取専用で件数取得) | PRESENT / USED (行の存在による) |

イベントの経路は'入口 -> event_gate/MCP -> events.db'と静的に読める。実際の全経路の証拠は未取得である。

---

## 5. 設計資料・実装・設定・実行時証拠の参照先

| 区分 | 参照先 | 注意 |
|---|---|---|
| 設計資料 | [docs/architecture/](../docs/architecture/), [ARCHITECTURE.md](../ARCHITECTURE.md), [docs/governance/](../docs/governance/) (390件) | 個別の現行性は未確認 |
| 監査資料 | [docs/audits/](../docs/audits/), root の KUROKO_PC_*.md (12件) | 過去時点の報告。現行証明ではない |
| 既存の Synapse 監査 | [KUROKO_PC_SYNapse_MASTER_MAP_20261003.md](../KUROKO_PC_SYNapse_MASTER_MAP_20261003.md), [KUROKO_PC_MOCKA_KNOWLEDGE_GRAPH_20261003.md](../KUROKO_PC_MOCKA_KNOWLEDGE_GRAPH_20261003.md) | 再利用する。Synapse は Knowledge Activation として設計済み、接続は未確認 |
| 実装 | [mocka_mcp_server.py](../mocka_mcp_server.py), [app.py](../app.py), [gateway/](../gateway/), [phi_os/](../phi_os/), [memory/](../memory/), [relay/](../relay/) | 多くが git 上で変更中(M) |
| 設定 | [.claude/CLAUDE.md](../.claude/CLAUDE.md), [.claude/settings.local.json](../.claude/settings.local.json), [.claude/mocka_config.json](../.claude/mocka_config.json), [.env](../.env) | .env の値は本台帳に記載しない |
| 実行時証拠 | [data/mocka_events.db](../data/mocka_events.db) の各テーブル (読取専用で件数のみ取得), [tools/auto_record.log](../tools/auto_record.log) | サーバーの稼働は未確認 |
| 権限境界の決定記録 | [DC_HG_20261010_P1_1_EXECUTION_GRAPH_FAIL_CLOSED_AUTHORIZATION_REQUEST_001.md](../DC_HG_20261010_P1_1_EXECUTION_GRAPH_FAIL_CLOSED_AUTHORIZATION_REQUEST_001.md), [HG_DECISION_TICKETS_D-A_TO_D-D_20261010.md](../HG_DECISION_TICKETS_D-A_TO_D-D_20261010.md) | 作成日 2026-10-10。内容は未読。HG 判断の証拠ではない |

---

## 6. 現在の主要作業・停止中の作業・未解決事項

詳細は [WORK_MAP.md](WORK_MAP.md)。要点:

- TODO の状態(data/MOCKA_TODO_ACTIVE.json, 92件): 未着手 52 / 完了 15 / 保留 13 / 進行中 10 / 保留(設計範囲確定済み) 1 / 廃止 1。
- 進行中の代表: TODO_221, TODO_220, TODO_242 (PR-OS/WordPress 系), TODO_425, TODO_428, TODO_437, TODO_445, TODO_448, PHI-OS-HUMAN-GATE-STATE-MODEL-V1 など。
- MOCKA_OVERVIEW の immediate: TODO_207 (TIC Layer 4 Human Gate UI), TODO_206 (impact_analyzer), TODO_205 (Sandbox)。
- 未解決: 現行 TODO と MOCKA_OVERVIEW の鮮度差(staleness_note 2026-07-07 時点の注記)、git 上の大量の未コミット変更。

---

## 7. Synapse 実装につながる接続候補

Synapse 専用の新機構は発明しない。既存の KUROKO 監査(A017)は、Synapse を MoCKA の Knowledge Activation(Gen9)と同一視し、未接続と結論づけている。本台帳はその結論を再利用し、接続候補のみを列挙する。

| 候補 | 接続元 -> 接続先 | 既存の手段 | 接続の証拠 | データ流れの証拠 | 意図した結果の証拠 |
|---|---|---|---|---|---|
| C1 文脈への注入 | events.db/TODO -> gateway/context_builder.py -> AI | build(mode) | CONNECTED (static) | NOT_VERIFIED | NOT_VERIFIED |
| C2 記憶の検索 | memory/memory_store.json -> memory_retriever.py -> 呼出元 | retrieve(intent) | CONNECTED (static: 内部のみ) | NOT_VERIFIED | NOT_VERIFIED |
| C3 MCP による読取 | AI -> mocka_search / mocka_get_* -> events.db | MCP tools | CONNECTED (static) | NOT_VERIFIED | NOT_VERIFIED |
| C4 RCL の Memory 証拠統合 | rcl memory_evidence_integration -> memory | テストで参照 | CONNECTED (static: テスト) | NOT_VERIFIED | NOT_VERIFIED |
| C5 Human Gate による昇格 | Reason Unit -> phi_os/human_gate.py (promotion) -> Knowledge Asset | submit_reason_promotion 等 | 関数定義を確認 | NOT_VERIFIED | NOT_VERIFIED |

再利用可能な機能は、C1 (context_builder)、C3 (MCP tools)、C5 (HG 昇格要求)。不足部分は、Memory から文脈への経路(C2 の利用側)と、Knowledge Asset の正本(未実装と A013 が記す)。

2026-10-10 の実証 (SYNAPSE_CHAIN_VERIFICATION.md): C3 (mocka_search -> mocka_read_event -> 原本) は実行証拠つきで成立。C2 (MemoryRetriever) は読取で動作するが関連性は弱い。C1, C4, C5 は未実証。Synapse の本来の効果 (知識が行動を変える) は未実証。

いずれの候補も、上記以外は実動検証は未実施である。検証はサーバー起動や DB 書込を伴うため、利用者の許可を得てから行う。

---

## 8. 既存機能の再利用候補

| 候補 | 理由 | 状態 |
|---|---|---|
| mocka_mcp_server.py の公開 MCP ツール 23 件 (分岐 25) | 読書・TODO・Decision・Integrity・Seal が揃う。tools/list・tools/call の応答を 2026-10-10 に確認 | CONNECTED (runtime_read) |
| gateway/context_builder.py | 3 モードの文脈生成が既にある | CONNECTED (static) |
| phi_os/event_gate.py | イベント単一入口・validate・idempotency | CONNECTED (static) |
| phi_os/human_gate.py | 承認状態機械と昇格要求 | CONNECTED (static) |
| phi_os/integrity.py | 署名・ハッシュチェーン | CONNECTED (static) |
| memory/memory_registry.py / memory_retriever.py | 記憶分類・保存ポリシー・検索 | CONNECTED (内部) |
| governance/mocka_git_safe_commit.py | git 操作の一元ヘルパー | CONNECTED (static) |
| tools/mocka_auto_record.py | 変更の自動記録 | CONNECTED (static) |

---

## 9. 未確認・矛盾・重複・孤立資産

詳細は [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)。主なもの:

- 重複: MOCKA_OVERVIEW の二重(repo mirror と外部 primary、ハッシュ不一致)。TODO の二重(ACTIVE と全件版)。Essence の二重(Claude 用と Gateway 用、別ファイルと宣言)。
- 同名の別層: relay/ と PlanningCaliber/workshop/Relay_Project/、memory/ と PlanningCaliber/workshop/memory/、Orchestra 三系統(tools/ の Playwright、core_kernel/orchestra、PlanningCaliber/workshop/Orchestra_Project)。
- 名称の不一致: CONSTITUTION.md は実際にはエンコーディング規約。
- 台帳の二重: events.db と runtime/main/ledger.json のどちらが台帳か未確定。
- 旧仕様の残存: interface/router.py は events.csv を前提とする。MOCKA_OVERVIEW は CSV を廃止済みと記す。
- 所在不明: planning_caliberB (指示書の名称) は未検出。JARVIS の実装体は未特定。GLK_RUNTIME_BRIDGE_v1.md はホームディレクトリ直下にあり、MoCKA 内には無い。
- 孤立の可能性: ADR は ADR-001.md のみ。Memory の本番利用経路は未確認。

---

## 10. 次に実装するべき作業と判断根拠

根拠は、本台帳で確認した不一致と未接続箇所である。優先順位は、低リスクで検証可能なものを先とする。

| 順位 | 候補 | 根拠 | 必要な許可 |
|---|---|---|---|
| 1 | 正本マップの確定: OVERVIEW 二重・TODO 二重・Essence 二重の正本宣言の照合 | 三系統の重複が確認された (A033/A034, A035/A036, A039/A040)。正本の誤りは作業を誤った場所へ導く | 読取のみで可 |
| 2 | 台帳の二系統(events.db と runtime/main/ledger.json)の関係調査 | 'single source of truth' と矛盾しうる | 読取のみで可 |
| 3 | 接続の実動検証計画の作成(C1-C5) | 接続は静的にしか確認していない | 計画のみ可。実行は別許可 |
| 4 | 旧 CSV 前提の除去計画 (interface/router.py) | 廃止済みと宣言された資産への参照が残る | 計画のみ可 |
| 5 | JARVIS 実装体の特定 | 文書のみで実装体が未特定 | 読取のみで可 |
| 6 | Synapse(Knowledge Activation)の接続点の HG 判断 | 設計は済み、実装は延期。接続は HG 判断事項 | HG 判断が必要 |

本作業では、いずれの候補も実行していない。実装は本台帳の確認と、利用者の判断を経て行う。

## 11. 完成度の点検 (2026-10-10, 読取のみ)

区分: COMPLETE_WITH_EVIDENCE (根拠があり目的に対して利用可能) / PARTIAL (一部整理、不足あり) / NOT_VERIFIED (存在だけでは目的を満たすか確認できない) / MISSING (調査範囲で見つからない) / BLOCKED_BY_HG (人間の判断・権限が必要)。区分の名称だけで完了とみなさない。

| 目的の項目 | 区分 | 根拠 (確認済み) | 未確認・限界 |
|---|---|---|---|
| 1. 何があり、どこにあるか (主要資産の所在) | COMPLETE_WITH_EVIDENCE | ASSET_INDEX の 59 件すべての path と absolute_path を、verify_mapping.py が存在確認 | 各資産の中身の正しさは、全件は未確認 (evidence の kind による) |
| 2. 各資産が何を提供できるか | PARTIAL | MCP (公開 23 件)、Gateway (8 ルート)、COMMAND CENTER (109 ルート定義) は定義を確認。MCP と Gateway の一部は応答を確認 | COMMAND CENTER の個別ルートの応答は未確認。Relay、Orchestra、Caliber の実行は未確認 |
| 3. どの機能がどの機能を呼ぶか (呼出し関係) | PARTIAL | DEPENDENCY_MAP の大半は grep による静的参照。Memory retriever は rcl と feedback から呼ばれる | 実行時の呼出しは、Memory を除き未確認。全経路の Event Gate 通過は未確認 |
| 4. 接続の確認 (経路ごと) | PARTIAL | 読取の経路 (mocka_search -> mocka_read_event -> 原本) は実行確認。Gateway health と phase は応答を確認 | 判断への接続 (decision_outcome) は、呼出し元がテストのみ (Q-42)。HG の強制は未検証 |
| 5. Memory、Mapping、Synapse の実装と未接続 | PARTIAL | Memory: 180 件の読取と retrieve の実行を確認。Mapping: 検証器が動く。Synapse: 読取経路のみ確認 | Memory から判断への接続は未確認。Memory から台帳への参照は解決不能 (Q-35)。Synapse の効果は未検証 |
| 6. 既存機能の再利用 | PARTIAL | MCP の 23 ツール、mocka_search、MemoryRetriever、context_builder、event_gate、integrity は、呼出しを確認した範囲で再利用可能 | 判断に使う前に、Memory の関連性 (Q-38) と参照整合性 (Q-34、Q-35) の解決が要る |
| 7. 特定できない機能・依存・証拠 | PARTIAL | 特定できないものを OPEN_QUESTIONS に列挙 (Q-01 から Q-55) | JARVIS の実装体は未特定 (Q-13)。planning_caliberB は見つからず (Q-12) |
| 8. Mapping を実装と検証に使える状態 | PARTIAL | 台帳、索引、検証器 (構造、語彙、パス、リンク、件数、証拠規則)、再現スクリプト 3 本 | 検証器は内容の真正性を検査しない (件数と語句だけ)。台帳の VERIFIED は 0 件 |
| 正本 (OVERVIEW、TODO、Essence、台帳) | BLOCKED_BY_HG | 二重の所在を確認 (A033/A034、A035/A036、A039/A040、A032/A047/A051) | 正本の宣言は、HG 判断事項 (Q-39、Q-07、Q-02、Q-03) |
| 決定記録の正本と権限の裏付け | BLOCKED_BY_HG | HG_DECISION_PACKAGE.md の 0.3、0.4 節 | Q-39、Q-41、Q-49〜Q-55 |
| 変更記録 (作業の正式な記録) | BLOCKED_BY_HG | 2026-10-10 の補完は GL8 により拒否 | Q-37。decision_id は HG 判断 |
| 発行 ID の正本 (専用ストア) | MISSING | 設計文書は要求し、ストアは NOT FOUND | 実装は未着手 |
| JARVIS の実装 | MISSING | 監査文書 (docs/audits) のみ確認 | Q-13 |
| Relay の実装と拡張の正本 | NOT_VERIFIED | relay/ は Python 実装、拡張の正本は PlanningCaliber と宣言 | 役割の関係、稼働は未確認 (Q-05、Q-08) |
| Orchestra (core_kernel) | NOT_VERIFIED | OrchestraEngine の定義、テストからの呼出し | 本番の呼出し元は確認できない。ストアは 0 行 |
| 認可の実効性 (RuntimeGate、RCL) | BLOCKED_BY_HG | 検査関数の存在を確認。ストアは 0 行 | Q-41、Q-45、Q-53 |

### 残作業 (優先順位付き。HG 判断を必要としないものを先に)

1. 完了: 文書の数字と台帳の不一致を検証器で検出する (件数、ID 範囲)。古い数字 (ツール数、ID 範囲、件数の記述) を修正。
2. 次: 各機能の確認手順 (読取専用のコマンド) を CAPABILITY_MAP に一覧化する。再現できることを、Mapping の使い道の中心にする。
3. 次: COMMAND CENTER の代表ルート 2、3 件について、読取専用の応答確認 (GET のみ、副作用のないもの) を行い、CAPABILITY_MAP に記録する。
4. 次: ASSET_INDEX の source_of_truth が null の 18 件について、宣言の有無を読取で確認する (宣言の無いものは null のまま)。
5. HG 判断待ち: 正本の宣言 (Q-39、Q-07、Q-02、Q-03)。権限の位置付け (Q-41、Q-50)。変更記録の補完 (Q-37)。
6. HG 判断待ち: JARVIS の実装体と Relay の役割の確定 (実装の所在の判断を含む)。

### 判断しないことの現状

Mapping は、所在、呼出し関係、読取の経路を、根拠付きで辿れる。判断を要する正本、権限、記録の補完は、現状のまま保留する。現状維持を既定の承認とはしない。

## 12. 統合経路図 (Mapping Phase 4, 2026-10-10)

記法: 入口 -> 境界 -> 呼出し先 -> データ -> 副作用 -> 証拠。証拠の区分は CAPABILITY_MAP 19 節の定義に従う。N/A は該当なし、NOT_VERIFIED は未確認。

### 12.1 イベント書込み (追記台帳)

| 経路 | 入口 | 境界 | 呼出し先 | データ | 証拠 |
|---|---|---|---|---|---|
| A. Claude 系 (MCP) | mocka_mcp_server.py mocka_write_event (752 行) | GL7 (execute_tool 内の before_tool)、必須項目検査 | POST http://localhost:5000/api/gate/event | events | 静的 + 稼働 (gate health 200) |
| B. Gate 直接 | phi_os/event_gate.py POST /api/gate/event (258 行) | 認証なし (127.0.0.1 の待受けに依存)。event_source は live に固定 | process_event (validate、_write) | events | 静的 (定義と登録 app.py:80) |
| C. Gateway 経由 | gateway/gateway.py POST /api/v1/event (142 行) | X-MoCKA-Key と HMAC (auth.py) | interface/event_buffer.py push -> POST /api/gate/event/batch | events | 静的 (バッファの定義) |
| D. SEO-OS 直接 | seo-os kernel/job_engine.py _mocka (98 行付近) | なし (SQL 直接) | sqlite3 で events へ INSERT | events (who_actor SEO-OS、44 件) | 静的 + DB (挿入は 2026-06-07 から 06-12、以後 DIRECT_UPDATE 132 件の記録) |
| E. Decision 系 | mocka_mcp_server.py mocka_decision_write (1086 行) | 必須項目検査のみ。重複検査なし | decision_ledger.jsonl へ追記 (_append_decision) | 台帳 (Decision 記録) | 静的 + 台帳の読取 (重複 1 件) |

注意: event_gate.process_event の docstring は'events 保存を行う唯一の経路'と記す。しかし、経路 D (SEO-OS) は SQL で直接書き、経路 D の書込みは Gate を経由していない。Gate の監査 (/api/gate/audit) の violation は 9 件で、経路 D の 2026-06 の行は'Gate 確立前'の legacy に分類される。監査テーブルの DIRECT_UPDATE は 22,476 件で、Gate の監査の分類 (_source) には含まれない。

### 12.2 イベント読出し

| 経路 | 入口 | 境界 | 呼出し先 | 証拠 |
|---|---|---|---|---|
| MCP | mocka_search、mocka_read_event、mocka_list_events | GL7 (before_tool) | events (SELECT) | 稼働 (tools/call の応答) |
| Gateway | GET /api/v1/context、/last_event (鍵を要する) | X-MoCKA-Key | gateway/context_builder.py (events、TODO、Essence) | 静的 (鍵を要するため未実行) |
| COMMAND CENTER | GET /integrity/status、/decision/log | 認証なし (127.0.0.1) | events (SELECT、フィルタ無し) | 稼働 (200) |
| Gate 監査 | GET /api/gate/audit、/api/gate/health | 認証なし (127.0.0.1) | events (SELECT) | 稼働 (200、event_count 24753) |

### 12.3 権限と承認 (Human Gate)

| 経路 | 入口 | 境界 | 呼出し先 | データ | 証拠・状態 |
|---|---|---|---|---|---|
| CLI 承認 | governance/human_gate_cli.py cmd_approve | TTY と対話の yes | phi_os/human_gate.approve (payload は note のみ) | human_gate_events | 静的 |
| HTTP 承認 | phi_os/human_gate.py http_approve (320 行) | Blueprint 未登録 (リポジトリ内) | approve (payload 全体を受理) | human_gate_events | 静的のみ。到達性 NOT_VERIFIED。BLOCKED_BY_HG |
| 不明な呼出し元 | 承認 payload の actor と authority_role | 検証なし | approve | AI_AUTHORITY 36 件 | 由来 UNKNOWN (Q-55)。BLOCKED_BY_HG |

### 12.4 実行時の認可判定

| 経路 | 境界 | データ参照 | 証拠 |
|---|---|---|---|
| RCL check_authorization | 呼出し引数の AuthorizationRecord (authority_subject、scope、expiry、revocation) | DB を読まない | 静的 (関数)。評価ログは判定欄無し (Q-53) |
| Orchestra RuntimeGate | core_kernel/orchestra/runtime_gate.py evaluate | core_kernel/orchestra/data/mocka_orchestra.db の authorization_records | 静的。ストアは全テーブル 0 行 (評価の永続化は無い) |
| MCP GL7 | execute_tool -> before_tool | governance pipeline | 静的 (稼働中の判定結果は未確認) |

### 12.5 Decision、Memory、Synapse (閉ループの構成要素)

| 段階 | 実装 | 呼出し | 状態 |
|---|---|---|---|
| 知識の保存 | memory/data/memory_store.json (180 件、episodic)、events | MemoryStore.append (未実行、書込みは禁止) | データ存在 (PRESENT) |
| 検索 | MemoryRetriever.retrieve (プロセス内)、mocka_search (events と knowledge_gate) | 稼働 (読取) | RUNTIME_VERIFIED (読取)。関連性は弱い (Q-38) |
| 判断入力 | decision_outcome.build_decision_outcome (tags=(etid,)) | closed_loop_runner.run_in_process のみ。その呼出し元はテスト | 静的のみ (STATICALLY_TRACED)。本番の呼出し無し |
| 人間の権限 | human_gate.approve、authority registry | 上記の 12.3 | BLOCKED_BY_HG (Q-41、Q-50) |
| 実行 | RuntimeGate (ExecutionGraph) | OrchestraEngine は orchestrator_api のモジュール読込時の生成、テストから参照 | 未確認 (実行の証拠無し) |
| 実際の帰結 | actual_consequence (memory 180 件中 178 件は UNKNOWN、2 件は CONFLICT) | - | NOT_VERIFIED |
| Memory への反映 | feedback/memory_reinforcer.py (提案のみ) | feedback_engine 等 | 静的のみ |

結論 (閉ループ): 検索から原本までの読取は確認済み。判断、実行、実際の帰結、Memory への反映は、いずれも実行証拠が無い。CLOSED_LOOP_VERIFIED は付けない。 [非主張]

### 12.6 セキュリティ境界 (優先リスク)

| 対象 | 待受け | 認証 (コード上) | 外部公開の設定 | 状態 |
|---|---|---|---|---|
| MCP (5002) | 0.0.0.0 | before_request は要求ログのみ。/mcp に鍵の検査無し。書込み系ツールを含む | cloudflared mcp.nsjp.org、ngrok addr 5002 | 優先リスク。到達性 NOT_VERIFIED。外部への試行は行わない |
| Gateway (5010) | 0.0.0.0 | X-MoCKA-Key (公開パスを除く)、POST /api/v1/event は HMAC | cloudflared gateway.nsjp.org | 検査は静的に確認。鍵の強度は未確認 |
| COMMAND CENTER (5000) | 127.0.0.1 | 認証無し (ルート単位、before_request とも無し) | 外部転送の設定は確認されず | 待受けは localhost。POST の多くは副作用を持つ (未実行) |
| Event Gate (経路 B) | 5000 (COMMAND CENTER 内) | 認証無し | - | 上と同じ。ただし 127.0.0.1 |

重要: 上の'認証無し'は静的な読取の結果。外部からの到達性、公開の実態、鍵の強度は確認していない。判断は HG と利用者の確認に委ねる。

### 12.7 件数の差 (同一の DB、異なる集計条件)

| 値 | 集計条件 | 出所 |
|---|---|---|
| 24,753 | 全件 (フィルタ無し) | COMMAND CENTER /integrity/status、Gate /api/gate/health、DB の直接集計 |
| 24,731 | data_integrity が normal、alt_schema_intentional、NULL のみ (corrupted_migration の 22 件を除外) | MCP /health (mocka_mcp_server.py:125 の _db_read_events) |

差の 22 件は、corrupted_migration の 22 件と一致する。フィルタを統一するかは HG 判断 (Q-36)。

### 12.8 Mapping 対象外の可能性がある既存能力 (今回の発見)

- interface/gate_policy.py の compute_gate_audit (Gate の違反の計数の定義)。
- interface/event_buffer.py (Gateway の非同期バッファ、フォールバックは data/event_buffer_fallback.jsonl。現在は存在しない)。
- PlanningCaliber/workshop/seo-os (別アプリ。MoCKA の DB へ直接書込む)。
- data/tic 配下 (relay_ping.json、health_log.jsonl 等。TIC 層)。

## 13. 統制境界の現状 (Mapping Phase 5, 2026-10-10)

判断パッケージ: [EVENT_GATE_CONTROL_PACKAGE.md](EVENT_GATE_CONTROL_PACKAGE.md)。以下は静的と監査記録の証拠に基づく。HG 判断は NOT_DECIDED。

| 境界 | 現状 (証拠の区分) | 未確認 |
|---|---|---|
| events への書込みの単一経路 | 正規経路 (Gate) は静的に確認。直接書込み (seo-os の _mocka と mocka_bridge) が存在し、2026-06 中旬の 44 行 (ESEOS) が監査記録と対応する (DB) | 直接書込みの現在の実行 (未確認)。全経路の網羅 |
| 直接書込みの検出 | 挿入トリガー (DIRECT_INSERT 100 件) と更新トリガー (DIRECT_UPDATE 22476 行、7685 イベント) が稼働 (DB)。挿入の検出は 2026-06-18 以降のみ | トリガーの作成日の記録 |
| 違反の計数 (Gate 監査) | 9 件は _source の語彙の不一致 (orchestra_lineage、CHECK 制約には有り、許可リストには無し)。直接書込みの証拠ではない (計算結果) | 語彙の正本の決定 (HG) |
| 一括更新 (2026-06-19) | 6 つの束。現在の data_integrity と、reclassify_alt_schema.py と clean_events.py の UPDATE 文が相関 (相関のみ) | 実行者 |
| MCP の認証境界 | 0.0.0.0:5002、before_request に認証無し、/mcp に鍵の検査無し、汎用プロキシ /api/<path> が localhost:5000 へ転送 (静的) | 外部到達性 (未確認)。実効性 |
| OAuth と登録 | 認可コードは認証無しで発行。トークンは保存も検証もされない。/register は誰でも登録可能 (静的) | 実効性の証拠無し |
| 公開系 | /api/action/publish_all、/api/distribution/publish は外部配信へ向かう実装 (静的) | 接続器の設定、実際の配信 (未確認) |
| 書込み系 MCP ツール | 各ツールの書込み先を確認 (CAPABILITY_MAP 20 節)。本作業では呼んでいない | GL7 の判定結果 (稼働中) |

要点: 統制の監視は、2 つの定義 (行の更新と、_source の分類) で並立している。どちらも全体の正しさを示さない。

## 14. Phase 6 の統合 (2026-10-10)

実装判断の証拠の統合は IMPLEMENTATION_DECISION_PACKAGE.md にある。要点:
- 公開経路 (MCP の /mcp、汎用プロキシ /api/<path>、OAuth、/register、公開系 POST) の認証の欠如は、静的に確認した事実。外部からの到達は未確認。最優先の判断事項。
- DIRECT_UPDATE 22,476 行は、7,685 イベントの更新の検知。大半は、2026-06-19 のデータ整備の一括更新と相関する (実行者は未確認)。
- 違反 9 件は、語彙の不一致 (orchestra_lineage)。直接書込みの証拠ではない。
- 2026-06-20 から 06-30 の検知の空白期間は、app.py の注釈 (TODO_371) の記録にある。
- 閉ループ、外部到達性、実行時の効果は未検証。


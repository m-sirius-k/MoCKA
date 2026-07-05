# AI_BOOT_HUB

## 位置づけ

本文書はMoCKAの「入口」である。情報そのものは持たない。

正本は各既存資産のままとし、本文書はそこへ到達するための手順とインデックスのみを持つ。

Rule 0(既存資産で代替できないことを証明できた場合のみ新規作成を認める)に基づき、本文書のみを新規文書として作成した。Single Source Registry・Capability Matrix・Reader Matrixのために別ファイルは作らず、本文書の中に節として収める。

対象読者: Claude、ChatGPT、Gemini、その他MoCKAに関与する全AI。

---

## 1. Boot Procedure

起動時は必ずこの順序で読むこと。順序を入れ替えない。

1. 禁止事項を確認する
   - Claude: `.claude/CLAUDE.md`
   - Claude以外: `docs/governance/GPT_RESTRICTIONS.md`(2026-04-01作成のまま更新が止まっている可能性があるため、`.claude/CLAUDE.md`の内容と食い違う場合は`.claude/CLAUDE.md`側を優先する)
2. `MOCKA_OVERVIEW.json`を読む(`C:\Users\sirok\MOCKA_OVERVIEW.json`)。現在フェーズ・理念・製品状況を把握する。
3. `MOCKA_OVERVIEW.json`内の`current_issues`/`next_actions`を取得する。
4. `MOCKA_TODO_ACTIVE.json`(`data/MOCKA_TODO_ACTIVE.json`)を読む。未着手/進行中のTODOを確認する。
5. 必要に応じて`events.db`を検索する(Claudeは`mocka_search`等のMCPツール経由。他AIは現時点で直接の検索手段を持たないため、Claude等MCP接続を持つAIに検索を依頼する)。
6. 1〜5の結果から「Current Case(現在扱う案件)」をその場で導出する。

Current Caseは本文書やその他のファイルに保存しない。保存すると`MOCKA_OVERVIEW.json`の`meta.updated`が17日間更新されずに陳腐化した前例と同じ問題が起きるため、起動のたびに1〜5から導出する運用とする。

---

## 2. Single Source Registry

正本・ミラー・キャッシュ・スナップショット・レガシー・デッドの分類。詳細な全件一覧ではなく、代表例のみを示す。個別ファイルの真偽に疑義がある場合は、コード内の実際の参照箇所(grep)で確認すること。

| 区分 | 代表例 |
|---|---|
| 正本 | `data/mocka_events.db`(唯一のイベント台帳)、`data/MOCKA_TODO_ACTIVE.json`(`mocka_mcp_server.py`のTODO_PATH)、`C:\Users\sirok\MOCKA_OVERVIEW.json`(同OVERVIEW_PATH)、`interface/lever_essence.json`(Claude用)、`data/lever_essence.json`(Gateway用、Claude用とは別ファイル)、`.claude/CLAUDE.md` |
| ミラー(内容同一) | `data/MOCKA_OVERVIEW.json`(外部版と内容は同一、`_snapshot_at`フィールドのみ差分) |
| キャッシュ | `data/tic/health_log.jsonl`、`governance/propagation/public_index_v1.json` |
| スナップショット | `mocka_events_pre_*.db`各種、`archive/ledger_old/`配下 |
| レガシー | `data/events.csv`系(廃止済み)、`docs/governance/`のv0.1シリーズ(裁定待ちで凍結中) |
| デッド | `./mocka_events.db`・`data/events.db`(いずれも0バイト) |

---

## 3. Capability Matrix

| AI | Read | Write |
|---|---|---|
| Claude(MCP経由) | 可 | 可 |
| ChatGPT(`adapter_gpt.py`) | 不可(読取関数が実装されていない) | 可(`/api/v1/event`へのPOSTのみ) |
| Gemini(`adapter_gemini.py`) | 不可(読取関数が実装されていない) | 可(同上) |
| Relay(Chrome拡張) | 自身の`chrome.storage.local`のみ | 同上のみ |
| Gateway(`gateway/context_builder.py`) | コード上は可(到達性は別問題) | コード上は可(到達性は別問題) |

---

## 4. Reader Matrix

| 対象 | Claude | ChatGPT | Gemini | Relay | Gateway |
|---|---|---|---|---|---|
| OVERVIEW | 読める | 読めない | 読めない | 読めない | 読める |
| TODO_ACTIVE | 読める | 読めない | 読めない | 読めない | 読める |
| events.db | 読める(検索経由) | 読めない | 読めない | 読めない | 読める(直近1件のみ) |
| lever_essence | 読める(interface版) | 読めない | 読めない | 読めない | 読める(data版、別ファイル) |
| CLAUDE.md | 読める | 読めない | 読めない | 読めない | 読めない |
| gateway/openapi.yaml | 読めない | 読めない | 読めない | 読めない | 読めない(人間が登録時に参照する静的仕様書であり、いずれのAIも実行時に読まない) |

**注記**: Capability MatrixおよびReader Matrixは、現在の資産構成に基づく制度情報である。対象ファイルの構成・配置・読取経路が変更された場合は、本Hubと併せて見直すこと。「恒久固定」ではない。

---

## 5. Decision Chainの保存場所

現状: 単一の正本は存在しない。

- `events.db`内に、タイトルへ`[governance_decision]`等を手動で付記したイベントが個別に存在する(例: override機構HOLD決定)。ただし`what_type`フィールドにはenum制約が無く、検索(`mocka_search`)以外にこれらを機械的に収集する手段はない。
- TODOの`contract_status`(`DECISION_RECORDED`等、enum制約あり)も裁定の一部を示すが、対象はArchitecture Contract系TODOに限られる。

将来、統一されたDecision Chainが実装された場合は、その参照先を本節に追記する。

---

## 6. Case Registryの保存場所

現状: 存在しない。

「案件(Case)」という単位でTODO・調査・インシデントを束ねる管理機構は、本セッションの調査時点で見当たらなかった。

将来、Case Registryが実装された場合は、その参照先を本節に追記する。

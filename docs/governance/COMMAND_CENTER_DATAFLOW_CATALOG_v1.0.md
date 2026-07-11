# COMMAND CENTER v6.1 データフロー完全台帳 v1.0

指示元: R01監査官(2026-07-11 最終裁定)
種別: COMMAND CENTERの正式設計資料(読み取り専用調査に基づく現状記録)
対象: C:\Users\sirok\MoCKA\index.html(1305行)

状態分類:
- Normal: データソース〜DOM反映まで正常に機能している
- Regression: 過去に機能していたが現在は断線している(復旧対象)
- Static: 元々ライブ化が計画・着手されておらず恒常的に固定値表示(退行ではない)
- Legacy: 別実装と機能的に重複する旧世代の実装
- Dead: UIのどこからも参照されない
- Planned: 現時点で本カタログの対象パネルには該当なし(将来追加候補は別文書「追加推奨項目」を参照)

## 1. パネル別データフロー一覧

| パネル | データソース | API | アダプタ | Render | Live | 状態 |
|---|---|---|---|---|---|---|
| Civilization Loop (civ) | STATIC.civ | GET /loop/status | なし(未実装) | renderCiv | ✗ | **Regression** |
| Heinrich Monitor (hein) | STATIC.hein(初期表示のみ) | GET /heinrich/status | mapHeinData() | renderHein | ○ | **Normal** |
| Active TODO (todo) | STATIC.todos | GET /risk/recommendation | なし(未実装、要再設計) | renderTodo | ✗ | **Regression** |
| 製品ステータス (products) | STATIC.products | なし | ー | renderProducts | ✗ | **Static** |
| BEE Ecology (bee) | STATIC.bee | GET /api/beta/status | なし(未実装) | renderBee | ✗ | **Regression** |
| Essence/PHL (essence) | STATIC.essence | GET CALIBER:5679/phl/history | なし(未実装) | renderEssence | ✗ | **Regression** |
| ISE State (ise-state) | なし(プレースホルダ) | GET /api/ise/state | ー | renderISEState | ○ | **Normal** |
| ISE Sessions (ise-sessions) | なし | GET /api/ise/status | ー | renderISESessions | ○ | **Normal** |
| PHI-OS Event Gate監査 (gate-audit) | なし | GET /api/gate/audit | ー | renderGateAudit | ○ | **Normal** |
| 第2ISEパネル(panel-ise、独立IIFE) | なし | GET /api/ise/panel(fetchLiveとは別、30秒独立ポーリング) | ー | インライン(即時DOM代入) | ○ | **Legacy**(ise-state/ise-sessionsと機能重複) |
| TIC Layer0 (tic0) | STATIC.tic0 | GET /health/status | ー | renderTic0Live | 条件付き○ | **Normal**(ただしchecks配列が空の場合はStatic維持に自動フォールバック) |
| TIC Layer1 (tic1) | STATIC.tic1 | なし | ー | renderTic(初期化時のみ) | ✗ | **Static** |
| Fluid Coordinates (coord) | STATIC.coords | なし | ー | renderCoords | ✗ | **Static**(「実測確定」表記は別途是正要、本監査①③参照) |
| SCAMPER Creative Engine | クライアント内蔵テンプレート | POST /scamper/run(結果送信のみ、fire-and-forget) | ー | renderScamperModes等 | ○ | **Normal**(設計通り、サーバー往復不要) |
| Distribution OS (Publish All) | ユーザー入力 | POST /api/action/publish_all(オンデマンド) | ー | インライン | ○ | **Normal**(設計通り、ポーリング対象外が正しい) |
| サーバー稼働ドット(topbar srv-row) | なし | なし | ー | なし | ✗ | **Static**(生死確認機構自体が存在しない) |
| Global Risk / Next Best Action(topbar risk-bar) | なし | なし | ー | なし | ✗ | **Static** |
| Seal表示(topbar) | なし | なし | ー | なし | ✗ | **Static**(2026-06-01時点の値で凍結、Seal制度設計は別TODOで検討) |

## 2. UI非参照だが存在するAPI(Dead候補、詳細判定はRELEASE CHECKLIST/Dead Code監査で別途実施)

| API | 実装箇所 | UIからの参照 |
|---|---|---|
| GET /api/ise/ai_sessions | app.py:3741 | なし |
| GET /api/ise/state_machine | app.py:3792 | なし |
| GET /api/ise/ledger | app.py:3805 | なし |
| GET /api/ise/taxonomy | app.py:3812 | なし |
| POST /api/ise/knock | app.py:3696 | なし(AIハンドシェイク用途、ダッシュボードUI対象外) |
| POST /api/ise/ack | app.py:3706 | なし(同上) |

## 3. 一覧からわかること

- 「取得しているが表示されない」(Regression、要復旧): civ / todo / bee / essence の4件
- 「そもそも取得すらしていない」(Static、退行ではなく未着手): products / tic1 / coord / サーバー行 / risk-bar・NBA / seal の6項目
- 「正常に機能している」(Normal): hein / ise-state / ise-sessions / gate-audit / tic0(条件付き) / scamper / dist-os の7件
- 「機能重複」(Legacy): panel-ise(第2ISEパネル)の1件
- 「UIから参照されないAPI」(Dead候補): /api/ise/系4本(ai_sessions/state_machine/ledger/taxonomy)

本台帳は2026-07-11時点のスナップショットである。今後のリリースでは本台帳とCOMMAND_CENTER_RELEASE_CHECKLIST_v1.0.mdの「Regression検査」項目を用いて、次回リリース時点の状態と本台帳を機械的に比較することを推奨する(詳細はチェックリスト文書参照)。

## 付録: Dead Code最終監査(R01指示Task 4)

単なる「消せるコード一覧」ではなく、制度設計上の位置付けを判定する。

| 項目 | 残す理由 | 廃止理由 | Phase4で必要か | Phase5候補か |
|---|---|---|---|---|
| GET /api/ise/ai_sessions | AI Runtime Domain個別セッション情報の取得元として、将来ダッシュボードに詳細ビューを追加する際に転用可能 | 現状ダッシュボードは`/api/ise/status`で同種の集約情報を取得済みであり、機能的に重複する可能性がある | 不要(現行`/api/ise/status`で代替済み) | 候補(セッション個別ドリルダウンUIを追加する場合) |
| GET /api/ise/state_machine | ISE状態遷移(state machine)を扱う専用エンドポイントであり、ガバナンス状態の正確な表現に資する可能性がある | ダッシュボードのどのパネルからも参照されておらず、用途が現状不明 | 要確認(用途をコード内実装から精査し、Phase4のRelease Gate可視化と関連するなら必要) | 候補 |
| GET /api/ise/ledger | Decision Ledger相当の情報をISEドメイン経由で取得する経路である可能性があり、親監査文書で指摘した「Decision Ledger可視化欠如」(P1)の解決に転用できる可能性がある | 現状`data/decisions/decision_ledger.jsonl`への直接アクセス経路の方が単純である可能性 | 要確認(P1のDecision Ledger可視化タスクで再検討) | 候補(有力) |
| GET /api/ise/taxonomy | ISEドメインの分類体系(taxonomy)を取得する専用エンドポイント。用途がダッシュボード上で現状想定されていない | ダッシュボードに対応する表示項目が存在しない | 不要(現行スコープに該当パネルなし) | 候補(将来taxonomy可視化が必要になった場合) |
| POST /api/ise/knock, POST /api/ise/ack | AIハンドシェイクプロトコル(Institution Handshake)の一部として現役稼働中(handshake.py系と連携する可能性が高い) | 該当なし(ダッシュボードUI観点でのDead判定対象外、別サブシステムとして現役) | 該当なし | 該当なし |
| 第2ISEパネル(panel-ise、`/api/ise/panel`) | 旧v1.3 Phase C統合パネルとして、`ise-revision`/`ise-hash`/`ise-todos`/`ise-warnings`等、第1パネルにない情報(Revision番号・State Hash等)を独自に表示しており、単純な重複ではなく情報の粒度が異なる | 「ISE — Institution State Engine」を名乗るパネルが2つ並存することはUI上の混乱を招く | 要統合検討(Phase4の表示信頼性要件に照らし、どちらか一方への統合、または明確な役割分担の表記が必要) | 該当なし(Phase4で判断すべき事項) |
| relay_dom FAIL静的表示(index.html:227) | Chrome拡張のDOMセレクタ生存確認という実在するリスク領域を示す表示意図自体は妥当 | 実際の現況を検証する仕組みがなく、恒久的に同じ表示のまま(実害の有無を確認する手段がない) | 要検証(現況を確認しライブ化するか、検証不能なら撤去) | 該当なし |

判定方針の要旨: 4本の未参照GETエンドポイント(ai_sessions/state_machine/ledger/taxonomy)のうち、`/api/ise/ledger`は親監査文書で指摘したP1課題(Decision Ledger可視化欠如)の解決手段として転用できる可能性が高く、Phase5を待たずPhase4のうちに用途精査を行う価値がある。他3本は現時点で明確な追加パネル計画がなければ、Phase5以降の検討候補として保留してよい。

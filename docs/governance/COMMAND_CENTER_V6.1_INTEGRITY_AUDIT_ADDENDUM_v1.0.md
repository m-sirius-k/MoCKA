# MoCKA COMMAND CENTER v6.1 総合整合性監査 追加報告 v1.0

親文書: docs/governance/COMMAND_CENTER_V6.1_INTEGRITY_AUDIT_v1.0.md
指示元: R01監査官(2026-07-11 追加裁定)
種別: 読み取り専用調査(コード変更なし)

R01より本監査(監査品質A評価)を受け、承認事項(P0-1 fetchLive配線修正設計、P0-2 Seal制度定義の確定)着手前の追加調査3点を実施した。

---

## 1. 4パネル未反映は意図的か実装漏れかの設計意図調査

### 結論: 実装漏れ(退行)。意図的な段階実装ではない。

一次データによる根拠:

1. **過去に稼働していた形跡**: commit `199c4a84f`(2026-06-01)時点のindex.htmlには、civ/todo/bee/essence各パネル用の個別ライブ更新関数が実在し機能していた(`refreshLoop()`→`/loop/status`、`refreshRisk()`→risk系、`refreshEssence()`→`/essence/detail`、BEE用`loadBetaStatus()`IIFE、コメント「TODO_216」付き)。

2. **退行の発生箇所**: 次にindex.htmlへ触れたcommit `a01af2e44a`(2026-06-08、コミットメッセージ「AUTO_SEAL_50EVT」、946行挿入/1133行削除の全面書き換え)で、上記の個別refresh関数群が削除され、現行のSTATIC定数+`renderXxx(data)`アーキテクチャに置換された。この置換の際、`fetchLive()`内で civ/todo/bee/essence の4パネルをdispatchする配線は一度も追加されなかった(全履歴検索で該当箇所なしを確認)。

3. **このコミット自体が既知のHuman Gate迂回インシデント**: AUTO_SEAL_50EVT系コミットは、後続commit `6187be3933e`(2026-06-26)のメッセージ内で「Human Gate未承認のまま自動生成」と明記され、event `E20260625_160794170c881`(「緊急発見: AUTO_SEAL_50EVTが承認待ちのTODO_347-c変更4ファイルを既に自動コミット済み（Human Gate迂回）」)がこれを裏付ける。**正規レビューを経ない自動コミットが、既存の稼働機能を落とした構図**であることが確定した。

4. **同型バグはheinパネル単体では既にTODO化・修正済み**: TODO_362(状態=完了)が「Heinrich Monitorパネル配線断絶」として、今回調査対象の4パネルと全く同一のバグパターンをhein単体について診断・起票し、commit `6187be3933e`で`mapHeinData()`変換関数を追加して修正済み。すなわちこのプロジェクトには「STATIC固定表示に取り残された配線断絶」を発見次第TODO化して個別修正する運用実績があるが、**civ/todo/bee/essenceの4パネルについては、この修復プロセスが一度も回ってこなかった**。

5. **civ/todo/bee/essenceタグ付きの既存TODOはいずれも別問題**: civタグ(TODO_374/375/387/364/384、全完了)は`/loop/status`集計の出典整合性調査。todoタグ(TODO_365、未着手)は`/risk/recommendation`のバックエンド側推奨ロジックバグ。BEEタグ(TODO_216完了/TODO_437進行中)はbeta_engine再設計・タイムアウト対策。Essenceタグ(TODO_359完了)はessence_auto_updater運用境界判断。いずれも「fetchLive()のrender呼び出し欠落」自体を対象にしたTODOではない。

### 緩和要素(実装工数の見積りに関わる事実)

`/loop/status`・`/risk/recommendation`・`/api/beta/status`・`CALIBER_BASE/phl/history`の実レスポンス形状を本監査でcurl実測したところ、いずれも`renderCiv`/`renderTodo`/`renderBee`/`renderEssence`が期待する形状と一致しない(下記2節参照)。hein同様の`mapXxxData()`変換層が必要であり、単純な1行呼び出し追加では済まない。ただしこれは「意図的な段階実装だった」ことを意味せず、「退行後、修復作業が単に着手されないまま放置された」ことを意味する。

### 判定サマリ

| パネル | 判定 | 根拠 |
|---|---|---|
| civ | 実装漏れ(退行) | 199c4a84f→a01af2e44aで喪失、対応TODOなし |
| todo | 実装漏れ(退行) | 同上、TODO_365は別問題(バックエンド側) |
| bee | 実装漏れ(退行) | 同上、TODO_216/437は別問題 |
| essence | 実装漏れ(退行) | 同上、TODO_359は別問題。エンドポイント自体も`/essence/detail`→`phl/history`へ変更されており移行が未完了 |

---

## 2. COMMAND CENTER全データフロー一覧表

データソース → API → fetch実施有無 → render呼び出し有無 → DOM反映状態、の一覧。

| パネル | データソース | API | fetch | render関数 | render呼び出し | DOM反映状態 |
|---|---|---|---|---|---|---|
| Civilization Loop (civ) | STATIC.civ | GET /loop/status | ○ | renderCiv | ✗ 未実装 | 常にSTATIC |
| Heinrich Monitor (hein) | STATIC.hein | GET /heinrich/status | ○ | renderHein(mapHeinData) | ○ | ライブ |
| Active TODO (todo) | STATIC.todos | GET /risk/recommendation | ○ | renderTodo | ✗ 未実装 | 常にSTATIC |
| 製品ステータス (products) | STATIC.products | なし | ✗ | renderProducts | 初期化時1回のみ | 常にSTATIC |
| BEE Ecology (bee) | STATIC.bee | GET /api/beta/status | ○ | renderBee | ✗ 未実装 | 常にSTATIC |
| Essence/PHL (essence) | STATIC.essence | GET CALIBER:5679/phl/history | ○ | renderEssence | ✗ 未実装 | 常にSTATIC |
| ISE State (ise-state) | なし(取得中...) | GET /api/ise/state | ○ | renderISEState | ○ | ライブ |
| ISE Sessions (ise-sessions) | なし | GET /api/ise/status | ○ | renderISESessions | ○ | ライブ |
| PHI-OS Gate Audit (gate-audit) | なし | GET /api/gate/audit | ○ | renderGateAudit | ○ | ライブ |
| 第2ISEパネル(panel-ise、独立IIFE) | なし | GET /api/ise/panel(30秒独立ポーリング) | ○ | インライン | ○ | ライブ(fetchLiveとは別経路) |
| TIC Layer0 (tic0) | STATIC.tic0 | GET /health/status | ○ | renderTic0Live | ○(ただしchecks空なら静的維持) | 条件付きライブ |
| TIC Layer1 (tic1) | STATIC.tic1 | なし | ✗ | (renderTic内、初期化のみ) | 初期化時1回のみ | 常にSTATIC |
| Fluid Coordinates (coord) | STATIC.coords | なし | ✗ | renderCoords | 初期化時1回のみ | 常にSTATIC |
| SCAMPER | クライアント内蔵 | POST /scamper/run(ログ送信のみ) | ユーザー操作時 | renderScamperModes等 | ○ | 正常設計(ライブ不要) |
| Distribution OS (Publish All) | ユーザー入力 | POST /api/action/publish_all | ユーザー操作時 | インライン | ○ | 正常設計(オンデマンド) |
| サーバー稼働ドット(topbar) | なし | なし | ✗ | なし | ✗ | 常に固定HTML |
| Global Risk / NBA / Seal(topbar) | なし | なし | ✗ | なし | ✗ | 常に固定HTML |

一目でわかる要点: 「取得しているが表示されない」パネルは civ/todo/bee/essence の4件。「そもそも取得すらしていない」パネルは products/tic1/coord/サーバー行/risk-bar/seal の6件。両者は原因が異なる(前者=退行、後者=元々ライブ化未着手)。

---

## 3. Dead Code調査

### 呼ばれないAPI(index.htmlから一切参照されないapp.py上のエンドポイント)

app.py上に実装されている`/api/ise/*`系エンドポイントは9本存在するが、index.htmlから参照されるのは3本のみ(`/api/ise/state`, `/api/ise/status`, `/api/ise/panel`)。以下4本のGETエンドポイントはダッシュボードのどこからも呼ばれていない:

- `GET /api/ise/ai_sessions`(app.py:3741)
- `GET /api/ise/state_machine`(app.py:3792)
- `GET /api/ise/ledger`(app.py:3805)
- `GET /api/ise/taxonomy`(app.py:3812)

(`/api/ise/knock`・`/api/ise/ack`はPOSTでAIハンドシェイク用途のためダッシュボード対象外、廃止候補ではない)

### 呼ばれないrender関数

該当なし。`renderCiv`/`renderTodo`/`renderBee`/`renderEssence`/`renderProducts`/`renderCoords`はすべて`initAll()`内でSTATIC引数付きで最低1回は呼ばれており、技術的な意味でのdead codeではない。ただし常に同一の静的引数でしか呼ばれず、ライブ更新経路が存在しない(2節参照)。

### 使用されないデータ

STATIC.products / STATIC.coords / STATIC.tic1 は、対応するfetch自体が`fetchLive()`のjobsに含まれていない(取得の試みすらない)。civ/todo/bee/essenceとは異なり「退行」ではなく「元々ライブ化が計画・着手されていない」カテゴリ。

### 廃止候補

1. **第2のISEパネル(panel-ise、`/api/ise/panel`)** — 第1のISEパネル(ise-state/ise-sessions、`/api/ise/state`+`/api/ise/status`)と表示内容が機能的に重複(Institution Domain状態・AI Runtime Sessionsをどちらも表示)。どちらを正本とするか整理が必要(親文書②で既報)。
2. **relay_dom FAIL静的表示**(index.html:227) — 実際の現況を検証する仕組みがなく、恒久的にFAIL表示されたまま。実害の有無を確認の上、正確な生死確認に置き換えるか撤去すべき候補。
3. **`/api/ise/ai_sessions`・`/api/ise/ledger`・`/api/ise/taxonomy`** — ダッシュボード非表示のまま存在。他クライアント(AI向けAPI等)からの利用有無を別途確認の上、UI追加候補か廃止候補かを判断する必要がある。

---

## 総括

R01裁定のP0-1(fetchLive配線修正設計)着手にあたっては、本追加調査により「civ/todo/bee/essenceの4パネルは、2026-06-08のHuman Gate迂回コミット(a01af2e44a)による機能退行であり、意図的な未着手ではない」ことが確定した。これはUI改善ではなく、**過去に存在した制度情報伝達経路の復旧**として扱うべき事案である。修復には各パネル用の`mapXxxData()`相当の変換層が必要(バックエンドAPI形状とフロント期待形状の不一致)。P0-2(Seal制度定義の確定)については追加調査の対象外のため親文書のまま。

以上を踏まえた実装設計案の提出可否は、引き続きHuman Gate裁定を仰ぐ。本追加報告でもコード変更は一切行っていない。

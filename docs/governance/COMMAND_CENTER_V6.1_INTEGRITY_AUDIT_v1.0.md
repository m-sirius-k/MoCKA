# MoCKA COMMAND CENTER v6.1 総合整合性監査報告 v1.0

監査実施: Claude-code-sonnet-5(くろこ)
指示元: R01監査官(きむら博士代理)
実施日: 2026-07-11
種別: 読み取り専用監査(画面修正・コード変更は本監査のスコープ外)

対象: C:\Users\sirok\MoCKA\index.html(COMMAND CENTER v6.1、1305行)および関連API/一次データ

---

## 1. Executive Summary

COMMAND CENTER v6.1は「制度ダッシュボード」として部分的にしか機能していない。最大の問題は表示の古さそのものより、表示更新の配線が構造的に欠落している箇所があること。

headline finding 2件:

1. ライブ取得から未反映バグ: fetchLive()(index.html:1210-1223)が9本のAPIを取得するが、レンダリング関数の呼び出し分岐が5本(hein/tic0/ise-state/ise-sessions/gate-audit)にしか実装されておらず、civ(文明ループ)・todo(Active TODO)・bee(BEE Ecology)・essence(Essence/PHL)の4パネルは、ライブ取得が成功してもハードコードされたSTATIC値を永久に表示し続ける。TODOパネルの4/7項目が完了済みなのに未完了表示されている根本原因はこれ。

2. Seal表示の長期停止: topbarのseal: c2d8c54e(index.html:206)は2026-06-01時点のgit commitハッシュ短縮形で、40日以上更新されていない。現在参照しうる「seal相当値」が3系統存在し(この古いgitハッシュ/2026-07-07の最新re-sealコミット/MOCKA_OVERVIEW.jsonのgovernance.latest_seal.sha256)、いずれも一致しない。

router/save・collaboration・shareの過去再発項目は、現在進行形のインシデントではない(全て2026-04-04〜04-13を最後に静止、saveのみ集計バグを2026-06-19に修正済みでドキュメント反映のみ未了)。

Phase 4(商用展開)の観点では、Release Gate(コード実装済み)・Decision Ledger(56件)・Human Gate(1,777件)・Incident実数(232件)など、信頼性の根拠となるべき制度データがことごとくダッシュボードに反映されていない。

## 2. 古い表示一覧

分類基準: A=最新 / B=表示更新必要 / C=廃止候補 / D=要確認

| 項目 | 場所 | 分類 | 詳細 |
|---|---|---|---|
| Civilization Loop 8段の件数 | index.html STATIC.civ | B | Incident=23(静的)、実測232件。ライブ取得はしているが未反映 |
| Active TODO一覧6件 | index.html STATIC.todos | B | TODO_254/154/CALIBER_EXPAND_001/206が完了済みなのに表示継続 |
| Seal表示 | index.html:206 | C(要更新) | 40日以上前のgitハッシュ、現在の3値いずれとも不一致 |
| Global Risk / Next Best Action文言 | index.html:212-217 | D | 現状たまたま正確(TODO_221進行中・TODO_205未着手は一致)だが更新機構が一切ない完全な固定文言 |
| サーバー稼働ドット(APP/MCP/CALIBER等) | index.html:220-230 | B | JSによる生死確認が一切なく常時on表示のまま |
| relay_dom FAIL表示 | index.html:227 | D | router/save等とは無関係の別ヘルスチェック(Chrome拡張DOM selector)。現況要検証 |
| TIC Layer1 roadmapタグ(TODO_205/206/207未着手) | index.html:886 | B | TODO_206は既に完了済みなのに「未着手」表示のまま |
| Fluid Coordinates「実測確定」表記 | index.html:413 | C | 完全ハードコード値に「実測確定」と付記、ライブ取得機構なし |
| Products(Orchestra CWS審査中) | index.html:608 | D | mini-mocka-series README(2026-05-16)は「ready」と矛盾する記載、現況要確認 |
| Products(Relay/PHI OS/vasAI) | index.html:609-611 | A | 現行実態と一致確認済み |
| PHI-OS Event Gate監査パネル | index.html:1142-1189 | A | ライブ配線・レンダリング共に正常動作 |
| ISE状態パネル(2種) | index.html:291-306, 320-338 | D | 廃止ではなく両方とも生存(/api/ise/state+status、/api/ise/panel 両方200応答)。重複表示として要整理 |

## 3. 整合性エラー一覧

| # | エラー内容 | 現行値 | 表示値 | 原因 |
|---|---|---|---|---|
| 1 | Incident件数 | 232件(events.db実測) | 23件(静的) | fetchLive未反映バグ |
| 2 | Active TODO表示 | TODO_254/154/206/CALIBER_EXPAND_001は完了済み | 未完了として表示 | 同上 |
| 3 | Seal値 | 3系統でバラバラ | 40日前の値で固定 | 更新機構なし |
| 4 | TIC roadmap | TODO_206完了済み | 「未着手」表示 | 静的タグ未更新 |
| 5 | router/save再発件数 | 現状40(自己参照21件除外後、修正済み) | MOCKA_OVERVIEW.json:90は04-04/04-05時点の記述のまま | ドキュメント反映漏れ |
| 6 | Decision Unit数 | data/decisions/56件 と data/ise/27件、2系統併存 | ダッシュボードには非表示 | 未整備+要確認(どちらが正か) |
| 7 | 作業ツリー未コミット | git上10ファイル(MOCKA_OVERVIEW.json含む)が未コミット | — | Repository状態の一部が正本(git)に未反映 |

## 4. MoCKA現行との差分

- API endpoint状態: 調査対象12本すべて実在・200応答(publish_all/scamper/runはcurl検証方法起因で結果あいまい、要再検証)。/api/ise/panelは廃止されておらず現役。新たに/api/ise/state_machineという未使用の4本目のISEエンドポイントを発見(index.htmlのどこからも呼ばれていない)。
- router/save,collaboration,share: 3経路とも実測データ上2026-04-04〜04-13で静止。実害なし(saveの集計バグのみ実害があったが解消済み)。
- TODO管理: ACTIVE 78件(未着手42/進行中8/完了15/保留11/条件付保留1/廃止1) + completed(アーカイブ側)55件。ダッシュボードはこの内訳を一切表示せず上位6件の(今は古い)固定リストのみ。
- Repository情報: branch=main、HEAD=db9a872ad2(2026-07-11、TODO_442コミット)、originより1コミット先行。ダッシュボードにはbranch/commit情報の表示項目自体が存在しない。

## 5. 追加推奨項目(Phase4不足管理項目)

| カテゴリ | 項目 | 現状 |
|---|---|---|
| 商用展開 | Release Gate可視化 | production_certification/gate/release_gate.pyにcan_release()実装済みだがダッシュボード非表示 |
| 商用展開 | External User Feedback | 収集機構自体が存在しない |
| 商用展開 | Documentation Status | 追跡機構なし |
| Governance | Decision Ledger可視化 | 56件(+ise系27件)存在するが非表示 |
| Governance | Human Gate実績可視化 | human_gate_eventsテーブル1,777件存在するが非表示 |
| Governance | Approval Chain表示 | Decision Ledgerのapproved_byは記録されているが集計・表示なし |
| 運用 | Incident実数の正確な反映 | 232件、表示は23件固定 |
| 運用 | Technical Debt台帳 | 専用の体系的台帳が存在しない |

## 6. 未整備項目

- External User Feedback収集の仕組み(存在しない)
- Documentation Status追跡の仕組み(存在しない)
- Technical Debt専用台帳(存在しない、個別TODO/docsに散在するのみ)
- CWS(Chrome Web Store)審査状況の最新性を確認する手段(静的文字列のみで裏取り不可)

## 7. 未完了一覧

項目: fetchLive()のcivil/todo/bee/essenceパネル未反映バグ
場所: index.html:1210-1223
現在状態: 4パネルとも恒久的にSTATIC値表示
問題: ライブAPIは正常応答しているのに画面に反映されない設計欠陥
影響: Incident件数23 vs 232、完了済みTODOの表示継続等、複数の派生的整合性エラーの根本原因
優先度: P0
推奨対応: fetchLive()のPromise.allSettledループ内にrenderCiv(data)/renderTodo(data)/renderBee(data)/renderEssence(data)相当の分岐を追加する設計(実装はHuman Gate承認後)

項目: Seal表示の長期不整合
場所: index.html:206
現在状態: 40日以上前のgitハッシュ固定
問題: 3系統のseal相当値が不一致、どれが正本か未確定
影響: 商用展開下での信頼性要件を損なう
優先度: P0
推奨対応: seal正本の一元化方針を博士に確認した上で、ライブ取得配線を設計

項目: ISEパネル二重実装
場所: index.html:291-306 と 320-338
現在状態: 両方生存・両方動作中(重複)
問題: 同名ISEを名乗る2つの独立パネルが並存、どちらが正本か不明瞭
影響: UI混乱、保守性低下
優先度: P2
推奨対応: 統合方針の判断

項目: Decision Ledger/Human Gate実績の不可視化
場所: ダッシュボード全体
現在状態: 一切表示なし
問題: 商用展開の信頼性要件である制度統治の実績が見えない
影響: 外部向け説明責任・監査対応力の不足
優先度: P1
推奨対応: 新規パネルの追加設計

項目: router/save関連ドキュメントの反映漏れ
場所: data/MOCKA_OVERVIEW.json:90
現在状態: 2026-04-04/04-05時点の記述のまま
問題: 2026-06-19の自己参照除外修正(commit cf9ac5c5a)が文言に反映されていない
影響: 軽微(実データ側は既に正しい、表示文言のみの遅延)
優先度: P3
推奨対応: 文言更新のみ

## 8. 修正優先順位

- P0 Critical: (1)fetchLive未反映バグ(civ/todo/bee/essence4パネル)、(2)Seal表示40日以上の不整合・正本不明
- P1 High: Decision Ledger/Human Gate実績の可視化欠如、Incident実数(232)の反映、CWS審査状況の裏取り
- P2 Medium: ISEパネル二重実装の整理、TIC roadmap tagのTODO_206完了未反映、サーバー稼働ドットのライブ化
- P3 Low: MOCKA_OVERVIEW.json:90のrouter/save文言更新、Global Risk/NBA文言の更新機構検討

## 9. 推奨Next Action

1. 本報告をきむら博士へ提出し、P0 2件(fetchLive未反映バグ／Seal正本確定)について修正着手の可否をHuman Gateで裁定いただく(本監査は画面修正を目的としないため、実装は別途TODO化・承認後)
2. Seal正本(git HEAD相当/re-seal commit/MOCKA_OVERVIEW.json.governance.latest_seal.sha256のいずれか)の一元化方針を博士に確認
3. Decision Ledgerがdata/decisions/とdata/ise/の2系統に分かれている件の要確認(どちらを「Decision Unit数」の正本とするか)
4. Chrome Web Store審査状況を博士側で実際のデベロッパーコンソールと突き合わせて確認
5. 承認が得られ次第、P0→P1→P2→P3の順でTODO化し、通常の設計→Human Gate承認→実装フローに乗せる

## 付記: 調査方法

本監査はClaude Code(くろこ)本体によるindex.html全文解析(直接Read)、および3件の並列サブエージェント調査(router/save系再発インシデント調査、MoCKA現行実態スナップショット取得、Phase4商用展開項目調査)の結果を統合して作成した。すべて読み取り専用で実施し、コード変更・ファイル変更は一切行っていない。

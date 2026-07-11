# COMMAND CENTER v6.1 退行インシデント報告書 v1.0

指示元: R01監査官(2026-07-11 最終裁定)
種別: 制度インシデント調査(読み取り専用、コード変更なし)
関連文書: COMMAND_CENTER_V6.1_INTEGRITY_AUDIT_v1.0.md、同ADDENDUM_v1.0.md

R01裁定により、本件はCOMMAND CENTER v6.1の表示不具合ではなく、2026-06-08のAUTO_SEAL_50EVTに起因する制度インシデントとして扱う。目的は「誰が悪いか」ではなく「なぜ制度がこれを検知できなかったか」の分析である。

## 1. 時系列

| 日時 | 出来事 | 根拠 |
|---|---|---|
| 2026-06-01 18:23 JST | commit `c2d8c54ed`(re-seal after c6c8b21)。この前後、index.html内に個別ライブ更新関数(refreshLoop/refreshRisk/refreshEssence/loadBetaStatus、BEE用IIFEにTODO_216タグ)が実在し正常稼働していた | `git show 199c4a84f:index.html`(2026-06-01時点) |
| 2026-06-08 10:11:51 | commit `a01af2e44a`(コミットメッセージ「AUTO_SEAL_50EVT」)。index.html全面書き換え(946行挿入/1133行削除)。上記の個別refresh関数群を削除し、現行のSTATIC定数+`renderXxx(data)`アーキテクチャへ置換。この時点でcivil/todo/bee/essence**および**hein含む5パネル全てが、fetchLive()内でrender未接続の状態になった(推定、hein個別修正が06-26のため) | commit差分、`git log --oneline -- index.html` |
| 2026-06-08前後 | このコミットが成立した時点で、index.htmlはCore System File保護の対象ですらなかった。`is_core_system_file()`の最初期実装はcommit `90a39ef27`(2026-06-25)、`governance/mocka_git_safe_commit.py`本体の新設・index.html追加はcommit `fda5e37ec2`(2026-06-30)であり、いずれも本件より17〜22日後 | `governance/mocka_git_safe_commit.py`のgit履歴 |
| 2026-06-08前後(期間) | AUTO_SEAL_50EVT機構(`scripts/ledger/anchor_update.py`)は`PRE_COMMIT_FORBIDDEN`(秘密情報漏洩防止のブラックリストのみ)を検査するのみで、変更内容の機能的妥当性は一切検証しない設計。加えて当時は`app.py`の`auto_audit_loop()`がevent_count差分50到達時にHuman Gate未経由で`anchor_update.py`を自動起動していた(この無条件自動push運用の是正は2026-07-07/08のTODO_427、commit `1707fcc382`/`3bc80842e`まで続いた) | `scripts/ledger/anchor_update.py`、TODO_427関連commit |
| 2026-06-25 | 同一AUTO_SEAL_50EVT機構による、index.html**とは別の**4ファイル(gateway/auth.py, structural/event_recency.py等)のHuman Gate迂回が発見・記録される(event `E20260625_160794170c881`)。この調査・是正プロセス(DC_20260708_001/006/007)の対象にindex.htmlは一度も含まれなかった | event `E20260625_160794170c881`、decision_ledger.jsonl |
| 2026-06-26 | commit `6187be3933e`。TODO_362としてHeinrich Monitor(hein)パネル**単体**の同型配線断絶(fetchLive取得成功もrender未接続)が個別に発見・修正される。`mapHeinData()`変換関数を追加しrenderHein呼び出しを接続。civ/todo/bee/essenceへの横展開・網羅スキャンは行われなかった | commit `6187be3933e`、TODO_362(ARCHIVE、完了) |
| 2026-06-30 | commit `fda5e37ec2`。`governance/mocka_git_safe_commit.py`新設、`CORE_SYSTEM_FILES_EXTRA`にindex.html追加。以後は無承認でのindex.html書き換えに対する制度的抑止は機能するが、既に成立済みの本件退行そのものは自動検出されない(過去分は対象外) | `governance/mocka_git_safe_commit.py:42` |
| 2026-07-07 20:03 | 直近のre-seal commit `de2356beebec`(anchor: re-seal after f1f0b69)。index.html topbarの静的seal表示「c2d8c54e」はこれより38日以上前の値のまま | git log |
| 2026-07-11 | R01監査官指示による本監査(COMMAND_CENTER_V6.1_INTEGRITY_AUDIT_v1.0.md)にて、civ/todo/bee/essence4パネルの配線断絶を発見。通常の自動チェック・Human Gate・TIC監視のいずれでもなく、専用の読み取り専用ダッシュボード監査によって初めて検知された | 本セッション |

civ/todo/bee/essenceは2026-06-08から2026-07-11まで**33日間**、修復されないまま放置されていた(heinは06-08〜06-26の18日間で個別修復)。

## 2. AUTO_SEAL_50EVTによる変更内容

commit `a01af2e44a`はindex.htmlを946行挿入/1133行削除の全面書き換えで置換した。旧アーキテクチャ(個別refresh関数がAPIを取得しDOMを直接更新)から、新アーキテクチャ(STATIC定数で即時描画→非同期`fetchLive()`でライブデータを取得し、成功時のみ明示的に`renderXxx(data)`を呼んで再描画)へ移行した。この設計変更自体は、SATIC値による即時描画+段階的ライブ化という妥当な設計判断だが、移行時に旧実装が持っていた5パネル分(hein含む)のライブ更新能力の再実装が完了しないまま本番へ反映された。

## 3. 削除されたrefresh系処理

`git show 199c4a84f:index.html`で確認できる旧実装:
- `refreshLoop()` — `fetch('/loop/status')`し`civ-loop`要素を直接更新(civパネル相当)
- `refreshRisk()` — risk/recommendation系を取得しrisk-level/risk-bar等を更新(todoパネル相当、ただし対象がrisk-bar寄りで現行todoパネルとは範囲が異なる可能性がある)
- `refreshEssence()` — `fetch('/essence/detail')`(現行の`CALIBER:5679/phl/history`とはエンドポイント自体が異なる)し`ess-incident`等を更新
- BEE用`loadBetaStatus()`(TODO_216タグ付きIIFE) — `/api/beta/status`+`/api/beta/meta`を取得しbee-panel-rowsを描画

## 4. Heinパネルのみ復旧した経緯

TODO_362(完了、ARCHIVE格納)が「Heinrich Monitorパネル配線断絶 — fetchLive()にrenderHein()呼び出しが存在せずSTATIC.heinハードコード値のまま固定表示」という、本件と同一パターンのバグを個別に診断・起票した。担当者が実際の画面表示とAPIレスポンスの不一致に気づき、`/heinrich/status`の実レスポンス形状(`heinrich.actual_ratio`/`capture_rate`/`missing_estimate`等)をrenderHein()が期待する`{l1,l2,l3,rate,uncaught,spark}`形式へ変換する`mapHeinData()`を新規実装してcommit `6187be3933e`で修正した(index.html:717-730のコメント「TODO_362:...」が対応箇所)。この発見・修正は網羅的なパネル走査ではなく、個別の気づきに基づく単発対応だった。

## 5. civ/todo/bee/essenceが未復旧となった経緯

TODO_362のようなヒヤリハット的な気づきが、civ/todo/bee/essenceの4パネルには一度も発生しなかった。既存のTODO台帳を検索すると、これら4パネルにタグ付けされたTODO(civ: TODO_374/375/387/364/384、todo: TODO_365、bee: TODO_216/437、essence: TODO_359)は存在するが、いずれも「render呼び出し欠落」自体を対象にしたものではなく、バックエンド側の集計ロジック・タイムアウト対策・運用境界判断など別種の課題を扱っていた。すなわち、この4パネルは「壊れていることに誰も気づかなかった」状態が33日間継続した。

## 6. Human Gate迂回インシデントとの関連

commit `a01af2e44a`は、後に発覚したAUTO_SEAL_50EVT系Human Gate迂回インシデント(event `E20260625_160794170c881`)と同一の自動push機構によって生成された。ただしこの迂回インシデントの発見・是正プロセス(DC_20260708_001/006/007)は、gateway/auth.py・structural/event_recency.py等**別の4ファイル**を対象としており、index.htmlはこの是正プロセスの俎上に一度も載らなかった。Decision Ledger全56件をgrepしてもindex.htmlへの言及は0件であり、「レビューされたが見逃された」のではなく「そもそもレビュー対象に一度も含まれなかった」。

## 7. 現在まで発見されなかった理由(制度分析)

単一原因ではなく、以下5点が重なった構造的死角である。

1. **時期的ギャップ**: 事故発生時点(2026-06-08)、Core System File保護制度(`is_core_system_file()`)自体がリポジトリに存在しなかった(制度化は06-25〜06-30)。「保護があったのにすり抜けた」のではなく「保護制度がまだ制度化されていなかった」。
2. **AUTO_SEAL機構の検証範囲の狭さ**: `anchor_update.py`の`check_staged_files()`は秘密情報漏洩防止のブラックリスト検査のみで、変更内容の機能的正当性は一切見ていない。加えて事故当時は無条件自動push運用下にあった(是正は07-07/08)。
3. **自動検証の対象外**: `verify_all.py`の9ステップ・TIC Layer0/1はいずれもガバナンス不変条件・サーバー疎通確認が中心で、UIのrender配線という「機能性」は検証範囲に含まれない。`mocka_mcp_server.py`変更時のような専用hash検証もindex.html向けには存在しない。
4. **レビュー対象からの脱落**: Decision Ledger56件にindex.htmlへの言及が皆無。同時期のHuman Gate迂回是正プロセスの対象からも漏れていた。
5. **再発防止策の個別化**: hein単体の同型バグ修正(TODO_362)が、横展開・網羅スキャンという制度的な再発防止に発展しなかった。「気づいた人が直す」という属人的プロセスに留まった。

## 8. 非目的・スコープ

本報告書は「誰が悪いか」を特定するものではない。事故発生時点でCore System File保護が未成立だったこと自体は、当時の制度発展段階として理解可能である。問題は「今この瞬間もこの種の検知網が存在しない」ことであり、再発防止策はCOMMAND_CENTER_RELEASE_CHECKLIST_v1.0.mdで別途提案する。本報告書ではコード変更・実装着手は一切行っていない。

## 付録A: Seal制度設計調査(R01指示Task 5、調査のみ・実装禁止)

「どれを正本にするか」ではなく、各seal相当値が何を保証するための値なのか、制度的役割を整理する。

### A-1. Git HEAD(コミットハッシュ)

対象: リポジトリ全体のソースコード・設定ファイルの、その時点でのスナップショット。Git標準機能そのものであり、seal専用の仕組みではない。他のseal機構(re-seal・summary_hash計算)の入力(対象コミット)として使われる基盤的な値。実測: `db9a872ad29dde46ac7f0ae26f99daea767de2cd`(2026-07-11T07:42:11+09:00)。

### A-2. re-seal commit(`anchor: re-seal after <commit>`)

実装: `scripts/ledger/anchor_update.py`。`git add -A`→`mocka_git_safe_commit`でコミット後、`governance/calc_summary_hash.py`が`git ls-tree -r <sealing_commit>`の出力(anchor_record.json自身は除外)をSHA-256化し、`governance/anchor_record.json`(+ミラー`mocka-governance-kernel/anchors/anchor_record.json`)へ`sealed_summary_hash`/`sealed_at_utc`/`external_ref`を書込み、その変更自体を`anchor: re-seal after <commit[:7]>`として再度コミットする。

保証対象: **その時点のgitツリー全体(ファイル一覧+blobハッシュ)の改ざん検知用の監査証跡**(`docs/governance/SEAL_CANONICAL_SOURCE_PROPOSAL_v0.1.md`の分類名「監査証跡seal」)。events.dbの中身は対象にしていない。トリガーは現在Human Gate必須(2026-07-07/08是正、TODO_427、commit `1707fcc382`/`3bc80842e`「AUTO_SEAL Pack1: 日次seal系Human Gate化」)。

実測: 直近re-seal commit `de2356beebec3057a6d888d11fc9aa32b25c6040`(2026-07-07T20:03:45+09:00、anchor: re-seal after f1f0b69)。`governance/anchor_record.json`本体: `sealed_summary_hash=37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5`、`sealed_at_utc=2026-07-07T11:03:41Z`。

既にDecision Ledger `DC_20260707_021`(Human Gate Phase1承認)にて、**`governance/anchor_record.json`が「監査証跡sealの正本」と確定済み**であり、`MOCKA_OVERVIEW.json`を正本候補とする案は明示的に却下されている(理由: 表示・Cloudflare export用途であり証跡そのものではない、専用同期経路不在)。

### A-3. `governance.latest_seal.sha256`(`data/MOCKA_OVERVIEW.json`)

保証対象: `SEAL_CANONICAL_SOURCE_PROPOSAL_v0.1.md`の分類名「状態説明seal」。人間向け状態要約文書内の転記値であり、証跡そのものではない。IC_20260707_005の調査で、専用の自動同期経路(export_for_cloudflare.py・sync_watch.py等)が発見できず「手動スナップショットの可能性が高い」と既に結論されている。

実測: `sha256=ad98246bef68a9a28f56b40d8b675e2b878b20db42ebec50c525132ea947ea27`、`event_count=12171`、`date="2026-06-18"`。ファイル自体のmtimeは更新されているが、当該フィールド値は2026-06-18時点のまま変化していない。

### A-4. mocka_seal MCPツール(events台帳ハッシュ)

上記3系統とは対象が異なる第4の仕組み。`mocka_mcp_server.py`の`mocka_seal`ツールは、SQLite events全件を`json.dumps(rows, sort_keys=True)`でシリアライズしSHA-256化する。**re-seal commitの対象(gitツリー)とは全く異なり、events.db内容そのものの整合性ハッシュ**。オンデマンド計算のみで専用の永続ファイルへの自動書込みは無い。

### A-5. index.html topbarの`seal: c2d8c54e`

静的HTML内の固定文字列。`c2d8c54e`はcommit `c2d8c54edea6507e894510a22f316de3842a9df4`(2026-06-01T18:23:14+09:00、anchor: re-seal after c6c8b21)の短縮形と一致する。すなわちこの表示は「監査証跡seal」系列からのある時点のコピーであり、以降の再封印(直近de2356be、2026-07-07)を一切反映しない完全な固定表示である。動的束縛は周辺コードに見当たらない。

### A-6. 既存設計文書との関係

`docs/governance/SEAL_CANONICAL_SOURCE_PROPOSAL_v0.1.md`(TODO_371、R01監査官指示)に、既に「Seal機能分類表」として制度設計が存在する: 監査証跡seal(`anchor_record.json`、正本確定済み)/表示用seal(`ledger.json`、廃止済みLegacy)/状態説明seal(`MOCKA_OVERVIEW.json`)/未使用候補(`data/seal_log.json`)の4分類。`index.html:206`の静的seal表示がこのいずれの分類に属すべきかは、`SEAL_MIGRATION_SPEC_v0.1.md`(Phase2設計、`civilization_loop.audit`表示ロジック向け)との関係も含め、本調査だけでは確認できていない。COMMAND CENTER表示との紐付け設計は、本Recovery Planのスコープ外として別途博士確認を要する。

## 付録B: Dead Code最終監査(R01指示Task 4)

COMMAND_CENTER_DATAFLOW_CATALOG_v1.0.md 付録に判定表を掲載した(残す理由/廃止理由/Phase4要否/Phase5候補の観点)。本文書からは参照のみとする。

# COMMAND CENTER Release Checklist v1.0

指示元: R01監査官(2026-07-11 最終裁定)
種別: 再発防止制度案(提案のみ、運用への正式導入はHuman Gate承認後)
関連: COMMAND_CENTER_REGRESSION_INCIDENT_REPORT_v1.0.md 第7節「なぜ検知されなかったか」

## 1. なぜ今回の退行がHuman Gateを通過できたか(分析の要約)

COMMAND_CENTER_REGRESSION_INCIDENT_REPORT_v1.0.md 第7節で特定した5つの構造的死角:

1. 事故発生時点(2026-06-08)、Core System File保護制度自体が未成立(制度化は06-25〜06-30)
2. AUTO_SEAL機構(`anchor_update.py`)は秘密情報漏洩防止のブラックリスト検査のみで、変更内容の機能的妥当性を検証しない
3. `verify_all.py`・TIC Layer0/1の自動検証はガバナンス不変条件・サーバー疎通確認が中心で、UIのrender配線という「機能性」は検証範囲外
4. Decision Ledger56件にindex.htmlへの言及が皆無(レビュー対象に一度も上がらなかった)
5. 同型バグ(hein、TODO_362)の再発防止が個別対応止まりで、横展開・網羅スキャンという制度に発展しなかった

この5点はいずれも「COMMAND CENTERというダッシュボードの機能性を専門に検査する仕組みが、MoCKAのHuman Gate/自動検証体系のどこにも存在しない」という共通の欠落に帰着する。以下、この欠落を埋めるチェックリストを提案する。

## 2. COMMAND CENTER Release Checklist(提案)

index.htmlおよび関連APIエンドポイントに変更を加える際、Human Gate承認前に以下を実施することを提案する。

### 2-1. ライブ取得APIがUIに接続されているか

`fetchLive()`(またはそれに相当する取得処理)のjobs一覧を機械的に抽出し、各jobについて対応する`renderXxx()`呼び出しが成功パスに存在するかを検査する。COMMAND_CENTER_DATAFLOW_CATALOG_v1.0.mdの「API」列と「Render」列の対応表を、コード変更のたびに再生成し前回との差分を確認する。

### 2-2. API応答形状とAdapterの整合性

対象APIへ実際にリクエストし、レスポンスを`render`関数が期待するスキーマ(`IC.expectArr`/`expectStr`/`expectNum`等の既存integrity checker、または同等の検証)に通す。本監査で判明した通り、fetchはできてもレスポンス形状が合わずrenderできないケース(civ/todo/bee)が実在するため、fetch成功だけでなく「render関数に実際に通るか」まで検証する。

### 2-3. Render到達率

全fetch jobsのうち、実際に対応するrender関数へ到達する(dispatchされる)割合を算出する。本監査時点(2026-07-11)の実測は9job中5job(hein/tic0/ise-state/ise-sessions/gate-audit)が到達、4job(civ/todo/bee/essence)が未到達で到達率55.6%だった。リリース基準として到達率100%を目標値とし、100%未満の場合は理由(Static固定表示が意図的な設計であることの明記等)をドキュメント化した上でのみ許容する。

### 2-4. Static値の残存検査

`STATIC`定数(またはハードコードされたフォールバック値)が、対応するライブAPIの実測値と長期間(閾値は要検討、例: 30日以上)乖離したまま画面に表示され続けていないかを定期検査する。DT(Diff Tracker、index.html内`DT`オブジェクト)の仕組みを応用し、STATIC値とライブ値の差分検知に転用できる可能性がある。

### 2-5. Dead Code検査

UIから参照されないAPIエンドポイント・呼ばれないrender関数・使用されないSTATICデータフィールドを、リリースごとに棚卸しする。COMMAND_CENTER_DATAFLOW_CATALOG_v1.0.md付録の「Dead Code最終監査」表を更新し続ける運用とする。

### 2-6. Regression検査

リリース直前に、直近の`COMMAND_CENTER_DATAFLOW_CATALOG_v1.0.md`(正本)と現在のindex.html実装を突き合わせ、各パネルの状態(Normal/Regression/Static/Legacy/Dead/Planned)が意図せず後退していないかを確認する。特に「Normal→Static」「Normal→Regression」への変化は、機能が失われた可能性を示す強いシグナルとして扱う。

### 2-7. (追加提案)大規模一括書き換えのHuman Gate必須化

本件の根本原因の一つは、946行挿入/1133行削除という大規模一括書き換えが、機能的レビューを経ないまま単一commitとして成立したことにある。差分行数が一定閾値(例: 200行)を超えるindex.html(またはCOMMAND CENTER関連ファイル)の変更は、AUTO_SEAL等の自動push機構を経由させず、Human Gateでの機能的差分レビューを必須とすることを提案する。

### 2-8. (追加提案)個別バグ修正時の横展開スキャン義務化

TODO_362(heinパネル修正)のような「STATIC固定表示への配線断絶」パターンが1件発見された場合、同一ファイル内の他パネルへの横展開スキャン(本チェックリスト2-1〜2-3相当の簡易チェック)を、修正完了条件の一部として義務付けることを提案する。

## 3. 導入方針

本チェックリストは提案であり、コード上の自動化(検証スクリプトの新規実装等)は一切行っていない。導入の要否・優先順位・自動化の範囲は、Human Gateでの裁定を仰ぐ。特に2-7・2-8は運用ルールの新設(CLAUDE.md相当の規約追加)を伴うため、既存の運用ルール整備プロセスに則って博士の承認を得た上で正式化することを推奨する。

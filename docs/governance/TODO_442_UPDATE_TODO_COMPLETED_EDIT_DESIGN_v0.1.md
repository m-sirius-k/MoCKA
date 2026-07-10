# TODO_442 設計案 v0.1: mocka_update_todo completed後編集不能欠陥の修正

作成: Claude-code-sonnet-5 (くろこ)
起票経緯: R02(博士代理)指示
提出先: R02経由できむら博士Human Gateレビュー
ステータス: 設計提案のみ。コード変更は未着手・ゲート承認まで着手禁止

対応するCHANGE_START: E20260711_340318303df0f

---

## 1. 問題の実態（発端）

本セッション内でTODO_439のstatusを"完了"から"進行中"へ訂正しようとした際、
mocka_update_todo(id="TODO_439", status="進行中", ...) が
{"error": "TODO_439 not found"} を返却した。TODO_439はmocka_get_todo()の
出力（MOCKA_TODO_ACTIVE.jsonの内容）には依然として存在しており、
物理的に消失していたわけではない。同一事象がTODO_440でも再現した。

## 2. 原因の一次確認（実測、mocka_mcp_server.py実装ベース）

対象: mocka_mcp_server.py 477-509行目、elif name == "mocka_update_todo": ブロック。

該当ロジック（490-506行目、要約）:

```
for item in data.get("todos", []):
    if item.get("id") == todo_id:
        (status/contract_status/note の PATCH 更新)
        if new_status == "完了":
            item["completed_at"] = 今日の日付
            data.setdefault("completed", []).append(item)
            data["todos"].remove(item)
        updated = True
        break
if not updated:
    return {"error": f"{todo_id} not found"}
```

確定事実:
- 検索ループは data.get("todos", []) （ACTIVE配列）のみを対象とする。
  data.get("completed", []) を検索する分岐は存在しない。
- status="完了"でPATCHされた瞬間、当該itemはtodos配列から物理的に
  removeされ、同じdataオブジェクト内のcompleted配列へ移動する
  （502-503行目）。
- そのため、一度でも"完了"にPATCHされたTODOに対する以後の
  mocka_update_todo呼び出しは、statusを変更しようとする場合はもちろん、
  note一つを追記しようとするだけの場合でも、検索ループが該当itemを
  一切発見できず {"error": "... not found"} で失敗する。
  この制限は status/contract_status/note のいずれのフィールド更新にも
  一律に及ぶ（フィールド単位の制限ではなく、レコード単位で完全に
  編集不能になる）。

判定: 「ACTIVE層のみを返すmocka_get_todo()のツール仕様」の副作用ではなく、
mocka_update_todo自身の検索範囲がtodos配列に限定されているという、
このツール単体の実装上の欠陥である。ACTIVE/completed層の分離設計自体
（3層構造: ACTIVE/LOCKED/ARCHIVEとは別に、ACTIVE内部でtodos/completedを
分けている設計）は本欠陥の前提ではあるが、「分離すること」自体が
編集不能の原因ではなく、「分離後、completed側を検索する経路を
実装し忘れたこと」が直接の原因である。

## 3. 影響範囲判定: 意図的保護か、設計漏れか

結論: 現時点で確認できる一次データからは、設計漏れである可能性が高い。
意図的な「完了印の改ざん防止」を裏付ける記録は発見できなかった。

根拠:
1. 該当ロジック（todos.remove + completed.append、単一配列のみ検索）は
   このファイルの最初のコミット 0da58c809
   （"feat: MCP caliber v1.2.0 + TODO system + server status UI [E20260405]"、
   2026-04-05）の時点で既に存在する。導入時のコミットメッセージに
   completed保護に関する言及はない。
2. その後の2回の改修（e675e3de9: 2026-06-18、c9848c438: TODO_385
   contract_status分離、日付未確認）でも、このロジック自体は
   一切変更されていない。両コミットともnote/contract_statusフィールドの
   PATCH対応を追加しているが、completed配列への検索対応は
   どちらでも追加されなかった。
3. mocka_update_todoのツール説明文に含まれる「completedに移動済みの
   TODOは対象外」という一文は、git log -S検索の結果、e675e3de9
   （2026-06-18、"GROUP H/G/E batch: encoding protection + health checks
   + PHI-OS audit"）で追加されたと確認した。このコミットは11件の
   異なるTODO（TODO_338/343/337/284/296/297/266/139/323/324/271）を
   束ねた一括バッチコミットであり、上記のうちいずれも
   「update_todoのcompleted対象外」を主題とするTODOではない。
   すなわちこの一文は、既存の（誤って導入されていた）挙動を
   後から観測し、その事実をツール説明に書き足しただけのものである
   可能性が高く、意図的な設計判断としてこの制限を新設した記録ではない。
4. data/decisions/decision_ledger.jsonl（全件）をgrepしたが、
   「completed」状態のTODOの編集制限・改ざん防止に関する記述は
   一件も見つからなかった。
5. mocka_update_todoの呼び出し箇所はmocka_mcp_server.py内でこの1箇所
   のみであり、他に同種ロジックの重複実装は存在しない
   （修正の影響範囲は本ブロックに限定される）。

留意: 上記はあくまで一次データ（コード・コミット履歴・Decision Ledger）
からの実測に基づく推定である。きむら博士が文書化せずに意図した
設計判断が別途存在する可能性は本調査だけでは排除できない。
その場合は博士の記憶・判断を一次情報として優先し、本判定を訂正する。

## 4. 修正方針（2択）

### 案(a): completed状態からの差し戻し専用経路（未完了へ戻すことだけ許可）

新規の明示的な「差し戻し」操作（例: mocka_reopen_todo(id, target_status, reason)）
を追加する。

- 検索対象を data.get("completed", []) に限定する（通常のmocka_update_todoの
  検索範囲=todosとは完全に分離する）。
- target_statusは"完了"以外のTODO_STATUS_ENUM値のみ許可する
  （再度"完了"を指定してこの経路を使うことは禁止し、
  「完了扱いのまま中身だけ書き換える」抜け道を塞ぐ）。
- reason（差し戻し理由）を必須パラメータとする。空文字は拒否する。
- 差し戻し実行時、completed配列から該当itemを取り出し、
  status=target_status、completed_atフィールドを削除し、
  todos配列へ戻す。
- 差し戻し操作自体をmocka_mcp_server.py内部からmocka_write_event相当の
  記録処理に必ず接続し（呼び出し元のAIが記録し忘れても、ツール自身が
  差し戻しイベントを記録する）、append-only原則（イベント台帳は追記のみ、
  既存イベントの書き換え・削除は行わない）を維持する。
  reasonの内容をそのままイベント本文に含める。
- 差し戻し後は、通常のmocka_update_todo（todos配列を検索する既存経路）が
  そのまま機能するため、note追記等の以後の編集は追加の実装なしに
  従来通り可能になる。

### 案(b): completed維持のままnote追記のみ許可（statusは触らせない）

mocka_update_todoの検索ループに、data.get("completed", [])も対象に含める
分岐を追加するが、completed状態のitemに対してはnoteフィールドのみ
更新を許可し、status/contract_statusの変更は拒否する。

- completed状態のitemが見つかった場合、statusまたはcontract_status
  引数が指定されていれば {"error": "completed item: status変更不可、
  reopenが必要"} 等で拒否し、noteのみ更新して保存する。
- itemはcompleted配列に留まったまま（todos配列への移動は発生しない）。

## 5. 案の比較と推奨

比較表:

| 観点 | 案(a) 差し戻し専用経路 | 案(b) note追記のみ許可 |
|---|---|---|
| 今回(TODO_439)の実際の要求（完了→進行中）を満たすか | 満たす | 満たさない（statusが完了のまま動かせない） |
| 完了印の意図しない上書きリスク | 低い（reason必須・別経路・"完了"への再指定禁止で歯止め） | 低い（statusに一切触れない） |
| 実装範囲 | 新規経路1本追加 | 既存検索ループの条件分岐追加 |
| 事後の note 以外の編集（優先度・担当者等） | 差し戻し後は既存PATCH経路で全フィールド対応可 | 対応不可（note限定のまま） |

推奨: 案(a)。

理由:
1. 本セッションで実際に発生した要求は「誤ってcompletedにしてしまった
   TODOのstatusをprogressへ戻す」ことであり、案(b)だけではこの
   ユースケースを解決できない（noteは足せてもstatus="完了"の表示は
   残ったままになる）。
2. 案(a)は「completed=一方向の確定」という既存の（結果的に）保護的な
   性質をむしろ明文化・強化する形になる。差し戻しを通常のPATCH動作から
   切り離し、reason必須・"完了"への再指定禁止という専用の歯止めを
   課すことで、3節で判定した「設計漏れ」を単純に開放するのではなく、
   意図の有無によらず今後は正式な保護仕様として運用できる。
3. 差し戻し後は既存のmocka_update_todo（todos配列検索）がそのまま
   機能するため、note以外のフィールド編集についても案(a)だけで
   カバーできる。案(b)は差し戻し機能なしに単独では運用上不十分であり、
   仮に両方を実装するとしても案(a)が必須で案(b)は任意の付加機能となる。
4. append-only原則は、差し戻し操作をツール内部で必ずイベント記録に
   接続する設計とすることで、案(a)側でも損なわれない
   （呼び出し元の記録漏れに依存しない、システム側の強制）。

## 6. 実装スコープ外・未実施事項（本ドキュメント作成時点）

- コード変更は一切行っていない。mocka_mcp_server.pyへの実装着手は
  Human Gate承認後まで行わない。
- 案(a)を選定した場合の新規ツール名・パラメータ名の最終確定
  （例: mocka_reopen_todo という名称が既存の命名規則
  mocka_<動詞>_<対象> と整合するか）は、ゲート承認時にあわせて
  確定する。
- 案(a)のreason必須化にともなう、reasonの最小文字数・禁止語彙等の
  詳細バリデーション仕様は本ドキュメントでは規定しない
  （必要であれば別途ゲートで指示を受けて詳細化する）。
- 既存のcompleted配列に既に格納されている過去の全TODO（TODO_439/440
  以外の既存completed項目）に対する遡及的な救済措置の要否は、
  本設計案のスコープ外とする。

## 7. Human Gate裁定事項（R02より提出）

1. 3節の判定（設計漏れ、意図的保護の記録なし）を承認するか、
   または博士の記憶にある未文書化の意図があれば提示いただきたい。
2. 4節の2択のうち、5節の推奨（案(a)）を承認するか、
   別案・修正案があれば指示いただきたい。
3. 承認後、実装（コード変更）着手の可否指示。

# STATE_INTEGRITY_CHECK_DESIGN_v0.1

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 設計提案のみ、実装は未着手(監査官R01「MoCKA State Integrity Restoration Plan」Phase 3対応)

## 背景

2026-07-08の状態監査で判明した事象は、一次データの破損ではなく、以下3層のうち後段2層が陳腐化・誤解釈を起こしたことによる。

```
一次データ（真実） -- 健全
    ↓
派生状態表示 -- 一部陳腐化(MOCKA_OVERVIEW_STALENESS_REPORT.md参照)
    ↓
人間向け監査資料 -- 一部誤解釈(外部状態報告のTODO_206/242等)
```

さらに調査の過程で、「ファイルが存在する」を「実装完了」と誤推論するリスク(`interface/impact_analyzer.py`が実装・実行済みだがTODO_206は`未着手`のまま、`governance/human_gate_cli.py`がTODO/Decision Record不在のまま存在)も確認された。本設計は、この2種の誤差(状態表示の陳腐化・存在と完了の混同)を将来にわたって検知する仕組みを定義する。**本文書は設計のみであり、コード実装は行わない。**

## チェック1: TODO整合(TODO status ≠ OVERVIEW status)

- **入力**: `MOCKA_TODO_ACTIVE.json`(todos+completed)・`MOCKA_TODO_ARCHIVE.json`の各TODO_IDのstatus、および状態表示層(現行は`MOCKA_OVERVIEW.json`、将来はTODO_428のGenerator出力)がTODO_IDに紐付けて含意するstatus文言。
- **検知条件**: 同一TODO_IDについて、一次データのstatusと状態表示層の含意status文言が一致しない場合に警告。
- **既知の実例**: TODO_242(進行中 vs 未着手)、TODO_325(保留 vs 未着手)、TODO_266(完了 vs 保留中)、TODO_171(完了 vs 未着手扱い)、TODO_215/TODO_346(完了だがARCHIVE層のみに存在、状態表示層は未対応のまま参照)。
- **設計上の留意**: ACTIVE層だけでなくARCHIVE層も参照しないとTODO_215/346型の乖離を検知できない(MOCKA_OVERVIEW_STALENESS_REPORT.md Q3参照)。

## チェック2: Event整合(reference_event ≠ 引用event)

- **入力**: 各TODO/Incident/Decisionレコードの`reference_event`フィールドと、`events.db`(または`events_latest.json`)の実際のevent_id・title・why_purpose。
- **検知条件**: `reference_event`が指すevent_idが実在しない、または実在するが内容(title/why_purpose)が当該レコードの主張と無関係な場合に警告。
- **既知の実例**: 今回の外部状態報告が引用した`E20260708_6037919164306`は実在するが内容は`CONSISTENCY_CHECK_TEST`という無関係な汎用イベントであり、実際の検証イベントは`E20260708_74001109651fa`(`GL7_FIX_VERIFY_TEST`)だった。この種の「実在するが無関係」な誤引用は、reference_event不在チェックだけでは検知できないため、内容の意味的一致確認(タイトル文字列の部分一致等の軽量な方式でよい)も設計に含める。

## チェック3: Artifact整合(untracked file + related TODO exists → 確認要求)

- **入力**: `git status --porcelain`のuntracked/modifiedファイル一覧と、`MOCKA_TODO_ACTIVE.json`の各TODOのtitle/descriptionに含まれるファイルパス名。
- **検知条件**: untracked/modifiedなファイルパスが、status`未着手`または`進行中`のTODOのtitle/description内で言及されているファイルパスと一致する場合、「要確認」フラグを立てる(自動昇格はしない)。
- **既知の実例**: `interface/impact_analyzer.py`(untracked、TODO_206のtitle「impact_analyzer.py」と一致)、`governance/human_gate_cli.py`(TODOなし、Decision Record候補として別途扱う)。

## 状態昇格ルール(誤推論防止、既存のTODO_384 status正規値運用に追記する形で適用)

今回の混乱原因は「ファイルが存在する」→「実装完了」という誤推論だった。これを禁止し、以下の順序でのみTODO statusの昇格(未着手→進行中→完了)を認める。

```
Artifact存在 → Review → Test → Decision Record → Commit → TODO Status更新
```

Integrity Check(上記3チェック)は、この順序のどこで昇格条件を満たしていないかを検知・警告するのみであり、**status自体を自動で書き換えることはしない**(自動承認機構の禁止、[[feedback_flag_autonomy_risk_in_governance_design]]と同じ原則)。あくまで人間(きむら博士)の判断を促す警告出力に留める。

## 実装方針(次工程、今回は未着手)

- TODO_428(MOCKA_OVERVIEW_CURRENT_GENERATION)の一部として、Generatorの出力に本チェックの警告セクションを含める設計が自然。
- 単独の`state_integrity_check.py`のようなスクリプトとして先行実装し、Generator本体より先に「検知のみ」を稼働させる分割も可能(Generatorの完成を待たずに警告機構だけ先に使える利点がある)。この分割方式の採否は次工程で判断する。
- 実行順序: AUTO_SEAL Pack1(TODO_427)のcommit・Phase 4 Close確定後に着手する。

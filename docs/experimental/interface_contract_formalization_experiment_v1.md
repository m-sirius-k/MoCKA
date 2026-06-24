# Interface Contract Formalization Experiment v1 (Non-Canonical)

Status: EXPERIMENTAL / NON-CANONICAL (思考実験・形式化資料)
Date: 2026-06-24
作成者: Claude(別チャット, Claude Code環境) / 整理・登録: Claude-sonnet-4-6

## 0. 本文書の位置づけ(最重要)

本文書は正式な制度文書ではない。以下の既存正式文書を上書き・置換するものではなく、
それらの下位にある形式的な抽象化モデルとして位置づける。

優先順位(上位が常に優先):

1. `docs/governance/mocka_hab_v1_contract.md` (HAB正式定義)
2. `docs/governance/mocka_human_gate_decision_definition_v1.md` (Human Gate正式定義、
   Human Gate Finalizationの裁定主体は博士本人に固定。これは本文書のいかなる記述
   よりも優先される)
3. 本文書(形式実験・公理化レイヤ)

本文書が既存正式文書と矛盾する場合、既存正式文書が常に正しい。本文書はpre-authorization
state、FROZEN層、Trigger Wiring凍結方針を一切変更しない。

## 1. 経緯

別のClaude Codeチャットセッションにおいて、HAB/Human Gate/Phase10/Extension間の
インターフェース契約を独立に議論し、以下の段階を経て公理系として形式化した。

1. Interface Contract v1.0(レイヤ間入出力形式の固定)
2. HAB Definition Fixation v1.0(状態粒度・不変条件)
3. Phase10 Dependency Revalidation(契約整合性検査)
4. Final Integration Architecture v2.0/v2.1(FAL統合・観測経路確定)
5. 静的運用マップ(非発火・非トリガー版)
6. 監査仕様 v1/v2(構造破綻検知・証明体系化)
7. 公理系 A1-A6(完全公理化)
8. 公理系メタ整合性検査v1

## 2. 既存正式文書との重要な差異(必読)

本実験で導入した`FAL(Finalization Attestation Layer)`は、`authority_tag`を
`HUMAN_FINALIZER | SYSTEM_EVALUATOR | EXTERNAL_INTERFACE`という抽象enumとして
定義したが、これは既存正式文書(`mocka_human_gate_decision_definition_v1.md`)が
すでに確定している「Human Gate Finalizationの裁定主体は博士本人という実在の人物に
固定する」という安全設計より抽象度が低い(誰が書き込んだかを実名で検証する仕組みを
持たない)。

既存正式文書がこの問題を先に解決済みである(AI単独裁定化を防ぐため、抽象ラベルでは
なく実在の人物に裁定権を縛った)ため、本文書のFAL/`authority_tag`は「既存Human Gate
Finalization定義の内部表現・形式的下位モデル」として位置づける。両者が衝突する場合は
既存定義(博士本人)が優先する。

## 3. 公理系 A1-A6(参照用、形式実験としての要約)

```
V = {Extension, HAB, Core, Phase10, FAL, Runtime}
E = { (Extension,HAB), (HAB,Core), (Core,Phase10), (Phase10,FAL), (FAL,Extension) }

A1: E以外の辺は存在しない(辺の固定性)
A2: 各ノードは単一Roleのみ持つ(役割単射性)
A3: can_commit(decision) <=> Authority = HUMAN_FINALIZER(確定権の単一性)
A4: Observation Path と Control Path はノード・辺を共有しない(観測非干渉性)
A5: HABはappendのみ、既存recordは変更不可(記録不変性)
A6: 時間変数なし、本体系は静的命題のみで構成される(非実行性)
```

本公理系は実行モデル・トリガーモデルを含まない(A6により体系外)。Trigger Wiring
凍結方針と整合する。

## 4. 監査仕様 v1/v2(破綻検知ルール、参照用要約)

破綻タイプ4分類:
- 依存逆転破綻(下位層が上位層を参照)
- 未定義経路破綻(マップ外の経路でデータが流れる)
- 権限逸脱破綻(本来の権限層以外が裁定・確定を行う)
- 役割混線破綻(評価・変換・裁定・署名が同一層に混在)

検出のみを行い、自動修復・自動裁定は一切行わない(実行性なし、A6に従う)。

## 5. 実装状態

本文書はいかなる実装・コード変更も含まない。コード・実行システムは一切実装していない。
本文書を理由にHAB/Human Gate正式文書の改版を行う場合は、博士本人の明示的な指示と
正式文書側でのCHANGE_START/CHANGE_DONE記録を要する。

## 6. 現在の運用状態(本文書の効力範囲外の事実)

2026-06-24時点の実際の状態は本文書により変化しない:
FROZEN=不変、Extension=DRAFT、Human Gate=未裁定、pre-authorization state=継続中、
Trigger Wiring=凍結継続。

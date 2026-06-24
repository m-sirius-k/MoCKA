# A6-v2: Structural Consistency Layer

Status: EXPERIMENTAL / META / NON-CANONICAL
Date: 2026-06-24
作成者: Claude(別チャット, Claude Code環境) / 整理・登録: Claude-sonnet-4-6

## 0. 必須ラベル(本文書の位置づけ、最重要)

- 本文書はA6(意味構造層)のv2拡張であり、A6の静的性質(非実行性)を変更しない。
- 正式governanceではない。`docs/governance/`配下の正式文書を上書き・置換しない。
- 本文書はA7(Trigger Wiring/実行モデル化/Relay接続/発火タイミング)には一切踏み込まない。
  v2はあくまで「A6内の検証可能性」を高めるものであり、実行可能性を追加するものではない。
- 優先順位(L0-L3、`integrated_architecture_compressed_v1.md`のv1.1番号体系)は不変。

## 1. 目的

A6を「読める設計」から「検証できる設計」へ拡張する。具体的には、これまで個別に
議論されてきた監査仕様(v1/v2)・公理系メタ整合性検査の内容を完全版として統合し、
さらにSVG-Contract対応マッピング・公理優先順位ルール・差分検知ルールの3要素を
新規追加する。

## 2. 既存内容の統合(完全版)

### 2.1 監査仕様v1: 破綻タイプ4分類

- **依存逆転破綻**: 下位層が上位層を参照する構造(例: HABがHuman Gateの判断結果を
  参照する)。即時違反。
- **未定義経路破綻**: マップに存在しない経路でデータが流れる構造(例: Extension→
  Phase10直結)。契約未成立。
- **権限逸脱破綻**: 本来の権限層以外が裁定・確定を行う構造(例: SYSTEM_EVALUATORが
  Finalizationを書き換える)。制度破綻(FAL無効化扱い)。
- **役割混線破綻**: 評価・変換・裁定・署名の機能が同一層に混在する状態。
  アーキテクチャ崩壊。

### 2.2 監査仕様v1: 整合性ルール(Invariant Rules)

- R1(単方向性維持): HABは読み取り中心構造。上位層からの意味付与は禁止。
- R2(裁定分離原則): 評価(Human Gate Core)・変換(Phase10)・署名(FAL)は絶対に
  統合されない。
- R3(観測分離原則): Extensionは必ずHABにのみ接続。Core系とは直接結合しない。
- R4(署名唯一性): FinalizationはFALのみで確定される。SYSTEM/Extensionは確定権を
  持たない。

### 2.3 監査仕様v2: 形式化(グラフ理論的定式化)

```
G = (V, E)
V = {Extension, HAB, Core, Phase10, FAL, Runtime}
E = { (Extension,HAB), (HAB,Core), (Core,Phase10), (Phase10,FAL), (FAL,Extension) }
```

定理1-5(単方向分離性/責務分離の完全性/署名唯一性/観測閉包性/非干渉性)は、
`interface_contract_formalization_experiment_v1.md`に記載のA1-A6から導出済み。
v2の役割はこれらを「証明」ではなく「破綻検出」の形式的基盤として位置づけること。

### 2.4 公理系メタ整合性検査v1(完全版)

- 循環依存チェック: A1(構造固定)・A3(権限制約)・A4(分離制約)は相互参照せず、
  循環依存なし(PASS)。
- 冗長性チェック: A4(観測分離)はA1(辺の固定性)から部分的に導出可能だが、A1は
  「構造」、A4は「集合分離」という異なる階層の主張であるため非冗長(PASS)。
- 過剰制約チェック: A3(確定権)とA5(記録不変性)は独立、A6(非実行性)は全体メタ
  制約であり、制約衝突なし(PASS)。
- 結論: 公理系(A1-A6)はConsistent(矛盾なし)・Minimal(冗長公理なし)・Closed
  (外部依存なし)・Non-temporal・Non-executable。

## 3. 新規拡張(v2固有)

### 3.1 SVG-Contract対応マッピング(逆引き可能性)

| SVGノード/要素 | 対応するContract/Axiom条項 |
|---|---|
| L0破線枠(博士本人) | External Dependency Structure 第3章(最終裁定/意味確定/責任帰属/公理選択) |
| L1 Relay/Orchestra/Memory/PHI-OS | Integrated Architecture v1.1 第2章L1定義 |
| L2 HAB/Human Gate/Phase10/FAL | Integrated Architecture v1.1 第2章L2定義、HAB Definition Fixation、Human Gate Decision Definition(正式governance側) |
| L3枠 | Boundary of Formal System 第3章(表現不能領域) |
| 実線矢印(L1/L2/L3→L0) | Axiom A3(確定権の単一性)、A4(観測非干渉性) |
| 破線矢印(L0→L3) | External Dependency Structure 第3.1-3.2節(最終裁定機能/意味確定機能) |
| fadeIn/pulse/flowアニメーション | Institutional Locked Diagram 第4章 |

この表により、SVGの任意の図形要素から対応するMarkdown条項を一意に逆引きできる。
逆方向(条項→図形要素)も同様に一意である(R1相当の単方向性をマッピング自体にも
適用)。

### 3.2 公理優先順位ルール

公理系メタ整合性検査v1の結論により、A1-A6は相互に独立(非冗長・非循環)である
ため、通常運用において優先順位の適用は発生しない。ただし将来A7以降の拡張で
新公理が追加され、既存公理と表層的に衝突する事態に備え、以下の優先順位を
事前に定義する:

1. A6(非実行性)が最優先される。いかなる新公理も、A6を無効化する形で追加
   されることはない(無効化したい場合はA6自体の改版が必要であり、それは
   「拡張」ではなく「体系の置換」となる)。
2. A3(確定権の単一性)はA6に次いで優先される。L0(博士本人)の裁定権を弱める
   方向の新公理は採用しない。
3. A1・A2・A4・A5は同列であり、相互に矛盾しない限り全て適用される。

### 3.3 差分検知ルール(v1→v2、将来のv2→v3にも適用)

バージョン間の差分は以下の3種に分類して記録する:

- **意味差分(Semantic Diff)**: 既存条項の解釈が変わる場合。例: 本文書2.1-2.4節は
  既存内容の「完全版化」であり意味差分ではない(要約→詳細の展開のみ)。
- **構造差分(Structural Diff)**: L0-L3の構造・矢印・公理が変わる場合。これは
  既存ファイルへの追記ではなく、新バージョンファイルの作成を要する(例:
  `integrated_architecture_compressed_v1.md`→v2作成時はv1を残し、互換注釈を
  v1側に追記する、というこれまでの運用パターンを継続する)。
- **拡張差分(Additive Diff)**: 既存構造を変更せず新規要素を追加する場合(本文書
  第3章がこれに該当)。既存ファイルは無変更のまま、新規ファイルとして追加する。

## 4. やらないことの確認(変更禁止事項)

- A7(Trigger Wiring、実行モデル化、Relay実データ接続、発火タイミング定義)には
  一切踏み込まない。
- L0の機能化・監査層化・自動化・削除統合は引き続き絶対禁止。
- 既存のSVG(`l0_l3_locked_institutional_diagram_v1.svg`)・ロックMD
  (`institutional_locked_diagram_v1.md`)は本文書により変更しない(第3.1節の
  対応表は新規追加情報であり、既存ファイルへの逆方向の書き込みは行わない)。

## 5. 結論

A6-v2は「意味構造+構造検証レイヤ」として、既存A6の閉包性(seal_a6_final_v1)を
破壊せずに、検証可能性(逆引きマッピング・優先順位・差分管理)を追加する。これは
拡張差分(Additive Diff、第3.3節の分類による)であり、既存のseal済みコミットに
対する変更要求ではない。

## 6. 実装状態

本文書はいかなる実装・コード変更も含まない。コード・実行システムは一切
実装していない。

## 7. 現在の運用状態(本文書の効力範囲外の事実)

2026-06-24時点の実際の状態は本文書により変化しない:
FROZEN=不変、Extension=DRAFT、Human Gate=未裁定、pre-authorization state=継続中、
Trigger Wiring=凍結継続。

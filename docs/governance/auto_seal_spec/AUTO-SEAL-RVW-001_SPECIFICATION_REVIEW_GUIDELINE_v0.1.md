# AUTO_SEAL Specification Review Guideline v0.1

- Document ID: AUTO-SEAL-RVW-001
- Series: AUTO_SEAL Documentation Framework
- Class: Process
- Status: Review Candidate (S0.5 Series は Review Complete(HG-11/DC_20260713_021)。文書個別 Status の Review Complete 昇格と IDX-001 Master Catalog 同期は全文書版確定後(HG-13/DC_20260713_023)へ繰延)
- Version: 0.2
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0.5, Review Integration Phase)
- Classification: Documentation only. No source code, no Core System File change.
- Depends on: AUTO-SEAL-ARCH-001, AUTO-SEAL-IDX-001, AUTO-SEAL-STD-005 (Status), AUTO-SEAL-GLO-001
- Future: 本ガイドラインは AUTO-SEAL-STD-009 (Review Standard) として規格化を検討中(予約)

本書は AUTO_SEAL Specification Series の「制度レビュー」の観点・役割・完了条件を定める再利用
可能な資産である。実装レビューではなく、規格文書そのものの品質保証を対象とする。個々の
レビュー依頼(誰にいつ送るか)は本書の対象外であり、Human Gate 主体(きむら博士)が回す。

---

## 1. 目的

Specification Series の各文書を、一貫した観点で繰り返しレビューできるようにする。今回の
S0.5 だけでなく、今後追加される全ての Standard / Template / Proposal に同一の品質保証
プロセスを適用できることを狙う。

## 2. 役割分離(制度レビューの独立性)

設計・レビュー・採択・実装を独立させる。同一主体が複数の役割を兼ねない。

| 役割 | 担当 | 責務 |
|---|---|---|
| 制度設計・最終判断 | きむら博士 | Human Gate、採択 / 却下 |
| 第一次レビュー | ChatGPT | 規格構造・アーキテクチャ・整合性 |
| 第二次レビュー | Gemini | 用語・運用性・長期保守性・第三者視点 |
| 文書整備・反映 | くろこ | 修正反映・整形・版管理 |
| 実装(承認後) | くろこ | 規格に従ったコード変更 |

くろこはレビュー依頼の起票主体にならない(設計者・実装者・レビュー起票者を近づけない)。

### 2.1 AI と Human Gate の権限境界(GEM-004 反映、DL-C1: DC_20260713_013)

AI(ChatGPT / Gemini / くろこ)の役割は、レビュー観点に対する提案・構造化・検証補助に限定される。
規格文書の承認(Approved)・採択・発効(Effective)化の権限は人間(Human Gate、きむら博士)のみが
持つ。AI は修正案の起草・整形・整合性検証を行うが、Review Complete 以降のいかなる状態遷移
(Approved / Effective)も Human Gate の明示承認を成立条件とする(approved_by=human、DC_20260713_003)。
自動処理(GL7 pass 等)による承認代替は認められない(事前フィルタに留まる)。本節は第2節の役割分離
を変更するものではなく、AI と人間の権限境界を説明責任の観点から明文化するものである。

## 3. レビュー観点(7 Dimensions)

各観点は「何を見るか」と「合格条件(Pass)」を持つ。

### 3.1 Structure Review

- 見る: Layer 構造(Foundation / Process / Governance)が一貫しているか。1 文書 1 分類か。
  責務境界(AUTO-SEAL-ARCH-001 第 3 章)に重複がないか。
- Pass: 全文書が単一 Class を持ち、ある概念の定義場所が 1 つに限られている。

### 3.2 Dependency Review

- 見る: 循環参照が存在しないか。依存が一方向(Foundation <- Process <- Governance)か。
- Pass: Dependency Matrix(AUTO-SEAL-IDX-001 第 3 章)に循環がなく、逆流参照がない。

### 3.3 Terminology Review

- 見る: 用語が Glossary(AUTO-SEAL-GLO-001)と一致しているか。文書内で用語を再定義していないか。
- Pass: 全用語が GLO-001 の定義に一致し、Series 内で再定義がない。

### 3.4 Conformance Review

- 見る: Normative キーワード(SHALL / SHOULD / MAY)が正しく使われているか。Normative(規範)と
  Informative(参考)が分離され、各要件が検証可能か。
- Pass: 規範要件が SHALL / SHOULD / MAY で表現され、参考記述と混在しない。
- 注: SHALL / SHOULD / MAY の全面適用は Sprint S1 の詳細化事項。本観点は S1 で満たすべき基準を
  あらかじめ登録するもの。

### 3.5 Traceability Review

- 見る: 参照切れ(dangling reference)がないか。上流 Decision / 設計文書への参照が有効か。
- Pass: 全参照先が実在し、pending_ref 等の接続要件(AUTO-SEAL-STD-002)が明記されている。

### 3.6 Governance Review

- 見る: Human Gate との矛盾がないか。恒常的な自動承認ループ(自律裁定化)を再導入していないか。
  approved_by=human 原則(GOV-DESIGN-ASBD-001 / DC_20260713_003)と整合しているか。
- Pass: 承認主体が人間で、GL7 等は事前フィルタに留まり、RB-2 型の矛盾がない。
- 注: 本観点の最終判断は Human Gate(きむら博士)。レビュアーは候補を指摘する。

### 3.7 Extensibility Review

- 見る: M3 以降(将来の Standard / Migration)を阻害しないか。TYPE / 番号体系が拡張余地を持つか。
- Pass: 将来拡張ルール(AUTO-SEAL-ARCH-001 第 6 章)と矛盾せず、番号が枯渇しない。

## 4. レビュアー観点の分担(重複回避)

第一次(ChatGPT)と第二次(Gemini)は重ならないように分担する。

| レビュアー | 主担当 Dimension | 重点 |
|---|---|---|
| ChatGPT(第一次) | Structure / Dependency / Conformance / Extensibility | 規格構造・アーキテクチャ・番号 / Prefix / Metadata 体系・ライフサイクル整合 |
| Gemini(第二次) | Terminology(自然さ)/ 可読性 | 英文表現・用語の自然さ・他規格との比較・長期保守性・第三者視点 |
| 共通 | Traceability / Governance(候補指摘のみ) | 参照切れ・Human Gate 矛盾の一次検出 |

Terminology は両者が触れるが角度が異なる。ChatGPT は Glossary との構造的一致、Gemini は
用語の自然さ・言語的品質を見る。

## 5. レビュー完了条件(Review Complete)

次を全て満たした時点で対象文書群を Review Complete とする。

1. 第一次(ChatGPT)・第二次(Gemini)の両レビューコメントが出揃っている。
2. くろこがコメントを統合し、修正版を作成・版管理している。
3. 未解決の重大指摘(Blocking)がゼロである。

Review Complete の後に Human Gate(きむら博士)へ渡す。

## 6. ライフサイクル上の位置

本ガイドラインは次のライフサイクル(AUTO-SEAL-STD-005 準拠)の Review Candidate から
Review Complete までの工程を規定する。

```
Review Candidate -> Review Complete -> Human Gate -> Approved -> Effective
```

## 7. 将来の規格化(予約)

本ガイドラインは AUTO-SEAL-STD-009 (Review Standard) として規格化することを検討する。
レビュー観点・役割分担・完了条件を標準化すれば、Proposal に限らず今後の全 Standard /
Template に同一の品質保証プロセスを適用でき、Series 全体のレビュー方法まで規格として
一貫させられる。番号 STD-009 は本用途に予約する(AUTO-SEAL-IDX-001 Master Catalog)。

## 8. Non Goals

- 個別のレビュー依頼の起票・送付(Human Gate 主体が回す)。
- 実装レビュー(本書は制度レビューのみ)。
- 本ガイドラインに基づく実際のレビュー実施そのもの。

## 9. History

- 2026-07-13: 初版(v0.1)。KUROKO-DOC-S0-001 Sprint S0.5。きむら博士裁定に基づき、制度
  レビューの 7 観点・役割分離・レビュアー分担・完了条件・ライフサイクル位置を定義。将来の
  AUTO-SEAL-STD-009 (Review Standard) 規格化を予約。Review Candidate として Human Gate 待ち。
- 2026-07-13: S0.5 二次レビュー GEM-004(Major、DL-C1: DC_20260713_013 採用)反映。第2.1節
  「AI と Human Gate の権限境界」を追加。既存の役割分離(第2節)・ARCH-001 責務境界・STD-005
  Status 語彙は不変。反映はきむら博士の限定凍結解除(RVW-001 / GLO-001 のみ)による。
- 2026-07-13: 版 re-cut v0.1 -> v0.2(HG-12 / DC_20260713_022)。第2.1節追加(GEM-004 反映)を版へ確定。
  S0.5 Series は Review Complete(HG-11 / DC_20260713_021、現時点のレビュー完了状態。変更は HG-08 フロー)。
  文書個別 Status の Review Complete 昇格と IDX-001 Master Catalog の version 列同期は全文書版確定後
  (HG-13 / DC_20260713_023)へ繰延。Document ID 不変(ARCH-001 第5.3節)。版確定=不変化ではなく改版経路
  (変更要求 -> 影響評価 -> Human Gate -> 改版)を維持。

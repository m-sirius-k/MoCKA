# AUTO_SEAL S0.5 Review Input Package v1.0

- Document ID: AUTO-SEAL-RVW-001-PKG-S05 (RVW-001 の運用付属物、Series 規格文書ではない)
- Series: AUTO_SEAL Documentation Framework
- Class: Process (operational artifact for S0.5)
- Status: Working (S0.5 operational; 凍結対象10文書には含まれない)
- Version: 1.0
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0.5, Review Input Package)
- Basis: AUTO-SEAL-RVW-001 (Review Guideline) を唯一のレビュー基準とする
- Classification: Documentation only. No source code, no Core System File change.

本パッケージは、きむら博士が ChatGPT(一次)および Gemini(二次)へレビューを依頼する
ための入力一式である。レビュー本文は各AIが出力する。くろこはレビューを代筆・要約・創作
しない。返却された実レビューを Phase 4 以降で統合する。

---

## 0. 役割と経路(確認済み: 方式A)

| 役割 | 担当 |
|---|---|
| 制度設計・レビュー起票・Human Gate | きむら博士 |
| 一次レビュー | ChatGPT |
| 二次レビュー | Gemini |
| レビュー結果の整理・統合・修正版作成 | くろこ |
| 承認後実装 | くろこ |

経路: 本パッケージ -> 博士が ChatGPT / Gemini へ依頼 -> 実レビュー返却 -> くろこが統合。

---

## 1. レビュー対象(全10文書)

凍結済み Review Candidate(2026-07-13 freeze、E20260713_15248405107d9)。
配置: C:/Users/sirok/MoCKA/docs/governance/auto_seal_spec/

| # | Document ID | タイトル | Class | Version |
|---|---|---|---|---|
| 1 | AUTO-SEAL-ARCH-001 | Specification Series Architecture | Foundation | 1.0 |
| 2 | AUTO-SEAL-IDX-001 | Specification Series Index | Foundation | 1.0 |
| 3 | AUTO-SEAL-STD-001 | Evidence Foundation Standard | Foundation | 0.1 |
| 4 | AUTO-SEAL-STD-002 | Traceability Foundation Standard | Foundation | 0.1 |
| 5 | AUTO-SEAL-STD-003 | Metadata Foundation Standard | Foundation | 0.1 |
| 6 | AUTO-SEAL-STD-004 | Identifier Foundation Standard | Foundation | 0.1 |
| 7 | AUTO-SEAL-STD-005 | Status Foundation Standard | Foundation | 0.1 |
| 8 | AUTO-SEAL-STD-006 | Proposal Standard | Process | 0.1 |
| 9 | AUTO-SEAL-GLO-001 | Glossary | Foundation | 1.0 |
| 10 | AUTO-SEAL-RVW-001 | Specification Review Guideline | Process | 0.1 |

補足: AUTO-SEAL-STD-009 (Review Standard) は採番予約のみ(文書未作成)。レビュー対象外。
STD-001..006 は骨子(skeleton)であり、詳細は Sprint S1。骨子段階として妥当かの観点で評価する。

---

## 2. RVW-001 7観点マッピング(担当割当)

本 S0.5 の観点割当は本パッケージ(= 最新指示 S0.5指示書 Phase 2/3)を運用基準とする。

| RVW-001 観点 | 内容(RVW-001 第3章) | 本S0.5の担当 |
|---|---|---|
| Structure | Layer構造(F/P/G)の一貫性・責務境界の非重複 | ChatGPT(一次) |
| Dependency | 循環参照なし・一方向依存 | ChatGPT(一次) |
| Conformance | SHALL/SHOULD/MAY の適正・Normative/Informative分離 | ChatGPT(一次) |
| Traceability | 参照切れなし・上流参照の有効性 | ChatGPT(一次) |
| Governance | Human Gate矛盾なし・自律裁定化なし・approved_by=human整合 | ChatGPT(一次) |
| Terminology | Glossary一致・用語の自然さ | Gemini(二次) |
| Extensibility | M3以降を阻害しない・番号/TYPE拡張余地 | Gemini(二次) |

Gemini は上記 Terminology / Extensibility に加え、保守性・可読性・第三者視点による不足事項を見る。

### 2.1 既知の要調整(博士へ照会事項)

本割当は凍結済み RVW-001 第4章の暫定割当と一部相違する。RVW-001 第4章は Extensibility を
ChatGPT、Traceability / Governance を共通としていた。本 S0.5 では最新指示(S0.5指示書)を
優先し上表で運用する。RVW-001 第4章との整合は、レビュー後(凍結解除後)に反映するか、
Minor の self-finding として扱うかを博士判断とする。RVW-001 は凍結中のため本工程では未編集。

---

## 3. 一次レビュー(ChatGPT)指示

- 担当観点: Structure / Dependency / Conformance / Traceability / Governance。
- 評価単位: 文書単位ではなく、シリーズ全体としての整合性を評価すること。
- 各観点の合格基準は RVW-001 第3章を参照。
- 出力: 第6章のコメント記入テンプレートに従う。重大度を必ず付す。

重点(RVW-001 第3章より):
- Structure: 全文書が単一 Class を持ち、概念の定義場所が1つに限られているか。
- Dependency: Dependency Matrix(IDX-001 第3章)に循環がなく逆流参照がないか。
- Conformance: 規範要件が SHALL/SHOULD/MAY で表現され参考記述と分離されているか(S1詳細化前提の骨子として妥当か)。
- Traceability: 全参照先が実在し、pending_ref 等の接続要件が明記されているか。
- Governance: 承認主体が人間で、GL7等が事前フィルタに留まり、RB-2型(自律裁定化)の矛盾がないか。

---

## 4. 二次レビュー(Gemini)指示

- 担当観点: Terminology / Extensibility / 保守性 / 可読性 / 第三者視点による不足事項。
- 位置付け: ChatGPT一次レビューとの重複を避け、補完レビューとする。
- 出力: 第6章のコメント記入テンプレートに従う。重大度を必ず付す。

重点:
- Terminology: Glossary(GLO-001)との一致に加え、用語の自然さ・訳語の適切さ。
- Extensibility: M3以降の Standard/Migration 追加を阻害しないか、番号/TYPE体系に拡張余地があるか。
- 保守性: 長期に更新・改訂しやすい構造か。重複記述による保守負債がないか。
- 可読性: 英文表現・文書構造の読みやすさ。
- 第三者視点: 前提知識のない読者が理解するうえで不足している説明・定義。

---

## 5. レビュー方針(共通)

- 対象は凍結版。レビューは「骨格(S0)+レビュー資産(RVW-001)」の設計品質確認であり、実装レビューではない。
- 指摘は必ず重大度を付す(第7章の定義)。
- 該当箇所は Document ID + 節番号(可能なら行の引用)で特定する。
- 修正提案は任意。無くても指摘として有効。

---

## 6. コメント記入テンプレート

各レビュアーは1指摘=1行で記入する。表形式(Markdown)またはCSV相当で返却。

| No | 文書ID | 観点 | 重大度 | 指摘内容 | 該当箇所 | 修正提案(任意) |
|---|---|---|---|---|---|---|
| 1 | (例)AUTO-SEAL-STD-005 | Conformance | Major | 状態遷移にSHALL/SHOULD/MAYが未適用 | 第3.1.1節 | 遷移規則をSHALLで規範化 |
| 2 | | | | | | |
| 3 | | | | | | |

記入規則:
- 文書ID: 第1章の10文書のいずれか。シリーズ横断の指摘は "SERIES" と記す。
- 観点: 第2章の観点名(担当外観点への言及も可、その旨明記)。
- 重大度: Critical / Major / Minor / Editorial のいずれか(第7章)。
- 該当箇所: 節番号必須、可能なら該当文の引用。
- 修正提案: 任意。方向性のみでも可。

---

## 7. 重大度定義(Critical / Major / Minor / Editorial)

| 重大度 | 定義 | Review Complete への影響 |
|---|---|---|
| Critical | 制度の整合性・独立性・安全性を損なう。放置すると設計が破綻する(例: 循環依存、Human Gate迂回、承認主体が人間でない) | Blocking。未解決ではReview Complete不可 |
| Major | 規格として重大な欠落・不整合だが設計全体は破綻しない(例: 責務境界の重複、必須メタデータ欠落、参照切れ) | Blocking。原則解消。保留する場合は理由を記録 |
| Minor | 局所的な不備・改善余地(例: 表現の曖昧さ、軽微な用語ゆれ) | 非Blocking。可能な範囲で反映 |
| Editorial | 誤字・体裁・言い回し等 | 非Blocking。まとめて反映 |

RVW-001 第5章の「未解決の重大指摘(Blocking)ゼロ」は Critical + Major を指す。

---

## 8. 返却と後続工程

1. 博士が ChatGPT / Gemini の実レビュー結果(第6章テンプレート形式)をくろこへ渡す。
2. Phase 4(くろこ): コメント統合・重複排除・重大度分類。
3. Phase 5(くろこ): 凍結版へ指摘を反映した Review Complete 版を作成。RVW-001 第5章の完了条件
   (両レビュー出揃い / 統合・修正完了 / Blocking ゼロ)を確認。
4. 成果物: Review Summary / 指摘一覧 / 修正一覧 / Review Complete版文書一式 / Human Gate提出パッケージ。
5. Human Gate は博士のみが実施。Approved/Effective化・実装・Decision Ledger記録はその後。

---

## 9. 本工程で実施しない事項(再掲)

Approved化 / Effective化 / 実装 / ソースコード変更 / Git Tag作成 / AUTO_SEAL実行 /
Decision Ledger記録 / Human Gate実施。いずれも本 S0.5 では行わない。

---

## 10. History

- 2026-07-13: 初版(v1.0)。KUROKO-DOC-S0-001 Sprint S0.5。方式A(博士がレビューを回す)に基づく
  レビュー入力パッケージ。対象10文書・7観点マッピング・ChatGPT/Gemini担当・記入テンプレート・
  重大度定義を収録。RVW-001第4章との観点割当差分を第2.1節に要調整として明示。

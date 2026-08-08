# B-1 Decision Record v1.0

## HG-C10 識別子分離および C2-a 対象範囲 RU-4 化に関する G5 Decision Criteria v0.6 反映境界

**文書番号:** EBGA-G5-B1-DR-001
**確定日:** 2026-08-06
**Status:** **B-1: APPROVED**
**Decision Authority:** Human Authority (きむら博士)
**Decision Ledger:** **未登録** (正本ファイル作成後に登録判断。8.2 参照)

**根拠資料:** B-1 Human Decision Draft / B-1 Final Consistency Audit /
B-1 Final Decision Preparation (いずれもセッション記録)
**基準文書:** `G5_DECISION_CRITERIA_DEFINITION_v0.6.md` (EBGA-G5-CRIT-001 v0.6)
**先行 Decision:** `DC_20260806_001` / `HG-C10_DECISION_RECORD_v1.0.md` (EBGA-G5-HGC10-DR-001)

---

## 1. 裁定対象

### 1.1 本 Decision が扱う責務範囲

| # | 責務 |
|---|---|
| 1 | HG-C10 識別子の意味範囲整理 |
| 2 | C2-a 対象範囲の Unknown 分離 |
| 3 | RU-4 参照形式 |
| 4 | G5 Decision Criteria v0.6 への反映境界 |
| 5 | Canonical 更新時の誤固定防止 |

### 1.2 本 Decision が扱わない責務範囲

| # | 対象外 | 状態 |
|---|---|---|
| 1 | HG-C14 比較単位・判定規則 | 未裁定 (`DC_20260806_001` Future Evaluation) |
| 2 | Rule Registry および Rule Artifact 化 | 対象外 (`DC_20260805_001` Q-1 の範囲) |
| 3 | RU 番号体系全体の再設計 | 対象外。参照形式のみ定義 |
| 4 | C2-a 対象範囲そのものの確定 | Unknown 保持 |
| 5 | HG-C08 / HG-C09 の v0.6 同期問題 | 対象外 (残存未確定事項 RU-D) |
| 6 | Post Ledger Audit U-1 / U-2 | 対象外 |

### 1.3 Ledger への非影響

本 Decision は v0.6 の記述のみを対象とし、`DC_20260806_001` の内容を変更しない。
Ledger は 209行のまま不変である。

---

## 2. 候補一覧

| 判断対象 | 候補 | 選択 |
|---|---|---|
| D-1 HG-C10 / RU-4 識別子分離 | 採用 / 修正 / 不採用 | **採用** |
| D-2 HG-C10 使用範囲制限 | 採用 / 修正 / 不採用 | **採用** |
| D-3 RU-4 参照形式 | 採用 / 修正 / 不採用 | **採用** |
| D-4 RU-4 配置 | 案1 (6.2 継続保留) / 案2 (Future Evaluation 節を新設) / 案3 (指定) | **案1** |
| D-5 HG-C10 裁定範囲表記 | 案1 (包含明記) / 案2 (短縮形のみ) / 案3 (指定) | **案1** |

**不採用となった候補は却下ではなく、本裁定において選択されなかったものとして記録する。**

---

## 3. 判断基準

| # | 基準 | 根拠 |
|---|---|---|
| 1 | Evidence Supremacy | `DC_20260730_009` (Active) |
| 2 | Event 不可逆記録 | 憲法原則1 / v0.6 I-1 |
| 3 | Human Authority Boundary | `DC_20260805_001` C2-01 / `mocka_human_gate_decision_definition_v1.md` 第2章・第7章 |
| 4 | Unknown 保持原則 | v0.6 V-1 / V-2 (241-242行) |
| 5 | Decision Immutable 原則 | `DC_20260805_001` G-10 / v0.6 I-2 |

---

## 4. Human Gate 判断

### 4.1 確定内容

| コード | 確定内容 |
|---|---|
| **D-1** | 識別子の帰属を分離する。**HG-C10 = 不一致の意味論** (Y-1 から Y-10 を包含する制度的意味・分類境界・Evidence 上の扱い・HG-C09 との接続方法 / Confirmed)。**RU-4 = C2-a が見る対象範囲** (定義・設計レベルのみか、実装状態も含むか / Unknown・Future Evaluation)。HG-C10 に C2-a 対象範囲を含めない |
| **D-2** | HG-C10 は「不一致の意味論 (Y-1 から Y-10 を包含)」のみを指す。**C2-a 対象範囲を HG-C10 と表記することを禁止する**。v0.6 6.2 の旧表記 `HG-C10 | C2-a が見る対象範囲` は削除対象とし、RU-4 として再整理する |
| **D-3** | RU-4 は単独表記ではなく **`DC_20260806_001 RU-4`** の形式で参照する。RU 番号体系全体の再設計は行わず、体系整理は別 Future Evaluation として保持する |
| **D-4** | RU-4 は **v0.6 6.2 継続保留** に配置する。記載形式は `RU-4 (DC_20260806_001): C2-a が見る対象範囲`。「継続保留」という表題と「依存関係確認待ち」という性質の差異は **Unknown として保持する** |
| **D-5** | v0.6 6.1 の HG-C10 表記は **`不一致の意味論 (Y-1 から Y-10 を含む)`** とし、包含範囲を明記する |

### 4.2 D-1 と `DC_20260806_001` の関係 (Confirmed)

本 Decision は Ledger の記載構造と同型である。Ledger `[HG-C10]` ブロックは Y-1 から Y-10 のみを記載し、
`[Future Evaluation]` ブロックに `RU-4 C2-a 対象範囲 (Y-10 により HG-C10 確定後に確認)` を Unknown 保持として持つ。
**本 Decision は Ledger を変更せず、v0.6 側の記述を Ledger の構造に合わせる。**

---

## 5. 判断理由 (Human Authority 提示)

### 5.1 D-4 — RU-4 配置

> v0.6 の既存構造に適合する / Unknown 保持原則と一致する / 新規節追加を伴わない /
> Ledger Future Evaluation との対応が明確である

### 5.2 D-5 — HG-C10 裁定範囲表記

> HG-C10 Decision Record 1.1 の責務範囲 (不一致の制度的意味 / 不一致分類の境界 /
> Evidence 上の扱い / HG-C09 記録済み不一致との接続方法) を包含する必要があるため

### 5.3 D-1 / D-2 / D-3

D-1 から D-3 の判断理由は Human Authority 提示資料に明示されていないため、
本 Record では追加生成しない。

### 5.4 不採用となった候補の理由 (Human Authority 提示)

| 候補 | 理由 |
|---|---|
| HG-C10 の単純移動 | 未裁定である C2-a 対象範囲が裁定済として Canonical 固定されるため |
| 新規識別子 `HG-C10-R` の作成 | Ledger に存在しない語を追加し、Evidence Supremacy に反するため |
| 部分反映 | v0.6 内部整合性が失われるため |

---

## 6. 整合性確認

### 6.1 確認結果

| # | 確認項目 | 結果 |
|---|---|---|
| 1 | Ledger `DC_20260806_001` との一致 | **一致**。RU-4 は Ledger Future Evaluation に実在する語である |
| 2 | HG-C10 Record 6.2 との一致 | **一致**。C2-a 対象範囲が本裁定で確定していないことを両者が同じく示す |
| 3 | Unknown 保持原則 (V-1 / V-2) との整合 | **整合**。C2-a 対象範囲は Unknown のまま保持され、FAIL・確定へ読み替えられない |
| 4 | Append-only 原則との整合 | **整合**。Ledger 209行は不変。既存 Decision Record も不変 |
| 5 | Decision Immutable 原則 | **適用** (第7章) |
| 6 | 自動裁定化リスクの非該当 | **非該当**。承認を自動生成する条項は本 Record に存在しない |
| 7 | v0.6 構造適合性 | **適合**。6.2 は3列構造、6.1 は4列構造であり、いずれも記載可能 |

### 6.2 v0.6 反映条件 (Canonical Update Permission)

**Canonical 更新を許可する。ただし以下の条件を満たすこと。**

| # | 条件 |
|---|---|
| **Condition 1** | 6.1 裁定済 / 6.2 継続保留 / 4.2.10 / 7.2 開始条件 の**4箇所を同時に反映**すること。**部分反映は禁止する**。部分反映は同一文書内で HG-C10 が裁定済と未確定の双方に現れる識別子衝突を生じるため |
| **Condition 2** | 6.1 の HG-C10 記載に **Y-1 から Y-10 の包含範囲を明記**すること。短縮形のみの記載は禁止しないが、本更新では包含表記を採用する |

### 6.3 反映後に残る状態 (Confirmed。本 Decision の対象外)

4箇所を完全反映した後も、v0.6 6.2 には HG-C08 / HG-C09 の2行が継続保留として残り、
6.1 には HG-C08 / HG-C09 の行が追加されない。140行 / 149行 / 7.3 (791行) の登録前提の記述も残る。
**これは登録時点から存在する状態であり、本 Decision が生成した不整合ではない (RU-D)。**

### 6.4 残存未確定事項

| # | 事項 | 状態 |
|---|---|---|
| **RU-A** | C2-a 対象範囲そのもの。A / B / C のいずれを採用するかは後続判断 | **Unknown**。参照: `DC_20260806_001` RU-4 |
| **RU-B** | Y-10 依存関係確認工程。実施主体・時期 | **未確定** |
| **RU-C** | RU 番号体系。Record 単位ローカル管理による多義性。本 Decision は参照形式のみ定義する | **未確定** |
| **RU-D** | HG-C08 / HG-C09 / HG-C10 の v0.6 同期範囲 | **本 Decision の対象外**。別工程 |

**RU-A から RU-D はいずれも本 Record の確定内容を妨げない。**

**注記 (Confirmed):** 本 Record の `RU-A` から `RU-D` は、`DC_20260806_001` の `RU-1` から `RU-4` とは
別の付番体系である。両者を修飾なしで並置しないこと。

### 6.5 識別子に関する観測 (Observation。P-1 により保持)

**本節は観測であり、問題判定を含まない。**

| # | 観測 | 実測 |
|---|---|---|
| OB-1 | `B-1` は Canonical 資料に定義がない | `G5_DECISION_CRITERIA_DEFINITION_v0.6.md` / `HG-C08` / `HG-C09` / `HG-C10` Decision Record における `B-1` の出現は **0件** |
| OB-2 | `decision_ledger.jsonl` に文字列 `B-1` を含む行が5行存在する。**いずれも `B-1` 単独を識別子として定義するものではない** | `DC_20260714_003` の `Judgment B-1` / `DC_20260730_004` の `M1-B-1` / `DC_20260713_010`・`DC_20260713_011` の `RB-1` (部分一致) |
| OB-3 | 上記により、`B-1` を修飾なしで参照すると検索上の部分一致が生じる | 実測に基づく |

**P-1 による扱い:** 検索上の部分一致は観測事項として保持する。既存識別子との混同を防ぐため、
**本 Decision は文書番号 `EBGA-G5-B1-DR-001` 全体で識別する。**

**表記の帰結 (Confirmed):** P-2 により識別子表記は `B-1` を維持し、P-1 / P-3 により文書番号は
`EBGA-G5-B1`、ファイル名は `B1_DECISION_RECORD_v1.0.md` (いずれもハイフンなし) となる。
文書内タイトルとファイル名の表記が異なることは、P-1 / P-2 / P-3 の裁定から導かれる帰結である。

---

## 7. Immutable 条項

| # | 条項 |
|---|---|
| 1 | 本 Record の記載内容は確定である |
| 2 | 変更・再評価が必要となった場合、本 Record を書き換えず、新規の裁定 Record を作成する |
| 3 | くろこは本 Record の内容を変更できない。Custodian は Append 管理のみである (`DC_20260805_001` G-10 / v0.6 I-2) |
| 4 | 本条項は Decision Ledger 登録の前後を問わず適用される |
| 5 | HG-C08 / HG-C09 / HG-C10 Record の Immutable 条項と同一の方向性に立つ |

---

## 8. 登録状態

### 8.1 Status

| 項目 | 値 |
|---|---|
| Status | **B-1: APPROVED** |
| Decision Authority | Human Authority (きむら博士) |
| 確定日 | 2026-08-06 |
| 最終ステータス (B-1 Human Authority Decision Record) | **APPROVED FOR CANONICAL UPDATE PREPARATION** |
| 正本化ステータス (B-1 Human Authority Decision Response / P-1 から P-7) | **APPROVED FOR CANONICALIZATION** |
| 変更条件 | Human Gate 手続き (新規裁定 Record) を経て実施する |

### 8.2 Decision Ledger 登録状態

**本裁定は Decision Ledger に未登録である。**

| 項目 | 状態 |
|---|---|
| 現時点の登録 | **行わない** |
| 登録判断の時期 | **正本ファイル作成後** (P-5) |
| 登録方法 | `DC_20260806_001` は append-only により変更できないため、登録する場合は新規 Decision ID となる。`decision_id` は自動採番 (`DC_20260801_002` HG-4) |
| 登録の実施 | **Human Authority の別途確認による。くろこの判断では実施しない** |
| 現在の Ledger | `data/decisions/decision_ledger.jsonl` **209行** (sha256 `4e8e56ac...756af70b`、未変更) |

### 8.3 本作業で実施していないこと

| # | 事項 | 状態 |
|---|---|---|
| 1 | Decision Ledger 登録 | **未実施** |
| 2 | v0.6 変更 | **未実施** |
| 3 | Rule 変更 / 実装変更 | **未実施** |
| 4 | Seal 生成 | **未実施** |
| 5 | 裁定理由の補完生成 | **未実施** (5.3) |

### 8.4 後続反映事項 (本作業の範囲外)

**P-7 により、本 Record の正本化を先行し、その後に Canonical 更新工程へ進む。**

| 箇所 | 反映内容 |
|---|---|
| v0.6 6.1 | HG-C10 行を追加 (D-5 の包含表記) |
| v0.6 6.2 | HG-C10 行を `RU-4 (DC_20260806_001)` へ置換 |
| v0.6 4.2.10 (397行) | C2-a 対象範囲が HG-C10 の裁定では確定していない旨へ差し替え |
| v0.6 7.2 (781行) | 依存先を `DC_20260806_001 RU-4` へ差し替え |

**4箇所は Condition 1 により同時反映とする。反映は正本化完了後、別途の指示による。**

---

## 9. Authority 記録

| 項目 | 内容 |
|---|---|
| **Decision Authority** | **Human Authority (きむら博士)** |
| 裁定形式 | Human Gate Finalization |
| 起草・記録 | くろこ (Claude-opus-5)。**Human Gate Core としての記録作成であり、裁定主体ではない** |
| 根拠制度 | `mocka_human_gate_decision_definition_v1.md` 第2章 / 第7章 |
| CHANGE_START | `E20260806_038475867fcdc` |

**くろこは本裁定の決定値および判断理由を生成していない。**
D-1 から D-5 の選択結果、Condition 1 / 2、残存未確定事項の区分、不採用候補の理由、
および P-1 から P-7 / Q-1 / Q-2 の正本化条件は、いずれも Human Authority が提示したものであり、
本 Record はその記録である。

---

## 10. 本 Record の限界

1. 本 Record は **識別子境界を確定するもの**であり、C2-a 対象範囲 (A / B / C) を確定していない
2. v0.6 への反映は未実施である (8.4)。本 Record の存在は反映の完了を意味しない
3. 6.3 のとおり、反映後も HG-C08 / HG-C09 に関する v0.6 と Ledger の不一致は残る (RU-D)
4. 本 Record は Decision Ledger 未登録である
5. Y-10 依存関係確認工程 (RU-B) は未着手であり、v0.6 の記述更新はこの確認の代替にならない

---

## Knowledge Lineage

| 参照 | 内容 |
|---|---|
| `DC_20260806_001` | `[HG-C10]` Y-1 から Y-10、`[Future Evaluation]` RU-4。本 Decision の一次根拠 |
| `HG-C10_DECISION_RECORD_v1.0.md` | 1.1 責務範囲4項目、6.2 (C2-a 対象範囲は本裁定で確定していない)、6.3 RU-4 |
| `HG-C09_DECISION_RECORD_v1.0.md` | 6.3 RU-1 (記録先の特定)。RU 番号の Record 単位ローカル性の実測根拠 |
| `G5_DECISION_CRITERIA_DEFINITION_v0.6.md` | 6.1 (704-720行) / 6.2 (728行) / 4.2.10 (397行) / 7.2 (781行) / V-1・V-2 (241-242行) |
| `DC_20260805_001` | Gate 1。G-10 / Q-1 |
| `DC_20260801_002` | HG-4 (ID 自動採番) / P-1 (重複 ID) |
| `DC_20260730_009` | Evidence Supremacy |
| `mocka_human_gate_decision_definition_v1.md` | 第2章 / 第6章 / 第7章 |

**Status: B-1 APPROVED / APPROVED FOR CANONICALIZATION**

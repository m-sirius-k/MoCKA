# Decision Identity Architecture Options Matrix v0.1

```
Document ID   : DECISION_IDENTITY_ARCHITECTURE_OPTIONS_v0.1
Date          : 2026-08-01
作成          : くろこ (Claude Code, Claude-opus-5)
Authority     : Human Gate 確定 (2026-08-01) により本ディレクトリへ配置
Decision      : DC_20260801_001
Related       : INC-DECISION-ID-COLLISION-20260730 (仮ID / 正式登録しない)
                DECISION_LEDGER_SCHEMA_v1.md
                DC_20260730_001 / _002 / _003 (COLLISION 対象)
基準データ    : decision_ledger.jsonl 204行 / 197 distinct ID / 730,796 bytes
                (2026-08-01 07:57 JST 実測)
配置          : 既提出内容からのファイル化。内容追加・判断変更なし
```

本文書は選択肢の整理であり、採用判断・推奨を含まない。

重要な注記: 本文書の A/B/C/D は、先行文書 Option Evaluation Matrix の A/B/C/D と
対応が異なる。混同を避けるため対応関係を明示する。

| 本文書 | 内容 | 先行文書での対応 |
|--------|------|-----------------|
| A 現行維持 + 参照解決改善 | 識別モデルは不変、読み取り側で解決を改善 | 先行 B (読み取り時に全件返却) に相当 |
| B decision_id + revision 方式 | 版番号フィールドを追加 | 新規 (先行文書に対応なし) |
| C decision_id + canonical/alias 方式 | 正準 ID と別名を分離 | 先行 C に相当 |
| D 行ID + series ID 分離方式 | 行の一意性と系列を別フィールドへ | 新規 (先行文書に対応なし) |

先行文書の A (現状維持・何もしない) と D (append-only 解消レコード追加) は、
本文書の比較対象に含まれない。

---

## 1. 基準状態 (現在の decision_id 単独モデル)

### 1-1. モデル

```
decision_id (文字列)
   |
   | 解決規則: ファイル内で最後に出現した行を採用 (last-wins)
   v
Decision Record (14フィールド / 1行)
```

[事実] decision_id 以外に Decision を識別するフィールドは schema に存在しない。
中間層 (行 ID・版番号・canonical 参照・alias) はいずれも未定義である。

### 1-2. 単一文字列が担う4役割

| 役割 | 保証 | 実測 |
|------|------|------|
| 一意性 | なし | 204行 / 197 distinct / 重複 7 ID (一意率 96.4%)。書込時の重複検査は未実装 |
| 系列性 | なし | 専用フィールドなし。supersedes 15/204、superseded_by 0/204、status=Superseded 1/204 |
| 状態更新 | 一意性と識別不能 | STATE_UPDATE (4 ID) と COLLISION (3 ID) が同一の物理形式 |
| 参照対象 | なし (last-wins 解決) | related_documents 内 52件 / 本文中 366件。参照される distinct ID 122 のうち 6 が重複 ID |

### 1-3. 基準状態のコード上の位置 (変更影響の起点)

| # | 位置 | 役割 |
|---|------|------|
| S-1 | mocka_mcp_server.py:364-380 `_read_decisions()` | 全行読み取り (重複除去なし)。呼び出し元 3箇所 (385 / 1033 / 1040) |
| S-2 | mocka_mcp_server.py:1031-1036 `mocka_decision_get` | `matches[-1]` を返す (単一オブジェクト) |
| S-3 | mocka_mcp_server.py:1038-1046 `mocka_decision_list` | `latest[did] = r` (後勝ち)、decision_id 降順 |
| S-4 | mocka_mcp_server.py:382-394 `_next_decision_id()` | `DC_{JST日付}_{当日最大+1:03d}` |
| S-5 | mocka_mcp_server.py:396-400 `_append_decision()` | 無条件 append |
| S-6 | mocka_mcp_server.py:976-985 書込検証 | 必須項目・alternatives 形状・status enum のみ。ID 検査なし |
| S-7 | mocka_mcp_server.py:472-474 / 1215-1217 | ツール定義が2箇所に重複記載 |
| S-8 | governance/write_path/runtime/adapter.py:27-44 `_read_decision` | 同一 last-wins 規則。未配線 |
| S-9 | governance/seal_governance_gate.py:126,147-149 | `DC_{execution_id}` 形式・18フィールドで直接 append。app.py:2211-2214 から配線済み・実績 0件 |

### 1-4. 同型構造の存在 (波及範囲の予告)

[事実] Integrity Ledger (data/integrity/integrity_classification.jsonl) は
48行 / 45 distinct / 重複 3 ID で、`mocka_integrity_get`
(mocka_mcp_server.py:1092-1097) が同一の `matches[-1]` 規則を用いている。

[未評価] IC 側の重複3件 (IC_20260705_016 / IC_20260707_006 / IC_20260708_001) が
STATE_UPDATE か COLLISION かは本調査では判定していない。

注: 後続の DESIGN_BOUNDARY_REPORT v0.1 において、この3件はすべて STATE_UPDATE で
COLLISION は 0件であることが実測確認された。

---

## 2. Options Matrix

### 2-1. 方式概要

| 方式 | 識別モデル | 変更の所在 |
|------|-----------|-----------|
| A 現行維持 + 参照解決改善 | decision_id 単独のまま。解決規則のみ変更 (全件返却または曖昧性の明示) | 読み取り側のみ |
| B decision_id + revision | (decision_id, revision) の複合キーで行を識別。同一 ID の追記は revision 増分 | schema + 書込 + 読み取り |
| C decision_id + canonical/alias | 正準 ID を別に持ち、decision_id は別名として解決される | schema + 書込 + 読み取り + 解決層 |
| D 行ID + series ID 分離 | 行ごとに一意 ID を付与し、系列は別フィールドで表現 | schema + 書込 + 読み取り + 参照体系 |

### 2-2. 比較表

| 比較項目 | A | B | C | D |
|---------|---|---|---|---|
| append-only 整合性 | 適合。既存行に一切触れない | 要検討。既存204行に revision が無く、欠落時の解釈規則が必要 | 要検討。既存204行に canonical 情報が無い | 要検討。既存204行に行 ID・series ID が無い |
| STATE_UPDATE 維持可否 | 維持される。ただし系列と衝突の判別は依然不可 | 維持され明示化される。ただし増分か新 ID かの判断規則が別途必要 | 維持される。canonical が同一なら系列 | 維持される。行 ID により衝突概念自体が消滅 |
| 既存204行への移行影響 | なし | あり。revision 欠落の既定値解釈が必要 | あり。既存7重複 ID の canonical 割り当て判断が必要 | あり。204行すべてに行 ID を要する |
| MCP API 影響 | `mocka_decision_get` の戻り値が単一 -> 複数 (破壊的)。変更箇所 S-2/S-3/S-8、定義 S-7 | revision 指定引数の追加。戻り値形式は維持可能 | 解決先が canonical 経由に変わる。戻り値形式は維持可能 | 引数意味論の再定義。影響は最大 |
| schema 変更範囲 | 不要 (§4 違反は未解消のまま) | §3 にフィールド追加 (revision)。§4 改訂 | §3 にフィールド追加 (canonical_id 等)。§4 改訂 | §3 の再設計。§4・§7・§8 の全面見直し |
| Human Gate 必要項目 | API 戻り値形式変更の承認 / §4 違反を残すことの承認 | schema 改訂 / revision 既定値解釈 / 使い分け規則 | schema 改訂 / 既存7重複 ID の canonical 割り当ての個別承認 / 移行方式 | schema v2 化 / 行 ID 採番方式 / 遡及方針 / 参照体系変更 |

### 2-3. 補助比較 (判断材料)

| 項目 | A | B | C | D |
|------|---|---|---|---|
| COLLISION 3件の到達性回復 | する | する | する | する |
| 誤解決 7参照の解消 | する | する | する | する |
| 今後の COLLISION 発生防止 | しない | 部分的 | する | する |
| 系列と衝突の機械的判別 | 不可 | 可 | 可 | 可 |
| Integrity Ledger への波及 | なし | 同型適用の判断が必要 | 同型適用の判断が必要 | 同型適用の判断が必要 |
| 実装変更の起点数 (S-1 から S-9) | 3-4 | 6-7 | 5-6 + 解決層新設 | 8-9 (全域) |

### 2-4. 各方式に固有の論点 [考察]

A: decision_id は引き続き4役割を単独で担う。到達性は回復するが、返された複数件の
   どれが目的の記録かの判断は呼び出し側 (MCP クライアント = AI エージェント) に
   移譲される。呼び出し側は静的列挙による影響確認ができない。

B: revision は同一決定の版を表すが、COLLISION は別決定が同一 ID を取った状態であり、
   revision 増分として記録されると衝突が正当な版に見えてしまう可能性がある。
   増分か新 ID かの判断規則が定義されない限り、衝突の防止機構にはならない。

C: 既存7重複 ID への canonical 割り当てには STATE_UPDATE / COLLISION の判定が前提と
   なる。判定材料は実測済みだが、7件という標本に対する観測であり判別規則としては
   未検証。割り当ては人による個別確認になる。

D: 行 ID の導入により同一 ID の複数行という状態そのものが消滅し、衝突概念が構造的に
   成立しなくなる。一方で既存の参照 (構造化52件・本文366件) はすべて decision_id
   文字列を前提としており、参照体系の再定義が伴う。既存204行への series ID 導出は
   COLLISION 3件について誤った系列を生成する。

### 2-5. 全方式に共通する未決事項 [事実]

| # | 事項 | 現状 |
|---|------|------|
| CM-1 | 書込時の ID 検査を追加するか、fail-closed か警告か | 検査未実装 (S-6) |
| CM-2 | decision_id の明示指定を許容するか | 規定なし。運用規約のみで対処可能 |
| CM-3 | 採番責任境界 | 未定義 |
| CM-4 | 第2書込経路 (S-9) の位置づけ | 未定義 |
| CM-5 | §7 の superseded_by 更新規定と append-only の不整合 | 規定と実装が不整合 (0/204) |
| CM-6 | ツール定義の2箇所重複 (S-7) の解消 | いずれの方式でも両方の更新が必要 |
| CM-7 | Integrity Ledger への同型適用の要否 | 未評価 |

---

## 3. 本文書の位置づけ

[事実] 本文書は選択肢の整理であり、以下を含まない。

- 採用判断
- 推奨案の提示
- 方式間の優劣評価
- 実装計画

---

## 4. 実施時の変更件数

変更 0件 / commit 0件 / push 0件 / Event Ledger 記録 0件。

Decision Ledger 204行 / 730,796 bytes、Integrity Ledger 48行、
schema sha256 6810ef0fecb1ec88、mocka_mcp_server.py sha256 5bdae5e020308941、
GOV-PROC-CETR-001 sha256 2e597aadb443b7c6 のいずれも不変。

# PHASE5_1_A HGD-D1 STEP 1 REGISTRY COMPLETENESS REPORT

- Date: 2026-10-02
- Executed by: KUROKO PC (Claude-sonnet-4-6)
- Mode: READ-ONLY AUDIT
- Source: mocka_mcp_server.py (C:/Users/sirok/MoCKA/mocka_mcp_server.py)
- Reference: DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION, DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE

---

## 1. 全 TOOL 一覧 (TOOLS array: /mcp エンドポイント公開ツール)

Classification basis: governance_pipeline.py `READ_ONLY_TOOLS` set (line 33-50)
- READ: READ_ONLY_TOOLS に含まれるもの
- WRITE/GOVERNED: READ_ONLY_TOOLS に含まれないもの (GL7 Dry Run 対象)

| # | Tool Name | READ/WRITE | Source Lines (TOOLS array) | Notes |
|---|-----------|-----------|---------------------------|-------|
| 1 | mocka_get_overview | READ | 531 | READ_ONLY_TOOLS |
| 2 | mocka_get_essence | READ | 532 | READ_ONLY_TOOLS |
| 3 | mocka_get_todo | READ | 533 | READ_ONLY_TOOLS |
| 4 | mocka_add_todo | WRITE | 534 | NOT in READ_ONLY_TOOLS |
| 5 | mocka_update_todo | WRITE | 535 | NOT in READ_ONLY_TOOLS |
| 6 | mocka_list_events | READ | 536 | READ_ONLY_TOOLS |
| 7 | mocka_read_event | READ | 537 | READ_ONLY_TOOLS |
| 8 | mocka_search | READ | 538 | READ_ONLY_TOOLS |
| 9 | mocka_write_event | WRITE | 539 | NOT in READ_ONLY_TOOLS |
| 10 | mocka_seal | WRITE/GOVERNED | 540 | NOT in READ_ONLY_TOOLS (auto_log writes to DB) |
| 11 | mocka_get_incidents | READ | 541 | READ_ONLY_TOOLS |
| 12 | mocka_get_guidelines | READ | 542 | READ_ONLY_TOOLS |
| 13 | mocka_get_command_center | READ | 543 | READ_ONLY_TOOLS |
| 14 | mocka_check_utf8 | READ | 544 | READ_ONLY_TOOLS |
| 15 | mocka_registry_get | READ | 545 | READ_ONLY_TOOLS |
| 16 | mocka_registry_add | WRITE | 546 | NOT in READ_ONLY_TOOLS |
| 17 | mocka_registry_current_state | READ | 547 | READ_ONLY_TOOLS |
| 18 | mocka_decision_write | WRITE | 548 | NOT in READ_ONLY_TOOLS |
| 19 | mocka_decision_get | READ | 549 | READ_ONLY_TOOLS |
| 20 | mocka_decision_list | READ | 550 | READ_ONLY_TOOLS |
| 21 | mocka_integrity_write | WRITE | 551 | NOT in READ_ONLY_TOOLS |
| 22 | mocka_integrity_get | READ | 552 | READ_ONLY_TOOLS |
| 23 | mocka_integrity_list | READ | 553 | READ_ONLY_TOOLS |

**TOOLS array total: 23**
**READ tools: 16**
**WRITE/GOVERNED tools: 7**

---

## 2. WRITE tool 一覧 (7 tools)

| Tool Name | HGD-B1 "missing" 記載 | 備考 |
|-----------|----------------------|------|
| mocka_add_todo | YES | HGD-B1 missing list に明示 |
| mocka_update_todo | YES | HGD-B1 missing list に明示 |
| mocka_write_event | NO | HGD-B1 missing list に不在 (11 hardcoded に含まれていた想定?) |
| mocka_seal | YES | HGD-B1 missing list に明示 |
| mocka_registry_add | YES | HGD-B1 missing list に明示 |
| mocka_decision_write | NO | HGD-B1 missing list に不在 (11 hardcoded に含まれていた想定?) |
| mocka_integrity_write | YES | HGD-B1 missing list に明示 |

---

## 3. HGD-B1 17-tool 見積もり との照合

### HGD-B1 コンテキスト (DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE より)

- "GL11 TOOL_REGISTRY has 11 hardcoded tools; 6 critical write tools are missing"
- 6 missing: mocka_add_todo, mocka_update_todo, mocka_seal, mocka_integrity_write, mocka_registry_add, **Bash**
- "17-tool list is an estimate pending Registry completeness 照合"
- "Registry completeness is implementation-time responsibility of KUROKO on Windows machine; 17-tool estimate may be revised after 照合"

### 照合結果

| 項目 | HGD-B1 見積もり | STEP 1 実測値 | 一致/不一致 |
|------|----------------|--------------|------------|
| 総 TOOL 数 | 17 (estimate) | 23 | **不一致 (delta +6)** |
| WRITE tool 数 | 6 (missing list) + α (hardcoded) | 7 | **要確認** |
| READ tool 数 | 11 (hardcoded 想定) | 16 | **不一致 (delta +5)** |
| "Bash" 存在 | missing list に記載 | TOOLS array に存在しない | **UNKNOWN** |

---

## 4. 一致 / 不一致 明示

### MATCH (一致)

- WRITE tool の中核 5 tool は HGD-B1 missing list に明示されており TOOLS array に実在:
  - mocka_add_todo, mocka_update_todo, mocka_seal, mocka_registry_add, mocka_integrity_write

### DISCREPANCY (不一致)

**D-1: 総 TOOL 数の乖離**
- 期待値 (HGD-B1): 17 tools
- 実測値: 23 tools
- 差: +6 tools
- 注記: DC_20261002_HGD_B1 は「照合後に改訂可」と明記。乖離自体は設計上予期された範囲。

**D-2: "Bash" が TOOLS array に存在しない**
- HGD-B1 missing list に "Bash" が含まれているが、TOOLS array の 23 tool に Bash は存在しない。
- Bash は Claude Code の組み込みコマンドであり、mocka MCP tool ではない。
- tool_registry.json に "Bash" エントリを追加すると GL11 で意図しない動作を引き起こす可能性がある。
- Human Gate 確認が必要。

**D-3: mocka_write_event が missing list に不在**
- mocka_write_event は WRITE/GOVERNED tool (governance_pipeline.py で READ_ONLY_TOOLS に含まれない)
- HGD-B1 missing list に明示されていない
- 11 hardcoded ベースに含まれている想定の場合、tool_registry.json に含める必要がある
- 明示確認が必要。

**D-4: mocka_decision_write が missing list に不在**
- mocka_decision_write は WRITE/GOVERNED tool
- HGD-B1 missing list に明示されていない
- D-3 同様、11 hardcoded ベースに含まれている想定の場合、tool_registry.json に含める必要がある
- 明示確認が必要。

---

## 5. WRITE tool coverage 確認

### Option B 前提 (HGD-A1 Option B: READ bypass — registry は WRITE tool のみ対象)

WRITE/GOVERNED tool: 7 tools

tool_registry.json に全 7 tool が含まれる場合: coverage = 100%

現時点での coverage 評価: **UNKNOWN (未確定)**

理由:
- HGD-B1 missing list は 5 tool のみ明示 (D-3, D-4 の 2 tool が不在)
- "Bash" は実在しない tool (D-2)
- 11 hardcoded ベースの内容が不明 (structural/tool_registry_enforcement.py が現時点で存在しない)

**coverage = 100% を確保するためには、tool_registry.json に以下 7 tool すべての登録が必要:**

1. mocka_add_todo
2. mocka_update_todo
3. mocka_write_event
4. mocka_seal
5. mocka_registry_add
6. mocka_decision_write
7. mocka_integrity_write

---

## 6. UNKNOWN 項目

| ID | 項目 | 内容 | 対応 |
|----|------|------|------|
| U-1 | "Bash" の扱い | HGD-B1 missing list に記載あり、TOOLS array に存在なし | Human Gate 判断必須 |
| U-2 | mocka_write_event の registry 明示性 | WRITE tool だが missing list 不在 | 確認必要 |
| U-3 | mocka_decision_write の registry 明示性 | WRITE tool だが missing list 不在 | 確認必要 |
| U-4 | 11 hardcoded ベースの内容 | tool_registry_enforcement.py が現時点で存在しない。何の 11 tool を指すか不明 | 確認必要 |

---

## 7. EXTRA 発見事項 (コード変更なし、報告のみ)

### E-1: mocka_get_command_center の二重定義

execute_tool 内に mocka_get_command_center が 2 箇所実装されている:
- 1st: line 894 (3 エンドポイント取得: loop_status, risk, heinrich)
- 2nd: line 943 (2 エンドポイントのみ: loop_status, risk)

elif チェーンの性質上、line 943 は デッドコード。STEP 1 では変更しない。

### E-2: TOOLS 非公開の execute_tool ハンドラ

TOOLS array に登録されていないが execute_tool で処理される tool が 3 件存在:
- mocka_search_incidents (line 956): READ — /agent/ エンドポイントのみアクセス可能
- mocka_get_phl (line 987): READ — /agent/ エンドポイントのみアクセス可能
- mocka_get_spp (line 1008): READ — /agent/ エンドポイントのみアクセス可能

これらは /mcp エンドポイントに露出していないため、GL11 registry 対象外。

---

## 8. STEP 1 RESULT

```
STEP 1 RESULT: DISCREPANCY DETECTED — HUMAN GATE REPORT REQUIRED

総 TOOL 数:   23 (HGD-B1 見積もり 17 から +6 乖離)
WRITE tool:   7  (明示的に registry 必要)
READ tool:    16
UNKNOWN:      4 項目 (U-1〜U-4、特に U-1 "Bash" の扱いは Human Gate 判断必須)

WRITE coverage: HGD-B1 missing list で明示された 5/7 WRITE tool は確認済み
               残り 2 tool (mocka_write_event, mocka_decision_write) は missing list 不在
               "Bash" は TOOLS array に存在しない (HGD-B1 見積もり誤り)

DC_20261002_HGD_B1 は「17-tool estimate may be revised after 照合」と明記。
D-1 (総数乖離) は設計上予期された範囲。

ただし D-2 ("Bash" 非実在) および D-3/D-4 (coverage 不確定) は
Human Gate による判断が必要。

STEP 2 進行条件:
  - Human Gate が D-2 の "Bash" 扱いを明示
  - Human Gate が D-3/D-4 (mocka_write_event / mocka_decision_write) の
    registry 登録を明示承認
  - 最終 WRITE tool リスト (7 tool) を Human Gate が確認
  条件充足後、STEP 2 (tool_registry.json 作成 および .gitignore 監査) へ進む。
```

---

*STEP 1 完了 — コード変更なし / コミットなし / Runtime activation なし*
*次アクション: Human Gate (きむら博士) による D-2/D-3/D-4 確認待ち*

---

## 9. HUMAN GATE DECISION RECORD (2026-10-02)

**Status: STEP 1 CLOSED**

Human Gate (きむら博士) による正式判断:

| Discrepancy | 判断 |
|-------------|------|
| D-2: "Bash" | TOOLS array に存在しないため tool_registry.json Registry 対象外とする |
| D-3: mocka_write_event | WRITE/GOVERNED として Registry 対象に含める |
| D-4: mocka_decision_write | WRITE/GOVERNED として Registry 対象に含める |

### 確定 Registry Completeness (Source of Truth)

```
TOTAL TOOLS       = 23  (HGD-B1 見積もり 17 を破棄、KUROKO PC 実測値採用)
WRITE/GOVERNED    =  7
READ              = 16
WRITE COVERAGE    = 7/7  (100%)
```

### 最終 WRITE/GOVERNED tool 一覧 (tool_registry.json 登録対象)

1. mocka_add_todo
2. mocka_update_todo
3. mocka_write_event
4. mocka_seal
5. mocka_registry_add
6. mocka_decision_write
7. mocka_integrity_write

### 制約 (継続)

- tool_registry.json 作成はまだ禁止 (STEP 2 完了後)
- コード変更禁止
- .gitignore 変更禁止
- Runtime activation 禁止
- commit 禁止
- push 禁止

**次ステップ: STEP 2 (.gitignore / TODO_390 audit) へ進む**

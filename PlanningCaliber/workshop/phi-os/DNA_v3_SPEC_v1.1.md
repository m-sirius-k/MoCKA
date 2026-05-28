# DNA_v3 / PHI OS — Claude Code 完全実装仕様書
**バージョン:** 1.1
**作成日:** 2026-05-28
**起草者:** きむら博士 / 執行官Claude
**参照イベント:** E20260528_021, E20260528_022, E20260528_024, E20260528_032
**保存先:** `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\DNA_v3_SPEC_v1.1.md`

## 変更履歴

### v1.1 (2026-05-28)
- セクション8.1: DBパスを `C:\Users\sirok\MoCKA\data\mocka_events.db` に訂正（疑念005解決）
- セクション5: commit-engineの実装方式をbetter-sqlite3ではなくPython子プロセス方式に変更（疑念006解決）
- セクション5: CommitトリガーをRelay引き継ぎボタンに確定（疑念002解決）
- セクション4.3: restore_packet最大文字数を3000文字に設定（疑念004解決）
- セクション4.2: IMMUTABLE層はHuman Gate必須・Claude Code書き込み禁止を明記（疑念003解決）
- セクション10: 疑念001（検索精度）を改良001として将来版に延期

---

## 0. この仕様書を読むClaudeへ

あなたはこれからMoCKAの「文明再起動エンジン」を実装する。

**絶対に守ること：**
- 実装前に`mocka_write_event(CHANGE_START)`を実行する
- 実装後に`mocka_write_event(CHANGE_DONE)`を実行する
- ファイル生成は`create_file`ツールのみ使用（bash heredoc禁止）
- PowerShellでPythonコードを書かない
- 全ファイルはUTF-8 BOMなしで保存する
- 判断に迷ったら実装せず、疑念レポートを出力してきむら博士に確認する

---

## 1. 思想と目的

### 1.1 解くべき問題

```
現状：
  セッション開始 → TODOとessence3軸のみ注入（薄い）
  セッション終了 → 何も保存しない
  結果           → 毎回リセット・同じ失敗・同じ説明の繰り返し

根本原因：
  Causality層が存在しない
  「なぜその判断をしたか」が一切保存されていない
  禁則・価値観が希釈される（コンテキスト汚染）
```

### 1.2 解決の思想

```
「記憶するAI」ではなく
「何度死んでも同じ文明として再起動できる外部OS」
ステートレスなLLMの上で動く Stateful Civilization Layer

前提：
  - セッション死は必ず起きる
  - AI交換は必ず起きる
  - 断絶は前提である
  → 「どう再構築するか」だけを設計する
```

### 1.3 MoCKAとの連続性

```
MoCKAが解いた問題：断絶 → 集約 → 還流
DNA_v3が解く問題：同じ構造の「配線の未完部分」

PHI OSは新しいシステムではない。
MoCKAの既存資産（events.db / essence / TODO / Orchestra / Relay）
への「Commit/Restore配線2本」を追加するだけである。
```

---

## 2. 資産役割分担（確定・変更不可）

| 資産 | 役割 | 変更禁止事項 |
|------|------|------------|
| Orchestra | 全文アーカイブ（長期エピソード記憶） | 全文削除禁止 |
| Relay | セッション間バトン（State転送） | 引き継ぎ形式変更禁止 |
| Memory | 構造化永続ストア（Fact/Intent） | スキーマ変更時は要確認 |
| **events.db** | **因果記憶（Causality層）** | テーブル削除禁止 |
| **essence** | **人格核（IMMUTABLE固定）** | IMMUTABLE層上書き禁止 |
| TODO.json | 行動状態（State層） | status以外の変更は要確認 |
| **PHI OS** | **文明再起動エンジン（配線のみ）** | 保存先にしない |

**重要：** PHI OSは保存先ではなく「検索→圧縮→再注入」のオーケストレータである。新規DBを作らない。

---

## 3. 4層保存モデル

```
Layer       内容                              既存資産での対応
─────────────────────────────────────────────────────────────
Fact        ファイルパス / API / 設定 / 定義   events.db
State       進捗 / 未完了 / 失敗位置           TODO.json (C:\Users\sirok\MOCKA_TODO.json)
Causality   なぜその判断か / エラー経緯        judgement_reason（新設）★
Intent      目標 / 優先順位 / 次回フック        essence + TODO
```

★ Causality層が最重要欠落。これがないと「同じ失敗」が永続する。

### 3.1 Causality層の意味

```
「PowerShellでPythonを書くな」は禁止事項ではない。
本当の意味：
  どういう状況で誤ったか
  なぜ誤ったか
  何が壊れたか
  何を学んだか
  次回どう防ぐか
  = 「経験の因果化」

judgement_reasonは単なるログテーブルではない。
「AI人格の因果記憶層」である。
```

### 3.2 IMMUTABLE層の意味

```
kernel protected memory に相当。
長会話になるほどLLMは：
  - 優先順位漂流
  - 安全性上書き
  - 文脈希釈
  - 過剰迎合
が起きる。

IMMUTABLE層はこれを防ぐ岩盤。
上書き不可・削除不可・セッション開始時に必ず先頭注入。
```

### 3.3 tension（違和感）の意味

```
tensionはバグではなく「未来の研究シード」である。
普通のTODOシステムは未完了しか保存しない。
MoCKAは「未言語化違和感」を保存する。

格納する：
  tension_severity: 1〜5（5が最重要）
  tension_at: 発生時刻
  tags: tension / anomaly / unresolved

Restore時にseverity≥3を上位表示する。
```

---

## 4. データ設計（確定）

### 4.1 DDL: judgement_reason テーブル

```sql
-- 実際のDB: C:\Users\sirok\MoCKA\data\mocka_events.db（v1.0の記述を訂正）
-- 実行前: mocka_write_event(CHANGE_START) 必須
CREATE TABLE IF NOT EXISTS judgement_reason (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id          TEXT    NOT NULL,
  session_date      TEXT    NOT NULL,
  decision          TEXT    NOT NULL
                    CHECK(decision IN ('採用','却下','保留')),
  rejected_reason   TEXT,
  reason            TEXT    NOT NULL,
  error_solved      TEXT,
  tension           TEXT,
  tension_severity  INTEGER DEFAULT 0
                    CHECK(tension_severity BETWEEN 0 AND 5),
  tension_at        TEXT,
  source_map        TEXT,
  tags              TEXT,
  created_at        TEXT    DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_jr_tags
  ON judgement_reason(tags);
CREATE INDEX IF NOT EXISTS idx_jr_tension
  ON judgement_reason(tension_severity DESC);
CREATE INDEX IF NOT EXISTS idx_jr_session
  ON judgement_reason(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_jr_event
  ON judgement_reason(event_id);
```

**制約事項：**
- `decision='却下'`のとき`rejected_reason`は必須（アプリ側バリデーション）
- `tension_severity≥3`のエントリはRestore時に必ず上位表示
- `tags='immutable'`のエントリはIMMUTABLE層へ昇格候補

### 4.2 Decay/Promotion 昇格ルール

```
incident（tags='incident'）
  ↓ 同パターン3回検出時
repeated_incident（tags='repeated_incident'）
  ↓ きむら博士がHuman Gate承認
law（lever_essence.json OPERATION層に追記）
  ↓ 思想レベルに昇華・きむら博士が最終承認
immutable（lever_essence.json PHILOSOPHY IMMUTABLE層に追記）

確認：昇格はClaude Codeが自動実行しない。
     必ずきむら博士の承認を経ること。
     Claude CodeはIMMUTABLE層への書き込み禁止（v1.1で明記）。
```

### 4.3 JSONスキーマ: restore_packet.json

```json
{
  "$schema": "DNA_v3_restore_packet_v1.0",
  "version": "3.0",
  "generated_at": "ISO8601",
  "session_context": "今日の作業テーマキーワード（30文字以内）",
  "immutable": {
    "philosophy": ["できないのはやらないからだ", ...],
    "forbidden": ["PowerShell環境でPythonコードを直接実行させない", ...],
    "values": ["違和感は次の発明のシード", ...]
  },
  "restore_5points": {
    "1_personality": "essence PHILOSOPHY軸 圧縮版（200字以内）",
    "2_current_goal": [{"todo_id": "...", "title": "...", "priority": "..."}],
    "3_active_work": "直近イベント要約（300字以内）",
    "4_tensions": [{"text": "...", "severity": 4, "tension_at": "...", "tags": "...", "source_map": "..."}],
    "5_recent_decisions": [{"decision": "...", "reason": "...", "rejected_reason": null, "error_solved": "...", "source_map": "..."}]
  }
}
```

**最大文字数: 3000文字（v1.1確定）**
トリム優先順位: active_work → decisions → tensions → IMMUTABLEは削除しない

---

## 5. ファイル構成と実装順序

### 5.1 ディレクトリ構成

```
C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\
│
├── DNA_v3_SPEC_v1.md              ← v1.0仕様書
├── DNA_v3_SPEC_v1.1.md            ← この仕様書（v1.1）
│
├── core\
│   ├── db_helper.py               ← SQLiteヘルパー（Python, Node.js代替）
│   ├── commit-engine.js           ← Step3: セッション終了5点書き込み
│   └── restore-engine.js          ← Step4: Restore Packet生成
│
├── db\
│   ├── add_judgement_reason.py    ← Step2: judgement_reasonテーブル追加
│   └── migration_v1.sql           ← Step2: DDL
│
├── immutable\
│   └── add_immutable_layer.py     ← Step1: essence IMMUTABLE層追加・検証
│
├── schemas\
│   └── restore_packet_schema.json ← Step4: スキーマ定義
│
└── tests\
    ├── test_db_schema.py          ← Step2後: DBテスト（5テスト）
    ├── test_commit.py             ← Step3後: Commitテスト（5テスト）
    └── test_restore.py            ← Step4後: Restoreテスト（6テスト）
```

### 5.2 実装状況（v1.1時点）

```
☑ Step1: lever_essence.json にIMMUTABLE層追加（E20260528_027）
☑ Step2: mocka_events.db に judgement_reason テーブル追加（E20260528_027）
☑ Step3: commit-engine.js 実装完了（E20260528_028）
          CommitトリガーはRelay引き継ぎボタン（v1.1確定）
☑ Step4: restore-engine.js 実装完了（E20260528_029）
          max_chars=3000・trimToMaxChars実装（v1.1確定）
☑ Step5: content.js DNA_v3注入対応（E20260528_030）
          v3優先・v2フォールバック
```

### 5.3 Commitトリガー（v1.1確定）

**採用案:** Relay引き継ぎボタンを押した時（疑念002解決）

実装先: `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\Relay_Project\extension\content.js`

`handleBadgeClick()` 内の `showBadgeFlash('safe')` 後に
`fetch('http://localhost:5000/commit_session', ...)` を呼び出す。

サーバーエンドポイント: `app.py` の `/commit_session`（POST）

### 5.4 SQLite接続方式（v1.1確定）

**採用方式:** Python子プロセス方式（疑念006解決）

理由: better-sqlite3 は Node.js v25.2.1 + Windows環境でビルド不可
     （node-gyp + VC++ Build Tools 未インストール）

`core/db_helper.py` を `child_process.spawnSync` で呼び出す。
コマンド: `write_judgement`, `read_restore_data`, `query`, `commit`

---

## 6. デバッグ報告書フォーマット

（v1.0と同一 — 省略）

---

## 7. 疑念フォーマット

（v1.0と同一 — 省略）

### 7.1 既知疑念 解決状況（v1.1時点）

| 疑念 | タイトル | 解決状況 |
|------|---------|---------|
| 疑念001 | restore-engine検索精度 | 改良001として将来版(v3.1)に延期 |
| 疑念002 | Commitトリガー | ✅ Relay引き継ぎボタン採用 |
| 疑念003 | IMMUTABLE管理権限 | ✅ Human Gate必須・Claude Code書き込み禁止を明記 |
| 疑念004 | restore_packet最大サイズ | ✅ 3000文字・trimToMaxChars実装 |
| 疑念005 | DBパス差異 | ✅ data/mocka_events.db に訂正 |
| 疑念006 | better-sqlite3ビルド不可 | ✅ Python子プロセス方式で代替 |

---

## 8. テスト仕様

### 8.1 Step2テスト: judgement_reason テーブル確認

**DB正規パス（v1.1訂正）:**

```python
DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
```

（v1.0の `C:\Users\sirok\MoCKA\mocka_events.db` は0バイト空ファイルのため使用不可）

テスト全5件 → [test_db_schema.py](tests/test_db_schema.py)

### 8.2〜8.3

（v1.0と同一。DB_PATHのみ上記に訂正）

---

## 9. 実装時の注意事項（特記）

### 9.1 絶対禁止事項

```
✗ bash_tool でのecho/heredoc/catによるファイル生成
✗ PowerShellの Set-Content / Out-File / -replace でのファイル編集
✗ mocka_events.db の既存テーブルへの破壊的変更
✗ lever_essence.json の IMMUTABLE層の無断上書き（v1.1追加）
✗ Decay/Promotionの無断実行（Human Gate必須）
✗ 判断に迷った時の独断実装（→疑念レポート提出）
✗ 1000行超のファイルを一括生成する（分割実装すること）
```

### 9.2〜9.4

（v1.0と同一）

### 9.5 commit-engine.js 実装の注意（v1.1更新）

```
- SQLite接続: better-sqlite3ではなくdb_helper.py(Python)をchild_process.spawnSync で呼ぶ
- コマンド: write_judgement / commit（relay向けショートカット）
- 5点全て書き込みが成功した場合のみevents.dbにcommit記録
- 部分失敗時はrollbackしてエラーレポートを出力
```

### 9.6 restore-engine.js 実装の注意（v1.1更新）

```
- Restore Packetの最大文字数: 3000文字（trimToMaxChars()で強制）
- トリム優先: active_work → decisions → tensions → IMMUTABLE削除禁止
- session_contextは呼び出し元から渡す
- immutable層は常に先頭に配置
- エラー時はRestoreをスキップし、v2（旧DNA）にフォールバック
```

---

## 10. 改良提案（将来版への提言）

```
改良001（旧疑念001）: restore-engineの検索精度向上
  内容: session_contextキーワードでのFTS検索 + morphology_engineとの連携
  効果: 「今日に関係ある断片」の精度向上
  難度: 中
  対象版: DNA_v3.1

改良002: Restore Packetの自動品質スコアリング
  内容: 生成したRestore Packetに「文明整合性スコア」を付与
  難度: 中

改良003: morphology_engineとの連携
  内容: DANGERパターン照合で「今日踏みそうな地雷」を優先表示
  難度: 中

改良004: AIエージェント別Restore差分
  内容: Claude/Gemini/GPTで異なるRestore Packet生成
  難度: 高

改良005: Restore Packetのバージョン管理
  内容: restore_packet.jsonをgit管理し文明状態の変化を追跡
  難度: 低
```

---

## 11. 完了定義（v1.1時点）

```
☑ Step1: lever_essence.json にIMMUTABLE層が存在する
☑ Step2: mocka_events.db に judgement_reason テーブルが存在する
☑ Step2: 全4インデックスが存在する
☑ Step3: commit-engine.js が5点書き込みに成功する
☑ Step4: restore_packet.json が正しいスキーマで生成される
☑ Step4: IMMUTABLE層が先頭グループに配置されている
☑ Step5: claude.ai の新規chatでDNA_v3パケットが注入される
☑ 全テストがPASSしている（16テスト）
☑ 全StepのPHL記録（E20260528_026〜033）が存在する
☑ デバッグ報告書 Step1〜5 が提出されている
☑ 疑念001〜006 が解決またはきむら博士に確認済み
□ きむら博士による実動作目視確認（claude.ai新規chatでDNA_v3注入確認）
```

---

## 12. 参照イベント・TODO一覧

```
E20260528_021  DNA_v3設計思想確立・PHI OS再定義合議
E20260528_022  TODO_191〜194登録完了
E20260528_024  仕様書作成開始
E20260528_026  CHANGE_START: DNA_v3 PHI OS実装開始
E20260528_027  Step1完了(IMMUTABLE) / Step2開始・完了(judgement_reason)
E20260528_028  Step3開始・完了(commit-engine)
E20260528_029  Step4開始・完了(restore-engine)
E20260528_030  Step5開始・完了(content.js)
E20260528_031  CHANGE_DONE: DNA_v3全実装完了
E20260528_032  残作業指示書発行（きむら博士）
E20260528_033  CHANGE_START: DNA_v3残作業全件実行

TODO_191  DNA_v3設計書作成 → 完了
TODO_192  PHI OS restore-engine.js実装 → 完了
TODO_193  PHI OS commit-engine.js実装 → 完了
TODO_194  events.db Causality層追加 → 完了
```

---

*この仕様書はきむら博士の思想とMoCKAの30年の経験知を基盤として作成された。*
*「できないのはやらないからだ」— MoCKA精神*

# TODO データソース統合設計案 v0.1(Human Gate提出資料)

作成日: 2026-07-07
対応TODO: TODO_420(TODOデータソースSSOT監査)Phase D
根拠: DC_20260707_005(Phase A-C監査事実)

本資料はコードを1行も変更せず、統合設計と影響範囲を確定することを目的とする。実装(ファイル名変更・import変更・パス変更・Gateway/Firestore/export_for_cloudflare修正)はHuman Gate承認後に別途実施する。

---

## Task 1: 全参照元の完全棚卸し

| ファイル | READ | WRITE | 用途 | 正本変更時の影響 |
|---|---|---|---|---|
| `data/MOCKA_TODO_ACTIVE.json` | `mocka_mcp_server.py`(MCPツール群)、`app.py`(todo_risk/get_latest_dna/gemini_briefing) | `mocka_mcp_server.py` | 現行正本。本日のTODO_416-420を含む全作業の実体 | (正本のため影響なし) |
| `data/MOCKA_TODO_ARCHIVE.json` | 確認できず(プログラムからの参照なし) | 確認できず | 2026-06-30作成の静的スナップショット(469KB) | 現状無影響 |
| `data/MOCKA_TODO_REFERENCE_LOCKED.json` | 確認できず | 確認できず | 2026-06-30作成の静的スナップショット(10KB、ARCHIVEと同時刻) | 現状無影響 |
| `data/MOCKA_TODO.json` | `gateway/context_builder.py`(Gateway API)、`interface/handshake.py`、`interface/mentor_engine.py`、`PlanningCaliber/workshop/phi-os/ise/*.py`(ISE状態管理)、`deploy/mocka_mcp_server_vps.py`(VPS版MCPサーバー) | `PlanningCaliber/workshop/mocka-cloudflare/export_for_cloudflare.py`(コピーのみ) | 外部公開系(Gateway等)が参照する唯一のソース。TODO_390で凍結 | 最大。参照側5系統すべてに関わる |
| `C:/Users/sirok/MOCKA_TODO.json` | `mocka_todo_sync.py`、`mocka_firestore_sync.py`、`ping_generator.py`、`add_sync.py`、`export_for_cloudflare.py`、`mocka_v3_eval/*.py`、`tools/fix_inc001_007.py` | `mocka_todo_sync.py`(pull_from_firestore)、`mocka_firestore_sync.py` | Firestore双方向同期の実体。`export_for_cloudflare.py`のコピー元 | Firestore連携全体に影響 |
| Firestore `intent_queue` | `mocka_todo_sync.py`(pull) | `mocka_todo_sync.py`(push) | クラウド側ミラー | Firestore依存アプリに影響(範囲未確認) |

備考: `MOCKA_TODO_ARCHIVE.json`・`MOCKA_TODO_REFERENCE_LOCKED.json`は本調査でプログラムからの参照が一件も見つからなかった。2026-06-30という同一時刻に作成されており、ACTIVE/ARCHIVE分離アーキテクチャ移行時の一回限りの成果物である可能性が高いが、これも状況証拠であり確定事実ではない。

---

## Task 2: 正本候補の制度的定義

| ファイル | 制度的役割(現状) | 制度的役割(統合後の案) |
|---|---|---|
| `data/MOCKA_TODO_ACTIVE.json`(+ARCHIVE) | 正本(唯一の書込先) | 変更なし。引き続き唯一の書込先 |
| `data/MOCKA_TODO.json` | 旧系列のミラー(独立した実体) | 正本からの**エクスポート生成物(読取専用キャッシュ)**へ役割変更 |
| `C:/Users/sirok/MOCKA_TODO.json` | Firestore同期の実体 | 正本発エクスポートを起点とする**片方向ミラー**へ役割変更を検討(要追加設計) |
| Firestore `intent_queue` | 双方向同期先 | 正本→Firestoreの**片方向配信先**へ役割変更を検討 |
| `MOCKA_TODO_ARCHIVE.json`/`REFERENCE_LOCKED.json` | 静的スナップショット | 統合設計の対象外として現状維持 |

---

## Task 3: 移行経路設計(概念図・コード変更なし)

### 現状

```
data/MOCKA_TODO_ACTIVE.json(正本)
        |
        v (接続なし ―――――――――――― 断絶)

C:/Users/sirok/MOCKA_TODO.json(旧系列源)
   <=> Firestore intent_queue
        |
        v export_for_cloudflare.py(コピー+_snapshot_at付与)
data/MOCKA_TODO.json(旧系列ミラー、TODO_390で凍結)
        |
        v
   Gateway / handshake.py / mentor_engine.py / ISE / VPS-MCP
        |
        v (Cloudflare配信経路は未確認)
```

### 統合後(案)

```
data/MOCKA_TODO_ACTIVE.json(正本、変更なし)
        |
        v Export(新設、正本→旧系列読者向けの一方向エクスポート)
data/MOCKA_TODO.json(キャッシュ化。Export専用の生成物へ役割変更)
        |
        v (参照先は無変更。ファイルパス互換のため既存コード改修不要)
   Gateway / handshake.py / mentor_engine.py / ISE / VPS-MCP
        |
        v
   Cloudflare配信

(別経路)
Firestore <= data/MOCKA_TODO_ACTIVE.json 由来のExportを起点とする片方向ミラーへ切替(案、要追加設計)
C:/Users/sirok/MOCKA_TODO.json は片方向ミラー受信専用へ縮退(案)
```

ポイント: 参照側(Gateway等5系統)のファイルパスは変更しないため、統合後もコード改修は不要と想定される(Export処理の出力先を既存の`data/MOCKA_TODO.json`パスに合わせるだけで済む)。

---

## Task 4: Human Gate提出資料

### 現状構成
Task 1・Task 3「現状」の通り。正本(ACTIVE.json)と旧系列(TODO.json系+Firestore)が完全に無接続。

### 問題点
1. 正本と旧系列が無接続(TODO_419のOrchestra乖離と同型のガバナンス問題)
2. Gateway経由で外部AI(GPT・Copilot等)が取得するTODO情報がTODO_390で凍結。本日のTODO_416-420を含む現行作業が一切反映されない
3. Firestore双方向同期が旧系列のみを対象とし、正本の変更がクラウド側へ伝播しない
4. VPS版MCPサーバー(`deploy/mocka_mcp_server_vps.py`)も同じ旧系列を参照しており、外部公開インターフェースが軒並み古いデータを返している可能性がある

### 統合案
正本(ACTIVE.json)からの一方向Export処理を新設し、`data/MOCKA_TODO.json`を「正本のキャッシュ/エクスポート生成物」として再定義する。既存の読者(Gateway等)はファイルパスを変更しないため、参照側のコード改修は不要と想定。Firestore双方向同期は、正本発のExportを起点とする片方向ミラーへの切替を検討する(追加設計が必要)。

### メリット
- 参照側(Gateway/handshake/mentor_engine/ISE/VPS-MCP)のコード変更が不要(パス互換維持)
- 外部AIが常に最新TODO状態を参照可能になる
- 正本が唯一つになり、以後の乖離再発を防止できる

### リスク
- Export処理自体に不具合があれば旧系列が現状よりさらに壊れる可能性がある
- Firestore双方向同期の片方向化は、Firestore側から手動更新する運用が存在する場合に影響が出る可能性がある(未確認、要調査)
- `export_for_cloudflare.py`の実行タイミング(定期/手動、要確認)次第で、正本更新から旧系列反映までのタイムラグが残る

### ロールバック方法
- Export処理を無効化するだけで現状(旧系列は最後にコピーされた時点のまま凍結)に戻る。旧系列自体を削除しないため低リスク
- 正本(`MOCKA_TODO_ACTIVE.json`)自体には手を加えないため、正本側のロールバックは不要

---

## 実装禁止事項(Phase D時点)

以下はHuman Gate承認後に実施する。本資料作成時点では一切行っていない。

- ファイル名変更
- import変更
- パス変更
- Gateway修正
- Firestore修正
- `export_for_cloudflare.py`修正

## 未確認事項(次回調査・承認判断時に確認推奨)

- Cloudflare配信の実際の経路(`data/MOCKA_TODO.json`から具体的にどう配信されるか)
- Firestore側から手動更新している運用の有無
- `export_for_cloudflare.py`の起動トリガー(定期実行か手動実行か)

# runtime/incident_* レガシー調査ノート

**起草**: Claude（制度書記官）
**日付**: 2026-07-02
**関連PHL**: E20260702_331336771c627, E20260702_673923179808f, INCIDENT_LEGACY調査(error_capture_engine.py未起動確定)

## 1. 結論: 未起動確定

`runtime/error_capture_engine.py`（`runtime/incident_engine.py`の`record_event()`を呼ぶ唯一の常時稼働候補）は、
以下3点の否定的証拠により**未起動が確定**した。

1. **プロセス確認**: 稼働中の全9 python プロセスのコマンドラインを特定したが、`error_capture_engine.py`を
   起動しているものは存在しない。
2. **起動シーケンス確認**: `MoCKA-START.bat`（全85行）に`error_capture_engine.py`を起動する行は存在しない。
   PHASE 0のstale-processクリーンアップ対象リストにも含まれていない。
3. **データ痕跡確認**: `runtime/incident_ledger.json`（`record_event()`の唯一の書き込み先）自体が
   ファイルとして存在しない。一度も実行されていないことの直接証拠。

なお `incident_classifier.py` / `incident_knowledge_base_engine.py` は `incident_pipeline.py` →
`self_healing_orchestrator.py`（別の`while True`常駐ループ）経由の定期実行が設計されているが、
上流の`incident_ledger.json`が存在しないため実際には空振りしている可能性が高い。

## 2. 現存データの扱い: アーカイブ扱い

- `runtime/incident_classification.json`（`{"Exception": {"count": 71}}`）
- `runtime/incident_knowledge_base.json`（incident/repair/verification結合ログ、最古レコード2026-03-15）

上記2ファイルは過去に稼働していた形跡（実データ）であり、**アーカイブ（過去の実行履歴）として扱う**。
現在進行形で更新されているデータではない。

## 3. 破棄しない理由

- `incident_knowledge_base.json`には実際の障害対応記録（repair_id, action等）が含まれており、
  過去のトラブルシューティング事例として参照価値がある。
- `incident_engine.py`の重複集約ロジック（`incident_hash = sha256(title+content+source)`一致で
  `repeat_count`加算）は、INL（Incident Navigation Layer）が現時点で持たない機能であり、
  将来のINL拡張時に参考・流用できる可能性がある（TODO登録済み: duplicate_of フィールド採用検討）。
- `runtime/incident_*` 4ファイル（`incident_engine.py`, `incident_classifier.py`,
  `incident_knowledge_base_engine.py`, 関連JSON）は本ノート作成にあたり**一切変更していない**。
  削除・改変は行わず、現状のまま保持する。

## 4. INLとの関係整理（暫定方針）

- `runtime/incident_*`系: レガシー・アーカイブ扱い。新規incidentの起点としては使用しない。
- `data/incident.json` + `class_registry.json` + `incident_links.json`（INL v0.1、後日v0.2で
  ラッパー層として再設計予定）: 今後の正式なIncident記録の入口として運用する方向。
- 両者を自動接続する実装は行わない。統合方針の最終決定は判断者（きむら博士）に委ねる。

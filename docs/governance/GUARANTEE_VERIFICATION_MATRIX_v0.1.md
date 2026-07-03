# Guarantee to Verification Matrix v0.1

位置づけ: 博士指示（2026-07-03、Task-K）に基づき新規作成。`GUARANTEE_MATRIX_AUDIT_v0.1.md`の続編。同ファイルが整理した10種の保証（G1〜G10）それぞれについて、「実際にどう検証するか」を対応付ける。

保証は宣言されているだけでは意味を持たない。検証方法が存在し、かつ実際に運用されて初めて保証は機能する。本ファイルは各Guaranteeについて(a)検証方法の提案、(b)現状その検証が実際に行われているかを整理する。実装は一切含まない。新規のコード調査は行わず、本日までの調査結果の再構成のみを行う。

---

## 第1部: 現状把握

### 1.1 前提

`GUARANTEE_MATRIX_AUDIT_v0.1.md`で整理したG1〜G10の保証は、いずれも「主張されている」ことが確認されたに過ぎず、「実際に検証する手段が存在し稼働しているか」は同ファイルの範囲外だった。本ファイルはその欠落を埋める。

### 1.2 検証の3分類

各Guaranteeの検証状況を以下3分類のいずれかで評価する。

- **稼働中**: 検証を行う具体的な仕組み（スクリプト・ツール・プロセス）が存在し、実際に動いていることが確認されている
- **設計のみ**: 検証方法は文書上で提案・設計されているが、実装または定期実行が確認されていない
- **不明**: 検証方法自体が今回の調査範囲で確認できなかった

---

## 第2部: 提案 — Guarantee to Verification 対応表

| Guarantee | 検証方法（提案） | 現状 | 根拠 |
|---|---|---|---|
| G1 存在保証 | Existence Query Test: 既知の成果物IDに対して台帳（KN-004等）への問い合わせが正しく応答するかを確認するテスト | 稼働中（部分的） | `mocka_registry_get`等のMCPツールは稼働している（KN-004 Registry）。ただしKN-004とMODULE_CATALOG_v1のスコープ重複が未検証のため、「単一の存在保証」としての検証はまだ設計されていない |
| G2 不変性・改ざん検知保証 | Hash Chain Verify: 各Ledger候補についてチェーンの整合性を検証するスクリプトの実行 | 稼働中（ledger.jsonのみ）／不明（他候補） | `scripts\ledger\ledger_verify.py`はledger.json向けに存在する。mocka_events.dbはaudit_trigger.pyによるリアルタイム検知はあるが定期的なフルチェーン検証の有無は不明。decision_ledger.jsonl（PHI-OS）はverify_chain()という関数はあるが、定期実行されているかは不明。KN_SERIES_LEDGERは実体未確認のため検証方法も不明 |
| G3 網羅性保証 | Coverage Audit: 一定期間の実際のファイル変更（git diff等）と対応するmocka_write_event記録数を突合し、記録漏れがないかを確認するテスト | 設計のみ（突合テスト自体は未確認） | event_gateによる書き込み経路の一元化（TODO_322）とPostToolUse自動記録フックは書き込み時点の保証であり、事後に「漏れがゼロであること」を突合するテストがあるかどうかは本日の調査範囲では確認できていない |
| G4 実行前安全性保証 | Adversarial Dry Run Test（カナリアテスト）: 意図的に危険な操作をDry Runで試み、実際にブロックされるかを確認する | 設計のみ | Decision PolicyのOVERRIDES enforcementにはカナリアテスト設計（`test_override_evidence_gap_is_rejected_by_event_gate`、CI定期実行）があるが、「liveness_guarantee」は「設計として明記済み・未実装」（v0.2課題）とDECISION_POLICY_v0.1.mdに明記されている。GL7自体のFORBIDDEN_EXECUTIONSに対する同種のカナリアテストの有無は不明 |
| G5 人間最終決定保証 | Approval Log Audit: 承認イベント（誰が・いつ・何を承認したか）を実行ログと突合し、承認なしに実行されたケースがゼロであることを確認するテスト | 不明 | Human Gateを経由した承認がイベントとして記録される仕組み自体はあると考えられるが、「承認ログと実行ログの突合による網羅性検証」という専用プロセスの存在は本日の調査で確認できていない。加えて、GL7 Dry Run後のHuman Gate接続自体が未実装（`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`参照、Task-Mで詳述）のため、検証すべき経路自体が一部欠落している |
| G6 暴走・停滞検知保証 | Health Index: `LOOP_HEALTH_INDEX_DESIGN_v0.1.md`で提案済みのLoop Health Indexを実際に運用し、既知の暴走・停滞パターンを注入して検知できるかを確認するテスト | 設計のみ（かつ既存基盤に疑義） | Loop Health Index自体が未実装の設計案。さらにDRIFT_STANDARDが依拠するはずのcalc_drift_v3等の関数がinterface\router.pyに実在しない疑いがあり（構文エラー・BOM混入も検出済み）、既存の検証手段そのものが機能していない可能性がある |
| G7 品質・妥当性保証 | 既存の閾値判定（復元率80%、CaliberScore 0.75等）およびWriter/CheckerのHard Gate（Test・再現性検証・構造チェック） | 稼働中（Caliber側）／設計のみ（Writer/Checker側） | `CALIBER_DESIGN_PRINCIPLES.md`・`PLANNING_CALIBER_LAW_v1.md`の閾値判定は実際に稼働しているとの記録がある。Writer/Checkerは`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`として設計されたのみで未実装 |
| G8 単一正本保証 | Cross-Reference Audit: KN-004とMODULE_CATALOG_v1のような候補ペアについて、同一対象への矛盾する記録がないかを突合するテスト | 不明（検証自体が未着手） | このような突合は本日の一連の監査で初めて疑いが指摘された段階であり、専用の検証テストは存在しない |
| G9 権限分離保証 | 静的検査（Decision Policyの責務境界=判定/実行/記録/承認の分離がコード上で越権していないかの確認）、および直接書き込み検知 | 稼働中（一部） | `phi_os\audit_trigger.py`のSQLiteトリガー（`trg_detect_direct_insert`等）はevent_gateを経由しない直接書き込みを検知する仕組みとして稼働している。Decision Policy自体の越権（例えば裁定と同時に実行や保存を行っていないか）を確認する静的検査の有無は不明 |
| G10 文脈・経験継承保証 | Resume Test: セッション再開後にworking_memory.py・Infieldの内容が正しく引き継がれるかを確認するテスト | 不明 | working_memory.pyは単一セッション内キャッシュとして設計されており、セッションをまたいだ復元（Resume）を目的とした設計かどうかは不明。mocka-infieldはORPHAN状態（`CONCEPT_AUDIT_v0.1.md`参照）のため、この検証は現状成立しない |

---

## 第3部: 未確定事項

- 「稼働中」と分類した項目も、本日の調査で存在が確認された仕組みが実際に定期的に実行されているか（例: ledger_verify.pyが定期実行されているか、それとも手動実行のみか）までは確認していない。「存在する」と「稼働し続けている」は別の確認事項であり、後者はTask-L（成熟度）で扱う観点に近い
- G5・G6の検証手段が特に手薄であることが判明したが、これはFIRST_PRINCIPLES_AUDIT_v0.1.mdのP3（人間最終決定）・G6（暴走・停滞検知）に直結する保証であるため、優先的な手当てが必要と考えられる。ただし本ファイルは検証方法の対応付けまでが範囲であり、実際の実装提案はしない
- 検証方法そのものの妥当性（例えばApproval Log Auditが本当にG5を検証するのに十分な方法か）は、本監査では吟味していない。今後の設計段階で再検証が必要

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Kに基づき新規作成。

# Option C Audit Resumption Plan v0.1

Status: 再開計画のみ（Task 1〜4の内容そのものの先取り実施は行わない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md、OPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.md、
REPOSITORY_DIVERGENCE_REPORT_v0.1.md

---

## 1. 再開するTask

当初指示のTask 1〜4を、名称・成果物ファイル名を変更せずそのまま再開対象とする。

```
Task 1: Jarvis Integration Traceability Audit
        成果物: JARVIS_INTEGRATION_TRACEABILITY_AUDIT_v0.1.md
Task 2: Deferred Boundary Verification（対象: DC_20260729_001）
        成果物: JARVIS_DEFERRED_BOUNDARY_VERIFICATION_v0.1.md
Task 3: Runtime Layer Mapping
        成果物: PHI_RUNTIME_LAYER_MAPPING_v0.1.md
Task 4: Option C位置付けの再定義
        成果物: OPTION_C_RUNTIME_POSITION_ANALYSIS_v0.1.md
```

## 2. 実施順序（提案。確定ではない）

1. **Task 2（Deferred Boundary Verification）を最優先とする。**
   理由: DC_20260729_001のDeferred裁定はJARVIS構想の制度的境界そのものであり、Option C設計がこの境界を
   越えていないかの確認は、他のTaskの前提となる（境界を越えている場合、Task 1・3・4の実施自体の
   位置づけが変わる）。
2. Task 1（Traceability Audit）を次に実施する。
   理由: Task 2で境界維持が確認された後、Sequence Controller・Module Adapter・Evidence Pipelineとの
   接続関係を確認する方が、手戻りが少ない。
3. Task 3（Runtime Layer Mapping）を次に実施する。
   理由: Task 1で得た接続関係の情報を、層構造として整理し直す形になるため。
4. Task 4（Option C位置付けの再定義）を最後に実施する。
   理由: Task 1〜3の結果（既存設計を壊していないことの確認、境界維持の確認、Runtime層構造の整理）が
   揃って初めて、（PHI-OS Runtime Infrastructureとして位置づけ直せるか）の分析に意味のある根拠が
   揃う。

この順序は提案であり、きむら博士の判断で変更してよい。

## 3. 完了条件

以下がすべて満たされた時点で、各Taskを再開してよいものとする。

- OPTION_C_REQUIRED_EVIDENCE_MANIFEST_v0.1.mdに列挙した収集対象文書のうち、当該Taskの（監査対象）欄に
  含まれるものが、本セッションから読み取り可能な状態になっていること（収集経路は問わない。ファイル添付、
  本チェックアウトへのcommit/push、本セッションへの直接貼り付け等、いずれでもよい）。
- 収集された文書が、Event Ledger上のCHANGE_DONE記録（event_id・作成日時）と対応関係を確認できること
  （別文書の取り違え防止のため）。

## 4. Human Gate条件

- 各Task成果物（JARVIS_INTEGRATION_TRACEABILITY_AUDIT_v0.1.md等）は、作成後にきむら博士のレビューを
  経ること。
- DC_20260730_010で既に（Option C採用確定）がHuman Gate裁定済みであるため、Task 1〜4の着手そのものに
  ついて追加のHuman Gate承認は不要と考えるが、Task 2の結果（Deferred境界維持の可否）がもし（境界を
  越えている）という結果になった場合は、その時点で追加のHuman Gate裁定を要する。

## 5. 実施しないこと

以下は、Task A〜Dの作成中も、Task 1〜4の再開後も、一貫して禁止する。

- Ledger要約（short_summary/why_purpose/decision本文の圧縮表現）から、文書本文を推測して補完すること。
- 存在しないファイルの内容を、命名規則や一般的なテンプレートから想定して記述すること。
- Deferred条件（DC_20260729_001の4つの保留理由）が解消したかどうかを、原文を確認せずに推測で評価すること。

## 6. 現時点でのブロッカー

- 収集経路が未確定（本文書の範囲外、REPOSITORY_DIVERGENCE_REPORT_v0.1.md 3節参照）。
- Cloud checkout側のGitHub push権限が未回復（別件として既に報告済み。Task 1〜4の再開そのものには
  必須ではないが、成果物をGitHubへ反映するには必要）。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task A〜D切替指示に基づき作成。 |

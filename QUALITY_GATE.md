# Quality Gate — Governance Layer v1.1 Baseline

Baseline ([GOVERNANCE_BASELINE.md](GOVERNANCE_BASELINE.md)) 以降、
`structural/` のGovernance Layer (GL1-7) に対する全変更が満たすべき
最低条件。いずれかがFAILした場合、Baselineへのマージは不可とする。

## 最低条件

1. **Governance Test PASS**
   `structural/gl_integration_test.py` が 14/14 PASS であること。
2. **Dogfood PASS**
   `structural/dogfood_run.py` で `bypassed == 0`, `fatal_errors == 0`,
   `write_aborted == 0`, `checklist_fail_count == 0` であること。
3. **Audit PASS**
   `structural/governance_audit_check.py` が全項目PASSであること
   （Fail Closed / GL6 enforcement / GL3 word-boundary / GL7 Default Deny
   / GL_AUDIT_REPORT.md v1.1総合判定PASS の各不変条件を維持）。
4. **Fail Closed維持**
   governance未初期化または `before_tool()` 例外時、`READ_ONLY_TOOLS`
   以外のtoolは `GL_FAIL_CLOSED` で実行停止すること。
5. **Default Deny維持**
   `READ_ONLY_TOOLS`（10種）に含まれない全tool（未知のtool含む）は
   GL7 Dry Run対象であること。
6. **Pipeline経由率100%**
   `/mcp` および `/agent/<tool_name>` の全経路が `execute_tool()` →
   `before_tool()` を経由すること。

## 実行方法

3項目（Integration Test / Dogfood / Audit）をまとめて検証するには:

```
python structural/governance_regression.py
```

`Overall PASS` が出力されない場合、いずれかの最低条件に違反している。
詳細は出力されたログおよび `structural/GOVERNANCE_REGRESSION_SUMMARY.md`
を参照すること。

## 将来のCI組み込み方針

`governance_regression.py` はCLI実行のみで完結し、外部サービスへの
依存を持たない。将来GitHub Actions等へ組み込む場合は、以下のように
ワークフローのステップから直接呼び出すことができる（CI構築自体は
本フェーズの対象外）。

```yaml
- name: Governance Regression
  run: python structural/governance_regression.py
```

終了コードが非ゼロの場合、CIジョブをFAILさせること。

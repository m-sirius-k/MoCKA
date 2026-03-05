# Security Policy

## EN

MoCKA treats security as a verifiability problem.
If you discover a vulnerability or a risky misconfiguration, please report it responsibly.

### Reporting

- Do not open public issues for exploitable vulnerabilities.
- Provide a minimal reproduction and impact assessment.
- If the issue concerns secret leakage, rotate secrets immediately.

### Scope

Examples in scope:

- Secret exposure (keys, tokens, credentials)
- Integrity bypass (tampering that avoids detection)
- Verification path compromise
- Supply-chain risks that affect reproducibility

## JP

MoCKA はセキュリティを「検証可能性」の問題として扱います。
脆弱性または危険な設定を見つけた場合は、責任ある方法で報告してください。

### 報告方法

- 悪用可能な脆弱性を公開 Issue に投稿しない
- 最小再現と影響評価を添付
- 秘密情報漏洩なら先にローテーションを実施

### 対象範囲

例：

- 秘密情報の露出（鍵、トークン、認証情報）
- 完全性検証の迂回（改ざんが検知されない）
- 検証経路の侵害
- 再現性に影響するサプライチェーンリスク

# Contributing

## EN

Thanks for your interest in MoCKA.

MoCKA is built around verifiability and reproducibility.
Contributions are welcome if they preserve:

- Determinism (no hidden state, no nondeterministic side effects)
- Auditability (clear artifacts, traceable changes)
- Governance boundaries (infield/outfield separation where applicable)
- Public-safe publishing (no secrets, no private keys, no sensitive paths)

### Workflow

1. Create a branch from main.
2. Keep commits small and explain intent.
3. Prefer documentation and tests for behavioral changes.
4. Use signed commits when possible.

### What to avoid

- Adding secrets or credentials
- Changing canonical formats without clear migration
- Introducing network calls in verification paths unless explicitly isolated

## JP

MoCKA への関心に感謝します。

MoCKA は「検証可能性」と「再現性」を中心に設計されています。
貢献は歓迎しますが、次を必ず維持してください。

- 決定性（隠れ状態や非決定的副作用を持ち込まない）
- 監査可能性（成果物が明確で変更が追跡できる）
- 統治境界（infield/outfield 分離が前提）
- 公開安全（秘密情報、鍵、機密パスを含めない）

### 進め方

1. main からブランチを作成
2. 小さく分かるコミット
3. 挙動変更にはドキュメントとテストを優先
4. 可能なら署名コミットを使用

### 避けること

- 秘密情報の追加
- 正本フォーマット変更を無移行で実施
- 検証経路に外部ネットワーク依存を混入

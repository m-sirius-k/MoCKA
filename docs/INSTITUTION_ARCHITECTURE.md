# MoCKA 制度アーキテクチャ v1.0

確定日: 2026-06-12

## 3層構造

### Layer 1: Constitution（憲法層）

- 変更不可の根本原則
- "AIを信じるな、システムで縛れ"
- Event ledger is append-only
- All decisions preserve 5W1H
- Human Gate for critical operations
- ファイル: docs/CONSTITUTION.md

### Layer 2: Institution（制度層）

- 変更可能だが合議・承認必須
- Institution Contract（TODO_280/281）
- AI Role Registry（TODO_277）
- Capability Registry（TODO_272）
- Commission Registry（TODO_286）
- ファイル: data/institution/

### Layer 3: Operation（運用層）

- 日常的に変化するデータ・設定
- events.db, guidelines.json, essence
- TODO, Connector設定
- ファイル: data/, interface/

## Institution Runtime

Handshakeはセッション確立ではなく「Institution Session Establishment」である。
AIは接続する前にInstitution Contractを読み、自分のRoleとCapabilityを宣言する。

1. AIがRoleとrequested_scopeを宣言する
2. InstitutionがContractに照らしてvalidateする
3. working_contextとともにセッションが確立する
4. すべての操作はsession_id付きでevents.dbに記録される

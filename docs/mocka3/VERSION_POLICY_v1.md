# MoCKA Version Policy v1

**Document ID**: VERSION_POLICY_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: EVENT_FOUNDATION_v1.md (v1.0.1), EVENT_DATA_LIFECYCLE_v1.md (v1.0.0), EVENT_TRANSITION_PROTOCOL_v1.md (v1.0.0)

---

## 1. Purpose

docs/mocka3/ 配下の仕様ドキュメントのバージョン管理・成熟度管理・変更手順・記録ルールを定義する。

---

## 2. Versioning Scheme

セマンティックバージョニング（vMAJOR.MINOR.PATCH）に従う。

| 変更種別 | 内容 |
|----------|------|
| MAJOR | 後方互換性のない変更（State定義変更、必須フィールド変更等） |
| MINOR | 後方互換性のある機能追加（新State追加、新セクション追加等） |
| PATCH | 誤字修正・表現の明確化・互換性に影響しない修正 |

---

## 3. Document Status Lifecycle

バージョンとは別軸で「仕様の成熟度」を管理する。

### Status 定義

| Status | 意味 |
|--------|------|
| Draft | 作成中 |
| Review | レビュー中 |
| Approved | 承認済み（実装可） |
| Active | 現行仕様（本番適用中） |
| Deprecated | 廃止予定 |
| Archived | 保守終了 |

### Status 遷移

```
Draft → Review → Approved → Active → Deprecated → Archived
```

### 管理ルール

- Statusはドキュメントヘッダーに明記する（Version と並列）
- StatusがApproved未満のドキュメントは実装に使用しない
- DeprecatedになったドキュメントはArchivedまで最低1 MAJORバージョンの猶予を設ける

### ドキュメントヘッダー形式（例）

| 項目 | 値 |
|------|-----|
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-06-15 |

---

## 4. 変更手順

1. 変更内容を分類（MAJOR / MINOR / PATCH）
2. Impact Assessment を実施し、影響ドキュメントを列挙する

   ### Impact Assessment フォーマット

   | 項目 | 内容 |
   |------|------|
   | Changed Document | EVENT_FOUNDATION_v1.md |
   | Change Type | MAJOR |
   | Affected | EVENT_DATA_LIFECYCLE_v1.md / EVENT_TRANSITION_PROTOCOL_v1.md |
   | Action | Review Required / No Update Required |
   | Reviewed by | きむら博士 / Claude / くろこ |

3. 影響ドキュメントがある場合は同一commitで更新する
4. 対象ドキュメントの変更履歴テーブルを更新
5. ドキュメントヘッダーのVersion・Statusを更新
6. ファイル名は変えない（バージョンはドキュメント内で管理）
7. git commit メッセージ形式:
   `docs: <ファイル名> vX.Y.Z — <変更内容一行要約>`
8. mocka_write_event で記録（what_type: DOCUMENT_UPDATED）

---

## 5. Version Release Rule（1対1対応）

1つのリリースバージョンに対して、必ず以下を1対1で対応させる：

| 要素 | 内容 |
|------|------|
| Document Version | vX.Y.Z |
| Git Commit | 単一commit（複数ファイルは同一commitにまとめる） |
| MoCKA Event | DOCUMENT_CREATED または DOCUMENT_UPDATED |

### 例

| Version | Git Commit | Event ID | what_type |
|---------|------------|----------|-----------|
| 1.0.0 | abc123 | E20260615_048 | DOCUMENT_CREATED |
| 1.1.0 | def456 | E20260615_0XX | DOCUMENT_UPDATED |

### 禁止事項

- 1つのcommitに複数バージョン変更を混在させない
- Eventを記録せずにバージョンを上げない
- commitせずにドキュメントを「Active」にしない

---

## 6. Appendix: 関連ドキュメント

```
VERSION_POLICY_v1.md（本仕様）
    └── docs/mocka3/ 配下の全ドキュメントのバージョン・Status・変更手順を管理

EVENT_FOUNDATION_v1.md
EVENT_DATA_LIFECYCLE_v1.md
EVENT_TRANSITION_PROTOCOL_v1.md
    └── 本Policyに従ってバージョン管理される
```

---

## 7. 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成: Document Status Lifecycle、Impact Assessment、Version/Commit/Event 1対1対応ルール定義 |

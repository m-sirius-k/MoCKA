# Guarantee Coverage Map v0.1

位置づけ: 博士指示（2026-07-03、Task-P）に基づき新規作成。PHI-OS→Memory→Relay→Orchestra→MoCKAの順に、それぞれ何を保証するのか、逆に誰も保証していない領域は何かを文章形式で整理する。図ではなく文章のみで構成する（博士指示による）。

実装は一切含まない。新規のコード調査は行わず、本日までの一連の監査（特に`GUARANTEE_MATURITY_INDEX_v0.1.md`、`CONCEPT_AUDIT_v0.1.md`）の内容を製品単位で読み替えたものである。

---

## 第1部: 現状把握

`GUARANTEE_MATURITY_INDEX_v0.1.md`で既に指摘した通り、本日の一連の監査はMoCKA本体とPHI-OSに関する情報に偏っており、Orchestra・Relayについては固有の保証実装がほぼ調査されていない。Memoryは製品としての実装（Chrome拡張）は確認されているが、それ以外の保証は薄い。したがって本マップは「均等に埋まった地図」ではなく、「調査の濃淡がそのまま可視化された地図」になる。この濃淡自体が一つの発見である。

---

## 第2部: 提案 — 製品別の保証内容と空白領域

### 2.1 PHI-OS

PHI-OSは、本日の調査で最も内容が確認できた製品側コンポーネントである。PHI-OSは「Chrome拡張Runtime Layer — 製品間神経系」という位置づけであり、MoCKA本体のガバナンス機構の一部（audit_trigger.py、human_gate.py、schema-registry.js、decision_ledger.jsonl／ise配下）が実際にPHI-OS配下に実装されている。

**PHI-OSが保証しているもの:** artifact_type（message/decision/todo/note等）の定義とバージョン一貫性（schema-registry.js）。event_gateを経由しない直接書き込みの検知（audit_trigger.py、SQLiteトリガー）。ISE（Intelligent State Engine）の状態遷移記録とその独自の整合性検証（decision_ledger.jsonl、verify_chain()）。人間承認の停止点そのもの（human_gate.py、Decision Policyから再利用される実装）。

**PHI-OSで誰も保証していない領域:** PHI-OS自体のTrust Boundary確立（Windows ACL設定、TODO_325未着手）。decision_ledger.jsonlのverify_chain()が定期的に実行されているか（カナリア的な継続検証）は不明。PHI-OSが処理する全artifact_typeについて、GL7相当の実行前安全性チェックを経由しているかは未確認。

### 2.2 Memory

Memory拡張（Chrome拡張、prefix "MEM-"）は、単一の明確な機能（ブラウザセッション内の作業状態＝ファイル・エラー・判断の記憶）を提供する製品として存在する。

**Memoryが保証しているもの:** chrome.storage.localを用いた、単一ブラウザセッション内での作業状態の保持（文脈継承保証の一種）。

**Memoryで誰も保証していない領域:** MoCKA本体が構想する「Infield（内部記憶）」という制度原則との統合（`mocka-infield`はORPHAN状態であり、Memory拡張がその代替物なのか、全く別物として並存するのかが未整理）。ブラウザデータが消去された場合の永続性（chrome.storage.localはユーザー操作で消去され得るが、それに対する保証・警告の仕組みがあるかは不明）。Memory拡張が保持するデータの正確性・改ざん検知（Ledgerクラスタのような不変性保証の対象になっているかは不明）。

### 2.3 Relay

Relay（Free/Pro/Oneプラン、Vault注入等の機能を持つ）について、本日の調査ではRelay固有の保証機構は確認できなかった。`CONCEPT_AUDIT_v0.1.md`のArchive/Catalog調査で「独自のarchive/catalog概念は未検出」（MODULE_CATALOGの傘下に統一管理される）という結果のみが判明している。

**Relayが保証しているもの（推定含む、要確認）:** MODULE_CATALOG_v1への登録という形での存在保証（G1）には含まれると考えられるが、Relay固有の機能（Pro/OneプランのAI要約・Vault注入等）が何を保証しているか（例えば要約内容の正確性、Vaultに保存されたデータの機密性・完全性）は今回調査していない。

**Relayで誰も保証していない領域（推定含む、要確認）:** 収益化パイプライン（Stripe連携、TODO_178保留中）の整合性保証。Vault機能のデータ保護に関する明示的な保証。これらは今回の監査群の対象に一度も入っておらず、本マップ作成時点では「未調査」というより「そもそも監査対象として認識されていなかった」に近い。

### 2.4 Orchestra

Orchestra（本番稼働中、Stripe→Cloudflare Workers→Resendという決済・通知パイプライン）についても、Relayと同様に固有の保証機構は確認できていない。

**Orchestraが保証しているもの（推定含む、要確認）:** MODULE_CATALOG_v1への登録という存在保証には含まれると考えられる。決済処理自体は本番稼働中であり実務上は機能しているはずだが、その整合性（決済の二重処理防止、webhook処理の冪等性等）が制度的にどう保証されているかは、本日の監査群では一度も扱われていない。

**Orchestraで誰も保証していない領域（推定含む、要確認）:** 決済フローの整合性保証全般。これはMoCKAの哲学的な保証（Ledger、Human Gate等）とは異なる、商用サービスとして本来最も重要度が高いはずの保証領域だが、本日の一連の監査（Concept/Guarantee/Human Gate/Vocabulary）のいずれもこの領域に触れていない。

### 2.5 MoCKA（本体）

MoCKA本体は、本日のほぼすべての監査の中心対象であり、G1〜G10の10種の保証のうち大半について、少なくとも制度定義（Level 1）以上の状況が確認されている（`GUARANTEE_MATURITY_INDEX_v0.1.md`参照）。

**MoCKAが保証しているもの:** 存在保証（KN-004、各local registry、部分的）、不変性保証（ledger.json、部分的）、網羅性保証（event_gate一元化、稼働中）、実行前安全性保証（GL7、既知の穴あり）、人間最終決定保証（human_gate.py実装済み、接続に複数の断絶）、品質・妥当性保証（Caliber各系統、稼働中）、権限分離保証（Decision Policy、audit_trigger.py）。

**MoCKAで誰も保証していない領域:** 暴走・停滞検知保証の実効性（DRIFT_STANDARDの実装疑義）。単一正本保証の完全性（KN-004/MODULE_CATALOG重複疑い）。文脈・経験継承保証の統合性（mocka-infield ORPHAN）。いずれもLevel 4（継続検証済）に到達している保証は一つもない。

---

## 第3部: 全体を通じて誰も保証していない領域（横断的な空白）

- **製品間を横断する統一的な保証枠組みが存在しない。** PHI-OS・Orchestra・Relay・Memoryは、それぞれMODULE_CATALOGへの登録という形式的な存在保証の傘下にはあるが、その先（不変性・品質・実行前安全性等）は製品ごとに実装状況がバラバラであり、統一的な基準で評価されたことがない
- **商用機能固有の保証（決済・配信・課金）は、本日の一連の監査（MoCKAの制度哲学に根ざしたGuarantee群）の対象に一度も入っていない。** これはMoCKAの保証体系が「制度的・記録的な正しさ」には強く焦点を当てている一方、「商用サービスとしての信頼性」という別種の保証軸をまだ体系的に扱っていないことを示唆している（要確認: これは意図的な棲み分けなのか、単なる未着手なのか）
- **Relay・Orchestra固有の保証は、今回「不明」というより「監査対象として一度も認識されていなかった」に近い。** これは`GUARANTEE_MATURITY_INDEX_v0.1.md`の限界（MoCKA本体・PHI-OSへの調査の偏り）がそのまま反映された結果であり、今回のマップ作成によって初めて明示的な空白として認識されたと言える

---

## 第4部: 未確定事項

- Relay・Orchestra・Memoryの保証内容の多くは「推定含む、要確認」と付記した通り、今回新規調査を行っていないための推測が含まれる。今後の追加調査が必要
- 商用機能の保証とMoCKAの制度的保証が別体系として意図的に棲み分けられているのか、単に一方が手薄なだけなのかは、博士確認が必要
- 本マップは文章のみで構成する指示に従ったが、対象・保証・空白領域の関係が複雑なため、将来的に図示した方が理解しやすい可能性がある（今回は指示通り図は作成していない）

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Pに基づき新規作成。

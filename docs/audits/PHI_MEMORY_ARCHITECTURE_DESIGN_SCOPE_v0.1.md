# PHI Memory Architecture Design Scope v0.1

**Status:** SCOPE(設計準備。Architecture本体の確定はまだ行わない)
**位置づけ:** DC-PHI-REG04-001(`DC_20260729_010`)確定後、ジャービス化ロードマップ Phase J1(PHI Memory Architecture設計)への移行準備。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. 対象

- Event Ledger
- Decision Ledger
- Living Context
- Memory分類
- Evidence再利用
- Forget / Retention Policy

---

## 2. 現状確認(Confirmed、既存資料に基づく)

設計をゼロから始めないため、各対象について既に存在する一次資料を確認した。

| 対象 | 現状(Confirmed) |
|---|---|
| Event Ledger | `data/mocka_events.db`(現在18,258件超、`phi_os/event_gate.py`の`process_event()`/`_write()`が唯一の正規書込経路、`integrity.py`によるSHA-256ハッシュチェーン署名あり) |
| Decision Ledger | `mocka_decision_write/get/list`ツール経由。本セッションで`DC_20260729_001`〜`010`まで運用実績あり(alternatives/rationale/impact/approved_byの構造化スキーマが既に機能している) |
| Living Context | `data/context_snapshots/*.json`(`context_latest.json`含む、スナップショット形式で継続的に生成されている) |
| Memory分類 | **PHI-OS Core(`ise/`)レベルでは未定義。** ただし`ise/state_machine.py`(状態遷移)・`ise/decision_ledger.py`(PHI-OS内部の別Decision Ledger、MoCKA側Decision Ledgerとは別データストア、`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`で既確認)が関連する既存構造として存在する |
| Evidence再利用 | Decision Ledgerの`related_documents`/`related_events`フィールドが、本セッション内で一貫してEvidence参照の仕組みとして機能している(既存の運用パターン) |
| Forget / Retention Policy | **`docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md`(2026-06-15、Status: Active)で既に定義済み。** 現行ポリシー(v1)は「全データ永久保持、DELETE全状態禁止」。将来の保持ポリシー候補(Archivedデータの5年後cold storage移行等)はv2以降で検討、と明記されている |

**重要な制約**: `EVENT_DATA_LIFECYCLE_v1.md`はMoCKA本体の既存Active仕様であり、本Memory Architecture設計がこれと矛盾するForget機構を提案する場合、既存仕様の改定が必要になる。本Scope段階ではこの矛盾の有無を指摘するに留め、解消は次工程(Architecture本体設計)で扱う。

---

## 3. 精査が必要な論点(未定義、Design本体で扱う)

- **Memory分類の4区分**(Episode/Semantic/Procedural/Decision Memory)を、PHI-OS Core(`phios/`+`ise/`)のどの既存コンポーネントに対応させるか、あるいは新規コンポーネントとして追加するか
- **保存条件**: どのイベント種別がどのMemory分類に振り分けられるか
- **再利用条件**: Decision Ledgerの`related_documents`/`related_events`のような参照の仕組みを、Memory全体でどう一般化するか
- **Forget条件**: `EVENT_DATA_LIFECYCLE_v1.md`が「全データ永久保持」と定めている中で、PHI-OS Core固有のMemory(Living Context等)に別のForget条件を設けることが許容されるか、それとも同一ポリシーに従うべきか
- **Verification条件**: Event Ledgerが持つSHA-256ハッシュチェーン検証の仕組みを、他のMemory種別にも同様に適用するか

---

## 4. 本Scopeの範囲外

- Memory Architecture本体の確定設計(`PHI_MEMORY_ARCHITECTURE_v1.0.md`は別途作成)
- `EVENT_DATA_LIFECYCLE_v1.md`の改定
- PHI Sequence Controller設計(Phase J2、別途着手)
- PHI-REG-04関連の実装(`DC_20260729_010`でLegacy Freeze確定済み、対象外)

---

## 5. 次工程

本Scopeの確認後、`PHI_MEMORY_ARCHITECTURE_v1.0.md`の作成(Memory分類・保存条件・再利用条件・Forget条件・Verification条件の確定設計)へ進む。

---

## Knowledge Lineage

**Document:** PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md
**Status:** SCOPE
**Created:** 2026-07-29
**Origin:** DC-PHI-REG04-001(`DC_20260729_010`)確定後、きむら博士よりジャービス化ロードマップPhase J1として作成を指示された。
**Parent Documents:**
- DC_20260729_010(DC-PHI-REG04-001)
- docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md
- PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md
**Derived From:** DC_20260729_010(次工程指定)
**Supersedes:** なし
**Reason For Creation:** Memory Architecture設計本体の着手前に、既存資料(Event/Decision Ledger、Living Context、既存Retention Policy)を確認し、精査が必要な論点と範囲外事項を明確化するため。
**Affected Components:** Event Ledger、Decision Ledger、Living Context、PHI-OS Core(`ise/`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。対象6項目の現状確認、精査が必要な論点5件、範囲外4件、次工程を記載。設計本体・実装・Decision Ledger登録は無し。

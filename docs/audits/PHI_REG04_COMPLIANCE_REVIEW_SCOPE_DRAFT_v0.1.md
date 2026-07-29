# PHI-REG-04 Compliance Review Scope Draft v0.1

**Status:** DRAFT(Scope定義のみ。レビュー本体はまだ実施しない)
**位置づけ:** DC-PHI-ID-002(`DC_20260729_009`、PHI Authority Flow Pending Resolution)確定後の次工程。PHI-REG-04(`phi_os_bridge.py`)のConstitution Compliance Reviewに着手する前のScope定義。
**目的(きむら博士指定):** 本レビューの目的は「Authorityを決定すること」ではなく、「現在のAuthority Pending状態でもPHI登録制度が破綻しないことを確認すること」である。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Registration対象の定義

- **レビュー対象実体:** `PlanningCaliber/workshop/seo-os/mocka/phi_os_bridge.py`(PHI-REG-04。`MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md`§1で既に確定済みのIdentity Registry ID)
- **レビュー対象外:** PHI-Con/PHI-Core/PHI-HABのIdentity/Responsibility Classification(`DC_20260729_008`で別途確定済み)。本レビューはこの分類を変更しない。
- **Identity Namespaceとの境界:** PHI-REG-04という識別自体は2026-06-24監査で既に確定したIdentity問題であり、本レビューはこの識別・Registry IDを変更・再定義しない。対象はあくまで「`phi_os_bridge.py`の動作がConstitutionの規定に従っているか」という運用上のCompliance問題のみに限定する。
- **Responsibility Classificationとの関係:** `phi_os_bridge.py`は現時点でPHI-Con/Core/HABいずれのAliasにも紐付けられていない(`DC_20260729_008`のスコープ外)。本レビューはこの紐付けを新設・確定するものではない。

## 2. Authority未確定状態への耐性確認

- **判定基準の独立性:** 本レビューの判定基準は`PHI_OS_CONSTITUTION_v1.md`第2章原則4「DBは保存媒体であり真実ではない」・第5章5.1「DB直接更新によるEvent生成」禁止のみに基づく。これらはRATIFIED Constitution本文の条項であり、PHI-Con/PHI-Core間のAuthority Flow(`DC_20260729_009`でPending Resolution)がModel A/B/Cいずれで確定しようと影響を受けない、独立した判定基準である。
- **暗黙前提の排除:** レビュー実施・記録行為自体が、PHI-Con/PHI-Core間の統治方向について何ら暗黙の前提を置かないことを、レビュー開始前にここで明記する。
- **Pending状態の維持:** 本レビューは`DC_20260729_009`(Pending Resolution)を変更・解消しない。レビュー結果がAuthority Flow解決の根拠として転用される場合は、別途Human Gate判断を要する。

## 3. Evidence追跡可能性

| 種別 | 対象 |
|---|---|
| 一次資料(制度) | `PHI_OS_CONSTITUTION_v1.md`第2章原則4、第5章5.1 |
| 実装コード(正規経路) | `phi_os/event_gate.py`(`process_event()`/`_write()`、TODO_322/369) |
| 実装コード(レビュー対象) | `phi_os_bridge.py`(本セッションで2026-07-29時点の状態を独自再検証済み、`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`§3参照) |
| 既存監査 | `MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md`§7(2026-06-24、同一違反候補の初出記録) |
| Decision参照 | 本レビュー結果は、承認され次第DC-PHI-ID-003候補として、DC-PHI-ID-001/002とは独立したDecisionになる見込み |
| Event Ledger連携 | 本セッション内のCHANGE_DONEイベント(`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`作成時、`phi_os_bridge.py`の2026-07-29時点の状態確認記録)を参照 |
| Human Gate対象 | レビュー結果の是正要否判断(コード修正の実施可否)は本Scope Draftの対象外とし、レビュー完了後に別途Human Gateへ諮る |

---

## 4. レビュー範囲の明示

**含む:**
- `phi_os_bridge.py`の現状コード(DB直接接続・生SQL INSERT・event_gate迂回・hash chain署名の有無)の事実確認
- 上記事実とConstitution第2章原則4・第5章5.1との照合
- 既存監査(2026-06-24)からの状態変化の有無の確認

**含まない:**
- `phi_os_bridge.py`のコード修正・is_core_system_file判定・削除等の実装対応
- PHI-Con/PHI-Core間のAuthority Flow解決
- PHI-Con/Core/HABへの`phi_os_bridge.py`の新規Alias付与
- SEO-OS側の他コンポーネントへのレビュー範囲拡大

---

## 5. 次ステップ(本Scope Draft確定後)

1. Findings整理(事実確認結果のまとめ)
2. Authority Pending状態との依存関係確認(Findingsが`DC_20260729_009`に影響しないことの再確認)
3. 必要なら新規Evidence生成(追加のコード確認等)
4. Authority Flow再評価条件確認(本レビュー結果が`DC_20260729_009`のNext Resolution Conditionに該当しないことの確認)

---

## Knowledge Lineage

**Document:** PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1.md
**Status:** DRAFT
**Created:** 2026-07-29
**Origin:** DC-PHI-ID-002(`DC_20260729_009`)確定後、きむら博士よりPHI-REG-04 Compliance Review着手前のScope定義作成を指示され作成。
**Parent Documents:**
- MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
- docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md
- PHI_OS_CONSTITUTION_v1.md
- DC_20260729_008、DC_20260729_009
**Derived From:** PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1(PHI-REG-04分離方針の継承元)
**Supersedes:** なし
**Reason For Creation:** PHI-REG-04 Compliance Reviewの範囲・判定基準・Authority Pending状態との非依存性を、レビュー本体着手前に明確化するため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Registration対象定義・Authority耐性確認・Evidence追跡可能性・レビュー範囲・次ステップを記載。レビュー本体・実装・Decision Ledger登録は無し。

# INSTITUTION_RUNTIME_v1.md
## PHI-OS Institution Runtime 設計書

**文書番号:** PHI-OS-RUNTIME-001  
**作成日:** 2026-06-16  
**フェーズ:** MoCKA Phase 5 — Institution Runtime 実装  
**状態:** IMPLEMENTED v1  
**上位文書:** PHI_OS_CONSTITUTION_v1.md  

---

## 概要

Institution Runtimeは、MoCKA全Gateが共通利用する制度実行エンジンである。  
制度判定を各Gateへ分散させず、このRuntimeに一元集約することで  
「制度ルールを各Gateへ重複実装しない」原則を実現する。

---

## モジュール構成

```
phi_os/
    runtime/
        __init__.py               — 公開API一覧
        institution_runtime.py    — Runtime統合入口 (シングルトン対応)
        runtime_types.py          — 共通型・データ構造定義
        runtime_errors.py         — Runtime専用例外
        meaning_registry.py       — Meaning辞書
        authority_manager.py      — Authority管理
        institution_registry.py   — Institution管理
        gate_registry.py          — Gate管理
        binding_engine.py         — Binding Layer実行エンジン
        compliance_engine.py      — 制度監査エンジン
```

---

## モジュール依存図

```
institution_runtime.py
    ├─ meaning_registry.py     ← runtime_types.py, runtime_errors.py
    ├─ authority_manager.py    ← runtime_types.py, runtime_errors.py
    ├─ institution_registry.py ← runtime_types.py, runtime_errors.py
    ├─ gate_registry.py        ← runtime_types.py, runtime_errors.py
    ├─ binding_engine.py       ← meaning_registry, institution_registry, gate_registry
    └─ compliance_engine.py    ← meaning_registry, institution_registry, gate_registry,
                                  binding_engine, authority_manager
```

外部依存: Python標準ライブラリのみ（hashlib, uuid, re, datetime, dataclasses, enum）

---

## API一覧

### InstitutionRuntime (institution_runtime.py)

| メソッド | 説明 | 参照制度文書 |
|---|---|---|
| `resolve_meaning(meaning_id)` | Meaning IDからMeaningを解決 | Constitution 原則6 |
| `register_meaning(meaning)` | 新Meaningを登録 | Constitution 原則2 |
| `resolve_institution(institution_id)` | InstitutionをID解決 | Constitution 原則7 |
| `register_institution(institution)` | Institutionを登録 | Constitution 原則2 |
| `resolve_authority(authority_type)` | AuthorityTypeからAuthority解決 | Constitution 3.1 |
| `resolve_authority_for_gate(gate_id)` | Gate対応Authorityを解決 | GATE_ARCH 4.1 |
| `validate_binding(artifact)` | Artifact Binding状態検証 | Constitution 4.1 |
| `register_artifact(artifact)` | Artifact制度登録 | Constitution 4.1, 原則7 |
| `validate_gate(gate_id, artifact)` | Gate通過可否検証 | GATE_ARCH 2章 |
| `create_event_context(artifact)` | Event生成コンテキスト作成 | INSTITUTION_PROTOCOL 5章 |
| `audit(artifacts)` | 全件制度監査 | Constitution 6.3 |
| `check_compliance(artifact)` | 単一Artifact即時チェック | Constitution 6.2 |
| `status()` | Runtime状態サマリ | — |
| `get_instance()` | シングルトン取得 | — |
| `reset()` | テスト用リセット | — |

---

## 型定義一覧 (runtime_types.py)

| 型 | 用途 |
|---|---|
| `Artifact` | 制度登録対象の基本単位 |
| `Meaning` | 制度意味分類 |
| `Institution` | 制度機関 |
| `Authority` | 権限単位 |
| `Gate` | 制度通過口 |
| `BindingResult` | Binding検証結果 |
| `ComplianceResult` | 監査結果 |
| `ComplianceViolation` | 個別違反記録 |
| `EventContext` | Event生成コンテキスト |
| `BindingStatus` | Binding状態enum |
| `MeaningClass` | Meaning分類enum |
| `AuthorityType` | Authority種別enum |
| `GateId` | Gate識別子enum |
| `GateStatus` | Gate稼働状態enum |
| `ViolationSeverity` | 違反重大度enum |

---

## 例外定義一覧 (runtime_errors.py)

| 例外 | トリガー条件 | 重大度 |
|---|---|---|
| `BindingError` | Binding接続の異常 | Medium〜High |
| `AuthorityConflictError` | Authority一意性違反 (Constitution 3.2) | Critical |
| `MeaningNotFoundError` | Meaning未登録 | High |
| `GateValidationError` | Gate通過検証失敗 | High |
| `InstitutionResolutionError` | Institution解決失敗 | High |
| `ComplianceViolationError` | 制度違反検知 | Critical〜High |
| `OrphanArtifactError` | Institution未所属 (Constitution 原則7) | High |
| `ShadowArtifactError` | Gate外部存在 (Constitution 4.2) | Medium |
| `DuplicateBindingError` | Binding重複登録禁止 | High |

---

## Compliance Engine — 検知項目一覧

| 検知種別 | メソッド | 重大度 | 根拠 |
|---|---|---|---|
| Gate迂回 | `check_gate_bypass()` | Critical | Constitution 5.3 |
| Authority重複 | `check_authority_duplication()` | Critical | Constitution 5.5 |
| Meaning未定義 | `check_undefined_meaning()` | High | Constitution 5.2 |
| Binding切断 | `check_binding_disconnected()` | High | Constitution 4.2 |
| Institution未所属 | `check_institution_missing()` | High | Constitution 5.2 |
| Event不正生成 | `check_event_invalid_generation()` | Critical | Constitution 5.1 |
| Authority競合 | `audit()` 内自動実行 | Critical | Constitution 3.2 |

---

## Binding状態遷移

```
UNKNOWN
  ↓ Meaning登録
  ↓ Institution帰属確定
  ↓ Gate割当
CONNECTED  ←── 正規状態 (全制度操作可)
  ↓ 廃止決定
DEPRECATED ←── 参照のみ可
  ↓ 後継確認後
(ARCHIVE)

UNKNOWN
  ↓ Institution未所属
ORPHAN   ←── 即時修復対象

UNKNOWN / PARTIAL
  ↓ Gate外部存在判定
SHADOW   ←── 監視対象。制度操作不可
```

---

## Gate Authority 対応表 (GATE_ARCHITECTURE_v1.md 4.1 準拠)

| Gate | Authority | 委任可否 |
|---|---|---|
| Event Gate (GATE-EVENT) | Event Authority | 不可 |
| Knowledge Gate (GATE-KNOW) | Knowledge Authority | 部分委任可 |
| Module Gate (GATE-MOD) | Institution Authority | 委任可 |
| Prompt Gate (GATE-PROMPT) | Gate Authority | 不可 |
| Release Gate (GATE-REL) | Version Authority | 不可 |
| Experiment Gate (GATE-EXP) | Gate Authority (PHI-OS) | 部分委任可 |
| Document Gate (GATE-DOC) | Gate Authority (PHI-OS) | 部分委任可 |

---

## Event Gate との連携方法

Event Gate (phi_os/event_gate.py) は、Phase 5以降以下のように Runtime を利用できる。

```python
from phi_os.runtime import InstitutionRuntime, Artifact, GateId

rt = InstitutionRuntime.get_instance()

# Gate通過前の制度検証
artifact = Artifact(
    artifact_id=payload.get("artifact_id", ""),
    name=payload.get("what_title", ""),
    path=payload.get("where_path", ""),
    meaning_id="SYSTEM_CORE",
    institution_id=payload.get("institution_id", "MoCKA"),
    gate_id=GateId.EVENT,
)
ok, issues = rt.validate_gate(GateId.EVENT, artifact)
if not ok:
    return {"status": "rejected", "errors": issues}

# Event Contextで Authority確認
ctx = rt.create_event_context(artifact)
# ctx.authority_type == AuthorityType.EVENT が保証される
```

---

## 実装原則（Phase 5実装指示書準拠）

1. Runtimeは制度文書を唯一の参照元とする
2. 各Gateは制度判定を自前実装しない
3. Authorityは必ず一意である（Authority Manager管理）
4. Binding判定はBinding Engineのみが担当する
5. Compliance判定はCompliance Engineのみが担当する
6. Runtime APIを通さない制度判定は禁止する

---

## テスト

```bash
# phi_os ルートから実行
cd C:\Users\sirok\MoCKA
python -m pytest phi_os/tests/test_institution_runtime.py -v
```

テストカバレッジ対象:
- MeaningRegistry: 登録・取得・変更履歴・UNCLASSIFIED拒否
- AuthorityManager: 解決・競合なし・委譲不可・継承
- InstitutionRegistry: 登録・所属判定・逆引き
- GateRegistry: 7Gate登録・遷移検証・MeaningClass検証
- BindingEngine: CONNECTED判定・ORPHAN・UNKNOWN・SHADOW・重複禁止
- ComplianceEngine: 全違反種別・全体監査
- InstitutionRuntime: シングルトン・Status・EventContext・全体パイプライン

---

## 完成条件（Phase 5実装指示書）

| 条件 | 状態 |
|---|---|
| Institution RuntimeがPHI-OS内で共通利用可能 | ✅ phi_os/runtime/ 実装完了 |
| Meaning・Institution・Authority・Gate・Bindingを一元管理 | ✅ 各Registryで管理 |
| Runtime API経由で制度判定が実行できる | ✅ InstitutionRuntime API提供 |
| Compliance Engineが制度違反を検知できる | ✅ 7種別の違反検知実装 |
| Event GateがRuntimeを利用できる構造 | ✅ EventContext API提供。移行は次フェーズ |
| 将来のGate等でも再利用可能な構造 | ✅ シングルトン + 依存注入設計 |

---

## 関連文書

- PHI_OS_CONSTITUTION_v1.md — 制度憲法
- INSTITUTION_PROTOCOL_v1.md — 制度参加者共通運用規約
- GATE_ARCHITECTURE_v1.md — Gate統一設計
- BINDING_REGISTRY_v1.md — Artifact制度登録台帳
- MEANING_AUTHORITY_v1.md — Meaning正典定義
- INSTITUTION_BINDING_MAP_v1.md — Institution・Gate接続マップ

*文書バージョン: v1.0*  
*最終更新: 2026-06-16*  
*実装者: Claude (Phase 5 実装指示書に基づく)*

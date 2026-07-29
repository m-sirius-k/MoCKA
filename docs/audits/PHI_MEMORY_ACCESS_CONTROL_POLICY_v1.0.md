# PHI Memory Access Control Policy v1.0

**Status:** DESIGN(正式定義案。実装・Decision Ledger登録はまだ行わない)
**位置づけ:** PHI-OS Operational Integration Phase, **I-03**。S07(`PHI_SEQUENCE_STATE_MODEL_v1.0.md`)が「状態遷移の憲法」を定義したのに対し、本文書は「記憶へのアクセス法典」を定義する。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 0. State -> Memory Permission Mapping(S07との整合)

`PHI_SEQUENCE_STATE_MODEL_v1.0.md`§2の11状態に対し、各状態でMemoryに許可される操作を対応づける。

| State | Memory操作 |
|---|---|
| OBSERVED | Read不可(Contextまだ未取得) |
| CLASSIFIED | Read開始(関連Memory検索) |
| CONTEXT_READY | Read完了(Context Reconstruction完了) |
| VERIFICATION_PENDING | Read継続(MoCKAがEvidence参照) |
| VERIFIED | Read(検証済みEvidenceとして確定) |
| HUMAN_GATE_REQUIRED | Read(Human Gateへの提示用) |
| APPROVED | Write要求発行(Decision Memory相当、Decision Ledger登録) |
| EXECUTING | Read限定(実行に必要な範囲のみ) |
| COMPLETED | Write準備(Audit Event生成待ち) |
| AUDITED | Write実行(Event Ledgerへの監査記録) |
| MEMORIZED | Write完了(Event/Decision/Semantic/Procedural Memoryへの正式分類) |
| UNKNOWN | Read可(既存Evidence参照は可)、**Write不可**(不確定な状態を新規Memoryとして確定させない) |

**原則**: Memoryへの書込(Write)は`APPROVED`以降の状態でのみ許可され、`OBSERVED`〜`VERIFICATION_PENDING`の間はRead(参照)のみに限定される。これは`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`のMemory Interface Contract(判断は行わない)と整合する。

---

## 1. Memoryの所有権境界

**Memory = 真実の保管庫ではない。** 「Memory = Evidence付き再利用可能状態の保存層」として定義する。

| 主体 | Memoryとの関係 |
|---|---|
| Memory Module | 保持する(Event/Decision/Semantic/Procedural Memoryの物理的な保存・分類・再構成を担当する唯一の主体) |
| MoCKA | 検証する(Memoryに書き込まれる内容がConstitution原則4・5.1・Event Gate経路に従っているかを検証する。Memory自体の内容の真偽判断はMoCKAの検証結果に基づく) |
| Orchestra | 参照可能(モデル選択・能力判断に必要な範囲のMemoryのみを参照する。全Memoryへの無制限アクセス権は持たない) |
| Relay | 搬送可能(外部システムとの間でMemory相当の情報を搬送するが、内容の信頼性判断は行わない。`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`のRelay境界と一致) |
| Sequence Controller | 判断可能な唯一の主体ではない。**Sequence Controllerは「どのMemoryを取り出すか」を判断できるが、「そのMemoryが正しいか」は判断しない**(Verificationの領域はMoCKAに属する) |

---

## 2. Access Control Matrix

| Actor | Read | Write | Approve | Delete |
|---|---|---|---|---|
| PHI-OS(Sequence Controller) | ○ | 要求のみ(直接書込は行わない) | × | × |
| MoCKA | ○ | ○(Event Gate経由のEvent Memory書込) | △(Gate通過判定のみ。Human Decisionそのものではない) | × |
| Memory | ○ | ○(実際の物理書込を実行する唯一の主体) | × | × |
| Orchestra | △(Model Selectionに必要な範囲のみ) | × | × | × |
| Relay | × (内容への直接読取は想定しない。状態同期のみ) | 要求のみ(MoCKA Gate経由でのみ反映) | × | × |
| Human Gate | ○(Evidence確認のため) | × | ○(唯一のApprove権限保持者) | × |

**Delete列が全Actorで×である理由(Confirmed)**: `docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md`「DELETEは全状態で禁止。MoCKAはデータを消さない」という既存Active仕様を、本Policyでも例外なく継承する。

---

## 3. Memory Freshness Contract

S07のUNKNOWN思想との接続。

```
Stored Evidence
      |
      v
 Time Passage
      |
      v
Validity Unknown
```

**時間経過したMemoryは、自動的にVerified扱いへ戻さない。** あるEvidenceが過去に`VERIFIED`状態を経て`MEMORIZED`されたとしても、それを再利用する時点で以下を確認する必要がある。

- 当該Memoryが参照する制度・実装(Constitution・Decision Ledger等)が、その後Supersede/変更されていないか
- 十分な時間が経過している場合、再利用前に再検証(MoCKA経由の再Verification)を要求するか否か

**本Policyで決めないこと**: 具体的な鮮度閾値(何日経過で再検証が必要か等)は本文書では確定させない。数値基準の設定は、Evidence不足のまま確定させることを避けるため、別途Decision対象とする。原則としては「古いMemoryをValidity Unknownとして扱う判断自体は許容されるが、Unknownから自動的にVerifiedへ戻す遷移は`PHI_SEQUENCE_STATE_MODEL_v1.0.md`§5の禁止(推測による自動遷移の禁止)に従い認めない」ことのみを確定する。

---

## 4. Forbidden Memory Operations

以下は明示的に禁止する。

| 禁止操作 | 理由 |
|---|---|
| 未検証MemoryからDecision生成 | `VERIFICATION_PENDING`〜`VERIFIED`を経由しないMemoryを根拠にHuman Gateへ判断を要求することは、Evidence Requirement(`PHI_MODULE_INTERFACE_CONTRACT_v0.1.md`)違反となる |
| Archive済Memoryの無断改変 | `EVENT_DATA_LIFECYCLE_v1.md`の不可逆遷移・禁止遷移原則(Normalizedの上書き禁止等)と整合。Archive済状態のMemoryは参照のみ許可され、内容変更は認めない |
| Context不足状態での再利用 | `CONTEXT_READY`に到達していないMemory(関連情報の取得が不完全な状態)を根拠に次の判断へ進むことは、`OBSERVED -> EXECUTING`等の禁止遷移(`PHI_SEQUENCE_STATE_MODEL_v1.0.md`§4)と同型のリスクを生む |
| Provenance欠落Memoryの昇格 | 出典(`event_id`/`decision_id`等)を持たないMemoryを、より上位の分類(例: Semantic Memoryへの一般化)へ昇格させることは、Evidence Chainの追跡可能性を破壊するため禁止する。これは本セッションで実施したPHI-REG-04 Compliance Reviewが重視した「Confirmed/Hypothesis/Unknownの峻別」原則と同じ精神に基づく |

---

## 5. 本Policyで決めないこと

- 具体的な鮮度閾値・再検証周期の数値
- Memory暗号化・アクセス認証の技術的実装
- 個人情報を含むMemoryの特別扱い(将来のPersonal Context Engine設計、Phase II-02で扱う)
- Human Gate Integration Model本体(Phase I-04で扱う)

---

## Knowledge Lineage

**Document:** PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md
**Status:** DESIGN
**Created:** 2026-07-29
**Origin:** `PHI_SEQUENCE_STATE_MODEL_v1.0.md`完了後、きむら博士よりPhase I-03(S08)として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_SEQUENCE_STATE_MODEL_v1.0.md
- docs/audits/PHI_MODULE_INTERFACE_CONTRACT_v0.1.md
- docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md
- docs/mocka3/EVENT_DATA_LIFECYCLE_v1.md
**Derived From:** PHI_SEQUENCE_STATE_MODEL_v1.0(State→Memory Permission Mapping)、PHI_MEMORY_ARCHITECTURE_v1.0(§6 Memory Access Governanceの未定義領域を引き継ぐ)
**Supersedes:** なし
**Reason For Creation:** `PHI_MEMORY_ARCHITECTURE_v1.0.md`§6で未定義のまま残されていたMemory Read Access Controlを正式に定義するため。
**Affected Components:** Memory、MoCKA、Orchestra、Relay、Sequence Controller
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。State→Memory Permission Mapping、所有権境界、Access Control Matrix、Memory Freshness Contract(S07 UNKNOWN接続)、Forbidden Memory Operations4件、本Policyで決めないこと4件を記載。実装・Decision Ledger登録は無し。

# PHI Runtime Architecture Validation v1.0

**Status:** REVIEW(V-01〜V-05俯瞰レビュー。新規実装はまだ行わない)
**位置づけ:** Phase V(Runtime Code Implementation)、V-06着手前の立ち止まりレビュー。次のRuntime層を追加する前に、実装済みコードを直接検証してArchitecture全体を俯瞰する。
**Git基準点(workshop repo):** `1d08ee2`(V-01)→`94f71fe`(V-02)→`d1a96b4`(V-03)→`fe99f21`(V-04)→`38db90d`(V-05)

---

## 1. 各コンポーネントの責務再確認(Confirmed、実コードから検証)

| Phase | ファイル | 行数 | 責務 |
|---|---|---|---|
| V-01 | `controller_core.py` | 166 | State保持・Transition要求受付・Transition条件確認・Event生成呼び出し(スタブ経由) |
| V-02 | `event_runtime.py` | 134 | TransitionRecord→EventObject変換・インメモリ保持 |
| V-03 | `adapter_runtime.py` | 114 | ExternalRequest検証・Controller Coreへの委譲(単純変換のみ) |
| V-04 | `test_runtime_integration.py` | 146 | 上記3層の統合経路検証(コンポーネントではなくEvidence) |
| V-05 | `memory_boundary.py` | 64 | Context保持・読み取り専用アクセス |

各ファイルの公開API(実コードから抽出、Confirmed)は、いずれも当初の設計文書(S05〜S09、P2-02、IV-02〜IV-03)が定めた最小責務を超えていない。

---

## 2. 依存関係の一方向性確認(Confirmed、import文を実測)

```
grep結果:
controller_core.py  -> (phios.runtime内部依存 0件)
event_runtime.py     -> controller_core(TransitionRecordのみ)
adapter_runtime.py   -> controller_core(ControllerCore, State, TransitionRecordのみ)
memory_boundary.py  -> (phios.runtime内部依存 0件)
```

依存グラフ:

```
              controller_core.py (基盤、依存0)
                    ^
        +-----------+-----------+
        |                       |
  event_runtime.py       adapter_runtime.py
   (1依存のみ)              (1依存のみ)

  memory_boundary.py (完全独立、依存0)
```

**確認結果**: 依存は完全に一方向であり、循環依存は存在しない。`event_runtime.py`と`adapter_runtime.py`は互いをimportしない(接続は呼び出し側コード・テストが担う、内部結合ではない)。`memory_boundary.py`は他のいずれの`phios.runtime`モジュールからも参照されていない、意図通りの疎結合。

---

## 3. 当初計画との照合(重要な発見)

`PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md`(IV-01)が定めた実装順序は以下だった。

```
1. Event Schema基盤
2. MoCKA Adapter
3. Memory Adapter
4. Orchestra Adapter
5. Relay Adapter
6. Sequence Controller(Reject除く)
7. Human Gate Interface(Approve/Request More Evidence経路)
```

実際の実装(V-01〜V-05)と照合すると:

| IV-01計画 | 実際の対応 | 一致度 |
|---|---|---|
| Event Schema基盤 | V-02 `event_runtime.py` | 一致 |
| Sequence Controller | V-01 `controller_core.py` | 一致 |
| MoCKA Adapter | **未実装**。V-03の`adapter_runtime.py`はMoCKA固有ではなく、任意の外部要求を受け付ける汎用入力境界として実装された | 乖離 |
| Memory Adapter | **部分実装**。V-05の`memory_boundary.py`は読み取り専用のみで、P2-02が定めたProvenance取得・Freshness返却は実装されていない | 部分乖離 |
| Orchestra Adapter | 未着手 | 未着手 |
| Relay Adapter | 未着手 | 未着手 |
| Human Gate Interface | 未着手(状態モデル上`UNKNOWN`経由のRequest More Evidence経路はController Core内に存在するが、独立したInterfaceコンポーネントは無い) | 未着手 |

**この乖離自体は問題ではない。** V-03/V-05は、4つの個別Adapterを1つずつ作るより先に、「どのAdapterにも共通する最小限の入出力境界」を先に確立するという、より基盤的なアプローチを取った。これはボトムアップ設計として合理的だが、**IV-01文書とは異なる順序で進んだという事実は記録として残す必要がある**(文書と実装の乖離を放置しない)。

---

## 4. MoCKA/Memory/Orchestra/Relay実接続の位置評価

現在の構造上、実接続点は明確に特定できる。

- **MoCKA接続点**: `adapter_runtime.py`とController Coreの間に、MoCKA固有の検証ロジック(`phi_os/event_gate.py`呼び出し)を持つ専用Adapterを追加する形が適切。現状の汎用`AdapterRuntime`はこの専用Adapterの前段(入力形式の検証)としてそのまま使える
- **Memory接続点**: `memory_boundary.py`はそのままでは実Memory(Event/Decision Ledger)を読まない(seed_contextによる静的スナップショットのみ)。実接続には、`MemoryBoundary`が受け取る`seed_context`を実際のEvent/Decision Ledgerから構築する変換層が別途必要
- **Orchestra/Relay接続点**: 現状どちらも対応するコードが存在しない。P2-02のOrchestra/Relay Adapter Contractがそのまま設計の出発点になる

---

## 5. 「これ以上Runtime層を増やす必要があるか」の判断

**判断: 現時点で汎用的なRuntime基盤層をこれ以上増やす必要はない。**

理由:

- Controller Core(状態制御)・Event Runtime(証拠化)・Adapter Runtime(汎用入力境界)・Memory Boundary(読み取り境界)という4つの基盤要素は、それぞれ単一責務・一方向依存・242テストで裏付けられた形で確立されている
- これ以上「汎用境界」を追加しても、既存4要素のいずれかの責務と重複するリスクが高く、「部品を増やすこと」自体が目的化する懸念(ご指摘の通り)と合致する

**次に必要なのは、汎用Runtime層の追加ではなく、Module接続(MoCKA/Memory/Orchestra/Relayとの実結線)である。** ただし実接続はPhase Vの当初境界(Module本接続は対象外、`PHI_RUNTIME_IMPLEMENTATION_EXECUTION_PLAN_v1.0.md`§4・§5)を超える工程であるため、着手する場合は新たなHuman Gate判断(Phase V終了・Phase VI開始相当の区切り)を要する。

**もう一つの選択肢**: Module接続に進む前に、Gap-001(REJECTED状態不足)を解消するかどうかを判断する。現在の状態モデル(S07)はHuman Gate Approve/Request More Evidenceの2経路のみを正式サポートしており、Reject経路は依然として未定義のままである。Module接続(特にHuman Gate Interfaceの実接続)に進む場合、この未定義のままでは真のHuman Gate実装が完結しない可能性が高い。

---

## 6. 総括

| 観点 | 評価 |
|---|---|
| 設計思想との整合性 | 良好(既存境界を書き換えず、責務分離を維持) |
| 依存関係の一方向性 | Confirmed(循環依存なし、grep実測済み) |
| テストによるEvidence | 良好(242/242 PASS、Regressionなし) |
| IV-01計画との一致度 | 部分乖離(汎用境界優先のボトムアップ実装、記録済み) |
| 追加すべきRuntime層 | なし |
| 次工程 | Module接続(MoCKA優先を推奨)、またはGap-001解消の判断 |

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md
**Status:** REVIEW
**Created:** 2026-07-29
**Origin:** V-01〜V-05の継続実装を受け、次の実装着手前にArchitecture全体を俯瞰するレビューとして作成された。
**Parent Documents:** Phase V全文書・実装(V-01〜V-05)、PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md(IV-01)
**Derived From:** 実コード(controller_core.py/event_runtime.py/adapter_runtime.py/memory_boundary.py)の直接検証
**Supersedes:** なし
**Reason For Creation:** 「部品を増やすこと」が目的化するのを防ぐため、既存Runtime層の責務・依存関係・当初計画との整合性を再確認し、次工程(Module接続かGap解消か)を判断するため。
**Affected Components:** Phase V全Runtime Component
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。責務再確認、依存関係実測確認、IV-01計画との照合(乖離の記録)、Module接続位置評価、Runtime層追加要否判断(不要)、総括を記載。実装・Decision Ledger登録は無し。

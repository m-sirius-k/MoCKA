# MoCKA 2.0 ARCHITECTURE DOCUMENT v1.0（確定版）

## 0. ステータス

- **本書のステータス**: 基準仕様（Baseline Specification）として確定。
- **変更ルール**: 以降この構造は「変更前提」ではない。変更が必要な場合は本書に対する**差分提案方式**（DIFF PROPOSAL）でのみ行う。差分提案は必ず `mocka_write_event` で記録し、Human Gate承認を経ること。
- **位置づけ**: MoCKA 1.0（Phase 1〜7・Event駆動・実行/検証/監査の閉ループ・Governance Intelligence Layer）は完成状態として保持。本書はその上に成立する**世代交代後の上位アーキテクチャ**を定義する。

## 1. 前提：中心の切り替え

| 項目 | MoCKA 1.0 | MoCKA 2.0 |
|---|---|---|
| 中心 | Event | Intent |
| 評価 | 正誤 | 意味整合 |
| Drift | 逸脱 | 意味変化 |
| Audit | 検証 | 解釈 |
| ゴール | 安定運用 | 自己進化 |

MoCKA 1.0は「実行・検証・監査の閉ループを持つEvent駆動システム」である。
MoCKA 2.0は「システム」ではなく「認知構造」であり、実行中心から意味中心へ移行する。データ処理ではなく「意図生成と追跡」が主目的となる。

## 2. 4層アーキテクチャ（Layer 0〜3）

### Layer 0：Physical Execution Layer（実行層）

- Event ingestion
- Runtime execution
- Engine processing
- Commit

1.0のコアをそのまま保持し、変更は最小限とする。

### Layer 1：Verification & Constraint Layer（制約層）

- Validation Engine
- Compliance Model
- Audit System
- Traceability Graph

「正しいかどうか」を担保する層。2.0において**必須**の安全装置であり、Layer 3の暴走（後述）を抑制する唯一の層である。

### Layer 2：Governance Intelligence Layer（意味層）

- Decision Reason Graph
- Drift Semantics Engine
- REQ Change History with Intent
- Policy evolution tracking

「なぜそうなったか」を保持する層。1.0で追加済みのGovernance Intelligence Layerを継承・拡張する。

### Layer 3：Cognitive Governance Layer（新規・本体）

MoCKA 2.0の本体。機能は以下：

- 意図の生成（Intent Synthesis）
- 意図の競合解消（Intent Conflict Resolution）
- システム全体の意味圧縮（Semantic Compression）
- 長期的設計方向の生成（Design Drift Projection）

「何をすべきかを作る層」。

## 3. 設計原則（P1〜P4）

- **P1：意図はすべての上位構造である**
  Eventより上にIntentを置く。すべてのEventは何らかのIntentに紐づく（または紐づけ候補として保留される）。

- **P2：構造は意味の圧縮である**
  ログ（生イベント列）ではなく「意味グラフ」を保持する。記録の量ではなく、記録間の意味関係を一次データとする。

- **P3：システムは自己修正ではなく自己再定義する**
  「修正」ではなく「再設計」へ。Layer 3が生成する変更提案は、既存構造へのパッチではなく、構造そのものの再定義として扱う（ただし発効はLayer 1の制約を通過した場合のみ）。

- **P4：意図の生成は制約の外で起きてはならない**
  Layer 3が生成・解消するすべてのIntentは、Layer 1（Constraint）を経由してのみ実行・記録に反映される。Layer 3はLayer 1をバイパスする経路を持たない。
  （P1〜P3はくろこ指示に明記された原則。P4は§5の危険領域に対する直接対応として、Layer構成上必須の原則として本書に追加する。）

## 4. システムフロー

```
Intent → Constraint → Execution → Reason Graph
```

1. **Intent**（Layer 3）: Intent Synthesisにより意図が生成・更新される。既存Intentとの競合がある場合はConflict Resolutionを経る。
2. **Constraint**（Layer 1）: 生成されたIntentはValidation Engine / Compliance Modelによって検証される。Traceability Graphへの登録もここで行う。
3. **Execution**（Layer 0）: 検証を通過したIntentに基づき、Event ingestion・Runtime execution・Engine processing・Commitが実行される。
4. **Reason Graph**（Layer 2）: 実行結果はDecision Reason Graphに反映され、Drift Semantics EngineおよびPolicy evolution trackingにより意味変化が追跡される。その結果はLayer 3のSemantic Compression / Design Drift Projectionへフィードバックされる。

この4段は単方向の閉鎖ループではなく、Reason GraphからIntentへのフィードバックを含む循環構造である。

## 5. 危険領域とその対応

このフェーズで必ず出る問題：

- Intentの過剰生成（ノイズ化）
- 意味グラフの発散
- 「正しさ」と「意図」の衝突
- システムが自己正当化に陥るリスク

**対応**: Layer 1（Constraint）は必須であり、上記すべての問題に対する最終防衛線として機能する。P4により、Layer 3はLayer 1を経由しない限り実行系・記録系に影響を与えられない。

## 6. 非機能要件

- **可観測性（Observability）**: Layer 3が生成するIntent・Conflict Resolutionの判断過程は、Layer 2のDecision Reason Graphから常に追跡可能でなければならない。「なぜそのIntentが生成されたか」が事後に説明できること。
- **再構成性（Reconfigurability）**: P3に基づき、構造の再定義提案はLayer 1を通過するまで「提案」状態に留まり、既存の実行系（Layer 0）に影響を与えない。再定義の発効・撤回は両方が可能であること。
- **拡張性（Extensibility）**: Layer 0（1.0コア）への変更を最小化したまま、Layer 1〜3を独立に拡張できること。Layer間の依存はフロー（§4）で定義された方向のみとする。
- **安定性（Stability）**: Intentの過剰生成・意味グラフの発散（§5）に対し、Layer 1での検証通過率・Conflict Resolution頻度等を監視可能な指標として持つこと（具体的指標はLayer 1/2の実装フェーズで定義する）。

## 7. 1.0との関係

- 1.0（Phase 1〜7）は完成状態として凍結・保持する。
- Layer 0は1.0コアの再利用であり、書き換えは行わない（変更最小）。
- Layer 1〜2は1.0で確立済みの検証・Governance Intelligence Layerを基盤として拡張する。
- Layer 3が新規追加分であり、MoCKA 2.0の本体である。

## 8. 次フェーズへの接続

本書（ARCHITECTURE_MOCKA_2_0_v1.md）の確定をもって、Layer 3の最小データ構造定義（INTENT_SCHEMA_v1.md）の設計に移行する。実装順序は以下の通り：

1. Intent Schema定義（intent object structure / priority / origin / stability）
2. Intent Graph構築（Event → Intent mapping / Decision back-propagation）
3. Semantic Drift Engine（意味変化検出・REQとの差分ではなく「意図差分」）
4. Cognitive Governance Layer prototype（初期はルールベース、後に学習化）

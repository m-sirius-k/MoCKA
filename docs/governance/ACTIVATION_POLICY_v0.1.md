# Knowledge Activation Policy v0.1

位置づけ：[MOCKA_THOUGHT_EVOLUTION_v0.1.md](MOCKA_THOUGHT_EVOLUTION_v0.1.md)で示された思想、およびTODO_395で確定したKnowledge Activation Architecture v0.4を実際に運用するための構成データ。Agent内部に埋め込まれたロジックではなく、参照可能・監査可能・差分追跡可能な外部ファイルとして管理する（v0.4実装引き継ぎノート①に基づく）。

本ファイルはコードではなく運用ポリシーである。固定仕様（Architecture Contract/LOCKED）ではなく、運用実績に基づき随時見直す前提とする（v0.4での位置づけ変更に基づく）。

## 1. Activation Policy（いつ参照するか）

Knowledge Activation Architecture v0.4の段階2に対応する。

- セッション開始時（起動プロトコル、CLAUDE.md記載）
- 判断分岐点でevent_gate通過前
- ファイル変更前（TODO_154）
- 矛盾検知時（外部メモと一次データの不一致等）

## 2. Reason Unit生成条件（初期値）

Knowledge Activation Architecture v0.4の段階9→10の遷移に対応する。Decision Evidenceが発生するたびに無条件でReason Unit化するとjudgement_reasonがノイズで埋まるため、以下のいずれかを満たす場合のみ生成する。

1. Tension発生時：Decisionの過程で既存Knowledge Assets間に矛盾・緊張（tension）が検出された場合
2. Human Gate通過時：human_gateで人間承認を要した判断
3. Reference Selectionが既存Reason Assetsを上書き・否定した場合
4. きむら博士の明示指定

これは初期値であり、運用実績に基づき本ファイルの改訂として随時見直す（固定仕様ではなく運用ポリシーとして扱う）。

## 3. Review Gate 実装方針（決定事項）

Knowledge Activation Architecture v0.4で新設されたReview Gate（Reason Unit→Knowledge Assets昇格の審査点）について、以下の方針を採用する。

**決定：既存の`phi_os/human_gate.py`との統合を採用する（別立てのGateは新設しない）。**

### 決定理由

1. TODO_364で確立した先例（git安全コミット操作を個別実装せず共有ヘルパーへ一元化した方針）と整合する。Review Gateも新規の並走する仕組みではなく、既存の人間承認機構に統合することで、将来の実装漏れリスクを構造的に防ぐ。
2. `human_gate`は既に「人間承認が必要な判断の停止点」として実装済みである。Reason Unit→Knowledge Assets昇格は、まさにこの性質の判断点に該当する。
3. 別立てにすると、TODO_391の資産棚卸しで確認された「event_gateが全イベントの単一受付点」という既存原則と矛盾する新しい経路が増えることになる。

### 実装注記（未実装・TODO_393-B以降の課題）

既存`human_gate`のスキーマは、Reason Unit昇格審査専用のフィールド（既存Reason Assetsとの矛盾チェック結果、昇格可否の理由等）を持たない。統合実装にあたっては`phi_os/human_gate.py`のスキーマ拡張が必要になる見込みだが、本ファイルは方針決定のみを行い、拡張実装そのものは別途の実装作業として切り出す。

## 4. 改訂履歴

- v0.1（2026-06-30）：TODO_393（再開版）に基づき新規作成。TODO_395 v0.4の実装引き継ぎノートを反映。

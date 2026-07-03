# Evolution Layer Specification v0.1

位置づけ: 博士指示（2026-07-03、Task-O）に基づき新規作成。外部知識（論文・OSS・他AIフレームワークの設計等）をMoCKAの制度として取り込む流れを、Observe→Compare→Evidence→Experiment→Institution→Review→Retireの7段階として正式化する。

本ファイルは、本日先行して作成した`docs\governance\EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`（Task-D、5条件と3段階判定プロセス）を、より詳細な7段階のパイプラインとして再構成し、既存のTIC（Technology Intelligence Caliber）構造・Knowledge Activation Policyとの対応関係を明確にするものである。実装は一切含まない。新規のコード調査は行わず、既存文書の再構成である。

---

## 第1部: 現状把握

### 1.1 既存の関連構造

- `EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`（Task-D）: 5条件（採用/保留/実験/不採用/将来再評価）と3段階判定プロセス（くろこ一次分類→TIC Sandbox相当検証→Human Gate最終確認）
- TIC（Technology Intelligence Caliber）: 過去のイベント記録（E20260601_011）で「4層構造：Watch/Sandbox/Impact/Health/Adoption/Archive」として設計。現状Layer0（health_check.py）・Layer1（tech_watcher.py v3.0）は稼働中、Layer2（Sandbox、TODO_205）・Layer3（impact_analyzer.py、TODO_206）・Layer4（Human Gate UI、TODO_207）は未着手
- `ACTIVATION_POLICY_v0.1.md`: Reason Unit生成→Knowledge Assets昇格（Review Gate、human_gate.pyとの統合方針は決定済みだが未実装）
- 前例パターン: Execution Runtime Systemの「新機能は別ブランチで開発する」原則、Task Orchestrator Layerの「外付け・未接続」実装（既存frozen構造を変更せず単体モジュールとして追加）

### 1.2 7段階と既存構造の対応関係（概観）

| 段階 | 対応する既存機構 | 現状 |
|---|---|---|
| Observe | TIC Layer0-1（health_check.py、tech_watcher.py） | 稼働中 |
| Compare | TIC Layer3（impact_analyzer.py）、Task-D Step1（くろこ一次分類） | Layer3未着手、Task-D側は制度定義済み |
| Evidence | Task-D Step1の根拠明示要件、TIC health_log | 制度定義済み（Task-D）／稼働中（health_log） |
| Experiment | TIC Layer2（Sandbox） | 未着手 |
| Institution | Task-D Step3（Human Gate確定）→Knowledge Assets化 | 制度定義済みだが接続に穴あり（`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`参照） |
| Review | Knowledge Activation Policyの見直し前提、Decision Policyの再評価 | 制度定義済み（運用実績に基づき随時見直す、という原則のみ） |
| Retire | TIC Archive層、MODULE_LIFECYCLEのARCHIVED状態 | TIC Archive未実装、MODULE_LIFECYCLEは別対象（モジュール）向けの仕組み |

---

## 第2部: 提案 — 7段階仕様

### 2.1 Observe（観測）

- **目的:** 外部の技術動向・論文・OSS・他AIフレームワークの設計変化を継続的に把握する
- **入力:** 外部情報源（技術ニュース、論文、GitHubリポジトリ等）
- **出力:** 観測記録（何が・いつ・どこで変化したか）
- **対応する既存機構:** TIC Layer0（health_check.py、7点モーニングチェック）・Layer1（tech_watcher.py v3.0、意味差分検知）
- **現状:** 稼働中
- **未実装部分:** なし（この段階は既に機能している）

### 2.2 Compare（比較）

- **目的:** 観測された外部知見を、MoCKAの既存制度・既存機構と比較し、重複・矛盾・補完関係を洗い出す
- **入力:** Observe段階の観測記録
- **出力:** 比較結果（既存の何と重複するか、既存の恒久ルールと矛盾しないか）
- **対応する既存機構:** TIC Layer3（impact_analyzer.py、依存マップ・影響範囲の自動洗い出し）、`EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`Step1のくろこ一次分類（5条件への当てはめ）
- **現状:** TIC Layer3は未着手（TODO_206）。Task-D側のStep1は制度として定義済みで、本日複数回実際に運用された（Task-A〜Cへの適用例）
- **未実装部分:** impact_analyzer.pyによる機械的な依存マップ生成。現状はくろこ（AI）が手動で既存文書を比較する形で代替している

### 2.3 Evidence（根拠）

- **目的:** Compare段階の結果を裏付ける具体的根拠（引用元・ファイルパス・実測値等）を明示する
- **入力:** Compare段階の比較結果
- **出力:** 根拠付きの評価（不確かな点は「不明・要確認」と明記）
- **対応する既存機構:** `EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`が求める「提案には必ず根拠を添える」という制約、TIC health_log.jsonl
- **現状:** 制度として定義済み。本日の一連の監査（Concept Audit等）でもこの原則を踏襲している
- **未実装部分:** なし（運用原則として既に機能している）

### 2.4 Experiment（実験）

- **目的:** 恒久構造（Human Gate・GL7・単一ルート規則等）を変更せず、隔離された場所で外部知見を試行する
- **入力:** Evidence段階までで「実験対象」に分類された知見
- **出力:** 実験結果（効果測定、副作用の有無）
- **対応する既存機構:** TIC Layer2（Sandbox）、前例パターン（Execution Runtime Systemの別ブランチ開発、Task Orchestrator Layerの外付け未接続実装）
- **現状:** TIC Layer2は未着手（TODO_205）。前例パターンとしての運用（別ブランチ・外付けモジュール）は過去に実績があるが、TIC専用のSandbox機構としては存在しない
- **未実装部分:** TIC Layer2そのもの。現状「実験対象」に分類された知見は、都度アドホックに前例パターンを踏襲する形になっており、統一されたSandbox環境はない

### 2.5 Institution（制度化）

- **目的:** 実験を経て採用が確定した知見を、正式な制度（TODO登録、ポリシー文書、コード実装）として組み込む
- **入力:** Experiment段階の結果、またはExperimentを経ずに直接「採用」判定された知見
- **出力:** 正式なTODO登録（PHL経由）、制度文書の更新
- **対応する既存機構:** `EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md`Step3（Human Gateによる最終確認）→Step4（記録）、`ACTIVATION_POLICY_v0.1.md`のKnowledge Assets昇格（Review Gate、human_gate.pyとの統合方針決定済み）
- **現状:** 制度としての手順は定義済みだが、`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`で指摘した通り、Review Gateの実装自体は未着手（TODO_393-B以降の課題）
- **未実装部分:** Review Gateのスキーマ拡張実装（human_gate.py側）

### 2.6 Review（再評価）

- **目的:** 制度化された知見が、時間の経過・運用実績によって妥当性を失っていないかを定期的に見直す
- **入力:** 制度化済みの知見（Knowledge Assets、ポリシー文書）
- **出力:** 見直し結果（継続/修正/廃止の判断）
- **対応する既存機構:** `ACTIVATION_POLICY_v0.1.md`・`DECISION_POLICY_v0.1.md`共通の「固定仕様ではなく運用実績に基づき随時見直す」という位置づけ
- **現状:** 見直すという原則は明文化されているが、「いつ・誰が・どの頻度で」見直すかという具体的なPeriodic Reviewの仕組みは確定していない（今回の一連のTask群の成果物すべてがv1.0を名乗らずv0.1に留めている理由そのものが、このPeriodic Review未確定にある）
- **未実装部分:** 定期見直しのトリガー・頻度・実施者を定めるPeriodic Reviewの仕組みそのもの

### 2.7 Retire（廃止）

- **目的:** 妥当性を失った、または上位互換に置き換えられた知見を、正式に廃止し記録として保管する
- **入力:** Review段階で「廃止」と判断された知見
- **出力:** 廃止記録（いつ・なぜ廃止されたかを含む）、Archiveへの移動
- **対応する既存機構:** TIC Archive層（採用判定後の保管）、MODULE_LIFECYCLEのARCHIVED状態（ただしこれはモジュール向けの仕組みであり、知見・制度の廃止とは対象が異なる）、通常TODOのstatus「廃止」
- **現状:** TIC Archive層は未実装。通常TODOの「廃止」ステータスは既存の5値の一つとして運用されている
- **未実装部分:** 外部知見の採用履歴を専用に保管するArchive機構。現状は通常TODOの「廃止」ステータスで代替せざるを得ない

---

## 第3部: 7段階全体の評価

7段階のうち、実際に稼働しているのはObserve（TIC Layer0-1）とEvidence（運用原則として）のみである。Compare・Experiment・Retireの3段階は、対応するTIC層（Layer2/Layer3/Archive）がいずれも未実装であり、Institution段階もReview Gateの実装待ちという状態にある。Review段階は原則のみで具体的な仕組みがない。

これを`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`の4段階モデル（宣言→接続→実装→検証）に当てはめると、Evolution Layer全体は多くの段階が「宣言」〜「接続方針決定」に留まっており、実装まで到達しているのはObserveのみという評価になる。

---

## 第4部: 未確定事項

- TIC Layer2-4（Sandbox/Impact/Adoption）の未着手状態は、今回新たに確認したものではなく既存のTODO_205/206/207としてすでに認識されている事実である
- Retire段階に対応する専用のArchive機構は現状存在せず、通常TODOの「廃止」ステータスで代替する以外の選択肢が明確でない。この点は今後の設計課題として残る
- Review段階のPeriodic Reviewの仕組みは、本日作成したすべてのv0.1文書に共通する未確定事項であり、Task-O固有の課題ではなく全体に横断する課題である

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Oに基づき新規作成。

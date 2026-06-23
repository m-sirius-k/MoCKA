# Explanation Builder Contract v1 (Phase7-A-3)

Status: DRAFT (Phase7-A-3。コードは最小スケルトンのみ。実データ接続は未着手)
Date: 2026-06-23

本文書は [meaning_query_engine_contract_v1.md](meaning_query_engine_contract_v1.md)
の3.3節（explanation generation）を土台に、explanation_builderの責務を
"Meaning Reconstruction Layer" として再定義する。Time OS Contract v1
（FROZEN）・Meaning Query Engine Contract v1（依存方向確定済み）は本文書
によって変更されない。

## 0. 再定義（重要）

explanation_builderは単なる説明文生成器ではない。

```
入力はある（canonical / intent / trace_path）
分解はある（cluster構造 / decision_trace）
しかし意味として再構築されていない
```

explanation_builderの責務は、この「分解されたものを意味として
再構築する」ことである。これを **Meaning Reconstruction Layer** と呼ぶ。

## 1. 入力（Meaning Reconstruction Model）

| 入力 | 出自 | 必須/任意 |
|---|---|---|
| `canonical` | canonical_search結果（CanonicalSearchResult） | 必須（主軸。契約v1 3.3節「入力主軸」） |
| `intent` | intent_search結果（IntentSearchResult、anchor経由） | 任意。無い場合は意味場の文脈情報なしで再構築する |
| `trace_path` | decision_traceの経路（cluster生成・mergeに至った決定列） | 必須（無ければreconstructionは行えず`INSUFFICIENT_TRACE`を返す） |

`canonical`が存在しない（`found=False`）場合、explanation_builderは
呼び出し不可（契約v1 3.3節の主軸固定ルールを継承）。

## 2. 出力（4要素・固定順）

1. **why_this_meaning** — なぜこの意味（cluster）として確定したか。
   trace_pathの決定列から導く理由テキスト。
2. **activated_structures** — どの構造（既存cluster内のどのサブ構造・
   どのintentとの一致点）が活性化したか。intentが無い場合は空集合。
3. **compression_process** — 個々のeventからclusterへ至る意味圧縮の
   過程（trace_pathの段階列、要約形）。
4. **final_judgement** — 上記3要素を統合した最終判断テキスト
   （「このclusterである理由」の一文要約）。

4要素は常にこの順で返す。一部が算出不能な場合は省略せず、
該当フィールドに理由付きの空値（例: `"reason": "no_intent_provided"`）
を入れる。

## 3. canonical × intent 統合規則（確定）

- **canonicalが主軸、intentは補強情報。** intentが無くてもexplanation
  生成は可能（`activated_structures`が空集合になるのみ）。intentのみ
  でcanonicalが無い状態からの生成は不可（契約v1 3.3節の継承）。
- intentが複数cluster参照を持つ場合、`activated_structures`には
  **canonicalのcluster_idと一致するものだけ**を採用する。canonicalと
  無関係なintent参照は採用しない（intent側のnoise除去）。
- 統合は読み取りのみで行う。cluster再計算・embedding再生成・
  decision_traceの改変はいずれも禁止（meaning_query_engine_contract_v1.md
  4章を継承）。

## 4. 絶対禁止 / 許可（継承・再確認）

禁止:
- PHI-OSへの書き込み
- cluster再計算・embedding再生成
- decision_traceの再実行・改変
- 4要素の順序変更・省略（算出不能時も空値で明示すること）

許可:
- 既存trace_path・既存intent結果・既存canonical結果の読み取りのみ
- 出力テキストの生成（reasoning summaryとしての要約のみ、新規事実の創出ではない）

## 5. ClusterReader実データ接続を見送る理由（設計判断の記録）

Phase7-A-2スケルトン完了時点でClusterReaderは抽象のままとした。
理由は「意味の形（本契約が定義する4要素の出力構造）が確定する前に
データ層へ降りると、後から意味の形を変えられなくなる」という設計
判断によるもの。本契約（Phase7-A-3）でMeaning Reconstruction Modelの
形を固定したのちに、ClusterReader/TraceReaderの具象実装に着手する
順序を維持する。

## 6. 段階実装フロー（更新）

1. Phase7-A-1: Meaning Query Engine契約（完了）
2. Phase7-A-2: meaning_query_engine.pyスケルトン（完了、ClusterReaderは抽象のまま）
3. **Phase7-A-3（本文書 + 最小スケルトン）**: explanation_builder契約 + 4要素出力のスケルトン。実データ接続なし。
4. Phase7-A-4（未着手・要承認）: ClusterReader/TraceReaderの具象実装（実データ接続）

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

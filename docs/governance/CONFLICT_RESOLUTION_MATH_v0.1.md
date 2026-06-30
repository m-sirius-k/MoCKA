# Conflict Resolution Math Closure v0.2

適用範囲: TODO_400（conflict_resolution_order設計、completed）の構造設計の上に乗る「数理閉包」設計。TODO_400本体への変更は行わない。Decision Policy Series（399→400→401→404→405→本文書）の理論的完成にあたる。

本ファイルはコードではなく設計文書である。実装（コード化）は本TODOの範囲外。

## 前提: TODO_400で確定した構造（変更禁止）

```
evaluation_vector(candidate) = (decision_effect_rank, -confidence, authority_rank, -created_at)
比較方式: 辞書式順序（lexicographic order）
override_resolution: 0件=none / 1件=単独採用 / N件=上位者採用 / tie=全員却下+escalate
implicit_conflict_confidence_margin: 0.3（初期値）
```

本文書はこの確定構造の「中身の関数」を定義する。枠組みは変えない。

---

## 1. confidence definition closure（①）

### 1-1. confidenceの定義

confidence（確信度）は、あるKnowledge Assetが「その主張する知識が正しく、当該文脈に適用可能である」という制度的根拠の強さを表す値である。

```
confidence: float, 範囲 [0.00, 1.00]（小数点以下2桁、0.01刻み）
```

confidence は「AIが推定した正確さ」ではなく「制度的根拠の厚さ」である。この区別は MoCKA の「AIを信じるな、システムで縛れ」原則に基づく。

### 1-2. 算出主体と付与プロセス

```
算出主体: Review Gate（human_gate.py / gate_type="review_gate"）の承認者（きむら博士）
付与タイミング: Review Gate承認時（approve_promotion）
```

具体的なプロセス:
1. くろこがReason Unitの昇格申請時に confidence_proposal（提案値）を付与する
2. Review Gate承認時に、承認者（きむら博士）が confidence_proposal を受理または上書きして確定する
3. 確定した値が knowledge_asset_events.activation_metadata.confidence として記録される

```json
{
  "confidence_assignment": {
    "proposer": "くろこ（AI）",
    "proposal_field": "confidence_proposal",
    "authority": "きむら博士（Review Gate承認者）",
    "final_field": "activation_metadata.confidence",
    "timing": "approve_promotion() 実行時"
  }
}
```

### 1-3. confidence_proposal の算出根拠（AIが提案する際の基準）

くろこが confidence_proposal を提案する際の根拠スコアリング（初期値・運用で調整）:

| 根拠の種類 | 加点 |
|---|---|
| 複数の独立したイベントで同一パターンが観測された | +0.30 |
| 人間（きむら博士）が明示的に言語化・確認した | +0.40 |
| 単一イベントのみ（再現未確認） | +0.10 |
| 推測・類推のみ（直接的証拠なし） | +0.05 |
| 既存Knowledge Assetと整合（矛盾なし確認済み） | +0.15 |
| 既存Knowledge Assetと部分的に矛盾あり | -0.10 |

合計を [0.00, 1.00] にクランプして提案値とする。承認者は提案値を参考として最終値を自由に設定できる。

### 1-4. 設計判断の根拠

「機械的な算出式（テキスト類似度等）」ではなく「人間が最終確定する制度的根拠」を採用した理由:
- confidence の誤った高値が conflict_resolution_order に直接影響するため、AIの自己申告に依存する設計はGL7-UNENFORCED-CONDITIONS-BUGと同型のリスクを持つ
- 現状の運用規模（個人開発者+くろこ）では人間が全件承認する設計が現実的かつ安全

---

## 2. ranking integration function（②）

### 2-1. 評価ベクトルの厳密形

```
V(a) = (d(a), -c(a), r(a), -t(a))
```

| 記号 | 意味 | 型 | 比較方向 |
|---|---|---|---|
| d(a) | decision_effect_rank: 候補aの判断への作用効果のランク | int, 定義値は2-3参照 | 小さいほど優先 |
| c(a) | confidence: 候補aの確信度 | float [0.00, 1.00] | 大きいほど優先（-c として反転） |
| r(a) | authority_rank: 候補aの知識源権威ランク | int, 定義値は2-4参照 | 小さいほど優先 |
| t(a) | created_at: 候補aの登録タイムスタンプ | Unix timestamp (int) | 新しいほど優先（-t として反転） |

### 2-2. 辞書式順序による比較関数の厳密形

候補 a が候補 b より優先される条件:

```
rank(a) < rank(b)

定義:
rank(a) < rank(b)
  iff d(a) < d(b)
  or (d(a) = d(b) and -c(a) < -c(b))
  or (d(a) = d(b) and c(a) = c(b) and r(a) < r(b))
  or (d(a) = d(b) and c(a) = c(b) and r(a) = r(b) and -t(a) < -t(b))
```

Python実装イメージ（設計参考・実装は範囲外）:
```python
def evaluation_key(candidate):
    return (
        candidate.decision_effect_rank,
        -candidate.confidence,
        candidate.authority_rank,
        -candidate.created_at_unix
    )

sorted_candidates = sorted(candidates, key=evaluation_key)
```

### 2-3. decision_effect_rankの定義値

| 値 | ラベル | 意味 |
|---|---|---|
| 1 | PROHIBIT | この候補を選べば禁止条件に抵触する（最高優先で排除） |
| 2 | REQUIRE | この候補が必須条件を満たす唯一の選択肢 |
| 3 | PREFER | 条件を満たす候補の中で優先するべきもの |
| 4 | NEUTRAL | 特記事項なし（デフォルト） |
| 5 | DISCOURAGE | 他に選択肢があれば避けるべきもの |

注: PROHIBIT（1）は「この候補が選ばれると問題が起きる」ではなく「この候補を優先して排除すべき」を意味する。rank=1が最優先で処理されるため、PROHIBIT候補は最初に除外対象として確認される。

### 2-4. authority_rankの定義値

| 値 | ラベル | 意味 |
|---|---|---|
| 1 | CONSTITUTION | MoCKA憲法・不変の設計原則 |
| 2 | GOVERNANCE_DOCUMENT | docs/governance/配下の確定ガバナンス文書 |
| 3 | COMPLETED_TODO | completed済みTODOのnote（設計確定記録） |
| 4 | EVENT_RECORD | events.dbの記録（実績・インシデント） |
| 5 | AI_PROPOSAL | AIが提案した未承認の知識 |

注（将来拡張）: EVENT_RECORD は現状粗い分類のままでよい。将来 event_source に基づき Human Event / System Event / AI Event へのサブ分類を追加することがあっても、authority_rank 自体の5段階構造は変更不要である。サブ分類は authority_rank=4 の内部属性として扱う。

---

## 3. evaluation vector normalization（③）

### 3-1. 正規化の必要性判定

TODO_400で採用した辞書式順序は「各要素を独立した次元として順番に比較する」方式であり、要素間のスケール差は比較には影響しない（重み付き合成スコアではないため）。

したがって「要素間の正規化」は不要である。ただし「要素内の正規化」（各要素の値が一貫した基準で付与されていること）は必要である。

### 3-2. 要素内の値範囲・制約

| 要素 | 型 | 許容範囲 | 不正値の扱い |
|---|---|---|---|
| decision_effect_rank | int | {1, 2, 3, 4, 5} | 範囲外はNEUTRAL（4）として扱う |
| confidence | float | [0.00, 1.00]、0.01刻み | 範囲外はクランプ。小数点以下3桁以上は四捨五入 |
| authority_rank | int | {1, 2, 3, 4, 5} | 範囲外はAI_PROPOSAL（5）として扱う |
| created_at | Unix timestamp | 正整数 | 0以下は登録エラーとして拒否 |

### 3-3. confidence の精度統一

confidenceは0.01刻みに正規化する。これは:
- 小数点以下3桁以上の差（0.001等）が実質的に意味を持たない運用規模であること
- implicit_conflict_confidence_margin（0.3）との整合性を保つため

```python
confidence_normalized = round(confidence, 2)  # 0.01刻み
confidence_normalized = max(0.00, min(1.00, confidence_normalized))
```

保存精度と制度精度の分離: confidenceの保存精度は実装依存でよい（0.001刻み等で保存することを禁止しない）。ただしDecision Policyで比較するときは制度上定めた精度（現行0.01刻み）へ正規化してから比較する。この分離により、保存精度を0.001等に変更しても本設計の制度変更にはならない。

---

## 4. deterministic tie-break system（④）

### 4-1. tie-breakが発生する条件

全ての比較軸が一致した場合:
```
d(a) = d(b) AND c(a) = c(b) AND r(a) = r(b) AND t(a) = t(b)
```

created_atが一致するケースは（同秒登録等で）稀だが排除できない。

### 4-2. tie-break規則

**一次tie-break: knowledge_key の辞書順（昇順）**

```
tie_break_key(a) = a.knowledge_key  # 人間可読な論理キー（文字列）
```

knowledge_keyは登録時に一意であることが保証されているため（Knowledge Asset登録ルール）、2候補が同一knowledge_keyを持つことはない。

- アルファベット順（Python標準の文字列比較・lexicographic）
- 大文字・小文字は区別しない（lower()正規化後に比較）

```python
def full_sort_key(candidate):
    return (
        candidate.decision_effect_rank,
        -candidate.confidence,
        candidate.authority_rank,
        -candidate.created_at_unix,
        candidate.knowledge_key.lower()  # tie-break
    )
```

### 4-3. tie-breakを「機械的勝者の生成」と見なさない理由

TODO_400の原則「機械的に説明できない勝者を作らない設計」との整合:
- knowledge_key は人間が命名した論理キーであり、その順序は「意味のある優劣」ではない
- tie-breakはあくまで決定論的な順序付けであり、「より優れた」候補を選んでいるわけではない
- この点を運用ルールとして明示する: tie-breakによる勝者はDecision Evidence上に「tie_break: true」フラグを記録し、後から人間が確認・覆せる状態を維持する

### 4-4. 最終tie-break（knowledge_keyも一致した場合）

同一knowledge_keyの候補が複数存在する場合はKnowledge Asset管理上の登録ミスであり、tie-breakではなくデータ整合性エラーとして扱う。escalate_if_needed()を呼び出し、Human Gateへ委ねる。

---

## 5. conflict_resolution_orderへの数学的接続（⑤）

### 5-1. 接続マップ

TODO_400で確定した構造への①〜④の接続位置:

```
detect_conflicts
  detect_explicit_conflicts: confidence は未使用（CONFLICTS_WITH関係は制度的確定・confidence非依存）
  detect_implicit_conflicts: confidence（①で定義） を使用
    -> implicit_conflict の判定: |c(a) - c(b)| >= 0.3 の場合のみ競合とみなす
       （confidence が 0.01刻み（③）で付与されていることが前提）

rank_candidates
  -> evaluation_key() / full_sort_key()（②③④で定義）を使用して候補をソート

apply_policy
  evaluate_override: override_requested フラグの評価のみ（confidence は関与しない）
  resolve_competition: rank_candidates の結果を使用
  finalize_selection: 上位1件を選択

escalate_if_needed
  -> tie-break 後もデータ整合性エラーが残る場合（④-4）に呼び出し
```

### 5-2. 数学的閉包の完成確認

TODO_400の「枠組み」と本文書の「中身」が矛盾なく接続されることを確認:

| TODO_400の構造 | 本文書での定義 | 接続状態 |
|---|---|---|
| evaluation_vector の各要素 | d, c, r, t の定義・型・範囲（②③） | 接続済み |
| 辞書式順序による比較 | 厳密な比較関数 rank() の定義（②） | 接続済み |
| confidence 算出方法は未定義 | ①で算出主体・プロセスを定義 | 接続済み |
| override_requested 複数件: confidence上位者採用 | rank() での c(a) 比較（②）で実現 | 接続済み |
| tie: 全員却下+escalate | ④-4でデータ整合性エラー時のみ escalate | 整合確認 |
| implicit_conflict_confidence_margin: 0.3 | ③の 0.01刻み正規化と整合 | 整合確認 |

### 5-3. 意図的に先送りした事項（v2.0以降）

- decision_effect_rank の動的付与（現在は静的定義値のみ）
- authority_rank の継承ルール（派生Knowledge Assetの権威継承）
- confidence の時間減衰（古い記録の confidence を自動で下げる仕組み）
- tie_break フラグの Human Gate 連携 UI

---

## 6. 評価関数の数学的保証

評価関数 `V(a) = (d(a), -c(a), r(a), -t(a))` に knowledge_key tie-break を加えた全順序関数 `full_sort_key(a)` が以下の4性質を満たすことを確認する。

### 6-1. 反射性（Reflexivity）

```
V(a) = V(a)  （任意の候補 a について）
```

各要素（d, c, r, t）は決定論的に算出された値であり、同一候補を同一条件で評価すれば常に同一ベクトルになる。confidence の 0.01刻み正規化（③）により浮動小数点誤差も排除される。成立。

### 6-2. 推移性（Transitivity）

```
V(a) <= V(b) かつ V(b) <= V(c) ならば V(a) <= V(c)
```

辞書式順序は各次元の全順序（整数比較・float比較・文字列比較）の直積として定義される。各次元の比較が推移的であれば、辞書式順序も推移的になる。d / r は整数比較（推移的）、c は 0.01刻み正規化後の float 比較（推移的）、t は整数比較（推移的）、knowledge_key は文字列比較（推移的）。したがって全体として推移的。成立。

### 6-3. 決定性（Totality / Determinism）

```
任意の2候補 a, b について V(a) <= V(b) または V(b) <= V(a) のいずれか一方が必ず成立する
```

辞書式順序は全ての次元で「等しい」か「どちらかが小さい」かを決定できる。最終次元である knowledge_key は Knowledge Asset 登録時に一意性が保証されており（④-4でデータ整合性エラーとして排除）、同値になることはない。よって全ての候補ペアについて順序が決定される。成立。

### 6-4. 全順序（Total Order）

上記 6-1〜6-3 により、`full_sort_key` は任意の候補集合に対して一意かつ再現可能な全順序を与える。

同一の候補集合に対して同一の入力で `full_sort_key` を適用すれば、常に同一の順序が得られる（決定論的ソート）。これは「機械的に説明できない勝者を作らない」（TODO_400原則）の数学的根拠である。

---

## 7. 成果物ガバナンス（TODO_408適用）

- Artifact Type: Governance Document
- Completion Evidence: .md必須
- Verification Status: Pending（きむら博士承認待ち）
- Evidence Location: C:/Users/sirok/MoCKA/docs/governance/CONFLICT_RESOLUTION_MATH_v0.1.md（v0.2 内部更新）

---

## 7. 改訂履歴

- v0.1（2026-07-01）: TODO_402として新規作成。Decision Policy Series（399→400→401→404→405→本文書）の数理閉包設計 v0.1。TODO_400本体への変更なし。
- v0.2（2026-07-01）: きむら博士レビュー後の3点補足追記。①EVENT_RECORD将来細分化注記（2-4）②confidence保存精度と制度精度の分離（3-3）③評価関数の数学的保証節（6）。構造変更なし・追記のみ。Decision Policy Series 数理閉包完成。

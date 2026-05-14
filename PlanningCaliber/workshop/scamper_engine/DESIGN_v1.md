# SCAMPER Creative Engine
## MoCKA 第三の柱 — 発明する文明への進化

プロジェクト開始: 2026-05-14
起点イベント: E20260514_054
設計者: きむら博士
執行官: Claude

---

## 設計思想

### MoCKAの進化3段階

```
第一段階: 記録する文明
  SPP（沈黙禁止）+ イベントDB + 5W1H
  → 過去に戻れる

第二段階: 予測する文明
  PHL（履歴注入）+ morphology_engine + pattern_library
  → 失敗/成功方向を予測できる

第三段階: 発明する文明  ← ここ
  SCAMPER × 蓄積知識
  → 今まで思いつかなかった解を生成できる
```

### 核心の問い

きむら博士の30年の知識がMoCKAに蓄積されている。
その知識を「記録」「予測」だけでなく「創造」に使えないか？

失敗体験/成功体験を文字分解して組み合わせると
**過去にない解が生まれる**という直感。

---

## SCAMPER 7視点 × MoCKA知識

| 視点 | 問いかけ | MoCKAでの活用 |
|---|---|---|
| S Substitute | 別のもので代替できるか | 失敗パターンの要素を別の解に置換 |
| C Combine | 組み合わせると何が生まれるか | 成功パターン同士を融合 |
| A Adapt | 別分野の解を適用できるか | 制御工学の知識をAI制度に転用 |
| M Modify | 変更・拡大・縮小すると？ | 既存Caliberを改造して新機能 |
| P Put to other uses | 別の使い道はあるか | 失敗記録を設計指針に転用 |
| E Eliminate | 不要なものを削ると？ | 制度の簡素化・本質化 |
| R Reverse | 逆転・再配置すると？ | AIと人間の役割を入れ替える |

---

## アーキテクチャ設計

```
入力: インシデント or 課題テキスト
    ↓
[Layer 1: 分解]
morphology_engine.py で形態素分解
pattern_library.json でパターン照合
失敗/成功ベクトルを算出

    ↓
[Layer 2: SCAMPER問いかけ]
7視点それぞれで問いかけテンプレートを適用
既存パターンとの組み合わせを生成

    ↓
[Layer 3: 候補生成]
「今まで思いつかなかった解」を3〜5件出力
根拠となったパターンIDを紐付け

    ↓
[Layer 4: Human Gate]
きむら博士が選択・修正・却下
選択結果をMoCKAイベントとして記録

    ↓
[Layer 5: 蓄積・進化]
採用された解をsuccess_patternsに追加
次回の創造に活用（自己進化ループ）
```

---

## 既存資産の活用

新規実装はほぼ不要。既存データを創造レイヤーで活用する。

```
morphology_patterns.db  → 分解・照合エンジン（既存）
pattern_library.json    → 101件パターン素材（既存）
danger_patterns.json    → 失敗方向語彙（既存）
success_patterns.json   → 成功方向語彙（既存）
lever_essence.json      → きむら博士思想（既存）
heinrich_engine.py      → 重要度分類（既存）

↓ 新規追加
scamper_engine.py       → 7視点問いかけ生成
scamper_templates.json  → 視点別問いかけテンプレート
scamper_results.db      → 生成結果・採用記録
```

---

## 実装フェーズ

### Phase 1（設計・テンプレート）
- [ ] scamper_templates.json 作成（7視点×問いかけ）
- [ ] 手動テスト（インシデント1件をSCAMPERで展開）
- [ ] 結果をきむら博士に確認

### Phase 2（エンジン実装）
- [ ] scamper_engine.py 実装
- [ ] morphology_engine との接続
- [ ] 候補3〜5件の生成ロジック

### Phase 3（COMMAND CENTER統合）
- [ ] /scamper/generate エンドポイント
- [ ] COMMAND CENTER に創造パネル追加
- [ ] Human Gate との接続

### Phase 4（自己進化ループ）
- [ ] 採用結果のsuccess_patterns自動追加
- [ ] 次回生成への反映確認

---

## 論文展開

SPP/PHLに次ぐ第三の柱として論文化可能。

タイトル案:
「From Recording to Inventing:
 SCAMPER-Based Creative Engine for Accumulated Engineering Knowledge」

主張:
- 30年の失敗/成功体験を構造化記録（MoCKA）
- パターン分解・予測（morphology）
- SCAMPER7視点で創造的組み合わせ
- 人間が思いつかない解を自動生成
- Human Gateで選択・蓄積・進化

---

## 関連イベント

- E20260514_054: プロジェクト立ち上げ着手前記録
- MoCKA設計思想: AIを信じるな、システムで縛れ
- 進化方向: 記録→予測→発明

---

次のアクション: Phase 1 scamper_templates.json作成
担当: Claude（きむら博士承認後）

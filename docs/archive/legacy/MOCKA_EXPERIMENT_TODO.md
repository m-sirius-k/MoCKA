# MoCKA 実験TODO — 論文評価データ収集
# 締切: 2026-05-21 (AoE) / 今日: 2026-04-04 / 残り47日
# 優先度順・1日1実験でも十分間に合う

---

## WEEK 1 (4/5-4/11): Type A 知識復元 残り2件

### [A-2] 短文ログの復元実験
- [ ] events.csvから直近の短いセッション（5000文字以下）を選ぶ
- [ ] run_experiment_A.py を実行（以下のスクリプト）
- [ ] 結果をresults/A2_short_log.json に保存
- [ ] RR（復元率）を記録

### [A-3] 混在ログの復元実験
- [ ] 日本語・英語混在のセッションログを選ぶ
- [ ] run_experiment_A.py を実行
- [ ] 結果をresults/A3_mixed_log.json に保存

---

## WEEK 2 (4/12-4/18): Type B 制約消失検証（OSP）

### [B-1] Claude の制約消失率
- [ ] run_experiment_B.py でバルブシナリオ10問を投入
- [ ] 制約を無視した回答数をカウント
- [ ] results/B1_claude.json に保存

### [B-2] GPT-4 の制約消失率
- [ ] 同じ10問をGPT-4に投入
- [ ] results/B2_gpt4.json に保存

### [B-3] Gemini の制約消失率
- [ ] 同じ10問をGeminiに投入
- [ ] results/B3_gemini.json に保存

---

## WEEK 3 (4/19-4/25): Type C 4AI合議 + Type D 障害耐性

### [C-1] 重み均等での合議精度
- [ ] mocka_orchestra を起動
- [ ] w1=w2=w3=w4=0.25 で10タスク実行
- [ ] results/C1_equal_weight.json に保存

### [C-2] 安全重視
- [ ] w4=0.5, 他0.17 で同じ10タスク
- [ ] results/C2_safety_weight.json に保存

### [C-3] 精度重視
- [ ] w1=0.5, 他0.17 で同じ10タスク
- [ ] results/C3_accuracy_weight.json に保存

### [D-1][D-2][D-3] 障害耐性
- [ ] AI1台停止してshadow起動を確認
- [ ] AI2台停止して継続運転率を記録
- [ ] ネット断シミュレーションで最小動作確認

---

## WEEK 4-6 (4/26-5/17): Type E 再発防止追跡
- [ ] 既知エラーパターンをevents.csvに記録
- [ ] 週次で再発件数を確認（0件が目標）
- [ ] 3週間分のデータを収集

---

## 5/18-5/21: 最終統合
- [ ] 15データセットをSection 4に統合
- [ ] 図表を更新
- [ ] Draft v5 として最終化
- [ ] 提出


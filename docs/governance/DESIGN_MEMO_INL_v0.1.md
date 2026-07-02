# MoCKA Incident Navigation Layer (INL) v0.1 — 設計メモ

**起草**: Claude（制度書記官）
**日付**: 2026-07-02
**初期投入インシデント**: INC-20260702-001（mocka_server IPv6解決障害）

## 1. 位置づけ：既存civilization loopとの関係

MoCKAには既に8段階loop（Observe→Record→**Incident**→**Recurrence**→**Prevention**→
Decision→Action→Audit）が存在する。INLはこれと並行する別システムではなく、
**Incident/Recurrenceステージの内部構造を強化する拡張層**として設計した。

- 従来: Incidentは単票で記録される → 次に同じ症状が起きても「初見処理」になる
- INL後: Incident登録時に分類(Layer2)とリンク(Layer3)が強制される
  → 次回同種の障害は class_registry.json を経由して即座に過去解決策へ到達する

civilization loopのRecurrence段階が「再発検知」を担っていたが、これまでは
検知の仕組み（何が再発か）が構造化されていなかった。INLのclass_id + linksが
Recurrenceステージの実データ基盤になる。

## 2. 3ファイル構成と役割分担

| ファイル | 層 | 役割 |
|---|---|---|
| `incident.json` | Layer 1 | 個別事象の単票。「何が起きたか」 |
| `class_registry.json` | Layer 2/3 | 分類＋階層構造。「意味的にどこに属するか」 |
| `incident_links.json` | 横断 | 個々のincident間の関連。「どの過去事例に繋がるか」 |

Layer2とLayer3を1ファイルに統合した理由: node_idの階層パス
（`ENV_NAME_RESOLUTION_FAULT.localhost_ambiguity.windows_ipv6_fallback`のような
ドット区切り）自体がグラフ構造を表現できるため、GPT案の「Failure Class」と
「Failure Graph」を分けるより単純化できると判断した。

## 3. 強制ルールの実装方法（3.2対応）

| GPT案のルール | v0.1での実装 |
|---|---|
| 単票禁止（class未設定NG） | `incident.json`の`class_id`必須フィールド化。値がclass_registry.json内に存在するか検証する軽量チェッカーを後日追加（今回は手動運用から開始） |
| 類似リンク未設定NG | 同classに既存incidentがあれば`linked_incidents`に最低1件設定を運用ルール化（incident_links.jsonの`_note_for_next_entry`に明記） |
| localhost/127.0.0.1タグ化必須 | `symptom_tags`配列に必ず含める運用。今回のINC-20260702-001で実例済み |

**v0.1では自動検証コードはまだ実装していない**（意図的にスコープ外）。
まずはくろこ側でincident.json手動更新を1〜2件運用してみて、記入の型が
安定してから、mocka_mcp_server.py側にschema validationを追加する
（早すぎる自動化は形式が固まる前の設計変更コストを増やすため）。

## 4. Failure Classの初期taxonomy（4ルート）

1. `ENV_NAME_RESOLUTION_FAULT` — 名前解決の環境依存性（今回のケース）
2. `NETWORK_CONNECTIVITY_FAULT` — 到達性そのもの（ポート閉塞等、未発生）
3. `ROUTER_STATE_DESYNC` — トンネル/ルーティング状態不整合（ngrok絡み、未発生）
4. `OBSERVATION_LAYER_FAILURE` — 観測層自体の誤報（今回のケースは症状面でこれも兼ねる）

**運用上の注意**: 今回のインシデントは`ENV_NAME_RESOLUTION_FAULT`（根本原因）と
`OBSERVATION_LAYER_FAILURE`（症状の見え方）の両方に関連する。v0.1では
`class_id`は1つだけ（根本原因ベースの分類を優先）とし、症状面の重複は
`symptom_tags`側で表現する設計にした。二重classificationを許すと
taxonomyがすぐ複雑化するため。

## 5. 今後の拡張（v0.2以降、今回は未実装）

- class_id存在チェックの自動validation
- 同class内incidentが3件以上溜まった際の子ノード自動分割提案
- incident.json → risk_engineへのフィードバック（同classの再発が
  一定回数を超えたら該当コンポーネントのリスクスコアを自動加点）
- GPT(R01)による定期的なtaxonomy見直しレビュー

## 6. くろこへの実装依頼範囲（分離）

Claude側（本メモ+3ファイル）で設計は完了。くろこ側の作業は：

1. 3ファイルを `MoCKA/data/` 配下の適切な位置に配置
2. 既存のIncident記録フロー（civilization loop の該当箇所）から
   `incident.json`への書き込みを呼び出すよう接続
   （既存のincident記録コードを壊さないよう、まず並行稼働→移行の順を推奨）
3. PHL記録（CHANGE_START/DONE）を通常通り実施

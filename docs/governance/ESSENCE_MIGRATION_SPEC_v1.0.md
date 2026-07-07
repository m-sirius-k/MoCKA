# ESSENCE Canonical Migration Spec v1.0

## 位置づけ

本文書はDC_20260707_019(Human Gate承認、監査官R01=きむら博士)で許可された次工程「Migration Spec作成」
に対応するSpec文書である。ESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.mdで確定したCanonical Essence Model
(Canonical Essence = `interface/lever_essence.json`、Legacy Essence Store = 第3ファイル)を前提に、
app.py側のessence参照をどう整理するかの選択肢を提示する。

**本文書はSpec(設計案)のみであり、app.py・各essenceファイルへの変更は一切行っていない。**
本Specに基づく実装は、Impact Analysis完了後、Human Gateの再承認を経てから着手する(DC_20260707_019準拠)。

## 1. 変更対象

app.py内のessence参照19箇所(ESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.md 1節で棚卸し済み)。
特に以下がMigration対象の中心となる。

| 箇所 | 現状 |
|---|---|
| `ESSENCE_PATH`定義(1478/1680/1769/1836行目) | Legacy Essence Store(第3ファイル)を直接参照 |
| COMMAND CENTER API内`essence_updated`計算(1490-1499行目) | Legacy Essence Storeの`{axis}_updated`のmax値を使用 |
| `/essence/detail`ルート(1833-1841行目) | Legacy Essence Storeの内容をそのまま公開 |
| `/public/essence`ルート(1882-1891行目) | Legacy Essence Storeの内容を無認証で公開(IC_20260707_004) |
| `auto_update_essence_from_mataka()`(724-751行目) | Active Writer。Legacy Essence StoreのINCIDENT軸に追記 |
| `_auto_danger_to_essence()`(2005-2025行目) | Active Writer。Legacy Essence StoreのINCIDENT軸に追記 |
| `run_essence()`(2561-2567行目) | Legacy Writer(`essence_classifier.py`)をsubprocess起動 |

## 2. 現状参照(要約、詳細はESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.md参照)

```
Canonical Essence(events.db essenceテーブル)
    -> essence_auto_updater.py
    -> interface/lever_essence.json(Canonical Essence、承認済み)
    -> export_for_cloudflare.py(一方向)
    -> data/lever_essence.json(Projection、承認済み)

Legacy Essence Store(第3ファイル、承認済み・管理対象化)
    <- app.py: auto_update_essence_from_mataka() [Active Writer]
    <- app.py: _auto_danger_to_essence() [Active Writer]
    <- interface/essence_classifier.py(app.py run_essence()経由) [Legacy Writer]
    <- interface/essence_extractor.py/condenser.py/trigger.py/pipeline.py,
       Essence_Direct_Parser.py, reflux.py [Legacy Writer、自動起動未確認]
    -> app.py: COMMAND CENTER表示、/essence/detail、/public/essence が読取
```

現状の問題: COMMAND CENTER・公開APIが見せる「essence」は、Claude/MCP/Gatewayが見るCanonical Essence
(interface/lever_essence.json、最新)とは別物のLegacy Essence Store(旧チェーンの断片的追記のみ)である。

## 3. 変更候補(4オプション、いずれも未実装)

### Option 1: 最小変更(表示ラベルのみ追加)

ESSENCE_PATHはLegacy Essence Storeのまま変更せず、COMMAND CENTER UI・`/essence/detail`・`/public/essence`
のレスポンスに`"source": "legacy_essence_store"`のような出所ラベルを追加するのみ。Active Writer
(MATAKA/DANGER)の動作は一切変更しない。

- 利点: 変更範囲が最小、Active Writerのロジックに触れないためリスクが低い
- 欠点: 「Living Contextは最新か」という本質的な疑義(Canonical Essenceとの乖離)は解消しない

### Option 2: 表示をCanonical Essence基準に切替え、Legacy Essence Storeは別セクション化(暫定推奨)

COMMAND CENTER APIの`essence_updated`/`essence_axes`/`essence_count`の算出元をCanonical Essence
(`interface/lever_essence.json`、またはevents.db直読み)に切り替える。Legacy Essence Store由来の情報
(MATAKA/DANGER自動追記分)は、レスポンス内に別フィールド(例: `legacy_alert`)として残し、削除はしない。
`/essence/detail`・`/public/essence`も同様に、Canonical Essence(主)とLegacy Essence Store(副、出所明記)
を分けて返す。

- 利点: Living Context疑義の本質的解消。Legacy Essence Storeの情報も失わない(DC_20260707_019の
  「削除禁止」制約を満たす)
- 欠点: レスポンス形式の変更を伴うため、これらのAPIを消費している側(COMMAND CENTER UI/index.html)
  の表示ロジックも合わせて変更が必要になる可能性がある

### Option 3: Adapter層導入(将来Phase候補)

essence読み書きを抽象化したAdapter(例: `interface/essence_adapter.py`)を新設し、app.pyは
Adapter経由でのみessenceにアクセスする。Canonical/Legacyの切替をAdapter内に閉じ込める。

- 利点: 将来Canonical Essenceの実装が変わっても、app.py側の変更が不要になる(保守性向上)
- 欠点: 変更範囲が最も大きい。今回のMigrationの目的(Living Context疑義の解消)に対して過剰投資の可能性

### Option 4: API境界の是正(IC_20260707_004対応、Option 1-3のいずれとも併用可能)

`/public/essence`・`/essence/detail`について、(a)認証(APIキー等)を追加する、または(b)ルート自体を
無効化しCOMMAND CENTER内部専用に限定する、のいずれかを選択する。

- 利点: コード上public・ネットワーク上privateという表現不一致(IC_20260707_004)を解消
- 欠点: (a)は認証機構の新規実装が必要。(b)は既存の外部利用実績があれば影響が出る(現状は
  openapi.yaml未登録・Cloudflare Tunnel未公開のため実利用は無いと推定、ただし断定はできない)

### 暫定推奨

Option 2を基本方針とし、Option 4(b: ルート無効化、または最小限の認証追加)を併せて実施する。
Option 1はOption 2着手前の暫定措置として採用可。Option 3は今回のMigrationスコープ外とし、
将来的にLegacy Essence Store統合/廃止判断(DC_20260707_019で「別途Human Gate」とされた論点)が
具体化した時点で改めて検討する。

## 4. Impact範囲

| 影響対象 | 内容 |
|---|---|
| COMMAND CENTER UI(index.html) | Option 2採用時、`essence_updated`等のレスポンス形式変更に伴い表示ロジックの追随が必要になる可能性 |
| `/essence/detail`・`/public/essence`の外部消費者 | 現状Cloudflare Tunnel非公開・openapi.yaml未登録のため実利用は無いと推定(断定不可、Unknown Writer監査と同様の限界がある) |
| Active Writer(MATAKA/DANGER自動フック) | Option 1/2/4のいずれも書込み先(Legacy Essence Store)自体は変更しないため、動作影響なし |
| Legacy Writer(essence_classifier.py等) | 変更なし。DC_20260707_019の「削除禁止」制約により、呼出ロジック自体も維持する方針 |
| テスト方法 | ローカルでapp.py起動→COMMAND CENTER API(`/api/command-center`等)のレスポンス確認→
`/essence/detail`・`/public/essence`のレスポンス確認→UTF-8検証→(Option 2の場合)index.html側の
表示崩れがないことを確認 |

## 5. 次のHuman Gate確認項目

- [ ] Option 1/2/3/4のうちどれを採用するか(暫定推奨: Option 2 + Option 4)
- [ ] Option 2採用の場合、COMMAND CENTER UI(index.html)側の表示変更も同時に行うか、
      レスポンス形式のみ変更してUI側は追って対応するか
- [ ] `/public/essence`・`/essence/detail`は認証追加(4a)・無効化(4b)・現状維持のいずれとするか
- [ ] Legacy Writer(essence_classifier.py含む)の呼出ロジックは変更せず維持することに同意するか
- [ ] 実装後の検証項目(UTF-8検証・構文検証・COMMAND CENTER実機確認)に合意するか
- [ ] 実装はCHANGE_START→変更→UTF-8検証→CHANGE_DONEの通常プロトコルで進めることに同意するか

本Spec承認後、Impact Analysisの詳細化(必要であれば)を経て実装に着手する。

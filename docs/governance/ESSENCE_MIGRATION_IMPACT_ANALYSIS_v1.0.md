# ESSENCE Migration Impact Analysis v1.0

## 位置づけ

本文書はDC_20260707_020(Human Gate再承認、監査官R01=きむら博士)で許可された次工程
「Impact Analysis作成」に対応する。ESSENCE_MIGRATION_SPEC_v1.1.mdで確定した方針
(Option2採用・Essence Resolver方式・Writer経路維持・API境界Spec化)を前提に、
app.py参照経路の完全棚卸しとResolver方式の詳細設計、影響範囲分析を行う。

**本文書はImpact Analysis(分析)のみであり、app.py・essenceファイル・API設定・Writer経路への
変更は一切行っていない。** 実装はHuman Gate再承認(Implementation Plan承認)を経てから着手する。

## 1. app.py参照経路の完全棚卸し・分類

ESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.md 1節で棚卸し済みの19箇所を、Migration上の扱いで4分類する。

| 行 | 参照内容 | 分類 |
|---|---|---|
| 736-748 `auto_update_essence_from_mataka()` | Legacy Essence Storeへ書込み | **移行不要**(Writer経路、DC_20260707_019/020で変更対象外と確定) |
| 753-765 `check_and_trigger_essence_update()` | MATAKA件数監視・Thread起動トリガー | **移行不要**(Writer経路のトリガーロジック) |
| 1478,1490-1499 COMMAND CENTER API内`essence_updated`等算出 | Legacy Essence Store読取 | **Resolver移行候補**(Option2により`get_canonical_essence()`基準へ切替) |
| 1680,1689-1695 プロンプトヘッダー生成 | Legacy Essence Store読取 | **Resolver移行候補** |
| 1769,1822-1830 詳細ステータスAPI | Legacy Essence Store読取 | **Resolver移行候補** |
| 1833-1841 `/essence/detail`ルート | Legacy Essence Store読取・公開 | **Resolver移行候補**(Option4のAPI境界Spec対象でもある) |
| 1882-1891 `/public/essence`ルート | Legacy Essence Store読取・公開 | **Resolver移行候補**(同上) |
| 2005-2025 `_auto_danger_to_essence()` | Legacy Essence Storeへ書込み | **移行不要**(Writer経路) |
| 2561-2567 `run_essence()` | `essence_classifier.py`(Legacy Writer)をsubprocess起動 | **移行不要**(Writer経路、Legacy Writer呼出ロジックも変更対象外) |

**Canonical直接参照**: 現時点でapp.py内にCanonical Essence(`interface/lever_essence.json`)を
直接参照する箇所は**存在しない**(ゼロ件)。これが今回のMigrationの核心であり、
「app.pyはCanonical Essenceを一切見ておらず、Legacy Essence Storeのみを見ている」という
現状そのものがIC_20260707_001の技術的原因である。Resolver導入によって、はじめてapp.pyから
Canonical Essenceへの参照経路が生まれることになる。

### 集計

| 分類 | 件数 |
|---|---|
| Canonical直接参照 | 0箇所(現状) |
| Legacy参照(読取、Resolver移行候補と同一) | 5箇所 |
| Resolver移行候補 | 5箇所(上記Legacy参照と同一の5箇所がそのままResolver経由に置き換わる) |
| 移行不要(Writer経路) | 4箇所(app.py内2書込み関数+1トリガー+1 Legacy Writer起動) |

## 2. Essence Resolver方式の詳細化

### 2.1 interface案

```python
# interface/essence_resolver.py(新設案、未実装、Human Gate対象の新規中核モジュール)

def get_canonical_essence() -> dict:
    """
    Canonical Essence(interface/lever_essence.json)を返す。
    入力: なし
    出力: {"INCIDENT": str, "OPERATION": str, "PHILOSOPHY": str, "_synced_at": str, ...}
    """

def get_legacy_essence() -> dict:
    """
    Legacy Essence Store(第3ファイル)を返す。
    入力: なし
    出力: {"INCIDENT": str, "OPERATION": str, "PHILOSOPHY": str,
           "INCIDENT_updated": str, "OPERATION_updated": str, "PHILOSOPHY_updated": str, ...}
    """

def get_display_essence() -> dict:
    """
    COMMAND CENTER/公開API向けの統合ビュー。Option2方針(Canonical主表示+Legacy別セクション)に従う。
    出力: {
        "canonical": get_canonical_essence()の内容(または例外時はNone+degraded flag),
        "legacy": get_legacy_essence()の内容(または例外時はNone),
        "primary_source": "canonical" | "legacy"(2.4のfallback条件により決定)
    }
    """
```

### 2.2 入出力

- 入力: いずれの関数も引数なし(対象ファイルパスはモジュール内定数として固定)
- 出力: 全て`dict`。ファイル不在・JSON不正の場合は空`dict`または`None`を返す
  (呼出側でcrashしないことを保証する。詳細は2.3例外処理)

### 2.3 依存関係

| 関数 | 依存先 |
|---|---|
| `get_canonical_essence()` | `interface/lever_essence.json`(ファイルI/O) |
| `get_legacy_essence()` | `C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json`(ファイルI/O) |
| `get_display_essence()` | 上記2関数(内部依存のみ、外部依存なし) |

events.db(essenceテーブル)への直接依存は持たない(Canonical Essenceの正本はevents.dbだが、
Resolverはそのfile projectionである`interface/lever_essence.json`を読む設計とする。理由:
events.db直読みにすると`essence_auto_updater.py`とResolverの二重読み込み経路が生まれ、
「単一Writer管理」の趣旨に反するため。Resolverはあくまでfile projectionの読取専用ラッパー)。

### 2.4 例外処理

| ケース | 挙動 |
|---|---|
| `interface/lever_essence.json`が存在しない | `get_canonical_essence()`は空dictを返す。ログ出力(`[ESSENCE_RESOLVER] Canonical not found`) |
| `interface/lever_essence.json`がJSON不正 | `json.JSONDecodeError`をcatchし空dictを返す。ログ出力+イベント記録(Integrity Classification対象になり得る) |
| Legacy Essence Storeが存在しない | `get_legacy_essence()`は空dictを返す(現状も`ESSENCE_PATH.exists()`チェックがapp.py側にあるため、この挙動は現状と同等) |
| 両方とも取得失敗 | `get_display_essence()`は`{"canonical": {}, "legacy": {}, "primary_source": "none"}`を返す。
  COMMAND CENTER側は「essence利用不可」を表示する想定(500エラーにはしない) |

### 2.5 Legacy fallback条件

Option2の「Canonical主表示+Legacy別セクション」は常時両方を返す設計が基本だが、
`primary_source`フィールドにより以下の場合はLegacyをfallbackとして扱う:

- Canonical Essence取得成功 → `primary_source: "canonical"`(通常時)
- Canonical Essence取得失敗(ファイル不在・不正)かつLegacy Essence Store取得成功
  → `primary_source: "legacy"`(降格表示、COMMAND CENTER側で「Canonical利用不可のためLegacy表示中」
  という注記を出す想定)
- 両方失敗 → `primary_source: "none"`

この設計により、Canonical Essenceパイプライン(`essence_auto_updater.py`)が何らかの理由で
停止した場合でも、COMMAND CENTER自体が完全に情報を失うことを防ぐ(Legacy Essence Storeが
「万一の際の保険」としての価値を持つ、というDC_20260707_019/020の「削除禁止」判断の裏付けにもなる)。

## 3. 影響範囲分析

### 3.1 app.py

Resolver導入により、ESSENCE_PATH定義4箇所(1478/1680/1769/1836行目)を`essence_resolver`の
呼出に置き換える想定。変更行数は多くないが、COMMAND CENTER APIレスポンス構造が
`{"canonical": ..., "legacy": ..., "primary_source": ...}`という新形式に変わるため、
呼出元(index.html)側の対応が必須になる。

### 3.2 essence関連module

- `essence_auto_updater.py`: 変更なし(Canonical Essenceの書込み主体として維持)
- `essence_classifier.py`ほかLegacy Writer5スクリプト: 変更なし
- `interface/essence_resolver.py`: 新設(Human Gate対象の新規中核モジュール、DC_20260707_020条件)

### 3.3 API

- `/essence/detail`・`/public/essence`: レスポンス構造がResolver経由に変わる。
  Option4(公開範囲/認証/命名/監査ログ)の最終決定次第でさらに変更が加わる可能性がある
  (本Impact Analysisの時点ではOption4は未確定のため、実装時に別途確認が必要)
- Gateway(`gateway/context_builder.py`・`gateway/gateway.py`): `data/lever_essence.json`を
  参照しており、Resolver導入の影響を受けない(Projection経路はexport_for_cloudflare.py経由のまま
  変更しないため)

### 3.4 COMMAND CENTER

`essence_updated`/`essence_axes`/`essence_count`の算出元がLegacy Essence Store基準から
Canonical Essence基準(Resolver経由)に変わるため、COMMAND CENTER UI(index.html)側で
新しいレスポンス構造(`canonical`/`legacy`/`primary_source`)に対応する表示ロジックの追加が必要。
これは今回のImpact Analysisで新たに識別された、v1.1時点より具体化した影響点である。

### 3.5 Orchestra連携

**調査の結果、影響なし**。理由: Orchestra拡張(content.js)の`fetchLivingContext()`は
`/api/handshake`のみを呼び出しており、essence関連の別エンドポイントを呼んでいないことを
grep確認済み。`/api/handshake`の実装(`interface/handshake.py`)自体もessenceデータ(Canonical/Legacy
いずれも)を一切参照しておらず、TODO一覧・現在フェーズ(`CURRENT_PHASE`定数)を返す設計になっている。
したがって、本MigrationはOrchestra拡張が実際に表示する「Living Context」の内容には影響を与えない。

この発見は、当初のLiving Context整合性監査の出発点(Orchestra handshakeが最新か)と、
今回のessence Migration(COMMAND CENTER/公開APIが最新か)が、実装上は独立した別系統である
ことを明確にする。両者を混同しないよう、今後のドキュメントでも区別を維持すること。

## 4. 未確定事項(次のHuman Gateで決定が必要)

- Option4(公開範囲/認証要否/命名/監査ログ)の最終決定(v1.1 2節で提示した暫定検討方向のまま)
- COMMAND CENTER UI(index.html)側の表示変更を今回のMigrationに含めるか、別タスクとするか
- Resolverの例外処理・Legacy fallback条件(2.4/2.5)の設計内容への同意

## 5. 禁止事項(継続)

- app.py本体の変更
- Legacy Essence Store・Legacy Writer(6スクリプト)の削除
- API公開設定(`/public/essence`・`/essence/detail`)の変更
- いずれかのessenceファイルの移動・リネーム・削除
- Writer経路(MATAKA/DANGER/essence_classifier.py等)の変更

## 6. 次工程

本Impact AnalysisのHuman Gate承認 → Implementation Plan作成(実装手順・コミット単位・
検証手順の具体化) → Human Gate最終承認 → 実装(CHANGE_START → 変更 → UTF-8検証 → CHANGE_DONE)。

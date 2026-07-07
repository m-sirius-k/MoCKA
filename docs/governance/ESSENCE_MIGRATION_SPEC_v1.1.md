# ESSENCE Canonical Migration Spec v1.1

## 位置づけ

本文書はESSENCE_MIGRATION_SPEC_v1.0.mdの後継であり、監査官R01(きむら博士)による採用方針確定
(2026-07-07)を反映する。v1.0は履歴として保持し、本文書で上書きしない。

**本文書は引き続きSpec(設計案)段階であり、app.py・各essenceファイルへの変更は一切行っていない。**
実装はHuman Gate再審査(本v1.1の承認)後、さらにImpact Analysis詳細化を経てから着手する。

## 1. 採用方針確定

- **Option2確定**: Canonical Essence(`interface/lever_essence.json`)を主表示とし、
  Legacy Essence Store(第3ファイル)は別管理セクションとして維持する(削除しない、DC_20260707_019の
  制約を継続する)。
- **Option4条件付き採用**: API境界是正(`/public/essence`・`/essence/detail`)をSpec対象化する。
  実装ではなく、整理項目の検討をこの段階で行う。現時点では両ルートへの変更は禁止のまま。

## 2. Option4 Spec対象整理項目

| 項目 | 検討内容(いずれも未決定、次のHuman Gateで判断) |
|---|---|
| **公開範囲** | 案(a)Legacy Essence Storeの全内容を返す(現状維持) / 案(b)要約のみ返す(INCIDENT/OPERATION/PHILOSOPHYの先頭数十文字等) / 案(c)出所ラベル(`legacy_essence_store`)を付与した上で全内容を返す |
| **認証要否** | 案(a)無認証のまま(現状、ただしIC_20260707_004の不一致は残る) / 案(b)簡易APIキー認証を追加 / 案(c)ルート自体をCOMMAND CENTER内部専用にし外部ルートとしては廃止 |
| **命名** | 案(a)現状維持(`/public/essence`) / 案(b)`/internal/legacy_essence`等、実態(private・legacy)に即した改名 / 案(c)`/public/`プレフィックスのみ除去 |
| **監査ログ** | 案(a)アクセスログなし(現状) / 案(b)アクセス毎に`mocka_write_event`で記録 / 案(c)異常アクセス(高頻度・未知IP等)のみ記録 |

暫定的な検討方向(次のHuman Gateで最終決定): 公開範囲は(c)、認証要否は(c)(内部専用化、外部到達性が
現状ないことと整合)、命名は(b)、監査ログは(b)。ただしこれらは提案であり、本v1.1時点での決定ではない。

## 3. app.py変更方針: Essence Resolver / Adapter方式(第一候補)

直接参照変更(ESSENCE_PATH等を書き換えるのみの最小変更)ではなく、**Essence Resolverモジュール
(仮称: `interface/essence_resolver.py`)を新設し、app.py内の読み取り経路を集約する方式**を
第一候補としてImpact Analysisを行う。

### 3.1 想定インターフェース(設計案、未実装)

```python
# interface/essence_resolver.py(新設案、未実装)
def get_canonical_essence() -> dict:
    """Canonical Essence(interface/lever_essence.json)を返す"""

def get_legacy_essence() -> dict:
    """Legacy Essence Store(第3ファイル)を返す"""

def get_display_essence() -> dict:
    """
    COMMAND CENTER/公開API向けの統合ビューを返す。
    Option2の方針(Canonical主表示+Legacy別セクション)に従い、
    {"canonical": get_canonical_essence(), "legacy": get_legacy_essence()}
    のような構造を返す想定。
    """
```

### 3.2 app.py側の変更範囲(想定、未実装)

- ESSENCE_PATH定義4箇所(1478/1680/1769/1836行目)を`essence_resolver`の呼出に置き換える
- `/essence/detail`・`/public/essence`ルートを`get_display_essence()`(またはOption4決定後の
  公開範囲に応じた専用関数)経由に置き換える
- COMMAND CENTER API内の`essence_updated`/`essence_axes`/`essence_count`算出を
  `get_canonical_essence()`基準に切り替える
- **Active Writer(`auto_update_essence_from_mataka()`・`_auto_danger_to_essence()`)の
  書込み先は変更しない**(Resolverは読み取り専用の集約層であり、書込み経路には触れない)
- **Legacy Writer(`essence_classifier.py`等)の呼出ロジックも変更しない**

### 3.3 Resolver方式を第一候補とする理由

- 現状7箇所以上に分散したessence参照(ESSENCE_PATHの重複定義4箇所含む)を1モジュールに集約でき、
  将来Canonical Essenceの実装(例: events.db直読みへの統一)が変わった場合もapp.py側の変更が
  最小で済む
- 直接参照変更(v1.0のOption1相当)より変更点が見えやすくなり、レビュー・rollbackが容易になる
- v1.0で「過剰投資」として一旦スコープ外としたOption3(Adapter層)の考え方を、今回は
  「読み取り専用の軽量Resolver」という限定された形で取り込むため、範囲を必要最小限に抑えられる

## 4. 追加項目(監査官R01指示)

### 4.1 Rollback設計

- app.pyはMoCKA本体リポジトリ(git管理下)にあるため、実装コミット前に必ず現状のapp.pyを
  `git diff`で確認し、実装は単一の識別可能なコミットとして行う(TODO_364準拠、
  `mocka_git_safe_commit()`経由)
- Rollbackトリガー基準(案): (a)COMMAND CENTER UIでessence関連表示がエラーになる
  (b)`/essence/detail`・`/public/essence`が500を返す (c)Active Writer
  (MATAKA/DANGER自動フック)の書込みが失敗するようになる、のいずれかを実装後の観察期間内に検知した場合
- Rollback手段: `git revert`(単一コミットのため)。Resolverモジュール自体は新規ファイルのため、
  rollback時はapp.py側の呼出変更のみを戻せばよい(Resolverファイル自体を残しても実害はない)

### 4.2 移行前後比較

| 項目 | 移行前(現状) | 移行後(Resolver方式採用時の想定) |
|---|---|---|
| COMMAND CENTER `essence_updated` | Legacy Essence Storeの`{axis}_updated`max値(2026-06-20で停滞) | Canonical Essence(interface/lever_essence.json)の`_synced_at`等、実際に鮮度が動く値 |
| `/public/essence`応答 | Legacy Essence Store全内容(無認証・命名`/public/`のまま) | Option4決定後の公開範囲・認証・命名に従う(4.のとおり未決定) |
| `/essence/detail`応答 | Legacy Essence Storeの`text`/`updated`/`count`/`filled` | `canonical`/`legacy`両セクションを含む構造(想定) |
| app.py内のessence参照箇所数 | 7箇所以上に分散(ESSENCE_PATH重複定義4箇所含む) | Resolverモジュール1箇所に集約、app.py側はResolver呼出のみ |
| Active Writer(MATAKA/DANGER) | Legacy Essence Storeへ直接書込み | 変更なし(書込み経路は今回のMigration対象外) |
| Legacy Writer(6スクリプト+essence_classifier.py) | Legacy Essence Storeへ書込み、呼出ロジックはapp.py内 | 変更なし |

### 4.3 影響範囲(詳細版、v1.0 4節の拡張)

| 影響対象 | 詳細 |
|---|---|
| COMMAND CENTER UI(index.html) | `essence_updated`等のレスポンス構造変更に伴い、表示ロジックの追随が必要。特に`canonical`/`legacy`分離表示への対応が新規に必要になる可能性が高い |
| `/public/essence`・`/essence/detail`外部消費者 | 現状Cloudflare Tunnel非公開・openapi.yaml未登録のため実利用なしと推定(断定不可) |
| Active Writer | 書込み経路は今回のMigration対象外のため影響なし |
| Legacy Writer | 呼出ロジック(`run_essence()`内の`essence_classifier.py`起動含む)は変更しないため影響なし |
| 新規コード(Resolver) | `interface/essence_resolver.py`という新しいコード面が追加されるため、単体テスト(Canonical/Legacy双方が正しく読めるか、片方のファイルが存在しない場合のフォールバック)が新規に必要 |
| CP932/UTF-8検証 | Resolverモジュール自体、JSON生成箇所ともに実装時にUTF-8検証必須(TODO_333準拠) |

### 4.4 Human Gate再承認条件

以下すべてを満たした時点で、app.py実装(CHANGE_START)に着手できるものとする。

- [ ] Option4整理項目(公開範囲/認証要否/命名/監査ログ)の最終決定
- [ ] Essence Resolver方式(3節)のインターフェース設計の承認
- [ ] Rollback設計(4.1)の承認
- [ ] 移行前後比較(4.2)の内容に相違がないことの確認
- [ ] 影響範囲(4.3)に見落としがないことの確認
- [ ] 実装後の検証手順(UTF-8検証・構文検証・COMMAND CENTER実機確認・Active Writer動作確認)への合意

## 5. 禁止事項(継続)

本v1.1時点でも以下は禁止のまま。

- app.py本体の変更
- Legacy Essence Store・Legacy Writer(6スクリプト)の削除
- API公開設定(`/public/essence`・`/essence/detail`)の変更
- いずれかのessenceファイルの移動・リネーム・削除

## 6. 次工程

本v1.1のHuman Gate再審査 → 承認後、Essence Resolverインターフェースの詳細設計(必要であれば
v1.2として別途作成) → 実装(CHANGE_START → 変更 → UTF-8検証 → CHANGE_DONE)。

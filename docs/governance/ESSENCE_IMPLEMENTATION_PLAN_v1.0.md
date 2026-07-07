# ESSENCE Implementation Plan v1.0

## 位置づけ

本文書は監査官R01(きむら博士)によるESSENCE_MIGRATION_IMPACT_ANALYSIS_v1.0.md承認を受けて作成する
実施計画である。ESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.md(DC_20260707_019)・
ESSENCE_MIGRATION_SPEC_v1.1.md(DC_20260707_020)・ESSENCE_MIGRATION_IMPACT_ANALYSIS_v1.0.mdの
一連の設計を前提とする。

**本文書は実施計画(Plan)のみであり、app.py・essenceファイル・API設定・Writer経路への変更、
Resolverの実装コードは一切書いていない。** 実装はHuman Gate最終承認(7節)を経てから着手する。

## 1. Essence Resolver導入計画

### 1.1 module構成

- 新設ファイル: `interface/essence_resolver.py`(1ファイル、既存のessence_auto_updater.py/
  essence_classifier.py等とは独立、それらを変更・置換しない)
- 呼出元: `app.py`のみ(現時点の想定。将来Gateway等が使う可能性はあるが本Planのスコープ外)

### 1.2 interface

```python
def get_canonical_essence() -> dict: ...   # interface/lever_essence.json読取
def get_legacy_essence() -> dict: ...      # Legacy Essence Store(第3ファイル)読取
def get_display_essence() -> dict: ...     # 統合ビュー(canonical/legacy/primary_source)
```
(詳細はESSENCE_MIGRATION_IMPACT_ANALYSIS_v1.0.md 2.1節を正本とする)

### 1.3 read/write境界

- Resolverは**読み取り専用**。書込み関数は一切持たない
- Active Writer(`auto_update_essence_from_mataka()`・`_auto_danger_to_essence()`)は
  Resolverを経由せず、現行どおりLegacy Essence Storeへ直接書込みを続ける
- Legacy Writer(`essence_classifier.py`等)もResolverを経由しない
- `essence_auto_updater.py`のCanonical Essence書込み(`sync_essence_db_to_file()`)もResolverを
  経由しない(Resolverは読取専用ラッパーであり、書込み経路には一切関与しない設計を維持する)

### 1.4 source識別

`get_display_essence()`の返り値に`primary_source`(`"canonical"`|`"legacy"`|`"none"`)を含める。
将来的な拡張として、各軸(INCIDENT/OPERATION/PHILOSOPHY)ごとの`source`ラベル付与も検討可能だが、
本v1.0では全体単位の`primary_source`のみを実装対象とする(過剰設計を避ける)。

### 1.5 fallback条件

Impact Analysis 2.5節を正本とする(Canonical取得失敗時のみLegacyへ降格表示、両方失敗時は
`"none"`)。実装時にこの3状態の単体テストを必ず用意する(6節検証計画参照)。

### 1.6 audit log設計

高頻度呼出になるため、呼出の都度イベント記録はしない。以下の場合のみ記録する。

- Canonical取得失敗の検知時(1時間に1回まで、連続失敗時の記録スパムを防止)
- `primary_source`が`"legacy"`または`"none"`に変化した瞬間(fallback発動の検知)
- 日次1回、Canonical/Legacy取得成功率のサマリー記録(将来のIntegrity監査の材料とする)

記録方法は既存の`mocka_write_event`を用いる(Resolver内から直接呼ぶか、呼出元app.py側で
判定してから記録するかは実装時に決定。過度な結合を避けるため後者を暫定推奨)。

## 2. app.py移行計画

| 項目 | 内容 |
|---|---|
| 現在のLegacy参照箇所 | 5箇所(COMMAND CENTER API内essence_updated等算出/プロンプトヘッダー生成/詳細ステータスAPI/`/essence/detail`/`/public/essence`)。Impact Analysis 1節の表を正本とする |
| Resolver置換対象 | 上記5箇所すべて。各箇所の`ESSENCE_PATH.read_text()`+`json.loads()`ブロックを`essence_resolver.get_display_essence()`(または用途に応じ`get_canonical_essence()`/`get_legacy_essence()`)の呼出に置換する |
| 変更量(見積り) | 5箇所×平均5-8行の削除、5箇所×1-2行の追加(import文含む)。純減の見込み。正確な行数は実装時のdiffで確定する |
| 影響範囲 | COMMAND CENTER APIレスポンス構造が`{"canonical":..., "legacy":..., "primary_source":...}`に変わるため、`index.html`側の表示ロジック追随が必須(3節参照) |

Active Writer(2箇所)・Legacy Writer起動(1箇所)・トリガーロジック(1箇所)の計4箇所は
**本Planの変更対象外**(Impact Analysis「移行不要」区分のまま)。

## 3. Legacy Essence Store対応

### 3.1 維持条件

DC_20260707_019/020で確定済みの制約をそのまま継続する。

- 新規Writer追加禁止
- 既存ファイル削除禁止
- Active Writer(MATAKA/DANGER)・Legacy Writer(6スクリプト+essence_classifier.py)は
  現状のまま稼働継続(呼出ロジックも変更しない)

### 3.2 fallback条件

1.5節のとおり。Canonical Essence取得が正常な限り、Legacy Essence Storeは「常時併記される
副次セクション」として表示され続け、Canonical失敗時のみ「主表示への降格」という形で価値を発揮する。

### 3.3 将来退役条件(目安、本Planでは決定しない)

以下はあくまで将来判断のための目安であり、本Implementation Planで退役を決定するものではない
(退役判断は別途Human Gateが必要、DC_20260707_019で明記済み)。

- Legacy Writer(6スクリプト)が一定期間(目安6ヶ月)完全に非稼働と確認できた場合
- Active Writer(MATAKA/DANGER)の役割がCanonical Essence側へ統合された場合
- Legacy Essence Storeの内容がきむら博士の判断で参照価値を失ったと確認された場合

## 4. API境界

| 項目 | 内容 |
|---|---|
| 現状 | `/public/essence`・`/essence/detail`は無認証、Legacy Essence Storeを直接返す。Cloudflare Tunnel未登録のため実質到達不可能(IC_20260707_004) |
| 問題 | (a)命名(`/public/`)が実態(private)と不一致 (b)認証機構なし (c)監査ログなし |
| 改善候補 | ESSENCE_MIGRATION_SPEC_v1.1.md 2節の3案ずつ(公開範囲/認証要否/命名/監査ログ)を参照。本Planでは**実施せず**、別フェーズ(sub-phase)として扱う |

**スコープ分離の提案**: 本Implementation Planの対象はResolver導入(Option2)のみとし、
API境界是正(Option4)は別途独立したHuman Gate判断・別のImplementation Planで扱う。
理由: 両者を同時実装するとレビュー・rollbackの単位が大きくなりすぎ、問題切り分けが困難になるため。

## 5. Rollback計画

| 対象 | Rollback方法 |
|---|---|
| **Code** | 実装は単一の識別可能なコミットとして行う(`mocka_git_safe_commit()`経由、TODO_364準拠)。問題発生時は`git revert`で当該コミットのみを戻す。`interface/essence_resolver.py`は新規ファイルのため、revert後もファイル自体が残っても実害はない(app.py側が参照しなくなるだけ) |
| **Config** | 本v1.0時点でResolver用の新規設定値(タイムアウト等)は導入しない想定。もし実装時に設定を追加する場合は、その設定ファイル(例: `.env`追加キー)も同一コミットに含め、revert対象とする |
| **Data Projection** | Resolver導入によりinterface/data/Legacy各lever_essence.jsonへの書込みは一切発生しない設計のため、data projectionのrollbackは基本的に不要。ただし将来Option4(API境界是正)実装時にレスポンス形式が変わる場合、外部クライアント側のキャッシュ・パース処理が旧形式を期待している可能性への配慮(後方互換フィールドの一時併存等)を、そのフェーズのPlanで別途検討する |

## 6. 検証計画

実装後、以下4点を必ず確認する。

1. **Canonical取得確認**: `get_canonical_essence()`が`interface/lever_essence.json`の内容
   (INCIDENT/OPERATION/PHILOSOPHY)を正しく返すことをローカルで確認する
2. **Legacy fallback確認**: `interface/lever_essence.json`を一時的にリネーム(退避)した状態で
   `get_display_essence()`が`primary_source: "legacy"`を返すことを確認し、確認後は必ずファイル名を
   元に戻す(検証用の一時操作であり、本番データへの影響がないことを確認する)
3. **COMMAND CENTER確認**: 実装後にCOMMAND CENTER UI・`mocka_get_command_center` MCPツールの
   応答が新しいレスポンス構造(`canonical`/`legacy`/`primary_source`)を正しく返すことを確認する
4. **Orchestra非影響確認**: 実装後にOrchestra拡張の`fetchLivingContext()`(`/api/handshake`)が
   引き続き正常動作することを回帰確認する(Impact Analysis 3.5節で「影響なし」と判定済みのため、
   念のための確認に留まる)

## 7. Human Gate最終承認条件

以下すべてを満たした時点で、app.py実装(CHANGE_START)に着手できるものとする。

- [ ] 1節(Resolver導入計画: module構成/interface/read-write境界/source識別/fallback条件/
      audit log設計)の承認
- [ ] 2節(app.py移行計画)の承認、特にResolver置換対象5箇所に相違がないことの確認
- [ ] 3節(Legacy Essence Store対応)の維持条件・fallback条件に同意すること
- [ ] 4節のスコープ分離提案(API境界是正=Option4は別フェーズとする)への同意
- [ ] 5節(rollback計画)の承認
- [ ] 6節(検証計画)4項目の実施に同意すること
- [ ] `interface/essence_resolver.py`新設が「Human Gate対象の新規中核モジュール」であることの
      再確認(DC_20260707_020の条件)

## 8. 禁止事項(継続)

本v1.0時点でも以下は禁止のまま。

- app.py本体の変更
- `interface/essence_resolver.py`の実装(コード作成)
- API設定(`/public/essence`・`/essence/detail`)の変更
- Legacy Essence Store・Legacy Writer(6スクリプト)の削除
- いずれかのessenceファイルの移動・リネーム・削除(6節検証計画内の一時的リネームを除き、
  検証後は必ず原状復帰する)

## 9. 次工程

本Implementation PlanのHuman Gate最終承認 → 実装着手
(CHANGE_START → `interface/essence_resolver.py`作成 → app.py 5箇所の置換 →
UTF-8検証・構文検証 → 6節検証計画の実施 → CHANGE_DONE)。

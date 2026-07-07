# Seal Migration Spec v0.1

## 位置づけ

本文書はDC_20260707_021(Human Gate Phase1承認、Seal Canonical Source確定)に基づき、
COMMAND CENTERのSeal参照切替設計(Phase2)として作成する。

**本文書は設計(Spec)のみであり、app.py変更・参照切替実装・anchor_record.json変更・
ledger.json変更・commit・Runtime再起動のいずれも行っていない。** 実装(Phase3)は本Specの
Human Gate承認後、別途着手する。

## 1. 現行参照経路の完全整理

app.py内でseal関連の値(`governance/anchor_record.json`・`runtime/main/ledger.json`・
`data/seal_log.json`)を扱う箇所を全数確認した結果、**想定より複雑な現状**が判明した。

| 行 | ルート/箇所 | 参照先 | 分類 |
|---|---|---|---|
| 1401-1439 | `/integrity/status` | `governance/anchor_record.json` | **既にCanonical参照(正常)** |
| 1464-1473 | `/seal/history` | `governance/anchor_record.json` | **既にCanonical参照(正常)** |
| 1512, 1554-1566, 1576 | `civilization_loop.audit`(`/loop/status`内) | `runtime/main/ledger.json` | Legacy参照(要切替) |
| 2064-2070 | AUTO-AUDIT日次ループ | `anchor_update.py`起動のみ(ledger.json/seal_log.jsonには非接触) | 変更不要 |
| 2091-2100 | `/audit/status` | `data/seal_log.json`(ファイル不在) | 未使用(別Decision対象) |
| 2102以降 | `/audit/seal`(POST) | `anchor_update.py`起動 + `data/seal_log.json`書込み | 未使用(別Decision対象) |

**重要な発見**: `/integrity/status`・`/seal/history`の2ルートは、**既に`governance/anchor_record.json`を
正しく参照している**。今回のMigration対象は`civilization_loop.audit`(COMMAND CENTER UIが直接見る
seal表示)の1箇所のみであり、コードベース全体がLegacy参照だったわけではない。

## A. 現状: ledger.json参照構造

```python
# app.py 1512行目
LEDGER_JSON = Path(r"C:\Users\sirok\MoCKA\runtime\main\ledger.json")

# app.py 1554-1566行目
last_seal = None
last_seal_hash = None
if LEDGER_JSON.exists():
    try:
        ldata = json.loads(LEDGER_JSON.read_text(encoding="utf-8-sig"))
        if isinstance(ldata, list) and ldata:
            last_entry = ldata[-1]
            last_seal = str(last_entry.get("timestamp", ""))
            last_seal_hash = last_entry.get("event_hash", "")[:16]
        elif isinstance(ldata, dict):
            last_seal = ldata.get("last_updated") or ldata.get("timestamp")
            last_seal_hash = ldata.get("hash") or ldata.get("anchor_hash")
    except: pass

# app.py 1576行目
"audit": {"label": "Audit", "last_seal": last_seal, "last_seal_hash": last_seal_hash},
```

`ledger.json`はリスト形式(各要素が`timestamp`/`event_hash`を持つチェーン構造)を前提にした
読み取りロジックであり、`anchor_record.json`の単一dict構造(後述)とはスキーマが異なる。

## B. 移行後: anchor_record.json参照構造(既存の`/integrity/status`と同一パターン)

```python
# 参考: /integrity/status(1414-1417行目)の既存実装
seal_path = os.path.join(ROOT_DIR, 'governance', 'anchor_record.json')
last_seal = {}
if os.path.exists(seal_path):
    try: last_seal = json.load(open(seal_path, encoding='utf-8'))
    except: pass
```

`anchor_record.json`は単一dict構造(`sealed_summary_hash`/`sealed_at_utc`/`external_ref`等)を持つ。
移行後の`civilization_loop.audit`は、この既存パターンを踏襲し以下のような形になる想定(設計案、未実装)。

```python
# 移行後案(未実装)
anchor_path = os.path.join(ROOT_DIR, 'governance', 'anchor_record.json')
last_seal = None
last_seal_hash = None
if os.path.exists(anchor_path):
    try:
        adata = json.load(open(anchor_path, encoding='utf-8'))
        last_seal = adata.get("sealed_at_utc")
        last_seal_hash = (adata.get("sealed_summary_hash") or "")[:16]
    except: pass
```

## C. 変更対象一覧

| 対象 | 変更内容(案) |
|---|---|
| app.py 1512行目 | `LEDGER_JSON`定義を`ANCHOR_PATH = Path(r"...\governance\anchor_record.json")`相当に置換、
または`/integrity/status`と共有できるヘルパー関数に集約 |
| app.py 1554-1566行目 | `ledger.json`のリスト構造読み取りロジックを、`anchor_record.json`の
dict構造読み取りロジックに置換(B節の案) |
| app.py 1576行目 | キー名(`last_seal`/`last_seal_hash`)は変更せず、値の算出元のみ切替(下流の
COMMAND CENTER UI・`mocka_get_command_center`への影響を最小化) |

## D. 非変更対象一覧

- `governance/anchor_record.json`本体(読むだけ、書込みは`anchor_update.py`のまま)
- `anchor_update.py`(変更なし)
- `/integrity/status`・`/seal/history`(既に正しく実装済み、変更不要)
- `runtime/main/ledger.json`本体(Legacy Ledgerとして保持、削除しない。DC_20260707_021の
  rollback・比較監査・移行検証用途)
- Legacy Ledger関連24スクリプト(変更なし、凍結のみで削除しない)
- `data/seal_log.json`関連(`/audit/status`・`/audit/seal`)は別Decision対象、本Migration Specの
  スコープ外(変更しない)
- AUTO-AUDIT日次ループ(`anchor_update.py`起動、2064-2070行目、ledger.json/seal_log.jsonに
  非接触のため無関係)

## E. Rollback方法

- **Code rollback**: `mocka_git_safe_commit()`経由の単一コミットとして実装し、問題発生時は
  `git revert`で当該コミットのみを戻す(Essence Resolver実装(commit 13f3038)と同じ手順)
- **Config rollback**: 本Migrationでは新規設定値を導入しない想定のため該当なし
- **Data projection rollback**: `civilization_loop.audit`は読取専用の変更であり、
  `anchor_record.json`・`ledger.json`いずれのファイルへも書込みを行わないため、
  データ側のrollbackは不要

## F. Validation項目

- [ ] `civilization_loop.audit.last_seal`/`last_seal_hash`が`anchor_record.json`の
      `sealed_at_utc`/`sealed_summary_hash`と一致することを確認
- [ ] `/integrity/status`・`/seal/history`(既存の正しい参照)と`civilization_loop.audit`
      (移行後)が、同一の`anchor_record.json`を参照するため、表示される値が一致することを確認
      (これが「Living Context表示整合」の直接的な検証になる)
- [ ] COMMAND CENTER実機確認(Essence Resolverと同様、restart後にHTTPレスポンスを確認)
- [ ] `runtime/main/ledger.json`への書込みが引き続き発生しないこと(そもそも本Migrationでは
      書込みロジック自体に触れないため、変更前後で当然変化なしのはずだが、確認項目として明記)
- [ ] `anchor_record.json`が存在しない場合(理論上)のフォールバック挙動(空dict扱い、
      500エラーにならないこと)

## 3. Essence Resolver方式との共通化確認・推奨案

**推奨: 単純な参照切替で十分。専用のSeal Resolverモジュール新設は不要。**

理由:

1. **Legacy側にActive Writerが存在しない**: Essence Migrationでは、Legacy Essence Store
   (第3ファイル)に対してapp.py自身のMATAKA/DANGER自動フックという生きた書込み経路が
   存在したため、Resolverによる「Canonical失敗時にLegacyへ降格表示」というfallback機構に
   実質的な価値があった。今回のLegacy(`ledger.json`)は2026-04-16以降、書込み主体が
   一切存在しない(完全に停止した記録)であるため、「Canonicalが失敗したらLegacyを見る」
   というfallbackにほぼ意味がない(Legacy側も新しい情報を持っていないため)。
2. **既存の正しい参照パターンが実在する**: `/integrity/status`・`/seal/history`が
   既に`anchor_record.json`を読む実装を持っており、Migrationはこのパターンの横展開
   (ほぼ流用に近い)で完結する。新規抽象化のコストに見合わない。
3. **複数ファイル(interface/data/Legacy)の3層構造だったEssenceと異なり、Sealは
   Canonical(anchor_record.json)とLegacy(ledger.json)の2層のみ**であり、Projection層
   に相当するものが存在しない。構造がシンプルであるため、軽量な参照切替で十分対応できる。

ただし、**最小限の重複排除**として、`anchor_record.json`読み込みロジックを1箇所の
小さなヘルパー関数(例: `_read_anchor_record()`、Resolverと呼ぶほどの抽象化ではない)に
切り出し、`/integrity/status`・`civilization_loop.audit`(移行後)の両方から呼ぶことは
検討に値する(コード重複の削減が主目的で、fallbackロジックの追加が目的ではない)。
これはPhase3実装時の詳細判断とし、本Specでは方向性のみ示す。

## 4. Phase3実装条件整理

Phase3(実装)着手には、以下すべてを満たす必要がある。

- [ ] 本SEAL_MIGRATION_SPEC_v0.1.mdのHuman Gate承認
- [ ] DC_20260707_021で示された「Phase2開始前に確認」の3項目(`calc_summary_hash.py`健全性・
      Legacy Ledger不定期起動経路・`seal_log`実行履歴)の確認完了、またはPhase3実装前で
      良いとする明示的な合意
- [ ] F節のValidation項目5点への合意
- [ ] ヘルパー関数化(3節)を行うか、素朴な重複実装のままにするかの決定

## 次工程

本Specの承認 → Phase3実装(CHANGE_START → app.py変更 → UTF-8検証 → CHANGE_DONE) →
Phase4 Runtime Validation(F節の検証項目) → Legacy凍結の最終確認 → 必要であればcommit。

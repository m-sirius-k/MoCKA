# INC_PIPELINE_FAILURE_ANALYSIS_v0.1

INC自動生成 -> GPT_RESTRICTIONS.md自動更新経路の構造監査。

- 作成日: 2026-07-31
- 種別: Observation(観測記録)。Decisionではない
- 上位記録: DC_20260731_001 (status: Active)
- 本工程での禁止事項遵守: コード修正なし / 自動生成仕様変更なし / Decision Ledger登録なし / 設計案の採用判断なし
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17 (HEAD)

---

## 0. 結論(先出し)

指示書が対象とした3欠陥は、いずれもコード上の根拠が確定した(Confirmed)。
さらに、この3欠陥だけでは説明できない別系統の欠陥が2件、調査過程で確定した(D-4, D-5)。
D-5の存在により、現時点のdata/events.csvを入力とする限りINCは1件も生成されない。
すなわち"3欠陥が今すぐ再発する"のではなく、"D-5が解消された瞬間に3欠陥が同時に再発する"
という状態にある。

---

## 1. 対象コードと確定情報

| # | path | 関数 | 最終更新commit | 日時 |
|---|------|------|----------------|------|
| 1 | tools/mocka_risk_engine.py | update_events_risk / auto_generate_incident / assess_risk | 194cd8c942b6555f0ae49fa30e94932227b9bb79 | 2026-04-01 14:14:39 |
| 2 | tools/mocka_5w1h.py | update_incidents_with_5w1h / classify_5w1h | 194cd8c942b6555f0ae49fa30e94932227b9bb79 | 2026-04-01 14:14:39 |
| 3 | tools/mocka_restrictions.py | generate_restrictions | 9d641b35fff329e022a8e190976ae320bc58c0de | 2026-04-01 13:15:25 |
| 4 | docs/governance/GPT_RESTRICTIONS.md | (生成物) | 0bec2c800d2558ca38e410d87eef6e3c03f083aa | 2026-04-01 13:46:37 |

3ファイルとも作業ツリーはclean(未コミット変更なし)。いずれもorigin/mainに到達済み。
GPT_RESTRICTIONS.mdの現物の生成日時スタンプは 2026-04-01 13:45:06 であり、
2026-04-01以降4か月間、再生成が一度も起きていないことを示す。

---

## 2. Phase 1: 呼び出し順序(Confirmed)

実測順序は以下であり、指示書の候補B(GPT_RESTRICTIONS生成 -> 5W1H生成)に一致する。

```
検知 assess_risk           risk_engine.py:24-66
 -> INC生成 auto_generate_incident   risk_engine.py:137 (定義75-111)
 -> GPT_RESTRICTIONS生成             risk_engine.py:155
 -> 5W1H生成                          risk_engine.py:158-159
```

根拠となる実コード(risk_engine.py:154-160):

```python
    if incidents_generated:
        os.system(f"python {RESTRICTIONS}")          # L155
        print("[GPT_RESTRICTIONS] 自動更新完了")      # L156
        # 5W1H自動分析
        w5h1_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mocka_5w1h.py")
        os.system(f"python {w5h1_script}")           # L159
```

INC生成時点で"## 再発防止:"欄は固定文字列"(要分析)"である(risk_engine.py:99-100)。
その状態のINCを入力としてGPT_RESTRICTIONS.mdが確定し(L155)、その後に初めて
再発防止の実体となる情報(5W1HのHow欄)が生成される(L159)。
GPT_RESTRICTIONS.mdへ戻る経路はコード上に存在しない。

欠陥2"生成順序逆転": Confirmed。

---

## 3. Phase 2: 情報消失ポイント(Confirmed)

### 3.1 抽出ロジック(restrictions.py:12-19)

```python
    for path in sorted(incidents):                       # L12  glob "INC-*.md" (L10)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if "## 再発防止" in content:                      # L15
            section = content.split("## 再発防止")[1]     # L16  抽出開始位置
            section = section.split("##")[0].strip()      # L17  抽出終了条件
            inc_id = os.path.basename(path).replace(".md", "")
            restrictions.append(f"### {inc_id} より\n{section}")   # L19
```

- 抽出開始位置: 文字列 `## 再発防止` の直後(全角コロンは含まないため、抽出結果の先頭に
  コロン1文字が残る。現物GPT_RESTRICTIONS.md:22 / :31 に実際に残存している)
- 抽出終了条件: 直後に現れる最初の `##` の直前まで
- parser: 正規表現ではなく単純なstr.split。見出し階層を解釈しない
- 後続セクション扱い: `## 5W1H分析(自動生成)` 以降は完全に抽出対象外

### 3.2 消失の確定

`orchestra経由(Playwright)` を含む文字列の所在:

1. 生成元: tools/mocka_5w1h.py:18
   `"how": "orchestra経由（Playwright）に切替。APIキー依存を排除する"` (パターンP001)
2. 元INCに存在する: docs/incidents/INC-20260401-002.md:29
   `- **How（どう防ぐ）**: orchestra経由（Playwright）に切替。APIキー依存を排除する`
3. 抽出対象外である: 同ファイルにおいて当該行は `## 5W1H分析（自動生成）` (L23) 配下にあり、
   `## 再発防止：` (L15) 配下ではない。L15配下の実体は `（要分析）` (L16) のみ
4. 最終成果物未反映である: docs/governance/GPT_RESTRICTIONS.md:29-31 は
   `### INC-20260401-002 より` / `：` / `（要分析）` のみ

指示書が再確認を求めた3点(元INCに存在 / 抽出対象外 / 最終成果物未反映)は、いずれもConfirmed。

欠陥3"抽出範囲不足による有効情報未利用": Confirmed。

### 3.3 欠陥2と欠陥3の独立性(重要)

仮に呼び出し順序のみを入れ替えて5W1Hを先に実行しても、本欠陥は解消しない。
5W1Hは `## 5W1H分析` セクションをファイル末尾へappendするだけであり(5w1h.py:135-136)、
`## 再発防止` 欄の `（要分析）` を書き換えないためである。
抽出範囲(restrictions.py:16-17)は依然として `（要分析）` のみを拾う。
欠陥2と欠陥3は、どちらか一方の是正では解消しない独立した2欠陥である。

---

## 4. Phase 3: 承認境界(未実装)

現行は以下である。

```
生成 -> 反映
```

以下ではない。

```
生成 -> 候補 -> 承認 -> 反映
```

確認結果:

| 確認項目 | 有無 | 根拠 |
|----------|------|------|
| status field | なし | INCファイルにstatus行が存在しない(auto_generate_incident: risk_engine.py:84-107) |
| review flag | なし | 3ファイル中に該当変数・引数・条件分岐なし |
| approval state | 文字列のみ存在、実効性なし | INCに `## 承認：` `自動生成 / 要Claude確認` が書かれる(risk_engine.py:104-106)が、restrictions.py側は当該欄を一切参照しない(restrictions.py:12-19に承認欄の読取・判定コードが存在しない) |
| human gate | なし | os.system呼び出し(risk_engine.py:155,159)は無条件・無対話 |
| ledger連携 | なし | 3ファイルにmocka_write_event / decision_ledger / events.db への書込コードなし |

したがって、承認状態確認分岐は**未実装**である。
`## 承認：` 欄は記述はされるが読まれることがなく、ゲートとして機能していない。

欠陥1"承認状態確認分岐の不存在": Confirmed(未実装)。

---

## 5. Phase 4: 再発条件(dry-run実測)

MoCKA本体を一切変更しない隔離サンドボックス(scratchpad配下に3スクリプトとデータを複製し、
パス定数のみサンドボックスへ書き換え)で実行した。本体のevents.csv / docs/incidents /
GPT_RESTRICTIONS.mdは読み取りのみで、変更していない。

### 5.1 Run A: 現状のdata/events.csvをそのまま入力

| 観測項目 | 結果 |
|----------|------|
| risk更新 | 92件 |
| INC生成 | **0件** |
| GPT_RESTRICTIONS更新 | 実行されず(risk_engine.py:154の`if incidents_generated:`が偽) |
| 再発防止策反映 | 実行されず |

CRITICAL/HIGH判定自体は6件成立していた(CRITICAL 2 / HIGH 4)。にもかかわらずINCが
0件だった原因は重複判定(risk_engine.py:131-136)の常時成立であり、詳細はD-5に記す。

### 5.2 Run B: 入力CSVのBOMのみ除去して再実行

| 観測項目 | 結果 |
|----------|------|
| risk更新 | 92件 |
| INC生成 | **6件** (INC-20260731-001 .. -006) |
| GPT_RESTRICTIONS更新 | 実行された(全文上書き) |
| 再発防止策反映 | **されない** |

生成されたINC-20260731-002.md の実体:

```
## 再発防止：
（要分析）
...
## 5W1H分析（自動生成）
- **How（どう防ぐ）**: orchestra経由（Playwright）に切替。APIキー依存を排除する
```

同一実行で生成されたGPT_RESTRICTIONS.md の該当箇所:

```
### INC-20260731-002 より
：
（要分析）
```

2026-04-01のINC-20260401-002で起きた事象が、2026-07-31時点のコードで完全に再現した。

質問"現在のコード状態で、同じ条件のINCが発生した場合、同じ結果になるか"への回答:

- 入力CSVがBOM付きである限り: INC自体が生成されない(D-5が先に効く)
- BOMが除去された場合: **同じ結果になる**(3欠陥が同時に再発。Run Bで実証済み)

### 5.3 Run B 2回目: 同一入力での再実行

| 観測項目 | 結果 |
|----------|------|
| risk更新 | 0件 |
| INC生成 | 0件 |
| GPT_RESTRICTIONS.md | 1回目の出力とバイト一致(diff無し) |

risk_levelは1回目で確定値へ書き換えられるため、2回目以降は`row.get("risk_level") != risk`
(risk_engine.py:124)が偽となり、以降のブロック全体に入らない。
結果として、後から5W1Hで生成されたHow欄が、後続実行でGPT_RESTRICTIONS.mdへ反映される
機会は永久に訪れない。`（要分析）` は新規INC発生まで固定され、新規INC発生時も
既存INCの`## 再発防止`欄は`（要分析）`のままであるため、再生成しても同じ内容が再出力される。

---

## 6. 欠陥分類

| ID | 欠陥 | 分類 | 状態 | コード根拠 |
|----|------|------|------|------------|
| D-1 | 承認状態確認分岐の不存在 | Missing Gate(未実装) | Confirmed | restrictions.py:12-19に承認欄参照なし / risk_engine.py:155,159が無条件実行 |
| D-2 | 生成順序逆転 | Ordering Defect | Confirmed | risk_engine.py:155 が 158-159 より先 |
| D-3 | 抽出範囲不足による有効情報未利用 | Extraction Scope Defect | Confirmed | restrictions.py:16-17 が `## 再発防止` 直後から次の`##`までに限定 |
| D-4 | BOM付きCSVによるevent_id列の全損 | Data Destruction | Confirmed(実測) | risk_engine.py:118-120 でBOM未処理 -> キーが`\ufeffevent_id`となり、L147の`row.get(k,"N/A")`で全132行のevent_idが`N/A`に置換される |
| D-5 | 重複判定の常時成立によるINC生成の完全停止 | Silent Suppression | Confirmed(実測) | D-4の副作用で`row.get("event_id","")`が空文字となり、risk_engine.py:132の`"" in content`が全ファイルで真。CRITICAL/HIGH 6件すべてがSKIPされた |

D-4/D-5は指示書の3欠陥に含まれないが、Phase 4のdry-runで再現したため記録する。
D-5はINC生成を無言で停止させるため、"INCが生成されないので問題が顕在化しない"という
形で、D-1/D-2/D-3を覆い隠している。

---

## 7. 影響範囲

### 7.1 確定している実害

- docs/governance/GPT_RESTRICTIONS.md:29-31 に未分析プレースホルダ`（要分析）`が
  公式禁止事項として掲載されている(1件、INC-20260401-002由来)
- 同ファイル:22 / :31 に抽出漏れによる孤立した全角コロンが混入している
- 本ファイルはorigin/mainへ到達済み(公開済み)

### 7.2 伝播先

- gateway/adapter_gpt.py:247-255 が、GPTセッション開始時に本ファイルの参照を指示している。
  すなわち、未分析プレースホルダはGPT側の行動制約として現に配布されている
- AI_BOOT_HUB.md:21 がClaude以外のAIの参照先として本ファイルを指定している
  (同行には既に陳腐化の可能性を示す注記があり、食い違い時は.claude/CLAUDE.mdを優先する
  旨が書かれている)

### 7.3 影響範囲外(確認済み)

- runtime/incident_engine.py 系(runtime/incident_ledger.json)は本経路と接続していない。
  INC-*.md / GPT_RESTRICTIONS.md への読み書きを行わない別系統である
- 本経路は常駐しておらず、起動点は手動実行のみ。したがって現在も継続的に破損を
  拡大させている状態ではない

---

## 8. 修正対象範囲(位置の特定のみ。是正案の提示・選定は行わない)

| 欠陥 | 修正対象ファイル | 修正対象位置 |
|------|------------------|--------------|
| D-1 | tools/mocka_restrictions.py | L12-19(抽出ループ内の採否判定) および tools/mocka_risk_engine.py L154-159(無条件起動) |
| D-2 | tools/mocka_risk_engine.py | L154-159 |
| D-3 | tools/mocka_restrictions.py | L16-17(抽出開始位置・終了条件) |
| D-4 | tools/mocka_risk_engine.py | L118(読取時のエンコーディング指定) および L143-147(書き戻し) |
| D-5 | tools/mocka_risk_engine.py | L131-136(重複判定) |

補足: D-3の是正がtools/mocka_5w1h.py側(`## 再発防止`欄の更新)になるか
tools/mocka_restrictions.py側(抽出範囲の拡張)になるかは設計判断であり、
本工程では確定しない。上表はコードとして接触が必要な最小範囲を示すものであって、
どちらを採るかの判断を含まない。

---

## 9. 未確認事項

1. DC_20260731_001が参照する `track_B_gpt_restrictions_reverification_design_v0.1.md`
   (commit d160f80, branch claude/pders-causal-projection-formal-z4cere) および
   `docs/formal/gpt_restrictions_incident_audit_v0.1.md` は、本ローカルリポジトリに
   存在しない。commit d160f80もローカルに存在しない(`git cat-file -t` で not a valid object)。
   本文書の内容と当該2文書の内容の異同は未照合である
2. data/events.csv にBOMが付いた時期・原因は未特定。git履歴の追跡は本工程では未実施
3. events.csvのevent_id列が既に`N/A`化された状態で本番に書き戻された履歴があるかは未確認
   (現物のevents.csvはevent_idを保持しているため、少なくとも直近の書き戻しでは発生していない)
4. INC ID採番(risk_engine.py:76-81)は当日分ファイル数+1であり、ファイル削除時にID衝突が
   起こりうる。本工程では机上確認のみで、実挙動の検証は未実施
5. docs/incidents/配下の他2文書(INCIDENT_IMPORT_APP_SIDE_EFFECT.md、
   CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md)は`INC-*`のglobに合致しないため
   抽出対象外である。これが意図された除外か否かは未確認
6. 走査範囲はC:\Users\sirok\MoCKA配下に限定される。他ホスト、Cloudflare Workers側、
   外部cron、workshop配下の別リポジトリは未走査であり、"本経路の起動点が手動実行のみ"
   という結論はこの範囲内での結論である

---

## 10. 完了条件の充足状況

- [x] 3欠陥のコード上根拠確認 (D-1/D-2/D-3、いずれもConfirmed)
- [x] 現行データフロー確定 (INC_PIPELINE_DATAFLOW_CURRENT.md)
- [x] 再発条件確認 (dry-run Run A / Run B / Run B 2回目)
- [x] 修正対象範囲確定 (位置の特定のみ。是正案は含まない)
- [x] 未知領域明記 (本文書 9.)

Decision Ledgerへの登録は行っていない(指示書の制約に従う)。本工程はObservation段階である。

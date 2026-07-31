# INC_PIPELINE_DATAFLOW_CURRENT

現行(as-is)データフロー図。設計上の理想形ではなく、コード実測に基づく現在の実行経路のみを記す。

- 作成日: 2026-07-31
- 種別: Observation(観測記録)
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17 (HEAD)
- 対象3ファイルの最終更新commit:
  - tools/mocka_risk_engine.py : 194cd8c942b6555f0ae49fa30e94932227b9bb79 (2026-04-01 14:14:39)
  - tools/mocka_5w1h.py        : 194cd8c942b6555f0ae49fa30e94932227b9bb79 (2026-04-01 14:14:39)
  - tools/mocka_restrictions.py: 9d641b35fff329e022a8e190976ae320bc58c0de (2026-04-01 13:15:25)
- 作業ツリー差分: 上記3ファイルはいずれもclean(未コミット変更なし)

---

## 1. 起動経路

```
(人手) python tools/mocka_risk_engine.py
        |
        v
   __main__  (mocka_risk_engine.py:162-168)
        |
        v
   update_events_risk()  (mocka_risk_engine.py:113)
```

常駐プロセス・スケジューラ・他モジュールからの呼び出しは検出されなかった(検出範囲は
本文書 5. を参照)。唯一の起動点は`__main__`である。

---

## 2. 現行フロー(実測)

```
data/events.csv
      |
      | csv.DictReader           (risk_engine.py:118-120)
      v
+-------------------------------+
| assess_risk(row)              |  risk_engine.py:24-66
| キーワード/error_rate照合      |
+-------------------------------+
      |
      | risk in (CRITICAL, HIGH) and reasons   (risk_engine.py:129)
      v
+-------------------------------+
| 重複判定                       |  risk_engine.py:131-136
| event_id が既存INC本文に含まれるか |
+-------------------------------+
      | 含まれない場合のみ
      v
+-------------------------------+
| auto_generate_incident()      |  risk_engine.py:75-111
| docs/incidents/INC-YYYYMMDD-NNN.md を新規作成
|   "## 再発防止:" -> 固定文字列 "(要分析)"   (risk_engine.py:99-100)
|   "## 承認:"     -> "自動生成 / 要Claude確認" (risk_engine.py:104-106)
+-------------------------------+
      |
      | row["related_event_id"] = inc_id       (risk_engine.py:138)
      v
+-------------------------------+
| events.csv 全文上書き          |  risk_engine.py:143-147
+-------------------------------+
      |
      | if incidents_generated:                (risk_engine.py:154)
      v
+-------------------------------------------+
| os.system("python tools/mocka_restrictions.py")  risk_engine.py:155
+-------------------------------------------+
      |
      v
+-------------------------------+
| generate_restrictions()       |  restrictions.py:8-56
| glob docs/incidents/INC-*.md  |  restrictions.py:10
| 各ファイルから                 |
|   split("## 再発防止")[1]      |  restrictions.py:16
|   .split("##")[0]             |  restrictions.py:17
| を抽出して連結                 |
+-------------------------------+
      |
      v
docs/governance/GPT_RESTRICTIONS.md   (全文上書き, restrictions.py:52-53)
      |
      | ここでGPT_RESTRICTIONS.mdは確定する
      v
+-------------------------------------------+
| os.system("python tools/mocka_5w1h.py")   |  risk_engine.py:158-159
+-------------------------------------------+
      |
      v
+-------------------------------+
| update_incidents_with_5w1h()  |  5w1h.py:89-141
| FAILURE_PATTERNS 照合          |  5w1h.py:10-46
| INCファイル末尾へ append       |  5w1h.py:135-136
|   "## 5W1H分析(自動生成)"      |
|   "- How(どう防ぐ): ..."       |  5w1h.py:125
|   "## パターン分類"            |
+-------------------------------+
      |
      v
docs/incidents/INC-*.md (追記のみ。"## 再発防止"欄は書き換えない)
      |
      X  <-- 以降、GPT_RESTRICTIONS.mdへ戻る経路は存在しない
```

---

## 3. 消費側(下流)

```
docs/governance/GPT_RESTRICTIONS.md
      |
      +--> gateway/adapter_gpt.py:247-255 get_system_prompt_snippet()
      |      GPTセッション開始時に本ファイルの参照を指示する文言を生成
      |
      +--> AI_BOOT_HUB.md:21
             Claude以外のAIの参照先として明記
```

---

## 4. 指示書に示された2案との対応

指示書が確認対象とした2つの候補順序のうち、実測は後者に一致する。

- 候補A(検知 -> INC生成 -> 5W1H生成 -> 再発防止抽出 -> GPT_RESTRICTIONS生成): 不一致
- 候補B(GPT_RESTRICTIONS生成 -> 5W1H生成): 一致(risk_engine.py:155 -> 158-159)

---

## 5. 検出範囲(scope limit)

本フロー図は以下の範囲の走査に基づく。範囲外に別経路が存在しないことは確認していない。

- 走査対象: C:\Users\sirok\MoCKA 配下の .py / .md / .json / .bat / .ps1 / .yml / .yaml / .xml
- 走査文字列: mocka_risk_engine, mocka_restrictions, mocka_5w1h, GPT_RESTRICTIONS
- Windowsタスクスケジューラ: schtasks /query 出力にmocka/risk該当なし
- 未走査: 他ホスト、Cloudflare Workers側、外部cron、他リポジトリ(workshop配下等)

# Phase10 Fixation Package Options v1

Status: OPTIONS AUDIT ONLY（固定候補の整理のみ。結論を出さない。
git add/commit/seal/push禁止）
Date: 2026-06-23

本文書はPHASE10_FIXED_STATE_MATRIX_v1.mdで確定した事実
（Phase10-1・Phase10-2がいずれもFile OK/Event OK/Git以降未実施の
同一状態）を前提に、今後の固定作業（git add/commit/seal/push）を
実施する場合の候補パッケージを整理する。本文書はいずれの候補も
採択しない。実行行為（git add/commit/seal/push）はいずれの候補に
ついても本文書では行わない。

## 候補A: Phase10-1のみ固定

```
対象:
    docs/contracts/phase10_1_observer_node_contract_v1.md
```

```
利点:
    - 固定対象が1ファイルのみであり、commit差分が最小になる。
    - Phase10-0で確立済みの「1契約=1commit」パターンと一致する
      （0b707e4cbはPhase10-0契約1件のみの差分だった）。
    - 監査時に「何を固定したか」の対応関係が単純（1:1）。

リスク:
    - Phase10-2が未固定のまま残る。次回別途固定作業が必要になり、
      作業が2回に分割される（運用コスト増）。
    - Phase10-1とPhase10-2は本来同じ「Node階層の連続した制度化」
      であり、Phase10-1のみを先に固定するとPhase10-2との間に
      「固定タイミングの非対称性」が生じる（Phase10-1は固定済み・
      Phase10-2は未固定という中間状態が一時的に発生する）。

監査容易性:
    - 高い。差分が単一ファイルのため、commit内容の検証が最も簡単。
    - 既存のPHASE10_1_*_AUDIT系文書との対応関係も1:1で追跡しやすい。
```

## 候補B: Phase10-1 + Phase10-2 同時固定

```
対象:
    docs/contracts/phase10_1_observer_node_contract_v1.md
    docs/contracts/phase10_2_advisor_node_contract_v1.md
```

```
利点:
    - Phase10-1とPhase10-2は権限階層上連続する制度
      （Observer→Advisor、Phase10-2第5章Advisor/Observer
      Boundaryで明示的に対比定義されている）であり、同時固定する
      ことで「Node階層の前半2層が揃った状態」を1つのcommitとして
      記録できる。
    - 固定作業が1回で完了し、運用コストが小さい。

リスク:
    - commit差分が2ファイルになるため、Phase10-0のcommit
      （1ファイルのみ）とパターンが異なる。今後「1契約=1commit」
      原則を維持するか「関連契約はまとめてcommit可」という新たな
      運用判断が必要になる可能性がある（本文書では判断しない）。
    - 2ファイルを1commitにまとめることで、将来「Phase10-1のみ
      revertしたい」場合にcommit分割が必要になる
      （ロールバック粒度が粗くなる）。

監査容易性:
    - 中程度。差分は2ファイルだが、いずれも同種の契約文書
      （Node Contract）であり、既存のPHASE10_1/10_2監査文書群が
      個別に対応関係を示しているため、追跡は可能。
    - commit 1件に対し監査文書が2系統（PHASE10_1_*とPHASE10_2_*）
      存在する非対称性がある。
```

## 候補C: Phase10-1 + Phase10-2 + Phase10-3準備資料

```
対象:
    docs/contracts/phase10_1_observer_node_contract_v1.md
    docs/contracts/phase10_2_advisor_node_contract_v1.md
    docs/audits/PHASE10_3_REASONING_PREPARATION_NOTE_v1.md
    （契約ではなく準備調査ノート。Phase10-3契約本体は含まない）
```

```
利点:
    - Phase10-1/10-2（確定済み契約）とPhase10-3準備ノート（未確定
      論点整理）を一括して履歴に残すことで、「Phase10の進行過程
      全体」を1つの時点でスナップショットできる。
    - 将来Phase10-3契約を作成する際、準備ノートが既にGit履行下に
      あることで参照の追跡性が上がる。

リスク:
    - 候補Cは「確定済み契約（Contract、規範文書）」と
      「未確定の準備ノート（PREPARATION NOTE、論点整理のみで
      結論なし）」という性質の異なる2種類の文書を同一commitに
      混在させる。Phase10-3準備ノート自体が明記する
      「契約固定は次回裁定まで行わない」という制約と、
      このノートをGit上で"fix"する行為が、意味的に矛盾しないか
      という論点が生じる（本文書では判断しない）。
    - 候補Bと比較して差分対象が増えるため、commit差分の
      レビュー負荷が上がる。
    - Phase10-3準備ノートは将来内容が更新される可能性がある
      （論点が後で採択・固定されるとノート自体も更新対象になり
      うる）。一度commitした後の扱い（修正コミットを重ねるか、
      新規ファイルに切り替えるか）が未整理。

監査容易性:
    - 低〜中程度。契約文書2件+準備ノート1件の合計3ファイルが
      対象となり、各ファイルの性質（規範/調査）が異なるため、
      commit 1件の中で「何が確定し、何が未確定のまま記録された
      だけか」を読み手が区別する必要がある。
```

## 比較表（事実整理のみ・優劣判定なし）

```
                  候補A      候補B          候補C
対象ファイル数      1          2              3
commit粒度         最細       中             最粗
ロールバック容易性  最高       中             低
監査追跡の単純さ    最高       中             低（混在文書種）
Phase10-0との      一致       不一致         不一致
  パターン整合
准備ノートの        対象外     対象外         含む（性質の論点あり）
  Git化是非
```

## 結論

```
本文書はA/B/Cの利点・リスク・監査容易性を整理したのみであり、
いずれの候補も採択しない。結論は出さない。

固定作業（git add/commit/seal/push）の実施判断、および
A/B/Cいずれを選択するかは、次回の明示的な裁定を待つ。
```

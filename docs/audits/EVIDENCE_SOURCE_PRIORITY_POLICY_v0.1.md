# Evidence Source Priority Policy v0.1

Status: 設計提案（Human Gate確認前。まだ制度として固定しない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: DC_20260730_009（未検証文脈の隔離ルール確立）、REPOSITORY_DIVERGENCE_REPORT_v0.1.md

本文書は、複数のEvidence源が食い違う、またはどちらか一方しか参照できない場合に、どの情報源を優先する
かの方針を検討する。提示された優先順位案（Local Repository / Git Repository / MCP取得内容 / Decision
Ledger / Event Summary）をそのまま採用せず、まず妥当性を検証する。

---

## 1. 提示された順位案

```
1. Local Repository（一次資料）
2. Git Repository
3. MCP取得内容
4. Decision Ledger
5. Event Summary
```

## 2. 既存の制度との照合

DC_20260730_009（2026-07-30、きむら博士承認、Active）は、既に確認順序を規定している。

```
(1) 現在の会話履歴
(2) リポジトリ内の実ファイル（一次証拠）
(3) Decision Ledger
(4) Event Ledger
(5) その他の履歴
```

この既存ルールと今回の案には、以下の相違点がある。

- （現在の会話履歴）というカテゴリが、今回の案には存在しない。
- （リポジトリ内の実ファイル）が、今回の案では（Local Repository）と（Git Repository）の2段階に
  分割されている。
- （MCP取得内容）というカテゴリが新規に追加されているが、これがLedger類と何を指して別物なのかが
  今回の案では明確でない（下記4節で検討）。
- （Event Ledger）が（Event Summary）に呼称変更されている（実質的には同じ対象と考えられる）。

新しい優先順位policyを既存のDC_20260730_009と無関係に確定させると、2つの矛盾したルールが並存する
ことになる。したがって本文書は、既存ルールを置き換えるのではなく、既存ルールをより詳細化・具体化する
ものとして位置づける。

## 3. 各段階の妥当性検証

### 3.1 （現在の会話履歴）の欠落について

DC_20260730_009が（現在の会話履歴）を最優先に置いた理由は、それが最も直接的で改変の余地が少ない
一次情報だからと考えられる（本セッション内でユーザーから直接提示された事実は、伝聞・要約を経ていない）。
今回の案でこのカテゴリが省略されているのは、Option C監査という（会話の外側にある既存資産を評価する）
文脈を想定したためと考えられるが、省略した理由が明文化されていない。本文書では（現在の会話履歴）を
最上位として復元することを提案する（理由は3.2以降と同じ: 伝聞・圧縮を経ていない情報が最も検証しやすい）。

### 3.2 （Local Repository）と（Git Repository）の分割について

この分割自体は、REPOSITORY_DIVERGENCE_REPORT_v0.1.mdで確認した実態（Local環境には未コミットの
`relay_client.py`のような資産が存在する可能性がある一方、git履歴には存在しない）を踏まえると意味がある。
ただし、優先順位として（Local Repository（未コミットを含む作業ツリー） > Git Repository（コミット
済み））という順序には検証が必要である。

- Local Repositoryを優先する根拠: 最新の作業状態を反映しており、情報の鮮度が最も高い。
- Git Repositoryを優先すべき根拠: commit hash・author・timestamp・（設定されていれば）署名により
  改変不可能な形で固定されており、後から独立に検証できる。MoCKAの三原則（Structure/Record/
  Verification）のうちVerificationに直接対応する。

**この2つは（新しさ）と（検証可能性）という異なる軸であり、単純にどちらが優先とは言えない。** 本文書
では、目的に応じて使い分けることを提案する。

- （現在何が起きているか・何が最新の設計か）を知りたい場合: Local Repositoryを優先する。
- （監査・裁定の根拠として第三者が後から検証できる証跡）が必要な場合: Git Repositoryを優先する。
  Local Repositoryのみに存在する情報は、正式な監査・Decision Ledgerへの記録の根拠としては、
  git commitされるまで（未検証（Unverified Provenance））の注記付きでのみ扱う。

Option C監査（Task 1〜4）は後者（監査・裁定の根拠）に該当するため、Task 1〜4の文脈では実質的に
Git Repositoryを優先すべきである。ただし、その場合Local Repositoryにしか存在しない最新設計は監査
対象から抜け落ちる可能性があり、これはEVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.mdが提案する
（コミット単位での同期）を先に行うべき理由でもある。

### 3.3 （MCP取得内容）の位置づけについて

本セッションが実際に使用できるmocka_MCPツール群を確認すると、（MCP経由で取得できるもの）は実質的に
Decision Ledger（`mocka_decision_get`/`mocka_decision_list`）とEvent Ledger（`mocka_search`/
`mocka_list_events`）、およびessence・guidelines・todo・registryである。つまり、今回の案が4番目・
5番目に置いている（Decision Ledger）（Event Summary）も、実際には（MCP取得内容）の一部である。

したがって、（MCP取得内容）を独立した第3位のカテゴリとして置くことは、カテゴリの重複を生んでいる。
これは今回の案の中で最も検証が必要な点である。想定される解消案は次の2つ。

- 案A: （MCP取得内容）というカテゴリを廃止し、Decision Ledger・Event Ledgerをそのまま2つの独立した
  段階として扱う（DC_20260730_009の構造に一致させる）。
- 案B: （MCP取得内容）を、Decision Ledger・Event Ledger以外のMCP経由データ（例: MoCKA Registry
  （KN-004）、essence、guidelines）を指すものとして再定義する。

本文書では案Aを推奨する。理由: 案Bで指すデータ（Registry・essence・guidelines）は、Option C監査の
文脈では参照頻度が低く、優先順位の主要な争点にならない。無理に独立カテゴリとして残すよりも、
DC_20260730_009の既存4段階構造にそのまま合流させる方が、既存ルールとの一貫性を保てる。

### 3.4 （Decision Ledger）が（Event Summary）より優先されることについて

これは既存のDC_20260730_009の順序（(3)Decision Ledger優先(4)Event Ledger）と一致しており、妥当と
判断する。理由: Decision Ledgerは意思決定の確定記録（decision/rationale/impact等の構造化された
本文）であるのに対し、Event LedgerのshortSummary系フィールドは変更作業の圧縮要約であり、情報の
欠落・単純化が生じやすい。

## 4. 提案する優先順位（既存DC_20260730_009への統合案）

```
(1) 現在の会話履歴（本セッション内でユーザーから直接提示された事実）
(2a) Git Repository（コミット済み、hash・timestampで検証可能） - 監査・裁定の根拠として使う場合
(2b) Local Repository（作業ツリー、未コミット） - 最新状態の把握として使う場合、
     Task 1-4等の正式監査では（未検証）注記付きでのみ使用
(3) Decision Ledger
(4) Event Ledger（Event Summary）
(5) その他の履歴
```

(2)を(2a)/(2b)の2系統に分けたのは、（新しさ）と（検証可能性）という異なる目的軸を無理に1本の順位に
統合しないためである。（MCP取得内容）という独立カテゴリは廃止し、Decision Ledger/Event Ledgerに
統合する（3.3節案A）。

## 5. 本文書の位置づけ

本文書はDC_20260730_009を置き換えるものではなく、その具体化・詳細化の提案である。正式に制度として
固定する（今後のすべての監査・判断に義務的に適用する）には、Human Gate（きむら博士）の確認・承認を
要する。承認された場合、mocka_decision_writeでDecision Ledgerへ記録し、DC_20260730_009との関係
（統合/詳細化である旨）を明記することを推奨する。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task1-4切替後の追加指示に基づき作成。提示された順位案を検証し、DC_20260730_009との統合案を提示。 |

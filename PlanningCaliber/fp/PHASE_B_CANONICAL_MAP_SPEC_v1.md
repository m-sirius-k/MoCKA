# PHASE_B_CANONICAL_MAP_SPEC_v1

MoCKA Canonical Map — データモデル仕様書（骨格設計のみ）

作成日: 2026-06-21
作成根拠: S1〜S4-Extended（PlanningCaliber/MOCKA_TODO.json/ホーム直下mocka-*群/mocka-joints/mocka-archive/mocka-node2 の各監査）
本文書の位置づけ: 仕様確定のみ。実データ入力・台帳ファイル（CSV/JSON/DB等）の作成は次回Phase Bで行う。
非破壊原則: 本文書作成は新規ファイル作成のみであり、既存ファイルへの変更・削除・git操作は一切行っていない。

---

## 1. 目的の明記

Canonical Mapは「正本を新たに決める」ためのものではない。

S1〜S4-Extendedの監査結果が示したのは、MoCKAには既に多くの正本（GitHub origin付きの正規リポジトリ、活動継続中の実装等）が**既に存在している**という事実である。問題は「正本が無い」ことではなく、「どれが正本であるかを、本人以外（あるいは数ヶ月後の本人自身）が後から確認できる状態になっていない」ことにある。

危険な未統合資産はS4-Extendedの調査で発見されなかった（mocka-node2は本体への統合済み残骸と確定）。すなわち、MoCKAは「整理する力」自体は持っていた——node2の変更は本体に取り込まれ、不要になったスクリプトはdocs/archive/に移されていた。しかし、その**整理が行われたという事実そのものを記録・参照可能な形で残す仕組み（台帳化）が存在しなかった**。これが今回の一連の調査（S1〜S4-Extended）が繰り返し発見した「同名・規模差・更新停止」という現象（PlanningCaliber、MOCKA_TODO.json、ホーム直下runtime、mocka-ecosystem内クローン群等）の共通根因である。

したがってCanonical Mapの目的は以下の二点に限定される：

1. **資産管理台帳**: 既存の各資産（フォルダ・リポジトリ）について、「これは正本である／これは派生・凍結・実験である」という既に下された（あるいは下されるべき）判断を、検索可能な形で記録する。
2. **記憶の制度化**: S1〜S4-Extendedで行われたような調査・整理作業は、調査者個人の記憶やチャット履歴の中に留まる限り、時間が経てば失われ、同じ調査が繰り返される（実際に今回、複数の独立した古いMoCKA本体クローンが発見されたのはこのため）。Canonical Mapはこの調査結果を「意味記憶」として永続化し、次回以降の調査コストをゼロに近づけるための制度である。

Canonical Mapは判定機関ではなく、**既に行われた判定・既に存在する事実を記録する台帳**である。

---

## 2. レコード構造（フィールド定義）

以下のフィールドを最低限のレコード構造として確定する。値は今回入力しない（空のテンプレート定義のみ）。

| 項目 | 内容 | 補足 |
|---|---|---|
| Asset ID | 一意識別子 | 例: `AST-0001` のような連番、またはパスのハッシュ値。形式は次回Phase B着手時に確定してよい（本仕様書では「一意であること」のみを要件とする） |
| Path | 実パス | フルパス（例: `C:\Users\sirok\mocka-civilization`）。ドライブ違い（A:/C:等）がある場合は別レコードとし、Parentで関係を表現する |
| Name | フォルダ/リポジトリ名 | 表示用の名称 |
| Category | Repository / Archive / Experiment / Backup / Unknown | 詳細は本文書セクション3 |
| Status | Active / Frozen / Deprecated | Active=現在も更新され使われている。Frozen=意図的に更新を止めた記録として保持。Deprecated=用途が失われ、もはや参照する必要がないもの |
| Canonical | Yes / No / Pending | このパスが当該プロジェクト/資産の正本かどうか。Pending=判断材料が不十分で未確定 |
| Parent | 親資産（入れ子構造がある場合の参照先） | 例: mocka-joints/mocka-ecosystem/mocka-civilization の場合、Parentに「mocka-joints」のAsset IDを記録。入れ子でない場合は空 |
| Origin | Git Origin（あれば） | リモートURL、ローカルパスorigin、または「プレースホルダー未設定」等の状態も記録可能とする（S4で発見した`https://github.com/あなたのID/mocka-public.git`のような未置換プレースホルダーも記録対象） |
| Last Verified | 最終確認日 | 本日（2026-06-21）の調査で確認されたものは初期値としてこの日付を入れる |
| Evidence | 監査証跡 | どのセクター調査結果に基づく記録かを明記（例: `sector2_survey_20260621.txt`, `sector4_extended_node2_diff_analysis_20260621.txt`）。複数の調査に基づく場合は複数列記可 |

---

## 3. 分類軸の確定（Categoryの根拠）

S1〜S4-Extendedの調査で実際に出現したパターンに基づき、以下5分類を確定する。

- **Repository**: GitHub等に正規のoriginを持ち、現在も更新が継続している、または継続すべき独立プロジェクト。
  例: ホーム直下のmocka-civilization, mocka-core-private, mocka-docs, mocka-external-brain, mocka-knowledge-gate, mocka-outfield, mocka-public, mocka-runtime, mocka-transparency（S2で確認）。

- **Archive**: 凍結・参照専用として機能している、または機能すべきもの。命名や運用が「記録として残す」目的に合致しているもの。
  例: MoCKA本体のdocs/archive/配下（S4-Extendedでgoal_evolution_engine.py等が完全一致で格納されていたことを確認）。
  注意: mocka-archiveフォルダ自体はS4の調査で「アーカイブとして機能していない」（命名規則不統一、未コミットの現役同然リポジトリが混在）と判定されており、Archiveに分類されるべきだが実態が伴っていない代表例として記録すべき。

- **Experiment**: 試行・検証目的で作成され、用途終了後も削除されずに残存しているもの。
  例: mocka-archive内のverify_test, phase2c_verify, mocka_verify_tmp（S4）、mocka-joints/mocka-ecosystem（S3、過去のエコシステム整合性検証作業の産物）。

- **Backup**: 本来は正本と同期される設計だったが、現在同期が停止しているもの。
  例: A:\MOCKA_TODO.json（TODO_357）、C:\Users\sirok\runtime（vs MoCKA\runtime、S2特記事項6）。

- **Unknown**: 現時点で分類根拠が不十分なもの。判断を急がず「不明」のまま保持してよい。
  例: mocka-joints/mocka-infield（ホーム直下版との優劣未確定、S3）、mocka-pythonbridge（独立用途の可能性はあるが未確認、S3）。

---

## 4. 既知の登録対象（将来Phase Bで登録すべき対象一覧）

以下はレコードの**事前リストアップ**であり、本仕様書内では実際のレコード（値の入力）は作成しない。

### TODO_355対象（PlanningCaliber系）
- `C:\Users\sirok\MoCKA\PlanningCaliber`
- `C:\Users\sirok\planningcaliber`
- `C:\Users\sirok\planning-caliber`

### TODO_357対象（MOCKA_TODO.json系）
- `C:\Users\sirok\MOCKA_TODO.json`
- `A:\MOCKA_TODO.json`

### S2で発見（ホーム直下mocka-*群）
- ホーム直下の9件のRepository候補: mocka-civilization, mocka-core-private, mocka-docs, mocka-external-brain, mocka-knowledge-gate, mocka-outfield, mocka-public, mocka-runtime, mocka-transparency
- `C:\Users\sirok\runtime`（MoCKA\runtimeとの規模差、Backup候補）
- `C:\Users\sirok\mocka-infield`（ホーム直下版）
- `C:\Users\sirok\mocka-joints\mocka-pythonbridge`（未確認・現役の可能性、Unknown候補）

### S3で発見（mocka-joints）
- `C:\Users\sirok\mocka-joints`（集約コンテナ自体、Unknown）
- `C:\Users\sirok\mocka-joints\mocka-ecosystem`（歴史的スナップショット、Experiment候補）
- mocka-ecosystem内の各クローン: mocka-civilization, mocka-core-private, mocka-external-brain, mocka-transparency, MoCKA-KNOWLEDGE-GATE, MoCKA（いずれもParentにmocka-ecosystemを指定すべき入れ子構造）
- `C:\Users\sirok\mocka-joints\mocka_extension`（残骸候補）
- `C:\Users\sirok\mocka-joints\mocka-infield`（ホーム直下版との関係未確定）

### S4/S4-Extendedで発見（mocka-archive）
- `C:\Users\sirok\mocka-archive`配下の12サブフォルダ全件:
  tools_backup_20260215, ops_mocka, verify_test, _mocka_phase22_checkout, phase2c_verify,
  MoCKA_phase22_anchored, MoCKA_phase22_iso, mocka_verify_tmp, MoCKA_clean_test__FROZEN,
  MoCKA_node2, mocka-node2, mocka-organized（入れ子のmocka-organized/publicを含む）
- `mocka-node2`は**統合済み残骸として確定済み**（S4-Extended）。Canonical Map登録時はStatus=Deprecated, Canonical=No, Evidence=sector4_extended_node2_diff_analysis_20260621.txt として登録できる、数少ない「判断済み」レコードの一つ。

---

## 5. 運用ルール（今後の更新方法）

1. **新規発見時の登録義務**: 新しいmocka-*類似フォルダ・リポジトリが発見または作成された場合、Canonical Mapへの登録を必須とする。登録なしに「とりあえず置いておく」運用は、今回発見された散在パターン（同名・規模差・更新停止）を再生産する直接原因であるため禁止する。

2. **既存制度との関係づけ**:
   - **TODO_144（ファイル変更前後の強制記録制度）**は「ファイル単位」の変更履行を記録する制度である。
   - **TODO_154（全文書き換え時の関連ファイル整合性確認プロトコル）**は「変更作業の手順」を定めた制度である。
   - **Canonical Map（本仕様書）はこれらの「資産版」に相当する位置づけ**である。TODO_144/154が「個々のファイル変更が正しく記録・確認されたか」を扱うのに対し、Canonical Mapは「フォルダ・リポジトリという単位の資産が、どこに何個存在し、どれが正本か」を扱う、一段上の粒度の記録制度である。両者は競合せず、Canonical Mapのレコードの中で「最終変更がTODO_144に基づき記録されているか」を確認する際の参照先として機能する。

3. **Last Verifiedの更新責任**: 既存レコードについて再調査・再確認を行った場合は、Last Verifiedの日付を更新し、Evidenceに今回の調査ファイル名を追記する。古いEvidenceは削除せず併記し、判断の変遷を追跡可能にする。

4. **Pending/Unknownの扱い**: CanonicalフィールドがPending、またはCategoryがUnknownのレコードは、定期的な棚卸し（頻度は次回Phase Bで別途定める）の対象とする。これらを放置したまま新規資産の登録のみを続けることは、本制度の目的（識別可能性の確保）に反する。

---

## 次回Phase B着手時のための申し送り

本仕様書はデータモデル（フィールド定義・分類軸・運用ルール）を確定したものであり、実際の台帳（CSV/JSON/DB等の形式選定、保存場所、レコード作成）は未着手である。次回Phase B着手時に必要な作業は以下の通り：

1. 台帳の実装形式を選定する（本仕様書はCSV/JSON/DB等のいずれにも依存しない抽象的なフィールド定義としている）。
2. 本文書セクション4の「既知の登録対象」リストを基に、実レコードを作成する。各レコードのEvidenceには対応するsector*_survey_*.txt / sector4_extended_*.txt を参照として記入する。
3. mocka-node2のみ、S4-Extendedの調査結果に基づき「判断済みレコード」として直ちに登録可能（Status=Deprecated, Canonical=No）。他の大半は調査済みだが「正本かどうかの最終判断（Canonical=Yes/No/Pending）」は本仕様書では下していないため、登録時に再度検討が必要。

---

## 6. S5（TODO_354派生調査）で発見分の申し送り（2026-06-21・GL7ブロック原因調査中に発見）

TODO_354（拡張機能正本パスレジストリ確立）の作業中、GL7ゲートのブロック原因調査としてリポジトリ全体のdirty stateを分類した結果、Canonical Map登録対象となる構造異常が1件発見された。本セクションは申し送りのみであり、対象への変更操作（`.git`除去等）は今回実施していない。

### 発見対象: `PlanningCaliber/workshop/Orchestra_Project/backend`

| 項目 | 内容 |
|---|---|
| Asset ID | （次回Phase B登録時に付与） |
| Path | `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\Orchestra_Project\backend` |
| Name | Orchestra backend（Cloudflare Worker） |
| Category | **Structural Remnant**（既存5分類に当てはまらない新パターン。埋め込み`.git`による野良サブモジュール構造そのものが問題であり、内容物の正本性とは別軸の異常） |
| Status | Deprecated（構造として。内容物は後述の通りActive相当） |
| Canonical | No（gitlink構造自体が非正規。`.gitmodules`未登録） |
| Recommended Action | Convert to normal directory（通常フォルダ化。`backend/.git`を除去し、親リポジトリ（MoCKA）の通常ファイルとしてtrackする） |
| Parent | `PlanningCaliber/workshop/Orchestra_Project`（正本extension配下とは別系統） |
| Origin | なし（`git remote -v`で空。独立リポジトリとしての体裁を持たない） |
| Last Verified | 2026-06-21 |
| Evidence | 本セッションのGL7ブロック調査（`git ls-files -s`でmode 160000確認、`.gitmodules`不存在確認、backend単体のhistory確認、`worker.js`差分確認、本番Worker `https://orchestra-license.nsjpkimura-mocka.workers.dev` への読み取り専用GET probe結果） |

### 判明した事実の詳細
1. `git ls-files -s` で mode `160000`（gitlink）と確認。しかしリポジトリ直下に`.gitmodules`が存在せず、正規のsubmodule登録ではない（誰かが`backend/`配下で直接`git init`等を行い、親が誤ってgitlinkとして記録した状態）。
2. 親リポジトリが記録するgitlink SHA（`7165e0a2...`）と`backend`単体の現在HEADは完全一致。ポインタの不整合ではない。
3. `backend`単体は`remote`なし・コミット2件のみ（`feat: add backend worker.js and wrangler config`、`chore: relay worker関連 backend更新`）。独立プロジェクトとしてのライフサイクルの形跡なし。内部実装の延長と判断。
4. `git status`が`M backend`を示す直接原因は、`backend`単体の作業ツリー自体がdirty（`worker.js`に71行の未コミット差分、`.wrangler/`はビルドキャッシュで無害）だったため。
5. `worker.js`の未コミット差分（`MOCKA_DEV_MODE`バイパス、`POST /api/trial/start`、`GET /api/trial/status`）は、正本`extension/trial.js`・`extension/background.js`・`CHANGELOG.md`に既に統合済みの記述があり、かつ本番Cloudflare Worker（`https://orchestra-license.nsjpkimura-mocka.workers.dev`）への読み取り専用GETで`/api/trial/status`が`200 OK`・`{"ok":true,"status":"none"}`を返すことを確認済み。つまり**この差分は未統合の失われた実装ではなく、デプロイ済み機能のローカル残骸**（結果A確定）。

### 次回Phase B着手時の処理順序（R01確定・きむら博士指示）
1. TODO_356（GL7修正・CHANGE_START）
2. Phase B台帳構築開始
3. 上記backendをCanonical Mapへ正式登録（本セクションの内容をレコード化）
4. 登録後、正式なCHANGE_STARTを起票してから`.git`除去を実施
5. 野良サブモジュール解消

本日（2026-06-21）はbackendへの変更操作（`.git`除去等）は一切実施していない。次回着手時は上記順序を厳守すること。

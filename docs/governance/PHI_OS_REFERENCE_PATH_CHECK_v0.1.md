# PHI-OS Reference Path Check v0.1

位置づけ: くろこ作業指示(2026-07-03、Task-J)に基づき新規作成。Repository Health Report v1.0で「PHI-OSはDOI付きで学術的に参照されているが、対応するGitHubリポジトリが検索で確認できない」と指摘した箇所のフォローアップ。

本ファイルの範囲はLevel1のみである。確認するのは「公開されている参照経路が整合しているか」の一点にとどめ、非公開・名称変更・リンク切れ等の原因究明は行わない(原因究明はLevel2以降)。実装・コード変更は一切含まない。既存ファイルの上書きは行わない。v0.1とし、v1.0は名乗らない。

Level分離の明記: 本ファイルの記載事実は、2026-07-03に実施したGitHub検索API・Webサイト取得・Zenodoページ取得の結果に基づく。セッション記憶(MOCKA_OVERVIEW.json記載のpaper情報を含む)は補助的な背景情報としてのみ扱い、観察事実そのものとは明確に分離して記載する。原因の推測は「仮説」として明示し、断定は行わない。

---

## 第1部: 確認した4つの参照経路

sirius-labのREADMEはPHI-OSを「査読中の論文」としてDOI(10.5281/zenodo.19606271)付きで参照している。以下4つの参照経路それぞれについて、2026-07-03時点で確認できた内容を記録する。

### (1) GitHub - m-sirius-k/phi-os (単体リポジトリとしての存在確認)

- 確認方法: GitHub検索API(`user:m-sirius-k` / `phi-os in:name` / `phi_os in:name`、いずれも`is:private`含む)
- 結果: いずれの検索でも該当リポジトリは0件
- 補足: Repository Health Report v1.0作成時に、ローカルのMoCKAクローンに`phios -> git@github.com:m-sirius-k/phi-os.git`というgit remoteが設定されていることを確認済みである(本ファイルでの新規確認ではない)。このremoteが指す先が実在するかどうかは、今回のGitHub検索APIの範囲では確認できなかった

### (2) GitHub - sirius-lab-products内のphi-osディレクトリ

- 確認方法: `m-sirius-k/sirius-lab-products`リポジトリのcontents API
- 結果: `phi-os/`ディレクトリが実在する。`README.md`(206バイト)・`CHANGELOG.md`(71バイト、本ファイルでは内容未取得)を含む
- README.md全文:
  ```
  # PHI-OS

  mini MoCKA Series 統合神経系。

  ## 主な機能
  - 全製品間のIndexedDBハブ
  - DNA v3 Commit/Restoreプロトコル
  - Orchestra / Relay / Memory 連携

  ## ステータス
  Coming Soon
  ```
- ステータス表記: "Coming Soon"

### (3) Webサイト - sirius-labサイトおよびPHI-OSページ

- 確認方法: `https://m-sirius-k.github.io/sirius-lab/`および`https://m-sirius-k.github.io/sirius-lab/phi-os/`の取得
- トップページ: 実在・閲覧可能。製品説明セクションに"PHI-OS Persistent History Injection OS - the published research architecture powering MoCKA's governance loop. Research ->"という記載があり、相対リンク`./phi-os/`が張られている
- PHI-OSページ: 実在・閲覧可能。ステータス表記は"Research Preview"および"Peer-reviewed Research - Under Review"。GitHubへのリンクは`https://github.com/m-sirius-k/sirius-lab`(sirius-lab本体へのリンクであり、phi-os単体リポジトリへのリンクではない)

### (4) Zenodo - DOI 10.5281/zenodo.19606271

- 確認方法: `https://doi.org/10.5281/zenodo.19606271`の取得(`https://zenodo.org/doi/10.5281/zenodo.19606271`へ302リダイレクト、正常に解決)
- タイトル: "Ping, Hook, Lever: A Lightweight Architecture for Auditable Behavioral Control of Large Language Models"
- 著者: Kimura, Masahito(MoCKA Project所属と表示)
- 公開日: 2026-04-16
- ステータス表記: "Preprint"
- 関連リンク: DOI 10.5281/zenodo.19503666・10.5281/zenodo.19507632(関連プレプリントとして引用)
- GitHubリポジトリ・ソースコードへの直接リンク: このZenodoページの取得結果には見当たらなかった

---

## 第2部: 観察された事実(不一致点、原因は問わない)

以下は取得結果を突き合わせた結果として観察された事実のみを記載する。いずれも「なぜ食い違っているか」には踏み込まない。

### (a) DOIの参照先タイトルとsirius-lab README記載のタイトルが一致しない

sirius-labのREADME(GitHub上)は、DOI 10.5281/zenodo.19606271を「Silence Prohibition Protocol and Persistent History Layer」という論文として記載している。一方、このDOIが実際に解決するZenodoページのタイトルは「Ping, Hook, Lever: A Lightweight Architecture for Auditable Behavioral Control of Large Language Models」であり、両者の文字列は一致しない。

### (b) 「peer review」の記載箇所がZenodoページ自体には見当たらない

sirius-lab本体のREADMEは同論文を"Venue: Under peer review"と記載し、Webサイトのphi-osページも"Peer-reviewed Research - Under Review"と記載している。一方、Zenodoページ自体の取得結果でのステータス表記は"Preprint"のみであり、"peer review"に相当する記載はZenodoページの抽出結果には現れなかった。

### (c) PHI-OSのステータス表記が2つのリポジトリ間で一致しない

同一製品(PHI-OS)について、`sirius-lab-products`内の`phi-os/README.md`は"Coming Soon"、公開Webサイト(`sirius-lab`リポジトリがホストするGitHub Pages)は"Research Preview"/"Peer-reviewed Research - Under Review"と記載しており、両者のステータス表記は一致しない。

### (d) 単体リポジトリ`phi-os`への参照は、確認できた公開経路のいずれにも含まれていない

ローカルのgit remote(`phios`)が指す`phi-os.git`という単体リポジトリは、GitHub検索(`is:private`含む)で確認できなかった。ただし、Webサイト・Zenodoページのいずれも、この単体リポジトリへのリンクを持っていない。つまり、一般の訪問者が辿る経路(サイト -> GitHub、サイト -> DOI)には、この未確認リポジトリへの参照は含まれていない。

---

## 第3部: 結論(Level1の範囲)

一般公開されている参照経路(Webサイト -> GitHub、Webサイト -> DOI)自体は解決し、リンク切れ(404等)は確認されなかった。ただし、第2部の(a)(b)(c)の3点で、参照先の内容・ステータス表記が参照元の記載と一致しない箇所が確認された。ローカルのgit remoteが指す`phi-os`単体リポジトリの存在有無は、本Level1調査(GitHub検索API)の範囲では確認できなかった。

---

## 第4部: 仮説(参考、断定ではない)

以下は(d)について考えられる可能性の列挙であり、いずれも本Level1調査の範囲では検証できていない。優先順位付けも行わない。

- 非公開(private)リポジトリとして存在する可能性
- リポジトリ名が変更された、または別リポジトリ(例: sirius-lab-products内のディレクトリ)に統合された可能性
- ローカルでのみgit remoteとして設定され、GitHub上には作成されていない、または作成後に削除された可能性

---

## 第5部: 未確定事項

- (a)のタイトル不一致が、sirius-lab README側の記載の古さによるものか、DOIリンク先が異なるバージョン・別記録に変わったことによるものかは要確認
- (d)の`phi-os`単体リポジトリの実在有無は、GitHub側への直接確認(博士によるログイン確認等)がなければ本調査では解消できない
- `sirius-lab-products/phi-os/CHANGELOG.md`(71バイト)の内容は本ファイルでは未取得
- 本ファイルは参照経路の整合性確認にとどめ、(a)(b)(c)(d)いずれについても対応の要否・優先順位の判断は博士に委ねる

---

## 改訂履歴

- v0.1(2026-07-03): くろこ作業指示Task-Jに基づき新規作成。

# TODO_425 Extension Injection Check v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase C-1.4
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_COMMS_CHECK_v0.1.md](TODO_425_EXTENSION_SYNC_COMMS_CHECK_v0.1.md)(Phase C-1.3)

本書はPhase C-1.3で判明した「claude.ai上でOrchestra content.jsが注入されていない」原因を、リポジトリ側から確認可能な範囲(manifest.json/ファイル配置/差分)で切り分けた記録である。コード変更・manifest変更・commitは一切行っていない。

---

## 1. chrome://extensions確認

**未達(ツール制約、Phase C-1.1から継続)**。claude-in-chrome MCPは内部ページを読めず、computer-use経由のアクセスもuser_deniedのため、本項目はAIエージェント単独では完了できない。ただし、4節の発見により、Human確認で見るべきポイントを従来より具体化できた(5節参照)。

## 2. manifest.json確認(content_scripts.matches)

現在のリポジトリ正本(`PlanningCaliber/workshop/Orchestra_Project/extension/manifest.json`)を確認した。

```json
"content_scripts": [
  {
    "matches": ["https://claude.ai/*"],
    "js": ["content.js", "orchestra_search_bridge.js"],
    "run_at": "document_idle"
  },
  {
    "matches": [
      "https://chatgpt.com/*", "https://gemini.google.com/*",
      "https://www.perplexity.ai/*", "https://copilot.microsoft.com/*",
      "https://www.genspark.ai/*"
    ],
    "js": ["content_orchestra.js"]
  }
]
```

`https://claude.ai/*`は正しく`content.js`のmatchesに含まれている。**現在のリポジトリのmanifest.json自体には問題がない**。`version`フィールドは`"1.1.0"`。

## 3. content.js配置確認

`PlanningCaliber/workshop/Orchestra_Project/extension/content.js`は正本パスに存在する(canonical_paths、TODO_354確定と一致)。ファイルmtimeは`content.js`・`content_orchestra.js`・`manifest.json`いずれも`Jun 26 12:25`(TODO_354のPrivateリポジトリ移行時刻)で揃っており、**content.jsだけが個別に編集された形跡(mtimeのズレ)はない**。

## 4. content_orchestra.jsとの差分確認

`diff content.js content_orchestra.js`は1048行の差分となった。ただし、これは想定内である。両ファイルは対象AIサービスごとにDOM操作ロジックが異なるため、メッセージキャプチャ・入力欄検出処理などの本体部分はそもそも別実装であり、Phase Bで比較したのは`fetchLivingContext()`前後(TODO_293 Living Context注入部分)のみである(そこは1箇所のホスト文字列を除き同一と既に確認済み)。

**新たな確認事項(想定外の発見)**:

1. **content_orchestra.jsの先頭にUTF-8 BOM(`EF BB BF`)が存在する**(`content.js`にはBOMなし)。これは`.claude/CLAUDE.md`のTODO_155(UTF-8強制・BOM禁止)に抵触する未修正の技術的負債であり、本調査の主題(claude.ai注入問題)とは別件だが、Human Gate記録として残す価値がある(直接の実行時エラーの原因にはならない可能性が高いが、要注意事項として記録)。
2. **ユーザー提供スクリーンショットの行番号・コード内容(`content_orchestra.js:451`の`console.warn('[MoCKA] 入力欄が見つかりませんでした')`、447行目のホスト判定等)は、現在のリポジトリの`content_orchestra.js`と完全に一致した**(offset 440-459行を直接確認)。これは、**実際にブラウザにインストールされているOrchestra拡張の`content_orchestra.js`は、現在のリポジトリの内容と(少なくともこの範囲は)一致している**という強い状況証拠である。

## 5. 判定と仮説の更新

4節の2により、「インストール済み拡張が古い/異なるバージョンではないか」という仮説はcontent_orchestra.jsに関しては裏付けが弱まった(内容が一致するため)。これを踏まえると、より可能性が高い仮説は以下である。

**仮説(未確認・chrome://extensions確認で検証可能)**: インストールされている拡張のパッケージ(zipまたはDeveloper mode読み込みフォルダ)自体は現行版のcontent_orchestra.jsを含んでいるにもかかわらず、**manifest.jsonのcontent_scripts配列に`https://claude.ai/*`のエントリ(content.js用)が含まれない、より古いバージョンのmanifest.jsonのまま**である可能性。この場合、Chromeは最初からclaude.aiに対して`content.js`を注入する設定自体を持たないため、エラーも出さず「何も起きない」状態になる(実際に観測した状態と一致する)。

この仮説が正しければ、原因は「claude.ai対応(content.js分離)がリポジトリには存在するが、実際にインストール済みの拡張(Developer modeで未リロード、またはWeb Store側が未更新)にはまだ反映されていない」という**同期漏れ**であり、コード自体のバグではない。これは皮肉にもTODO_425の本題(Extension Configuration Sync Pipeline)と地続きの問題であり、「設定値の同期」だけでなく「拡張本体のリロード/更新も同期対象に含めるべきではないか」という論点を示唆する。

## 6. Human確認ポイント(更新・具体化)

chrome://extensionsで以下を確認していただきたい(5節の仮説を検証するため)。

1. Orchestra拡張の「詳細」を開き、**Developer mode読み込み(unpacked)か、Chrome Web Store経由のインストールか**を確認する。
2. Developer mode読み込みの場合: 拡張カードの「再読み込み」ボタン(循環矢印アイコン)を押し、その後もう一度claude.aiでの動作を試す。もしこれで動くようになれば、5節の仮説(古いmanifestのまま)が正しかったことになる。
3. Web Store経由の場合: 現在のバージョン番号を確認する。リポジトリの`manifest.json`は`"version": "1.1.0"`であり、これと一致しない場合、Web Store側が未更新であることが確定する。
4. いずれの場合も、読み込み元パスが正本パス(`...PlanningCaliber\workshop\Orchestra_Project\extension`)と一致するかを確認する。

## 未決定事項

1. 5節の仮説(manifest未反映による同期漏れ)は、chrome://extensionsでの実物確認が完了するまで確定しない。
2. BOM混入(4節1)はTODO_155違反の技術的負債として別途記録すべきだが、本書の範囲では修正しない(コード変更禁止の制約下のため)。
3. 「Developer mode拡張の再読み込みだけで直る」のか「manifest自体を最新化するコード変更が必要」なのかは、6節の確認結果次第で分岐する。

---

以上、Phase C-1.4完了。リポジトリ側(manifest.json/ファイル配置/差分)からの切り分けは限界に達し、5節の仮説検証にはHuman確認(chrome://extensionsでの拡張リロード試行含む)が必須となる。

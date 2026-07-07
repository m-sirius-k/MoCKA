# TODO_425 Extension Sync Design v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase B
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_INVENTORY_v0.1.md](TODO_425_EXTENSION_SYNC_INVENTORY_v0.1.md)(Phase A)

本書はPhase Aで発見した「Orchestra content.jsのみngrok URLを参照している」不一致の原因分析と、Extension同期アーキテクチャの権限境界設計を行う。実装・manifest変更・Extension配布変更・commitは一切行っていない。

---

## 1. 現行通信モデル

### 1.1 通信経路の実装形態

`content.js`(claude.ai用)・`content_orchestra.js`(chatgpt.com/gemini/perplexity/copilot/genspark用)ともに、**content script自身が直接`fetch()`を呼ぶ**実装であり、`background.js`へメッセージパッシングして代理フェッチさせる設計にはなっていない(コード確認済み)。

### 1.2 該当コードの比較

`fetchLivingContext()`関数(TODO_293由来)を両ファイルで比較した結果、以下の1点を除き完全に同一構造(コメント文言・変数名・ロジックまで一致)。

| 項目 | content.js(claude.ai) | content_orchestra.js(chatgpt.com等) |
|---|---|---|
| `MOCKA_HANDSHAKE_URL` | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/api/handshake` | `http://localhost:5000/api/handshake` |
| `MOCKA_ROLE_MAP` | `{chatgpt.com:R01, chat.openai.com:R01, claude.ai:R02}` | 同一(chatgpt.com/claude.aiのマッピングを両方保持) |
| リクエスト本体(`ai_id`/`role`/`scope`/`contract_version`) | 同一 | 同一 |
| エラーハンドリング | 同一(`console.warn('[MoCKA] Handshake failed:', e)`) | 同一 |

**注目点**: `content.js`の`MOCKA_ROLE_MAP`には`chatgpt.com`用のエントリが残っているが、`content.js`はmanifest.json上`https://claude.ai/*`にしかマッチせず、chatgpt.com上では実行されない。同様に`content_orchestra.js`側も`claude.ai`用エントリを保持している。両ファイルとも「本来自分が実行されないサイト向けのマッピング」を保持しており、コードが分岐時に個別最適化されず、同一ロジックがコピーされたまま残っていることを示す。

### 1.3 git履歴による確認

`mocka-workshop-private`リポジトリはTODO_354のPrivateリポジトリ移行時(2026-06-26、commit `c264dee`)に「initial snapshot」として作成されており、移行前の変更履歴(いつ・なぜngrok URLとlocalhost URLに分岐したか)はこのリポジトリのgit履歴からは追跡不能(blame上の最古コミットが移行コミット自体になっている)。

---

## 2. 原因分析

### 2.1 claude.ai固有制約の検証(CSPヘッダー実測)

「claude.ai固有の技術的制約でngrokが必要なのでは」という仮説を検証するため、claude.ai・chatgpt.comの実際のレスポンスヘッダーを取得し`Content-Security-Policy`の`connect-src`ディレクティブを比較した(2026-07-07実測)。

- **claude.ai**: `connect-src 'self' https://challenges.cloudflare.com`
- **chatgpt.com**: `connect-src 'self' *.blob.core.windows.net *.oaiusercontent.com api.mapbox.com ...(以下略、長大なホワイトリスト)`

両サイトとも、`connect-src`に`localhost:5000`・`*.ngrok-free.dev`のいずれも含まれていない。つまり、**もしページのCSPが拡張機能のcontent script発のfetch()にそのまま適用されるなら、claude.ai上ではlocalhostもngrokも等しくブロックされるはずであり、「ngrokだけ許可されclaude.aiで動く」という技術的説明にはならない**。

逆に、実際にはOrchestra拡張の`content_orchestra.js`はchatgpt.com上で`localhost:5000`への直接fetchを行い正常動作している実績があり(Phase A確認済み)、chatgpt.comのCSPにも`localhost:5000`は含まれていない。これは、Chrome拡張のcontent scriptが宣言済み`host_permissions`を持つ場合、ページ自体のCSPの`connect-src`制限を受けずにfetchできるというChrome拡張(Manifest V3)の既知の仕様(ページCSPからの拡張フェッチ免除)と整合する。

**結論(暫定)**: CSPレベルでの技術的制約は確認できず、claude.ai固有にngrokを必要とする根拠は見つからなかった。

### 2.2 実装差分比較

1.2節の比較の通り、`content.js`と`content_orchestra.js`はホスト文字列以外に実装上の差異が存在しない。サイト固有のワークアラウンド(例: リトライ処理・プロキシ経由・別ヘッダー付与)は両ファイルとも存在しない。

### 2.3 localhost利用時との機能差確認

`content_orchestra.js`が`localhost:5000`で実運用されている実績(chatgpt.com/gemini/perplexity/copilot/genspark向け)がある一方、`content.js`(claude.ai向け)で同じ`localhost:5000`を使った場合の実機動作は、本Phaseでは**実装・配布変更が禁止されているため検証していない**(未実施であり「差がない」と断定するものではない)。

### 2.4 判定: 必要条件か過去設計残骸か

以下の状況証拠から、**「過去設計残骸」である可能性が高い**と判断する。

- CSPヘッダー実測でclaude.ai固有の技術的必然性を示す証拠が得られなかった(2.1節)。
- `content.js`/`content_orchestra.js`は同一ロジックのコピーであり、サイト固有の分岐処理が存在しない(2.2節)。
- 両ファイルとも「自分が実行されないサイト」向けのrole mapエントリを不要に保持しており、コピー後に個別最適化(不要コードの削除)が行われた形跡がない(1.2節)。
- Node側(TODO_422-A対象)では`.env`のMOCKA_ENDPOINTが既にSSOTとして機能しており、ngrok URLは「サーバーへの外部到達点」全般を指す設計だったが、Chrome拡張側はローカル実行前提(`localhost:5000`)へ移行が進んでいる中、`content.js`だけ移行から取り残された可能性が高い。

ただし、git履歴が移行時点で途切れているため、**100%の確証(意図的仕様だった可能性の完全排除)はできない**。この点はきむら博士の記憶・意図確認が必要な未決定事項として残す(5節参照)。

---

## 3. 採用候補比較

Phase B指示のA/B/C 3案を、Phase Aで確認した権限境界(docs/governance/TODO_425_EXTENSION_SYNC_INVENTORY_v0.1.md 5節)と2.4節の原因分析を踏まえて比較する。

### A. ngrok依存を正式仕様化する場合

- 内容: `content.js`のngrok参照を意図的な仕様と確定し、外部公開エンドポイントとして正式管理する。
- 前提: 2.4節の原因分析が覆り、claude.ai固有の理由が確認された場合にのみ成立する。
- 必要な追加作業: なぜOrchestra拡張の中で`content.js`だけが外部公開経路を要するのかの技術的根拠を明文化し、Node側の`.env`(MOCKA_ENDPOINT)とは独立した「Extension外部公開エンドポイント」というSSOT区分を新設する必要がある。
- Human Gate対象範囲: 外部公開URL(ngrok tunnel)は無料枠で再起動毎に変わりうる不安定な値であり(TODO_421既確認)、値変更のたびに`content.js`の再配布(Web Store再審査)が必要になる。この構成を正式仕様化すると、Human Gateの発火頻度が「ngrokの再起動」という制御不能な外部要因に紐づいてしまう。
- 評価: 2.4節の判定(過去設計残骸の可能性が高い)と矛盾するため、**現時点では採用根拠が薄い**。

### B. localhost統一する場合

- 内容: `content.js`の参照先を`http://localhost:5000/api/handshake`に統一し、`content_orchestra.js`と揃える。
- 移行条件(案): (a)2.4節の未決定事項(意図的仕様でないことの確認)がきむら博士により確定すること、(b)claude.ai上での実機動作確認(本Phaseでは未実施)が事前に行われること。
- 影響範囲: `content.js`本体の変更のみ。`manifest.json`のhost_permissionsから旧ngrok URLを削除する場合はさらに一段重いHuman Gate(Web Store再審査)が必要になるが、削除せず併記のまま残す選択肢(実害はないが将来の混乱要因)もある。
- rollback条件(案): 変更後にclaude.ai上でLiving Context機能(ハンドシェイク)が失敗する場合、`content.js`のみを旧ngrok参照に戻す(`manifest.json`は変更しないため、host_permissions側のrollbackは不要)。
- 評価: 2.4節の分析と整合し、Node側(TODO_422-A)で採用したのと同じ「実態に合わせて重複/不整合を解消する是正修正」の枠組みに乗る。**現時点での推奨候補**(4節参照)。

### C. 別経路設計の場合

- 内容: `content.js`/`content_orchestra.js`双方とも直接fetchをやめ、`background.js`経由のメッセージパッシングに統一した上で、エンドポイント解決をbackground.js側に一元化する。
- 利点: 拡張全体でエンドポイント参照箇所が1つ(background.js)に集約され、将来値が変わっても変更箇所が最小化される。また将来的にHuman Authorization層(5節)を挟む際の単一介入点になる。
- 欠点: content script側の呼び出し方自体を変更するため、A/B案より変更範囲が大きい(3ファイル関係する変更になり、動作確認範囲も広がる)。
- 評価: 中長期的なアーキテクチャとしては魅力的だが、TODO_425の直接のスコープ(Phase A発見の不一致解消)を超える規模になるため、**将来の別TODOとして切り出す候補**とする(2.4節の是正だけならB案で十分)。

---

## 4. 推奨案

**B案(localhost統一)を推奨する。** 理由は2.4節の原因分析(過去設計残骸の可能性が高い)と、TODO_422-Aで確立した「実態に合わせた是正修正」という同一パターンに乗せられる点にある。ただし、以下2点が確定するまでは**実装に着手しない**。

1. 5節「未決定事項1」(claude.ai固有の意図的理由が本当に存在しないか)のきむら博士による最終確認。
2. B案の移行条件(b)(claude.ai実機での`localhost:5000`動作確認)。本Phaseでは実装・配布変更が禁止されているため未実施。

C案(background.js経由への一元化)は、B案で問題が解消した後の中長期改善候補として別途TODO化することを提案する(即時実装の対象にはしない)。A案は現時点の証拠と整合しないため採用しない。

---

## 5. Extension Capability境界(権限設計)

きむら博士指摘の原則を踏まえ、Extension設定同期を「設定配布」ではなく「権限経路」として位置付ける。

```
Extension Capability   (どのExtensionが、どのエンドポイント種別[local/public]を参照してよいか)
        ↓
Capability Schema      (上記を明文化した台帳。値そのものではなく「何を参照してよいか」の定義)
        ↓
Architecture Contract  (Capability Schema自体はAI通常Commit権限では変更不可。[[project_mocka_capability_layer_precondition]]のCapability Governance Rule v1を踏襲)
        ↓
Human Authorization    (Schema変更・manifest変更・Web Store再提出は、既存Human Gate統合層への権限移譲であり、新規承認系統を作らない)
```

この原則の具体化として、以下を将来のCapability Schema案(Phase C以降・未確定)の骨子として記録する。

| フィールド(案) | 説明(案) |
|---|---|
| `extension_id` | 5正本(`extension_canonical_paths`)のいずれか |
| `endpoint_class` | `local`(localhost:5000等) \| `public`(ngrok等外部公開) |
| `authority_level` | `docs/contracts/adapter_registry_v1.md`の`authority_level`概念を援用(本件はAdapterではなくExtensionだが同じ「誰がどの権限で」の枠組みを踏襲) |
| `distribution_impact` | `none`(開発者モードのみ) \| `repackage`(再パッケージのみ) \| `store_review`(Web Store再審査要) |

これは**設計の方向性のみ**であり、Phase Bの時点でSchemaそのものを確定・実装するものではない。

---

## 未決定事項

1. **(最重要・Phase Cへの前提条件)** `content.js`のngrok URL参照が意図的仕様か過去設計残骸かの最終確認をきむら博士に仰ぐ必要がある。2.4節の状況証拠(CSPヘッダー実測・コード比較)は「残骸」説を支持するが、git履歴が移行時点で途切れているため完全な確証ではない。
2. B案採用の場合、claude.ai実機での`localhost:5000`動作確認をどのタイミング・どの環境(開発者モード読込)で行うかの実施計画が未確定。
3. C案(background.js経由一元化)を将来TODO化する場合の優先度・着手時期は未確定。
4. 5節のCapability Schema案は方向性のみであり、フィールド定義の確定・[[project_mocka_human_gate_phase1a]]のPhase1B凍結解除との関係整理は未着手。
5. `manifest.json`のhost_permissionsから旧ngrok URLエントリを削除するか、当面併記のまま残すかは未確定(B案の範囲に含めるかどうかも含め要判断)。

---

以上、Phase B(設計判断)完了。実装(B案の`content.js`修正)は上記未決定事項1・2の確定後、あらためてCHANGE_START記録の上で着手する。

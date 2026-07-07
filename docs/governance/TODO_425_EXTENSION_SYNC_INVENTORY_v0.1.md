# TODO_425 Extension Sync Inventory v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase A
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
根拠: DC_20260707_017、TODO_422 Phase 1調査(E20260707_5690049345a67)で発見した「content.js/manifest.jsonは動的解決不可能」という切り出し理由の詳細化

本書はChrome拡張5製品(Relay/Orchestra/Memory/PHI-OS/mocka_bridge)の設定ファイルを棚卸しし、READ/WRITEの実態・SSOT候補・Human Gate対象点・既存Capability Governanceとの重複を整理する。コード変更・commit・設定変更は一切行っていない。設計判断はここでは確定せずSpec化のみに留める。

---

## 1. Extension関連設定ファイル一覧

対象は`MOCKA_OVERVIEW.json`の`extension_canonical_paths`(TODO_354確定)に基づく5正本。

| 製品 | 正本パス | エンドポイント参照ファイル |
|---|---|---|
| Orchestra | `PlanningCaliber/workshop/Orchestra_Project/extension/` | `content.js`(claude.ai用) / `content_orchestra.js`(chatgpt.com等用) / `background.js` / `manifest.json` |
| Relay | `PlanningCaliber/workshop/Relay_Project/extension/` | `background.js` / `manifest.json` |
| Memory | `PlanningCaliber/workshop/memory/extension/` | 該当なし(MoCKAサーバーへの直接参照を持たない) |
| PHI-OS(拡張本体) | `PlanningCaliber/workshop/phi-os/extension/` | `core/state-store.js` / `ui/options.js`(表示のみ) / `ui/options.html` |
| PHI-OS(Node側アダプタ、※拡張本体とは別コードベース) | `PlanningCaliber/workshop/phi-os/adapters/mocka-bridge.js` | TODO_422-Aで是正済み(env→config→localhost解決) |
| mocka_bridge(拡張) | `tools/mocka-bridge/extension/` | `background.js` / `content.js` / `manifest.json` |

**命名の注意**: `phi-os/adapters/mocka-bridge.js`(Node側モジュール、TODO_422-Aの対象)と`tools/mocka-bridge/extension/`(独立したChrome拡張製品)は名称が同じ「mocka-bridge」だが別物である。今後の設計・記録で混同しないこと。

---

## 2. 設定情報の現在の所有場所・実値

grep実測(2026-07-07)による確認結果。

| ファイル | ハードコードされているホスト | 種別 |
|---|---|---|
| Orchestra `content.js`(claude.ai用、463行) | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/api/handshake` | 外部公開(ngrok tunnel) |
| Orchestra `manifest.json`(host_permissions) | 同上ngrok URL + `http://localhost:5000/*` | 両方併記 |
| Orchestra `content_orchestra.js`(chatgpt.com等用、269行) | `http://localhost:5000/api/handshake` | ローカル |
| Orchestra `background.js`(45行) | `http://localhost:5000/api/gate/event/extension` | ローカル |
| Relay `background.js`(22行) | `http://localhost:5000/relay/ping` | ローカル |
| Relay `manifest.json`(host_permissions) | `http://localhost:5000/*` | ローカル |
| PHI-OS拡張 `core/state-store.js`(30行) | `http://localhost:5000/b/health` | ローカル |
| PHI-OS拡張 `ui/options.js`/`options.html` | `localhost:5000`(文言表示のみ、fetchなし) | ローカル(表示) |
| mocka_bridge拡張 `background.js`/`content.js`/`manifest.json` | `http://localhost:5000/*`(ask/orchestra/success/todo等複数エンドポイント) | ローカル |
| Memory拡張 | 該当ファイルなし | - |

---

## 3. SSOT候補確認

Node側(サーバー・アダプタ層)には既にSSOT解決チェーンが存在する。

```
.env(MOCKA_ENDPOINT)
  ↓ 優先
process.env.MOCKA_ENDPOINT (mocka-bridge.js)
  ↓ 未設定時
.claude/mocka_config.json (mcp_endpoint)
  ↓ 未設定時
http://localhost:5002/mcp (最終フォールバック)
```

これはTODO_218設計・TODO_422-Aで是正済みの経路であり、**Node側(file-guard.js等)の正本SSOTとして機能している**。

一方、Chrome拡張側(5正本のブラウザコード)には対応するSSOT機構が一切存在しない。5製品とも個別に`http://localhost:5000/...`をハードコードしており、値自体は現状すべて一致しているが、「同じ値を独立に4〜5箇所に書いている」状態であり、コードレベルでの共有元は無い。

**重要な発見(想定外)**: TODO_422の調査時点では「ngrok URLが4箇所に重複している」という前提だったが、実際にはOrchestra拡張の中でも
- `content.js`(claude.ai専用) → ngrok tunnel URL
- `content_orchestra.js`(chatgpt.com等) / `background.js` → `localhost:5000`

と、**同一拡張内で同一目的(Living Context handshake / gate通知)のコードが異なるホストを参照しており**、他4製品はすべて`localhost:5000`のみを使っている。ngrok URLを使っているのはOrchestra `content.js`と`manifest.json`のhost_permissionsのみであり、「Extension全体でngrok URLに統一されている」わけではない。この不一致がTODO_422当時の意図(旧設計の名残か、claude.ai固有の技術的理由か)かは本調査だけでは判別できない(4節・6節参照)。

---

## 4. 読取経路・書込経路確認

| 層 | 読取経路 | 書込経路 |
|---|---|---|
| Node/サーバー側(mocka-bridge.js等) | `process.env` → `fs.readFileSync(mocka_config.json)` | `.env`は手動編集、`mocka_config.json`も手動編集(自動生成スクリプトなし) |
| Chrome拡張側(5正本) | ソースコード中の文字列リテラル(ビルド時決定・実行時は不変) | ソースファイルを直接編集 → 拡張を再パッケージ → (Web Store配布分は)審査提出。開発者モード読み込み分はファイル保存のみで反映 |
| `manifest.json`のhost_permissions | Chromeがインストール/更新時に静的パース | ファイル直接編集のみ。動的注入不可(Manifest V3の仕様) |

拡張側には「実行時に外部設定を読みに行く」経路が存在しない(chrome.storageは`phi_connected_mode`等のトグル状態のみに使用されており、エンドポイントURL自体を保存する用途には使われていないことをoptions.js実測で確認済み)。

---

## 5. Human Gate対象になる変更点抽出

`.claude/CLAUDE.md`のTODO_354/TODO_364/Core System File関連規則、および今回実測したgit remote構成から、変更点ごとのHuman Gate要否を整理する。

| 変更対象 | 変更の重さ | Human Gate要否の根拠 |
|---|---|---|
| `manifest.json`(host_permissions追加/変更) | 高 | Chrome Web Store再審査が必須(公開済み拡張への権限変更は特に審査が厳しい)。ユーザー(既存インストール者)への権限再同意プロンプトも発生しうる |
| `content.js`/`content_orchestra.js`/`background.js`のエンドポイント変更 | 中〜高 | manifest.jsonのversion up + 再パッケージ + (Web Store配布分は)再提出が伴う。開発者モード読込のみなら再起動で反映されるが、Web Store配布との差分管理が必要 |
| Node側(`phi-os/adapters/mocka-bridge.js`等) | 低(TODO_422-Aで実績あり) | Chrome再配布を伴わず、DC承認+CHANGE_START/DONE記録で完結 |
| `.env`/`mocka_config.json`の値変更自体 | 中 | 値変更そのものは配布不要だが、Node側読取元が複数(app.py等)にまたがるため影響範囲確認が必要(TODO_421で既確認済み) |

**Extension同期は「便利機能」ではなく「設定権限経路」である**というきむら博士の指摘(前ターン)の裏付け: 拡張の設定変更はChrome Web Store側の審査・配布権限という、MoCKA内部のHuman Gateだけでは完結しない外部ゲートを経由する。したがって同期パイプライン設計は「いつ・誰が・どの承認を得てから」再パッケージ/再提出を実行するかを明示的にモデル化する必要がある。

---

## 6. 既存Capability Governanceとの重複確認

検索対象: `docs/governance/`、`docs/contracts/`配下。

| 既存文書 | 内容 | TODO_425との関係 |
|---|---|---|
| `docs/governance/MOCKA_EXTENSION_HUMAN_GATE_SUMMARY_v1.md` | **名称が紛らわしいが別物**。「MoCKA Extension」= Analytical Event/Index/Meta-Essence/Loopという*データモデル拡張層*の話であり、Chrome拡張(ブラウザプラグイン)とは無関係。DRAFT状態・実装未着手・統合未裁定 | 重複なし(名称衝突のみ。今後の文書命名で混同注意) |
| `docs/contracts/capability_registry_v1.md` | Relay(`phi_os/api/time_api.py`)のTime Query API 5能力を列挙する契約 | 直接の重複なし。だが「能力を列挙し、範囲外の追加を禁止する」という設計パターンは参考になる |
| `docs/contracts/adapter_contract_v1.md` | GPT/MCPがMoCKAへ接続する際のAuthority/Message/Capability/Audit 4層契約(GPT=Advisor、MCP=Transport) | 直接の重複なし(対象がGPT/MCPアダプタでありChrome拡張ではない)。ただし「Authority Contract」的な発想(誰が何をしてよいか)はExtension同期の権限設計にも応用できる |
| `docs/contracts/adapter_registry_v1.md` | Adapter登録制度(adapter_id/type/capability_set/authority_level/audit_policy) | 直接の重複なし | 
| [[project_mocka_capability_layer_precondition]](memory、DC未登録・Decision Ledger未登録の口頭合意) | Capability Governance Rule v1(5項目): Schema=Architecture Contract化/通常Commit権限では変更不可/専用Approval経路必須/変更者と付与対象の分離/AI自己権限拡張の禁止。Human Gate統合層と別の承認系統を作ってはならないという原則 | **最重要参考事項**。TODO_425でExtension Capability境界を設計する際、同じ原則(新しい承認系統を作らず既存Human Gateへ渡す前段として位置付ける/権限定義自体をArchitecture Contract化する)を踏襲すべき |

**結論**: TODO_425は既存のCapability Registry/Adapter Contract/Adapter Registry(GPT/MCP向け)と対象が異なるため直接の重複はない。ただし[[project_mocka_capability_layer_precondition]]で合意されたCapability Governance Rule v1の原則(新規承認系統の禁止・Schema自体のArchitecture Contract化)は、Extension Capability境界の設計にもそのまま適用すべき先行原則として扱う。

---

## 現状構造(まとめ図)

```
[Node/サーバー側]                       [Chrome拡張側(5正本)]
.env → mocka-bridge.js → mocka_config.json    Orchestra: content.js(ngrok) / content_orchestra.js・background.js(localhost)
  ↓ (TODO_422-Aで是正済み)                     Relay: background.js(localhost)
file-guard.js 等                              PHI-OS拡張: state-store.js(localhost)
                                               mocka_bridge拡張: background.js/content.js(localhost)
                                               Memory: 該当なし
      ※両者の間に共有の設定供給経路は存在しない
```

## 問題点

1. Chrome拡張側5製品には実行時の動的設定解決経路が存在せず、全てソースコード直書き。
2. Orchestra拡張内部でも`content.js`(ngrok)と`content_orchestra.js`/`background.js`(localhost)でホストが不一致(同一機能・異なる参照先)。他4製品はlocalhost一本。
3. `manifest.json`の変更はChrome Web Store審査という、MoCKA内部のHuman Gateだけでは完結しない外部承認ゲートを伴う。
4. Node側SSOT(TODO_422-Aで是正済み)とChrome拡張側の間に橋渡しの仕組みがない(手動転記に依存)。

## 権限境界

- Node側の設定変更(`.env`/`mocka_config.json`/アダプタコード): 現行のDecision Ledger + CHANGE_START/DONEプロトコルで完結(TODO_422-A実績)。
- Chrome拡張のソース変更: 上記に加えて「再パッケージ」「(Web Store配布分は)再提出」という追加の実行ステップが必要であり、これは今のCHANGE_START/DONEプロトコルが想定していない外部提出行為である。
- `manifest.json`のhost_permissions変更: 最も重い。ユーザーへの権限再同意を要求しうるため、Human Gateにおいても「他の変更より高い注意水準」を要求すべき。

## 推奨アーキテクチャ案(未確定・Phase B判断待ち)

現時点では2方向が考えられ、いずれもここでは決定しない。

- **案1(値の一本化のみ)**: Chrome拡張側はビルド/リリース時に`.env`の`MOCKA_ENDPOINT`相当の値から生成する軽量パッチスクリプトを導入し、手動転記をなくす。ただし「実行時の動的解決」ではなく「リリース時の静的生成」に留まる(Chromeの仕様上それ以上はできない)。
- **案2(Authority Contract化)**: [[project_mocka_capability_layer_precondition]]の原則を踏襲し、「どのExtensionが」「どの権限レベルで」「どのエンドポイント種別(ローカル/公開)を使ってよいか」をAdapter Registry的に台帳化してからパッチ生成に着手する。Orchestra `content.js`のngrok参照のような例外がなぜ存在するかを台帳上で明示できる。

## 未決定事項

1. Orchestra `content.js`がなぜ`localhost:5000`ではなく ngrok tunnel URLを参照しているのか(claude.ai固有の技術的制約か、旧設計の残骸か)は本調査だけでは未確定。次のPhase Bの前に、この差異が意図的仕様か放置された不整合かをきむら博士に確認する必要がある。
2. Chrome拡張のリリース同期を「CHANGE_START/DONE」の枠内に収めるか、Web Store提出を含む別の記録ライフサイクル(例: RELEASE_START/RELEASE_DONE)を新設するかは未決定。
3. Extension Capability台帳(案2)を新設する場合、[[project_mocka_human_gate_phase1a]]のPhase1B凍結解除前に進めてよいか、あるいはPhase1B解除を前提条件とすべきかは未確定(Capability Layer precondition memoryの「前提条件2点」と同じ論点)。
4. Memory拡張がMoCKAサーバーに一切接続しない設計が意図的なものか(未実装なだけか)は本調査の範囲外(該当ファイルなしを確認したのみ)。

---

以上、Phase A(現状調査)完了。Phase B(設計判断)はきむら博士の確認後に着手する。

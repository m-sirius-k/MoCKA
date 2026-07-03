# Concept Audit v0.1

位置づけ: 博士指示（2026-07-03）に基づき新規作成。MoCKA本体・PHI-OS・Orchestra・Relay・Memoryで使用される主要概念（Registry/Ledger/Memory/Archive/Catalog/Caliber）について、責務・境界・重複・依存関係を横断的に監査する。

本ファイルはコードではなく監査文書である。実装・コード変更は一切含まない。

**調査方法の注記（重要）:** 本監査は、Registry/Ledger/Memory/Archive・Catalogの4クラスタをそれぞれ独立した調査で洗い出した後、本ファイルでクラスタをまたいだ再点検を行う二段構成を取った。個別クラスタ内の重複判定（例: KN-004とrecurrence_registryは別物）は各調査ですでに「重複ではない」と結論づけられているが、クラスタをまたいだ重複（例: Registry調査とCatalog調査の両方に登場するファイル）は個別調査の対象外だったため、本ファイルの第2部で改めて検証した。Caliberについては本日先行して作成済みの`docs\caliber\CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`の調査結果をそのまま参照する（再調査はしていない）。

---

## 第1部: 現状把握（概念別インベントリ）

### 1.1 Registry

| 名称 | パス | 記録対象 |
|---|---|---|
| KN-004 Registry（6層） | `docs\governance\REGISTRY_*_v1.0.md` / `PlanningCaliber\workshop\registry_kn004\registry_store.py` | MoCKA内に存在する「すべての成果物」（DOCUMENT/EVENT/DECISION/POLICY/SPEC等）の存在確認台帳 |
| recurrence_registry | `data\recurrence_registry.csv` | 同一コンポーネント・同一タイプのイベント再発鎖（87件） |
| beta_registry | `structural\beta_registry.json` | 仮説的構造（β）の成長段階管理（観察→成長中→確立→制度化→衰退→消滅） |
| Impact Registry | `mocka-joints\mocka-ecosystem\MoCKA\audit\ed25519\governance\impact_registry.csv` | Phase14.6監査用の変更影響レベル記録 |
| PHI-OS schema-registry | `PlanningCaliber\workshop\phi-os\extension\core\schema-registry.js` | 拡張機能内artifact_typeの定義・バージョン管理 |
| SEO-OS CapabilityRegistry / CommandRegistry | `PlanningCaliber\workshop\seo-os\caliber\capability_registry.py` / `command_index\registry.py` | Workerクラス・コマンドの自動登録・依存関係管理 |
| ed25519 keys registry | `mocka-joints\mocka-ecosystem\MoCKA\governance\registry.json` | 署名鍵のactivated/revoked管理 |
| ai_capability_registry | `MOCKA_OVERVIEW.json`内`connector_framework`節 | 各AI（ChatGPT/Perplexity/Gemini/Claude）の能力・制約台帳。実装状況は不明・要確認 |

判定（Registry単体クラスタ内）: 各Registryは「存在管理」「傾向管理」「進化管理」「製品ローカル設定」という異なる責務を持ち、階層が異なるため重複ではない、とサブエージェント調査で確認済み。根拠: `mocka_mcp_server.py` L34-41でKN-004は「既存TODO管理とは完全に独立したドメイン」と明記。

### 1.2 Ledger

| 名称 | パス | 記録対象 |
|---|---|---|
| ledger.json（低レベル行動チェーン） | `runtime\main\ledger.json` | DECISION/EXPLORE/ANALYZE等の行動記録。SHA-256ハッシュチェーン（prev_hash/event_hash） |
| ledger検証・封印 | `scripts\ledger\ledger_verify.py` / `ledger_seal.py` / `anchor_update.py` | チェーン整合性検証・Governance Seal記録 |
| mocka_events.db（高レベル業務イベント） | `data\mocka_events.db`（SQLite、旧events.csv） | 11929件超の業務イベント（変更・設計・判断）。mocka_write_event/mocka_searchで操作 |
| PHI-OS Decision Ledger | `PlanningCaliber\workshop\phi-os\ise\decision_ledger.py`（データ: `data/ise/decision_ledger.jsonl`） | ISE（Intelligent State Engine）の状態遷移決定記録。verify_chain()で独自にチェーン検証 |
| Decision Evidence / audit_trigger | `docs\governance\DECISION_POLICY_v0.1.md` 第4節 / `phi_os/audit_trigger.py` | 裁定の正当性を事後検証可能にする証跡。event_gate（存在確認のみ）+ SQLiteトリガーによる直接書き込み検知 |

判定（Ledger単体クラスタ内）: サブエージョンは「ledger.jsonは低レベル行動追跡、mocka_events.dbは高レベル業務記録であり、別概念だが相補的」と判定した。ただし本ファイル第2部でこの判定を再検証する（後述）。

### 1.3 Memory

| 名称 | パス | 粒度 |
|---|---|---|
| Memory製品（Chrome拡張） | `PlanningCaliber\workshop\memory\extension\`（chrome.storage.local使用） | ブラウザセッション内の作業状態（ファイル・エラー・判断） |
| mocka-infield（独立リポジトリ） | `mocka-joints\mocka-infield\` | Constitution上の「Infield=internal memory」の理想形。**BINDING_GAP_REPORT_v1 GAP-O01で「ORPHAN（制度未接続）」と明記**、内容ほぼ空 |
| MoCKA/data/storage/infield（本体内部ストレージ） | `data\storage\infield\` | システム内部状態・イベント履歴の長期永続化 |
| working_memory.py | `structural\working_memory.py`（保存先: `data\working_memory.json`） | GL2における単一AI応答セッション内の作業キャッシュ（15フィールド） |
| Knowledge Assets / Reason Unit | `docs\governance\ACTIVATION_POLICY_v0.1.md` | 判断理由の構造化・制度的知識への昇格（Review Gate未実装） |

判定（Memory単体クラスタ内）: 4つは粒度が異なるため重複ではない、とサブエージェント調査で結論。ただしmocka-infieldはORPHAN状態（重複ではなく「設計されたが未接続」という別種の欠落）。

### 1.4 Archive / Catalog

| 名称 | パス | 役割 |
|---|---|---|
| TIC Archive層 | `data\tic\`（Layer2-4は未実装、TODO_205/206/207） | 外部技術知見の採用判定後の保管層（未実装） |
| Phase ARCHIVE層 | `docs\governance\phase3_simulation_sealed_v1.md` | Phase3実行設計の「非構造・参照停止・履歴領域」。2026-06-25博士裁定で確定 |
| Module ARCHIVED状態 | `docs\governance\MODULE_LIFECYCLE_v1.md` | モジュールライフサイクルの終端状態（巻き戻し不可） |
| MODULE_CATALOG_v1 | `docs\mocka3\MODULE_CATALOG_v1.md` | 制度OS全体モジュール（PHI-OS/Orchestra/Relay/Memory等12種）の一元登録台帳 |
| CATEGORY_REGISTRY_v2.0 | `docs\governance\CATEGORY_REGISTRY_v2.0.md` | MoCKA内6分類カテゴリ（DP/GV/IA/OA/KN/KA）の整理。**「KN_SERIES_LEDGER」を一次ソースとして参照（要確認・後述）** |
| MODULE_REGISTRY_MODEL_v1 | `docs\governance\MODULE_REGISTRY_MODEL_v1.md` | MODULE_CATALOGの登録情報を正本とするAudit/Health/Lifecycle連携基盤 |
| MODULE_INDEX_SPEC_v1 | `docs\governance\MODULE_INDEX_SPEC_v1.md` | MODULE_REGISTRY内モジュールの検索用インデックス（9種） |
| AUTOSEAL_SYSTEM_CATALOG_v1.0 | `PlanningCaliber\fp\AUTOSEAL_SYSTEM_CATALOG_v1.0.md` | AUTO_SEAL関連3経路+WATCHDOGの実装挙動を事実列挙 |

判定（Archive/Catalog単体クラスタ内）: Archiveは3つの独立発生概念（重複ではないが同語異義）。Catalogは階層構造（MODULE_CATALOG=マクロ層→MODULE_REGISTRY_MODEL=統合層→MODULE_INDEX_SPEC=検索層）であり重複ではない、とサブエージェント調査で結論。

### 1.5 Caliber（参照: `docs\caliber\CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`、本日先行作成）

6系統（テキスト濃縮chat_pipeline / PlanningCaliberスコアリング / ドリフト監視・ルーティング / Connector Caliber / vasAI BaseCALIBER / Technology Intelligence Caliber）が相互にコード共有なく並存。既にこの調査単体で「単一概念ではない」と結論済み。

---

## 第2部: 監査結果 — 名称が異なるが実質同じ役割になっているものの判定

ここからは各クラスタ内の判定を前提とした上で、クラスタをまたいだ再点検を行う。個別調査はそれぞれ別のサブエージェントが独立に実施しており、互いの結果を参照していないため、ここでの指摘は一次的な仮説であり、正式な統合判断には追加検証が必要である。

### 2.1 最重要候補: 「追記型・改ざん検知可能な証跡」パターンの並行発明（要検証）

以下の4つは、記録対象は異なるものの、「変更不可能な形で判断・行動の履歴を残す」という同一の設計パターンを、少なくとも3つの独立した実装として持っている。

| 実装 | 検証方式 | 記録対象 |
|---|---|---|
| `runtime\main\ledger.json` | SHA-256ハッシュチェーン（prev_hash/event_hash）、`ledger_verify.py`で検証 | 低レベル行動（DECISION/EXPLORE/ANALYZE） |
| `data\mocka_events.db` + `phi_os\audit_trigger.py` | SQLiteトリガーによる直接書き込み検知、event_gateによる存在確認 | 高レベル業務イベント（変更・設計・判断） |
| PHI-OS `data/ise/decision_ledger.jsonl` | 独自の`verify_chain()` | ISEの状態遷移決定 |
| CATEGORY_REGISTRY_v2.0が参照する「KN_SERIES_LEDGER」 | 不明・未調査 | シリーズ台帳の一次ソースとされているが、本監査のLedger調査では対象になっておらず実体未確認 |

**判定: 「同一の役割（改ざん検知可能な追記専用の証跡管理）が、対象範囲ごとに別々の名前・別々の実装で少なくとも3〜4回発明されている」可能性が高い。** これは典型的な「名称が異なるが実質同じ役割」のケースに該当しうる。ただし、各実装の記録粒度（低レベル行動／業務イベント／ISE状態遷移／シリーズ台帳）が本当に別物として維持すべきなのか、それとも単一の追記型ストア＋ビューの分離で代替できるのかは、本監査だけでは判断できない。TODO_364で確立された「経路増殖の回避（個別実装ではなく共有ヘルパーへの一元化）」という既存原則に照らすと、統合の検討価値があると考えられるが、**これは提案であり断定ではない**。KN_SERIES_LEDGERの実体調査が未実施である点も含め、要確認。

### 2.2 次点候補: KN-004 RegistryとMODULE_CATALOG_v1のスコープ重複疑い（要検証）

Registry調査はKN-004を「MoCKA内に存在するすべての成果物（DOCUMENT/EVENT/DECISION/POLICY/SPEC等）の存在確認台帳」と説明した。一方Catalog調査はMODULE_CATALOG_v1を「制度OS全体のモジュール（PHI-OS/Orchestra/Relay/Memory等12種）の一元登録台帳」と説明した。「モジュール」は「成果物」の一種であるはずだが、両調査ともに相手側のドキュメントへの参照や役割分担の言及がなかった。

**判定:** 両者が同じ情報（モジュールの存在・状態）を別々に二重管理している可能性を否定できない。ただし、KN-004がまだ設計フェーズ（`PlanningCaliber\workshop\registry_kn004\`配下で正式帰属先ディレクトリ未確定）である一方、MODULE_CATALOG_v1は既存のdocs配下で稼働している別軸の可能性もある。**この点は両ドキュメントを実際に突き合わせた検証が別途必要であり、本監査の範囲では「不明・要確認」に留める。**

### 2.3 その他のクラスタ: 重複ではないと判定したものの再確認

Registry内の各台帳（KN-004/recurrence/beta/製品ローカル）、Memory内の各記憶（Memory製品/Infield/working_memory/Knowledge Assets）、Catalog内の階層（MODULE_CATALOG/MODULE_REGISTRY_MODEL/MODULE_INDEX_SPEC）については、個別調査の「粒度・責務が異なるため重複ではない」という判定を妥当と考える。理由: いずれも「対象範囲」「更新頻度」「アクセスするコンポーネント」のいずれかが明確に異なっており、単なる名称のバリエーションではなく実際に異なる問い合わせ（「何が存在するか」「何が繰り返しているか」「どの状態にあるか」等）に答えている。

---

## 第3部: 名称は同じだが実質は別物（逆方向の混同リスク）

ユーザーの質問（名称が異なるが同じ役割）とは逆方向だが、監査中に発見した重要なリスクとして記録する。同じ単語が無関係な概念を指しているケースは、将来の設計・実装時に誤読・誤統合を招く危険がある。

### 3.1 「Archive」の多義性

- TIC Archive層（外部知見採用後の保管、未実装）
- Phase ARCHIVE層（非構造化・凍結された設計記録、活性化禁止）
- Module ARCHIVED状態（ライフサイクル終端、巻き戻し不可）

この3つは意味論的に無関係（何を・いつ・なぜ保管するかがすべて異なる）だが、同じ単語"Archive"を共有している。共通するのは「非アクティブな記録領域」という抽象度の高いイメージのみ。

### 3.2 「Caliber」の多義性

既存調査（`CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`）で確認済みの6系統。改めて言及するのみに留める。

### 3.3 「Registry」と「Catalog」の語彙境界の曖昧さ

CATEGORY_REGISTRY_v2.0.mdは名称に"Registry"を含むが、Catalog調査（分類目録機能）にも同時に該当した。「Registry」（登録台帳）と「Catalog」（分類目録）という2つの用語がMoCKA内で明確に使い分けられていない可能性がある。少なくとも1ファイルが両方の調査に引っかかったことがその兆候である。

---

## 第4部: 未確定事項・要確認一覧

- KN_SERIES_LEDGERの実体（ファイルパス・内容）は本監査で未調査。Ledgerクラスタの再点検（第2.1節）に必要
- KN-004 RegistryとMODULE_CATALOG_v1の役割分担・重複有無は未検証（第2.2節）
- mocka-infieldのORPHAN状態は本監査以前から既知の欠落（BINDING_GAP_REPORT_v1 GAP-O01）であり、本監査で新規に発見したものではない。修復提案（H-005）が既に存在するとサブエージェント調査で報告されているが、本監査ではその内容自体は確認していない
- Orchestra/Relay/Memory/PHI-OS個別製品が独自のarchive/catalog概念を持つかどうかは「未検出」という結果だったが、読み取り範囲の限界による可能性があり、断定はしない
- ai_capability_registry（AI能力台帳）の実装状況は不明
- 本監査は4クラスタをそれぞれ別のサブエージェントが独立調査したものを統合した二段構成であり、クラスタをまたいだ照合は本ファイルの第2部でのみ行った。より網羅的な監査のためには、発見された全ファイルを一つの表に集約した上でのファイル単位の全数突合が望ましいが、今回はスコープ外とした

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示に基づき新規作成。

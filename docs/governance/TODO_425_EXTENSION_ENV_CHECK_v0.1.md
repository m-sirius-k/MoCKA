# TODO_425 Extension Environment Check v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase C-1.1
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_VALIDATION_RESULT_v0.1.md](TODO_425_EXTENSION_SYNC_VALIDATION_RESULT_v0.1.md)(Phase C-1)

本書はPhase C-1で判明した「Orchestra拡張が接続ブラウザ上で実行された形跡がない」という結果を受け、原因を切り分けるための環境確認を試みた記録である。**結論を先に述べると、本セッションのツールセットではchrome://extensionsの内容を自動確認する手段がなく、4項目中3項目はHuman(きむら博士)による直接目視確認が必要**という結果になった。コード変更・manifest変更・commitは一切行っていない。

---

## 確認項目ごとの結果

### 1. Chromeの対象Profile確認

**未確認(ツール制約)**。claude-in-chrome MCPは接続ブラウザの内部情報(プロファイル名・パス)を返すAPIを持たず、`chrome://version`等の内部ページも次項の理由でアクセス不能。computer-use経由でのスクリーンショット取得も試みたが、ユーザー側で拒否された(下記3項参照)。

→ **Human確認が必要**: 実際にChromeを開き、右上のプロファイルアイコンで現在のプロファイル名を確認してほしい。

### 2. chrome://extensionsで確認(Orchestra Extension存在・有効状態・Developer mode状態・読み込み元パス)

**未確認(ツール制約)**。以下2つの自動化経路を試したが、いずれも失敗した。

- claude-in-chrome MCPで`chrome://extensions`へnavigateを試行 → 「Frame with ID 0 is showing error page」で拒否(Chrome拡張機能は内部ページ`chrome://`をスクリプト/読み取り対象にできない仕様。セキュリティ上の制約であり本ツール固有の不具合ではない)。
- 代替として`chrome-extension://<拡張ID>/manifest.json`への直接ナビゲーションを試行 → claude-in-chromeの`navigate`ツールが非http(s)スキームを正しく扱えず、`chrome-extension://...`が`https://chrome-extension//...`という無効なURLに壊れて navigateされてしまい、検証として成立しなかった(この経路は破棄し、結果を証拠として採用しない)。

→ **Human確認が必須**: `chrome://extensions`を直接開き、Orchestra(拡張ID: `lbjcmlkcjgjibcmlaokldopjokajjlgc`、`MOCKA_OVERVIEW.json`の`extension_canonical_paths`確定値)が一覧に存在するか、存在する場合は有効/無効・Developer mode・読み込み元パスを確認してほしい。

### 3. mocka_bridgeが動作している同一Profileか確認

**確認済み(Yes)**。Phase C-1の検証はすべて同一タブ・同一接続ブラウザセッション(claude-in-chrome MCP、deviceId: `9a90f68a-62b9-4741-8f22-5373adfc494f`)内で実施しており、mocka_bridge拡張(拡張ID: `doapadhfedmognoilmjieekfhijeadnf`)のcontent.jsが動作した観測(`[MOCKA] DNA注入完了`等)と、Orchestra拡張が動作しなかった観測は、物理的に同一のブラウザプロファイル・同一のページロード内で得られたものである。したがって「別プロファイルだから見えなかった」という原因は**排除できる**(この接続ブラウザ内で確認する限り、mocka_bridgeは動くがOrchestraは動いていない、という差が実在する)。

### 4. Orchestra正本パスとの差異確認

**未確認(前提条件未成立)**。2項目(chrome://extensionsでの読み込み元パス確認)ができていないため、実際にインストールされている実体が`MOCKA_OVERVIEW.json`の正本パス(`C:/Users/sirok/MoCKA/PlanningCaliber/workshop/Orchestra_Project/extension/`)と一致するかどうかも未確認。

---

## 試行した自動化アプローチと失敗理由(記録として残す)

| アプローチ | 結果 | 理由 |
|---|---|---|
| claude-in-chrome navigateで`chrome://extensions`へ | 失敗 | 拡張機能はChromeの内部管理ページを読み取り対象にできない(ブラウザのセキュリティ制約) |
| claude-in-chrome navigateで`chrome-extension://<id>/manifest.json`へ | 失敗・証拠不採用 | navigateツールが非http(s)スキームをhttps://prefix付きの不正なURLに壊してしまい、意図した検証ができなかった |
| computer-use経由でGoogle Chromeのスクリーンショット取得 | 拒否 | `request_access(["Google Chrome"])`がuser_deniedで拒否された。なお、たとえ許可されてもcomputer-useのブラウザアクセスは常に"read"tier(スクリーンショット閲覧のみ)であり、URLバーへの入力やクリックはそもそも実行できない制約がある |

---

## 判定と次のアクション

3項目(Profile名・chrome://extensions内容・読み込み元パス)がHuman確認待ちのまま、これ以上AIエージェント単独では切り分けを進められない状態に達した。1項目(同一Profile内での差の実在)のみ確認済み。

**きむら博士へのお願い(具体的な確認手順)**:

1. 実際にお使いのChromeで`chrome://extensions`を開く。
2. 一覧に「Orchestra」という名前の拡張機能があるか確認する。
3. あれば: 右下のトグルが有効(青色)になっているか、「Developer mode」がONになっているか、カードをクリックして「ID」と「読み込み元」のパスが`...PlanningCaliber\workshop\Orchestra_Project\extension`になっているかを確認する。
4. なければ: Developer modeをONにし、「パッケージ化されていない拡張機能を読み込む」からこの正本パスを選択してインストールしてほしい(既にWeb Store版がインストール済みの場合は、拡張ID衝突を避けるため、一時的に無効化してから開発者モード版を追加するか、Web Store版の状態を教えてほしい)。
5. 結果(存在有無・有効状態・パス)を教えていただければ、Phase C-1を再実施する。

---

以上、Phase C-1.1(環境確認)はツール制約によりAI単独では完了できず、Human確認待ちで一旦停止する。

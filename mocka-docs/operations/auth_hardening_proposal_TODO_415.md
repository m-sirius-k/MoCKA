# auth.py実認証キー化 - 調査結果・設計整理・実装案・検証計画 (TODO_415)

作成日: 2026-07-06
対象: gateway/auth.py, gateway/adapter_gpt.py等のアダプター群
段階: 調査・設計・計画提示のみ。実装変更は人間承認後に別途行う。

## 1. 現状調査

### 1.1 認証フローの再確認

`gateway/auth.py` の該当箇所:

```
13: VALID_KEYS   = set(filter(None, os.environ.get("MOCKA_API_KEYS",   "").split(",")))
14: HMAC_SECRET  = os.environ.get("MOCKA_HMAC_SECRET", "").encode()
...
44: key = request.headers.get("X-MoCKA-Key", "").strip()
45: if not key:
46:     abort(401, "X-MoCKA-Key header missing")
47: if VALID_KEYS and key not in VALID_KEYS:
48:     abort(403, "Invalid API key")
```

`VALID_KEYS`・`HMAC_SECRET` はいずれもモジュールのトップレベル(import時点)で一度だけ評価される。リクエストごとに再評価されるものではない。

### 1.2 「適当な値でも通る」原因の特定

47行目 `if VALID_KEYS and key not in VALID_KEYS:` は、`VALID_KEYS` が空集合(=`MOCKA_API_KEYS`未設定)の場合、`and`の左辺が`False`になり式全体が`False`になる。よって45-46行目の「ヘッダーが空でないこと」さえ満たせば、`key`の中身がどんな文字列であってもこのif文を通過してしまう。原因はこの1行のみで、他に迂回経路は無い。

### 1.3 環境変数の実際の読込状況(重要な追加発見)

`MOCKA_API_KEYS` と `MOCKA_HMAC_SECRET` の実際の設定状況を、`.env`ファイル・OS環境変数(Process/User/Machine全スコープ)の両方で確認した。

| 項目 | .envファイル | OS環境変数(全スコープ) |
|---|---|---|
| MOCKA_API_KEYS | 記載なし | 未設定 |
| MOCKA_HMAC_SECRET | **記載あり(値は設定済み)** | 未設定 |

さらに重要な点として、`gateway.py`および`auth.py`・各`adapter_*.py`はいずれも`load_dotenv()`を呼び出していない(`mocka_mcp_server.py`は呼び出しているが、これは別プロセス)。`MoCKA-START.bat`が`gateway.py`を起動するコマンドも環境変数を明示的に渡していない(`cd /d C:\Users\sirok\MoCKA\gateway && python -X utf8 gateway.py`のみ)。

**結論: `.env`に`MOCKA_HMAC_SECRET`が設定されているにもかかわらず、`gateway.py`のプロセスには一切読み込まれておらず、実質的に無効な設定になっている。** 何者か(過去のセッションと推測される)が`.env`にHMAC_SECRETを設定したが、`gateway.py`側の読込処理が実装されなかったため、意図した効果が発生していなかったと考えられる。

### 1.4 影響範囲

`gateway.py`は`adapter_gpt`等のアダプターモジュールを同一プロセス内にimportする構成のため(gateway.py:24-28)、`auth.py`だけでなく各`adapter_*.py`の`MOCKA_API_KEY`/`HMAC_SECRET`変数も同じ理由(未設定)で意図した値を持っていない。

## 2. 設計整理

### 2.1 開発/本番の分離状況

現状のコードには開発環境・本番環境を区別する仕組みが存在しない(`MOCKA_ENV`等のフラグは未実装、grep調査で確認済み)。`VALID_KEYS`が空の場合に全リクエストを通す47行目の挙動は、ローカル開発時の利便性を意図した設計と推測されるが、外部公開(gateway.nsjp.org)後も全く同じコードパスがそのまま有効になっている。つまり「開発時の利便性」と「本番の安全性」が同一コードパス・同一条件分岐に同居しており、環境による切替が存在しない。

### 2.2 本番でフォールバック認証を無効化できるか

現状の設計では不可能(そのような分岐が存在しないため)。改善案としては大きく2方向ある。

**案A: フォールバックを完全に撤廃し、fail-closed(拒否優先)にする**
47行目を `if key not in VALID_KEYS:` に変更する(先頭の`VALID_KEYS and`を削除)。`VALID_KEYS`が空の場合、いかなる`key`も`in`判定でFalseになるため、全リクエストが403で拒否される。「キー未設定=閉じる」という安全側の失敗モードになる。実装がもっとも単純。

**案B: 明示的な開発モードフラグを新設する**
`MOCKA_ALLOW_INSECURE_DEV`のような環境変数を新設し、これが明示的に`1`等に設定されている場合のみ現行のフォールバック挙動を許可する。本番では当該フラグを設定しない(=fail-closed)。開発時の利便性を残しつつ、本番との切替を明示化できる。

案Aの方がシンプルで、本番運用開始時点では開発時の利便性より安全側の失敗を優先すべきと考えるが、最終的な採否はきむら博士の判断とする。

## 3. 実装案(移行手順)

以下は承認後に実施する想定の手順であり、今回は実施しない。

1. 実キーを生成する(例: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)。複数キー運用(ローテーション)に備え、カンマ区切りで複数設定可能な現行のVALID_KEYS実装はそのまま活用する。
2. `.env`に`MOCKA_API_KEYS=<生成した実キー>`を追記する(既存の`MOCKA_HMAC_SECRET`行はそのまま維持)。
3. `gateway.py`の先頭(他のimportより前)に`from dotenv import load_dotenv` および `load_dotenv()` を追加する。`auth`・各`adapter_*`のimportより前に配置することが必須(モジュールレベルで環境変数を読むため、順序を誤ると反映されない)。
4. 案A採用の場合、`auth.py`47行目のフォールバック条件を撤廃する。案B採用の場合、`MOCKA_ALLOW_INSECURE_DEV`判定を追加する。
5. `gateway.py`(port:5010)の実行プロセスを再起動する(現行プロセスは環境変数変更前の状態のまま稼働し続けるため、コード変更のみでは反映されない)。
6. デプロイ手順: ローカル環境のみの変更のため、git commit(該当があれば)・`.env`はgit管理対象外であることを確認(`.gitignore`確認、TODO_390インシデントの教訓を踏襲)。
7. ロールバック手順: `.env`から`MOCKA_API_KEYS`行を削除(またはコメントアウト)し、`auth.py`の変更を`git revert`等で戻し、`gateway.py`プロセスを再起動する。案Aを採用した場合、ロールバックしない限り「キー未設定=全拒否」になる点に留意(旧来の「キー未設定=全許可」には自動的に戻らない、安全側の非対称性)。

## 4. 検証計画

変更実施後、以下7項目を実地確認する(TODO_266のgateway_verification_checklist.mdの認証セクションを更新する形で追記予定)。

1. `X-MoCKA-Key`ヘッダー無し → 401
2. 無効なキー(実キーと異なる値) → 403(案A採用時。現状はここが通ってしまっていたのが今回の修正対象)
3. 正しいキー → 200
4. `gateway.nsjp.org/api/v1/health` → 正常(200、認証不要パスのため変更の影響を受けないことの確認)
5. `POST /api/v1/event`(正しいキー使用) → 201、Gateway経由イベント投稿が正常に機能することの確認
6. 上記で投稿したイベントが`mocka_list_events`等MCP側から確認できること
7. `adapter_gpt.py`経由のGPT通信(実キーを`MOCKA_API_KEYS`に設定した状態)が正常に成功すること

## 5. スコープ外(今回は対応しない)

- Relay接続の確認・対応
- `openapi.yaml`のservers.url更新
- Copilot Studio登録作業
- HMAC署名検証(`MOCKA_HMAC_SECRET`)自体の本格運用化(今回はAPIキー方式の実効化のみを対象とし、HMAC部分は「.envに設定されているが読み込まれていない」という事実の記録に留める。HMAC運用化が必要な場合は別途タスク化する)

# MoCKA MCP Scope Separation Observation v0.1

位置づけ: `MOCKA_MCP_SCOPE_SEPARATION_DIAGRAM_v1.0`(博士提供テンプレート)の適用結果。テンプレート自体が示すLevel 0〜3の層構造・分離図(論理構造)は博士提供のものをそのまま用い、くろこが新たに層構造を設計・変更することはしていない。各層の状態は、events.db記録・本セッションで直接確認した設定ファイル・ユーザー申告のみに基づく事実記載とする。推測・設計・改善提案は含めない。

**アクセス境界の明記**: くろこはclaude.aiアカウント側のOAuth設定・Connected Apps管理画面を直接閲覧する権限を持たない。「Claude.ai側」に関する記載は既存記録・ユーザー申告に基づく間接情報であり、直接検証したものではない。

---

## 5.1 レイヤー別状態

| Layer | 状態 | 備考 |
|---|---|---|
| Level 0: Physical Transport Layer(HTTP(S)/ngrok endpoint/SSE・stream transport) | 到達性は確認されている(間接情報+直接情報) | event `E20260703_940641396d615`: ngrok Inspector(127.0.0.1:4040)で、claude.aiバックエンドからのPOST/GET `/mcp`に対し200 OKが返っていることを確認済み(間接情報)。Claude Code側は`~/.claude/settings.json`(`mcpServers.mocka`, `type: "url"`, `url: https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp`)により同一エンドポイントに接続する設定であることを本セッションで直接確認した。SSE/stream transportの明示的な指定は設定ファイル上には確認できなかった(`type: "url"`のみ)。 |
| Level 1: MCP Connection Layer(handshake/session establishment/authentication boundary) | handshakeは成立していると記録されている(間接情報) | event `E20260703_940641396d615`内の記述「claude.aiバックエンド側でのハンドシェイク成功後のツール一覧伝播失敗」という文言が、handshake自体は成立している前提であることを示す(間接情報、くろこが直接検証したものではない)。認証境界について: Claude Code側の設定(`~/.claude/settings.json`)には`type`と`url`のみが記載されており、トークン・認証ヘッダー等の記述はこのファイル自体には見当たらなかった。Claude.ai側の認証方式(OAuth)の設定内容はくろこの閲覧権限外であり確認していない。 |
| Level 2: Tool Registry Layer(tool list exposure/capability registry/permission filtering) | A/B間で明確な差が記録されている | event `E20260703_940641396d615`: 同一Connector(ID `724b556c-6b48-401e-91a3-035b280e9f30`)に対し、claude.ai Web chatのtool_searchは0件、同時刻のClaude Code CLIのtool_searchは17件全てを正しく返却したと記録されている。Claude Code側には`MoCKA/.claude/settings.local.json`・`~/.claude/settings.local.json`に個別ツール名を列挙した`permissions.allow`リストが存在することを本セッションで確認した(このリストが可視性にどう影響するかは、本調査の範囲では確認していない)。 |
| Level 3: Application Layer(Memory Caliber/Orchestra/Relay/PHI-OS) | 個別の層別の差分は本調査では確認できていない | 本調査で直接確認できたのはMCP Server Backend(`mocka_mcp_server.py`、ポート5002、ngrok経由公開)までであり、Memory Caliber/Orchestra/Relay/PHI-OSそれぞれの層でA/B間の差があるかどうかは、今回のA/B比較の情報源(2026-07-03記録・ユーザー申告・本セッション設定確認)からは確認できなかった。 |

---

## 5.2 断点リスト

- **断点の位置**: Level 1(MCP Connection Layer)とLevel 2(Tool Registry Layer)の間。event `E20260703_940641396d615`の記述「ハンドシェイク成功後のツール一覧伝播失敗」に基づけば、Level 1(handshake)までは成立し、Level 2(tool list exposure)で断絶が生じていると記録されている。
- **何が消えたか**: claude.ai Web chat側のtool_search結果において、Connectorが提供する17件のツール(Claude Code側では同時刻に全件確認されたもの)が、claude.ai Web chat側では0件として観測された。本日のユーザー申告でも、同一Connector経由でNotion関連ツールは表示されるがMoCKA関連ツールが表示されないという、同種の消失パターンが申告されている。
- **断点の再現範囲**: 2026-07-03の記録・本日のユーザー申告のいずれも「Claude.ai側(A)」の経路でのみ観測されており、「Claude Code側(B)」の経路では同種の断絶は本調査の情報源では確認されていない。

## 5.3 再現条件(ログベースのみ)

- 確認できた発生条件(2026-07-03記録): Connector「MoCKA Memory Caliber2.01」がclaude.ai Settings画面で「接続済み・全ツール許可」と表示されている状態で、claude.ai Web chatの新規セッション・既存セッションいずれでもtool_searchが0件を返した。同一時刻に同一Connector IDへ別クライアント(Claude Code CLI)から接続した場合は17件全て正しく返却された。
- 確認できた発生条件(本日のユーザー申告): claude.ai Web chatのtool_searchでNotion関連ツールは認識されるが、MoCKA関連ツールは認識されない状態が申告された。この申告について、本セッションでは再現条件の追加調査(サーバー側ログの再確認等)は行っていない。
- 上記2件が同一の再現条件によるものかどうかは、本調査の範囲では確認できていない(推測はしない)。

---

## 改訂履歴

- v0.1(2026-07-04): `MOCKA_MCP_SCOPE_SEPARATION_DIAGRAM_v1.0`に基づき新規作成。くろこ起草。

# Phase8-2: Runtime Bridge Contract v1 (Boundary Declaration Layer)

Status: DRAFT (Phase8-2。境界宣言のみ。変換・統合・正規化は恒久的に禁止)
Date: 2026-06-23

本文書はPhase8-3（[execution_orchestrator.py](../../semantic/query_engine/execution_orchestrator.py)）
の検証で露出した発見——trace_id namespace（Phase7-A4: Meaning Input
Layer）とcluster_id namespace（Phase7-B3/B4: Structural Recovery /
Order Normalization）が実データ上で別世界として存在する——を前提に、
Runtime Bridge Layerを**「接続装置」ではなく「境界認識レイヤ」**として
再定義する契約を固定する。

## 0. 核心原則

```
統合しないことでシステムを安定させる
```

trace_id空間とcluster_id空間は「別世界として正しく存在している」。
これはバグではなく構造的事実である。Runtime Bridgeの役割は、この
分割状態を**固定する**ことであり、橋渡しすることではない。

```
誤解: 接続するもの/変換するもの
正解: 接続しないことを保証する層
```

## 1. Namespace Registry（宣言のみ）

```
trace_id namespace    - Phase7-A4: member trace_id (例: UV1CD6DA52B2)
cluster_id namespace  - Phase7-B3/B4: canonical_cluster_id (例: 54c3b22f05dd23c7)
event_id namespace    - PHI-OS event_id (例: E20260328_001)
```

Registryは「どのnamespaceが存在するか」を宣言するだけであり、
namespace間の対応表・変換関数は一切提供しない（提供すること自体が
本契約の絶対禁止に該当する）。

## 2. Raw Event Ingress

- 外部から受信したイベントは**rawのまま保持**する。
- 受信時に行うのは「どのnamespaceに属するか」のタグ付けのみ
  （文字列パターン等の機械的判定。意味解釈は含まない）。
- ペイロード自体の変更・補完・正規化は行わない。

## 3. Routing Tagging

- イベントには所属namespaceのタグのみを付与する。
- タグ付けは分類であり、解釈ではない（「このイベントはtrace_id
  namespaceに属する」という事実の記録であり、「だからこう扱うべき」
  という判断は含まない）。
- 異なるnamespace間でのルーティング統合（例: trace_id namespaceの
  イベントをcluster_id namespaceの処理に流すこと）は行わない。

## 4. 絶対禁止（恒久的・確定）

```
trace_id <-> cluster_id の強制マッピング   禁止
自動補正                                    禁止
正規化                                      禁止
統一キーの生成                              禁止
namespace間の変換関数の提供                 禁止
```

これらはPhase8のいかなる将来フェーズによっても解除されない
（本契約の変更ではなく、Phase7全体の設計思想——非時間・非破壊・
collision保持——を守るための恒久的境界である）。

## 5. 出力構造

```
RawEvent = {
    payload: dict,          # 受信したそのままのデータ(変更なし)
    namespace: "trace_id" | "cluster_id" | "event_id" | "unknown",
    received_at: str | None, # 呼び出し側提供値。システム生成しない。
}
```

`namespace`が`"unknown"`の場合もエラーにしない（判定できないことを
正直に表現する。推測で埋めない）。

## 6. Phase7全構造の維持（再確認）

```
非時間構造                  維持（timestamp生成禁止を継続）
非破壊原則                  維持（rawペイロード変更禁止）
collision保持               維持（Runtime Bridgeはcollisionに関与しない）
Human Gate単一裁定点         維持
```

## 7. 段階フロー

1. **Phase8-2（本文書 + NamespaceRegistry/RawEventIngress最小スケルトン）**: 完了対象。
2. 以降（未着手・要承認）: 実際の外部接続手段（HTTP/MCP/ファイルwatch等）の具象化。

## 8. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。第4章の絶対禁止は他のいかなる変更からも独立して
維持される。

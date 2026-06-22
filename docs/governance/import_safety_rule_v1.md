# Import Safety Rule v1

Status: PROPOSED（INCIDENT_IMPORT_APP_SIDE_EFFECTを踏まえた制度規約案）
Date: 2026-06-22

## 規約

```
モジュールimport時に

Thread起動
Timer起動
DB更新
Git操作
外部通信(HTTP/ネットワーク)
外部プロセス起動(subprocess)

を発生させてはならない。
```

## 適用範囲

MoCKAコアシステムファイル全般(`app.py`、`relay/`配下、`phi_os/`配下、
`interface/`配下等)。新規ファイル作成時・既存ファイルレビュー時の
チェック項目として適用する。

## 背景

`INCIDENT_IMPORT_APP_SIDE_EFFECT`(`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`)
において、`app.py`を`import`するだけでThread起動・git commit・DB書込・
HTTP通信・外部プロセス起動が発火することが判明した。この問題は
「import ≠ 実行」という基本原則(Pythonの一般的な設計慣習であり、
かつPhase5で確立した「制度設計→実装」の順序とも整合する原則)が
守られていなかったことに起因する。

## 判定基準

あるコードが本規約に違反しているかどうかは、以下の問いで判定する。

> そのファイルを`import <module>`だけで読み込んだ場合に、
> Thread/Timer/DB/Git/外部通信/外部プロセスのいずれかが発火するか?

発火する場合、該当処理は`if __name__ == "__main__":`ブロック内、
または明示的に呼び出される初期化関数(例: `start_background_loops()`、
呼び出し元が`__main__`ブロックや明示的なセットアップ手順に限定される
関数)の内側に移動する必要がある。

## 許容される例外

- 読み取り専用の初期化(設定ファイルの読込、インメモリのオブジェクト
  構築、既存ファイルの存在チェックのみ)はimport時に行ってよい。
- Flask Blueprintの定義・`@app.route`によるルート登録はimport時に
  行ってよい(これはHTTPリクエストを受け付けるまで実際の処理を
  実行しない)。

## 検証方法

`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`の「9. Phase5.x-B2
追加監査」で用いた手法(Python `ast`モジュールによるモジュールトップ
レベル文の全数列挙+危険パターン照合)を、本規約の検証手段として
推奨する。

## 適用状況

- `app.py`: 本規約に違反している(6箇所、`INCIDENT_IMPORT_APP_SIDE_EFFECT.md`
  参照)。修正は人間ゲート承認後に実施予定。
- `relay/relay_kernel.py`他Phase5系ファイル: 本規約に準拠している
  (Repository/Kernel初期化はオブジェクト構築のみで、Thread/Timer/
  Git/外部通信を伴わない)。
- `phi_os/api/time_api.py`: 本規約に準拠している(RelayKernelの
  シングルトン生成はオブジェクト構築のみ)。

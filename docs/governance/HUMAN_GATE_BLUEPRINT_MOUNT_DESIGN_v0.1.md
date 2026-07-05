# Human Gate Blueprint Mount Design v0.1

位置づけ: フェーズ1(Human Gate配線)のPhase1Aスコープ(設計・事実整理のみ、コード変更は含まない)。
2026-07-05、フェーズ1着手前の合意に基づき作成。実装(app.pyへの実際のregister_blueprint実行、
/decision/approve系への変更)はPhase1Bとして別途、博士の承認を得てから着手する。

本文書は`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`(2026-07-03)と重複しない範囲に限定する。
同監査はGL7・Writer/Checker等からHuman Gate(`phi_os/human_gate.py`の関数)への**Python関数呼び出し
レベルの接続**を扱っており、本文書が扱う**Flask HTTPルートとしてのapp.pyへのマウント**とは
別の階層の問題である。同監査は「Approval Gate本体(human_gate.py)は宣言・接続・実装は確認できる」
としているが、これは`DECISION_POLICY_v0.1.md`のescalate_if_needed()がhuman_gate.pyの`submit()`を
直接importして呼ぶ経路の話であり、`/api/human_gate/*`がHTTP経由で外部到達可能かどうかとは無関係である。

---

## 第1部: 実態の明文化(事実確認のみ)

### 1.1 app.pyへのhuman_gate_bp登録状況

`app.py`全文をgrep(`Blueprint|register_blueprint`)した結果、以下11個のBlueprintが登録されている
(app.py:67-77)。

```
ai_session_bp / handshake_bp / dashboard_bp / reflection_bp / prediction_bp /
mentor_bp / commission_bp / context_bp / gate_bp / integrity_bp / time_api_bp
```

`phi_os.human_gate.human_gate_bp`はこのリストに含まれない。`app.py`内に`human_gate`という
文字列自体が一件も出現しない(grep 0件)。したがって`phi_os/human_gate.py`が定義する
`/api/human_gate/submit` `/api/human_gate/approve` `/api/human_gate/reject`
`/api/human_gate/status/<request_id>` `/api/human_gate/pending`の5エンドポイントは、
コードとして実装済み・動作確認可能な状態にはあるが、Flaskアプリ本体(port:5000)からは
現状HTTP到達不能である。

なお`app.py:61-62`で登録されている`gate_bp`(`phi_os/event_gate.py`)は名称が近いが別物であり、
これは「PHI-OS GATE v1」のEvent Gate統合(TODO記載: Phase3)を指し、Human Gate(承認/却下の
状態機械)とは無関係である。混同を避けるため、以降本文書では前者を「Event Gate」、
後者を「Human Gate」と呼び分ける。

### 1.2 既存の並行機構: /decision/approve, /decision/reject

`app.py:2246-2306`に、`phi_os/human_gate.py`とは別実装の承認/却下機構が既に稼働している。

* `/prevention/queue` (GET): `data/prevention_queue.json`の一覧を返す
* `/decision/approve` (POST): `payload.id`に一致するqueueエントリの`status`を`"approved"`に
  直接書き換える。呼び出し元の身元を検証する処理は存在しない
* `/decision/reject` (POST): 同様に`"rejected"`へ書き換える

両エンドポイントとも、リクエストが実際に人間(きむら博士)から送信されたことを検証する
認証・認可コードを持たない。`who_actor: "kimura_hakase"`という文字列は、誰がPOSTを送っても
無条件でイベントに記録される(app.py:2272)。これは「人間が実行した」という事実ではなく
「人間が実行したという体裁のログ」であり、両者は区別されない。

この事実は`gl7_execution_kernel_spec_v1.md`第10.3節が既に記録済みである
(「`app.py`には別の機構として『PREVENTION QUEUE + DECISION』が実在するが、GL7の
`pre_execution_check()`が返す`approved=True`の後続フローとは一切接続されていない」)。
本文書はこれに「かつ、この機構自体にも呼び出し元の人間検証がない」という追加観察を加える。

### 1.3 衝突チェック

`/api/human_gate/*`という命名空間は、app.pyの既存ルート一覧(grep結果、約120ルート)と
文字列衝突しない。既存の`/decision/approve`等ともパスが異なるため、Blueprintを
そのまま登録してもルート衝突は発生しない。

---

## 第2部: リスク評価

### 2.1 分類

現状は「Human Gateが存在しない」のではなく、「Human Gateという制御層(未強制)と、
Decision API(prevention_queue経由の実行層、直接到達可能)が、互いに独立に存在している」
という構造である。

| 経路 | 到達可能性 | 人間検証 | 状態機械 |
|---|---|---|---|
| `/decision/approve`, `/decision/reject`(既存) | HTTP到達可能(app.py稼働中) | なし(呼べば通る) | なし(status文字列を直接上書き) |
| `/api/human_gate/*`(phi_os/human_gate.py) | HTTP到達不能(未マウント) | 未設計(マウントされていないため議論以前) | あり(event-sourced、TRANSITIONS制約あり) |

### 2.2 GL7との関係

`gl7_execution_kernel_spec_v1.md`10.3が指摘する「Dry Run通過後のHuman Gate承認が未実装」
という欠落と、本文書が扱う「human_gate_bpの未マウント」は、同一の根本原因(Human Gate本体への
接続経路がどこからも張られていない)から生じる、異なる2つの現れである。

* GL7側の欠落: `structural/`側からHuman Gateへの**発信経路**がない(GL7が承認要求を送る先がない)
* app.py側の欠落: Human Gateの**受信経路**(HTTPエンドポイント)が外部に開かれていない

したがって、仮に本文書のPhase1B(blueprint登録)のみを実施しても、GL7からHuman Gateを
呼び出すコードが別途実装されない限り、GL7側の欠落(GL7-UNENFORCED-CONDITIONS-BUG)は
解消しない。両者は連動して設計する必要があるが、着手順序としては「受信経路を開く
(本文書のスコープ)」を先に安全な形で用意し、「発信経路を張る」(GL7側、別TODO)を
後続とするのが自然である。

### 2.3 バイパス可能経路の一覧化

現時点で、承認/却下の判断を「人間検証なしに」確定させられる経路は以下の通り。

1. `/decision/approve` (POST, app.py:2252) — 既存・稼働中
2. `/decision/reject` (POST, app.py:2287) — 既存・稼働中

`/api/human_gate/approve`等は現状HTTP到達不能なため、逆説的に「バイパスされようがない
(そもそも到達できない)」状態にある。Phase1Bでマウントする際は、この状態を後退させない
こと(＝マウントした瞬間に(1)(2)と同種の無検証バイパス経路を新たに増やさないこと)が
設計上の必須条件になる。

---

## 第3部: ゲート設計の前提条件(Phase1Bへの申し送り)

Phase1B(実装)に着手する際、以下を設計条件として満たすこと。

### 3.1 安全マウント(disabled-by-defaultフラグ)

```python
# app.py 想定差分(未適用・レビュー用)
# 63行目付近(integrity_bpインポートの近く)に追加
from phi_os.human_gate import human_gate_bp

# 77行目付近(register_blueprint群の末尾)に追加
app.register_blueprint(human_gate_bp)
```

読み取り専用エンドポイント(`/api/human_gate/status/<id>`, `/api/human_gate/pending`)は
マウントと同時に有効化してよい(状態を変更しないため、1.3で確認した通り既存ルートとも
衝突せず、リスクがない)。

書き込み系エンドポイント(`/api/human_gate/submit`, `/api/human_gate/approve`,
`/api/human_gate/reject`)は、環境変数によるフラグでdisabled-by-defaultとし、
明示的に有効化されない限り403を返すガードをBlueprint登録時ではなくルート関数内に
実装する(例: `HUMAN_GATE_API_WRITE_ENABLED`環境変数、既定値`"0"`)。この方式であれば
Phase1Bで`register_blueprint`自体は実行しても、書き込み経路は博士が明示的に
環境変数を切り替えるまで実行系に影響を与えない。

### 3.2 人間検証の保証点(未確定・要博士判断)

「呼び出し元が人間である」ことをどこで保証するかは、本文書では決定せず、Phase1Bの
検討事項として残す。候補:

* A. COMMAND CENTER UI(localhost限定・ブラウザ操作)からのみ許可し、外部からの直接POSTは
  拒否する(ネットワーク層での限定)
* B. 既存`/decision/approve`と同様、当面は「呼べば通る」ことを許容し、TODO_207
  (Human Gate UI)実装後にUI経由のみへ絞る段階的移行とする
* C. 何らかのトークン/セッション検証を新規実装する

現状の`/decision/approve`はB相当(検証なし)のまま稼働継続しているため、Phase1Bで
human_gate_bpをマウントする際に少なくともB以上の水準を満たすかどうかは、既存機構との
整合性も含めて博士の判断が必要。

### 3.3 既存/decision/approveとの関係整理(未確定・要博士判断)

Phase1Bで問うべき論点として記録する(本文書では結論を出さない):

* 既存`/decision/approve`・`/decision/reject`は温存し、`/api/human_gate/*`と並存させるか
* 既存機構を`/api/human_gate/*`へ段階的に統合(prevention_queueのPENDING項目をhuman_gate.py
  のevent-sourced状態機械へ移行)するか
* 統合する場合、`data/prevention_queue.json`(6箇所から投入)の移行コストをどう扱うか

---

## 第4部: 未確定事項

* 3.2/3.3は本文書の対象外(Phase1Bの検討事項として申し送り)
* GL7側の発信経路実装(GL7-UNENFORCED-CONDITIONS-BUGの候補C)は本文書のスコープ外。
  別TODOとして着手順序を博士判断で決定する必要がある
* AUTO_SEAL・Writer/Checker等、`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`が扱う他4系統との
  関係は本文書では扱わない

---

## 改訂履歴

* v0.1(2026-07-05): フェーズ1(Human Gate配線)Phase1Aスコープとして新規作成。

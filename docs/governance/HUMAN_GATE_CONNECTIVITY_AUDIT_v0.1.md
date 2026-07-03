# Human Gate Connectivity Audit v0.1

位置づけ: 博士指示（2026-07-03、Task-M）に基づき新規作成。GL7・Approval Gate・AUTO_SEAL・Knowledge Activation・Writer/Checkerの5系統について、Human Gateへの接続が「宣言→接続→実装→検証」のどの段階で止まっているかを調査する。

本監査は`GUARANTEE_MATRIX_AUDIT_v0.1.md`のG5（人間最終決定保証）で指摘した「複数の未接続点」を、系統別に詳細化したものである。実装は一切含まない。新規のコード調査は限定的であり、大半は本日までに作成した文書（WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1、ACTIVATION_POLICY_v0.1、DECISION_POLICY_v0.1、CONCEPT_AUDIT_v0.1）の再構成である。

---

## 第1部: 現状把握

### 1.1 4段階モデルの定義

本監査では、Human Gateへの接続を以下4段階に分解して評価する。

| 段階 | 意味 | 判定基準 |
|---|---| ---|
| 宣言 | 「ここでは人間の承認が必要である」という方針・設計意図が文書化されている | 制度文書・設計文書に明記されているか |
| 接続 | 宣言された箇所から実際にHuman Gate（human_gate.py等）を呼び出すコードパス・仕様が定義されている | 呼び出し元・呼び出し先の対応が設計または実装レベルで存在するか |
| 実装 | 接続されたコードパスが実際にコードとして書かれ、動作する状態にある | 実装済みと確認できる記述があるか |
| 検証 | 実装が実際に機能していることを事後的に確認する仕組み（ログ突合・カナリアテスト等）がある | `GUARANTEE_VERIFICATION_MATRIX_v0.1.md`のG5行の内容と整合 |

各系統は、この4段階のどこまで到達しているか、どこで止まっているかを判定する。

---

## 第2部: 提案 — 5系統の接続状況

### 2.1 総括表

| 系統 | 宣言 | 接続 | 実装 | 検証 | 止まっている段階 |
|---|---|---|---|---|---|
| GL7（Dry Run後のHuman Gate） | 済み | **未達** | 未達 | 未達 | **接続** |
| Approval Gate本体（human_gate.py） | 済み | 済み | 済み | 不明 | **検証**（最も先まで到達） |
| AUTO_SEAL | 要確認 | 要確認 | 要確認 | 要確認 | **調査不足のため判定不能** |
| Knowledge Activation（Review Gate） | 済み（統合方針まで） | 部分的（統合先は決定済みだが未実装） | **未達** | 未達 | **実装**（接続方針は決定済みという点でGL7より一歩進んでいる） |
| Writer/Checker | 済み（本日設計） | **未達**（設計のみ） | 未達 | 未達 | **接続** |

### 2.2 系統別詳細

#### (1) GL7

`gl7_execution_kernel_spec_v1.md`第10章（`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`作成時の調査による記載）によれば、GL7のDry Run通過後にHuman Gateへ処理を引き継ぐという設計意図（宣言）は存在するが、実際の接続コードは確認されていない（同spec 10.3で「未実装」と記載されているとの報告）。加えて、GL7自身のFORBIDDEN_EXECUTIONSが実行経路に未接続という別種の問題（同spec 10章、10.1）も存在し、Human Gate云々の前段階であるGL7自体の安全性メカニズムにも穴がある。

**止まっている段階: 接続。** 宣言はあるが、Human Gateへ処理を渡す具体的な呼び出し経路が定義・実装されていない。

#### (2) Approval Gate本体（phi_os/human_gate.py）

`ACTIVATION_POLICY_v0.1.md`第3節に「`human_gate`は既に『人間承認が必要な判断の停止点』として実装済みである」と明記されている。さらに`DECISION_POLICY_v0.1.md`第4段（escalate_if_needed）は、この既存human_gate.pyの`submit()`を再利用し、`gate_type=decision_policy`で区別する設計を採用しており、これは実際に「接続」が行われている実例である（TODO_401で確定）。

したがって、この系統は宣言・接続・実装のいずれも確認できる。唯一確認できないのは「検証」段階であり、`GUARANTEE_VERIFICATION_MATRIX_v0.1.md`のG5行で述べた通り、承認ログと実行ログを突合して「承認なき実行がゼロであること」を確認する専用の検証プロセスの有無は不明である。

**止まっている段階: 検証。** 5系統の中で最も先まで到達しているが、最後の検証の輪が閉じていない。

#### (3) AUTO_SEAL

`CONCEPT_AUDIT_v0.1.md`作成時のArchive/Catalog調査で、`AUTOSEAL_SYSTEM_CATALOG_v1.0.md`という文書の存在が確認され、AUTO_SEAL関連の実行経路として「AUTO_SEAL_50EVT」「MANUAL_SEAL」「auto_audit_loop（daemon）」「WATCHDOG_DAILY_SEAL」の3+1経路が事実列挙されていることが分かっている。しかし、この調査はAUTO_SEALの動作そのものを対象としており、**AUTO_SEALとHuman Gateの関係については今回の調査範囲に含まれていなかった。**

特に「auto_audit_loop（daemon）」という常駐プロセスによる自動実行経路が存在することが分かっている点は、Human-First原則（P3、`FIRST_PRINCIPLES_AUDIT_v0.1.md`参照）との関係を確認する必要がある。すなわち、AUTO_SEALの一部経路がHuman Gateを介さず自動的に完結する設計になっている場合、それが「そもそも人間承認を必要としない性質の作業（例: 定期的なハッシュ封印のような機械的処理）だから問題ない」のか、「本来は人間の目が必要な判断を含むにもかかわらず自動化されている」のかは、本監査だけでは判別できない。

**止まっている段階: 判定不能（調査不足）。** これは他の4系統と異なり、「Human Gateとの接続点があるかどうか」自体が未確認という、より根本的な情報不足の状態である。

#### (4) Knowledge Activation（Review Gate）

`ACTIVATION_POLICY_v0.1.md`第3節に、Reason Unit→Knowledge Assets昇格の審査点（Review Gate）について「既存の`phi_os/human_gate.py`との統合を採用する（別立てのGateは新設しない）」という**決定事項**が明記されている。これは「宣言」だけでなく「どこに接続するか」という接続方針まで確定している点で、GL7・Writer/Checkerより一歩進んでいる。

しかし同節「実装注記」に「既存`human_gate`のスキーマは、Reason Unit昇格審査専用のフィールド（既存Reason Assetsとの矛盾チェック結果、昇格可否の理由等）を持たない。統合実装にあたっては`phi_os/human_gate.py`のスキーマ拡張が必要になる見込みだが、本ファイルは方針決定のみを行い、拡張実装そのものは別途の実装作業として切り出す」と明記されており、実装は着手されていない（TODO_393-B以降の課題）。

**止まっている段階: 実装。** 接続先・接続方針は決定済みだが、実装（human_gate.pyのスキーマ拡張）が未着手。

#### (5) Writer/Checker

本日作成した`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`自体が、Checker PASS後にHuman Gateへ引き継ぐという設計を提案したばかりの段階である。同ファイルは「Checker PASSが形式的な追認に堕さないか」というリスクを自ら未確定事項として明記しており、Human Gateへの具体的な接続方式（どのタイミングで・どの情報を持ってHuman Gateへ渡すか）はまだ設計されていない。

**止まっている段階: 接続。** 宣言（設計文書）はできたばかりだが、接続の具体設計はこれから。

---

## 第3部: 総括

5系統のうち、最も進んでいるのはApproval Gate本体（human_gate.py、検証段階で停止）であり、これは既存の実装済みコンポーネントである。残る4系統（GL7・AUTO_SEAL・Knowledge Activation・Writer/Checker）は、いずれも「宣言」または「接続方針の決定」までは到達しているものの、Human Gate本体への実際の接続コードは未実装、という共通パターンを持つ。

これは`GUARANTEE_MATRIX_AUDIT_v0.1.md`第2.3節(b)で「構造的な傾向」の可能性として指摘した内容と一致する。すなわち、MoCKAはHuman Gateという**単一の実装済みコンポーネント**を持っているにもかかわらず、そこへ接続すべき新しい系統（GL7の実行後処理、Knowledge Assetsの昇格審査、Writer/Checkerの成果物確定）が増えるたびに、接続作業自体が後回しになる傾向があるように見える。**これは断定ではなく、5件という限られたサンプルからの傾向観察である。**

AUTO_SEALについては、他の4系統と異なり「そもそもHuman Gateとの関係を持つべき性質の処理なのか」という前提の確認が必要であり、優先度の高い追加調査対象として記録する。

---

## 第4部: 未確定事項

- AUTO_SEALとHuman Gateの関係は本監査では判定不能。auto_audit_loop（daemon）が人間承認を要する種類の判断を含むかどうかは追加調査が必要
- GL7 spec 10章・10.1・10.3の内容は`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`作成時の調査結果の引用であり、本監査で実ファイルを再確認していない
- 「構造的な傾向」という第3部の指摘は5件のサンプルに基づく観察であり、統計的な根拠を持つものではない
- Approval Gate本体の「検証」段階の欠落（承認ログと実行ログの突合）を埋める具体的な設計は、本監査の範囲外（`GUARANTEE_VERIFICATION_MATRIX_v0.1.md`と合わせて別途検討が必要）

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Mに基づき新規作成。

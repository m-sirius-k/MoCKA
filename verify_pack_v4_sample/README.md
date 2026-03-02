\# MoCKA Governance Model v4

\## Verifiable Multi-Signature Responsibility Layer (2-of-3 Threshold)

\## 検証可能なマルチシグ責任証明層（2-of-3閾値モデル）



MoCKA v4 is a fully reproducible governance sample demonstrating a 2-of-3 multi-signature responsibility model built on Ed25519, canonical JSON, and SHA256 anchoring.



MoCKA v4 は、Ed25519・Canonical JSON・SHA256アンカーを基盤とした

2-of-3 マルチシグ責任モデルを実装した完全再現可能なガバナンス実証サンプルです。



This repository proves a simple principle:



No hidden state.  

No internal memory claims.  

No unverifiable declarations.  

Only cryptographic evidence.



本リポジトリが示す原則は明確です。



内部状態に依存しない。  

自己申告を証拠としない。  

検証不能な宣言を信用しない。  

暗号学的証拠のみを根拠とする。



The sample includes a complete verification pack with an append-only key registry, revocation handling, threshold signature enforcement, and attack simulations.



本サンプルには、追記専用キー台帳、revoke（失効）処理、

閾値署名強制、攻撃シミュレーションを含む

完全な検証パックが含まれています。



---



\## What This Demonstrates / 本サンプルが実証するもの



\- Threshold multi-signature verification (2-of-3)

\- Append-only key registry with revoke support

\- Canonical JSON enforcement

\- Deterministic verification using Python + cryptography

\- Byte-level tamper detection via SHA256



・2-of-3 閾値マルチシグ検証  

・追記専用キー台帳と失効処理  

・Canonical JSON 強制  

・Python + cryptography による決定論的検証  

・SHA256 によるバイト単位改ざん検出  



This is not a conceptual mockup.

It is an executable, externally verifiable artifact.



これは概念実験ではありません。

外部から完全再検証可能な実行可能アーティファクトです。



---



\## Included Verification Samples (5 Total)

\## 含まれる検証サンプル（全5種）



1\. valid\_2\_of\_3.json  

&nbsp;  ✔ PASS  

&nbsp;  Demonstrates correct 2-of-3 verification using active keys only.  

&nbsp;  有効鍵のみを使用した正しい2-of-3署名検証。



2\. insufficient\_signature.json  

&nbsp;  ✖ FAIL (Insufficient signatures)  

&nbsp;  Demonstrates threshold enforcement.  

&nbsp;  閾値未満の署名を拒否。



3\. duplicate\_signer.json  

&nbsp;  ✖ FAIL (Duplicate signer)  

&nbsp;  Demonstrates signer uniqueness enforcement.  

&nbsp;  署名者重複の検出。



4\. revoked\_key\_used.json  

&nbsp;  ✖ FAIL (Revoked key used)  

&nbsp;  Demonstrates revocation policy enforcement.  

&nbsp;  失効鍵の使用検出。



5\. canonical\_tamper.json  

&nbsp;  ✖ FAIL (Invalid signature after payload modification)  

&nbsp;  Demonstrates byte-level tamper resistance.  

&nbsp;  署名後の改ざん検出。



Each failure mode isolates a specific governance invariant.  

各FAILは個別のガバナンス不変条件を検証します。



---



\## Why This Matters / なぜ重要か



Most systems rely on internal assumptions or administrative trust.

MoCKA v4 replaces assumption with verification.



多くのシステムは内部状態や管理者信頼に依存します。

MoCKA v4 はそれを検証可能性に置き換えます。



Any external engineer can:



\- Recompute signatures

\- Verify registry state

\- Confirm revocation enforcement

\- Reproduce the SHA256 anchor



外部の第三者は以下を再計算できます。



・署名の再検証  

・台帳状態の確認  

・失効処理の検証  

・SHA256アンカーの再計算  



If one byte changes, verification fails.  

1バイトでも変更されれば検証は失敗します。



---



\## Cryptographic Stack / 暗号技術構成



\- Ed25519

\- Canonical JSON (sorted keys, no whitespace variance)

\- SHA256 artifact anchoring

\- UTC timezone-aware timestamps

\- Python 3.10+

\- cryptography library only



Docker不要。外部サービス不要。隠れた依存なし。



---



\## Quick Start / 実行方法



pip install cryptography  

python verify\_all\_v4.py



Expected result / 期待結果



1 PASS  

4 FAIL (by design)



If results match, the governance model is intact.  

結果が一致すれば、制度は完全に成立しています。



---



\## Artifact Integrity Anchor / 封印アンカー



Artifact: verify\_pack\_v4\_sample.zip  

SHA256: d5995d34e3cb651dbd00ba9d5acae52aaafbc67cdf27ba502de7893830221fea



If the computed SHA256 differs, the artifact must be rejected.  

算出値が一致しない場合、そのアーティファクトは無効です。


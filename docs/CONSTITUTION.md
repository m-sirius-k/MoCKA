# MoCKA Constitution（憲法層）

確定日: 2026-06-12

本書はMoCKAの変更不可の根本原則を定める。Institution層・Operation層の規程は
本憲法に矛盾してはならない。

## 根本原則

1. AIを信じるな、システムで縛れ
   - 自己申告ではなく、構造（チェック関数・スキーマ・権限定義）によって行動を制約する。

2. Event ledger is append-only
   - events.dbへの記録は追記のみ。改変・削除は行わない。
   - 記録なき作業はMoCKAとして存在しない。

3. All decisions preserve 5W1H
   - who/what/where/why/how/when を必ず記録する。

4. Human Gate for critical operations
   - seal, core_file_edit, external_serviceなど重要操作はHuman Gateの承認なしに
     AI単独で完了させてはならない。

これらはInstitution Contract（data/institution/）の上位規範であり、
Contractの変更自体もこの憲法に違反してはならない。

# GL7 Encoding Remediation Evidence (2026-07-14)

Artifact Type: Remediation Evidence Log (READ ONLY verifiable)
Status: EVIDENCE RECORD
Authority: Human Gate Approved (きむら博士 / 判断(a) GL7 ブロッカー解消先行工程)
実行者: くろこ(Claude-opus-4-8)
Date: 2026-07-14

## Purpose

CONT-GL7-PROMOTION-GATE-v1.0 Decision Record 正式化の前提として、GL7 が
encoding_mismatch と判定した root 直下12件を UTF-16LE(BOM FF FE) から UTF-8 へ
再エンコードした工程の変更前後証跡を保存する。GL7 バイパスは行っていない。

## Scope

- 対象: GL7 abort が encoding_mismatch として列挙した12件のみ。
- 実施: 各ファイルを bytes 読込 -> decode('utf-16') -> encode('utf-8') -> write_bytes。
  BOM 除去・改行変換なし(write_bytes)・本文一致検証あり。
- 非対象(未変更): diff_full.txt / full_file_map.txt / untracked.txt(root では
  UTF-16LE だが GL7 走査対象外。承認範囲外のため保持)。

## Before/After Evidence (SHA-256)

| file | before_bom | before_bytes | before_sha256 | after_bom(hex) | after_bytes | after_sha256 | content_preserved | utf8_no_bom |
|------|-----------|--------------|---------------|----------------|-------------|--------------|-------------------|-------------|
| blueprint_registration_map.txt | fffe | 1336 | 753aee97...604585e | 6170 | 667 | 6da77af4...b9bf01 | true | true |
| decision_gate_boundary_map.txt | fffe | 18334 | e2586240...e9c2f5 | 6170 | 9888 | 8d9f2168...f512598 | true | true |
| decision_hg_chain_map.txt | fffe | 88544 | 75b2e134...fcf3fe | 6170 | 45783 | 8fbaa43d...a24a5dd | true | true |
| governance_surface_map.txt | fffe | 129070 | 3a6aa5fb...c1572c | 506c | 68658 | 612dc1c5...fc3c637 | true | true |
| human_gate_impl_map.txt | fffe | 4086 | 9f2fb8bc...72f4f5d | 6372 | 2042 | 8a4b393d...f7dfcd | true | true |
| mcp_tool_surface_map.txt | fffe | 122998 | e97493f5...99ff78c | 506c | 66860 | 198932ea...b7909f | true | true |
| persistence_surface_map.txt | fffe | 269776 | b9eb0d35...81a1c2 | 4573 | 136944 | 7ef793a1...c3d85ea | true | true |
| python_import_surface_map.txt | fffe | 542660 | 17a9b512...5a6f4f | 4573 | 271389 | ff2e16e0...33bff4a | true | true |
| recent_change_surface_map.txt | fffe | 14002 | a0067ea7...cda228f | 3631 | 7000 | cb29d872...bc6efa9 | true | true |
| repo_file_inventory.txt | fffe | 856666 | adab9073...bbcd0e3 | 2e63 | 428332 | ec7048f5...46e346fa | true | true |
| runtime_api_surface_map.txt | fffe | 56276 | 4054a64b...a42c3 | 6164 | 28237 | 72cb226f...665d805c | true | true |
| runtime_main_entry_map.txt | fffe | 72468 | 1395145f...686f47 | 4573 | 36257 | e0d00594...326a7362 | true | true |

注: after_bom(hex) は再エンコード後ファイル先頭2バイト(本文の先頭文字)であり、
UTF-8 BOM(EF BB BF)ではない。全件で utf8_no_bom=true。content_preserved は
raw.decode('utf-16') == reencoded.decode('utf-8') の一致確認。

## Post-Remediation Verification (READ ONLY)

- mocka_check_utf8 を12件全てに適用: 全件 ok=true / has_bom=false / encoding=utf-8 /
  issues=[]。
- root 直下 UTF-16LE(BOM FF FE) 残存再測定: 3件(diff_full.txt / full_file_map.txt /
  untracked.txt = GL7 走査対象外・未変更)。GL7 指摘12件は0件残存。

## Non-Impact Confirmation

- 変更対象は上記12件(git 未追跡 MAP-LAB 生成物)のみ。
- GL7 設定変更なし / GL7 バイパスなし。
- F-A Event Write: Pending 維持(本工程で再開しない)。
- Decision Ledger / Decision Record / Canonical 化: 本証跡工程では未実施。
- Seal / commit / push: Human Gate 再確認後(本証跡工程では未実施)。

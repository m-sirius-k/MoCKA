# MoCKA Encoding Policy v1.01 (FINAL)
1. Canonical Encoding: すべてのテキスト資産は UTF-8 を唯一の正規形とする。
2. File-Type Rules: JSON/MD/PY等は UTF-8 (BOMなし)。CSVは保存時 UTF-8-SIG 固定。
3. Implementation Rule: 全read/write時に encoding 指定を必須とし、未指定を禁止する。
4. Validation: 文字化け断片（"","鬮","繝","縺"）検知時は直ちに HALT する。

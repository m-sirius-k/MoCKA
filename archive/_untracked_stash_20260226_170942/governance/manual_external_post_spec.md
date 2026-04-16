# manual_external_post_spec v1.0

## 前提
- working tree clean
- origin 固定
- WSL 環境

## 手順
1. calc_summary_hash.py 実行
2. sealing_commit 作成
3. anchor_record.json 更新
4. external_ref = sealing_commit
5. push

## 成功判定
- git rev-parse HEAD == anchor_record.json.sealing_commit
- calc_summary_hash 出力一致

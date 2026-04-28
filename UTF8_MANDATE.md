# MoCKA UTF-8 鉄の掟 (IRON MANDATE)
## 制定：2026-04-28
## 原則：MoCKAに関わる全ての処理はUTF-8のみ。例外なし。

## 【Python側の掟】
1. 全ファイルの先頭に `# -*- coding: utf-8 -*-` を必須とする
2. open()は必ず `encoding="utf-8"` または `encoding="utf-8-sig"` を指定する
3. CSVの書き込みは必ず `encoding="utf-8-sig"` を使う
4. HTTPレスポンスは必ず `ensure_ascii=False` でJSONを返す
5. subprocessは `encoding="utf-8"` を指定する

## 【PowerShell側の掟】
1. Invoke-WebRequestでJSON送信は禁止
2. 必ずHttpWebRequestでUTF-8バイト直接送信する
3. ファイル書き込みは必ず `[System.IO.File]::WriteAllText(..., [System.Text.Encoding]::UTF8)` を使う
4. Get-Contentは必ず `-Encoding UTF8` を指定する
5. スクリプト先頭に以下を必須とする：
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $OutputEncoding = [System.Text.Encoding]::UTF8

## 【Chrome拡張側の掟】
1. fetchのContentTypeは必ず `application/json; charset=utf-8` を指定する
2. JSON.stringify()の結果は必ずUTF-8として送信する

## 【違反検知】
- 起動時に `check_utf8_mandate.py` を実行し、違反ファイルを検出する
- 違反があれば起動を停止する（PHASE8_BLOCKと同等）

## 【インシデント記録】
- 2026-04-28：PowerShellのInvoke-WebRequestがShift-JISでJSON送信
  → 200件超のパターンデータが文字化けしてevents.csvに記録された
  → HttpWebRequest + UTF-8バイト直接送信で解決
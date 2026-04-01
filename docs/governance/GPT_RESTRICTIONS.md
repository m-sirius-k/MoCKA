# GPT作業禁止事項（自動生成）
生成日時：2026-04-01 13:14:59
ソース：docs/incidents/INC-*.md

---

## 常時禁止（全タスク共通）
- README.mdへの変更禁止（Claude専任）
- interface/router.py への変更禁止（Claude専任）
- tools/mocka_orchestra_v10.py への変更禁止
- app.py への変更禁止
- secrets/ 内ファイルの作成禁止
- git push --force 禁止
- mocka-seal の実行禁止（Claude専任）
- コアシステムファイルへの無断変更禁止

---

## インシデントから導出された禁止事項

### INC-20260401-001 より
：
憲章第2条制定
secrets/フォルダ運用開始
.gitignore完全版適用

---

## 適用ルール
1. 本ファイルは全GPT指示書の冒頭に必ず参照する
2. 新規インシデント発生時は自動更新される
3. 禁止事項への違反はINCIDENTとして記録される
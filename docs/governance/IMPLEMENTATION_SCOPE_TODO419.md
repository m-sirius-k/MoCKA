# TODO_419 実装スコープ確定書 v1.0

作成日: 2026-07-07
根拠: DC_20260707_006(Human Gate承認)
Phase: 実装Phase1(準備) — コード本体はまだ変更していない

---

## 変更対象ファイル

| ファイル | 種別 |
|---|---|
| `tools/mocka_orchestra_v10.py`(正本) | 部分修正(4行の1行置換 + 冒頭6行追加) |
| `tools/orchestra_context_bridge.py`(新規配置) | private版から無変更でコピー配置 |

## バックアップ

- `tools/mocka_orchestra_v10.py.bak_20260707_TODO419`(実装前スナップショット、10268bytes)を作成済み

---

## 変更対象関数(1行のみの置換)

各関数内の`.fill(PROMPT)`を`.fill(ENRICHED_PROMPT)`に置換する。それ以外(セレクター探索・待機処理・フォールバック・エラーハンドリング)は一切変更しない。

| 関数 | 変更前 | 変更後 |
|---|---|---|
| `run_chatgpt(context)` | `await chatgpt_box.fill(PROMPT)` | `await chatgpt_box.fill(ENRICHED_PROMPT)` |
| `run_perplexity(context)` | `await box.fill(PROMPT)` | `await box.fill(ENRICHED_PROMPT)` |
| `run_gemini(context)` | `await box.fill(PROMPT)` | `await box.fill(ENRICHED_PROMPT)` |
| `run_copilot(context)` | `await box.fill(PROMPT)` | `await box.fill(ENRICHED_PROMPT)` |

## 新規追加関数/コード(ファイル冒頭、`PROMPT`定義の直後に挿入)

```python
# TODO_419: Orchestra Context Bridge統合(DC_20260707_006承認)
_NO_CONTEXT = "--no-context" in sys.argv
try:
    from orchestra_context_bridge import inject_context as _inject_context
    ENRICHED_PROMPT = PROMPT if _NO_CONTEXT else _inject_context(PROMPT)
except ImportError:
    ENRICHED_PROMPT = PROMPT
```

## import追加

標準ライブラリの新規importは不要。`orchestra_context_bridge`は既存の`try/except ImportError`ガード内でローカルimportするのみ(トップレベルimport文は追加しない)。

## Bridge配置

`PlanningCaliber/workshop/Orchestra_Project/orchestra/orchestra_context_bridge.py`(private版)の内容を無変更で`tools/orchestra_context_bridge.py`(正本リポ側)へコピー配置する。

---

## 変更しない箇所(承認範囲外・不可侵)

- `load_chat_urls()` / `save_chat_url()` / `clean()` / `wait_for_completion()` / `get_or_resume_page()`
- `run_chatgpt` / `run_perplexity` / `run_gemini` / `run_copilot`内の、セレクター探索ロジック・複数セレクターフォールバック・タイムアウト処理・入力欄が見つからない場合のスキップ処理
- `main()`のCDP接続処理・Claude統合(claude_page)処理・タスク並列実行(`asyncio.gather`)・統合プロンプト組み立て部分
- `MODE`の分岐ロジック全般

---

## 承認事項の解釈確認(Phase2着手前に確認をお願いします)

DC_20260707_006の禁止事項リストには`run_chatgpt()` `run_copilot()` `run_gemini()` `run_perplexity()`が列挙されています。これを「関数に一切触れない」という意味に取ると、`.fill(PROMPT)`→`.fill(ENRICHED_PROMPT)`の置換自体が不可能になり、TODO_419の目的(Context Injection)自体が実施できなくなります。

したがって本書では、この禁止事項を「各関数内のPlaywright制御・セレクター取得・待機処理を変更しない」という意味と解釈し、`.fill()`の引数変数名のみの1行置換は許可される変更(承認事項1-a「ENRICHED_PROMPTへの置換」)に含まれるものとして扱います。

この解釈に相違なければPhase2(コード実装)へ進みます。

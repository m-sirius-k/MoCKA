# くろこへの指示書 — WPメニュー構築 + Orchestra LP投稿
作成日: 2026-06-03

---

## STEP 1（TODO_220）: メニュー構造作成

### 前提確認
固定ページが以下のスラッグで作成済みであること（未作成なら先に作成）：
- `mocka-about`
- `vasai`、`vasai/use-cases`、`vasai/docs`
- `mini-mocka`、`mini-mocka/orchestra`、`mini-mocka/relay`、`mini-mocka/phi-os`、`mini-mocka/memory`
- `research`
- `verification`

### 作業手順
```
管理画面 → 外観 → メニュー → 新規メニュー作成
メニュー名: メインメニュー
```

以下の階層構造でメニューを組む：

```
Home                  → 固定ページ「Sirius Lab」（トップページ）
MoCKA                 → 固定ページ「MoCKA」（/mocka-about）
vasAI                 → 固定ページ「vasAI」（/vasai）
mini MoCKA            → 固定ページ「mini MoCKA」（/mini-mocka）
  ├ Orchestra         → 固定ページ「Orchestra」（/mini-mocka/orchestra）
  ├ Relay             → 固定ページ「Relay」（/mini-mocka/relay）
  ├ PHI-OS            → 固定ページ「PHI-OS」（/mini-mocka/phi-os）
  └ Memory            → 固定ページ「Memory」（/mini-mocka/memory）
Research              → 固定ページ「Research」（/research）
Verification          → 固定ページ「Verification」（/verification）
```

### 完了条件
- メニューの位置:「プライマリメニュー」または「ヘッダーメニュー」にチェック済み
- 「メニューを保存」を押して保存完了
- ブラウザで `https://mocka.nsjp.org/` を開き、ヘッダーメニューが表示されることを確認

---

## STEP 2（TODO_221）: Orchestra LP 投稿

### 対象ページ
```
固定ページ「Orchestra」
URL: https://mocka.nsjp.org/mini-mocka/orchestra
親ページ: mini MoCKA
```

### 作業手順

1. `管理画面 → 固定ページ → 一覧 → 「Orchestra」を編集`
2. エディタを **「クラシックエディタ」** または **「カスタムHTML ブロック」** に切り替える
3. 添付の `orchestra_lp_content.html` の内容を**全文貼り付け**
4. ページ属性:
   - 親ページ: `mini MoCKA`
   - テンプレート: フルワイド（テーマによる・あれば選択）
5. 「公開」または「更新」を押す

### 確認
- `https://mocka.nsjp.org/mini-mocka/orchestra` にアクセスしてLPが表示されること
- 「Pro プランで始める」「One プランで始める」ボタンのリンクがStripeに飛ぶこと

---

## 注意事項
- HTMLにはStripeのPayment Link URLが2箇所含まれています（`href="..."` 部分）
- URLはきむら博士が確認済みのものが差し込まれています
- スラッグは変更しないこと（`orchestra` 固定）

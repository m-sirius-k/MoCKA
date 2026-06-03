# NTP Phase 1 完了レポート

作成日: 2026-06-03  
バージョン: 1.0

---

## 完了した成果物

### src/ui/index.html
- FP向け保険比較UIをブラウザで直接開ける単一HTMLファイルとして実装
- 被保険者属性・健康状態・希望保障の入力フォーム
- APIモード / ローカルモードの自動切替（APIサーバー未起動時はブラウザ内簡易エンジンで動作）
- スコアランキング表示・理由・警告のカード型結果表示

### src/planner/engine.py
- `ClientProfile` データクラスで被保険者属性を定義
- スコアリングアルゴリズム: 保障ニーズ合致度(40pt) + 家族構成(20pt) + 予算適合(20pt) + 特約(15pt) - 待機ペナルティ
- `load_products()` でdata/insurers/sample_master.jsonを読込
- `search_plans()` / `format_results()` でPhase2 APIと共用可能なインターフェース

### data/insurers/sample_master.json
- 4社6商品のサンプルデータ（定期・終身・医療・がん・就業不能・年金）
- Phase3でスクレイパーが上書きする形式と互換

### config/insurers.json
- 明治安田・日本生命・住友生命・第一生命の4社設定

---

## くろこへの次回作業指示

### Phase 2: FastAPI APIサーバー実装 ← **完了済み (2026-06-03)**

以下のファイルが作成済みです:

```
src/api/
├── main.py              ← FastAPIアプリ本体（CORS設定済み）
├── routers/
│   ├── plans.py         ← POST /api/plans/search
│   └── insurers.py      ← GET /api/insurers, GET /api/insurers/{id}
└── models/
    └── schemas.py       ← Pydanticスキーマ定義
```

起動方法: `start_api.bat` をダブルクリック  
API仕様確認: http://localhost:8400/docs

### Phase 3: スクレイパー実装（未着手）

`src/scraper/` ディレクトリを作成し、各保険会社サイトから商品データを取得するスクレイパーを実装する。

- `config/insurers.json` の `products_url` を各社の商品一覧ページに設定
- Playwright または requests+BeautifulSoup でスクレイピング
- 取得結果を `data/insurers/{insurer_id}.json` に保存
- `data/insurers/sample_master.json` と同一スキーマで出力

### Phase 4: Excel入力対応（未着手）

openpyxl を使って顧客データのExcel一括インポート機能を実装する。

### Phase 5: PDF出力（未着手）

比較結果をPDF帳票として出力する機能を実装する（reportlab または weasyprint）。

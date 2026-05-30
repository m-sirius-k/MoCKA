# vasAI API仕様書

Base URL: `http://localhost:6000`

## ヘルス

| Method | Path | 説明 |
|---|---|---|
| GET | `/health` | 基本ヘルスチェック |
| GET | `/status` | movement + shadow + ステージ件数 |

## イベント

| Method | Path | 説明 |
|---|---|---|
| POST | `/events` | イベント記録 |
| GET | `/events/<id>` | イベント取得 |
| GET | `/events?limit=50&type=INCIDENT` | イベント検索 |

### POST /events body
```json
{
  "who": "Claude",
  "what": "CHANGE_DONE",
  "where": "system/component",
  "why": "変更理由",
  "how": "SDK",
  "content": {},
  "caliber_id": "medical_v1",
  "stage": "RECORD"
}
```

## 監査

| Method | Path | 説明 |
|---|---|---|
| GET | `/audit/verify` | チェーン検証 |
| POST | `/audit/seal` | 封印 |
| GET | `/audit/report` | 監査レポート |

## Caliber

| Method | Path | 説明 |
|---|---|---|
| GET | `/calibers` | 登録caliber一覧 |
| POST | `/calibers/register` | caliber登録 |
| POST | `/calibers/<id>/process` | intranetデータ処理 |

## Governance

| Method | Path | 説明 |
|---|---|---|
| GET | `/governance/queue` | 承認待ちキュー |
| POST | `/governance/approve/<id>` | 承認 |
| POST | `/governance/reject/<id>` | 却下 |
| GET | `/governance/decisions` | 決定履歴 |

## Shadow

| Method | Path | 説明 |
|---|---|---|
| GET | `/shadow/status` | shadow状態 |
| POST | `/shadow/enter-degraded` | 縮退モード（テスト用）|
| POST | `/shadow/exit-degraded` | 復旧（テスト用）|

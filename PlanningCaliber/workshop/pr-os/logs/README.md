# Logs

公開・エラーログ保管フォルダ。

## 命名規則

| 種別 | 形式 | 例 |
|------|------|----|
| 公開ログ | `PUB_NNN_{adapter}_{date}.json` | `PUB_001_wp_20260606.json` |
| エラーログ | `ERR_{adapter}_{timestamp}.json` | `ERR_wp_20260606T1000.json` |

## 保持ポリシー

- 公開ログ: 無期限保持
- エラーログ: 90日

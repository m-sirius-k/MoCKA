# MoCKA docs 構造定義

## 公開層（Public）
docs/architecture/   # システム設計
docs/caliber/        # Caliber仕様・LEAP指標
docs/api/            # インターフェース仕様
docs/incidents/      # インシデント記録
docs/governance/     # 憲章・規約
docs/images/         # 画像リソース

## 非公開層（Private）
secrets/             # トークン・state・認証情報
data/                # events.csv（ローカルのみ）

## 境界ルール
- secrets/は.gitignoreで完全除外
- state.json系は全てsecrets/へ
- APIキーは環境変数のみ（ファイル禁止）

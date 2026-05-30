# vasAI

**AI Activity Recording & Governance Platform**

> AIが何をしたかを記録し、監査し、継承するための基盤

MoCKAの設計思想を企業向けに圧縮・軽量化した第二文明核。

## クイックスタート

```bash
# 依存関係インストール
pip install -r requirements.txt

# 起動
python api/app.py
# → http://localhost:6000/health

# またはバッチファイルで起動（Windows）
vasAI-START.bat
```

## 3行でSDKを使う

```python
from sdk.vasai import VasAIClient

client = VasAIClient(endpoint="http://localhost:6000", caliber_id="medical_v1")
event_id = client.record(who="Claude", what="CHANGE_DONE", content={"summary": "done"})
report = client.audit.verify()
print(report.chain_valid)  # True
```

## アーキテクチャ

- **2心臓**: MoCKAMovement（8ステージ）+ ShadowMovement（縮退75%保証）
- **append-only**: SQLite + SHA-256ハッシュチェーン
- **HMAC監査連鎖**: 改ざん検知
- **caliber**: 企業ごとのアダプター（医療・金融サンプル付き）

## テスト

```bash
pytest tests/ -v
```

## ドキュメント

- [アーキテクチャ](docs/ARCHITECTURE.md)
- [Caliber作成ガイド](docs/CALIBER_GUIDE.md)
- [API仕様書](docs/API_SPEC.md)

---

「記録なき作業は存在しない」「知識循環は止まらない」

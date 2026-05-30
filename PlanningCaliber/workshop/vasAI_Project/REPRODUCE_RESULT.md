# vasAI L4.9 Proof of Reproducibility — 再現結果

**生成日時**: 2026-05-30T23:53:48.838045+00:00
**総合判定**: VERIFIED
**結果**: 18/18 PASS
**再現ハッシュ**: sha256:3d25d97708a5f5888c66a6103b4213c54127ec28ce3bdfd9833a55fc9aec3c37

## 実行環境

| 項目 | 値 |
|------|-----|
| OS | Windows |
| OS Version | 10.0.26200 |
| Python | 3.13.13 |
| SQLite | 3.50.4 |
| Hostname | mam |

## シナリオ結果

| ID | シナリオ | 結果 | 時間(s) |
|----|---------|------|---------|
| S-01 | 基本記録・監査 | PASS | 0.4 |
| S-02 | shadow縮退・回復 | PASS | 0.32 |
| S-03 | 3業種caliber | PASS | 0.36 |
| S-04 | Human Gate | PASS | 0.34 |
| S-00 | なぜvasAIが必要か | PASS | 0.38 |
| S-05 | 負荷3段階 | PASS | 96.77 |
| S-06 | Hostile Environment | PASS | 0.13 |
| S-07 | 30日連続運用 | PASS | 6.07 |
| S-08 | マルチ部門運用 | PASS | 0.2 |
| S-09 | AI再現性 | PASS | 0.19 |
| S-10 | 監査官試験 | PASS | 0.2 |
| S-11 | 障害注入強化 | PASS | 1.37 |
| S-12 | 経営価値 | PASS | 0.36 |
| S-13 | Evidence Ledger | PASS | 0.51 |
| S-14 | PHI Layer + MoCKA Bridge | PASS | 0.82 |
| S-15 | 180日組織運用 | PASS | 19.64 |
| S-16 | 故意破壊試験 | PASS | 1.91 |
| S-17 | 失敗DNA試験 | PASS | 1.05 |

## 判定

**VERIFIED**: 18/18 シナリオが成功

## 再現ハッシュ（SHA-256）

```
sha256:3d25d97708a5f5888c66a6103b4213c54127ec28ce3bdfd9833a55fc9aec3c37
```

> このハッシュは全シナリオの合否結果から生成されます。
> 同じ環境・同じコードで実行した場合、同じハッシュが生成されます。
"""
L5 Hash二層分離パッチ
reproduce_mocka.py の generate_report() を修正する

適用:
  python patch_l5_hash.py
"""
import os, sys, re, hashlib, socket
from pathlib import Path

BASE_DIR = Path(__file__).parent
TARGET   = BASE_DIR / "reproduce_mocka.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} が見つかりません")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ── 旧Hash生成ブロックを特定して置換 ──────────────────────────────────────────
OLD = '''\
    hash_input = json.dumps({
        "product": "MoCKA",
        "date": datetime.now().isoformat(),
        "passed": passed, "failed": failed, "skipped": skipped,
        "results": [{"id": r["id"], "status": r["status"]} for r in results],
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    # vasAI教訓: CRLF正規化
    sha256 = hashlib.sha256(hash_input.replace(b\'\\r\\n\', b\'\\n\')).hexdigest()'''

NEW = '''\
    # ── Reproduction Hash（環境非依存・固定） ────────────────────────────────
    # L5設計: datetime を除外し結果内容のみでHash生成
    # 同じコード・同じ結果 → 常に同じHash（クロス環境一致の証拠）
    SUITE_VERSION = "mocka-reproduce-v1.0"
    repro_input = json.dumps({
        "product":            "MoCKA",
        "test_suite_version": SUITE_VERSION,
        "pass_count":         passed,
        "fail_count":         failed,
        "skip_count":         skipped,
        "critical_flags":     {"fail_zero": failed == 0, "skip_zero": skipped == 0},
        "test_results":       [{"id": r["id"], "status": r["status"]} for r in results],
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha256 = hashlib.sha256(repro_input.replace(b\'\\r\\n\', b\'\\n\')).hexdigest()

    # ── Audit Hash（実行ごとに変化・実行証跡ID） ──────────────────────────────
    import socket as _sock
    try:
        _machine = _sock.gethostname()
    except Exception:
        _machine = "unknown"
    audit_input = json.dumps({
        "reproduction_hash": sha256,
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "machine":           _machine,
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    audit_hash = hashlib.sha256(audit_input.replace(b\'\\r\\n\', b\'\\n\')).hexdigest()'''

if OLD not in src:
    print("ERROR: 置換対象が見つかりません（既にパッチ適用済み？）")
    print("  → reproduce_mocka.py のhash_input部分を手動確認してください")
    sys.exit(1)

src = src.replace(OLD, NEW)

# ── 表示部分: Reproduction Hash + Audit Hash を両方表示 ──────────────────────
OLD_DISPLAY = '''\
    print(f"\\n  Reproduction Hash: sha256:{sha256[:16]}...")'''

NEW_DISPLAY = '''\
    print(f"\\n  Reproduction Hash: sha256:{sha256[:16]}...  ← 環境非依存・固定")
    print(f"  Audit Hash:        sha256:{audit_hash[:16]}...  ← 実行証跡ID（毎回変化）")'''

if OLD_DISPLAY in src:
    src = src.replace(OLD_DISPLAY, NEW_DISPLAY)

# ── Markdownレポートにもaudit_hashを追記 ──────────────────────────────────────
OLD_MD_HASH = '''\
## Reproduction Hash

```
sha256:{sha256}
```'''

NEW_MD_HASH = '''\
## Reproduction Hash（環境非依存・固定）

```
sha256:{sha256}
```

## Audit Hash（実行証跡ID）

```
sha256:{audit_hash}
```

> Reproduction Hashは環境・実行時刻に関わらず同一の結果なら常に一致します。
> Audit Hashは実行ごとに変化し、いつ・どこで実行したかの証跡になります。'''

if OLD_MD_HASH in src:
    src = src.replace(OLD_MD_HASH, NEW_MD_HASH)

# ── generate_report()の返り値にaudit_hashを追加 ───────────────────────────────
OLD_RETURN = "    return sha256, l3, l4"
NEW_RETURN = "    return sha256, audit_hash, l3, l4"
if OLD_RETURN in src:
    src = src.replace(OLD_RETURN, NEW_RETURN)

# ── main()の返り値受け取りも修正 ─────────────────────────────────────────────
OLD_MAIN_CALL = "    sha256, l3, l4 = generate_report(duration)"
NEW_MAIN_CALL = "    sha256, audit_hash, l3, l4 = generate_report(duration)"
if OLD_MAIN_CALL in src:
    src = src.replace(OLD_MAIN_CALL, NEW_MAIN_CALL)

# ── 書き込み ──────────────────────────────────────────────────────────────────
TARGET.write_text(src, encoding="utf-8")
print(f"✅ パッチ適用完了: {TARGET}")
print(f"   Reproduction Hash: 環境非依存（datetime除外）")
print(f"   Audit Hash:        実行証跡ID（毎回変化）")
print(f"\n次のステップ:")
print(f"  docker compose -f docker-compose.reproduce.l5.yml build --no-cache")
print(f"  docker compose -f docker-compose.reproduce.l5.yml run --rm reproduce-mocka-l5")

from pathlib import Path

path = Path(r'C:\Users\sirok\MoCKA\app.py')
txt = path.read_text(encoding='utf-8')

old = "        except Exception as _e:\n            pass\n        # ===== matcher_v3 終了 ====="
new = "        except Exception as _e:\n            import traceback\n            print('[MOCKA matcher_v3 ERROR]', traceback.format_exc())\n        # ===== matcher_v3 終了 ====="

if old in txt:
    txt = txt.replace(old, new)
    path.write_text(txt, encoding='utf-8')
    print("パッチ適用完了")
else:
    print("対象文字列が見つかりません")

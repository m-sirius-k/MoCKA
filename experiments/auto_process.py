import requests, time, os, json
from datetime import datetime

APP_URL = "http://localhost:5000"
PILS_DIR = r"C:\Users\sirok\MoCKA\data\storage\outbox\PILS"

print("")
print("=" * 55)
print("  MoCKA 自動連続処理 v2 - 全件処理まで継続")
print("  Ctrl+C で停止")
print("=" * 55)

processed = 0
errors = 0

while True:
    try:
        now = datetime.now().strftime("%H:%M:%S")

        # PILSフォルダを直接確認
        files = [f for f in os.listdir(PILS_DIR) if f.endswith(".json")]

        if not files:
            print("[{}] キューが空。30秒後に再確認...".format(now))
            time.sleep(30)
            continue

        print("[{}] キュー残: {}件 → 処理開始: {}".format(now, len(files), files[0][:40]))

        # PROCESS NOW
        r = requests.post(
            APP_URL + "/caliber/process",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=1800
        )

        now2 = datetime.now().strftime("%H:%M:%S")
        if r.status_code == 200:
            result = r.json()
            rate = result.get("restore_rate", "?")
            processed += 1
            print("[{}] 完了 #{} restore_rate={}".format(now2, processed, rate))
        else:
            errors += 1
            msg = r.text[:100] if r.text else "no response"
            print("[{}] エラー({}): {}".format(now2, r.status_code, msg))

        time.sleep(5)

    except KeyboardInterrupt:
        print("\n停止。処理済み: {}件 エラー: {}件".format(processed, errors))
        break
    except Exception as e:
        errors += 1
        print("[{}] 例外: {}".format(datetime.now().strftime("%H:%M:%S"), str(e)[:80]))
        time.sleep(30)

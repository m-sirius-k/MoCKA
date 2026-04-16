import json
import sys
from pathlib import Path

# router.pyをインポート
sys.path.insert(0, str(Path("C:/Users/sirok/MoCKA/interface")))
from router import MoCKARouter

PING_PATH = Path("C:/Users/sirok/MoCKA/data/storage/infield/PACKET/ping_latest.json")

def essence_to_share():
    # ping_latest.jsonを読む
    if not PING_PATH.exists():
        print("[ERROR] ping_latest.json が存在しません")
        return

    ping = json.loads(PING_PATH.read_text(encoding="utf-8"))
    es = ping.get("ESSENCE_SUMMARY", {})

    # 送信テキスト構築（最小限）
    text = (
        f'[MOCKA]{{"H":"{ping["H"]}","G":{ping["G"]},"C":"{ping["C"]}","P":"{ping["P"]}"}}\n'
        f'[ESSENCE]\n'
        f'INCIDENT:{es.get("INCIDENT","none")}\n'
        f'PHILOSOPHY:{es.get("PHILOSOPHY","none")}\n'
        f'OPERATION:{es.get("OPERATION","none")}'
    )

    print("[SHARE] 送信内容:")
    print(text)
    print("[SHARE] router.share()起動...")

    router = MoCKARouter()
    router.share(text)
    print("[SHARE] Playwright経由でclaude.aiに送信完了")

if __name__ == "__main__":
    essence_to_share()

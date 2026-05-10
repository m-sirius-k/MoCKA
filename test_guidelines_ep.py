import sys
sys.path.insert(0, r'C:\Users\sirok\MoCKA')

# app.pyのguidelines_status関数を単体実行してエラーを特定
from pathlib import Path
import json

ROOT_DIR = r'C:\Users\sirok\MoCKA'

try:
    gpath = Path(ROOT_DIR) / "data" / "guidelines.json"
    print("1. gpath exists:", gpath.exists())
    
    data = json.loads(gpath.read_text(encoding="utf-8"))
    print("2. data loaded, guidelines count:", len(data["guidelines"]))
    
    top5 = sorted(data["guidelines"], key=lambda g: g.get("score", 0), reverse=True)[:5]
    print("3. top5 count:", len(top5))
    
    result = {
        "total": data["summary"]["total"],
        "by_category": data["summary"]["by_category"],
        "last_updated": data["summary"].get("last_updated", ""),
        "top5": [{
            "category": g["category"],
            "score": g["score"],
            "directive": g["action_directive"],
        } for g in top5]
    }
    print("4. result keys:", list(result.keys()))
    print("5. top5[0]:", result["top5"][0] if result["top5"] else "empty")
    print("\nOK: エンドポイントは正常に動作するはず")

except Exception as e:
    import traceback
    print("ERROR:", e)
    traceback.print_exc()

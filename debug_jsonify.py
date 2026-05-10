import sys, json
sys.path.insert(0, r'C:\Users\sirok\MoCKA')

from pathlib import Path
from flask import Flask
app = Flask(__name__)

gpath = Path(r'C:\Users\sirok\MoCKA\data\guidelines.json')
data = json.loads(gpath.read_text(encoding='utf-8'))
top5 = sorted(data["guidelines"], key=lambda g: g.get("score", 0), reverse=True)[:5]

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

# jsonifyをシミュレート
with app.app_context():
    try:
        from flask import jsonify
        resp = jsonify(result)
        print("OK: jsonify成功")
        print("response data:", resp.get_data(as_text=True)[:200])
    except Exception as e:
        import traceback
        print("ERROR in jsonify:", e)
        traceback.print_exc()
        
        # どのフィールドが問題か特定
        for g in top5:
            try:
                json.dumps(g)
            except Exception as e2:
                print(f"問題のguideline: {g['category']} - {e2}")
                for k,v in g.items():
                    try:
                        json.dumps(v)
                    except Exception as e3:
                        print(f"  問題フィールド: {k} = {repr(v)[:100]}")

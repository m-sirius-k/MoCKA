import urllib.request, json

data = json.dumps({
    "text": "なぜPowerShellで書くのですか",
    "url": "https://claude.ai/test",
    "timestamp": "2026-05-11T12:00:00Z"
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:5000/user_voice',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req) as res:
        print("レスポンス:", res.read().decode('utf-8'))
except Exception as e:
    print("エラー:", e)

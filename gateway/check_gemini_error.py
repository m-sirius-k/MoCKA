import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_dispatcher import dispatch_multi_request

response = dispatch_multi_request(
    request_text='Test decision context binding',
    providers=['gemini'],
    models={'gemini': 'gemini-2.0-flash'},
    title='Check Gemini Error Detail',
    decision_id='JARVIS_OBS_20260923031206'
)

print("=" * 70)
print("GEMINI ERROR DETAIL")
print("=" * 70)

for result in response.get('results', []):
    if result.get('provider') == 'gemini':
        print(f"\nStatus: {result.get('status')}")
        print(f"Error: {result.get('error')}")
        print(f"Model: {result.get('model')}")

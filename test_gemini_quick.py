#!/usr/bin/env python
import sys
sys.path.insert(0, 'gateway')

from adapter_gemini import call_api as gemini_call

question = 'C-001とC-002について、過去の判断を踏まえて説明してください。'
result = gemini_call(question, model='gemini-2.0-flash')

print('GEMINI TEST RESULT:')
print(f'Status: {result.get("status")}')
if result.get('status') == 'ok':
    print(f'Response length: {len(result.get("response", ""))} chars')
    print(f'Response preview: {result.get("response", "")[:200]}...')
    print('Result: CONNECTED SUCCESS')
else:
    print(f'Error: {result.get("error")}')
    print('Result: BLOCKED')

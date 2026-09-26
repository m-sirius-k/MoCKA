#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-AI Provider Connection Test
Test all 4 providers for HAB/JARVIS integration
"""

import sys
sys.path.insert(0, 'gateway')

test_question = 'C-001とC-002について、過去の判断を踏まえて説明してください。'

results = {}

# GPT Test
print('\n' + '='*80)
print('GPT PROVIDER TEST')
print('='*80)
try:
    from adapter_gpt import call_api as gpt_call
    result = gpt_call(test_question, model='gpt-4')
    results['GPT'] = result
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'ok':
        print(f"Response preview: {result.get('response', '')[:150]}...")
        print("Result: CONNECTED")
    else:
        print(f"Error: {result.get('error')}")
        print("Result: BLOCKED")
except Exception as e:
    print(f"Import/execution error: {e}")
    print("Result: BLOCKED")

# Claude Test
print('\n' + '='*80)
print('CLAUDE PROVIDER TEST')
print('='*80)
try:
    from adapter_claude import call_api as claude_call
    result = claude_call(test_question, model='claude-opus-5')
    results['Claude'] = result
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'ok':
        print(f"Response preview: {result.get('response', '')[:150]}...")
        print("Result: CONNECTED")
    else:
        print(f"Error: {result.get('error')}")
        print("Result: CONFIGURED / NOT CONNECTED (API Key Missing)")
except Exception as e:
    print(f"Import/execution error: {e}")
    print("Result: BLOCKED")

# Gemini Test
print('\n' + '='*80)
print('GEMINI PROVIDER TEST')
print('='*80)
try:
    from adapter_gemini import call_api as gemini_call
    result = gemini_call(test_question, model='gemini-2.0-flash')
    results['Gemini'] = result
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'ok':
        print(f"Response preview: {result.get('response', '')[:150]}...")
        print("Result: CONNECTED")
    else:
        print(f"Error: {result.get('error')}")
        if 'google.generativeai' in str(result.get('error')) or 'No module' in str(result.get('error')):
            print("Result: NOT CONFIGURED (SDK Missing)")
        else:
            print("Result: CONFIGURED / NOT CONNECTED")
except Exception as e:
    print(f"Import/execution error: {e}")
    print("Result: NOT CONFIGURED (SDK Missing)")

# Perplexity Test
print('\n' + '='*80)
print('PERPLEXITY PROVIDER TEST')
print('='*80)
try:
    from adapter_perplexity import call_api as pplx_call
    result = pplx_call(test_question, model='sonar-pro')
    results['Perplexity'] = result
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'ok':
        print(f"Response preview: {result.get('response', '')[:150]}...")
        print("Result: CONNECTED")
    else:
        print(f"Error: {result.get('error')}")
        print("Result: CONFIGURED / NOT CONNECTED (API Key Missing)")
except Exception as e:
    print(f"Import/execution error: {e}")
    print("Result: BLOCKED")

# Summary
print('\n' + '='*80)
print('SUMMARY')
print('='*80)
for provider, result in results.items():
    status = result.get('status', 'unknown')
    print(f"{provider}: {status}")

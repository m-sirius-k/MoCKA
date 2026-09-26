#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

print('\nCREDENTIAL STATUS CHECK (2026-09-23)')
print('='*80)

credentials = {
    'GPT': {
        'env_var': 'OPENAI_API_KEY',
        'has_value': bool(os.environ.get('OPENAI_API_KEY')),
        'value_start': (os.environ.get('OPENAI_API_KEY') or '')[:20]
    },
    'Claude': {
        'env_var': 'ANTHROPIC_API_KEY',
        'has_value': bool(os.environ.get('ANTHROPIC_API_KEY')),
        'value_start': (os.environ.get('ANTHROPIC_API_KEY') or '')[:20]
    },
    'Gemini': {
        'env_var': 'GEMINI_API_KEY',
        'has_value': bool(os.environ.get('GEMINI_API_KEY')),
        'value_start': (os.environ.get('GEMINI_API_KEY') or '')[:20],
        'note': 'placeholder/invalid'
    },
    'Perplexity': {
        'env_var': 'PERPLEXITY_API_KEY',
        'has_value': bool(os.environ.get('PERPLEXITY_API_KEY')),
        'value_start': (os.environ.get('PERPLEXITY_API_KEY') or '')[:20]
    }
}

for provider, info in credentials.items():
    status = 'FOUND' if info['has_value'] else 'NOT FOUND'
    print(f'\n{provider}:')
    print(f'  Variable: {info["env_var"]}')
    print(f'  Status: {status}')
    if info['has_value']:
        print(f'  Value (first 20 chars): {info["value_start"]}')
        if 'note' in info:
            print(f'  Note: {info["note"]}')

print('\n' + '='*80)
print('CONNECTIVITY ASSESSMENT:')
print('='*80)

connected_count = 0
for provider, info in credentials.items():
    if not info['has_value']:
        print(f'{provider}: NOT CONNECTED (credential not set)')
    elif 'note' in info and 'invalid' in info['note']:
        print(f'{provider}: NOT CONNECTED (credential is placeholder)')
    else:
        print(f'{provider}: READY FOR TEST (credential present)')
        connected_count += 1

print('\n' + '='*80)
print(f'TOTAL PROVIDERS READY: {connected_count}/4')
if connected_count >= 2:
    print('STATUS: Multi-AI dispatch possible')
elif connected_count == 1:
    print('STATUS: Single provider test only')
else:
    print('STATUS: No valid credentials available')
print('='*80 + '\n')

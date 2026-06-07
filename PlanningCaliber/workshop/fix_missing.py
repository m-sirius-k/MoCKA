import re
content = open('orchestra_lp_v4_base.html', encoding='utf-8').read()

patches = [
    ('<div class="ab">論理的に整理すると', '<div class="ab" id="t-ab-claude">論理的に整理すると'),
    ('<div class="ab">業界別データでは口コミROIが3.2倍', '<div class="ab" id="t-ab-chatgpt">業界別データでは口コミROIが3.2倍'),
    ('<div class="ab">Google調査ではSNS', '<div class="ab" id="t-ab-gemini">Google調査ではSNS'),
    ('<div class="ab">Microsoft Ads の', '<div class="ab" id="t-ab-copilot">Microsoft Ads の'),
    ('<div class="ab">最新リサーチ', '<div class="ab" id="t-ab-perplexity">最新リサーチ'),
    ('<div class="sec-label">FAQ</div>', '<div class="sec-label" id="t-lbl-faq">FAQ</div>'),
    ('<div class="sec-label">Get started</div>', '<div class="sec-label" id="t-lbl-cta">Get started</div>'),
    ('<div class="sec-label">Pricing</div>', '<div class="sec-label" id="t-lbl-price">Pricing</div>'),
    ('<div class="sec-label">対応 AI ラインナップ</div>', '<div class="sec-label" id="t-lbl-ai">対応 AI ラインナップ</div>'),
    ('<div class="sec-label">📁 自動保存', '<div class="sec-label" id="t-lbl-save">📁 自動保存'),
    ('<div class="sec-label">🎼 Orchestra 最大の革新', '<div class="sec-label" id="t-lbl-rclick">🎼 Orchestra 最大の革新'),
    ('<div class="sec-label">📍 保存した会話', '<div class="sec-label" id="t-lbl-jump">📍 保存した会話'),
    ('<div class="sec-label lt">⚡', '<div class="sec-label lt" id="t-lbl-parallel">⚡'),
    ('<div class="sec-label lt">How it works</div>', '<div class="sec-label lt" id="t-lbl-how">How it works</div>'),
]

applied = 0
for old, new in patches:
    if old in content:
        content = content.replace(old, new, 1)
        applied += 1
    else:
        print('SKIP:', old[:60])

open('orchestra_lp_v4_base.html', 'w', encoding='utf-8').write(content)
print('applied:', applied)

ids = re.findall(r'id="t-([^"]+)"', content)
print('total t- IDs:', len(ids))
for k in ['ab-claude','lbl-faq','lbl-save','lbl-rclick','lbl-parallel','lbl-how','lbl-price','lbl-ai','lbl-cta']:
    print('OK' if k in ids else 'MISSING', 't-' + k)

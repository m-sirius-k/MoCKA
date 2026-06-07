import re

content = open('orchestra_lp_v4_base.html', encoding='utf-8').read()

patches = [
    # rclick-text内の固定テキスト（日本語のみ → 多言語化）
    (
        '          Claude.ai でいつも通り会話中...<br><br>\n          「次のマーケティング戦略として、\n          <span class="sel-text" id="t-sel-text">SNS広告よりも口コミ施策を優先すべきか？</span>\n          について各AIの意見を聞きたい」',
        '          <span id="t-rclick-pre">Claude.ai でいつも通り会話中...<br><br>「次のマーケティング戦略として、</span>\n          <span class="sel-text" id="t-sel-text">SNS広告よりも口コミ施策を優先すべきか？</span>\n          <span id="t-rclick-post">について各AIの意見を聞きたい」</span>'
    ),
    # sec-p lt (parallel section) — IDなし
    (
        '<p class="sec-p lt">あなたが選んだ AI 全員が、それぞれの視点で自動回答。あなたは待つだけでいい。</p>',
        '<p class="sec-p lt" id="t-p-parallel">あなたが選んだ AI 全員が、それぞれの視点で自動回答。あなたは待つだけでいい。</p>'
    ),
    # pd-q-box
    (
        '<div class="pd-q-box">「SNS広告より口コミ施策を優先すべきか？」</div>',
        '<div class="pd-q-box" id="t-kwq">「SNS広告より口コミ施策を優先すべきか？」</div>'
    ),
    # send-label
    (
        '<div class="send-label">↓ 全 AI に同時送信</div>',
        '<div class="send-label" id="t-kw-lbl-send">↓ 全 AI に同時送信</div>'
    ),
    # merge-arrow
    (
        '<div class="merge-arrow">↓ 全員の回答を比較・統合</div>',
        '<div class="merge-arrow" id="t-kw-lbl-merge">↓ 全員の回答を比較・統合</div>'
    ),
    # rb-label
    (
        '<div class="rb-label">✦ あなたが得られるもの</div>',
        '<div class="rb-label" id="t-kw-result-lbl">✦ あなたが得られるもの</div>'
    ),
    # rb-txt
    (
        '<div class="rb-txt">5つの異なる視点・データ・根拠が一度に揃う。<br>一人の AI では気づけなかった答えが見えてくる。</div>',
        '<div class="rb-txt" id="t-kw-result-txt">5つの異なる視点・データ・根拠が一度に揃う。<br>一人の AI では気づけなかった答えが見えてくる。</div>'
    ),
]

applied = 0
for old, new in patches:
    if old in content:
        content = content.replace(old, new, 1)
        applied += 1
    else:
        print('SKIP:', old[:80])

open('orchestra_lp_v4_base.html', 'w', encoding='utf-8').write(content)
print('applied:', applied)

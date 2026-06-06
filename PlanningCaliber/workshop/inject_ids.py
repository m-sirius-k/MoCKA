# inject_ids.py
# orchestra_lp_v3.html の全テキスト要素に t- IDを付与する
# 出力: orchestra_lp_v4_base.html

from pathlib import Path

src = Path("orchestra_lp_v3.html").read_text(encoding="utf-8")

# (検索文字列, 置換後文字列) のペア
# 注意: replaceは1回だけ (count=1)
patches = [
    # タイトル
    ('<title>Orchestra', '<title id="doc-title">Orchestra'),
    # eyebrow
    ('"o-eyebrow">mini MoCKA', '"o-eyebrow" id="t-eyebrow">mini MoCKA'),
    # h1
    ('<h1>すべての', '<h1 id="t-h1">すべての'),
    # hero-sub
    ('"o-hero-sub">Orchestraは', '"o-hero-sub" id="t-hero-sub">Orchestraは'),
    # CTA buttons hero
    ('href="https://chromewebstore.google.com/detail/aollpclhdmcaocbahnakiacfhafamllo" target="_blank" rel="noopener">\n      <i class="ti ti-brand-chrome"',
     'href="https://chromewebstore.google.com/detail/aollpclhdmcaocbahnakiacfhafamllo" target="_blank" rel="noopener" id="t-btn-free">\n      <i class="ti ti-brand-chrome"'),
    ('href="#pricing">料金プランを見る', 'href="#pricing" id="t-btn-plan">料金プランを見る'),
    # badges
    ('<span class="o-badge">Chrome Web Store 公式掲載</span>', '<span class="o-badge" id="t-badge1">Chrome Web Store 公式掲載</span>'),
    ('<span class="o-badge">Claude / ChatGPT / Gemini 対応</span>', '<span class="o-badge" id="t-badge2">Claude / ChatGPT / Gemini 対応</span>'),
    ('<span class="o-badge">ライセンス即時自動配信</span>', '<span class="o-badge" id="t-badge3">ライセンス即時自動配信</span>'),
    # 自動保存セクション
    ('<div class="sec-lbl">📁 自動保存', '<div class="sec-lbl" id="t-lbl-save">📁 自動保存'),
    ('<h2 class="sec-h">すべての会話が、ここに残る。</h2>', '<h2 class="sec-h" id="t-h-save">すべての会話が、ここに残る。</h2>'),
    ('<p class="sec-p">拡張アイコンをクリックするだけ。今日', '<p class="sec-p" id="t-p-save">拡張アイコンをクリックするだけ。今日'),
    ('<div class="l">保存済み</div>', '<div class="l" id="t-saved">保存済み</div>'),
    ('<div class="l">今月</div>', '<div class="l" id="t-thismonth">今月</div>'),
    ('🔍 キーワード検索...', '🔍 <span id="t-search-ph">キーワード検索...</span>'),
    ('<div class="pi-d">今日 10:32</div>', '<div class="pi-d" id="t-today">今日 10:32</div>'),
    ('<div class="pi-d">昨日 14:18</div>', '<div class="pi-d" id="t-yesterday">昨日 14:18</div>'),
    ('<div class="pi-d">3日前 09:45</div>', '<div class="pi-d" id="t-3days">3日前 09:45</div>'),
    # popup flylinks (3つ)
    ('<div class="pi-link">↗ このページへ飛ぶ</div>\n            </div>\n            <div class="pm-item">\n              <div class="pi-t">Orchestra LP',
     '<div class="pi-link" id="t-flylink">↗ このページへ飛ぶ</div>\n            </div>\n            <div class="pm-item">\n              <div class="pi-t">Orchestra LP'),
    ('<div class="pi-link">↗ このページへ飛ぶ</div>\n            </div>\n            <div class="pm-item">\n              <div class="pi-t">Stripe',
     '<div class="pi-link" id="t-flylink2">↗ このページへ飛ぶ</div>\n            </div>\n            <div class="pm-item">\n              <div class="pi-t">Stripe'),
    ('<div class="pi-link">↗ このページへ飛ぶ</div>\n          </div>\n        </div>\n      </div>',
     '<div class="pi-link" id="t-flylink3">↗ このページへ飛ぶ</div>\n          </div>\n        </div>\n      </div>'),
    # popup feats
    ('<strong>「先週やったよな？」', '<strong id="t-pf1h">「先週やったよな？」'),
    ('<span>すべての会話が日時つきで自動記録', '<span id="t-pf1p">すべての会話が日時つきで自動記録'),
    ('<strong>「このページへ飛ぶ」', '<strong id="t-pf2h">「このページへ飛ぶ」'),
    ('<span>保存した会話をタップするだけで', '<span id="t-pf2p">保存した会話をタップするだけで'),
    ('<strong>会話の「中身」まで全文検索</strong>', '<strong id="t-pf3h">会話の「中身」まで全文検索</strong>'),
    ('<span>タイトルだけでなく', '<span id="t-pf3p">タイトルだけでなく'),
    # 右クリックセクション
    ('<div class="sec-lbl">🎼 Orchestra 最大の革新', '<div class="sec-lbl" id="t-lbl-rclick">🎼 Orchestra 最大の革新'),
    ('<h2 class="sec-h">選んで、右クリック。それだけ。</h2>', '<h2 class="sec-h" id="t-h-rclick">選んで、右クリック。それだけ。</h2>'),
    ('<p class="sec-p">気になるテキストを反転させて', '<p class="sec-p" id="t-p-rclick">気になるテキストを反転させて'),
    ('<span class="step-pin sp1">① テキストを選択</span>', '<span class="step-pin sp1" id="t-step1pin">① テキストを選択</span>'),
    ('<span class="step-pin sp2">② 右クリック</span>', '<span class="step-pin sp2" id="t-step2pin">② 右クリック</span>'),
    ('<span class="sel-text">SNS広告よりも', '<span class="sel-text" id="t-sel-text">SNS広告よりも'),
    ('<span class="cmi">🎼</span>\n              Orchestra で協議する', '<span class="cmi">🎼</span>\n              <span id="t-ctx-feat">Orchestra で協議する</span>'),
    ('<span class="cmi">📋</span>コピー', '<span class="cmi">📋</span><span id="t-ctx-copy">コピー</span>'),
    ('<span class="cmi">🔍</span>Google で検索', '<span class="cmi">🔍</span><span id="t-ctx-search">Google で検索</span>'),
    ('<span class="cmi">🔗</span>リンクをコピー', '<span class="cmi">🔗</span><span id="t-ctx-link">リンクをコピー</span>'),
    # 並列セクション
    ('<div class="sec-lbl lt">⚡ 実際の動作', '<div class="sec-lbl lt" id="t-lbl-parallel">⚡ 実際の動作'),
    ('<h2 class="sec-h lt">5人の専門家に、同時に相談できる。</h2>', '<h2 class="sec-h lt" id="t-h-parallel">5人の専門家に、同時に相談できる。</h2>'),
    ('<p class="sec-p lt">誰に送るかを自分で設定', '<p class="sec-p lt" id="t-p-parallel">誰に送るかを自分で設定'),
    # kw-tabs
    ('"kw-tab active" onclick="kwTab(\'send\',this)">', '"kw-tab active" onclick="kwTab(\'send\',this)" id="t-kwtab1">'),
    ('"kw-tab" onclick="kwTab(\'setting\',this)">', '"kw-tab" onclick="kwTab(\'setting\',this)" id="t-kwtab2">'),
    # kw-qbox
    ('<div class="kw-qbox">「SNS広告', '<div class="kw-qbox" id="t-kwq">「SNS広告'),
    # kw-lbl x2
    ('<div class="kw-lbl">↓ チェックした', '<div class="kw-lbl" id="t-kw-lbl-send">↓ チェックした'),
    ('<div class="kw-lbl">↓ 全員の回答を', '<div class="kw-lbl" id="t-kw-lbl-merge">↓ 全員の回答を'),
    # kw-result
    ('<div class="rl">✦ あなたが得られるもの</div>', '<div class="rl" id="t-kw-result-lbl">✦ あなたが得られるもの</div>'),
    ('<div class="rt">5つの異なる', '<div class="rt" id="t-kw-result-txt">5つの異なる'),
    # inno-banner
    ('<div class="inno-tag">Orchestra が革新的な理由</div>', '<div class="inno-tag" id="t-inno-tag">Orchestra が革新的な理由</div>'),
    ('<div class="inno-h">AI から', '<div class="inno-h" id="t-inno-h">AI から'),
    ('<div class="inno-p">これまでの', '<div class="inno-p" id="t-inno-p">これまでの'),
    # AI cards
    ('<div class="ab">論理的には口コミのLTV', '<div class="ab" id="t-ab-claude">論理的には口コミのLTV'),
    ('<div class="ab">業界別データでは', '<div class="ab" id="t-ab-chatgpt">業界別データでは'),
    ('<div class="ab">2025年Google調査', '<div class="ab" id="t-ab-gemini">2025年Google調査'),
    ('<div class="ab">Microsoft Ads：', '<div class="ab" id="t-ab-copilot">Microsoft Ads：'),
    ('<div class="ab">HBR最新論文', '<div class="ab" id="t-ab-perplexity">HBR最新論文'),
    # 設定パネル
    ('<div class="em-t2">ライブラリ</div>', '<div class="em-t2" id="t-em-lib">ライブラリ</div>'),
    ('<div class="em-t2 active">⚙ 設定</div>', '<div class="em-t2 active" id="t-em-set">⚙ 設定</div>'),
    ('<p>右クリック操作の前に', '<p id="t-em-notice">右クリック操作の前に'),
    ('<div class="em-stitle">◆ 送信先', '<div class="em-stitle" id="t-em-dest-title">◆ 送信先'),
    ('<p class="em-hint">チェックしたAIが', '<p class="em-hint" id="t-em-hint">チェックしたAIが'),
    ('<div class="em-stitle">◎ 応答待機時間</div>', '<div class="em-stitle" id="t-em-speed-title">◎ 応答待機時間</div>'),
    ('<span class="slider-lbl">送信後、AIの読み込みを', '<span class="slider-lbl" id="t-em-speed-lbl">送信後、AIの読み込みを'),
    ('<span class="slider-tk">遅い 5.0s</span>', '<span class="slider-tk" id="t-sk-slow">遅い 5.0s</span>'),
    ('<span class="slider-tk">0.8s 早い</span>', '<span class="slider-tk" id="t-sk-fast">0.8s 早い</span>'),
    ('<p>エラーが多い', '<p id="t-em-warn">エラーが多い'),
    # sf-cards
    ('<span>送信先AIを自由に選ぶ</span>', '<span id="t-sf1h">送信先AIを自由に選ぶ</span>'),
    ('<p>使いたいAIだけにチェック。3つに', '<p id="t-sf1p">使いたいAIだけにチェック。3つに'),
    ('<span>回線速度に合わせて調整</span>', '<span id="t-sf2h">回線速度に合わせて調整</span>'),
    ('<p>回線が速い環境なら', '<p id="t-sf2p">回線が速い環境なら'),
    ('<span>Share モードで一時的に絞り込み</span>', '<span id="t-sf3h">Share モードで一時的に絞り込み</span>'),
    ('<p>右クリック時に Share モードを', '<p id="t-sf3p">右クリック時に Share モードを'),
    ('<span>事前ログインが必要</span>', '<span id="t-sf4h">事前ログインが必要</span>'),
    ('<p>Orchestraは各AIのブラウザ画面', '<p id="t-sf4p">Orchestraは各AIのブラウザ画面'),
    # チャットジャンプ
    ('<div class="sec-lbl">📍 保存した会話', '<div class="sec-lbl" id="t-lbl-jump">📍 保存した会話'),
    ('<h2 class="sec-h">選んだ瞬間、その会話のその場所へ。</h2>', '<h2 class="sec-h" id="t-h-jump">選んだ瞬間、その会話のその場所へ。</h2>'),
    ('<p class="sec-p">「ページへ」を押すと', '<p class="sec-p" id="t-p-jump">「ページへ」を押すと'),
    ('<div class="sv-t">マーケティング戦略', '<div class="sv-t" id="t-sv1t">マーケティング戦略'),
    ('<div class="sv-m">先週木曜', '<div class="sv-m" id="t-sv1m">先週木曜'),
    ('<div class="sv-t">Stripe Webhook', '<div class="sv-t" id="t-sv2t">Stripe Webhook'),
    ('<div class="sv-m">3日前 · 32分', '<div class="sv-m" id="t-sv2m">3日前 · 32分'),
    # goto-btn (最初の2つ)
    ('<a class="goto-btn" href="#">↗ ページへ</a>\n      </div>\n      <div class="sv-item">',
     '<a class="goto-btn" href="#" id="t-goto-btn">↗ ページへ</a>\n      </div>\n      <div class="sv-item">'),
    ('<a class="goto-btn" href="#">↗ ページへ</a>\n    </div>',
     '<a class="goto-btn" href="#" id="t-goto-btn2">↗ ページへ</a>\n    </div>'),
    # jump-banner
    ('<div class="jb-badge">↓ claude.ai が開き', '<div class="jb-badge" id="t-jump-banner">↓ claude.ai が開き'),
    ('<span class="b-ext">Orchestra で保存済み</span>', '<span class="b-ext" id="t-b-ext">Orchestra で保存済み</span>'),
    ('<div class="scroll-note">📍 保存した位置まで', '<div class="scroll-note" id="t-scroll-note">📍 保存した位置まで'),
    ('<div class="cs-new">＋ 新しいチャット</div>', '<div class="cs-new" id="t-new-chat">＋ 新しいチャット</div>'),
    ('<div class="cs-item active">SNS', '<div class="cs-item active" id="t-cs1">SNS'),
    ('<div class="cs-item">Stripe実装メモ</div>', '<div class="cs-item" id="t-cs2">Stripe実装メモ</div>'),
    ('<div class="cs-item">AIES論文推敲</div>', '<div class="cs-item" id="t-cs3">AIES論文推敲</div>'),
    ('<div class="cs-item">vasAI設計</div>', '<div class="cs-item" id="t-cs4">vasAI設計</div>'),
    # chat messages
    ('<div class="bbl u faded">SNSと口コミ', '<div class="bbl u faded" id="t-chat1">SNSと口コミ'),
    ('<div class="bbl ai faded">マーケティング予算', '<div class="bbl ai faded" id="t-chat2">マーケティング予算'),
    ('<div class="bbl u faded">具体的なROIの比較は？</div>', '<div class="bbl u faded" id="t-chat3">具体的なROIの比較は？</div>'),
    ('<div class="hl-pin">📍 Orchestra が保存した会話</div>', '<div class="hl-pin" id="t-hl-pin">📍 Orchestra が保存した会話</div>'),
    ('<div class="bbl ai hl">口コミ施策', '<div class="bbl ai hl" id="t-chat4">口コミ施策'),
    ('<div class="bbl u">なるほど、具体的な施策を3つ挙げて</div>', '<div class="bbl u" id="t-chat5">なるほど、具体的な施策を3つ挙げて</div>'),
    ('<div class="bbl ai">① 紹介プログラムの設計', '<div class="bbl ai" id="t-chat6">① 紹介プログラムの設計'),
    # AI ラインナップ
    ('<div class="sec-lbl">対応 AI ラインナップ</div>', '<div class="sec-lbl" id="t-lbl-ai">対応 AI ラインナップ</div>'),
    ('<h2 class="sec-h">5つの AI を、一つの拡張で動かす。</h2>', '<h2 class="sec-h" id="t-h-ai">5つの AI を、一つの拡張で動かす。</h2>'),
    ('<p style="margin-top:20px;font-size:13px;color:var(--muted);">各 AI の', '<p style="margin-top:20px;font-size:13px;color:var(--muted);" id="t-p-ai">各 AI の'),
    # HOW
    ('<div class="sec-lbl lt">How it works</div>', '<div class="sec-lbl lt" id="t-lbl-how">How it works</div>'),
    ('<h2 class="sec-h lt">AIとの対話を「資産」に変える', '<h2 class="sec-h lt" id="t-h-how">AIとの対話を「資産」に変える'),
    ('<p class="sec-p lt">セットアップは数分', '<p class="sec-p lt" id="t-p-how">セットアップは数分'),
    ('<h3>Chrome に追加</h3>', '<h3 id="t-step1h">Chrome に追加</h3>'),
    ('<p>Chrome Web Store から', '<p id="t-step1p">Chrome Web Store から'),
    ('<h3>Claude で会話開始</h3>', '<h3 id="t-step2h">Claude で会話開始</h3>'),
    ('<p>いつも通り Claude.ai を開いて', '<p id="t-step2p">いつも通り Claude.ai を開いて'),
    ('<h3>右クリック → 協議</h3>', '<h3 id="t-step3h">右クリック → 協議</h3>'),
    ('<p>気になるテキストを選択して右クリック。', '<p id="t-step3p">気になるテキストを選択して右クリック。'),
    ('<h3>CSV / JSON で持ち出し</h3>', '<h3 id="t-step4h">CSV / JSON で持ち出し</h3>'),
    ('<p>蓄積した履歴は', '<p id="t-step4p">蓄積した履歴は'),
    # PRICING
    ('<div class="sec-lbl">Pricing</div>', '<div class="sec-lbl" id="t-lbl-price">Pricing</div>'),
    ('<h2 class="sec-h">シンプルな 3 プラン。</h2>', '<h2 class="sec-h" id="t-h-price">シンプルな 3 プラン。</h2>'),
    ('<p class="sec-p">まず無料で試して', '<p class="sec-p" id="t-p-price">まず無料で試して'),
    # plan names / prices
    ('<div class="plan-name">Free</div>\n        <div class="plan-price">', '<div class="plan-name" id="t-name-free">Free</div>\n        <div class="plan-price" id="t-price-free">'),
    ('¥0</div>\n        <div class="plan-period">永久無料', '¥0</div>\n        <div class="plan-regular"> </div>\n        <div class="plan-period" id="t-period-free">永久無料'),
    # free plan features
    ('<li><span class="chk">✓</span>会話の自動保存（無制限）</li>', '<li><span class="chk">✓</span><span id="t-pf1">会話の自動保存（無制限）</span></li>'),
    ('<li><span class="chk">✓</span>全文検索・フィルター</li>', '<li><span class="chk">✓</span><span id="t-pf2">全文検索・フィルター</span></li>'),
    ('<li><span class="chk">✓</span>CSV / JSON エクスポート</li>', '<li><span class="chk">✓</span><span id="t-pf3">CSV / JSON エクスポート</span></li>'),
    ('<li><span class="chk dim">—</span><span class="dim">多AI 並列協議</span></li>', '<li><span class="chk dim">—</span><span class="dim" id="t-pf4">多AI 並列協議</span></li>'),
    ('<li><span class="chk dim">—</span><span class="dim">AI 別タイマー表示</span></li>', '<li><span class="chk dim">—</span><span class="dim" id="t-pf5">AI 別タイマー表示</span></li>'),
    ('<a class="plan-btn" href="https://chromewebstore.google.com/detail/aollpclhdmcaocbahnakiacfhafamllo" target="_blank" rel="noopener">今すぐ無料で追加</a>',
     '<a class="plan-btn" href="https://chromewebstore.google.com/detail/aollpclhdmcaocbahnakiacfhafamllo" target="_blank" rel="noopener" id="t-btn-free2">今すぐ無料で追加</a>'),
    # Pro plan
    ('<div class="plan-name">Pro</div>', '<div class="plan-name" id="t-name-pro">Pro</div>'),
    ('<div class="plan-period">/ 月（税別）</div>', '<div class="plan-regular"> </div>\n        <div class="plan-period" id="t-period-pro">/ 月（税別）</div>'),
    ('<li><span class="chk">✓</span>Free のすべての機能</li>', '<li><span class="chk">✓</span><span id="t-pp1">Free のすべての機能</span></li>'),
    ('<li><span class="chk">✓</span>多AI 並列協議（5 AI 同時）</li>', '<li><span class="chk">✓</span><span id="t-pp2">多AI 並列協議（5 AI 同時）</span></li>'),
    ('<li><span class="chk">✓</span>AI 別カウントダウンタイマー</li>', '<li><span class="chk">✓</span><span id="t-pp3">AI 別カウントダウンタイマー</span></li>'),
    ('<li><span class="chk">✓</span>協議プロンプトカスタマイズ</li>', '<li><span class="chk">✓</span><span id="t-pp4">協議プロンプトカスタマイズ</span></li>'),
    ('<li><span class="chk">✓</span>メールサポート</li>', '<li><span class="chk">✓</span><span id="t-pp5">メールサポート</span></li>'),
    ('<a class="plan-btn" href="#cta">Pro にアップグレード</a>', '<a class="plan-btn" href="#cta" id="t-btn-pro">Pro にアップグレード</a>'),
    # One plan
    ('<div class="plan-ribbon">LAUNCH EDITION</div>', '<div class="plan-ribbon" id="t-ribbon">LAUNCH EDITION</div>'),
    ('<div class="plan-name">One</div>', '<div class="plan-name" id="t-name-one">One</div>'),
    ('<li><span class="chk">✓</span>Pro のすべての機能</li>', '<li><span class="chk">✓</span><span id="t-po1">Pro のすべての機能</span></li>'),
    ('<li><span class="chk">✓</span>mini MoCKA 全製品アクセス</li>', '<li><span class="chk">✓</span><span id="t-po2">mini MoCKA 全製品アクセス</span></li>'),
    ('<li><span class="chk">✓</span>Relay（会話自動引き継ぎ）</li>', '<li><span class="chk">✓</span><span id="t-po3">Relay（会話自動引き継ぎ）</span></li>'),
    ('<li><span class="chk">✓</span>PHI-OS（セッション記憶復元）</li>', '<li><span class="chk">✓</span><span id="t-po4">PHI-OS（セッション記憶復元）</span></li>'),
    ('<li><span class="chk">✓</span>優先サポート</li>', '<li><span class="chk">✓</span><span id="t-po5">優先サポート</span></li>'),
    ('<a class="plan-btn" href="#cta">One にアップグレード</a>', '<a class="plan-btn" href="#cta" id="t-btn-one">One にアップグレード</a>'),
    # FAQ
    ('<div class="sec-lbl">FAQ</div>', '<div class="sec-lbl" id="t-lbl-faq">FAQ</div>'),
    ('<h2 class="sec-h">よくある質問。</h2>', '<h2 class="sec-h" id="t-h-faq">よくある質問。</h2>'),
    ('<p class="sec-p">導入前によくいただく', '<p class="sec-p" id="t-p-faq">導入前によくいただく'),
    ('<div class="faq-q">無料プランと Pro の違いは何ですか？</div>', '<div class="faq-q" id="t-fq1">無料プランと Pro の違いは何ですか？</div>'),
    ('<div class="faq-a">無料プランでは会話の保存', '<div class="faq-a" id="t-fa1">無料プランでは会話の保存'),
    ('<div class="faq-q">ライセンスキーはいつ届きますか？</div>', '<div class="faq-q" id="t-fq2">ライセンスキーはいつ届きますか？</div>'),
    ('<div class="faq-a">Stripe での購入完了後', '<div class="faq-a" id="t-fa2">Stripe での購入完了後'),
    ('<div class="faq-q">会話データはどこに保存されますか？</div>', '<div class="faq-q" id="t-fq3">会話データはどこに保存されますか？</div>'),
    ('<div class="faq-a">すべてのデータはお使いの Chrome', '<div class="faq-a" id="t-fa3">すべてのデータはお使いの Chrome'),
    ('<div class="faq-q">One プランの「$8」はいつまでですか？</div>', '<div class="faq-q" id="t-fq4">One プランの「$8」はいつまでですか？</div>'),
    ('<div class="faq-a">先着 500 名限定の特別価格', '<div class="faq-a" id="t-fa4">先着 500 名限定の特別価格'),
    ('<div class="faq-q">チーム利用や複数ライセンスは可能ですか？</div>', '<div class="faq-q" id="t-fq5">チーム利用や複数ライセンスは可能ですか？</div>'),
    ('<div class="faq-a">現時点では 1 ライセンス', '<div class="faq-a" id="t-fa5">現時点では 1 ライセンス'),
    # CTA
    ('<div class="sec-lbl">Get started</div>', '<div class="sec-lbl" id="t-lbl-cta">Get started</div>'),
    ('<h2 class="sec-h">AIとの対話を、今日から「資産」に。</h2>', '<h2 class="sec-h" id="t-h-cta">AIとの対話を、今日から「資産」に。</h2>'),
    ('<p class="sec-p" style="margin:0 auto 28px;">保存する', '<p class="sec-p" style="margin:0 auto 28px;" id="t-p-cta">保存する'),
    ('<i class="ti ti-brand-chrome" aria-hidden="true"></i> 無料で始める</a>\n      <a class="btn-s" href="#pricing">プランを比較する</a>',
     '<i class="ti ti-brand-chrome" aria-hidden="true"></i> <span id="t-cta-free">無料で始める</span></a>\n      <a class="btn-s" href="#pricing" id="t-cta-plan">プランを比較する</a>'),
]

result = src
applied = 0
skipped = []
for old, new in patches:
    if old in result:
        result = result.replace(old, new, 1)
        applied += 1
    else:
        skipped.append(old[:60])

# One planの価格行を処理（v3の実際の構造に合わせて）
one_patterns = [
    ('$8</div>\n        <div class="plan-period">/ 月（通常 $10）</div>',
     '$8</div>\n        <div class="plan-regular" id="t-regular-one">通常 $10 / 月</div>\n        <div class="plan-period" id="t-period-one">/ 月（先着500名限定価格）</div>'),
]
for old, new in one_patterns:
    if old in result:
        result = result.replace(old, new, 1)
        applied += 1
    else:
        skipped.append(old[:60])

# plan-note
plan_note_old = '<p class="plan-note">One の $8 は'
plan_note_new = '<p class="plan-note" id="t-plan-note">One の $8 は先着 500 名限定のローンチ価格です。枠が埋まり次第、通常価格の <strong>$10 / 月</strong> に移行します。価格変更後も、既存ユーザーには変更前の価格が継続適用されます。</p>'
if plan_note_old in result:
    # 既存のplan-noteを終わりまで置換
    import re
    result = re.sub(r'<p class="plan-note">One の \$8 は.*?</p>', plan_note_new, result, flags=re.DOTALL)
    applied += 1

# lang-bar を <body> 直後に追加
lang_bar_html = '''
<!-- 言語バー -->
<div id="lang-bar" style="position:fixed;top:14px;right:18px;z-index:9999;display:flex;gap:5px;background:rgba(10,10,20,.85);backdrop-filter:blur(10px);padding:5px 8px;border-radius:100px;border:1px solid rgba(201,168,76,.35);">
  <button class="lb active" onclick="setLang('ja')" style="font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:4px 10px;border-radius:100px;border:none;cursor:pointer;background:#c9a84c;color:#1a1a1a;">日</button>
  <button class="lb" onclick="setLang('en')" style="font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:4px 10px;border-radius:100px;border:none;cursor:pointer;background:transparent;color:rgba(255,255,255,.5);">EN</button>
  <button class="lb" onclick="setLang('zh')" style="font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:4px 10px;border-radius:100px;border:none;cursor:pointer;background:transparent;color:rgba(255,255,255,.5);">中</button>
  <button class="lb" onclick="setLang('ko')" style="font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:4px 10px;border-radius:100px;border:none;cursor:pointer;background:transparent;color:rgba(255,255,255,.5);">한</button>
  <button class="lb" onclick="setLang('es')" style="font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:4px 10px;border-radius:100px;border:none;cursor:pointer;background:transparent;color:rgba(255,255,255,.5);">ES</button>
</div>
'''

if 'id="lang-bar"' not in result:
    result = result.replace('<body>', '<body>' + lang_bar_html)

Path("orchestra_lp_v4_base.html").write_text(result, encoding="utf-8")
print(f"orchestra_lp_v4_base.html 生成完了: {len(result):,} chars")
print(f"パッチ適用: {applied} 件")
if skipped:
    print(f"スキップ（見つからなかった）: {len(skipped)} 件")
    for s in skipped[:10]:
        print(f"  - {s}")

# ID確認
import re
ids = re.findall(r'id="t-([^"]+)"', result)
print(f"\nt- ID数: {len(ids)}")
check_keys = ["h1", "hero-sub", "btn-free", "badge1", "h-save", "ab-claude", "ribbon", "plan-note", "h-cta", "lbl-faq"]
for k in check_keys:
    status = "✓" if k in ids else "✗ MISSING"
    print(f"  {status}: t-{k}")

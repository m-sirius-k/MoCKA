(function() {
    if (window.MOCKA_INITIALIZED) return;
    window.MOCKA_INITIALIZED = true;
    console.log("[MOCKA] 自律監視プロトコル v16.1 起動 (user_voice ON / matcher_result注入 ON)");

    let lastUrl = window.location.href;
    let dnaSentInThisSession = false;
    let essenceSentInThisSession = false;

    // ===== USER VOICE: 送信フック =====
    function isClaudeInputEditor(el) {
        if (!el) return false;
        if (el.getAttribute('data-placeholder')) return true;
        if (el.closest('form')) return true;
        const parent = el.closest('footer, [class*="composer"], [class*="chat-input"], [class*="ProseMirror"]');
        if (parent) return true;
        return false;
    }

    function hookSendButton() {
        const btn = getSendButton();
        if (!btn || btn._mockaHooked) return;
        btn._mockaHooked = true;
        btn.addEventListener('click', function() {
            const editor = getEditor();
            if (!editor || !isClaudeInputEditor(editor)) return;
            const text = getEditorText(editor).trim();
            if (!text || text.startsWith('[MOCKA]{')) return;
            saveUserVoice(text);
        }, true);
        console.log("[MOCKA] 送信ボタンにuser_voiceフック完了");
    }

    function hookEditorEnter() {
        const editor = getEditor();
        if (!editor || editor._mockaVoiceHooked) return;
        if (!isClaudeInputEditor(editor)) return;
        editor._mockaVoiceHooked = true;
        editor.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                const text = getEditorText(editor).trim();
                if (!text || text.startsWith('[MOCKA]{')) return;
                saveUserVoice(text);
            }
        }, true);
        console.log("[MOCKA] Enterキーにuser_voiceフック完了");
    }

    async function saveUserVoice(text) {
        const url = window.location.href;
        if (!url.includes('claude.ai')) return;

        // ===== フィルター: 不純物除去 =====
        const t = text.trim();

        // 短すぎる（3文字以下）はスキップ
        if (t.length < 3) return;

        // システムログ・エラーログパターンを除外
        const noisePatterns = [
            /^\[PING/,
            /^\[MOCKA/,
            /^\[UTF-8/,
            /^Traceback/,
            /^File "[^"]+", line \d+/,
            /^SyntaxError:/,
            /^TypeError:/,
            /^ValueError:/,
            /^AttributeError:/,
            /^ImportError:/,
            /^OperationalError:/,
            /^PS /,
            /^>>> /,
            /^Enumerating objects:/,
            /^Counting objects:/,
            /^Writing objects:/,
            /^remote:/,
            /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/,  // タイムスタンプ行
        ];
        for (const pat of noisePatterns) {
            if (pat.test(t)) return;
        }

        // きむら博士の発言シグナル（これがあれば優先保存）
        const kimuraSignals = [
            /なぜ/, /どうして/, /いやいや/, /そこで/, /ヒント/, /グレート/,
            /またか/, /クレーム/, /やろう/, /して/, /ください/, /確認/,
            /おはよ/, /よろしく/, /ありがとう/, /わかった/, /OK/, /ｙ$/,
        ];
        const hasSignal = kimuraSignals.some(p => p.test(t));

        // シグナルなし かつ 英数字記号のみ（コード行）はスキップ
        if (!hasSignal && /^[-]+$/.test(t) && t.length < 30) return;

        const ts = new Date().toISOString();
        try {
            await fetch('http://127.0.0.1:5000/user_voice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text: t, url: url, timestamp: ts })
            });
            console.log("[MOCKA] user_voice保存:", t.slice(0, 40) + (t.length > 40 ? '...' : ''));
        } catch(e) {
            console.warn("[MOCKA] user_voice保存失敗:", e.message);
        }
    }

    const hookLoop = setInterval(() => {
        hookSendButton();
        hookEditorEnter();
    }, 1500);

    // ===== 既存コード =====

    const urlWatcher = setInterval(() => {
        const currentUrl = window.location.href;
        if (currentUrl !== lastUrl) {
            console.log("[MOCKA] URL変化検知:", currentUrl);
            lastUrl = currentUrl;
            dnaSentInThisSession = false;
            essenceSentInThisSession = false;
        }
    }, 500);

    const mainLoop = setInterval(() => {
        const url = window.location.href;
        const editor = getEditor();
        if (!editor) return;

        if ((url.includes('/new') || url === 'https://claude.ai/') && !dnaSentInThisSession) {
            if (getEditorText(editor).trim() === "") {
                injectDNA(editor);
            }
        } else if (url.includes('/chat/') && !url.includes('/new') && !essenceSentInThisSession) {
            if (getEditorText(editor).trim() === "") {
                shootEssence(editor);
            }
        }
    }, 1000);

    function getEditor() {
        return document.querySelector('div[contenteditable="true"][data-placeholder]')
            || document.querySelector('div[contenteditable="true"]');
    }

    function getEditorText(el) {
        return el.innerText || el.textContent || "";
    }

    function getSendButton() {
        const byLabel = document.querySelector('button[aria-label="メッセージを送信"]')
            || document.querySelector('button[aria-label="Send message"]')
            || document.querySelector('button[aria-label*="送信"]')
            || document.querySelector('button[aria-label*="Send"]');
        if (byLabel) return byLabel;

        const byTestId = document.querySelector('button[data-testid="send-button"]')
            || document.querySelector('button[data-testid*="send"]');
        if (byTestId) return byTestId;

        const allButtons = Array.from(document.querySelectorAll('button'));
        const bySvg = allButtons.find(btn =>
            btn.querySelector('svg') &&
            (btn.type === 'submit' || btn.closest('form'))
        );
        if (bySvg) return bySvg;

        const form = document.querySelector('form');
        if (form) {
            const formBtns = Array.from(form.querySelectorAll('button'));
            if (formBtns.length > 0) return formBtns[formBtns.length - 1];
        }

        return null;
    }

    // ===== Layer 3: matcher_result読み込み =====
    async function fetchMatcherResult() {
        try {
            const res = await fetch('http://127.0.0.1:5000/get_latest_dna');
            const data = await res.json();
            const mr = data.ping && data.ping.matcher_result;
            if (!mr) return null;
            // SAFE以外のみ注入（SAFEはノイズになるので省く）
            if (mr.verdict === 'SAFE') return null;
            return mr;
        } catch(e) {
            return null;
        }
    }

    function buildMatcherPrefix(mr) {
        const emoji = mr.verdict === 'CRITICAL' ? '🚨' :
                      mr.verdict === 'DANGER'   ? '⚠️' :
                      mr.verdict === 'WARNING'  ? '🟡' : '';
        const lines = [
            `[MOCKA_ALERT] ${emoji} verdict=${mr.verdict} score=${mr.score}`,
        ];
        if (mr.matched_patterns && mr.matched_patterns.length > 0) {
            lines.push(`matched: ${mr.matched_patterns.slice(0, 3).join(' / ')}`);
        }
        return lines.join('\n') + '\n';
    }

    async function injectDNA(el) {
        dnaSentInThisSession = true;
        try {
            console.log("[MOCKA] DNA取得中...");
            const res = await fetch('http://127.0.0.1:5000/get_latest_dna');
            const data = await res.json();
            const p = data.ping;

            // Layer 3: matcher_result があれば先頭に付加
            let prefix = '';
            const mr = p.matcher_result;
            if (mr && mr.verdict && mr.verdict !== 'SAFE') {
                prefix = buildMatcherPrefix(mr);
                console.log("[MOCKA] matcher_result注入:", mr.verdict, mr.score);
            }


            // TODO_134: PENDING承認待ちALERT注入
            if (p && p.alert_pending && p.alert_pending.count > 0) {
                const _n   = p.alert_pending.count;
                const _top = p.alert_pending.top || '';
                const pendingLine = '[MOCKA_ALERT]  verdict=PENDING score=' + _n + '\n'
                    + (_top ? '承認待ち ' + _n + '件 — 最優先: ' + _top + '\n' : '');
                prefix = pendingLine + (prefix || '');
            }
            const dnaText = `[MOCKA]{"H":"${p.H}","G":${p.G},"C":"${p.C}","P":"${p.P}"}`;
            const text = prefix ? prefix + dnaText : dnaText;

            await writeAndSend(el, text);
            console.log("[MOCKA] DNA注入完了 (v16.0)");

            const hookIndicator = document.createElement('div');
            hookIndicator.textContent = mr && mr.verdict !== 'SAFE'
                ? `⚡MOCKA HOOKED [${mr.verdict}]`
                : '⚡MOCKA HOOKED';
            hookIndicator.style.cssText = 'position:fixed;bottom:120px;right:20px;color:rgba(255,255,255,0.6);font-size:10px;z-index:99999;pointer-events:none;letter-spacing:1px;';
            document.body.appendChild(hookIndicator);

            if (p.essence_updated === true) {
                console.log("[MOCKA] essence_updated=true");
                essenceSentInThisSession = true;
            } else {
                console.log("[MOCKA] essence_updated=false skip");
            }
        } catch(e) {
            dnaSentInThisSession = false;
            console.error("[MOCKA] DNA取得失敗", e);
        }
    }

    async function shootEssence(el) {
        essenceSentInThisSession = true;
        try {
            const res = await fetch('http://127.0.0.1:5000/get_latest_dna');
            const data = await res.json();
            const p = data.ping;
            if (p.essence_updated === true) {
                console.log("[MOCKA] /chat/ essence_updated=true: MCPツールで取得済み");
            } else {
                console.log("[MOCKA] /chat/ essence_updated=false: skip");
            }
        } catch(e) {
            essenceSentInThisSession = false;
            console.error("[MOCKA] Essence確認失敗", e);
        }
    }

    async function writeAndSend(el, text) {
        el.focus();
        el.innerHTML = '';
        await new Promise(r => setTimeout(r, 100));

        document.execCommand('selectAll', false, null);
        document.execCommand('delete', false, null);
        document.execCommand('insertText', false, text);
        await new Promise(r => setTimeout(r, 150));

        if (getEditorText(el).trim() === '') {
            el.focus();
            el.innerText = text;
            ['input', 'change', 'keyup', 'keydown'].forEach(evtType => {
                el.dispatchEvent(new InputEvent(evtType, {
                    bubbles: true, cancelable: true,
                    inputType: 'insertText', data: text
                }));
            });
            await new Promise(r => setTimeout(r, 150));
        }

        if (getEditorText(el).trim() === '') {
            el.focus();
            await navigator.clipboard.writeText(text).catch(() => {});
            document.execCommand('paste');
            await new Promise(r => setTimeout(r, 200));
        }

        console.log("[MOCKA] 送信ボタン待機中...");
        for (let attempt = 0; attempt < 5; attempt++) {
            await waitForSendButton(2000);
            const testBtn = getSendButton();
            if (testBtn) break;
            await new Promise(r => setTimeout(r, 500));
        }

        const btn = getSendButton();
        if (btn) {
            btn.removeAttribute("disabled");
            btn.disabled = false;
            await new Promise(r => setTimeout(r, 100));
            btn.click();
            btn.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
            console.log("[MOCKA] 送信ボタンクリック成功");
        } else {
            console.warn("[MOCKA] 送信ボタン見つからず。手動送信してください。");
        }
    }

    function waitForSendButton(timeout) {
        return new Promise(resolve => {
            const start = Date.now();
            const check = setInterval(() => {
                const btn = getSendButton();
                const elapsed = Date.now() - start;
                if (btn || elapsed > timeout) {
                    clearInterval(check);
                    resolve();
                }
            }, 100);
        });
    }

})();


// ===== TURN COUNTER (TODO_138 + relay_mode) =====
// mocka_relay_mode=true の時はRelayに委譲してMoCKAカウンターを無効化
window.mocka_turn_count = window.mocka_turn_count || 0;
window.MOCKA_TURN_LIMIT = window.MOCKA_TURN_LIMIT || 20;

function mocka_count_turns() {
    if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.get('mocka_relay_mode', function(data) {
            if (data.mocka_relay_mode === true) return; // Relayに委譲
            _mocka_count_turns_inner();
        });
        return;
    }
    _mocka_count_turns_inner();
}

function _mocka_count_turns_inner() {
    const humanMsgs = document.querySelectorAll('[class*="user-message"]');
    const newCount = humanMsgs.length;
    if (newCount > window.mocka_turn_count) {
        window.mocka_turn_count = newCount;
        if (window.mocka_turn_count > 0 && window.mocka_turn_count % window.MOCKA_TURN_LIMIT === 0) {
            mocka_show_handoff_popup(window.mocka_turn_count);
        }
    }
}

function mocka_show_handoff_popup(turns) {
    const existing = document.getElementById('mocka-handoff-popup');
    if (existing) existing.remove();
    const popup = document.createElement('div');
    popup.id = 'mocka-handoff-popup';
    popup.setAttribute('style', 'position:fixed;top:20px;right:20px;z-index:99999;background:#1a1a2e;color:#e0e0e0;border:2px solid #ff6b35;border-radius:12px;padding:16px 20px;width:320px;font-family:monospace;font-size:13px;box-shadow:0 4px 20px rgba(0,0,0,0.5);');
    popup.innerHTML = '<div style="color:#ff6b35;font-weight:bold;font-size:14px;margin-bottom:8px;">MoCKA: ' + turns + 'turn\u5230\u9054</div><div style="margin-bottom:12px;">\u30c8\u30fc\u30af\u30f3\u6d88\u8cbb\u5897\u52a0\u4e2d\u3002\u65b0chat\u306b\u5f15\u304d\u7d99\u304e\u307e\u3059\u304b\uff1f</div><div style="display:flex;gap:8px;"><button id="mocka-ok" style="background:#ff6b35;color:white;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;flex:1;">\u5f15\u304d\u7d99\u3050</button><button id="mocka-skip" style="background:#333;color:#aaa;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;flex:1;">\u7d9a\u3051\u308b</button></div>';
    document.body.appendChild(popup);
    document.getElementById('mocka-ok').onclick = function() { popup.remove(); mocka_generate_handoff(); };
    document.getElementById('mocka-skip').onclick = function() { popup.remove(); };
    setTimeout(function() { if (popup.parentNode) popup.remove(); }, 30000);
}

function mocka_generate_handoff() {
    Promise.all([
        fetch('http://localhost:5000/public/todo').then(function(r){return r.json();}).catch(function(){return {};}),
        fetch('http://localhost:5000/loop/status').then(function(r){return r.json();}).catch(function(){return {};}),
        fetch('http://localhost:5000/recent_events?n=5').then(function(r){return r.json();}).catch(function(){return {};})
    ]).then(function(results) {
        var todoData   = results[0];
        var loopData   = results[1];
        var eventData  = results[2];

        var todos = (todoData.todos || [])
            .filter(function(t){ return t.status === '\u672a\u7740\u624b'; })
            .slice(0,5)
            .map(function(t){ return '  [' + (t.priority||'\u4e2d') + '] ' + t.id + ': ' + t.title; })
            .join('\n');

        var inprogress = (todoData.todos || [])
            .filter(function(t){ return t.status === '\u9032\u884c\u4e2d'; })
            .map(function(t){ return '  ' + t.id + ': ' + t.title; })
            .join('\n');

        var events = (eventData.events || [])
            .slice(0,5)
            .map(function(e){ return '  ' + (e.event_id||'') + ' [' + (e.what_type||'') + '] ' + (e.title||'').substring(0,40); })
            .join('\n');

        var msgs = document.querySelectorAll('[class*="user-message"]');
        var recentMsgs = Array.from(msgs).slice(-3).map(function(m){
            return '  > ' + m.textContent.substring(0,60).replace(/\n/g,' ');
        }).join('\n');

        var phase = (loopData.current_phase || todoData.current_phase || '\u4e0d\u660e');

        var packet = [
            '[MOCKA\u5f15\u304d\u7d99\u304e\u30d1\u30b1\u30c3\u30c8]',
            '\u30bf\u30fc\u30f3\u6570: ' + window.mocka_turn_count,
            '\u73fe\u30d5\u30a7\u30fc\u30ba: ' + phase,
            '',
            '=== \u76f4\u524d\u306e\u4f5c\u696d\uff08\u3053\u306echat\u306e\u672b\u5c3e3\u767a\u8a00\uff09===',
            recentMsgs || '  \uff08\u53d6\u5f97\u3067\u304d\u305a\uff09',
            '',
            '=== \u76f4\u8fd1\u30a4\u30d9\u30f3\u30c8\uff08events.db\uff09===',
            events || '  \uff08\u53d6\u5f97\u3067\u304d\u305a\uff09',
            '',
            '=== \u9032\u884c\u4e2dTODO ===',
            inprogress || '  \u306a\u3057',
            '',
            '=== \u672a\u7740\u624bTODO\uff08\u512a\u5148\u9806\uff09===',
            todos || '  \u306a\u3057',
            '',
            '=== \u5f15\u304d\u7d99\u304e\u6307\u793a ===',
            '[MOCKA]{"H":"MOCKA_DNA_v2","G":5,"C":"STRICT","P":"SESSION_START_LOCK"}',
            '\u4e0a\u8a18DNA\u3067\u65b0chat\u3092\u958b\u59cb\u3057\u3066\u304f\u3060\u3055\u3044\u3002'
        ].join('\n');

        navigator.clipboard.writeText(packet).then(function() {
            alert('\u5f15\u304d\u7d99\u304e\u30d1\u30b1\u30c3\u30c8\u3092\u30af\u30ea\u30c3\u30d7\u30dc\u30fc\u30c9\u306b\u30b3\u30d4\u30fc\u3057\u307e\u3057\u305f\u3002\n\u65b0\u3057\u3044chat\u3092\u958b\u3044\u3066\u8cbc\u308a\u4ed8\u3051\u3066\u304f\u3060\u3055\u3044\u3002');
            window.open('https://claude.ai/new', '_blank');
        });
    }).catch(function() {
        navigator.clipboard.writeText('[MOCKA\u5f15\u304d\u7d99\u304e] \u30bf\u30fc\u30f3\u6570: ' + window.mocka_turn_count + '\n[MOCKA]{"H":"MOCKA_DNA_v2","G":5,"C":"STRICT","P":"SESSION_START_LOCK"}').then(function() {
            window.open('https://claude.ai/new', '_blank');
        });
    });
}

setInterval(mocka_count_turns, 5000);
// ===== END TURN COUNTER =====


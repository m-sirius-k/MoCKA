(function() {
    if (window.MOCKA_INITIALIZED) return;
    window.MOCKA_INITIALIZED = true;
    console.log("[MOCKA] 自律監視プロトコル v15 起動 (user_voice ON)");

    let lastUrl = window.location.href;
    let dnaSentInThisSession = false;
    let essenceSentInThisSession = false;

    // ===== USER VOICE: 送信フック =====
    // 送信ボタン監視: クリック前にきむら博士の発言を保存する
    let sendButtonHooked = false;

    function hookSendButton() {
        const btn = getSendButton();
        if (!btn || btn._mockaHooked) return;
        btn._mockaHooked = true;
        btn.addEventListener('click', function() {
            const editor = getEditor();
            if (!editor) return;
            const text = getEditorText(editor).trim();
            // DNA注入テキストは保存しない
            if (!text || text.startsWith('[MOCKA]{')) return;
            saveUserVoice(text);
        }, true); // capture=true: Claudeのイベントより先に発火
        console.log("[MOCKA] 送信ボタンにuser_voiceフック完了");
    }

    // Enterキーによる送信も捕捉
    function hookEditorEnter() {
        const editor = getEditor();
        if (!editor || editor._mockaVoiceHooked) return;
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
        const ts  = new Date().toISOString();
        try {
            await fetch('http://127.0.0.1:5000/user_voice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text: text, url: url, timestamp: ts })
            });
            console.log("[MOCKA] user_voice保存:", text.slice(0, 40) + (text.length > 40 ? '...' : ''));
        } catch(e) {
            console.warn("[MOCKA] user_voice保存失敗:", e.message);
        }
    }

    // 定期的にフックを確認（DOM再構築に対応）
    const hookLoop = setInterval(() => {
        hookSendButton();
        hookEditorEnter();
    }, 1500);

    // ===== 既存コード（変更なし）=====

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

    async function injectDNA(el) {
        dnaSentInThisSession = true;
        try {
            console.log("[MOCKA] DNA取得中...");
            const res = await fetch('http://127.0.0.1:5000/get_latest_dna');
            const data = await res.json();
            const p = data.ping;
            const text = `[MOCKA]{"H":"${p.H}","G":${p.G},"C":"${p.C}","P":"${p.P}"}`;
            await writeAndSend(el, text);
            console.log("[MOCKA] DNA注入完了");

            const hookIndicator = document.createElement('div');
            hookIndicator.textContent = '⚡MOCKA HOOKED';
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

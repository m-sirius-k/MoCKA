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

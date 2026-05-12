
// ===== TURN COUNTER (TODO_138) =====
let mocka_turn_count = 0;
const MOCKA_TURN_LIMIT = 20;

function mocka_count_turns() {
    const humanMsgs = document.querySelectorAll('[data-testid="human-turn"], .font-user-message');
    const newCount = humanMsgs.length;
    if (newCount > mocka_turn_count) {
        mocka_turn_count = newCount;
        if (mocka_turn_count > 0 && mocka_turn_count % MOCKA_TURN_LIMIT === 0) {
            mocka_show_handoff_popup(mocka_turn_count);
        }
    }
}

function mocka_show_handoff_popup(turns) {
    const existing = document.getElementById('mocka-handoff-popup');
    if (existing) existing.remove();
    const popup = document.createElement('div');
    popup.id = 'mocka-handoff-popup';
    popup.setAttribute('style', 'position:fixed;top:20px;right:20px;z-index:99999;background:#1a1a2e;color:#e0e0e0;border:2px solid #ff6b35;border-radius:12px;padding:16px 20px;width:320px;font-family:monospace;font-size:13px;box-shadow:0 4px 20px rgba(0,0,0,0.5);');
    popup.innerHTML = '<div style="color:#ff6b35;font-weight:bold;font-size:14px;margin-bottom:8px;">MoCKA: ' + turns + 'turn到達</div><div style="margin-bottom:12px;">トークン消費増加中。新chatに引き継ぎますか？</div><div style="display:flex;gap:8px;"><button id="mocka-ok" style="background:#ff6b35;color:white;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;flex:1;">引き継ぐ</button><button id="mocka-skip" style="background:#333;color:#aaa;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;flex:1;">続ける</button></div>';
    document.body.appendChild(popup);
    document.getElementById('mocka-ok').onclick = function() { popup.remove(); mocka_generate_handoff(); };
    document.getElementById('mocka-skip').onclick = function() { popup.remove(); };
    setTimeout(function() { if (popup.parentNode) popup.remove(); }, 30000);
}

function mocka_generate_handoff() {
    fetch('http://localhost:5000/public/todo')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var todos = (data.todos || []).filter(function(t) { return t.status === '未着手'; }).slice(0,3).map(function(t) { return t.id + ': ' + t.title; }).join('\n');
            var packet = '[MOCKA引き継ぎ]\nターン数: ' + mocka_turn_count + '\n未着手TODO:\n' + (todos || 'なし') + '\n新chatでMoCKA_DNA_v2を使用してください。';
            navigator.clipboard.writeText(packet).then(function() {
                alert('引き継ぎパケットをクリップボードにコピーしました。新しいchatを開いて貼り付けてください。');
                window.open('https://claude.ai/new', '_blank');
            });
        })
        .catch(function() {
            navigator.clipboard.writeText('[MOCKA引き継ぎ] ターン数: ' + mocka_turn_count).then(function() {
                window.open('https://claude.ai/new', '_blank');
            });
        });
}

setInterval(mocka_count_turns, 5000);
// ===== END TURN COUNTER =====

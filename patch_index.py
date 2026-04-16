path = r"C:\Users\sirok\MoCKA\index.html"
with open(path, encoding="utf-8") as f:
    src = f.read()

loop_panel = r"""
    <!-- ── LOOP STATUS & ESSENCE INJECT PANEL ── -->
    <div class="block" id="loop-block">
        <h3>
            <span id="loop-inject-dot" class="server-dot online"></span>
            <span id="loop-inject-label" style="font-size:13px;color:#4ade80;letter-spacing:2px;">ESSENCE INJECT — ON</span>
            <button id="loop-toggle-btn" onclick="toggleInject()"
                style="margin-left:auto;padding:4px 14px;font-size:12px;border-color:#4ade80;color:#4ade80;">
                ⬛ STOP INJECT
            </button>
            <button onclick="refreshLoop()" style="padding:3px 10px;font-size:11px;">↻</button>
        </h3>

        <!-- Essence stats row -->
        <div class="layer-row" style="margin-bottom:10px;">
            <div class="layer-chip green">
                <div class="num" id="loop-essence-count">-</div>
                <div class="lbl">ESSENCE</div>
            </div>
            <div class="layer-chip">
                <div class="num" id="loop-raw-count">-</div>
                <div class="lbl">RAW</div>
            </div>
            <div class="layer-chip amber">
                <div class="num" id="loop-ping-age" style="font-size:13px;margin-top:4px;">-</div>
                <div class="lbl">PING AGE</div>
            </div>
        </div>

        <!-- ping_latest preview -->
        <div style="background:#0a1a0f;border:1px solid #1a4a2a;border-radius:6px;padding:10px;font-size:11px;font-family:monospace;color:#4ade80;min-height:48px;">
            <div style="color:#6b7280;font-size:10px;letter-spacing:1px;margin-bottom:4px;">PING_LATEST.JSON — DNA v2.0 PACKET</div>
            <div id="loop-ping-preview">— loading —</div>
        </div>

        <!-- Loop stages -->
        <div style="margin-top:10px;display:flex;gap:4px;flex-wrap:wrap;">
            <span style="font-size:10px;color:#9ca3af;letter-spacing:1px;width:100%;margin-bottom:4px;">CIVILIZATION LOOP</span>
            <span class="loop-stage" id="ls-1">① Observe</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-2">② Record</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-3">③ Incident</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-4">④ Recurrence</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-5">⑤ Prevention</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-6">⑥ Decision</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-7">⑦ Action</span>
            <span class="loop-arrow">→</span>
            <span class="loop-stage" id="ls-8">⑧ Audit</span>
        </div>
    </div>
"""

loop_style = r"""
        /* loop panel */
        .loop-stage { font-size:10px; padding:4px 8px; border-radius:4px;
            background:#0f2a1a; border:1px solid #1a4a2a; color:#4ade80; letter-spacing:0.5px; }
        .loop-stage.active { background:#004400; border-color:#00cc00; color:#fff;
            box-shadow:0 0 6px #00aa00; }
        .loop-arrow { font-size:10px; color:#374151; align-self:center; }
"""

loop_js = r"""
        async function refreshLoop() {
            try {
                const r = await fetch('/loop/status');
                const d = await r.json();

                // inject mode
                const on = d.inject_mode === 'ON';
                const dot   = document.getElementById('loop-inject-dot');
                const label = document.getElementById('loop-inject-label');
                const btn   = document.getElementById('loop-toggle-btn');
                dot.className   = 'server-dot ' + (on ? 'online' : 'offline');
                label.innerText = 'ESSENCE INJECT — ' + d.inject_mode;
                label.style.color = on ? '#4ade80' : '#6b7280';
                btn.innerText     = on ? '⬛ STOP INJECT' : '▶ START INJECT';
                btn.style.borderColor = on ? '#4ade80' : '#fbbf24';
                btn.style.color       = on ? '#4ade80' : '#fbbf24';

                // stats
                document.getElementById('loop-essence-count').innerText = d.essence_count ?? '-';
                document.getElementById('loop-raw-count').innerText     = d.raw_count     ?? '-';
                document.getElementById('loop-ping-age').innerText      = d.ping_age      ?? '-';

                // ping preview
                const ping = d.ping_latest || {};
                const preview = Object.entries(ping).slice(0,6)
                    .map(([k,v]) => `<span style="color:#9ca3af">${k}</span>: <span style="color:#4ade80">${JSON.stringify(v).slice(0,40)}</span>`)
                    .join('  ');
                document.getElementById('loop-ping-preview').innerHTML = preview || '— no packet —';

                // loop stage animation (cycle through)
                const stages = [1,2,3,4,5,6,7,8];
                const active = Math.floor(Date.now()/1500) % 8 + 1;
                stages.forEach(i => {
                    const el = document.getElementById('ls-'+i);
                    if(el) el.className = 'loop-stage' + (i===active?' active':'');
                });
            } catch(e) { console.error('loop status error', e); }
        }

        async function toggleInject() {
            try {
                const r = await fetch('/loop/inject_toggle', {method:'POST'});
                const d = await r.json();
                await refreshLoop();
            } catch(e) { console.error('toggle error', e); }
        }
"""

# スタイル挿入（</style>の直前）
src2 = src.replace("    </style>", loop_style + "    </style>")

# パネル挿入（最初の<div class="block">の直前）
src2 = src2.replace('    <div class="block">', loop_panel + '    <div class="block">', 1)

# JS挿入（window.onload の直前）
src2 = src2.replace("        window.onload = () => {",
    loop_js + "        window.onload = () => {")

# setInterval にrefreshLoop追加
src2 = src2.replace(
    "setInterval(refreshQueue, 10000);",
    "setInterval(refreshQueue, 10000); setInterval(refreshLoop, 3000); refreshLoop();"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(src2)
print("index.html updated: LOOP panel added")

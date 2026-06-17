/* Distribution Center v2.0 — dc.js */
'use strict';

/* ═══════════════════════════════════════════════
   DATA STORE  (replace with API calls in prod)
═══════════════════════════════════════════════ */
const DC = {

  data: {
    stats: { scheduled:8, successRate:92, queueCount:3, failedCount:1, activeChannels:8, publishedToday:5 },

    aiRecommendations: [
      { level:'ok',   text:'LinkedIn への投稿は 12:00 が最適です（過去データ: CTR +22%）' },
      { level:'warn', text:'X (Twitter) rate limit が 85% です。次の投稿まで 43 分待機推奨' },
      { level:'ok',   text:'Dev.to 記事は Markdown 変換済みで配信可能状態です' },
    ],

    queue: [
      { id:'Q001', title:'MoCKA v3.1 Release Notes',      channel:'GitHub Release', priority:'高', time:'10:30', ai:'Claude',   status:'waiting' },
      { id:'Q002', title:'Institution Runtime 解説',        channel:'Dev.to',        priority:'中', time:'12:00', ai:'GPT-4o',   status:'waiting' },
      { id:'Q003', title:'Weekly Report 2026-W24',         channel:'LinkedIn',      priority:'高', time:'09:00', ai:'Claude',   status:'posting' },
    ],

    drafts: [
      { id:'D001', title:'SEO-OS Phase6 発表',              type:'ai',     tags:['seo','phase6'],          status:'review' },
      { id:'D002', title:'vasAI v1.5 ロードマップ',          type:'manual', tags:['vasai','roadmap'],       status:'draft'  },
      { id:'D003', title:'Architecture Decision Record',   type:'ai',     tags:['architecture','adr'],    status:'draft'  },
    ],

    scheduled: [
      { id:'S001', title:'MoCKA v3.1 Release Notes',      channel:'GitHub Release', time:'2026-06-17 10:30', status:'scheduled' },
      { id:'S002', title:'Institution Runtime 解説',        channel:'Dev.to',        time:'2026-06-17 12:00', status:'scheduled' },
      { id:'S003', title:'BEE v2.0 Architecture',         channel:'Medium',        time:'2026-06-18 09:00', status:'scheduled' },
      { id:'S004', title:'Weekly Report 2026-W25',        channel:'LinkedIn',      time:'2026-06-20 08:00', status:'scheduled' },
    ],

    publishing: [
      { id:'P001', title:'Weekly Report 2026-W24', channel:'LinkedIn', progress:65,
        log:['09:00:02 認証 OK','09:00:04 コンテンツ変換中...','09:00:07 LinkedIn API 送信中...'] },
    ],

    published: [
      { id:'PB001', title:'MoCKA Phase4 完了報告',    channel:'GitHub',  url:'https://github.com/m-sirius-k/MoCKA', date:'2026-06-16 14:22', views:142 },
      { id:'PB002', title:'vasAI v1.4.9 VERIFIED',   channel:'Dev.to',  url:'https://dev.to/',                     date:'2026-06-15 11:00', views:89  },
      { id:'PB003', title:'BEE Ecology 解説',         channel:'Medium',  url:'https://medium.com/',                 date:'2026-06-14 09:30', views:201 },
    ],

    failed: [
      { id:'F001', title:'PHI OS v1.0 発表', channel:'Substack', error:'認証エラー', type:'auth', time:'2026-06-16 09:00', retries:2 },
    ],

    retry: [
      { id:'R001', title:'PHI OS v1.0 発表', channel:'Substack', retries:2, nextRun:'2026-06-17 11:00', successRate:0 },
    ],

    channels: [
      {name:'GitHub',            cat:'Developer',  status:'connected', type:'token',    limit:'5000/h'},
      {name:'GitHub Release',    cat:'Developer',  status:'connected', type:'token',    limit:'5000/h'},
      {name:'GitHub Discussions', cat:'Developer', status:'connected', type:'token',    limit:'5000/h'},
      {name:'GitHub Pages',      cat:'Developer',  status:'disabled',  type:'token',    limit:'1000/h'},
      {name:'Dev.to',            cat:'Developer',  status:'connected', type:'api_key',  limit:'30/h'},
      {name:'WordPress',         cat:'Blog',       status:'connected', type:'app_pass', limit:'200/h'},
      {name:'Medium',            cat:'Blog',       status:'connected', type:'token',    limit:'100/h'},
      {name:'Substack',          cat:'Blog',       status:'pending',   type:'session',  limit:'20/h'},
      {name:'LinkedIn',          cat:'Business',   status:'connected', type:'oauth2',   limit:'100/h'},
      {name:'X',                 cat:'Social',     status:'connected', type:'oauth2',   limit:'50/h'},
      {name:'Bluesky',           cat:'Social',     status:'connected', type:'app_pass', limit:'100/h'},
      {name:'Mastodon',          cat:'Social',     status:'connected', type:'oauth2',   limit:'300/h'},
      {name:'Threads',           cat:'Social',     status:'pending',   type:'oauth2',   limit:'25/h'},
      {name:'Instagram',         cat:'Social',     status:'pending',   type:'oauth2',   limit:'25/h'},
      {name:'Facebook',          cat:'Social',     status:'pending',   type:'oauth2',   limit:'200/h'},
      {name:'Reddit',            cat:'Community',  status:'pending',   type:'oauth2',   limit:'60/h'},
      {name:'Discord',           cat:'Community',  status:'connected', type:'bot',      limit:'50/h'},
      {name:'Slack',             cat:'Enterprise', status:'pending',   type:'bot',      limit:'1/h'},
      {name:'YouTube',           cat:'Video',      status:'pending',   type:'oauth2',   limit:'6/h'},
      {name:'YouTube Shorts',    cat:'Video',      status:'pending',   type:'oauth2',   limit:'6/h'},
      {name:'TikTok',            cat:'Video',      status:'pending',   type:'oauth2',   limit:'20/h'},
      {name:'LINE Official',     cat:'Messaging',  status:'pending',   type:'token',    limit:'1000/h'},
    ],

    campaigns: [
      { id:'C001', name:'MoCKA v3 Launch',     period:'2026-06-15 〜 2026-06-30',
        channels:['GitHub','Dev.to','LinkedIn','X'], goal:'リーチ 1,000', progress:45 },
      { id:'C002', name:'vasAI Enterprise',    period:'2026-07-01 〜 2026-07-31',
        channels:['LinkedIn','Medium'],              goal:'リード 50',    progress:0  },
    ],

    history: [
      { eventId:'E20260616_031', title:'MoCKA Phase4 完了報告', channel:'GitHub',  date:'2026-06-16 14:22', status:'success' },
      { eventId:'E20260615_044', title:'vasAI v1.4.9 VERIFIED', channel:'Dev.to',  date:'2026-06-15 11:00', status:'success' },
      { eventId:'E20260614_033', title:'PHI OS v1.0 発表',       channel:'Substack',date:'2026-06-14 09:00', status:'failed'  },
      { eventId:'E20260613_021', title:'BEE Ecology 解説',        channel:'Medium',  date:'2026-06-13 09:30', status:'success' },
    ],
  },

  /* ═══════════════════════════════════════════════
     NAVIGATION
  ═══════════════════════════════════════════════ */
  activePanel: 'dashboard',

  navigate(panelId) {
    document.querySelectorAll('.dc-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.dc-nav-item').forEach(n => n.classList.remove('active'));
    const panel   = document.getElementById('panel-' + panelId);
    const navItem = document.querySelector(`[data-panel="${panelId}"]`);
    if (panel)   panel.classList.add('active');
    if (navItem) navItem.classList.add('active');
    DC.activePanel = panelId;
    DC.inspector.clear();
  },

  /* ═══════════════════════════════════════════════
     RENDERERS
  ═══════════════════════════════════════════════ */
  render: {

    dashboard() {
      const s  = DC.data.stats;
      const ai = DC.data.aiRecommendations;
      const el = document.getElementById('panel-dashboard');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div>
            <div class="dc-panel-title">Dashboard</div>
            <div class="dc-panel-sub">${new Date().toLocaleDateString('ja-JP',{year:'numeric',month:'long',day:'numeric',weekday:'short'})} の運用状況</div>
          </div>
          <div class="dc-panel-actions">
            <button class="dc-btn" data-action="refresh">↻ Refresh</button>
          </div>
        </div>
        <div class="dc-stat-grid">
          <div class="dc-stat info"><div class="dc-stat-val">${s.scheduled}</div><div class="dc-stat-lbl">今日の投稿予定</div></div>
          <div class="dc-stat ok">  <div class="dc-stat-val">${s.successRate}%</div><div class="dc-stat-lbl">本日の成功率</div></div>
          <div class="dc-stat info"><div class="dc-stat-val">${s.queueCount}</div><div class="dc-stat-lbl">キュー件数</div></div>
          <div class="dc-stat ${s.failedCount>0?'warn':'ok'}"><div class="dc-stat-val">${s.failedCount}</div><div class="dc-stat-lbl">失敗件数</div></div>
          <div class="dc-stat ok">  <div class="dc-stat-val">${s.activeChannels}</div><div class="dc-stat-lbl">稼働媒体数</div></div>
          <div class="dc-stat ok">  <div class="dc-stat-val">${s.publishedToday}</div><div class="dc-stat-lbl">本日投稿済み</div></div>
        </div>
        <div class="dc-two-col">
          <div class="dc-card">
            <div class="dc-card-hd">
              <span class="dc-card-title">AI 推奨事項</span>
              <span class="badge badge-blue">AI</span>
            </div>
            ${ai.map(r=>`
              <div class="ai-row">
                <span class="dot dot-${r.level==='ok'?'ok':'warn'}"></span>
                <span>${r.text}</span>
              </div>`).join('')}
          </div>
          <div class="dc-card">
            <div class="dc-card-hd"><span class="dc-card-title">最近の投稿</span></div>
            ${DC.data.published.map(p=>`
              <div style="display:flex;align-items:center;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:11px">
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-right:8px">${p.title}</span>
                <span class="badge badge-ok">${p.views.toLocaleString()} views</span>
              </div>`).join('')}
          </div>
        </div>
        <div class="dc-card">
          <div class="dc-card-hd"><span class="dc-card-title">配信キュー — 直近</span></div>
          ${DC.data.queue.map(q=>`
            <div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:11px">
              <span class="dot dot-${q.status==='posting'?'blue':'warn'}"></span>
              <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${q.title}</span>
              <span class="badge badge-muted">${q.channel}</span>
              <span class="text-blue">${q.time}</span>
            </div>`).join('')}
        </div>`;
      DC.utils.bindAction(el, 'refresh', () => DC.refresh());
    },

    queue() {
      const items = DC.data.queue;
      const el    = document.getElementById('panel-queue');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Queue</div><div class="dc-panel-sub">${items.length} 件待機中</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn dc-btn-primary" data-action="add">+ 追加</button>
          </div>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>#</th><th>タイトル</th><th>媒体</th><th>優先度</th><th>時刻</th><th>担当AI</th><th>状態</th><th>操作</th></tr>
            </thead>
            <tbody>
              ${items.map(q=>`
                <tr data-item='${JSON.stringify(q)}' data-type="queue">
                  <td class="td-mono text-muted">${q.id}</td>
                  <td>${q.title}</td>
                  <td><span class="badge badge-muted">${q.channel}</span></td>
                  <td><span class="badge badge-${q.priority==='高'?'ng':'warn'}">${q.priority}</span></td>
                  <td class="text-blue">${q.time}</td>
                  <td class="text-muted">${q.ai}</td>
                  <td>
                    <span class="dot dot-${q.status==='posting'?'blue':'warn'}"></span>
                    ${q.status==='posting'?'配信中':'待機'}
                  </td>
                  <td>
                    <button class="dc-btn dc-btn-danger" data-action="cancel" data-id="${q.id}"
                      style="font-size:10px;padding:2px 7px">取消</button>
                  </td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindTableRows(el, 'queue');
    },

    calendar() {
      const year = 2026, month = 5;
      const firstDay    = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month+1, 0).getDate();
      const days        = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
      const events = {
        14:[{t:'PHI OS 発表',c:'fail'}],
        15:[{t:'vasAI Release',c:'ok'}],
        17:[{t:'Weekly Report',c:'ok'},{t:'Dev.to 記事',c:'sched'}],
        18:[{t:'BEE Architecture',c:'sched'}],
        20:[{t:'LinkedIn Post',c:'sched'}],
        24:[{t:'Monthly Report',c:'sched'}],
      };
      let cells = '';
      for (let i=0; i<42; i++) {
        const d = i - firstDay + 1;
        if (d<1 || d>daysInMonth) {
          cells += `<div class="cal-cell other-month"><div class="cal-date">${d<1?'':d}</div></div>`;
        } else {
          const isToday = d===17;
          const evs     = events[d]||[];
          cells += `<div class="cal-cell${isToday?' today':''}">
            <div class="cal-date">${d}</div>
            ${evs.map(e=>`<div class="cal-event ${e.c}" title="${e.t}">${e.t}</div>`).join('')}
          </div>`;
        }
      }
      document.getElementById('panel-calendar').innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Calendar</div></div>
          <div class="dc-panel-actions">
            <div class="dc-btn-group">
              <button class="dc-btn active" data-view="month">月</button>
              <button class="dc-btn"        data-view="week" >週</button>
              <button class="dc-btn"        data-view="day"  >日</button>
            </div>
          </div>
        </div>
        <div class="cal-top">
          <button class="dc-btn" id="cal-prev">‹</button>
          <span class="cal-month-label">2026年 6月</span>
          <button class="dc-btn" id="cal-next">›</button>
        </div>
        <div class="cal-grid">
          <div class="cal-header">
            ${days.map(d=>`<div class="cal-header-cell">${d}</div>`).join('')}
          </div>
          <div class="cal-body">${cells}</div>
        </div>`;
    },

    draft() {
      const items = DC.data.drafts;
      const el    = document.getElementById('panel-draft');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Draft</div><div class="dc-panel-sub">${items.length} 件の下書き</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn dc-btn-ai"      data-action="ai-gen">AI 生成</button>
            <button class="dc-btn dc-btn-primary" data-action="new">+ 手動作成</button>
          </div>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>#</th><th>タイトル</th><th>作成方法</th><th>タグ</th><th>状態</th><th>操作</th></tr>
            </thead>
            <tbody>
              ${items.map(d=>`
                <tr data-item='${JSON.stringify(d)}' data-type="draft">
                  <td class="td-mono text-muted">${d.id}</td>
                  <td>${d.title}</td>
                  <td><span class="badge badge-${d.type==='ai'?'blue':'teal'}">${d.type==='ai'?'AI 生成':'手動'}</span></td>
                  <td>${d.tags.map(t=>`<span class="badge badge-muted" style="margin-right:2px">${t}</span>`).join('')}</td>
                  <td><span class="badge badge-${d.status==='review'?'warn':'muted'}">${d.status==='review'?'レビュー待ち':'下書き'}</span></td>
                  <td>
                    <button class="dc-btn dc-btn-primary" data-action="publish" data-id="${d.id}"
                      style="font-size:10px;padding:2px 7px">配信</button>
                  </td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindTableRows(el, 'draft');
    },

    scheduled() {
      const items = DC.data.scheduled;
      const el    = document.getElementById('panel-scheduled');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Scheduled</div><div class="dc-panel-sub">${items.length} 件予約済み</div></div>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>#</th><th>タイトル</th><th>媒体</th><th>配信予定日時</th><th>状態</th><th>操作</th></tr>
            </thead>
            <tbody>
              ${items.map(s=>`
                <tr data-item='${JSON.stringify(s)}' data-type="scheduled">
                  <td class="td-mono text-muted">${s.id}</td>
                  <td>${s.title}</td>
                  <td><span class="badge badge-muted">${s.channel}</span></td>
                  <td class="text-blue">${s.time}</td>
                  <td><span class="badge badge-blue">予約済み</span></td>
                  <td style="display:flex;gap:4px">
                    <button class="dc-btn" data-action="edit" data-id="${s.id}"
                      style="font-size:10px;padding:2px 7px">変更</button>
                    <button class="dc-btn dc-btn-danger" data-action="cancel" data-id="${s.id}"
                      style="font-size:10px;padding:2px 7px">取消</button>
                  </td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindTableRows(el, 'scheduled');
    },

    publishing() {
      const items = DC.data.publishing;
      const el    = document.getElementById('panel-publishing');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Publishing</div><div class="dc-panel-sub">現在配信中: ${items.length} 件</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn" data-action="refresh">↻ 更新</button>
          </div>
        </div>
        ${items.length===0
          ? `<div class="dc-card"><p class="text-muted" style="text-align:center;padding:20px;font-size:11px">現在配信中のコンテンツはありません</p></div>`
          : items.map(p=>`
            <div class="dc-card dc-card-clickable" data-item='${JSON.stringify({...p,log:undefined})}' data-type="publishing">
              <div class="dc-card-hd">
                <span class="dc-card-title">${p.title}</span>
                <span class="badge badge-blue">配信中</span>
              </div>
              <div style="font-size:11px;color:var(--muted);margin-bottom:8px">媒体: ${p.channel}</div>
              <div class="dc-progress">
                <div class="dc-progress-fill" style="width:${p.progress}%;background:var(--blue)"></div>
              </div>
              <div style="font-size:10px;color:var(--blue);margin-top:4px">${p.progress}% 完了</div>
              <div class="log-box">${p.log.map(l=>`<div>${l}</div>`).join('')}</div>
            </div>`).join('')}`;
      DC.utils.bindCardRows(el, 'publishing');
      DC.utils.bindAction(el, 'refresh', () => DC.render.publishing());
    },

    published() {
      const items = DC.data.published;
      const el    = document.getElementById('panel-published');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Published</div><div class="dc-panel-sub">${items.length} 件投稿済み</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn" data-action="export-csv">CSV</button>
          </div>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>#</th><th>タイトル</th><th>媒体</th><th>投稿日時</th><th>閲覧数</th><th>URL</th></tr>
            </thead>
            <tbody>
              ${items.map(p=>`
                <tr data-item='${JSON.stringify(p)}' data-type="published">
                  <td class="td-mono text-muted">${p.id}</td>
                  <td>${p.title}</td>
                  <td><span class="badge badge-muted">${p.channel}</span></td>
                  <td class="text-muted">${p.date}</td>
                  <td class="text-ok">${p.views.toLocaleString()}</td>
                  <td><a class="dc-link" href="${p.url}" target="_blank" rel="noopener">リンク</a></td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindTableRows(el, 'published');
      DC.utils.bindAction(el, 'export-csv', () => DC.export.csv());
    },

    failed() {
      const items = DC.data.failed;
      const el    = document.getElementById('panel-failed');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Failed</div><div class="dc-panel-sub">${items.length} 件の失敗</div></div>
        </div>
        ${items.length===0
          ? `<div class="dc-card"><p class="text-ok" style="text-align:center;padding:20px;font-size:11px">失敗はありません ✓</p></div>`
          : `<div class="dc-table-wrap"><table class="dc-table">
              <thead>
                <tr><th>#</th><th>タイトル</th><th>媒体</th><th>原因</th><th>分類</th><th>日時</th><th>再試行数</th><th>操作</th></tr>
              </thead>
              <tbody>
                ${items.map(f=>`
                  <tr data-item='${JSON.stringify(f)}' data-type="failed">
                    <td class="td-mono text-muted">${f.id}</td>
                    <td>${f.title}</td>
                    <td><span class="badge badge-muted">${f.channel}</span></td>
                    <td class="text-ng">${f.error}</td>
                    <td><span class="badge badge-ng">${f.type}</span></td>
                    <td class="text-muted">${f.time}</td>
                    <td class="text-warn">${f.retries}</td>
                    <td>
                      <button class="dc-btn dc-btn-primary" data-action="retry" data-id="${f.id}"
                        style="font-size:10px;padding:2px 7px">再送</button>
                    </td>
                  </tr>`).join('')}
              </tbody>
            </table></div>`}`;
      DC.utils.bindTableRows(el, 'failed');
    },

    retry() {
      const items = DC.data.retry;
      const el    = document.getElementById('panel-retry');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Retry Queue</div><div class="dc-panel-sub">${items.length} 件</div></div>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>#</th><th>タイトル</th><th>媒体</th><th>再送回数</th><th>次回実行</th><th>成功率</th><th>操作</th></tr>
            </thead>
            <tbody>
              ${items.map(r=>`
                <tr data-item='${JSON.stringify(r)}' data-type="retry">
                  <td class="td-mono text-muted">${r.id}</td>
                  <td>${r.title}</td>
                  <td><span class="badge badge-muted">${r.channel}</span></td>
                  <td class="text-warn">${r.retries}</td>
                  <td class="text-blue">${r.nextRun}</td>
                  <td class="text-${r.successRate>50?'ok':'ng'}">${r.successRate}%</td>
                  <td style="display:flex;gap:4px">
                    <button class="dc-btn dc-btn-primary" data-action="retry-now" data-id="${r.id}"
                      style="font-size:10px;padding:2px 7px">今すぐ再送</button>
                    <button class="dc-btn dc-btn-danger" data-action="cancel" data-id="${r.id}"
                      style="font-size:10px;padding:2px 7px">取消</button>
                  </td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindTableRows(el, 'retry');
    },

    channels() {
      const items = DC.data.channels;
      const cats  = [...new Set(items.map(c=>c.cat))];
      const total = items.length;
      const conn  = items.filter(c=>c.status==='connected').length;
      const el    = document.getElementById('panel-channels');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div>
            <div class="dc-panel-title">Channels</div>
            <div class="dc-panel-sub">${conn} 接続済み / ${total} 媒体</div>
          </div>
          <div class="dc-panel-actions">
            <button class="dc-btn dc-btn-primary" data-action="add">+ 追加</button>
          </div>
        </div>
        ${cats.map(cat=>`
          <div class="section-hd">${cat}</div>
          <div class="ch-grid mb-10">
            ${items.filter(c=>c.cat===cat).map(c=>`
              <div class="ch-card ${c.status}" data-item='${JSON.stringify(c)}' data-type="channel">
                <div class="ch-card-name">${c.name}</div>
                <div class="ch-card-meta">
                  <span class="dot dot-${c.status==='connected'?'ok':c.status==='pending'?'warn':'off'}"></span>
                  ${c.status==='connected'?'接続済み':c.status==='pending'?'設定待ち':'無効'}<br>
                  ${c.type} &nbsp;·&nbsp; ${c.limit}
                </div>
              </div>`).join('')}
          </div>`).join('')}`;
      DC.utils.bindCardRows(el, 'channel');
    },

    campaigns() {
      const items = DC.data.campaigns;
      const el    = document.getElementById('panel-campaigns');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">Campaigns</div><div class="dc-panel-sub">${items.length} キャンペーン</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn dc-btn-primary" data-action="new">+ 新規</button>
          </div>
        </div>
        ${items.map(c=>`
          <div class="dc-card dc-card-clickable" data-item='${JSON.stringify(c)}' data-type="campaign">
            <div class="dc-card-hd">
              <span class="dc-card-title">${c.name}</span>
              <span class="badge badge-${c.progress>0?'blue':'muted'}">${c.progress>0?'進行中':'未開始'}</span>
            </div>
            <div style="font-size:11px;color:var(--muted);margin-bottom:7px">
              ${c.period} &nbsp;·&nbsp; 目標: ${c.goal}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:9px">
              ${c.channels.map(ch=>`<span class="badge badge-muted">${ch}</span>`).join('')}
            </div>
            <div class="dc-progress">
              <div class="dc-progress-fill" style="width:${c.progress}%;background:var(--blue)"></div>
            </div>
            <div style="font-size:10px;color:var(--blue);margin-top:4px">${c.progress}% 完了</div>
          </div>`).join('')}`;
      DC.utils.bindCardRows(el, 'campaign');
    },

    history() {
      const items = DC.data.history;
      const el    = document.getElementById('panel-history');
      el.innerHTML = `
        <div class="dc-panel-hd">
          <div><div class="dc-panel-title">History</div><div class="dc-panel-sub">${items.length} 件</div></div>
          <div class="dc-panel-actions">
            <button class="dc-btn" data-action="export-csv">CSV</button>
            <button class="dc-btn" data-action="export-json">JSON</button>
            <button class="dc-btn dc-btn-ai" data-action="audit">監査ログ</button>
          </div>
        </div>
        <div class="dc-filter-row">
          <input type="text" class="dc-filter-input" id="hist-search" placeholder="タイトル・EventID で検索...">
          <select class="dc-filter-select" id="hist-ch">
            <option value="">全媒体</option>
            ${[...new Set(items.map(h=>h.channel))].map(ch=>`<option value="${ch}">${ch}</option>`).join('')}
          </select>
          <select class="dc-filter-select" id="hist-st">
            <option value="">全状態</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </div>
        <div class="dc-table-wrap">
          <table class="dc-table">
            <thead>
              <tr><th>Event ID</th><th>タイトル</th><th>媒体</th><th>日時</th><th>状態</th><th>監査</th></tr>
            </thead>
            <tbody id="hist-tbody">
              ${DC.render._histRows(items)}
            </tbody>
          </table>
        </div>`;
      DC.utils.bindAction(el, 'export-csv',  () => DC.export.csv());
      DC.utils.bindAction(el, 'export-json', () => DC.export.json());
      DC.utils.bindTableRows(el, 'history');
      ['hist-search','hist-ch','hist-st'].forEach(id=>{
        document.getElementById(id).addEventListener('input', DC.render._histFilter);
        document.getElementById(id).addEventListener('change', DC.render._histFilter);
      });
    },

    _histRows(items) {
      return items.map(h=>`
        <tr data-item='${JSON.stringify(h)}' data-type="history">
          <td class="td-mono text-muted">${h.eventId}</td>
          <td>${h.title}</td>
          <td><span class="badge badge-muted">${h.channel}</span></td>
          <td class="text-muted">${h.date}</td>
          <td><span class="badge badge-${h.status==='success'?'ok':'ng'}">${h.status==='success'?'SUCCESS':'FAILED'}</span></td>
          <td><a class="dc-link" href="#" data-event="${h.eventId}">ログ</a></td>
        </tr>`).join('');
    },

    _histFilter() {
      const q  = (document.getElementById('hist-search')?.value||'').toLowerCase();
      const ch = document.getElementById('hist-ch')?.value||'';
      const st = document.getElementById('hist-st')?.value||'';
      const filtered = DC.data.history.filter(h=>
        (!q  || h.title.toLowerCase().includes(q) || h.eventId.toLowerCase().includes(q)) &&
        (!ch || h.channel===ch) &&
        (!st || h.status===st)
      );
      const tbody = document.getElementById('hist-tbody');
      if (tbody) tbody.innerHTML = DC.render._histRows(filtered);
    },
  },

  /* ═══════════════════════════════════════════════
     INSPECTOR
  ═══════════════════════════════════════════════ */
  inspector: {
    aiComments: {
      queue:      'この投稿の配信順序と時間帯は最適化されています。',
      draft:      'コンテンツ品質は良好です。公開前にタグを確認してください。',
      scheduled:  '予約時刻は対象オーディエンスの活動ピーク帯と一致しています。',
      publishing: '配信進捗は正常です。完了まであと数分の見込みです。',
      published:  'この投稿のパフォーマンスは平均を上回っています。',
      failed:     '認証トークンの再発行を試みてください。OAuth 再認証が必要な可能性があります。',
      retry:      '次回の自動再送を待つか、認証情報を確認してから手動再送を推奨します。',
      channel:    'このチャンネルの利用状況は正常範囲内です。',
      campaign:   'キャンペーンの進捗は計画通りです。',
      history:    'MoCKA Event Ledger に記録済みです。監査トレースが利用可能です。',
    },

    show(type, data) {
      const body  = document.getElementById('inspector-body');
      const title = document.getElementById('inspector-title');
      title.textContent = type.toUpperCase();

      const skip = new Set(['log']);
      const detail = Object.entries(data)
        .filter(([k])=>!skip.has(k))
        .map(([k,v])=>`
          <div class="insp-row">
            <span class="insp-lbl">${k}</span>
            <span class="insp-val">${Array.isArray(v)?v.join(', '):v}</span>
          </div>`).join('');

      body.innerHTML = `
        <div class="insp-section">
          <div class="insp-section-title">詳細情報</div>
          ${detail}
        </div>
        <div class="insp-section">
          <div class="insp-section-title">AI コメント</div>
          <div class="insp-ai">${DC.inspector.aiComments[type]||'特記事項はありません。'}</div>
        </div>
        <div class="insp-section">
          <div class="insp-section-title">操作</div>
          <div class="insp-ops">
            <button class="dc-btn dc-btn-primary" style="font-size:11px">配信</button>
            <button class="dc-btn"                style="font-size:11px">編集</button>
            <button class="dc-btn dc-btn-danger"  style="font-size:11px">削除</button>
          </div>
        </div>
        <div class="insp-section">
          <div class="insp-section-title">操作履歴</div>
          <div class="insp-row">
            <span class="insp-lbl">最終確認</span>
            <span class="insp-val">${new Date().toLocaleString('ja-JP')}</span>
          </div>
        </div>`;
    },

    clear() {
      document.getElementById('inspector-body').innerHTML = '<div class="insp-empty">アイテムを選択してください</div>';
      document.getElementById('inspector-title').textContent = 'Inspector';
    },
  },

  /* ═══════════════════════════════════════════════
     UTILITIES
  ═══════════════════════════════════════════════ */
  utils: {
    bindTableRows(el, type) {
      el.querySelectorAll('tr[data-item]').forEach(tr=>{
        tr.addEventListener('click', e=>{
          if (e.target.closest('button, a')) return;
          try { DC.inspector.show(type, JSON.parse(tr.dataset.item)); } catch(_){}
        });
      });
    },
    bindCardRows(el, type) {
      el.querySelectorAll('[data-item]').forEach(card=>{
        card.addEventListener('click', e=>{
          if (e.target.closest('button')) return;
          try { DC.inspector.show(type, JSON.parse(card.dataset.item)); } catch(_){}
        });
      });
    },
    bindAction(el, action, fn) {
      el.querySelectorAll(`[data-action="${action}"]`).forEach(btn=>{
        btn.addEventListener('click', e=>{ e.stopPropagation(); fn(btn.dataset.id); });
      });
    },
  },

  /* ═══════════════════════════════════════════════
     EXPORT
  ═══════════════════════════════════════════════ */
  export: {
    _download(filename, content, type) {
      const a   = document.createElement('a');
      a.href     = URL.createObjectURL(new Blob([content],{type}));
      a.download = filename;
      a.click();
      setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
    },
    csv() {
      const rows = DC.data.history.map(h=>`${h.eventId},"${h.title}",${h.channel},${h.date},${h.status}`);
      DC.export._download('distribution_history.csv','EventID,Title,Channel,Date,Status\n'+rows.join('\n'),'text/csv');
    },
    json() {
      DC.export._download('distribution_history.json', JSON.stringify(DC.data.history,null,2),'application/json');
    },
  },

  /* ═══════════════════════════════════════════════
     API STUBS  (replace with real fetch() calls)
  ═══════════════════════════════════════════════ */
  api: {
    async get(endpoint) {
      const map = {
        '/api/distribution/queue':     DC.data.queue,
        '/api/distribution/drafts':    DC.data.drafts,
        '/api/distribution/scheduled': DC.data.scheduled,
        '/api/distribution/published': DC.data.published,
        '/api/distribution/failed':    DC.data.failed,
        '/api/distribution/channels':  DC.data.channels,
        '/api/distribution/history':   DC.data.history,
      };
      return Promise.resolve(map[endpoint]||null);
    },
    async post(endpoint, body) {
      console.log('[DC API stub]', endpoint, body);
      return Promise.resolve({status:'ok'});
    },
  },

  /* ═══════════════════════════════════════════════
     STATUS BAR
  ═══════════════════════════════════════════════ */
  updateStatusBar() {
    const d = DC.data;
    document.getElementById('status-channels').textContent =
      `Channels: ${d.channels.filter(c=>c.status==='connected').length} active`;
    document.getElementById('status-queue').textContent =
      `Queue: ${d.queue.length}`;
    document.getElementById('status-today').textContent =
      `Today: ${d.published.length} posted`;
    document.getElementById('status-failed').textContent =
      `Failed: ${d.failed.length}`;
    document.getElementById('status-time').textContent =
      new Date().toLocaleTimeString('ja-JP');
  },

  /* ═══════════════════════════════════════════════
     REFRESH ALL
  ═══════════════════════════════════════════════ */
  refresh() {
    const panels = ['dashboard','queue','calendar','draft','scheduled',
                    'publishing','published','failed','retry','channels','campaigns','history'];
    panels.forEach(p => { try{ DC.render[p](); }catch(e){ console.error('[DC render]', p, e); }});
    DC.updateStatusBar();
  },

  /* ═══════════════════════════════════════════════
     INIT
  ═══════════════════════════════════════════════ */
  init() {
    // Navigation
    document.querySelectorAll('.dc-nav-item[data-panel]').forEach(item=>{
      item.addEventListener('click', ()=> DC.navigate(item.dataset.panel));
    });

    // Inspector close
    document.getElementById('inspector-close')
      .addEventListener('click', ()=> DC.inspector.clear());

    // Global search
    document.getElementById('dc-search').addEventListener('input', e=>{
      if (DC.activePanel==='history') {
        const input = document.getElementById('hist-search');
        if (input) { input.value = e.target.value; DC.render._histFilter(); }
      }
    });

    // Top bar actions
    document.getElementById('btn-refresh').addEventListener('click', ()=> DC.refresh());
    document.getElementById('btn-export') .addEventListener('click', ()=> DC.export.csv());

    // Render all + start clock
    DC.refresh();
    setInterval(()=> DC.updateStatusBar(), 1000);
  },
};

document.addEventListener('DOMContentLoaded', ()=> DC.init());

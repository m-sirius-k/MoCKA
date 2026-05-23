
let allMessages = [];
let currentRole = 'all';
let currentQuery = '';
let currentSort = 'desc';
let currentPeriod = 'all';

function loadStats() {
  chrome.runtime.sendMessage({ type: 'GET_STATS' }, (res) => {
    if (res?.ok) {
      document.getElementById('stat-total').textContent = res.data.total;
      document.getElementById('stat-sessions').textContent = res.data.sessions;
    }
  });
}

function loadMessages(query = '') {
  currentQuery = query;
  const msg = query
    ? { type: 'GET_MESSAGES', query, limit: 200 }
    : { type: 'GET_MESSAGES', limit: 200 };
  chrome.runtime.sendMessage(msg, (res) => {
    if (res?.ok) {
      allMessages = res.data;
      renderMessages();
    }
  });
}

function renderMessages() {
  const list = document.getElementById('message-list');

  // 期間フィルター
  const now = new Date();
  let filtered = allMessages.filter(m => {
    if (currentRole !== 'all' && m.role !== currentRole) return false;
    if (currentPeriod === 'all') return true;
    const d = new Date(m.timestamp);
    if (currentPeriod === 'today') {
      return d.toDateString() === now.toDateString();
    } else if (currentPeriod === 'week') {
      const weekAgo = new Date(now); weekAgo.setDate(now.getDate() - 7);
      return d >= weekAgo;
    } else if (currentPeriod === 'month') {
      const monthAgo = new Date(now); monthAgo.setMonth(now.getMonth() - 1);
      return d >= monthAgo;
    }
    return true;
  });

  // ソート
  filtered = filtered.slice().sort((a, b) => {
    return currentSort === 'desc'
      ? b.timestamp.localeCompare(a.timestamp)
      : a.timestamp.localeCompare(b.timestamp);
  });

  document.getElementById('stat-showing').textContent = filtered.length;

  if (filtered.length === 0) {
    const msg = currentQuery
      ? 'No results for "' + escHtml(currentQuery) + '"'
      : 'No messages captured yet.<br>Open claude.ai and start chatting!';
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">◈</div><div class="empty-text">' + msg + '</div></div>';
    return;
  }

  list.innerHTML = filtered.map(m => {
    const timeStr = new Date(m.timestamp).toLocaleString('en', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
    const sessShort = m.session_id ? m.session_id.slice(-6) : '--';
    const preview = escHtml(m.content.slice(0, 120));
    const full = escHtml(m.content);
    const highlighted = currentQuery
      ? preview.replace(new RegExp(escRegex(currentQuery), 'gi'), s => '<span class="highlight">' + s + '</span>')
      : preview;

    return '<div class="msg-item" data-id="' + m.id + '">' +
      '<div class="msg-header">' +
      '<span class="role-badge ' + m.role + '">' + (m.role === 'user' ? 'YOU' : 'AI') + '</span>' +
      '<span class="msg-time">' + timeStr + '</span>' +
      '<span class="msg-session">#' + sessShort + '</span>' +
      '</div>' +
      '<div class="msg-preview">' + highlighted + (m.content.length > 120 ? '...' : '') + '</div>' +
      '<div class="msg-full">' + full + '</div>' +
      '</div>';
  }).join('');

  list.querySelectorAll('.msg-item').forEach(el => {
    el.addEventListener('click', () => el.classList.toggle('expanded'));
  });
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function download(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.getElementById('btn-export-csv').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'EXPORT_CSV' }, (res) => {
    if (res?.ok) {
      const ts = new Date().toISOString().slice(0,10);
      download(res.data, 'orchestra-' + ts + '.csv', 'text/csv');
    }
  });
});

document.getElementById('btn-export-json').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'EXPORT_JSON' }, (res) => {
    if (res?.ok) {
      const ts = new Date().toISOString().slice(0,10);
      download(res.data, 'orchestra-' + ts + '.json', 'application/json');
    }
  });
});

document.getElementById('btn-clear').addEventListener('click', () => {
  if (confirm('Delete ALL saved messages? This cannot be undone.')) {
    chrome.runtime.sendMessage({ type: 'CLEAR_ALL' }, () => {
      allMessages = [];
      renderMessages();
      loadStats();
    });
  }
});

let searchTimer;
document.getElementById('search').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadMessages(e.target.value.trim()), 300);
});

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentRole = tab.dataset.role;
    renderMessages();
  });
});

loadStats();
loadMessages();

// ソート変更
document.getElementById('select-sort').addEventListener('change', (e) => {
  currentSort = e.target.value;
  renderMessages();
});

// 期間変更
document.getElementById('select-period').addEventListener('change', (e) => {
  currentPeriod = e.target.value;
  renderMessages();
});

// 2秒ごとに自動更新
setInterval(() => {
  loadStats();
  loadMessages(currentQuery);
}, 2000);

// Tab navigation
document.querySelectorAll('[data-tab]').forEach(function(el) {
  el.addEventListener('click', function() {
    var tab = this.getAttribute('data-tab');
    var mainPanel = document.getElementById('main-panel');
    var settingsPanel = document.getElementById('settings-panel');
    var navMain = document.getElementById('nav-main');
    var navSettings = document.getElementById('nav-settings');
    if (mainPanel) mainPanel.classList.toggle('hidden', tab !== 'main');
    if (settingsPanel) settingsPanel.classList.toggle('active', tab === 'settings');
    if (navMain) navMain.classList.toggle('active', tab === 'main');
    if (navSettings) navSettings.classList.toggle('active', tab === 'settings');
  });
});

// ── Plan display & license management ────────────────────────────────────────

const PLAN_META = {
  free: {
    label: 'Free',
    labelClass: 'accent',
    desc: 'Save &amp; search conversations · CSV/JSON export · No time limit',
    price: '$0',
    note: 'The Free plan is fully functional — no features are locked, no nudges to upgrade.<br>Orchestra works completely out of the box, forever, at no cost.',
    badgeColor: 'rgba(232,255,71,0.3)',
    badgeBg: 'rgba(232,255,71,0.1)',
    badgeTextColor: 'var(--accent)',
  },
  pro: {
    label: 'Orchestra Pro',
    labelClass: 'accent',
    desc: '5 AI parallel Orchestration · assign roles · one click to launch',
    price: '$5/mo',
    note: 'Pro plan active. Click the 🎼 5AI Orchestra button on any Claude response to launch.',
    badgeColor: 'rgba(232,255,71,0.3)',
    badgeBg: 'rgba(232,255,71,0.1)',
    badgeTextColor: 'var(--accent)',
  },
  one: {
    label: 'Orchestra One',
    labelClass: 'gold',
    desc: 'Everything · No API key · Fully autonomous · 100% local',
    price: '$10/mo',
    note: 'One plan active. Use 🎼 5AI Orchestra (semi-auto) or ⚡ Orchestra One (fully autonomous via Playwright).',
    badgeColor: 'rgba(201,168,76,0.4)',
    badgeBg: 'rgba(201,168,76,0.15)',
    badgeTextColor: '#c9a84c',
  },
};

function renderPlanUI(plan) {
  const meta = PLAN_META[plan] || PLAN_META.free;

  const nameEl = document.getElementById('plan-name-display');
  const badgeEl = document.getElementById('plan-active-badge');
  const descEl = document.getElementById('plan-desc-display');
  const priceEl = document.getElementById('plan-price-display');
  const noteEl = document.getElementById('plan-note-display');

  if (nameEl) {
    nameEl.innerHTML =
      `<span class="plan-row-name ${meta.labelClass}">${meta.label}</span>`;
    if (badgeEl) {
      badgeEl.style.background = meta.badgeBg;
      badgeEl.style.border = `1px solid ${meta.badgeColor}`;
      badgeEl.style.color = meta.badgeTextColor;
      nameEl.appendChild(badgeEl);
    }
  }
  if (descEl) descEl.innerHTML = meta.desc;
  if (priceEl) {
    priceEl.textContent = meta.price;
    priceEl.className = 'plan-row-price' + (plan === 'one' ? ' gold' : '');
  }
  if (noteEl) noteEl.innerHTML = meta.note;

  // Show/hide Remove button based on whether a license is active
  const removeBtn = document.getElementById('license-remove-btn');
  if (removeBtn) removeBtn.style.display = plan !== 'free' ? 'inline-block' : 'none';
}

function loadAndRenderPlan() {
  chrome.runtime.sendMessage({ type: 'GET_PLAN' }, res => {
    if (res?.ok) renderPlanUI(res.plan);
  });
}

// License activation
document.getElementById('license-activate-btn')?.addEventListener('click', () => {
  const input = document.getElementById('license-key-input');
  const statusEl = document.getElementById('license-status-msg');
  const key = input?.value?.trim();

  if (!key) {
    if (statusEl) { statusEl.textContent = 'Please enter a license key.'; statusEl.className = 'license-status err'; }
    return;
  }

  chrome.runtime.sendMessage({ type: 'SET_LICENSE', key }, res => {
    if (res?.ok) {
      renderPlanUI(res.plan);
      if (statusEl) {
        const planName = PLAN_META[res.plan]?.label || res.plan;
        statusEl.textContent = `✓ ${planName} activated successfully!`;
        statusEl.className = 'license-status ok';
      }
      if (input) input.value = '';
    } else {
      if (statusEl) { statusEl.textContent = 'Activation failed. Please try again.'; statusEl.className = 'license-status err'; }
    }
  });
});

// License removal
document.getElementById('license-remove-btn')?.addEventListener('click', () => {
  if (!confirm('Remove license key and revert to Free plan?')) return;
  chrome.runtime.sendMessage({ type: 'REMOVE_LICENSE' }, res => {
    if (res?.ok) {
      renderPlanUI('free');
      const statusEl = document.getElementById('license-status-msg');
      if (statusEl) { statusEl.textContent = 'License removed. Now on Free plan.'; statusEl.className = 'license-status'; }
    }
  });
});

// Load plan on popup open
loadAndRenderPlan();

// ── 合議ステータス カウントアップ + 協議/協業ラベル ──────────────────────────────
window.__orchestraTimers = {};

function updateStatusBar(mode) {
  const modeLabel = mode === 'collaboration' ? '🤝 協業' : '💬 協議';
  const modeColor = mode === 'collaboration' ? '#4fc3f7' : '#e8ff47';
  let bar = document.getElementById('orchestra-status-bar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'orchestra-status-bar';
    bar.style.cssText = [
      'position:fixed', 'bottom:0', 'left:0', 'right:0',
      'background:#111', 'border-top:1px solid #333',
      'padding:6px 10px', 'font-size:10px', 'z-index:9999',
      'display:flex', 'flex-wrap:wrap', 'gap:6px', 'align-items:center'
    ].join(';');
    document.body.appendChild(bar);
  }
  const entries = Object.entries(window.__orchestraTimers).map(([name, data]) => {
    const elapsed = ((Date.now() - data.startTime) / 1000).toFixed(1);
    const statusText = data.done ? '✓' : `⏱ ${elapsed}s`;
    const color = data.done ? '#666' : modeColor;
    return `<span style="color:${color}">● ${name} ${statusText}</span>`;
  }).join('');
  bar.innerHTML = `<span style="color:${modeColor};font-weight:bold;margin-right:4px">${modeLabel}</span>${entries}`;
}

window.startOrchestraStatus = function(aiName, mode) {
  if (window.__orchestraTimers[aiName]?.interval) {
    clearInterval(window.__orchestraTimers[aiName].interval);
  }
  const startTime = Date.now();
  const interval = setInterval(() => updateStatusBar(mode), 100);
  window.__orchestraTimers[aiName] = { startTime, interval, done: false, mode };
  updateStatusBar(mode);
};

window.doneOrchestraStatus = function(aiName) {
  const t = window.__orchestraTimers[aiName];
  if (!t) return;
  clearInterval(t.interval);
  t.done = true;
  updateStatusBar(t.mode || 'deliberation');
  const allDone = Object.values(window.__orchestraTimers).every(x => x.done);
  if (allDone) {
    setTimeout(() => {
      const bar = document.getElementById('orchestra-status-bar');
      if (bar) bar.remove();
      window.__orchestraTimers = {};
    }, 3000);
  }
};

// background.js からの合議イベントを受信
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === 'ORCHESTRA_START') {
    window.__orchestraTimers = {};
    (msg.targets || []).forEach(ai => window.startOrchestraStatus(ai, msg.mode || 'deliberation'));
  }
  if (msg.type === 'ORCHESTRA_DONE') {
    window.doneOrchestraStatus(msg.ai);
  }
});

// ── AI Target Selector ───────────────────────────────────────────────────────
(function initTargetSelector() {
  // Settingsタブが表示されるまで待機してからrow取得
  function bindTargetRows() {
    const rows = document.querySelectorAll('.ai-target-row');
    if (!rows.length) return;

    // 保存済み選択を復元
    chrome.runtime.sendMessage({ type: 'GET_TARGETS' }, (res) => {
      const saved = (res && res.targets) ? res.targets : ['ChatGPT','Gemini','Perplexity','Copilot','Genspark'];
      rows.forEach(row => {
        if (saved.includes(row.dataset.ai)) {
          row.classList.add('checked');
        } else {
          row.classList.remove('checked');
        }
      });
    });

    // クリックでtoggle + 保存
    rows.forEach(row => {
      row.addEventListener('click', () => {
        row.classList.toggle('checked');
        const selected = Array.from(rows)
          .filter(r => r.classList.contains('checked'))
          .map(r => r.dataset.ai);
        if (selected.length === 0) {
          row.classList.add('checked');
          return;
        }
        chrome.runtime.sendMessage({ type: 'SET_TARGETS', targets: selected });
      });
    });
  }

  // nav-tab クリック時にもbind（Settingsタブ切替後）
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      setTimeout(bindTargetRows, 50);
    });
  });

  // 初期実行
  bindTargetRows();
})();


// ── Action Bar: Plan-aware unlock ────────────────────────────────────────────
(function initActionBar() {
  function applyPlanToActionBar(plan) {
    const isPro = plan === 'pro' || plan === 'one';
    const isOne = plan === 'one';

    // Header badge
    const badge = document.getElementById('header-plan-badge');
    if (badge) {
      badge.className = 'plan-badge';
      if (isOne) {
        badge.classList.add('one');
        badge.textContent = 'ONE';
      } else if (isPro) {
        badge.classList.add('pro');
        badge.textContent = 'PRO';
      }
    }

    // AI Share button (Pro+)
    const shareBtn = document.getElementById('action-share');
    if (shareBtn) {
      if (isPro) {
        shareBtn.classList.remove('locked');
        shareBtn.classList.add('unlocked');
        shareBtn.addEventListener('click', () => {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
              chrome.tabs.sendMessage(tabs[0].id, { type: 'ORCHESTRA_SHARE' });
              window.close();
            }
          });
        });
      } else {
        shareBtn.classList.add('locked');
        shareBtn.addEventListener('click', () => {
          // Settingsタブへ誘導
          const navSettings = document.getElementById('nav-settings');
          if (navSettings) navSettings.click();
          const licInput = document.getElementById('license-key-input');
          if (licInput) {
            licInput.focus();
            licInput.style.borderColor = 'var(--accent)';
            setTimeout(() => { licInput.style.borderColor = ''; }, 2000);
          }
        });
      }
    }

    // AI Collab button (One only)
    const collabBtn = document.getElementById('action-collab');
    if (collabBtn) {
      if (isOne) {
        collabBtn.classList.remove('locked');
        collabBtn.classList.add('unlocked');
        collabBtn.addEventListener('click', () => {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
              chrome.tabs.sendMessage(tabs[0].id, { type: 'ORCHESTRA_COLLAB' });
              window.close();
            }
          });
        });
      } else {
        collabBtn.classList.add('locked');
        collabBtn.addEventListener('click', () => {
          const navSettings = document.getElementById('nav-settings');
          if (navSettings) navSettings.click();
          const licInput = document.getElementById('license-key-input');
          if (licInput) {
            licInput.focus();
            licInput.style.borderColor = '#c9a84c';
            setTimeout(() => { licInput.style.borderColor = ''; }, 2000);
          }
        });
      }
    }

    // ツールチップのテキストを言語対応
    if (window.ORCHESTRA_I18N) {
      // 将来のi18n対応用フック
    }
  }

  // プランを取得してアクションバーに反映
  chrome.runtime.sendMessage({ type: 'GET_PLAN' }, (res) => {
    if (res?.ok) {
      applyPlanToActionBar(res.plan);
      renderPlanUI(res.plan);
    }
  });

  // プラン変更を監視（ライセンス有効化直後に反映）
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.license_plan) {
      const newPlan = changes.license_plan.newValue || 'free';
      applyPlanToActionBar(newPlan);
      renderPlanUI(newPlan);
    }
  });
})();

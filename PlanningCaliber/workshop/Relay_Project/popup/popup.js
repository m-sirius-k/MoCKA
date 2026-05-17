/**
 * Relay - popup.js v2.0
 * Free: Home + Logbook
 * Pro:  Vault
 */

let isPro = false;
let currentSessionId = null;

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  await checkLicense();
  loadStats();
  loadTurnLimit();
  bindTabs();
  bindButtons();
}

// ── License ───────────────────────────────────────────────────────────────────
async function checkLicense() {
  return new Promise(resolve => {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      const key = prefs.licenseKey || '';
      chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key }, (res) => {
        isPro = res?.valid === true;
        updateTierUI();
        resolve();
      });
    });
  });
}

function updateTierUI() {
  const badge = document.getElementById('tier-badge');
  if (isPro) {
    badge.textContent = 'PRO ★';
    badge.className = 'tier-badge tier-pro';
  } else {
    badge.textContent = 'FREE';
    badge.className = 'tier-badge tier-free';
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────────
function loadStats() {
  chrome.runtime.sendMessage({ type: 'RELAY_GET_STATS' }, (stats) => {
    if (!stats) return;
    document.getElementById('stat-sessions').textContent = stats.sessions || 0;
    document.getElementById('stat-messages').textContent = stats.messages || 0;
    document.getElementById('stat-todos').textContent    = stats.todos    || 0;
  });
}

// ── Turn limit ────────────────────────────────────────────────────────────────
function loadTurnLimit() {
  chrome.storage.sync.get('mocka_global_prefs', (result) => {
    const prefs = result.mocka_global_prefs || {};
    document.getElementById('turn-limit').value = prefs.turnLimit || 20;
  });
  document.getElementById('turn-limit').addEventListener('change', (e) => {
    const val = parseInt(e.target.value, 10);
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, turnLimit: val } });
    });
  });
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function bindTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const name = tab.dataset.tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-' + name).classList.add('active');

      if (name === 'logbook') loadLogbook();
      if (name === 'vault')   loadVault();
    });
  });
}

// ── Buttons ───────────────────────────────────────────────────────────────────
function bindButtons() {
  // Handoff
  document.getElementById('btn-handoff').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_POPUP_HANDOFF' }, (res) => {
      if (chrome.runtime.lastError || !res?.ok) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_MANUAL_HANDOFF' });
        });
      }
      window.close();
    });
  });

  // Open Logbook tab
  document.getElementById('btn-view-logbook').addEventListener('click', () => {
    document.querySelector('[data-tab="logbook"]').click();
  });

  // Detail back
  document.getElementById('detail-back').addEventListener('click', () => {
    document.getElementById('detail-view').style.display = 'none';
    document.getElementById('list-view').style.display  = 'block';
    currentSessionId = null;
  });

  // Save to Vault
  document.getElementById('btn-save-vault').addEventListener('click', () => {
    if (!currentSessionId) return;
    chrome.runtime.sendMessage({ type: 'RELAY_GET_SESSION', id: currentSessionId }, (res) => {
      const s = res?.session;
      if (!s) return;
      const text = buildVaultText(s);
      chrome.runtime.sendMessage({
        type: 'RELAY_VAULT_ADD',
        payload: { label: s.title, text, sessionId: s.id }
      }, (r) => {
        if (r?.ok) {
          document.getElementById('btn-save-vault').textContent = '✓ Saved to Vault!';
          setTimeout(() => {
            document.getElementById('btn-save-vault').textContent = '★ Save to Vault (Pro)';
          }, 2000);
        } else {
          alert('Vault requires Relay Pro. Activate your license in the Vault tab.');
        }
      });
    });
  });

  // Add current chat to Vault
  document.getElementById('btn-add-vault')?.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_GET_SUMMARY_FOR_VAULT' }, (res) => {
        if (!res?.text) {
          alert('No active Claude chat found.');
          return;
        }
        chrome.runtime.sendMessage({
          type: 'RELAY_VAULT_ADD',
          payload: { label: res.title || 'Current chat', text: res.text }
        }, () => loadVault());
      });
    });
  });

  // License activation
  document.getElementById('btn-verify-license')?.addEventListener('click', activateLicense);
}

function buildVaultText(session) {
  const lb = session.logbook || {};
  const parts = [];
  if (lb.decisions?.length) parts.push('Decisions:\n' + lb.decisions.map(d => `• ${d}`).join('\n'));
  if (lb.todos?.length)     parts.push('Next steps:\n' + lb.todos.map(t => `• ${t}`).join('\n'));
  if (lb.insights?.length)  parts.push('Key insights:\n' + lb.insights.map(i => `• ${i}`).join('\n'));
  return parts.join('\n\n') || session.messages?.slice(-2).map(m => m.text).join('\n') || '';
}

// ── Logbook ───────────────────────────────────────────────────────────────────
function loadLogbook() {
  document.getElementById('detail-view').style.display = 'none';
  document.getElementById('list-view').style.display  = 'block';

  chrome.runtime.sendMessage({ type: 'RELAY_GET_INDEX' }, (res) => {
    const index = res?.index || [];
    const container = document.getElementById('logbook-list');

    if (!index.length) {
      container.innerHTML = '<div class="logbook-empty">No sessions yet.<br>Start a relay to build your Logbook.</div>';
      return;
    }

    container.innerHTML = index.map(s => {
      const lb = s.logbook || {};
      const chips = [
        lb.decisions ? `<span class="logbook-chip decision">✓ ${lb.decisions} decision${lb.decisions !== 1 ? 's' : ''}</span>` : '',
        lb.todos     ? `<span class="logbook-chip todo">→ ${lb.todos} todo${lb.todos !== 1 ? 's' : ''}</span>` : '',
        lb.insights  ? `<span class="logbook-chip insight">★ ${lb.insights} insight${lb.insights !== 1 ? 's' : ''}</span>` : ''
      ].filter(Boolean).join('');
      const date = new Date(s.createdAt).toLocaleDateString('en', { month:'short', day:'numeric' });
      return `
        <div class="logbook-item" data-id="${s.id}">
          <div class="logbook-item-title">${escHtml(s.title)}</div>
          <div class="logbook-item-meta">
            <span class="logbook-chip">${s.turns} turns · ${date}</span>
            ${chips}
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.logbook-item').forEach(el => {
      el.addEventListener('click', () => showDetail(el.dataset.id));
    });
  });
}

function showDetail(id) {
  currentSessionId = id;
  chrome.runtime.sendMessage({ type: 'RELAY_GET_SESSION', id }, (res) => {
    const s = res?.session;
    if (!s) return;
    const lb = s.logbook || {};

    document.getElementById('detail-title').textContent = s.title;

    let html = '';
    if (lb.decisions?.length) {
      html += `<div class="detail-section">
        <h4>✓ Decisions</h4>
        ${lb.decisions.map(d => `<div class="detail-item">${escHtml(d)}</div>`).join('')}
      </div>`;
    }
    if (lb.todos?.length) {
      html += `<div class="detail-section">
        <h4>→ Next steps</h4>
        ${lb.todos.map(t => `<div class="detail-item">${escHtml(t)}</div>`).join('')}
      </div>`;
    }
    if (lb.insights?.length) {
      html += `<div class="detail-section">
        <h4>★ Key insights</h4>
        ${lb.insights.map(i => `<div class="detail-item">${escHtml(i)}</div>`).join('')}
      </div>`;
    }
    if (!html) {
      html = '<div class="logbook-empty" style="text-align:left;color:#4a6080;font-size:12px">No structured data extracted from this session.</div>';
    }

    document.getElementById('detail-content').innerHTML = html;

    // Vault button: Pro only
    const vaultBtn = document.getElementById('btn-save-vault');
    vaultBtn.style.display = isPro ? 'flex' : 'none';

    document.getElementById('detail-view').style.display = 'block';
    document.getElementById('list-view').style.display   = 'none';
  });
}

// ── Vault ─────────────────────────────────────────────────────────────────────
function loadVault() {
  const gate    = document.getElementById('vault-gate');
  const content = document.getElementById('vault-content');

  if (!isPro) {
    gate.style.display    = 'block';
    content.style.display = 'none';
    return;
  }

  gate.style.display    = 'none';
  content.style.display = 'block';

  chrome.runtime.sendMessage({ type: 'RELAY_VAULT_LIST' }, (res) => {
    const vault = res?.vault || [];
    const list = document.getElementById('vault-list');

    if (!vault.length) {
      list.innerHTML = '<div class="logbook-empty">No saved contexts yet.<br>Save a Logbook entry to start.</div>';
      return;
    }

    list.innerHTML = vault.map(v => `
      <div class="vault-item ${v.active ? '' : 'inactive'}" data-id="${v.id}">
        <button class="vault-toggle ${v.active ? '' : 'off'}" data-id="${v.id}" data-active="${v.active}">
          ${v.active ? '✓' : ''}
        </button>
        <span class="vault-label">${escHtml(v.label)}</span>
        <button class="vault-del" data-id="${v.id}">×</button>
      </div>
    `).join('');

    list.querySelectorAll('.vault-toggle').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id     = btn.dataset.id;
        const active = btn.dataset.active === 'true';
        chrome.runtime.sendMessage({ type: 'RELAY_VAULT_TOGGLE', id, active: !active }, () => loadVault());
      });
    });
    list.querySelectorAll('.vault-del').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Remove this Vault entry?')) {
          chrome.runtime.sendMessage({ type: 'RELAY_VAULT_DELETE', id: btn.dataset.id }, () => loadVault());
        }
      });
    });
  });
}

// ── License activation ────────────────────────────────────────────────────────
function activateLicense() {
  const key = document.getElementById('license-input').value.trim();
  const status = document.getElementById('license-status');
  chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key }, (res) => {
    if (res?.valid) {
      chrome.storage.sync.get('mocka_global_prefs', (result) => {
        const prefs = result.mocka_global_prefs || {};
        chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, licenseKey: key, vaultEnabled: true } }, () => {
          status.textContent = '✓ Pro activated!';
          status.className   = 'license-status license-ok';
          isPro = true;
          updateTierUI();
          setTimeout(() => loadVault(), 500);
        });
      });
    } else {
      status.textContent = '✗ Invalid license key';
      status.className   = 'license-status license-err';
    }
  });
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.addEventListener('DOMContentLoaded', init);

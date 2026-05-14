
let allMessages = [];
let currentRole = 'all';
let currentQuery = '';

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
  const filtered = currentRole === 'all'
    ? allMessages
    : allMessages.filter(m => m.role === currentRole);

  document.getElementById('stat-showing').textContent = filtered.length;

  if (filtered.length === 0) {
    const msg = currentQuery
      ? 'No results for "' + escHtml(currentQuery) + '"'
      : 'No messages captured yet.<br>Open claude.ai and start chatting!';
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">\u25c8</div><div class="empty-text">' + msg + '</div></div>';
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

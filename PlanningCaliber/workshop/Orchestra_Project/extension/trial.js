// Orchestra Trial Manager v1.1.0
// 30-day free trial via Google OAuth2 + CF Worker KV
// Google sub → SHA-256 hash → privacy-preserving trial tracking

const TRIAL_WORKER_URL = 'https://orchestra-license.nsjpkimura-mocka.workers.dev';
const TRIAL_STORAGE_KEY = 'orchestra_trial';
const TRIAL_CACHE_TTL_MS = 60 * 60 * 1000; // 1時間キャッシュ

const TrialManager = (() => {

  // ── SHA-256ハッシュ (Google sub → hex) ─────────────────────────────────────
  async function _sha256hex(str) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // ── Google OAuth2 でid_token取得 → sub抽出 → SHA-256ハッシュ化 ────────────
  async function getGoogleIdHash() {
    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive: true }, async (token) => {
        if (chrome.runtime.lastError || !token) {
          reject(new Error(chrome.runtime.lastError?.message || 'OAuth cancelled'));
          return;
        }
        try {
          // Google UserInfo API で sub を取得
          const resp = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (!resp.ok) throw new Error(`UserInfo API error: ${resp.status}`);
          const info = await resp.json();
          const sub = info.sub;
          if (!sub) throw new Error('No sub in UserInfo response');
          const hash = await _sha256hex(sub);
          resolve(hash);
        } catch (err) {
          // トークンが無効な場合はキャッシュを削除して再試行可能にする
          chrome.identity.removeCachedAuthToken({ token }, () => {});
          reject(err);
        }
      });
    });
  }

  // ── トライアル開始 ─────────────────────────────────────────────────────────
  async function startTrial() {
    let idHash;
    try {
      idHash = await getGoogleIdHash();
    } catch (err) {
      return { ok: false, error: 'oauth_failed', detail: err.message };
    }

    try {
      const resp = await fetch(`${TRIAL_WORKER_URL}/api/trial/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_hash: idHash }),
      });
      const data = await resp.json();

      if (resp.status === 409) {
        // already_used → ステータス取得して返す
        const status = await _fetchStatus(idHash);
        return { ok: false, error: 'already_used', ...status };
      }
      if (!resp.ok || !data.ok) {
        return { ok: false, error: data.error || 'server_error' };
      }

      // ローカルにキャッシュ
      await _saveLocal({ id_hash: idHash, ...data, cached_at: Date.now() });
      return { ok: true, ...data };
    } catch (err) {
      return { ok: false, error: 'network_error', detail: err.message };
    }
  }

  // ── トライアル状態取得 (KV問い合わせ) ─────────────────────────────────────
  async function _fetchStatus(idHash) {
    const resp = await fetch(
      `${TRIAL_WORKER_URL}/api/trial/status?id_hash=${encodeURIComponent(idHash)}`
    );
    return await resp.json();
  }

  // ── ローカルキャッシュ保存 ─────────────────────────────────────────────────
  function _saveLocal(data) {
    return new Promise(resolve => {
      chrome.storage.local.set({ [TRIAL_STORAGE_KEY]: data }, resolve);
    });
  }

  // ── ローカルキャッシュ読み込み ─────────────────────────────────────────────
  function _loadLocal() {
    return new Promise(resolve => {
      chrome.storage.local.get([TRIAL_STORAGE_KEY], data => {
        resolve(data[TRIAL_STORAGE_KEY] || null);
      });
    });
  }

  // ── トライアル状態チェック (キャッシュ優先 → KV) ───────────────────────────
  // 返り値: { status: 'none'|'active'|'expired', days_left, started_at, expires_at }
  async function getStatus() {
    const local = await _loadLocal();

    // キャッシュが新鮮な場合はローカルで判定
    if (local && local.expires_at) {
      const now = new Date();
      const expires = new Date(local.expires_at);
      const cacheAge = Date.now() - (local.cached_at || 0);

      // キャッシュが1時間以内 かつ 有効期限内
      if (cacheAge < TRIAL_CACHE_TTL_MS) {
        if (expires > now) {
          const daysLeft = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));
          return { status: 'active', days_left: daysLeft, started_at: local.started_at, expires_at: local.expires_at };
        } else {
          return { status: 'expired', days_left: 0, started_at: local.started_at, expires_at: local.expires_at };
        }
      }

      // キャッシュ期限切れ → KVに問い合わせ
      if (local.id_hash) {
        try {
          const remote = await _fetchStatus(local.id_hash);
          if (remote.ok) {
            // キャッシュ更新
            await _saveLocal({ ...local, ...remote, cached_at: Date.now() });
            return { status: remote.status || 'none', days_left: remote.days_left || 0, started_at: remote.started_at, expires_at: remote.expires_at };
          }
        } catch (_) { /* ネットワークエラーはキャッシュで代替 */ }
        // フォールバック: キャッシュで判定
        if (expires > now) {
          const daysLeft = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));
          return { status: 'active', days_left: daysLeft, started_at: local.started_at, expires_at: local.expires_at };
        }
        return { status: 'expired', days_left: 0, started_at: local.started_at, expires_at: local.expires_at };
      }
    }

    return { status: 'none', days_left: 0 };
  }

  // ── Proライセンス確認 (background.jsのGET_PLANと連携) ─────────────────────
  async function checkProLicense() {
    return new Promise(resolve => {
      chrome.runtime.sendMessage({ type: 'GET_PLAN' }, res => {
        if (chrome.runtime.lastError || !res) { resolve({ plan: 'free' }); return; }
        resolve({ plan: res.plan || 'free', expiry: res.expiry });
      });
    });
  }

  // ── 有効なアクセス権限を返す (trial > pro > free) ──────────────────────────
  // 返り値: { access: 'pro'|'trial'|'free', days_left?, source }
  async function check() {
    const licenseInfo = await checkProLicense();
    if (licenseInfo.plan === 'pro' || licenseInfo.plan === 'one') {
      return { access: licenseInfo.plan, source: 'license' };
    }
    const trial = await getStatus();
    if (trial.status === 'active') {
      return { access: 'trial', source: 'trial', days_left: trial.days_left, expires_at: trial.expires_at };
    }
    return { access: 'free', source: 'free', trial_status: trial.status };
  }

  return { startTrial, getStatus, check, checkProLicense, getGoogleIdHash };
})();

// Service Worker / popup 両方から使えるよう window への公開はしない
// background.js から require/import するか、popup から直接 <script> タグで読み込む
if (typeof window !== 'undefined') {
  window.TrialManager = TrialManager;
}

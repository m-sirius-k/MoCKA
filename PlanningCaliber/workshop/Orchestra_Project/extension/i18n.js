/**
 * Orchestra i18n.js v2.0
 * data-i18n属性を持つ要素を確実に翻訳する方式。
 * popup.htmlのdata-i18n属性が翻訳のアンカーになる。
 */

(function() {
  'use strict';

  const SUPPORTED = ['en', 'ja', 'zh', 'ko', 'es'];
  const LANG_LABELS = { en: 'EN', ja: '日', zh: '中', ko: '한', es: 'ES' };

  // ── 言語検出 ──────────────────────────────────────────────────
  function detectLang() {
    const saved = localStorage.getItem('orchestra_lang');
    if (saved && SUPPORTED.includes(saved)) return saved;
    const nav = (navigator.language || 'en').toLowerCase().slice(0, 2);
    return SUPPORTED.includes(nav) ? nav : 'en';
  }

  // ── messages.json 読み込み ─────────────────────────────────────
  async function loadMessages(lang) {
    try {
      const url = chrome.runtime.getURL('_locales/' + lang + '/messages.json');
      const res = await fetch(url);
      if (!res.ok) throw new Error('fetch failed');
      return await res.json();
    } catch (e) {
      if (lang !== 'en') return loadMessages('en');
      return {};
    }
  }

  // ── data-i18n属性で確実に適用 ─────────────────────────────────
  function applyDataI18n(msgs) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const val = msgs[key] && msgs[key].message;
      if (val) el.textContent = val;
    });
  }

  // ── 固定セレクターで適用（data-i18nなし要素） ─────────────────
  function applyFixed(msgs) {
    function t(key) {
      return msgs[key] && msgs[key].message ? msgs[key].message : null;
    }

    // Nav tabs
    const navMain = document.getElementById('nav-main');
    if (navMain && t('navLibrary')) navMain.textContent = t('navLibrary');
    const navSettings = document.getElementById('nav-settings');
    if (navSettings && t('navSettings')) navSettings.textContent = t('navSettings');

    // Stats labels
    const statLabels = document.querySelectorAll('.stat-label');
    const statKeys = ['statMessages', 'statSessions', 'statShowing'];
    statLabels.forEach((el, i) => { if (t(statKeys[i])) el.textContent = t(statKeys[i]); });

    // Search placeholder
    const search = document.getElementById('search');
    if (search && t('searchPlaceholder')) search.placeholder = t('searchPlaceholder');

    // Filter tabs (All / You / AI)
    const filterTabs = document.querySelectorAll('.filter-tabs .tab');
    const tabKeys = ['tabAll', 'tabYou', 'tabAi'];
    filterTabs.forEach((el, i) => { if (t(tabKeys[i])) el.textContent = t(tabKeys[i]); });

    // Sort select options
    const sortEl = document.getElementById('select-sort');
    if (sortEl) {
      const opts = sortEl.querySelectorAll('option');
      if (opts[0] && t('sortNewest')) opts[0].textContent = t('sortNewest');
      if (opts[1] && t('sortOldest')) opts[1].textContent = t('sortOldest');
    }

    // Period select options
    const periodEl = document.getElementById('select-period');
    if (periodEl) {
      const opts = periodEl.querySelectorAll('option');
      const pKeys = ['periodAll', 'periodToday', 'periodWeek', 'periodMonth'];
      opts.forEach((opt, i) => { if (t(pKeys[i])) opt.textContent = t(pKeys[i]); });
    }

    // Status bar
    const statusText = document.getElementById('status-text');
    if (statusText && t('statusBar')) statusText.textContent = t('statusBar');

    // Current Plan section title
    document.querySelectorAll('.settings-section-title').forEach(el => {
      if (el.textContent.trim() === 'Current Plan' && t('currentPlanTitle')) {
        el.textContent = t('currentPlanTitle');
      }
      if (el.textContent.trim() === 'License Key' && t('licenseTitle')) {
        el.textContent = t('licenseTitle');
      }
      if (el.textContent.includes('Upgrade') && t('upgradeTitle')) {
        el.textContent = t('upgradeTitle');
      }
      if (el.textContent.trim() === 'About' && t('aboutTitle')) {
        el.textContent = t('aboutTitle');
      }
    });

    // License input placeholder
    const licInput = document.getElementById('license-key-input');
    if (licInput && t('licensePlaceholder')) licInput.placeholder = t('licensePlaceholder');

    // License buttons
    const licActivate = document.getElementById('license-activate-btn');
    if (licActivate && t('licenseActivate')) licActivate.textContent = t('licenseActivate');
    const licRemove = document.getElementById('license-remove-btn');
    if (licRemove && t('licenseRemove')) licRemove.textContent = t('licenseRemove');

    // License status default message
    const licStatus = document.getElementById('license-status-msg');
    if (licStatus && !licStatus.classList.contains('ok') && !licStatus.classList.contains('err')) {
      if (t('licenseDefault')) licStatus.textContent = t('licenseDefault');
    }

    // Upgrade section buttons
    const upgradeLinks = document.querySelectorAll('.settings-section .plan-btn');
    const upgradeBtnKeys = ['getBtnPro', 'getBtnUpgrade', 'getBtnOne', 'getBtnLaunch'];
    upgradeLinks.forEach((el, i) => {
      if (upgradeBtnKeys[i] && t(upgradeBtnKeys[i])) el.textContent = t(upgradeBtnKeys[i]);
    });

    // About website button
    const websiteBtn = document.querySelector('a[href*="sirius-lab"]');
    if (websiteBtn && t('websiteBtn')) websiteBtn.textContent = t('websiteBtn');

    // About description
    const aboutDesc = document.querySelector('.settings-section .plan-row-desc');
    if (aboutDesc && t('aboutDesc')) {
      // About sectionのdescのみ（最後のsettings-sectionを探す）
      const aboutSection = Array.from(document.querySelectorAll('.settings-section')).find(s => {
        const title = s.querySelector('.settings-section-title');
        return title && (title.textContent.includes('About') || title.textContent.includes('情報') ||
               title.textContent.includes('关于') || title.textContent.includes('정보') ||
               title.textContent.includes('Acerca'));
      });
      if (aboutSection) {
        const desc = aboutSection.querySelector('.plan-row-desc');
        if (desc && t('aboutDesc')) desc.textContent = t('aboutDesc');
        const wb = aboutSection.querySelector('.plan-btn');
        if (wb && t('websiteBtn')) wb.textContent = t('websiteBtn');
      }
    }

    // window.ORCHESTRA_I18N に動的テキストをセット（popup.jsが参照）
    window.ORCHESTRA_I18N = {
      confirmClear:         t('confirmClear'),
      emptyDefault:         t('emptyDefault'),
      licenseEmpty:         t('licenseEmpty'),
      licenseError:         t('licenseError'),
      licenseRemoveConfirm: t('licenseRemoveConfirm'),
      licenseRemoved:       t('licenseRemoved'),
      planFreeLabel:        t('planFreeLabel'),
      planFreeDesc:         t('planFreeDesc'),
      planFreeNote:         t('planFreeNote'),
      planProLabel:         t('planProLabel'),
      planProDesc:          t('planProDesc'),
      planProNote:          t('planProNote'),
      planOneLabel:         t('planOneLabel'),
      planOneDesc:          t('planOneDesc'),
      planOneNote:          t('planOneNote'),
    };
  }

  // ── 言語切り替えボタン ────────────────────────────────────────
  function addLangSwitcher(currentLang) {
    const header = document.querySelector('.header');
    if (!header || document.getElementById('lang-switcher')) return;

    const switcher = document.createElement('div');
    switcher.id = 'lang-switcher';
    switcher.style.cssText = 'display:flex;gap:3px;align-items:center;flex-shrink:0;margin-left:auto';

    SUPPORTED.forEach(lang => {
      const btn = document.createElement('button');
      btn.textContent = LANG_LABELS[lang];
      const isActive = lang === currentLang;
      btn.style.cssText = [
        'background:transparent',
        'border:1px solid ' + (isActive ? 'var(--accent)' : 'var(--border)'),
        'border-radius:3px',
        'color:' + (isActive ? 'var(--accent)' : 'var(--muted)'),
        'font-family:Syne,sans-serif',
        'font-size:9px',
        'font-weight:600',
        'padding:2px 5px',
        'cursor:pointer',
        'transition:all 0.12s',
        'letter-spacing:0.3px',
        'line-height:1'
      ].join(';');
      btn.addEventListener('click', () => {
        localStorage.setItem('orchestra_lang', lang);
        location.reload();
      });
      switcher.appendChild(btn);
    });

    // header-titleの後に挿入（右端）
    const title = header.querySelector('.header-title');
    if (title) {
      title.after(switcher);
    } else {
      header.appendChild(switcher);
    }
  }

  // ── メイン ────────────────────────────────────────────────────
  async function init() {
    const lang = detectLang();
    const msgs = await loadMessages(lang);
    applyDataI18n(msgs);
    applyFixed(msgs);
    addLangSwitcher(lang);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

// content.js
'use strict';

const MEMORY_PATTERNS = {
  WINDOWS_PATH: /[A-Za-z]:\\(?:[\w\-\. ]+\\)*[\w\-\. ]+\.\w+/g,
  UNIX_PATH: /\/(?:[\w\-\.]+\/)+[\w\-\.]+\.\w+/g,
  CREATED_JA: /[「『]?([\w\-\.\/\\:]+\.\w+)[」』]?(?:を作成|に保存|を生成|を配置)/g,
  CREATED_EN: /(?:created|saved|written|placed)\s+(?:to\s+)?[「']?([\w\-\.\/\\:]+\.\w+)[」']?/gi,
  ERROR_KEYWORDS: ['cp932', 'encoding error', 'BOM', 'UnicodeDecodeError', 'SyntaxError'],
  DECISION_JA: /(?:採用|決定|確定|〜にした|〜とする|方針:|結論:)(.{5,80})/g,
  DECISION_EN: /(?:decided|confirmed|will use|going with|final decision:)(.{5,80})/gi
};

let observerActive = false;
let lastCapturedText = '';

function initMemoryCapture() {
  if (observerActive) return;

  const targetNode = document.body;
  const config = { childList: true, subtree: true, characterData: true };

  const observer = new MutationObserver(() => {
    clearTimeout(window.__memoryDebounce);
    window.__memoryDebounce = setTimeout(captureFromPage, 1200);
  });

  observer.observe(targetNode, config);
  observerActive = true;
}

function captureFromPage() {
  const SELECTORS = [
    '[data-testid="assistant-message"] .prose',
    '.markdown.prose',
    '[data-message-author-role="assistant"]',
    '.model-response-text'
  ];

  let responseText = '';
  for (const sel of SELECTORS) {
    const els = document.querySelectorAll(sel);
    if (els.length > 0) {
      responseText = els[els.length - 1].innerText || '';
      break;
    }
  }

  if (!responseText || responseText === lastCapturedText) return;
  lastCapturedText = responseText;

  const paths = extractPaths(responseText);
  const errors = detectErrors(responseText);
  const decisions = extractDecisions(responseText);

  if (paths.length > 0 || errors.length > 0 || decisions.length > 0) {
    chrome.runtime.sendMessage({
      type: 'MEMORY_CAPTURE',
      payload: { paths, errors, decisions, timestamp: new Date().toISOString() }
    });
  }
}

function extractPaths(text) {
  const paths = new Set();

  const winMatches = text.matchAll(MEMORY_PATTERNS.WINDOWS_PATH);
  for (const m of winMatches) paths.add({ path: m[0], type: 'windows' });

  const unixMatches = text.matchAll(MEMORY_PATTERNS.UNIX_PATH);
  for (const m of unixMatches) {
    if (m[0].startsWith('/mnt/') || m[0].startsWith('/home/')) {
      paths.add({ path: m[0], type: 'unix' });
    }
  }

  return [...paths];
}

function detectErrors(text) {
  const detected = [];
  const lowerText = text.toLowerCase();

  for (const keyword of MEMORY_PATTERNS.ERROR_KEYWORDS) {
    if (lowerText.includes(keyword.toLowerCase())) {
      detected.push({ keyword, context: extractContext(text, keyword, 100) });
    }
  }
  return detected;
}

function extractDecisions(text) {
  const decisions = [];

  const jaMatches = text.matchAll(MEMORY_PATTERNS.DECISION_JA);
  for (const m of jaMatches) {
    if (m[1] && m[1].trim().length > 3) {
      decisions.push({ content: m[1].trim(), lang: 'ja' });
    }
  }

  const enMatches = text.matchAll(MEMORY_PATTERNS.DECISION_EN);
  for (const m of enMatches) {
    if (m[1] && m[1].trim().length > 3) {
      decisions.push({ content: m[1].trim(), lang: 'en' });
    }
  }

  return decisions;
}

function extractContext(text, keyword, radius) {
  const idx = text.toLowerCase().indexOf(keyword.toLowerCase());
  if (idx === -1) return '';
  return text.substring(Math.max(0, idx - radius), Math.min(text.length, idx + radius));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMemoryCapture);
} else {
  initMemoryCapture();
}

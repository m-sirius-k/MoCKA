// debug-panel.js — PHI OS デバッグパネル（content.js内で使用）
'use strict';

import { HealthCheck } from './health-check.js';
import { getErrorLog, clearErrorLog } from './error-reporter.js';

const PANEL_ID = 'phi-os-debug-panel';

export class DebugPanel {
  constructor() {
    this._panel = null;
  }

  toggle() {
    if (this._panel) {
      this._panel.remove();
      this._panel = null;
    } else {
      this._render();
    }
  }

  async _render() {
    const hc      = new HealthCheck();
    const results = await hc.run();
    const errors  = await getErrorLog();

    const el  = document.createElement('div');
    el.id     = PANEL_ID;
    el.style.cssText = [
      'position:fixed', 'bottom:100px', 'right:24px', 'width:360px',
      'max-height:400px', 'overflow-y:auto', 'z-index:9999999',
      'background:#0a0e1a', 'border:1px solid #1e3a5f', 'border-radius:10px',
      'padding:12px', 'font-family:monospace', 'font-size:11px', 'color:#e2e8f0',
      'box-shadow:0 8px 32px rgba(0,0,0,0.8)',
    ].join(';');

    const healthHtml = results.map(r =>
      `<div style="color:${r.status === 'OK' ? '#22c55e' : r.status === 'WARNING' ? '#f59e0b' : '#ef4444'}">[${r.status}] ${r.name}: ${r.detail || ''}</div>`
    ).join('');

    const errHtml = errors.slice(0, 5).map(e =>
      `<div style="color:#ef4444;margin-top:4px">[${e.type}] ${e.message}</div>`
    ).join('') || '<div style="color:#475569">No errors</div>';

    el.innerHTML = `
      <div style="font-weight:700;color:#38bdf8;margin-bottom:8px">Φ PHI OS Debug Panel</div>
      <div style="margin-bottom:8px"><strong>Health</strong>${healthHtml}</div>
      <div style="margin-bottom:8px"><strong>Errors (last 5)</strong>${errHtml}</div>
      <button id="phi-debug-clear" style="background:#111827;color:#94a3b8;border:1px solid #1e3a5f;border-radius:4px;padding:3px 8px;cursor:pointer;font-size:10px">Clear Errors</button>
      <button id="phi-debug-close" style="background:#111827;color:#94a3b8;border:1px solid #1e3a5f;border-radius:4px;padding:3px 8px;cursor:pointer;font-size:10px;margin-left:6px">Close</button>
    `;

    document.body.appendChild(el);
    this._panel = el;

    el.querySelector('#phi-debug-clear')?.addEventListener('click', async () => {
      await clearErrorLog();
      this._render();
    });
    el.querySelector('#phi-debug-close')?.addEventListener('click', () => {
      el.remove();
      this._panel = null;
    });
  }
}

// health-check.js — PHI OS 自己診断
'use strict';

import { detectMode, getBytesInUse } from '../core/state-store.js';
import { SCHEMA_VERSION }            from '../core/schema-registry.js';

const STORAGE_LIMIT = 5 * 1024 * 1024; // 5MB

export class HealthCheck {
  /**
   * 全チェックを実行して結果配列を返す
   * @returns {Promise<Array<{name:string, status:string, detail:string|null}>>}
   */
  async run() {
    const results = await Promise.allSettled([
      this.checkStorage(),
      this.checkSchemaVersion(),
      this.checkMoCKAConnection(),
      this.checkCommitIndex(),
    ]);

    return results.map((r, i) => ({
      name:   ['storage', 'schema', 'mocka', 'commit_index'][i],
      status: r.status === 'fulfilled' ? (r.value.ok ? 'OK' : 'WARNING') : 'ERROR',
      detail: r.status === 'fulfilled' ? r.value.detail : (r.reason?.message || 'unknown error'),
    }));
  }

  async checkStorage() {
    const bytes = await getBytesInUse();
    const pct   = bytes / STORAGE_LIMIT * 100;
    if (pct > 90) return { ok: false, detail: `NEAR LIMIT: ${(bytes / 1024).toFixed(0)} KB / 5 MB` };
    return { ok: true, detail: `${(bytes / 1024).toFixed(0)} KB used (${pct.toFixed(1)}%)` };
  }

  async checkSchemaVersion() {
    const stored = await chrome.storage.local.get('phi_schema_version');
    const ver    = stored['phi_schema_version'];
    if (!ver) return { ok: false, detail: 'schema version not set' };
    if (ver !== SCHEMA_VERSION) return { ok: false, detail: `version mismatch: ${ver} != ${SCHEMA_VERSION}` };
    return { ok: true, detail: `v${ver}` };
  }

  async checkMoCKAConnection() {
    const mode = await detectMode();
    return { ok: true, detail: mode };
  }

  async checkCommitIndex() {
    const stored = await chrome.storage.local.get('phi_commit_index');
    const index  = stored['phi_commit_index'] || [];
    return { ok: true, detail: `${index.length} commits stored` };
  }
}

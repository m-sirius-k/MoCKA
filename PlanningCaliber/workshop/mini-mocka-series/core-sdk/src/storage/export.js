/**
 * mini MoCKA Core SDK — storage/export.js
 * CSV / JSON export. Migrated and cleaned from Orchestra.
 */

export const MockaExport = {
  /**
   * Convert sessions array to CSV Blob.
   */
  toCSV(sessions) {
    const rows = [['id', 'product', 'title', 'url', 'turns', 'createdAt', 'role', 'text']];
    for (const s of sessions) {
      if (!s.messages || s.messages.length === 0) {
        rows.push([s.id, s.product, s.title, s.url, s.turns, s.createdAt, '', '']);
        continue;
      }
      for (const m of s.messages) {
        rows.push([
          s.id, s.product,
          this._esc(s.title), this._esc(s.url),
          s.turns, s.createdAt,
          m.role || '', this._esc(m.text || '')
        ]);
      }
    }
    const csv = rows.map(r => r.join(',')).join('\n');
    return new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
  },

  /**
   * Convert sessions array to JSON Blob.
   */
  toJSON(sessions) {
    const json = JSON.stringify(sessions, null, 2);
    return new Blob([json], { type: 'application/json' });
  },

  /**
   * Trigger browser download.
   */
  download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },

  _esc(str) {
    if (!str) return '';
    const s = String(str).replace(/"/g, '""');
    return s.includes(',') || s.includes('\n') || s.includes('"') ? `"${s}"` : s;
  }
};

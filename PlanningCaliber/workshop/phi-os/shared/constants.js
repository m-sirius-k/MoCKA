/**
 * PHI OS — constants.js
 * Shared constants for all mini MoCKA products (Orchestra, Relay, ...)
 */

const PHI_OS = Object.freeze({
  VERSION: '1.0.0',
  STORAGE_PREFIX: 'phi_',

  // Session
  MAX_SESSIONS: 50,
  SESSION_NS: 'phi_session_',
  SESSION_INDEX_KEY: 'phi_sessions_index',

  // TODO / Logbook
  TODO_KEY: 'phi_todos',
  LOG_KEY: 'phi_log',
  MAX_TODOS: 200,
  MAX_LOG: 500,

  // Vault
  VAULT_KEY: 'phi_vault',
  MAX_VAULT: 20,

  // Settings
  PREFS_KEY: 'phi_prefs',

  // Products
  PRODUCTS: ['orchestra', 'relay'],
});

if (typeof module !== 'undefined') module.exports = { PHI_OS };
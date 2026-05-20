/**
 * PHI OS — schema.js
 * Data schema definitions shared across all products.
 */

function createSession({ product, title, url, messages, turns, sessionId }) {
  const now = new Date().toISOString();
  return {
    phi_os_version: '1.0.0',
    id: crypto.randomUUID(),
    product: product || 'unknown',
    session_id: sessionId || crypto.randomUUID(),
    title: title || 'Untitled',
    url: url || '',
    turns: turns || 0,
    messages: (messages || []).map(m => ({
      role: m.role,
      content: (m.content || '').slice(0, 2000),
      ts: m.ts || Date.now(),
    })),
    created_at: now,
    updated_at: now,
  };
}

function createTodo({ content, sessionId, priority }) {
  const now = new Date().toISOString();
  return {
    id: 'TODO_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
    content: content || '',
    status: 'open',        // open | done
    priority: priority || 'medium',  // low | medium | high
    session_id: sessionId || null,
    created_at: now,
    updated_at: now,
  };
}

function createLogEntry(todo) {
  return {
    ...todo,
    status: 'done',
    completed_at: new Date().toISOString(),
  };
}

if (typeof module !== 'undefined') module.exports = { createSession, createTodo, createLogEntry };
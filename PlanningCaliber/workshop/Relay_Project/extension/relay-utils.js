'use strict';
// Relay shared utilities — loaded before content.js (content script) and via importScripts (background)

/**
 * Returns false if the text should be rejected as a TODO candidate.
 * Rules apply in extractTodos (content.js) and getHandoffPacket (background.js).
 */
function isValidTodoContent(text) {
  const t = (typeof text === 'string' ? text : '').trim();
  if (!t) return false;
  // Numbered list — period form: "1. some text"
  if (/^\d+\.\s+.{5,}/.test(t)) return false;
  // Numbered list — parenthesis form: "1) some text"
  if (/^\d+\)\s*.{5,}/.test(t)) return false;
  // [LB_xxx] self-block references
  if (/\[LB_[A-Z0-9_]+\]/.test(t)) return false;
  return true;
}

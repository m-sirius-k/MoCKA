/**
 * mini MoCKA Core SDK — summary/generator.js
 * Pure JS conversation summariser. No API key required.
 * Used by: Relay (handoff), Vault (save), Logbook (extract)
 */

const DECISION_PATTERNS = [
  /\b(decided|we('ll| will)|let's|confirmed|agreed|going with|will use|chosen)\b/i,
  /\b(the plan is|our approach|we settled on|final answer)\b/i,
];

const TODO_PATTERNS = [
  /\b(need to|should|next step|to-?do|action item|follow[- ]up|will implement)\b/i,
  /\b(remember to|don't forget|make sure|check|investigate|look into)\b/i,
];

const TOPIC_STOP_WORDS = new Set([
  'the','a','an','is','it','in','on','of','to','and','or','but','for',
  'with','this','that','i','you','we','they','he','she','was','are','be',
  'have','has','had','do','did','not','so','if','at','by','from'
]);

function extractKeywords(messages, max = 8) {
  const freq = {};
  for (const m of messages) {
    const words = (m.text || '').toLowerCase().split(/\W+/);
    for (const w of words) {
      if (w.length > 3 && !TOPIC_STOP_WORDS.has(w)) {
        freq[w] = (freq[w] || 0) + 1;
      }
    }
  }
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, max)
    .map(([w]) => w);
}

function extractDecisions(messages) {
  const decisions = [];
  for (const m of messages) {
    if (!m.text) continue;
    const sentences = m.text.split(/[.!?]/);
    for (const s of sentences) {
      if (DECISION_PATTERNS.some(p => p.test(s))) {
        const trimmed = s.trim();
        if (trimmed.length > 10 && trimmed.length < 200) {
          decisions.push(trimmed);
        }
      }
    }
  }
  return [...new Set(decisions)].slice(0, 5);
}

function extractTodos(messages) {
  const todos = [];
  for (const m of messages) {
    if (!m.text) continue;
    const sentences = m.text.split(/[.!?]/);
    for (const s of sentences) {
      if (TODO_PATTERNS.some(p => p.test(s))) {
        const trimmed = s.trim();
        if (trimmed.length > 10 && trimmed.length < 200) {
          todos.push(trimmed);
        }
      }
    }
  }
  return [...new Set(todos)].slice(0, 5);
}

export const MockaSummary = {
  /**
   * Generate a structured summary from conversation messages.
   * @param {Array<{role,text}>} messages
   * @param {{ maxLength?, style? }} options
   * @returns {{ summary, decisions, todos, keywords, turnCount }}
   */
  generate(messages, options = {}) {
    const { maxLength = 500, style = 'relay' } = options;

    if (!messages || messages.length === 0) {
      return { summary: '', decisions: [], todos: [], keywords: [], turnCount: 0 };
    }

    const userMessages = messages.filter(m => m.role === 'user');
    const keywords = extractKeywords(messages);
    const decisions = extractDecisions(messages);
    const todos = extractTodos(userMessages);

    const topicLine = keywords.length
      ? `Topic: ${keywords.slice(0, 4).join(', ')}`
      : '';

    const decisionLines = decisions.length
      ? `Key decisions:\n${decisions.map(d => `• ${d}`).join('\n')}`
      : '';

    const todoLines = todos.length
      ? `Next steps:\n${todos.map(t => `• ${t}`).join('\n')}`
      : '';

    const lastUser = userMessages[userMessages.length - 1]?.text?.slice(0, 200) || '';
    const lastLine = lastUser ? `Last message: "${lastUser}"` : '';

    const parts = [
      `[Conversation context — ${messages.length} turns]`,
      topicLine,
      decisionLines,
      todoLines,
      lastLine
    ].filter(Boolean);

    let summary = parts.join('\n\n');
    if (summary.length > maxLength) {
      summary = summary.slice(0, maxLength) + '…';
    }

    return {
      summary,
      decisions,
      todos,
      keywords,
      turnCount: messages.length
    };
  },

  /**
   * Format for Relay handoff injection.
   */
  formatHandoff(summaryResult) {
    const { summary, turnCount } = summaryResult;
    return `[Continuing from previous conversation (${turnCount} turns)]\n\n${summary}\n\n---\nPlease continue from where we left off.`;
  },

  /**
   * Format for Logbook extraction.
   */
  formatLogbook(summaryResult) {
    const { decisions, todos, keywords } = summaryResult;
    const lines = [`# Session Notes`, `**Keywords:** ${keywords.join(', ')}`];
    if (decisions.length) {
      lines.push(`\n## Decisions`);
      decisions.forEach(d => lines.push(`- ${d}`));
    }
    if (todos.length) {
      lines.push(`\n## Action Items`);
      todos.forEach(t => lines.push(`- [ ] ${t}`));
    }
    return lines.join('\n');
  }
};

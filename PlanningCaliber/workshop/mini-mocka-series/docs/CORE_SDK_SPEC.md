# mini MoCKA Series — Core SDK Specification v1.0

**Path:** `planningcaliber/workshop/mini-mocka-series/core-sdk/`  
**Status:** Phase 0 — Design & Implementation  
**Language:** English (Japanese localisation planned post-launch)  
**Classification:** PRIVATE — not exposed to end users  

---

## 1. Purpose

The Core SDK is the shared private foundation for all 5 products in the mini MoCKA Series.  
It is **not** connected to MoCKA's core systems (no ledger, no essence, no MCP).  
Each product imports only the modules it needs.

---

## 2. Module Map

```
core-sdk/
├── src/
│   ├── dom/
│   │   ├── watcher.js          # claude.ai DOM observation (turn count, new messages)
│   │   └── extractor.js        # Extract conversation text from DOM
│   ├── storage/
│   │   ├── store.js            # chrome.storage.local abstraction (key-value)
│   │   ├── session.js          # Session record management
│   │   └── export.js           # CSV / JSON export (from Orchestra)
│   ├── summary/
│   │   ├── generator.js        # Conversation → summary text
│   │   └── injector.js         # Inject summary into new claude.ai chat
│   ├── settings/
│   │   └── prefs.js            # Shared user preferences across products
│   ├── bridge/
│   │   └── inter-product.js    # Inter-product data sharing interface
│   └── index.js                # Public API surface
├── tests/
│   └── *.test.js
└── package.json
```

---

## 3. Module Specifications

### 3-1. dom/watcher.js

Observes claude.ai conversation DOM. Used by: **Relay, Prism, Logbook**

```javascript
// Public API
MockaWatcher.init(options)
// options: { onTurn: fn, onMessage: fn, onNewChat: fn }

MockaWatcher.getTurnCount()   // → number
MockaWatcher.getMessages()    // → Array<{ role, text, timestamp }>
MockaWatcher.destroy()
```

**Implementation notes:**
- Use `MutationObserver` on `[data-testid="conversation-turn"]`
- Selector may change — wrap in try/catch with fallback
- DO NOT copy from Orchestra's content.js directly — rewrite clean
- Emit `mocka:turn` custom events on window

---

### 3-2. dom/extractor.js

Extracts structured conversation content. Used by: **Relay, Logbook, Vault**

```javascript
MockaExtractor.getConversation()
// → { turns: [{role, text, ts}], url, sessionId, title }

MockaExtractor.getLastN(n)
// → last N turns

MockaExtractor.getUserMessages()
// → user-only messages (for Vault save proposals)
```

---

### 3-3. storage/store.js

Abstraction over `chrome.storage.local`. Used by: **all products**

**Orchestra reuse decision:**  
Orchestra's storage is tightly coupled to its own data schema.  
→ Extract the **pattern** (get/set/delete/list with namespacing), rewrite as generic.

```javascript
const store = new MockaStore('relay')  // namespaced per product
await store.set('key', value)
await store.get('key')          // → value | null
await store.delete('key')
await store.list()              // → [{ key, value }]
await store.clear()
```

---

### 3-4. storage/session.js

Session record management. **Migrated from Orchestra** (296 messages / 16 sessions logic)

```javascript
MockaSession.save(conversationData)   // → sessionId
MockaSession.getAll()                 // → Array<Session>
MockaSession.getById(id)              // → Session | null
MockaSession.search(query)            // → Array<Session>
MockaSession.delete(id)
```

**Session schema:**
```javascript
{
  id: string,           // uuid
  product: string,      // 'orchestra' | 'relay' | 'vault' | 'logbook'
  title: string,
  url: string,
  turns: number,
  messages: [{role, text, ts}],
  tags: string[],
  createdAt: ISO8601,
  updatedAt: ISO8601
}
```

---

### 3-5. storage/export.js

CSV / JSON export. **Migrated from Orchestra** (existing feature)

```javascript
MockaExport.toCSV(sessions)    // → Blob
MockaExport.toJSON(sessions)   // → Blob
MockaExport.download(blob, filename)
```

---

### 3-6. summary/generator.js

Generates a handoff summary from conversation. Used by: **Relay, Vault**

```javascript
MockaSummary.generate(messages, options)
// options: { maxLength: 500, style: 'relay' | 'vault' | 'logbook' }
// → { summary: string, decisions: string[], todos: string[], keywords: string[] }
```

**Implementation approach (no API key required):**
- Extract last N user messages
- Identify decision patterns: "decided", "we'll", "let's", "confirmed"
- Identify TODO patterns: "need to", "should", "will", "next step"
- Concatenate with structured template
- No external LLM call — pure JS string processing

---

### 3-7. summary/injector.js

Injects context into a new claude.ai chat. Used by: **Relay, Vault**

```javascript
MockaInjector.inject(summaryText)
// Focuses claude.ai textarea, inserts summary as first message context
// Returns: Promise<boolean>
```

**Implementation notes:**
- Target `div[contenteditable]` or `textarea` in claude.ai
- Simulate user input events for React compatibility
- Test across claude.ai DOM updates — wrap in version detection

---

### 3-8. settings/prefs.js

Shared user preferences, synced across products. Used by: **all products**

```javascript
MockaPrefs.get(key, defaultValue)
MockaPrefs.set(key, value)
MockaPrefs.getAll()   // → { turnLimit, language, theme, ... }
```

**Default preferences:**
```javascript
{
  turnLimit: 20,          // Relay trigger threshold
  language: 'en',         // 'en' | 'ja'
  autoSave: true,         // Vault auto-save
  showBadge: true,        // Turn counter badge
  summaryStyle: 'relay',
  exportFormat: 'json'
}
```

---

### 3-9. bridge/inter-product.js

Inter-product data sharing. Allows e.g. Relay to hand off to Vault.

```javascript
MockaBridge.emit(event, data)
// event: 'relay:handoff' | 'vault:save' | 'logbook:extract'

MockaBridge.on(event, handler)
MockaBridge.off(event, handler)
```

**Uses `chrome.runtime.sendMessage` for cross-extension communication.**  
Products share a common `externally_connectable` origin: `https://claude.ai`

---

## 4. Orchestra Reuse Decision Table

| Orchestra component | Action | Reason |
|---|---|---|
| Storage module (save/search/export) | ✅ Migrate to session.js + export.js | Core pattern is solid |
| DOM watcher (content.js turn counter) | ⚠️ Reference only, rewrite | Tightly coupled to Orchestra's MoCKA hooks |
| CSV/JSON export | ✅ Migrate to export.js | Clean, reusable as-is |
| background.js message passing | ⚠️ Reference only, rewrite | Simplify — remove MoCKA-specific logic |
| manifest.json structure | ✅ Use as template | Good baseline for all products |
| UI popup (popup.html/js) | ❌ Do not reuse | Product-specific |
| DNA injection hooks | ❌ Do not reuse | MoCKA-specific, not for mini series |

---

## 5. Build & Integration

Each product has its own `manifest.json` and imports Core SDK modules via relative path:

```
orchestra/
  manifest.json
  background.js
  content.js
  lib/ → symlink to ../core-sdk/src/

relay/
  manifest.json
  background.js
  content.js
  popup/
  lib/ → symlink to ../core-sdk/src/
```

**No bundler required for v1** — plain ES modules with `import/export`.  
Chrome MV3 supports ES modules in service workers and content scripts.

---

## 6. Implementation Order (Phase 0)

1. `storage/store.js` — foundation everything else needs
2. `storage/session.js` — migrate Orchestra logic
3. `storage/export.js` — migrate Orchestra logic  
4. `dom/watcher.js` — fresh implementation
5. `dom/extractor.js` — fresh implementation
6. `summary/generator.js` — fresh implementation
7. `summary/injector.js` — fresh implementation
8. `settings/prefs.js` — simple key-value
9. `bridge/inter-product.js` — last, after products take shape

---

## 7. Quality Gates

Before any product ships:
- [ ] Core SDK modules have unit tests
- [ ] No MoCKA-specific code in Core SDK
- [ ] No API keys required in Core SDK
- [ ] Works on Chrome 120+
- [ ] Dark mode compatible (UI modules)
- [ ] English strings only (ja strings in separate locale files)

---

*Generated: 2026-05-16 | mini MoCKA Series Phase 0*

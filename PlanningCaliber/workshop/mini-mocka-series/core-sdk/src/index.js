/**
 * mini MoCKA Core SDK — index.js
 * Public API surface. Import from this file in all products.
 *
 * Usage:
 *   import { MockaWatcher, MockaSummary, MockaSession } from '../lib/index.js';
 */

export { MockaStore }    from './storage/store.js';
export { MockaSession }  from './storage/session.js';
export { MockaExport }   from './storage/export.js';
export { MockaWatcher }  from './dom/watcher.js';
export { MockaExtractor} from './dom/extractor.js';
export { MockaSummary }  from './summary/generator.js';
export { MockaInjector } from './summary/injector.js';
export { MockaPrefs }    from './settings/prefs.js';
export { MockaBridge }   from './bridge/inter-product.js';

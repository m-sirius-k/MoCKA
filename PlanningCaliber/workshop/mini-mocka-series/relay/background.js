/**
 * Relay for Claude — background.js
 */

import { MockaSession } from '../core-sdk/src/storage/session.js';
import { MockaBridge }  from '../core-sdk/src/bridge/inter-product.js';

MockaBridge.initBackground();

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'RELAY_SAVE_SESSION') {
    MockaSession.save({
      product: 'relay',
      title: msg.payload.title,
      url: msg.payload.url,
      messages: msg.payload.messages
    }).then(id => {
      MockaBridge.emit('vault:save-available', { sessionId: id });
      sendResponse({ ok: true, id });
    });
    return true;
  }

  if (msg.type === 'RELAY_GET_STATS') {
    MockaSession.stats().then(stats => sendResponse(stats));
    return true;
  }
});

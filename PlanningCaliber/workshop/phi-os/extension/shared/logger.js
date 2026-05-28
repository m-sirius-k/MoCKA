/**
 * PHI OS — logger.js
 * Lightweight logger with product prefix.
 */

function createLogger(product) {
  const prefix = '[PHI:' + product.toUpperCase() + ']';
  return {
    info:  (...a) => console.info(prefix, ...a),
    warn:  (...a) => console.warn(prefix, ...a),
    error: (...a) => console.error(prefix, ...a),
    debug: (...a) => console.debug(prefix, ...a),
  };
}

if (typeof module !== 'undefined') module.exports = { createLogger };
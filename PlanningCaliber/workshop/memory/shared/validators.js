// shared/validators.js
export function validateRegistry(reg) {
  if (!reg || typeof reg !== 'object') return false;
  if (!reg.schema_version) return false;
  if (!Array.isArray(reg.files)) return false;
  if (!Array.isArray(reg.known_errors)) return false;
  return true;
}

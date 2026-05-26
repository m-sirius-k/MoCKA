// shared/schema.js
export const REGISTRY_SCHEMA = {
  required: ['schema_version', 'workspace_id', 'files', 'known_errors', 'environment'],
  file_fields: ['id', 'path', 'filename', 'ext', 'status', 'hash', 'summary', 'captured_at', 'source'],
  error_fields: ['id', 'signature_hash', 'error_pattern', 'trigger_keywords', 'solution', 'occurrence_count', 'last_seen', 'resolved', 'severity']
};

// shared/constants.js
export const SCHEMA_VERSION = '1.0';

export const PLAN_LIMITS = {
  free: {
    max_files: 20,
    max_errors: 10,
    max_sessions: 1,
    max_decisions: 0,
    time_machine: false
  },
  pro: {
    max_files: 200,
    max_errors: 100,
    max_sessions: 30,
    max_decisions: 50,
    time_machine: false
  },
  one: {
    max_files: -1,
    max_errors: -1,
    max_sessions: -1,
    max_decisions: -1,
    time_machine: true
  }
};

export const FILE_STATUS = {
  STABLE: 'stable',
  MODIFIED: 'modified',
  BROKEN: 'broken',
  UNKNOWN: 'unknown'
};

export const ERROR_SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical'
};

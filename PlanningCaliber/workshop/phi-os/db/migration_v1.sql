-- DNA_v3 migration_v1.sql
-- judgement_reason テーブル追加（Causality層）
-- 対象DB: C:\Users\sirok\MoCKA\data\mocka_events.db
-- 実行前: mocka_write_event(CHANGE_START) 必須

CREATE TABLE IF NOT EXISTS judgement_reason (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id          TEXT    NOT NULL,
  session_date      TEXT    NOT NULL,
  decision          TEXT    NOT NULL
                    CHECK(decision IN ('採用','却下','保留')),
  rejected_reason   TEXT,
  reason            TEXT    NOT NULL,
  error_solved      TEXT,
  tension           TEXT,
  tension_severity  INTEGER DEFAULT 0
                    CHECK(tension_severity BETWEEN 0 AND 5),
  tension_at        TEXT,
  source_map        TEXT,
  tags              TEXT,
  created_at        TEXT    DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_jr_tags
  ON judgement_reason(tags);

CREATE INDEX IF NOT EXISTS idx_jr_tension
  ON judgement_reason(tension_severity DESC);

CREATE INDEX IF NOT EXISTS idx_jr_session
  ON judgement_reason(session_date DESC);

CREATE INDEX IF NOT EXISTS idx_jr_event
  ON judgement_reason(event_id);

# -*- coding: utf-8 -*-
# Connector Caliber v1.0
# Role: gateway/ を MoCKA Caliber層として位置づける
# ref: E20260610_017
import sqlite3
from datetime import datetime, timezone

from flask import jsonify, request

CALIBER_ID = 'connector_caliber_v1'


class ConnectorCaliber:
    def __init__(self, db_path, context_builder, auth, adapters):
        self.db_path = db_path
        self.cb = context_builder
        self.auth = auth
        self.adapters = adapters  # {'gpt': ..., 'gemini': ..., 'copilot': ...}

    def register(self, app):
        @app.route('/api/v1/connector/health', methods=['GET'])
        def connector_health():
            return jsonify({'status': 'ok', 'caliber': CALIBER_ID})

        @app.route('/api/v1/connector/context', methods=['POST'])
        def connector_context():
            data = request.get_json(silent=True) or {}
            mode = data.get('mode', 'standard')
            return jsonify(self.cb.build(mode))

        @app.route('/api/v1/connector/query', methods=['POST'])
        def connector_query():
            data = request.get_json(silent=True) or {}
            ai = data.get('ai', 'unknown')
            query = data.get('query', '')
            context_mode = data.get('context_mode', 'compact')

            if ai not in self.adapters:
                return jsonify({'error': f'unknown ai: {ai}'}), 400

            context = self.cb.build(context_mode)
            result = {'ai': ai, 'query': query, 'context': context}
            self._record_event(ai, query, result)
            return jsonify(result)

    def _record_event(self, ai, query, result):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM events")
            count = cur.fetchone()[0]
            now = datetime.now(timezone.utc)
            event_id = f"E{now.strftime('%Y%m%d')}_{count+1:03d}"

            cur.execute(
                """INSERT INTO events
                   (event_id, title, short_summary, when_ts,
                    who_actor, ai_actor, what_type, free_note,
                    where_component, lifecycle_phase, why_purpose)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_id,
                    f"connector_query: {ai}",
                    (query or "")[:200],
                    now.isoformat(),
                    ai,
                    "connector_caliber",
                    "connector_query",
                    "",
                    "connector_caliber",
                    "in_operation",
                    "connector_caliber_v1_auto_record",
                )
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

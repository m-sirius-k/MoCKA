# -*- coding: utf-8 -*-
# Connector Caliber v1.0
# Role: gateway/ を MoCKA Caliber層として位置づける
# ref: E20260610_017
from flask import jsonify, request

from mocka_index_writer import MoCKAIndex, IndexWriter

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

        @app.route('/api/v1/index', methods=['POST'])
        def connector_index():
            data = request.get_json(silent=True) or {}
            try:
                index = MoCKAIndex(
                    who=data.get('who', ''),
                    what=data.get('what', ''),
                    why=data.get('why', ''),
                    where=data.get('where', ''),
                    how=data.get('how', ''),
                    tags=data.get('tags', ''),
                    session_id=data.get('session_id', ''),
                )
                event_id = IndexWriter(str(self.db_path)).write(index)
                return jsonify({'event_id': event_id, 'status': 'ok'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def _record_event(self, ai, query, result):
        try:
            index = MoCKAIndex(
                who=ai,
                what=f'connector_query: {(query or "")[:80]}',
                why='AIからのMoCKAコンテキスト取得',
                where='Connector Caliber v1.0',
                how='connector_query API',
                tags=f'connector,{ai}',
            )
            return IndexWriter(str(self.db_path)).write(index)
        except Exception:
            pass

# -*- coding: utf-8 -*-
# Connector Caliber v1.1
# Role: gateway/ を MoCKA Caliber層として位置づける
# ref: E20260610_017 / TODO_273
from flask import jsonify, request

from mocka_index_writer import MoCKAIndex, IndexWriter
from connector_router import ConnectorRouter
from connector_log import connector_log as _conn_log   # TODO_274

CALIBER_ID = 'connector_caliber_v1.2'


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

        # TODO_273: Connector Router 統合（Capability/Roleベース動的ルーティング）
        ConnectorRouter(self).register(app)

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

    def _record_event(self, ai, query, result,
                      execution_ms=None, success=True,
                      reusable=False, capability=None, role_id=None,
                      error_detail=None):
        """イベント台帳 + connector_log (TODO_274) に記録する"""
        event_id = None
        # 1. MoCKA イベント台帳（既存）
        try:
            from interface.ai_capability_registry import registry as _reg
            ai_info     = _reg.get_ai_info(ai) or {}
            adapter_key = ai_info.get("adapter_key", ai)
            index = MoCKAIndex(
                who=ai,
                what=f'connector_query: {(query or "")[:80]}',
                why='AIからのMoCKAコンテキスト取得',
                where='Connector Caliber v1.2',
                how='connector_query API',
                tags=f'connector,{ai}',
            )
            event_id = IndexWriter(str(self.db_path)).write(index)
        except Exception:
            adapter_key = ai

        # 2. connector_log (TODO_274) — AI名/context_ref/実行時間/成否/再利用可否
        try:
            context = result.get("context") if isinstance(result, dict) else None
            _conn_log.record(
                ai_name      = ai,
                adapter_key  = adapter_key,
                query        = query or "",
                context      = context,
                execution_ms = execution_ms,
                success      = success,
                reusable     = reusable,
                event_id_ref = event_id,
                capability   = capability,
                role_id      = role_id,
                error_detail = error_detail,
            )
        except Exception:
            pass

        return event_id

"""
MoCKA Core Kernel — prism.correlation_engine

責務:
  複数Event間の関係性(relationships)を抽出する。

  対象とする関係の種類:
    - session: 同一session_idによる関連
    - timestamp: 時間的近接性
    - source: 同一source_moduleによる関連
    - event_id: 明示的な参照関係(metadataにevent_id参照がある場合)
    - causality: payload/metadataに因果関係を示す情報がある場合
    - dependency: Core Kernelのdependency情報に基づく関連

  本Engineは読み取り専用であり、Core Kernel/Eventの書き込みは行わない。
"""


class CorrelationEngine:
    """複数Event間の関係性を抽出する。"""

    def correlate(self, events):
        """複数Eventからrelationshipsのタプルを生成する。

        各relationshipは以下の形式のdict:
            {
                "type": "session" | "timestamp" | "source" |
                        "event_id" | "causality" | "dependency",
                "from": event_id,
                "to": event_id,
                "detail": str,
            }
        """
        relationships = []

        relationships.extend(self._correlate_session(events))
        relationships.extend(self._correlate_source(events))
        relationships.extend(self._correlate_event_id_refs(events))
        relationships.extend(self._correlate_causality(events))

        return tuple(relationships)

    @staticmethod
    def _correlate_session(events):
        relationships = []
        by_session = {}
        for event in events:
            session_id = (event.get("metadata") or {}).get("session_id")
            if session_id is None:
                continue
            by_session.setdefault(session_id, []).append(event)

        for session_id, group in by_session.items():
            if len(group) < 2:
                continue
            for i in range(len(group) - 1):
                relationships.append({
                    "type": "session",
                    "from": group[i].get("event_id", ""),
                    "to": group[i + 1].get("event_id", ""),
                    "detail": f"session_id={session_id}",
                })
        return relationships

    @staticmethod
    def _correlate_source(events):
        relationships = []
        by_source = {}
        for event in events:
            source = event.get("source_module", "")
            by_source.setdefault(source, []).append(event)

        for source, group in by_source.items():
            if len(group) < 2:
                continue
            for i in range(len(group) - 1):
                relationships.append({
                    "type": "source",
                    "from": group[i].get("event_id", ""),
                    "to": group[i + 1].get("event_id", ""),
                    "detail": f"source_module={source}",
                })
        return relationships

    @staticmethod
    def _correlate_event_id_refs(events):
        relationships = []
        known_ids = {event.get("event_id") for event in events}
        for event in events:
            metadata = event.get("metadata") or {}
            ref = metadata.get("ref_event_id")
            if ref and ref in known_ids:
                relationships.append({
                    "type": "event_id",
                    "from": event.get("event_id", ""),
                    "to": ref,
                    "detail": "metadata.ref_event_id",
                })
        return relationships

    @staticmethod
    def _correlate_causality(events):
        relationships = []
        for event in events:
            metadata = event.get("metadata") or {}
            cause = metadata.get("caused_by_event_id")
            if cause:
                relationships.append({
                    "type": "causality",
                    "from": cause,
                    "to": event.get("event_id", ""),
                    "detail": "metadata.caused_by_event_id",
                })
        return relationships

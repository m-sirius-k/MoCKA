"""
Write Path v1.0 -- Runtime Binding Layer (Phase 8-2)

Schema Layer(governance/write_path/{evidence,transition,restore}/schema.py)は
契約境界として一切変更しない。本パッケージはそのschemaに対して、
既存の events.db / decision_ledger.jsonl / anchor_record.json を
読み取り専用で束ね、レコードを組み立てる責務のみを持つ。

    Schema Layer
        |
        v
    Runtime Binding Layer   <- 本パッケージ
        |
        v
    Existing Governance Infrastructure (events.db / decision_ledger.jsonl / anchor_record.json)

書き込み責務は以下に厳密に限定する:
    - events.db への書き込みは interface/gate_policy.py の
      ALLOWED_DIRECT_CHANNELS 内 "restore" チャネル経由のみ(generator.record_change_event)
    - decision_ledger.jsonl への書き込みは行わない(Decision Authority専属)
    - restore_packet.json への書き込みは行わない(Legacy、凍結・read-only維持)
"""

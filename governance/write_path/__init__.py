"""
Write Path v1.0 -- MoCKA Core Governance Layer

Observation -> Runtime Evidence Record -> Governance Transition Record
    -> Governance Seal -> Restore Packet v1 -> Reader Verification -> DNA Injection

このパッケージは Evidence の生成・Authority への接続・Restore Packet の
再構成のみを責務とする(WRITE_PATH_v1_FINAL_SPEC, DESIGN_FROZEN 準拠)。

Generator Owner = MoCKA Core Governance Layer のみ。
Extension / Relay / MCP は本パッケージのロジックを呼び出す側であって、
生成責務を持たない(Principle 1: Reader != Generator)。
"""

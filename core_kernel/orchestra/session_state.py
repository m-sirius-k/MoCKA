"""
MoCKA Core Kernel — orchestra.session_state

セッション単位の状態保持(event/execution/output ログ)。
"""


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id

        self.event_log = []
        self.execution_log = []
        self.output_log = []

    def apply_event(self, event):
        self.event_log.append(event)

    def apply_execution(self, execution):
        self.execution_log.append(execution)

    def apply_output(self, output):
        self.output_log.append(output)

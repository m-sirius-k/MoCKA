"""
MoCKA Core Kernel — orchestra.execution_graph

ノードID -> ハンドラのマッピングと実行。
"""


class ExecutionGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, handler):
        self.nodes[node_id] = handler

    def execute(self, node_id, context):
        if node_id not in self.nodes:
            raise Exception(f"Node not found: {node_id}")

        return self.nodes[node_id](context)

"""
phios_integration.tests.test_external_interfaces

Memory/Relay/Orchestra連携インターフェース(ABC)に関するテスト。

本Phaseではインターフェース定義のみを確認し、実データ保存・実通信・
実行制御は行わない。
"""

import pytest

from core_kernel.phios_integration import (
    MemoryWriterInterface,
    OrchestraAdapterInterface,
    RelayAdapterInterface,
)


@pytest.mark.parametrize("interface_cls", [
    MemoryWriterInterface,
    RelayAdapterInterface,
    OrchestraAdapterInterface,
])
def test_interfaces_cannot_be_instantiated_directly(interface_cls):
    with pytest.raises(TypeError):
        interface_cls()


def test_memory_writer_interface_abstract_methods():
    assert MemoryWriterInterface.__abstractmethods__ == frozenset({
        "write_analysis", "write_context", "write_observation",
    })


def test_relay_adapter_interface_abstract_methods():
    assert RelayAdapterInterface.__abstractmethods__ == frozenset({
        "push_context", "pull_context", "merge_context",
    })


def test_orchestra_adapter_interface_abstract_methods():
    assert OrchestraAdapterInterface.__abstractmethods__ == frozenset({
        "plan", "suggest_actions", "evaluate_state",
    })

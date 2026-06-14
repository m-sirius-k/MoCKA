"""
phios_integration.tests.test_external_interfaces

将来のMemory/Relay/Orchestra連携インターフェース(未実装)に関するテスト。

本Phaseではインターフェース定義のみを確認し、実装・接続は行わない。
"""

import pytest

from core_kernel.phios_integration import (
    MemoryWriterInterface,
    OrchestraNotifierInterface,
    RelayAdapterInterface,
)


@pytest.mark.parametrize(
    "interface_cls,method_name",
    [
        (MemoryWriterInterface, "write"),
        (RelayAdapterInterface, "send"),
        (OrchestraNotifierInterface, "notify"),
    ],
)
def test_interfaces_cannot_be_instantiated_directly(interface_cls, method_name):
    with pytest.raises(TypeError):
        interface_cls()


@pytest.mark.parametrize(
    "interface_cls,method_name",
    [
        (MemoryWriterInterface, "write"),
        (RelayAdapterInterface, "send"),
        (OrchestraNotifierInterface, "notify"),
    ],
)
def test_interfaces_define_abstract_method(interface_cls, method_name):
    assert method_name in interface_cls.__abstractmethods__


def test_interfaces_are_not_implemented_yet():
    """未実装であることの確認: 具象クラスが存在しないこと。"""
    import core_kernel.phios_integration as integration

    for name in dir(integration):
        assert "Writer" not in name or name == "MemoryWriterInterface"
        assert "Adapter" not in name or name == "RelayAdapterInterface"
        assert "Notifier" not in name or name == "OrchestraNotifierInterface"

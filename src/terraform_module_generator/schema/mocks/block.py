"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .attribute import AttributeMock
    from .nested_block import NestedBlockMock


@dataclass()
class BlockMock:
    """
    Mock object for https://github.com/inmanta/inmanta-tfplugin/blob
        /7269bc7d28d751b5dc110161dae29a6209c3fb63/docs/tf_grpc_plugin
        /proto/inmanta_tfplugin/tfplugin5.proto#L81
    """

    version: int
    attributes: typing.List["AttributeMock"]
    block_types: typing.List["NestedBlockMock"]
    description: str
    description_kind: str
    deprecated: bool = False

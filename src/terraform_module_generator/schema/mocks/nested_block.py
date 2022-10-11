"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .block import BlockMock


@dataclass()
class NestedBlockMock:
    """
    Mock object for https://github.com/inmanta/inmanta-tfplugin/blob
        /7269bc7d28d751b5dc110161dae29a6209c3fb63/docs/tf_grpc_plugin
        /proto/inmanta_tfplugin/tfplugin5.proto#L102
    """

    type_name: str
    block: "BlockMock"
    nesting: int
    min_items: int
    max_items: int

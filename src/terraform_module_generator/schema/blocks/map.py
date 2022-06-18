"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .nested_block import NestedBlock, nested_block


def is_map(schema: Any) -> bool:
    return schema.nesting == 4


@nested_block(index="abc-map-z", condition=is_map)
class MapNestedBlock(NestedBlock):
    pass

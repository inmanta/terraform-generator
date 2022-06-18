"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .nested_block import NestedBlock, nested_block


def is_list(schema: Any) -> bool:
    return schema.nesting == 2


@nested_block(index="abc-list-z", condition=is_list)
class ListNestedBlock(NestedBlock):
    pass

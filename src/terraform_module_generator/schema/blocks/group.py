"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .nested_block import NestedBlock, nested_block


def is_group(schema: Any) -> bool:
    return schema.nesting == 5


@nested_block(index="abc-group-z", condition=is_group)
class GroupNestedBlock(NestedBlock):
    pass

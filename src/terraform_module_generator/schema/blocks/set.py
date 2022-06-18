"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .nested_block import NestedBlock, nested_block


def is_set(schema: Any) -> bool:
    return schema.nesting == 3


@nested_block(index="abc-set-z", condition=is_set)
class SetNestedBlock(NestedBlock):
    pass

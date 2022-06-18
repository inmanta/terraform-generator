"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .nested_block import NestedBlock, nested_block


def is_single(schema: Any) -> bool:
    return schema.nesting == 1


@nested_block(index="abc-single-z", condition=is_single)
class SingleNestedBlock(NestedBlock):
    pass

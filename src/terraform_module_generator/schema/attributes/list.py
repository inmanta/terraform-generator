"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from terraform_module_generator.schema import mocks

from .base import attribute
from .collection import CollectionAttribute


def is_list(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        ListAttribute.legacy_regex.fullmatch(t) is not None
        or ListAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-list-z", condition=is_list)
class ListAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["list",(.+)\]')
    regex = re.compile(r"list\((.+)\)")

    def as_nested_block(self) -> mocks.NestedBlockMock:
        nested_block = super().as_nested_block()
        nested_block.nesting = 2  # LIST
        return nested_block

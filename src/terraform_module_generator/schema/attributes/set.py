"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any
import typing

from terraform_module_generator.schema import mocks
from terraform_module_generator.schema.helpers.cache import cache_method_result

from inmanta_module_factory import builder

from .base import attribute
from .collection import CollectionAttribute


def is_set(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        SetAttribute.legacy_regex.fullmatch(t) is not None
        or SetAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-set-z", condition=is_set)
class SetAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["set",(.+)\]')
    regex = re.compile(r"set\((.+)\)")

    @cache_method_result
    def get_serialized_attribute_expression(self, entity_reference: str, module_builder: builder.InmantaModuleBuilder, imports: typing.Set[str]) -> str:
        # For sets we sort the list of values to make sure the config serialization is consistent
        attribute_reference = super().get_serialized_attribute_expression(entity_reference, module_builder, imports)
        imports.add("terraform")
        sorted_list = f"terraform::sorted_list({attribute_reference})"

        if self.optional:
            return f"{attribute_reference} is defined ? {sorted_list} : {attribute_reference}"
        else:
            return sorted_list

    @cache_method_result
    def nested_block_mock(self) -> mocks.NestedBlockMock:
        nested_block = super().nested_block_mock()
        nested_block.nesting = 3  # SET
        return nested_block

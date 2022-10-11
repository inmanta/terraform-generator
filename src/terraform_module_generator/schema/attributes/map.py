"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
import typing

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema import mocks
from terraform_module_generator.schema.helpers.cache import cache_method_result

from .base import attribute
from .collection import CollectionAttribute


def is_map(attribute: typing.Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        MapAttribute.legacy_regex.fullmatch(t) is not None
        or MapAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-map-z", condition=is_map)
class MapAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["map",(.+)\]')
    regex = re.compile(r"map\((.+)\)")

    @cache_method_result
    def inmanta_attribute_type(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.InmantaType:
        return inmanta.InmantaDictType

    def as_nested_block(self) -> mocks.NestedBlockMock:
        nested_block = super().as_nested_block()
        nested_block.nesting = 4  # MAP
        return nested_block

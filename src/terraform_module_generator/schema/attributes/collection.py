"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
import re

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema import mocks
from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.attributes.structure import StructureAttribute
from terraform_module_generator.schema.helpers.cache import cache_method_result
from terraform_module_generator.schema.mocks import AttributeMock


class CollectionAttribute(Attribute):
    legacy_regex: re.Pattern[str]
    regex: re.Pattern[str]

    def __init__(self, path: typing.List[str], schema: typing.Any) -> None:
        super().__init__(path, schema)
        self.inner_type = self.get_inner_type(path, schema)

    @cache_method_result
    def inmanta_attribute_type(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.InmantaType:
        inner_type = self.inner_type.inmanta_attribute_type(module_builder)
        assert isinstance(inner_type, inmanta.InmantaBaseType)
        return inmanta.InmantaListType(inner_type)

    @cache_method_result
    def nested_block_mock(self) -> mocks.NestedBlockMock:
        assert isinstance(self.inner_type, StructureAttribute)

        return mocks.NestedBlockMock(
            type_name=self.name,
            block=self.inner_type.block_mock(),
            nesting=0,  # This will have to be overwritten in sub-classes
            min_items=0,
            max_items=0,  # No upper bound
        )

    @classmethod
    def get_inner_type_expression(cls, schema: typing.Any) -> bytes:
        t = schema.type.decode("utf-8")
        legacy_match = cls.legacy_regex.fullmatch(t)
        if legacy_match:
            return legacy_match.group(1).strip().encode("utf-8")

        match = cls.regex.fullmatch(t)
        if match:
            return match.group(1).strip().encode("utf-8")

        raise ValueError(f"Failed to match type: {t}")

    @classmethod
    def get_inner_type(cls, path: typing.List[str], schema: typing.Any) -> Attribute:
        mock = AttributeMock(
            name=schema.name,
            type=cls.get_inner_type_expression(schema),
        )
        return Attribute.build_attribute(path, mock)

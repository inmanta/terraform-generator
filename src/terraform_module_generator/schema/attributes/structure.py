"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import abc
import re
import typing

from inmanta_module_factory.helpers.utils import inmanta_safe_name

from terraform_module_generator.schema import mocks
from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.helpers.cache import cache_method_result


class StructureAttribute(Attribute):
    legacy_regex: re.Pattern[str]
    regex: re.Pattern[str]

    def __init__(self, path: typing.List[str], schema: typing.Any) -> None:
        Attribute.__init__(self, path, schema)
        self.inner_attributes = self.get_inner_attributes(
            path + [inmanta_safe_name(self.name)], schema
        )

    @cache_method_result
    def block_mock(self) -> mocks.BlockMock:
        return mocks.BlockMock(
            version=0,
            attributes=[attr._source_attribute for attr in self.inner_attributes],
            block_types=[],
            description=self.description,
            description_kind=self.description_kind,
            deprecated=self.deprecated,
        )

    @classmethod
    def get_inner_attributes_expression(cls, schema: typing.Any) -> str:
        t = schema.type.decode("utf-8")
        legacy_match = cls.legacy_regex.fullmatch(t)
        if legacy_match:
            return legacy_match.group(1)

        match = cls.regex.fullmatch(t)
        if match:
            return match.group(1)

        raise ValueError(f"Failed to match type: {t}")

    @classmethod
    @abc.abstractmethod
    def get_inner_attributes(
        cls, path: typing.List[str], schema: typing.Any
    ) -> typing.List[Attribute]:
        """
        Return a list of inner attribute objects.
        """

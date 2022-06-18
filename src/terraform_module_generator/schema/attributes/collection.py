"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from regex import Pattern

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.mocks import AttributeMock


class CollectionAttribute(Attribute):
    legacy_regex: Pattern[str]
    regex: Pattern[str]

    def __init__(self, schema: Any) -> None:
        super().__init__(schema)
        self.inner_type = self.get_inner_type(schema)

    @classmethod
    def get_inner_type_expression(cls, schema: Any) -> bytes:
        t = schema.type.decode("utf-8")
        legacy_match = cls.legacy_regex.fullmatch(t)
        if legacy_match:
            return legacy_match.group(1).strip().encode("utf-8")

        match = cls.regex.fullmatch(t)
        if match:
            return match.group(1).strip().encode("utf-8")

        raise ValueError(f"Failed to match type: {t}")

    @classmethod
    def get_inner_type(cls, schema: Any) -> Attribute:
        mock = AttributeMock(
            name=schema.name,
            type=cls.get_inner_type_expression(schema),
        )
        return Attribute.build_attribute(mock)

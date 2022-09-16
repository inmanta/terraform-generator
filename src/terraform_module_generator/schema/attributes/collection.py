"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, List

from inmanta_module_factory import builder, inmanta
from regex import Pattern

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.helpers.cache import cache_method_result
from terraform_module_generator.schema.mocks import AttributeMock


class CollectionAttribute(Attribute):
    legacy_regex: Pattern[str]
    regex: Pattern[str]

    def __init__(self, path: List[str], schema: Any) -> None:
        super().__init__(path, schema)
        self.inner_type = self.get_inner_type(path, schema)

    @cache_method_result
    def get_entity_field(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityField:
        inner_type_field = self.inner_type.get_entity_field(module_builder)
        if isinstance(inner_type_field, inmanta.Attribute):
            # If the inner type is a simple attribute, we can wrap its in a list and return the original
            # attribute
            inner_type_field.inmanta_type = inmanta.InmantaListType(
                inner_type_field.inmanta_type
            )
            return inner_type_field

        assert isinstance(
            inner_type_field, inmanta.EntityRelation
        ), "If the inner field is not an attribute, it must be a relation."
        # If the field is a relation, and we can have a list of it, we must remove any upper bound
        # Then we can return the original object
        inner_type_field.cardinality_max = None
        return inner_type_field

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
    def get_inner_type(cls, path: List[str], schema: Any) -> Attribute:
        mock = AttributeMock(
            name=schema.name,
            type=cls.get_inner_type_expression(schema),
        )
        return Attribute.build_attribute(path, mock)

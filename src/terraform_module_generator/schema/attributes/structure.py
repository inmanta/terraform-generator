"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from abc import abstractclassmethod
from typing import Any, List

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name
from regex import Pattern

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.helpers.cache import cache_method_result


class StructureAttribute(Attribute):
    legacy_regex: Pattern[str]
    regex: Pattern[str]

    def __init__(self, path: List[str], schema: Any) -> None:
        super().__init__(path, schema)
        self.inner_attributes = self.get_inner_attributes(
            path + [inmanta_safe_name(self.name)], schema
        )

    @cache_method_result
    def get_entity(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Entity:
        entity = inmanta.Entity(
            name=inmanta_entity_name(self.name),
            path=self.path,
            description=self.description,
        )
        module_builder.add_module_element(entity)

        for attribute in self.inner_attributes:
            field = attribute.get_entity_field(module_builder)
            entity.attach_field(field)
            field.attach_entity(entity)

        return entity

    @cache_method_result
    def get_entity_field(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityField:
        entity = self.get_entity(module_builder)
        relation = inmanta.EntityRelation(
            name=inmanta_safe_name(self.name),
            path=entity.path,
            cardinality=(0 if self.optional else 1, 1),
            description=self.description,
            peer=inmanta.EntityRelation(
                name="",
                path=entity.path,
                cardinality=(1, 1),
                entity=entity,
            ),
        )
        module_builder.add_module_element(relation)

        return relation

    @classmethod
    def get_inner_attributes_expression(cls, schema: Any) -> str:
        t = schema.type.decode("utf-8")
        legacy_match = cls.legacy_regex.fullmatch(t)
        if legacy_match:
            return legacy_match.group(1)

        match = cls.regex.fullmatch(t)
        if match:
            return match.group(1)

        raise ValueError(f"Failed to match type: {t}")

    @abstractclassmethod
    def get_inner_attributes(cls, path: List[str], schema: Any) -> List[Attribute]:
        """
        Return a list of inner attribute objects.
        """

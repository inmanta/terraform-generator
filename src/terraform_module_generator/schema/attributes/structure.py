"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from abc import abstractclassmethod
from typing import Any, List
from regex import Pattern
from terraform_module_generator.schema.helpers.cache import cache_method_result

from terraform_module_generator.schema.attributes.base import Attribute


from inmanta_module_factory import inmanta, builder
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name

class StructureAttribute(Attribute):
    legacy_regex: Pattern[str]
    regex: Pattern[str]

    def __init__(self, schema: Any) -> None:
        super().__init__(schema)
        self.inner_attributes = self.get_inner_attributes(schema)

    @cache_method_result
    def get_entity(self, module_builder: builder.InmantaModuleBuilder) -> inmanta.Entity:
        entity = inmanta.Entity(
            name=inmanta_entity_name(self.name),
            path=[],  # TODO
            description=self.description,
        )
        module_builder.add_module_element(entity)

        for attribute in self.inner_attributes:
            entity.attach_field(attribute.get_entity_field(module_builder))

        return entity

    @cache_method_result
    def get_entity_field(self, module_builder: builder.InmantaModuleBuilder) -> inmanta.EntityField:
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
    def get_inner_attributes(cls, schema: Any) -> List[Attribute]:
        """
        Return a list of inner attribute objects.        
        """

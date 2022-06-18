"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import json
import re
from typing import Any, List
from terraform_module_generator.schema.helpers.cache import cache

from terraform_module_generator.schema.mocks.attribute import AttributeMock

from .base import Attribute, attribute
from .structure import StructureAttribute
from inmanta_module_factory.inmanta import EntityField, Entity, EntityRelation
from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name


def is_object(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        ObjectAttribute.legacy_regex.fullmatch(t) is not None
        or ObjectAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-object-z", condition=is_object)
class ObjectAttribute(StructureAttribute):
    legacy_regex = re.compile(r'\["object",(.+)\]')
    regex = re.compile(r"object\((.+)\)")

    def __init__(self, schema: Any) -> None:
        super().__init__(schema)
        self.inner_attributes = self.get_inner_attributes(schema)

    @cache
    def get_entity(self, module_builder: InmantaModuleBuilder) -> Entity:
        entity = Entity(
            name=inmanta_entity_name(self.name),
            path=[],  # TODO
            description=self.description,
        )
        module_builder.add_module_element(entity)

        for attribute in self.inner_attributes:
            entity.attach_field(attribute.get_entity_field(module_builder))

        return entity

    @cache
    def get_entity_field(self, module_builder: InmantaModuleBuilder) -> EntityField:
        entity = self.get_entity(module_builder)
        relation = EntityRelation(
            name=inmanta_safe_name(self.name),
            path=entity.path,
            cardinality=(0, 1),  # TODO
            description=self.description,
            peer=EntityRelation(
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

    @classmethod
    def get_inner_attributes(cls, schema: Any) -> List[Attribute]:
        raw_inner_attributes_expression = cls.get_inner_attributes_expression(schema)
        inner_attributes_expression: dict = json.loads(raw_inner_attributes_expression)
        return [
            Attribute.build_attribute(
                AttributeMock(
                    type=json.dumps(value).strip().encode("utf-8"),
                    name=key,
                )
            )
            for key, value in inner_attributes_expression.items()
        ]

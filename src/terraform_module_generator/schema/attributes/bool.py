"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.attributes.base import Attribute, attribute
from inmanta_module_factory.inmanta import EntityField, InmantaBooleanType
from inmanta_module_factory.builder import InmantaModuleBuilder


def is_bool(attribute: Any) -> bool:
    return attribute.type.decode("utf-8") in ["bool", '"bool"']


@attribute(index="abc-boolean-z", condition=is_bool)
class BooleanAttribute(Attribute):
    def get_entity_field(self, module_builder: InmantaModuleBuilder) -> EntityField:
        return InmantaBooleanType

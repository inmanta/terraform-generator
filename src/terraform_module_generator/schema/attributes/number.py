"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.attributes.base import Attribute, attribute
from inmanta_module_factory.inmanta import EntityField, InmantaNumberType
from inmanta_module_factory.builder import InmantaModuleBuilder


def is_number(attribute: Any) -> bool:
    return attribute.type.decode("utf-8") in ["number", '"number"']


@attribute(index="abc-number-z", condition=is_number)
class NumberAttribute(Attribute):
    def get_entity_field(self, module_builder: InmantaModuleBuilder) -> EntityField:
        return InmantaNumberType

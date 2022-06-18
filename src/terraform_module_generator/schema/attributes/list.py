"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from .base import attribute
from .collection import CollectionAttribute
from inmanta_module_factory.inmanta import EntityField, InmantaListType, EntityRelation, InmantaBaseType
from inmanta_module_factory.builder import InmantaModuleBuilder


def is_list(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        ListAttribute.legacy_regex.fullmatch(t) is not None
        or ListAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-list-z", condition=is_list)
class ListAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["list",(.+)\]')
    regex = re.compile(r"list\((.+)\)")

    def get_entity_field(self, module_builder: InmantaModuleBuilder) -> EntityField:
        inner_type_field = self.inner_type.get_entity_field(module_builder)
        if isinstance(inner_type_field, InmantaBaseType):
            return InmantaListType(inner_type_field)
        
        # TODO

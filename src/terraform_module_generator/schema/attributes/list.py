"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from inmanta_module_factory import builder, inmanta

from .base import attribute
from .collection import CollectionAttribute
from terraform_module_generator.schema.helpers.cache import cache_method_result



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

    

    @cache_method_result
    def get_entity_field(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityField:
        inner_type_field = super().get_entity_field(module_builder)

        if isinstance(inner_type_field, inmanta.EntityRelation):
            # We must also add a key attribute on the entity, that will be used as key in the map
            inner_type_field.peer.entity.attributes.append(
                inmanta.Attribute(
                    name="_sorting_index",
                    inmanta_type=inmanta.InmantaStringType,
                    optional=False,
                    description="(required) The index used to store the relation this entity is part of.",
                )
            )

        return inner_type_field

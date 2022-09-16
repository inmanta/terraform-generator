"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema.helpers.cache import cache_method_result

from .base import attribute
from .collection import CollectionAttribute


def is_map(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        MapAttribute.legacy_regex.fullmatch(t) is not None
        or MapAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-map-z", condition=is_map)
class MapAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["map",(.+)\]')
    regex = re.compile(r"map\((.+)\)")

    @cache_method_result
    def get_entity_field(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityField:
        inner_type_field = super().get_entity_field(module_builder)

        if isinstance(inner_type_field, inmanta.EntityRelation):
            # We must also add a key attribute on the entity, that will be used as key in the map
            inner_type_field.peer.entity.attributes.append(
                inmanta.Attribute(
                    name=f"{self.name}_key",
                    inmanta_type=inmanta.InmantaStringType,
                    optional=False,
                    description="(required) The key to identify this instance.",
                )
            )

        return inner_type_field

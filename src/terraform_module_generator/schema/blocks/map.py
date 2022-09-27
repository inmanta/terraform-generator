"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from typing import Any

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema.helpers.cache import cache_method_result

from .nested_block import NestedBlock, nested_block


def is_map(schema: Any) -> bool:
    return schema.nesting == 4


@nested_block(index="abc-map-z", condition=is_map)
class MapNestedBlock(NestedBlock):
    @cache_method_result
    def get_map_key_attribute(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Attribute:
        return inmanta.Attribute(
            name="_map_key",
            inmanta_type=inmanta.InmantaStringType,
            optional=False,
            description="The key used to reference this entity in the mapping it is a part of.",
            entity=self.get_entity(module_builder),
        )

    @cache_method_result
    def get_config_block_attributes(
        self,
        module_builder: builder.InmantaModuleBuilder,
        imports: typing.Set[str],
    ) -> typing.Dict[str, str]:
        attributes = super().get_config_block_attributes(module_builder, imports)
        attributes["nesting_mode"] = '"map"'
        attributes["key"] = "self." + self.get_map_key_attribute(module_builder).name
        return attributes

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        index = inmanta.Index(
            path=self.get_entity(module_builder).path,
            entity=self.get_entity(module_builder),
            fields=[
                self.get_entity_relation(module_builder).peer,
                self.get_map_key_attribute(module_builder),
            ],
            description="This index ensure that each element of the config tree is unique",
        )
        module_builder.add_module_element(index)
        return index

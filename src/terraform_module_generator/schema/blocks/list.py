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


def is_list(schema: Any) -> bool:
    return schema.nesting == 2


@nested_block(index="abc-list-z", condition=is_list)
class ListNestedBlock(NestedBlock):
    @cache_method_result
    def get_list_index_attribute(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Attribute:
        return inmanta.Attribute(
            name="_sorting_index",
            inmanta_type=inmanta.InmantaStringType,
            optional=False,
            description="The index used to store the relation this entity is part of.",
            entity=self.get_entity(module_builder),
        )

    @cache_method_result
    def get_config_block_attributes(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Dict[str, str]:
        attributes = super().get_config_block_attributes(module_builder)
        attributes["nesting_mode"] = '"list"'
        attributes["key"] = "self." + self.get_list_index_attribute(module_builder).name
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
                self.get_list_index_attribute(module_builder),
            ],
            description="This index ensure that each element of the config tree is unique",
        )
        module_builder.add_module_element(index)
        return index

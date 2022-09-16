"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import TYPE_CHECKING, Any, List

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.helpers.cache import cache_method_result

if TYPE_CHECKING:
    from terraform_module_generator.schema.blocks.nested_block import NestedBlock


class Block:
    def __init__(self, name: str, path: List[str], schema: Any) -> None:
        self.name = name
        self.path = path
        self.attributes = Block.get_attributes(path + [inmanta_safe_name(name)], schema)
        self.nested_blocks = Block.get_nested_blocks(
            path + [inmanta_safe_name(name)], schema
        )
        self.description: str = schema.description
        self.deprecated: bool = schema.deprecated

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

        for attribute in self.attributes:
            field = attribute.get_entity_field(module_builder)
            entity.attach_field(field)
            field.attach_entity(entity)

        for nested_block in self.nested_blocks:
            relation = nested_block.get_entity_relation(module_builder)
            entity.attach_field(relation)
            relation.attach_entity(entity)

        return entity

    @staticmethod
    def get_attributes(path: List[str], block: Any) -> List[Attribute]:
        print(block)
        return [
            Attribute.build_attribute(path, attribute) for attribute in block.attributes
        ]

    @staticmethod
    def get_nested_blocks(path: List[str], block: Any) -> List["NestedBlock"]:
        from terraform_module_generator.schema.blocks.nested_block import NestedBlock

        return [
            NestedBlock.build_nested_block(path, block_type)
            for block_type in block.block_types
        ]

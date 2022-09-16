"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import TYPE_CHECKING, Any, List
from terraform_module_generator.schema.helpers.cache import cache_method_result

from terraform_module_generator.schema.attributes.base import Attribute

from inmanta_module_factory import inmanta, builder
from inmanta_module_factory.helpers.utils import inmanta_entity_name

if TYPE_CHECKING:
    from terraform_module_generator.schema.blocks.nested_block import NestedBlock


class Block:
    def __init__(self, schema: Any) -> None:
        self.attributes = Block.get_attributes(schema)
        self.nested_blocks = Block.get_nested_blocks(schema)
        self.description: str = schema.description
        self.deprecated: bool = schema.deprecated

    @cache_method_result
    def get_entity(self, module_builder: builder.InmantaModuleBuilder) -> inmanta.Entity:
        entity = inmanta.Entity(
            name=inmanta_entity_name(self.name),
            path=[],  # TODO
            description=self.description,
        )
        module_builder.add_module_element(entity)

        for attribute in self.attributes:
            entity.attach_field(attribute.get_entity_field(module_builder))
        
        for nested_block in self.nested_blocks:
            entity.attach_field(nested_block.get_entity_relation(module_builder))

        return entity

    @staticmethod
    def get_attributes(block: Any) -> List[Attribute]:
        return [Attribute.build_attribute(attribute) for attribute in block.attributes]

    @staticmethod
    def get_nested_blocks(block: Any) -> List["NestedBlock"]:
        from terraform_module_generator.schema.blocks.nested_block import NestedBlock
        return [
            NestedBlock.build_nested_block(block_type)
            for block_type in block.block_types
        ]

"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, List

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.blocks import nested_block


class Block:
    def __init__(self, schema: Any) -> None:
        self.attributes = Block.get_attributes(schema)
        self.nested_blocks = Block.get_nested_blocks(schema)
        self.description: str = schema.description
        self.deprecated: bool = schema.deprecated

    @staticmethod
    def get_attributes(block: Any) -> List[Attribute]:
        return [Attribute.build_attribute(attribute) for attribute in block.attributes]

    @staticmethod
    def get_nested_blocks(block: Any) -> List["nested_block.NestedBlock"]:
        return [
            nested_block.NestedBlock.build_nested_block(block_type)
            for block_type in block.block_types
        ]

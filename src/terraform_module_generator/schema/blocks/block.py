"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import textwrap
import typing
from typing import TYPE_CHECKING, Any, List

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name

from terraform_module_generator.schema.attributes.base import Attribute
from terraform_module_generator.schema.helpers.cache import cache_method_result

if TYPE_CHECKING:
    from terraform_module_generator.schema.blocks.nested_block import NestedBlock


TERRAFORM_CONFIG_BLOCK_ENTITY = inmanta.Entity(
    name="Block",
    path=["terraform", "config"],
)


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

    @cache_method_result
    def get_config_block_relation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityRelation:
        relation = inmanta.EntityRelation(
            name="_config_block",
            path=self.get_entity(module_builder).path,
            cardinality=(1, 1),
            description="Relation to the config block used internally to generate the config tree.",
            entity=self.get_entity(module_builder),
            peer=inmanta.EntityRelation(
                name="",
                path=self.get_entity(module_builder).path,
                cardinality=(0, None),
                entity=TERRAFORM_CONFIG_BLOCK_ENTITY,
            ),
        )
        module_builder.add_module_element(relation)

        return relation

    @cache_method_result
    def get_config_block_attributes(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Dict[str, str]:
        attributes = "\n".join(
            [
                f'"{attribute.name}": self.{attribute.get_entity_field(module_builder).name},'
                for attribute in self.attributes
                if attribute.computed is False
                and isinstance(
                    attribute.get_entity_field(module_builder), inmanta.Attribute
                )
            ]
        )

        return {
            "name": "null",
            "attributes": "{\n" + textwrap.indent(attributes, prefix=" " * 4) + "\n}",
            "deprecated": str(self.deprecated).lower(),
            "nesting_mode": '"single"',
            "parent": "null",
        }

    @cache_method_result
    def get_config_implementation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Implementation:
        config_block = "terraform::config::Block(\n"
        for key, value in self.get_config_block_attributes(module_builder).items():
            field = f"{key}={value}"
            field = textwrap.indent(field, " " * 4)
            config_block += field + ",\n"
        config_block += ")"
        config_block = (
            "self."
            + self.get_config_block_relation(module_builder).name
            + " = "
            + config_block
        )

        implementation_body = "# Building the config block for this entity\n"
        implementation_body += config_block

        implementation = inmanta.Implementation(
            name="config",
            path=self.path + [inmanta_safe_name(self.name)],
            entity=self.get_entity(module_builder),
            content=implementation_body,
            description="Build the config block corresponding to this entity and attaching all the non-computed entity attributes to it.",
        )
        implementation.add_import("::".join(TERRAFORM_CONFIG_BLOCK_ENTITY.path))
        module_builder.add_module_element(implementation)

        return implementation

    @cache_method_result
    def get_state_implementation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Implementation]:
        computed_attributes = [
            attribute
            for attribute in self.attributes
            if attribute.computed is True
            and isinstance(
                attribute.get_entity_field(module_builder), inmanta.Attribute
            )
        ]

        if not computed_attributes:
            return None

        config_block = self.get_config_block_relation(module_builder).name
        implementation_body = "\n".join(
            f'self.{attribute.get_entity_field(module_builder).name} = self.{config_block}._state["{attribute.name}"]'
            for attribute in computed_attributes
        )

        implementation = inmanta.Implementation(
            name="state",
            path=self.path + [inmanta_safe_name(self.name)],
            entity=self.get_entity(module_builder),
            content=implementation_body,
            description="Attach all the generated attributes values to the entity.",
        )
        module_builder.add_module_element(implementation)

        return implementation

    def add_to_module(self, module_builder: builder.InmantaModuleBuilder) -> None:
        # Build the two implementations
        self.get_config_implementation(module_builder)
        self.get_state_implementation(module_builder)

        # For each nested block, call the add_to_module method
        for nested_block in self.nested_blocks:
            nested_block.add_to_module(module_builder)

    @staticmethod
    def get_attributes(path: List[str], block: Any) -> List[Attribute]:
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

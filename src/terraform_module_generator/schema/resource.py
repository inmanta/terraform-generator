"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import textwrap
import typing
from typing import Any, List

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema.base import Schema
from terraform_module_generator.schema import const
from terraform_module_generator.schema.helpers.cache import cache_method_result


class Resource(Schema):
    def __init__(self, name: str, path: List[str], schema: Any) -> None:
        super().__init__(name, path, schema)
        self.name = name

    @cache_method_result
    def get_resource_unique_name_attribute(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Attribute:
        return inmanta.Attribute(
            name="_unique_name",
            inmanta_type=inmanta.InmantaStringType,
            optional=False,
            default=None,
            description="This is the unique identifier of the resource",
            entity=self.block.get_entity(module_builder),
        )

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        index = inmanta.Index(
            path=self.block.get_entity(module_builder).path,
            entity=self.block.get_entity(module_builder),
            fields=[self.get_resource_unique_name_attribute(module_builder)],
            description="This index ensure that each resource is unique",
        )
        module_builder.add_module_element(index)
        return index

    @cache_method_result
    def get_resource_implementation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Implementation:
        implementation_body = f"""
            terraform::Resource(
                type="{self.name}",
                name=self.{self.get_resource_unique_name_attribute(module_builder).name},
                root_config=self.{self.block.get_config_block_relation(module_builder).name},
                manual_config=false,
            )
        """
        implementation_body = textwrap.dedent(implementation_body.strip("\n"))

        implementation = inmanta.Implementation(
            name="resource",
            path=self.block.get_config_implementation(module_builder).path,
            entity=self.block.get_entity(module_builder),
            content=implementation_body,
            description="Create the terraform resource corresponding to this entity",
        )
        implementation.add_import("::".join(const.TERRAFORM_RESOURCE_ENTITY.path))
        module_builder.add_module_element(implementation)
        return module_builder

    def add_to_module(self, module_builder: builder.InmantaModuleBuilder) -> None:
        # Add the index
        self.get_entity_index(module_builder)

        # Add the implementation
        self.get_resource_implementation(module_builder)

        # Add everything in the inner block
        self.block.add_to_module(module_builder)

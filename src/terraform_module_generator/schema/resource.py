"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import textwrap
import typing
from typing import Any, List

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema import const
from terraform_module_generator.schema.base import Schema
from terraform_module_generator.schema.helpers.cache import cache_method_result
from terraform_module_generator.schema.provider import Provider


class Resource(Schema):
    def __init__(
        self, name: str, path: List[str], schema: Any, provider: Provider
    ) -> None:
        super().__init__(name, path, schema)
        self.name = name
        self.provider = provider

    @cache_method_result
    def get_entity(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Entity:
        entity = self.block.get_entity(module_builder)
        entity.parents.append(const.BASE_RESOURCE_ENTITY)
        return entity

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        index = inmanta.Index(
            path=self.get_entity(module_builder).path,
            entity=self.get_entity(module_builder),
            fields=[const.BASE_RESOURCE_ENTITY_INMANTA_ID],
            description="This index ensure that each resource is unique",
        )
        module_builder.add_module_element(index)
        return index

    @cache_method_result
    def get_resource_implementation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Implementation:
        implementation_body = f"""
            self.{const.BASE_RESOURCE_ENTITY_TERRAFORM_RESOURCE_RELATION.name} = terraform::Resource(
                type="{self.name}",
                name=self.{const.BASE_RESOURCE_ENTITY_INMANTA_ID.name},
                terraform_id=self.{const.BASE_RESOURCE_ENTITY_IMPORT_ID.name},
                root_config=self.{const.BASE_ENTITY_CONFIG_BLOCK_RELATION.name},
                manual_config=false,
                auto_agent=self.{const.BASE_RESOURCE_ENTITY_AUTO_AGENT.name},
                provider=self.{self.provider.get_resource_relation(module_builder).peer.name}.{self.provider.get_terraform_provider_relation(module_builder).name},
                purged=self.purged,
                purge_on_delete=self.purge_on_delete,
            )
        """
        implementation_body = textwrap.dedent(implementation_body.strip("\n"))

        implementation = inmanta.Implementation(
            name="resource",
            path=self.block.get_config_implementation(module_builder).path,
            entity=self.get_entity(module_builder),
            content=implementation_body,
            description="Create the terraform resource corresponding to this entity",
        )
        implementation.add_import("::".join(const.TERRAFORM_RESOURCE_ENTITY.path))
        module_builder.add_module_element(implementation)

        implement = inmanta.Implement(
            path=self.get_entity(module_builder).path,
            implementation=None,
            implementations=[implementation],
            entity=self.get_entity(module_builder),
        )
        module_builder.add_module_element(implement)

        return module_builder

    def add_to_module(self, module_builder: builder.InmantaModuleBuilder) -> None:
        # Add the index
        self.get_entity_index(module_builder)

        # Add the implementation
        self.get_resource_implementation(module_builder)

        # Add everything in the inner block
        self.block.add_to_module(module_builder)

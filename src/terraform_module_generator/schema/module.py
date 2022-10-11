"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema import const
from terraform_module_generator.schema.helpers.cache import cache_method_result

from .data_source import DataSource
from .provider import Provider
from .resource import Resource


class Module:
    def __init__(
        self, name: str, schema: Any, namespace: str, type: str, version: str
    ) -> None:
        self.name = name
        self.provider = Provider(
            "provider", [name], schema.provider, namespace, type, version
        )
        self.resources = [
            Resource(key, [name, "resources"], s, self.provider)
            for key, s in schema.resource_schemas.items()
        ]
        self.data_sources = [
            DataSource(key, [name, "data_sources"], d, self.provider)
            for key, d in schema.data_source_schemas.items()
        ]

    @cache_method_result
    def get_base_entity(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Entity:
        entity = const.BASE_ENTITY
        relation = const.BASE_ENTITY_CONFIG_BLOCK_RELATION

        # We don't simply replace the path as it is reused in other objects
        entity.path.clear()
        entity.path.append(self.name)

        module_builder.add_module_element(entity)
        module_builder.add_module_element(relation)

        return entity

    @cache_method_result
    def get_base_resource(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Entity:
        entity = const.BASE_RESOURCE_ENTITY
        relation = const.BASE_RESOURCE_ENTITY_TERRAFORM_RESOURCE_RELATION

        # We don't simply replace the path as it is reused in other objects
        entity.path.clear()
        entity.path.append(self.name)

        module_builder.add_module_element(entity)
        module_builder.add_module_element(relation)

        return entity

    def build(self, module_builder: builder.InmantaModuleBuilder) -> None:
        self.get_base_entity(module_builder)
        self.get_base_resource(module_builder)

        self.provider.add_to_module(module_builder)
        for resource in self.resources:
            resource.add_to_module(module_builder)

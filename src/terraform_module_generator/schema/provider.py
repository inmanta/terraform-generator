"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import textwrap
import typing

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema import const
from terraform_module_generator.schema.base import Schema
from terraform_module_generator.schema.helpers.cache import cache_method_result


class Provider(Schema):
    def __init__(
        self,
        name: str,
        path: typing.List[str],
        schema: typing.Any,
        namespace: str,
        type: str,
        version: str,
    ) -> None:
        super().__init__(name, path, schema)
        self.name = name
        self.namespace = namespace
        self.type = type
        self.version = version

    @cache_method_result
    def get_provider_alias_attribute(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Attribute:
        return inmanta.Attribute(
            name="alias",
            inmanta_type=inmanta.InmantaStringType,
            optional=False,
            default='""',
            description="This is the unique identifier of the provider",
            entity=self.block.get_entity(module_builder),
        )

    @cache_method_result
    def get_terraform_provider_relation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityRelation:
        relation = inmanta.EntityRelation(
            name="_provider",
            path=self.block.get_entity(module_builder).path,
            cardinality=(1, 1),
            peer=inmanta.EntityRelation(
                name="",
                path=self.block.get_entity(module_builder).path,
                cardinality=(0, None),
                entity=const.TERRAFORM_PROVIDER_ENTITY,
            ),
            entity=self.block.get_entity(module_builder),
            description="This is a relation to the provider entity from the terraform module.  For internal usage.",
        )
        module_builder.add_module_element(relation)
        return relation

    @cache_method_result
    def get_resource_relation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityRelation:
        relation = inmanta.EntityRelation(
            name="_resources",
            path=self.block.get_entity(module_builder).path,
            cardinality=(0, None),
            entity=self.block.get_entity(module_builder),
            description="This is a relation to all the resources in this module deployed using this provider.",
            peer=inmanta.EntityRelation(
                name="_provider",
                path=const.BASE_RESOURCE_ENTITY.path,
                cardinality=(1, 1),
                entity=const.BASE_RESOURCE_ENTITY,
                description=(
                    "This is the a relation to the provider entity defined in this module "
                    "that should be used to deploy this resource."
                ),
            ),
        )
        module_builder.add_module_element(relation)
        return relation

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        index = inmanta.Index(
            path=self.block.get_entity(module_builder).path,
            entity=self.block.get_entity(module_builder),
            fields=[self.get_provider_alias_attribute(module_builder)],
            description="This index ensure that each provider is unique",
        )
        module_builder.add_module_element(index)
        return index

    @cache_method_result
    def get_provider_implementation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Implementation:
        implementation_body = f"""
            self.{self.get_terraform_provider_relation(module_builder).name} = terraform::Provider(
                namespace="{self.namespace}",
                type="{self.type}",
                version="{self.version}",
                alias=self.{self.get_provider_alias_attribute(module_builder).name},
                root_config=self.{const.BASE_ENTITY_CONFIG_BLOCK_RELATION.name},
                manual_config=false,
            )
        """
        implementation_body = textwrap.dedent(implementation_body.strip("\n"))

        implementation = inmanta.Implementation(
            name="provider",
            path=self.block.get_config_implementation(module_builder).path,
            entity=self.block.get_entity(module_builder),
            content=implementation_body,
            description="Create the terraform provider corresponding to this entity",
        )
        implementation.add_import("::".join(const.TERRAFORM_PROVIDER_ENTITY.path))
        module_builder.add_module_element(implementation)

        implement = inmanta.Implement(
            path=implementation.path,
            implementation=None,
            implementations=[implementation],
            entity=self.block.get_entity(module_builder),
        )
        module_builder.add_module_element(implement)

        return module_builder

    def add_to_module(self, module_builder: builder.InmantaModuleBuilder) -> None:
        # Add the index
        self.get_entity_index(module_builder)

        # Add the implementation
        self.get_provider_implementation(module_builder)

        # Add everything in the inner block
        self.block.add_to_module(module_builder)

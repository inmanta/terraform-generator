"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from textwrap import dedent, indent
from typing import Any, Dict, List, Literal, Tuple

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.helpers.utils import inmanta_entity_name, inmanta_safe_name
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.entity_relation import EntityRelation
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.index import Index
from inmanta_module_factory.inmanta.module_element import DummyModuleElement
from inmanta_module_factory.inmanta.plugin import Plugin, PluginArgument
from inmanta_module_factory.inmanta.types import (
    InmantaAnyType,
    InmantaBooleanType,
    InmantaDictType,
    InmantaListType,
    InmantaPrimitiveType,
    InmantaStringType,
    InmantaType,
)


def config_plugin_name(entity: Entity) -> str:
    return f"get_{'_'.join(entity.path + [entity.name.lower()])}_config"


class TerraformSchemaParser:
    def __init__(
        self,
        module_builder: InmantaModuleBuilder,
        namespace: str,
        type: str,
        version: str,
        module_name: str,
    ) -> None:
        self.module_builder = module_builder
        self.namespace = namespace
        self.type = type
        self.version = version
        self.module_name = module_name

        self.dummy = DummyModuleElement(path=[self.module_name])
        self.module_builder.add_module_element(self.dummy)

        self.base_entity = Entity(
            name="Base",
            path=[self.module_name, "common"],
            fields=[
                Attribute(
                    name="inmanta_id",
                    inmanta_type=InmantaStringType,
                    optional=False,
                    description="This is the identifier of the entity.",
                ),
                Attribute(
                    name="terraform_id",
                    inmanta_type=InmantaStringType,
                    optional=True,
                    default="null",
                    description="This is the identifier of the terraform resource to import.",
                ),
            ],
            description="This entity is the base entity for all entities of the module.",
        )
        self.base_entity.overwrite_ordering_key("0")
        self.module_builder.add_module_element(self.base_entity)

    def parse_module(self, schema: Any):
        # Resource base entity
        resource_base_entity = Entity(
            name="Resource",
            path=[self.module_name],
            fields=[
                Attribute(
                    name="purged",
                    inmanta_type=InmantaBooleanType,
                    optional=False,
                    default="false",
                    description="Set this to true to purge the related terraform resource.",
                )
            ],
            description="This entity is the base entity for all resource entities of the module.",
        )
        resource_base_entity.overwrite_ordering_key("1")
        self.module_builder.add_module_element(resource_base_entity)

        terraform_resource_relation = self.build_terraform_resource_relation(
            resource_base_entity
        )
        self.module_builder.add_module_element(terraform_resource_relation)

        # Provider entity
        provider = self.parse_entity(
            [self.module_name],
            "provider",
            schema.provider.block,
            skip_index=True,
            has_id=False,
        )
        provider.parents = []
        provider.overwrite_ordering_key("0")

        terraform_provider_relation = self.build_terraform_provider_relation(provider)
        self.module_builder.add_module_element(terraform_provider_relation)

        provider_config_implementation = self.build_provider_config_implementation(
            provider
        )
        self.module_builder.add_module_element(provider_config_implementation)

        provider_config_implem = Implement(
            path=provider.path,
            implementation=provider_config_implementation,
            entity=provider,
        )
        self.module_builder.add_module_element(provider_config_implem)

        # Relation between the module provider and all module resource entities
        resource_provider_relation = EntityRelation(
            name="provider",
            path=resource_base_entity.path,
            entity=resource_base_entity,
            cardinality=(1, 1),
            description="A relation to the resource provider.",
            peer=EntityRelation(
                name="resources",
                path=provider.path,
                cardinality=(0, None),
                entity=provider,
            ),
        )
        self.module_builder.add_module_element(resource_provider_relation)

        # Each resource of the module
        for resource_name, resource_schema in schema.resource_schemas.items():
            resource_path = [self.module_name] + resource_name.split("_")
            resource_path_filtered = []
            last_resource_path_elem = ""
            for resource_path_elem in resource_path:
                resource_path_elem = inmanta_safe_name(resource_path_elem)

                if resource_path_elem != last_resource_path_elem:
                    resource_path_filtered.append(resource_path_elem)

                last_resource_path_elem = resource_path_elem

            resource_entity = self.parse_entity(
                resource_path_filtered[:-1],
                resource_path_filtered[-1],
                resource_schema.block,
            )
            resource_entity.parents.append(resource_base_entity)

            resource_config_implementation = self.build_resource_config_implementation(
                resource_name, resource_path[-1], resource_entity
            )
            self.module_builder.add_module_element(resource_config_implementation)

            resource_config_implem = Implement(
                path=resource_entity.path,
                implementation=resource_config_implementation,
                entity=resource_entity,
            )
            self.module_builder.add_module_element(resource_config_implem)

    def build_terraform_resource_relation(
        self, resource_entity: Entity
    ) -> EntityRelation:
        return EntityRelation(
            name="terraform_resource",
            path=resource_entity.path,
            entity=resource_entity,
            cardinality=(1, 1),
            description="A relation to the resource from the terraform module.",
            peer=EntityRelation(
                name="",
                path=["terraform"],
                cardinality=(0, 0),
                entity=Entity(
                    name="Resource",
                    path=["terraform"],
                    fields=[],
                ),
            ),
        )

    def build_terraform_provider_relation(
        self, provider_entity: Entity
    ) -> EntityRelation:
        return EntityRelation(
            name="provider",
            path=provider_entity.path,
            entity=provider_entity,
            cardinality=(1, 1),
            description="A relation to the provider from the terraform module.",
            peer=EntityRelation(
                name="",
                cardinality=(0, 0),
                path=["terraform"],
                entity=Entity(
                    name="Provider",
                    path=["terraform"],
                    fields=[],
                ),
            ),
        )

    def build_provider_config_implementation(
        self, provider_entity: Entity
    ) -> Implementation:
        implementation = Implementation(
            name="config",
            path=[self.module_name, "provider"],
            entity=provider_entity,
            content=dedent(
                f"""
                    self.provider = terraform::Provider(
                        namespace="{self.namespace}",
                        type="{self.type}",
                        version="{self.version}",
                        config={config_plugin_name(provider_entity)}(self),
                    )
                """.strip(
                    "\n"
                )
            ),
        )
        implementation.add_import("terraform")
        return implementation

    def build_resource_config_implementation(
        self, resource_type: str, resource_raw_name: str, resource_entity: Entity
    ) -> Implementation:
        implementation = Implementation(
            name="config",
            path=resource_entity.path + [inmanta_safe_name(resource_raw_name)],
            entity=resource_entity,
            content=dedent(
                f"""
                    self.terraform_resource = terraform::Resource(
                        name=self.inmanta_id,
                        terraform_id=self.terraform_id,
                        type="{resource_type}",
                        config={config_plugin_name(resource_entity)}(self),
                        purged=self.purged,
                        provider=self.provider.provider,
                        requires=self.requires,
                        provides=self.provides,
                    )
                """.strip(
                    "\n"
                )
            ),
        )
        implementation.add_import("terraform")
        return implementation

    def parse_entity(
        self,
        path: List[str],
        raw_name: str,
        schema_block: Any,
        skip_index: bool = False,
        has_id: bool = True,
    ) -> Entity:
        attributes_mapping = dict()
        relations_mapping = dict()
        attributes = list()

        for attribute in schema_block.attributes:
            if attribute.computed and not attribute.optional:
                continue

            entity_attribute = self.parse_attribute(attribute)
            attributes.append(entity_attribute)
            attributes_mapping.setdefault(attribute.name, entity_attribute)

        entity = Entity(
            name=inmanta_entity_name(raw_name),
            path=path,
            fields=attributes,
            parents=[self.base_entity] if has_id else [],
        )
        self.module_builder.add_module_element(entity)

        for block_type in schema_block.block_types:
            embedded_entity = self.parse_entity(
                path=path + [inmanta_safe_name(raw_name)],
                raw_name=inmanta_safe_name(block_type.type_name),
                schema_block=block_type.block,
                has_id=has_id,
            )

            max_cardinality = block_type.max_items
            if max_cardinality == 0:
                max_cardinality = None

            relation = EntityRelation(
                name=inmanta_safe_name(block_type.type_name),
                path=path,
                entity=entity,
                cardinality=(block_type.min_items, max_cardinality),
                peer=EntityRelation(
                    name="",
                    path=path,
                    entity=embedded_entity,
                    cardinality=(0, 0),
                ),
            )
            self.module_builder.add_module_element(relation)
            relations_mapping.setdefault(
                block_type.type_name, (relation, block_type.nesting)
            )

        plugin = self.build_plugin(entity, attributes_mapping, relations_mapping)
        self.module_builder.add_plugin(plugin)

        if not skip_index and has_id:
            inmanta_id = next(
                attribute
                for attribute in self.base_entity.attributes
                if attribute.name == "inmanta_id"
            )

            index = Index(
                path=entity.path,
                entity=entity,
                fields=[inmanta_id],
            )
            self.module_builder.add_module_element(index)

        implement = Implement(
            path=entity.path,
            implementation=Implementation(
                name="none",
                path=["std"],
                entity=entity,
                content="",
            ),
            entity=entity,
        )
        self.module_builder.add_module_element(implement)

        return entity

    def build_plugin(
        self,
        entity: Entity,
        attributes_mapping: Dict[str, Attribute],
        relations_mapping: Dict[str, Tuple[EntityRelation, int]],
    ) -> Plugin:
        self.dummy.add_import(entity.path_string)

        plugin_statements = ["config = dict()"]
        for key, attribute in attributes_mapping.items():
            plugin_statements.append(f"config['{key}'] = entity.{attribute.name}")

        for key, (relation, nesting) in relations_mapping.items():
            plugin_name = config_plugin_name(relation.peer.entity)
            value = "None"
            if nesting in [1, 5]:
                # 1 = SINGLE, 5 = GROUP
                value = f"{plugin_name}(entity.{relation.name})"
            if nesting in [2, 3]:
                # 2 = LIST, 3 = SET
                # We go below in all the trouble of sorting the list because entity
                # relations are sets, so the order is not guaranteed.
                value = dedent(
                    f"""
                    [
                        {plugin_name}(x)
                        for x in sorted(
                            entity.{relation.name},
                            key=lambda x: x.inmanta_id,
                        )
                    ]
                """.strip(
                        "\n"
                    )
                ).strip()
                if relation.cardinality_max == "1":
                    value = f"[{plugin_name}(entity.{relation.name})]"

            if nesting == 4:
                # 4 = MAP
                value = dedent(
                    f"""
                    {{
                        x.inmanta_id: {plugin_name}(x)
                        for x in entity.{relation.name}
                    }}
                """.strip(
                        "\n"
                    )
                ).strip()
                if relation.cardinality_max == "1":
                    value = dedent(
                        f"""
                        {{
                            entity.{relation.name}.inmanta_id: {plugin_name}(entity.{relation.name})
                        }}
                    """.strip(
                            "\n"
                        )
                    ).strip()

            risky_statement = f"\nconfig['{key}'] = {value}"

            plugin_statements.append(
                dedent(
                    f"""
                        try:{indent(risky_statement, prefix="                            ")}
                        except OptionalValueException:
                            pass
                    """.strip(
                        "\n"
                    )
                ).strip()
            )

        plugin_statements.append("return config")

        plugin = Plugin(
            name=config_plugin_name(entity),
            arguments=[PluginArgument("entity", inmanta_type=entity)],
            return_type=PluginArgument("", "dict"),
            content="\n".join(plugin_statements),
        )

        if relations_mapping:
            plugin.add_import("from inmanta.ast import OptionalValueException")

        return plugin

    def parse_attribute(self, schema: Any) -> Attribute:
        type = schema.type.decode("utf-8")
        return Attribute(
            name=inmanta_safe_name(schema.name),
            inmanta_type=self.parse_type(type),
            optional=schema.optional,
            description=schema.description,
        )

    def parse_type(self, raw_type: str) -> InmantaType:
        def parse_primitive(input_type: str) -> InmantaType:
            parsed = input_type.strip('"')
            if parsed in ["string", "bool", "number"]:
                return InmantaPrimitiveType(parsed)

            if parsed == "any":
                return InmantaAnyType

            raise Exception(f"Unknown primitive type: {input_type}")

        def parse_aggregate(input_type: str) -> Literal["list", "dict"]:
            parsed = input_type.strip('"')
            if parsed in ["list", "set"]:
                return "list"

            if parsed == "map":
                return "dict"

            raise Exception(f"Unknown aggregate type: {input_type}")

        if raw_type.startswith('"'):
            primitive = parse_primitive(raw_type)
            return primitive

        if raw_type.startswith("["):
            parsed = raw_type.strip("[]").split(",")
            if len(parsed) != 2:
                raise Exception(f"Unknown aggregate type: {raw_type}")

            aggregate = ""
            primitive = InmantaAnyType
            if parsed[0].startswith('"'):
                aggregate = parse_aggregate(parsed[0])

            if parsed[1].startswith('"'):
                primitive = parse_primitive(parsed[1])

            if aggregate == "dict":
                return InmantaDictType
            return InmantaListType(primitive)

        raise Exception(f"Unknown type: '{raw_type}'")

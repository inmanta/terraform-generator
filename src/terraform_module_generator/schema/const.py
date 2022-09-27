"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from inmanta_module_factory import inmanta

STD_PURGEABLE_RESOURCE = inmanta.Entity(
    name="PurgeableResource",
    path=["std"],
)

TERRAFORM_CONFIG_BLOCK_ENTITY = inmanta.Entity(
    name="Block",
    path=["terraform", "config"],
)
TERRAFORM_RESOURCE_ENTITY = inmanta.Entity(
    name="Resource",
    path=["terraform"],
)
TERRAFORM_PROVIDER_ENTITY = inmanta.Entity(
    name="Provider",
    path=["terraform"],
)

BASE_ENTITY = inmanta.Entity(
    name="ConfigBasedEntity",
    path=["__config__"],
    description="This is the base entity for all entities that should be serialized as config blocks.",
)
BASE_ENTITY_CONFIG_BLOCK_RELATION = inmanta.EntityRelation(
    name="_config_block",
    path=BASE_ENTITY.path,
    cardinality=(1, 1),
    description="Relation to the config block used internally to generate the config tree.",
    entity=BASE_ENTITY,
    peer=inmanta.EntityRelation(
        name="",
        path=BASE_ENTITY.path,
        cardinality=(0, None),
        entity=TERRAFORM_CONFIG_BLOCK_ENTITY,
    ),
)

BASE_RESOURCE_ENTITY = inmanta.Entity(
    name="BaseResource",
    path=BASE_ENTITY.path,
    description="This is the base entity for all resources in this module.",
    parents=[STD_PURGEABLE_RESOURCE],
)
BASE_RESOURCE_ENTITY_INMANTA_ID = inmanta.Attribute(
    name="_inmanta_id",
    inmanta_type=inmanta.InmantaStringType,
    optional=False,
    default=None,
    description="This is the unique identifier of the resource",
    entity=BASE_RESOURCE_ENTITY,
)
BASE_RESOURCE_ENTITY_AUTO_AGENT = inmanta.Attribute(
    name="_auto_agent",
    inmanta_type=inmanta.InmantaBooleanType,
    optional=False,
    default="true",
    description=(
        "Whether to start an agent automatically or not.  "
        "If set to false the relation agent_config should be set manually."
    ),
    entity=BASE_RESOURCE_ENTITY,
)
BASE_RESOURCE_ENTITY_IMPORT_ID = inmanta.Attribute(
    name="_import_id",
    inmanta_type=inmanta.InmantaStringType,
    optional=True,
    default="null",
    description="This attribute can be used to import an existing resource into the orchestrator.",
    entity=BASE_RESOURCE_ENTITY,
)
BASE_RESOURCE_ENTITY_TERRAFORM_RESOURCE_RELATION = inmanta.EntityRelation(
    name="_resource",
    path=BASE_RESOURCE_ENTITY.path,
    cardinality=(1, 1),
    description="This is the relation to the terraform resource entity.",
    entity=BASE_RESOURCE_ENTITY,
    peer=inmanta.EntityRelation(
        name="",
        path=BASE_RESOURCE_ENTITY.path,
        cardinality=(0, None),
        entity=TERRAFORM_RESOURCE_ENTITY,
    ),
)

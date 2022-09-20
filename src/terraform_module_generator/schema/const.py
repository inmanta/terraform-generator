"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from inmanta_module_factory import inmanta

TERRAFORM_CONFIG_BLOCK_RELATION = "_config_block"
TERRAFORM_CONFIG_BLOCK_ENTITY = inmanta.Entity(
    name="Block",
    path=["terraform", "config"],
)
TERRAFORM_RESOURCE_ENTITY = inmanta.Entity(
    name="Resource",
    path=["terraform"],
)

"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from typing import Any

from inmanta_module_factory import builder

from terraform_module_generator.schema.helpers.cache import cache_method_result

from .nested_block import NestedBlock, nested_block


def is_group(schema: Any) -> bool:
    return schema.nesting == 5


@nested_block(index="abc-group-z", condition=is_group)
class GroupNestedBlock(NestedBlock):
    @cache_method_result
    def get_config_block_attributes(
        self, module_builder: builder.InmantaModuleBuilder, imports: typing.Set[str]
    ) -> typing.Dict[str, str]:
        attributes = super().get_config_block_attributes(module_builder, imports)
        attributes["nesting_mode"] = '"group"'
        return attributes

"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from typing import Any

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema.helpers.cache import cache_method_result

from .nested_block import NestedBlock, nested_block


def is_set(schema: Any) -> bool:
    return schema.nesting == 3


@nested_block(index="abc-set-z", condition=is_set)
class SetNestedBlock(NestedBlock):
    @cache_method_result
    def get_config_block_attributes(
        self,
        module_builder: builder.InmantaModuleBuilder,
        imports: typing.Set[str],
    ) -> typing.Dict[str, str]:
        attributes = super().get_config_block_attributes(module_builder, imports)
        attributes["nesting_mode"] = '"set"'
        return attributes

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        return None

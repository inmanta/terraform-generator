"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import typing
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_safe_name

from terraform_module_generator.schema import const
from terraform_module_generator.schema.blocks import block
from terraform_module_generator.schema.helpers.cache import cache_method_result


class NestedBlock(block.Block):
    __nested_block_types: Dict[
        str, Tuple[Callable[[Any, bool], Type["NestedBlock"]]]
    ] = dict()

    def __init__(self, path: List[str], schema: Any) -> None:
        super().__init__(schema.type_name, path, schema.block)
        self.min_items: int = schema.min_items
        self.max_items: int = schema.max_items  # Zero for no upper bound

    @cache_method_result
    def get_entity_relation(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.EntityRelation:
        entity = self.get_entity(module_builder)
        relation = inmanta.EntityRelation(
            name=inmanta_safe_name(self.name),
            path=entity.path,  # Will be overwritten
            cardinality=(self.min_items, self.max_items or None),
            description=self.description,
            peer=inmanta.EntityRelation(
                name="_parent",
                path=entity.path,
                cardinality=(1, 1),
                entity=entity,
            ),
        )

        return relation

    @cache_method_result
    def get_config_block_attributes(
        self,
        module_builder: builder.InmantaModuleBuilder,
        imports: typing.Set[str],
    ) -> typing.Dict[str, str]:
        attributes = super().get_config_block_attributes(module_builder, imports)

        relation_to_parent = self.get_entity_relation(module_builder).peer

        attributes["name"] = f'"{self.name}"'
        attributes["parent"] = (
            "self."
            + relation_to_parent.name
            + "."
            + const.BASE_ENTITY_CONFIG_BLOCK_RELATION.name
        )
        return attributes

    @cache_method_result
    def get_entity_index(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> typing.Optional[inmanta.Index]:
        index = inmanta.Index(
            path=self.get_entity(module_builder).path,
            entity=self.get_entity(module_builder),
            fields=[self.get_entity_relation(module_builder).peer],
            description="This index ensure that each element of the config tree is unique",
        )
        module_builder.add_module_element(index)
        return index

    def add_to_module(self, module_builder: builder.InmantaModuleBuilder) -> None:
        super().add_to_module(module_builder)
        self.get_entity_index(module_builder)

    @classmethod
    def register_nested_block_type(
        cls: Type["NB"], index: str, condition: Callable[[Any], bool]
    ) -> None:
        if index in cls.__nested_block_types:
            raise ValueError(
                f"Can not register nested block type {cls.__name__} with index {index}.  "
                f"There is already another registered with this index: {cls.__nested_block_types[index][1].__name__}"
            )

        cls.__nested_block_types[index] = (condition, cls)

    @classmethod
    def get_nested_block_types(
        cls,
    ) -> List[Tuple[Callable[[Any], bool], Type["NestedBlock"]]]:
        """
        Get all the registered nested block types, ordered by index.
        """
        return [
            x[1]
            for x in sorted(
                ((key, value) for key, value in cls.__nested_block_types.items()),
                key=lambda x: x[0],
            )
        ]

    @classmethod
    def build_nested_block(cls, path: List[str], nested_block: Any) -> "NestedBlock":
        for condition, attribute_type in cls.get_nested_block_types():
            if condition(nested_block):
                return attribute_type(path, nested_block)

        raise ValueError(
            f"Couldn't find a matching type for nested block {nested_block}"
        )


NB = TypeVar("NB", bound=NestedBlock)


def nested_block(
    *, index: str, condition: Callable[[Any], bool]
) -> Callable[[Type["NB"]], Type["NB"]]:
    """
    Decorator for all the nested_block classes.  It will automatically register it as a possible
    nested_block type.  Calling
    """

    def register_nested_block(nested_block: Type["NB"]) -> Type["NB"]:
        nested_block.register_nested_block_type(index, condition)
        return nested_block

    return register_nested_block

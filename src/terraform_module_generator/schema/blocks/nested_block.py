"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar
from terraform_module_generator.schema.helpers.cache import cache_method_result

from terraform_module_generator.schema.blocks import block

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_safe_name


class NestedBlock(block.Block):
    __nested_block_types: Dict[
        str, Tuple[Callable[[Any, bool], Type["NestedBlock"]]]
    ] = dict()

    def __init__(self, schema: Any) -> None:
        super().__init__(schema)
        self.name: str = schema.type_name
        self.min_items: int = schema.min_items
        self.max_items: int = schema.max_items

    @cache_method_result
    def get_entity_relation(self, module_builder: builder.InmantaModuleBuilder) -> inmanta.EntityRelation:
        entity = self.get_entity(module_builder)
        relation = inmanta.EntityRelation(
            name=inmanta_safe_name(self.name),
            path=entity.path,
            cardinality=(self.min_items, self.max_items),
            description=self.description,
            peer=inmanta.EntityRelation(
                name="",
                path=entity.path,
                cardinality=(1, 1),
                entity=entity,
            ),
        )
        module_builder.add_module_element(relation)

        return relation

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
    def build_nested_block(cls, nested_block: Any) -> "NestedBlock":
        for condition, attribute_type in cls.get_nested_block_types():
            if condition(nested_block):
                return attribute_type(nested_block)

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

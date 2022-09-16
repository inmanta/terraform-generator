"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar
from inmanta_module_factory import inmanta
from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.helpers.utils import inmanta_safe_name

from terraform_module_generator.schema.helpers.cache import cache_method_result


class Attribute:
    __attribute_types: Dict[
        str, Tuple[Callable[[Any, bool], Type["Attribute"]]]
    ] = dict()

    def __init__(self, schema: Any) -> None:
        self.name: str = schema.name
        self.description: str = schema.description
        self.required: bool = schema.required
        self.optional: bool = schema.optional
        self.computed: bool = schema.computed
        self.deprecated: bool = schema.deprecated

    @abstractmethod
    def inmanta_attribute_type(self, module_builder: InmantaModuleBuilder) -> inmanta.InmantaType:
        """
        Return the inmanta type corresponding to this attribute
        """

    @cache_method_result
    def get_entity_field(self, module_builder: InmantaModuleBuilder) -> inmanta.EntityField:
        """
        Return the entity field corresponding to this entity which should
        be added to the entity it is attached to.
        """
        description = []
        if self.computed:
            description.append("(computed)")
        if self.deprecated:
            description.append("(deprecated)")
        if self.required:
            description.append("(required)")

        description.append(self.description)

        return inmanta.Attribute(
            name=inmanta_safe_name(self.name),
            inmanta_type=self.inmanta_attribute_type(module_builder),
            optional=self.optional,
            default="null" if self.optional else None,
            description=" ".join(description),
        )

    @classmethod
    def register_attribute_type(
        cls: Type["A"], index: str, condition: Callable[[Any], bool]
    ) -> None:
        if index in cls.__attribute_types:
            raise ValueError(
                f"Can not register type {cls.__name__} with index {index}.  "
                f"There is already another registered with this index: {cls.__attribute_types[index][1].__name__}"
            )

        cls.__attribute_types[index] = (condition, cls)

    @classmethod
    def get_attribute_types(
        cls,
    ) -> List[Tuple[Callable[[Any], bool], Type["Attribute"]]]:
        """
        Get all the registered attribute types, ordered by index.
        """
        return [
            x[1]
            for x in sorted(
                ((key, value) for key, value in cls.__attribute_types.items()),
                key=lambda x: x[0],
            )
        ]

    @classmethod
    def build_attribute(cls, attribute: Any) -> "Attribute":
        for condition, attribute_type in cls.get_attribute_types():
            if condition(attribute):
                return attribute_type(attribute)

        raise ValueError(f"Couldn't find a matching type for attribute {attribute}")


A = TypeVar("A", bound=Attribute)


def attribute(
    *, index: str, condition: Callable[[Any], bool]
) -> Callable[[Type["A"]], Type["A"]]:
    """
    Decorator for all the attribute classes.  It will automatically register it as a possible
    attribute type.  Calling
    """

    def register_attribute(attribute: Type["A"]) -> Type["A"]:
        attribute.register_attribute_type(index, condition)
        return attribute

    return register_attribute

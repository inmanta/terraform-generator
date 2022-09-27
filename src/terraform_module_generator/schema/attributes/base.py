"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import abc
import typing

from inmanta_module_factory import builder, inmanta
from inmanta_module_factory.helpers.utils import inmanta_safe_name

from terraform_module_generator.schema.helpers.cache import cache_method_result


class Attribute:
    __attribute_types: typing.Dict[
        str, typing.Tuple[typing.Callable[[bool], typing.Type["Attribute"]]]
    ] = dict()

    def __init__(self, path: typing.List[str], schema: typing.Any) -> None:
        self.path = path
        self.name: str = schema.name
        self.description: str = schema.description
        self.description_kind: str = schema.description_kind
        self.required: bool = schema.required
        self.optional: bool = schema.optional
        self.computed: bool = schema.computed
        self.deprecated: bool = schema.deprecated

        self._source_attribute = schema

    @abc.abstractmethod
    def inmanta_attribute_type(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.InmantaType:
        """
        Return the inmanta type corresponding to this attribute
        """

    @cache_method_result
    def get_attribute(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.Attribute:
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
            optional=self.optional and not self.computed,
            default="null" if self.optional and not self.computed else None,
            description=" ".join(description),
        )

    @cache_method_result
    def get_serialized_attribute_expression(
        self,
        entity_reference: str,
        module_builder: builder.InmantaModuleBuilder,
        imports: typing.Set[str],
    ) -> str:
        # By default we consider the attribute to be serializable all by itself
        return f"{entity_reference}.{self.get_attribute(module_builder).name}"

    @classmethod
    def register_attribute_type(
        cls: typing.Type["A"],
        index: str,
        condition: typing.Callable[[typing.Any], bool],
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
    ) -> typing.List[
        typing.Tuple[typing.Callable[[typing.Any], bool], typing.Type["Attribute"]]
    ]:
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
    def build_attribute(
        cls, path: typing.List[str], attribute: typing.Any
    ) -> "Attribute":
        for condition, attribute_type in cls.get_attribute_types():
            if condition(attribute):
                return attribute_type(path, attribute)

        raise ValueError(f"Couldn't find a matching type for attribute {attribute}")


A = typing.TypeVar("A", bound=Attribute)


def attribute(
    *, index: str, condition: typing.Callable[[typing.Any], bool]
) -> typing.Callable[[typing.Type["A"]], typing.Type["A"]]:
    """
    Decorator for all the attribute classes.  It will automatically register it as a possible
    attribute type.  Calling
    """

    def register_attribute(attribute: typing.Type["A"]) -> typing.Type["A"]:
        attribute.register_attribute_type(index, condition)
        return attribute

    return register_attribute

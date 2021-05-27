"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Optional, Union

from typing_extensions import Literal

InmantaPrimitiveType = Literal["string", "int", "float", "number", "bool"]


class InmantaPrimitiveList:
    def __init__(self, primitive_type: InmantaPrimitiveType) -> None:
        self.primitive_type = primitive_type

    def __str__(self) -> str:
        return self.primitive_type + "[]"


InmantaAttributeType = Union[
    Literal["dict", "any"], InmantaPrimitiveType, InmantaPrimitiveList
]


class Attribute:
    def __init__(
        self,
        name: str,
        inmanta_type: InmantaAttributeType,
        optional: bool = False,
        default: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        :param name: The name of the attribute
        :param inmanta_type: The type of the attribute
        :param optional: Whether this attribute is optional or not
        :param default: Whether this attribute has a default value or not
        :param description: A description of the attribute to add in the docstring
        """
        self.name = name
        self._inmanta_type = inmanta_type
        self.optional = optional
        self.default = default
        self.description = description

    @property
    def is_list(self) -> bool:
        return isinstance(self._inmanta_type, InmantaPrimitiveList)

    @property
    def inmanta_type(self) -> str:
        return str(self._inmanta_type)

    def __str__(self) -> str:
        type_expression = self.inmanta_type
        if self.optional:
            type_expression += "?"

        default_expression = ""
        if self.default is not None:
            default_expression = f" = {self.default}"
        elif self.optional:
            default_expression = " = null"

        return f"{type_expression} {self.name}{default_expression}\n"

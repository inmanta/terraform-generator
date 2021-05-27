"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from textwrap import indent
from typing import List, Optional, Set

from inmanta_module_builder.helpers.const import INDENT_PREFIX
from inmanta_module_builder.inmanta.attribute import Attribute
from inmanta_module_builder.inmanta.module_element import ModuleElement


class Entity(ModuleElement):
    def __init__(
        self,
        name: str,
        path: List[str],
        attributes: List[Attribute],
        parents: Optional[List["Entity"]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        An entity definition.
        :param name: The name of the entity
        :param path: The place in the module where the entity should be printed out
        :param attributes: A list of all the attributes of this entity
        :param parents: A list of all the entities this one inherit from
        :param description: A description of this entity, to be added in its docstring
        """
        super().__init__(name, path, description)
        self.attributes = attributes
        self.parents = parents or []

    def _ordering_key(self) -> str:
        return self.name

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        for parent in self.parents:
            if self.path_string != parent.path_string:
                # Parent is in a different file
                imports.add(parent.path_string)

        return imports

    def docstring(self) -> str:
        doc = super().docstring()

        for attribute in self.attributes:
            description = attribute.description or ""
            doc += f":attr {attribute.name}: {description}\n"

        # TODO add relations ?

        return doc

    def _definition(self) -> str:
        inheritance = ""
        if self.parents:
            parents = []
            for parent in self.parents:
                parent_path = parent.name
                if self.path_string != parent.path_string:
                    # Parent is in a different file
                    parent_path = parent.full_path_string

                parents.append(parent_path)

            inheritance = " extends " + ", ".join(parents)

        return f"entity {self.name}{inheritance}:\n"

    def __str__(self) -> str:
        return (
            self._definition()
            + indent(
                (
                    '"""\n'
                    + self.docstring()
                    + '"""\n'
                    + "".join([str(attribute) for attribute in self.attributes])
                ),
                prefix=INDENT_PREFIX,
            )
            + "end\n"
        )

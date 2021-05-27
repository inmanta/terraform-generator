"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import List, Optional, Set

from inmanta_module_builder.inmanta.attribute import Attribute
from inmanta_module_builder.inmanta.entity import Entity
from inmanta_module_builder.inmanta.module_element import ModuleElement


class Index(ModuleElement):
    def __init__(
        self,
        path: List[str],
        entity: Entity,
        attributes: List[Attribute],
        description: Optional[str] = None,
    ) -> None:
        """
        An index statement.
        :param path: The place in the module where the index should be printed
        :param entity: The entity this index is applied to
        :param attributes: A portion of the entity attributes on which apply the index
        :param description: A description of the index, to be added as docstring
        """
        super().__init__("index", path, description)
        self.entity = entity
        self.attributes = attributes

    def _ordering_key(self) -> str:
        suffix = "_".join([attribute.name for attribute in self.attributes])
        if self.path_string != self.entity.path_string:
            return f"{chr(255)}.index.{self.entity.full_path_string}_{suffix}"

        return f"{self.entity.ordering_key}_{suffix}"

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        if self.path_string != self.entity.path_string:
            # Entity is in another file
            imports.add(self.entity.path_string)

        return imports

    def validate(self) -> bool:
        return len(set(self.attributes) - set(self.entity.attributes)) == 0

    def __str__(self) -> str:
        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in another file
            entity_path = self.entity.full_path_string

        return f"index {entity_path}({', '.join([attribute.name for attribute in self.attributes])})\n"

"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import List, Optional, Set, Tuple

from inmanta_module_builder.inmanta.entity import Entity
from inmanta_module_builder.inmanta.module_element import ModuleElement


class EntityRelation(ModuleElement):
    def __init__(
        self,
        name: str,
        path: List[str],
        entity: Entity,
        arity: Tuple[int, Optional[int]],
        description: Optional[str] = None,
        peer: Optional["EntityRelation"] = None,
    ) -> None:
        """
        A relation statement (or rather half of it).
        :param name: The name of the relation
        :param path: The path in the module where the relation should be printed
        :param entity: The entity this relations belongs to
        :param arity: The multiplicity of the relation, a tuple contianing the min and max
        :param description: A description of the relation
        :param peer: The peer relation, which goes on the other end of "--"
        """
        super().__init__(name, path, description)
        self.entity = entity
        self.peer = peer
        self.arity_min = str(arity[0])
        self.arity_max = str(arity[1] or "")
        self._is_single = arity[1] or 2 == 1

    def _ordering_key(self) -> str:
        if self.path_string != self.entity.path_string:
            return f"{chr(255)}.relation.{self.entity.full_path_string}_{self.name}"

        return f"{self.entity.ordering_key}.{self.name}"

    @property
    def is_single(self) -> bool:
        return self._is_single

    def _raise_if_not_complete(self) -> None:
        if self.peer is None:
            raise RuntimeError("A relation must have a peer to be printed")

        if not self.name:
            raise RuntimeError(
                "The relation attribute can not be empty on the left side"
            )

    def _get_derived_imports(self) -> Set[str]:
        self._raise_if_not_complete()

        imports = set()

        if self.path_string != self.entity.path_string:
            # Entity is in another file
            imports.add(self.entity.path_string)

        if self.path_string != self.peer.entity.path_string:
            # Peer entity is in another file
            imports.add(self.peer.entity.path_string)

        return imports

    def __str__(self) -> str:
        self._raise_if_not_complete()

        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in another file
            entity_path = self.entity.full_path_string

        peer_entity_path = self.peer.entity.name
        if self.path_string != self.peer.entity.path_string:
            # Peer entity is in another file
            peer_entity_path = self.peer.entity.full_path_string

        arity = f"[{self.arity_min}:{self.arity_max}]"
        if self.arity_min == self.arity_max:
            arity = f"[{self.arity_min}]"

        peer_suffix = f".{self.peer.name} [{self.peer.arity_min}:{self.peer.arity_max}]"
        if not self.peer.name:
            peer_suffix = ""
        elif self.peer.arity_min == self.peer.arity_max:
            peer_suffix = f".{self.peer.name} [{self.peer.arity_min}]"

        return f"{entity_path}.{self.name} {arity} -- {peer_entity_path}{peer_suffix}\n"

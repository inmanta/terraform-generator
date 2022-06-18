"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from .base import attribute
from .collection import CollectionAttribute


def is_map(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        MapAttribute.legacy_regex.fullmatch(t) is not None
        or MapAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-map-z", condition=is_map)
class MapAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["map",(.+)\]')
    regex = re.compile(r"map\((.+)\)")
